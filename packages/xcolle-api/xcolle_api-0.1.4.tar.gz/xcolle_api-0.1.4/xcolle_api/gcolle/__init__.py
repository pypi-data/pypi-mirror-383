from __future__ import annotations

import datetime
import logging
from typing import TYPE_CHECKING, Any
from unicodedata import normalize

import yarl
from html2text import html2text

from xcolle_api import _css, _utils
from xcolle_api._common import API, USER_AGENT, HumanBytes
from xcolle_api.gcolle.models import GcolleCategory, GcolleProduct

if TYPE_CHECKING:
    from collections.abc import Generator

    import bs4


_logger = logging.getLogger(__name__)
_PRIMARY_HOST = "gcolle.net"
_IMAGES_HOST = "img." + _PRIMARY_HOST
_PRIMARY_URL = yarl.URL("https://" + _PRIMARY_HOST)
_IMAGES_URL = yarl.URL("https://" + _IMAGES_HOST)
_ANDROID_UA = "Mozilla/5.0 (Linux; Android 16) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.7339.52 Mobile Safari/537.36"
_categories: dict[int, GcolleCategory] = {}


def _parse_url(string: str) -> yarl.URL:
    base = _PRIMARY_URL
    if "/images/" in string:
        string = string.replace("/images/", "/")
        base = _IMAGES_URL

    url = _utils.parse_url(string, base)
    if "uploader" not in url.parts:
        return url

    url = url.with_host(_IMAGES_HOST)
    if "x" not in url.parts[2]:
        return url

    new_parts = list(url.parts)
    _ = new_parts.pop(2)
    new_path = "/".join(new_parts[1:])
    return url.with_path(new_path, keep_query=True, keep_fragment=True)


class GcolleAPI(API):
    def __init__(self) -> None:
        super().__init__()
        self._headers["User-Agent"] = _ANDROID_UA

    async def product(self, product_id: str, /) -> GcolleProduct:
        _utils.check_string_input(locals())

        url = _PRIMARY_URL / "product_info.php/products_id" / product_id
        soup = await self._fetch_webpage(url)
        return _parse_product(soup, url)

    async def categories(self) -> dict[int, GcolleCategory]:
        await self._update_categories()
        return _categories

    async def _fetch_webpage(self, url: yarl.URL, /, **kwargs: Any) -> bs4.BeautifulSoup:
        await self._update_categories()
        return await super()._fetch_webpage(url, **kwargs)

    async def _validate_resp(self, soup: bs4.BeautifulSoup) -> bs4.BeautifulSoup:
        if age_check := soup.select_one("#page-age-check"):
            _logger.info("passing age check")
            age_check_link = _parse_url(
                _css.attr(_css.select_one(age_check, "a.btn-danger"), "href")
            )
            soup = await self._raw_request(age_check_link)
        return soup

    async def _update_categories(self) -> None:
        if _categories:
            return
        async with self._lock:
            if _categories:
                return
            await self._get_categories()

    async def _get_categories(self) -> None:
        global _categories
        _logger.info("getting categories")
        url = _PRIMARY_URL / "default.php/cPath/254/price/2/order/6d/page/1"
        _ = await API._fetch_webpage(self, url)  # bypass age check
        headers = self._headers | {
            "User-Agent": USER_AGENT
        }  # category list is only available on desktop site
        soup = await API._fetch_webpage(self, url / "language/ja", headers=headers)
        _categories = {c.id: c for c in sorted(_parse_categories(soup))}
        _ = await API._fetch_webpage(self, url / "language/en")  # back to english


def _parse_product(soup: bs4.BeautifulSoup, url: yarl.URL) -> GcolleProduct:
    product_id = url.name
    main_section = _css.select_one(soup, "body > div.container")
    info_table = _css.select_one(main_section, "div.border-info table")

    def _parse_video_preview() -> str | None:
        try:
            source = _css.select_one(main_section, "video.video-js source")
        except _css.SelectorError:
            return None
        else:
            return str(_parse_url(_css.attr(source, "src")))

    def _parse_date() -> datetime.datetime:
        date_tag = _css.select_one(
            _css.get_td(info_table, "Uploaded:"),
            "small.text-muted date",
        )

        date = datetime.datetime.fromisoformat(_css.attr(date_tag, "datetime"))
        if not date.tzinfo:
            date = date.replace(tzinfo=datetime.UTC)
        return date

    def _parse_price() -> int:
        price_tag = _css.select_one(main_section, "b:has(span.fa-yen-sign)")
        return _utils.number(price_tag.get_text())

    def _parse_contains() -> Generator[str]:
        for a_tag in _css.get_td(info_table, "Contains:").select("a"):
            yield _parse_url(_css.attr(a_tag, "href")).name

    def _parse_bites() -> HumanBytes:
        bites_tag = _css.select_one(_css.get_td(info_table, "File size:"), "small.text-muted")
        return HumanBytes(_utils.number(bites_tag.get_text()))

    desc_html = (
        _css.select_one(main_section, "#description p")
        .decode_contents()
        .replace("\r\n", "\n")
        .strip()
    )

    human_bytes = _parse_bites()
    manufacturer_url = _parse_url(_css.attr(_css.select_one(soup, "#manufacturer dd a"), "href"))
    manufacturer_id = manufacturer_url.name
    category_url = _parse_url(_css.attr(_css.select_one(main_section, "a[href*=cPath]"), "href"))
    category_id = int(category_url.name.split("_")[-1])

    return GcolleProduct(
        id=product_id,
        sets=(),
        additional_info=(),
        description_html=desc_html,
        url=str(url),
        category_id=category_id,
        category=_categories[category_id],
        price=_parse_price(),
        manufacturer_id=manufacturer_id,
        seller_id=manufacturer_id,
        description=html2text(desc_html, baseurl=str(_PRIMARY_URL)),
        title=_css.select_one(main_section, "h1").get_text(strip=True),
        previews=tuple(
            str(_parse_url(_css.attr(img, "src")))
            for img in main_section.select("a[data-gallery='banners'] img")
        ),
        tags=tuple(a_tag.get_text(strip=True) for a_tag in main_section.select("p#tags a")),
        thumbnail=str(_parse_url(_css.attr(_css.select_one(main_section, "a img"), "src"))),
        video_preview=_parse_video_preview(),
        file_name=_css.get_td(info_table, "File name:").get_text(strip=True),
        file_size_bytes=int(human_bytes),
        file_size=human_bytes.to_string(),
        sales_start_date=_parse_date(),
        views=_utils.number(_css.get_td(info_table, "Page viewed:").get_text()),
        contains=tuple(_parse_contains()),
    )


def _parse_categories(soup: bs4.BeautifulSoup) -> Generator[GcolleCategory, Any, None]:
    current_parents: list[int] = [-1, -1, -1]
    for category_entry in soup.select("select[name=categories_id] option[value]"):
        category_id = int(_css.attr(category_entry, "value"))
        name = normalize("NFKD", category_entry.get_text())

        if any(trash in name for trash in ["│ ├ ", "│ └ "]):
            parents = 2
        elif any(trash in name for trash in ["├ ", "└ "]):
            parents = 1
        else:
            parents = 0

        current_parents[parents] = category_id
        name = name[parents * 2 :]

        yield GcolleCategory(
            id=category_id,
            name=name.strip(),
            full_id="_".join(map(str, [*current_parents[:parents], category_id])),
        )
