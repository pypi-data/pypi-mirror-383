from __future__ import annotations

import datetime
import logging
from typing import TYPE_CHECKING, Literal

import yarl
from html2text import html2text

from xcolle_api import _css, _utils
from xcolle_api._common import (
    API,
    HumanBytes,
    ResultStats,
)
from xcolle_api.pcolle.models import (
    PcolleBonus,
    PcolleCategory,
    PcolleNews,
    PcolleProduct,
    PcolleSeller,
    PcolleTag,
    ProductTagStats,
)

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator, Generator, Iterable

    import bs4


logger = logging.getLogger(__name__)
_PRIMARY_URL = yarl.URL("https://www.pcolle.com")
_tags: dict[int, ProductTagStats] = {}


def _parse_url(string: str) -> yarl.URL:
    return _utils.parse_url(string, relative_to=_PRIMARY_URL)


class PcolleAPI(API):
    async def product(self, product_id: str, /) -> PcolleProduct:
        _utils.check_string_input(locals())
        url = (_PRIMARY_URL / "product/detail/").update_query(product_id=product_id)
        soup = await self._fetch_webpage(url)
        return _parse_product(soup, url)

    async def seller(self, manage_id: str, /) -> PcolleSeller:
        _utils.check_string_input(locals())

        # fetch with filter by all product (p=0) to get a correct "n_products"
        url = (_PRIMARY_URL / "manage/detail/").with_query(
            p=0,
            r="new",
            manage_id=manage_id,
        )

        soup = await self._fetch_webpage(url)
        return _parse_seller(soup, url)

    async def tags(self) -> dict[int, ProductTagStats]:
        await self._update_tags()
        return _tags

    async def _get_tags(self) -> None:
        global _tags
        url = _PRIMARY_URL / "product/tags/"
        soup = await self._fetch_webpage(url)
        _tags = {t.tag.id: t for t in sorted(_parse_tags(soup))}

    async def _update_tags(self) -> None:
        if _tags:
            return
        async with self._lock:
            if _tags:
                return
            await self._get_tags()

    async def products(
        self,
        *,
        price: Literal["PAID", "FREE", "ALL"] = "ALL",
        only_on_sale: bool = False,
        only_sets: bool = False,
        only_w_bonus: bool = False,
        exclude_approved_members_only: bool = False,
    ) -> AsyncGenerator[str]:
        prices = {"PAID": 1, "FREE": 2, "ALL": 0}

        if price not in prices:
            raise ValueError(f"Invalid price filter. Expected {prices.keys()} got {price!r}")

        url = (_PRIMARY_URL / "product/result/").with_query(p=prices[price], r="new")

        for name, param in {
            "only_on_sale": "s",
            "only_sets": "v",
            "only_w_bonus": "g",
            "exclude_approved_members_only": "n",
        }.items():
            value = locals()[name]
            if not isinstance(value, bool):
                raise TypeError(f"Invalid {name}. Expected bool, got {type(value)}")
            if value:
                url = url.update_query({param: 1})

        seen: set[str] = set()

        def extract_product_ids(soup: bs4.BeautifulSoup) -> Generator[str]:
            for a_tag in soup.select(
                ".search_item_product a[href*='/product/detail/?product_id=']"
            ):
                url = _parse_url(_css.attr(a_tag, "href"))
                product_id = url.query["product_id"]
                if product_id not in seen:
                    seen.add(product_id)
                    yield product_id

        soup: bs4.BeautifulSoup = await self._fetch_webpage(url.update_query(page=1))
        for product_id in extract_product_ids(soup):
            yield product_id

        stats = _parse_search_results(soup)
        if stats.pages == 1:
            return

        async for soup in _utils.batched_gather(
            self._fetch_webpage(url.update_query(page=page)) for page in range(2, stats.pages + 1)
        ):
            for product_id in extract_product_ids(soup):
                yield product_id

        if stats.videos > (n_products := len(seen)):
            logger.warning(
                f"missing {stats.videos - n_products} results. Expected: {stats.videos}, Got: {n_products}"
            )


