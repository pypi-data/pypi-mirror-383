from __future__ import annotations

import dataclasses
from typing import TYPE_CHECKING

from xcolle_api._common import Jsonable, Product

if TYPE_CHECKING:
    import datetime


@dataclasses.dataclass(slots=True, kw_only=True)
class PcolleSeller(Jsonable):
    id: str
    name: str

    profile_image: str = dataclasses.field(repr=False)
    url: str = dataclasses.field(repr=False)
    email: str | None = dataclasses.field(repr=False)
    self_introduction: str = dataclasses.field(repr=False)
    products_count: int = dataclasses.field(repr=False)
    news: tuple[PcolleNews, ...] = dataclasses.field(repr=False)


@dataclasses.dataclass(slots=True, kw_only=True)
class PcolleProduct(Product):
    category: PcolleCategory = dataclasses.field(repr=False)
    ratings: int = dataclasses.field(repr=False)
    tags: tuple[PcolleTag, ...] = dataclasses.field(repr=False)
    manage_id: str = dataclasses.field(repr=False)
    bonus: PcolleBonus | None = dataclasses.field(repr=False)


@dataclasses.dataclass(slots=True, order=True)
class PcolleCategory(Jsonable):
    id: int
    name: str


@dataclasses.dataclass(slots=True, order=True)
class PcolleTag(Jsonable):
    id: int
    name: str


@dataclasses.dataclass(slots=True)
class PcolleBonus(Jsonable):
    file_name: str

    file_size: str = dataclasses.field(repr=False)
    file_size_bytes: int = dataclasses.field(repr=False)
    restrictions: tuple[str, ...] = dataclasses.field(repr=False)


@dataclasses.dataclass(slots=True, kw_only=True, order=True)
class PcolleNews(Jsonable):
    date: datetime.datetime
    manage_id: str
    title: str
    text: str = dataclasses.field(repr=False)


@dataclasses.dataclass(slots=True, order=True)
class ProductTagStats(Jsonable):
    tag: PcolleTag
    videos: int
