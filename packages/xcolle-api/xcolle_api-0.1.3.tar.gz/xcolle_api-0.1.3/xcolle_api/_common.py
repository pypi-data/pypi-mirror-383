from __future__ import annotations

import asyncio
import dataclasses
import json
import logging
import re
import types
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, ClassVar, NamedTuple, Self

import aiohttp
from aiolimiter import AsyncLimiter
from bs4 import BeautifulSoup

if TYPE_CHECKING:
    import datetime
    from collections.abc import Mapping

    import yarl


logger = logging.getLogger(__name__)


USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64; rv:141.0) Gecko/20100101 Firefox/141.0"
DEFAULT_HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Connection": "keep-alive",
}


class ResultStats(NamedTuple):
    videos: int
    pages: int
    videos_per_page: int


class API(ABC):
    def __init__(self) -> None:
        self._session: aiohttp.ClientSession | None = None
        self._limiter = AsyncLimiter(1, 5)
        self._headers = DEFAULT_HEADERS
        self._lock = asyncio.Lock()

    async def close(self) -> None:
        if self._session is not None:
            await self._session.close()
            self._session = None

    def _create_session(self) -> aiohttp.ClientSession:
        return aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(connect=30),
            raise_for_status=True,
            headers=self._headers,
            cookies={"AGE_CONF": "1"},
        )

    async def _validate_resp(self, soup: BeautifulSoup) -> BeautifulSoup:
        return soup

    async def _raw_request(self, url: yarl.URL, /, **kwargs: Any) -> BeautifulSoup:
        if self._session is None:
            self._session = self._create_session()
        logger.debug(f"Making GET request to {url}")
        try:
            async with self._session.get(url, **kwargs) as resp:
                return BeautifulSoup(await resp.text(), "html.parser")
        except aiohttp.ClientResponseError as e:
            raise ValueError(f"GET request to {url}: {e.status}") from None
        except Exception as e:
            raise ValueError(f"GET request to {url}: {e!r}") from None

    async def _fetch_webpage(self, url: yarl.URL, /, **kwargs: Any) -> BeautifulSoup:
        async with self._limiter:
            try:
                soup = await self._raw_request(url, **kwargs)
            except Exception:
                soup = await self._raw_request(url, **kwargs)

            return await self._validate_resp(soup)

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()

    @abstractmethod
    async def product(self, product_id: str, /) -> Product: ...


_byte_sizes: dict[str, float] = {
    "b": 1,
    "kb": 2**10,
    "mb": 2**20,
    "gb": 2**30,
    "tb": 2**40,
    "pb": 2**50,
    "eb": 2**60,
    "bit": 1 / 8,
    "kbit": 2**10 / 8,
    "mbit": 2**20 / 8,
    "gbit": 2**30 / 8,
    "tbit": 2**40 / 8,
    "pbit": 2**50 / 8,
    "ebit": 2**60 / 8,
}

_BYTE_SIZES: Mapping[str, float] = types.MappingProxyType(
    _byte_sizes | {k[0]: v for k, v in _byte_sizes.items() if "bit" not in k}
)
del _byte_sizes


class HumanBytes(int):
    """An int with helper methods to convert a string representing a number of bytes and unit into an integer (and viceversa).
    '1MB' means 1_048_576 bytes (binary scale).

    """

    _match_string = re.compile(r"^\s*(\d*\.?\d+)\s*(\w+)?", re.IGNORECASE).match

    @classmethod
    def from_string(cls, string: str, /) -> Self:
        try:
            return cls(int(string))
        except ValueError:
            pass

        match = cls._match_string(str(string))
        if match is None:
            raise ValueError("string is not valid bytes")

        num, unit = match.groups()
        unit = unit or "b"
        multiple = _BYTE_SIZES.get(unit.lower())
        if multiple is None:
            raise ValueError(f"Unknown byte unit: {unit}") from None

        return cls(int(float(num) * multiple))

    def to_string(self, separator: str = " ") -> str:
        divisor = 1024

        number = float(self)
        for unit in ("B", "KB", "MB", "GB", "TB", "PB"):
            if abs(number) < 1000:
                if unit == "B":
                    return f"{number:0.0f}{separator}{unit}"
                return f"{number:0.2f}{separator}{unit}"
            number /= divisor

        return f"{number:0.2f}{separator}EB"


class Jsonable:
    __dataclass_fields__: ClassVar[dict[str, dataclasses.Field[Any]]]

    def to_json(self) -> str:
        return json.dumps(
            self.as_dict(),
            ensure_ascii=False,
            indent=2,
            default=str,
        )

    def as_jsonsable_dict(self) -> dict[str, Any]:
        return json.loads(self.to_json())

    as_dict = dataclasses.asdict


@dataclasses.dataclass(slots=True, kw_only=True)
class Product(Jsonable):
    id: str
    file_name: str | None

    file_size: str | None = dataclasses.field(repr=False)
    file_size_bytes: int | None = dataclasses.field(repr=False)

    views: int = dataclasses.field(repr=False)
    price: int = dataclasses.field(repr=False)
    title: str = dataclasses.field(repr=False)
    sales_start_date: datetime.datetime = dataclasses.field(repr=False)
    seller_id: str = dataclasses.field(repr=False)
    thumbnail: str = dataclasses.field(repr=False)
    url: str = dataclasses.field(repr=False)
    contains: tuple[str, ...] = dataclasses.field(repr=False)
    sets: tuple[str, ...] = dataclasses.field(repr=False)
    additional_info: tuple[str, ...] = dataclasses.field(repr=False)
    description: str = dataclasses.field(compare=False, repr=False)
    description_html: str = dataclasses.field(compare=False, repr=False)
    previews: tuple[str, ...] = dataclasses.field(repr=False)