def _parse_seller(soup: bs4.BeautifulSoup, url: yarl.URL) -> PcolleSeller:
    manage_id = url.query["manage_id"]
    top_main = _css.select_one(soup, "div.top-main")
    info_table = _css.select_one(top_main, "div.item-main table")

    def parse_email() -> str | None:
        # Email use to be available
        try:
            email = _css.get_td(info_table, "メールアドレス:").get_text(strip=True).strip()
        except _css.SelectorError:
            return None
        else:
            if email != "非公開":
                return email
        return None

    def parse_news() -> Iterable[PcolleNews]:
        news_section = top_main.select_one("div.news")
        if not news_section:
            return

        for entry in news_section.select("li"):
            title_and_date, content = entry.select("p")
            title = _css.select_one(title_and_date, "span").extract().get_text(strip=True)
            year, month, day = _utils.digits(title_and_date.get_text(strip=True))

            yield PcolleNews(
                title=title,
                manage_id=manage_id,
                date=datetime.datetime(year, month, day, tzinfo=datetime.UTC),
                text=content.get_text().replace("\r\n", "\n").strip(),
            )

    def parse_product_count() -> int:
        filter_tag = _css.select_one(top_main, "dl.search-filter + span")
        filter_text = filter_tag.get_text(strip=True).rsplit("/", 1)[-1]
        return _utils.number(filter_text)

    return PcolleSeller(
        id=manage_id,
        name=_css.get_td(info_table, "名前:").get_text(strip=True),
        profile_image=str(
            _parse_url(_css.attr(_css.select_one(top_main, "div.item-main img"), "src"))
        ),
        self_introduction=_css.get_td(info_table, "自己紹介:")
        .get_text()
        .replace("\r\n", "\n")
        .strip(),
        url=str(url.with_query(manage_id=manage_id)),
        email=parse_email(),
        news=tuple(parse_news()),
        products_count=parse_product_count(),
    )


def _parse_product(soup: bs4.BeautifulSoup, url: yarl.URL) -> PcolleProduct:
    main_section = _css.select_one(soup, "div.main")
    info_table = _css.select_one(main_section, ".item-info table")
    details_section = _css.select_one(main_section, ".item_detail")

    def parse_price() -> int:
        price_text = (
            _css.get_td(info_table, "金額(税込):").get_text(strip=True).partition("円")[0].strip()
        )
        if price_text == "無料":
            return 0
        return _utils.number(price_text)

    def parse_description() -> str:
        desc = _css.select_one(main_section, ".item_description")
        _css.decompose(desc, ".btn_set")
        return desc.decode_contents().replace("\r\n", "\n").strip()

    def parse_bonus() -> PcolleBonus | None:
        gifts_section = details_section.select_one("#item_gift")
        if not gifts_section:
            return None

        file_name = _css.get_dd(gifts_section, "特典ファイル名:").get_text(strip=True)
        file_size, bytes_approx = _parse_file_size(
            _css.get_dd(gifts_section, "ファイルサイズ:").get_text(strip=True)
        )
        restrictions = []
        try:
            restrictions_tag = _css.get_dd(gifts_section, "特典配布制限:")
        except _css.SelectorError:
            pass
        else:
            restrictions.append(_utils.clean_single_line(restrictions_tag.get_text(strip=True)))
            for tag in restrictions_tag.find_next_siblings("dd"):
                if text := _utils.clean_single_line(tag.get_text(strip=True)):
                    restrictions.append(text)
        return PcolleBonus(file_name, file_size, bytes_approx, tuple(restrictions))

    def parse_sales_date() -> datetime.datetime:
        year, month, day = _utils.digits(
            _css.get_td(info_table, "販売開始日:").get_text(strip=True)
        )
        return datetime.datetime(year, month, day, tzinfo=datetime.UTC)

    def parse_category() -> PcolleCategory:
        a_tag = _css.select_one(_css.get_td(info_table, "カテゴリー:"), "a")
        url = _parse_url(_css.attr(a_tag, "href"))
        return PcolleCategory(id=int(url.query["c"]), name=a_tag.get_text(strip=True))

    def parse_contains() -> Iterable[str]:
        try:
            value_tag = _css.get_dd(details_section, "セット商品:")
        except _css.SelectorError:
            return

        for tag in value_tag.select("a"):
            yield _parse_url(_css.attr(tag, "href")).query["product_id"]

    def parse_set_info() -> tuple[str, ...]:
        try:
            value_tag = _css.get_dd(details_section, "セット商品情報:")
        except _css.SelectorError:
            return ()

        sets = [
            _parse_url(_css.attr(tag, "href")).query["product_id"] for tag in value_tag.select("a")
        ]

        return tuple(sorted(sets))

    def get_dd_text_or_none(dt_value: str) -> str | None:
        try:
            return _css.get_dd(details_section, dt_value).get_text(strip=True)
        except _css.SelectorError:
            return None

    category = parse_category()
    desc_html = parse_description()

    if file_size_str := get_dd_text_or_none("ファイルサイズ:"):
        file_size, bytes_approx = _parse_file_size(file_size_str)
    else:
        file_size, bytes_approx = None, None

    manage_id = _parse_url(
        _css.attr(_css.select_one(_css.get_td(info_table, "販売会員:"), "a"), "href")
    ).query["manage_id"]

    return PcolleProduct(
        id=url.query["product_id"],
        file_name=get_dd_text_or_none("ファイル名:"),
        file_size=file_size,
        file_size_bytes=bytes_approx,
        price=parse_price(),
        views=int(_css.get_td(main_section, "総閲覧数:").get_text(strip=True).replace(",", "")),
        ratings=int(_css.get_td(main_section, "合計評価数:").get_text(strip=True).replace(",", "")),
        title=_css.select_one(main_section, "div.title-04").get_text(strip=True),
        sales_start_date=parse_sales_date(),
        category=category,
        manage_id=manage_id,
        seller_id=manage_id,
        thumbnail=str(
            _parse_url(_css.attr(_css.select_one(main_section, "div.part1 article img"), "src"))
        ),
        url=str(url),
        bonus=parse_bonus(),
        contains=tuple(parse_contains()),
        sets=parse_set_info(),
        additional_info=tuple(
            _utils.clean_single_line(li.get_text(strip=True))
            for li in details_section.select(".additions li")
        ),
        description=html2text(desc_html, baseurl=str(_PRIMARY_URL)),
        description_html=desc_html,
        previews=tuple(
            str(_parse_url(_css.attr(img, "src")))
            for img in main_section.select(".item_images img")
        ),
        tags=tuple(
            PcolleTag(
                id=int(_parse_url(_css.attr(a_tag, "href")).query["t"]),
                name=a_tag.get_text(strip=True),
            )
            for a_tag in main_section.select("section.item_tags a[href*='t=']")
        ),
    )


def _parse_search_results(soup: bs4.BeautifulSoup) -> ResultStats:
    form = _css.select_one(soup, "form[action='/product/result/'][method=post]")
    before, after = form.get_text(strip=True).split("/", 1)
    _, videos_per_page = [_utils.number(t) for t in before.split("～")]
    n_videos = _utils.number(after)
    mod = n_videos / videos_per_page
    n_pages = int(mod) + (mod % 1 > 0)
    return ResultStats(n_videos, n_pages, videos_per_page)


def _parse_file_size(file_size: str) -> tuple[str, int]:
    human_bytes = HumanBytes.from_string(file_size)
    return human_bytes.to_string(), int(human_bytes)


def _parse_tags(soup: bs4.BeautifulSoup) -> Generator[ProductTagStats]:
    for li in soup.select(".item_tags li:has(a[href*='t='])"):
        a_tag = _css.select_one(li, "a[href*='t=']").extract()
        url = _parse_url(_css.attr(a_tag, "href"))
        count = _utils.number(li.get_text())
        tag = PcolleTag(
            id=int(url.query["t"]),
            name=a_tag.extract().get_text(strip=True),
        )
        yield ProductTagStats(tag, count)
