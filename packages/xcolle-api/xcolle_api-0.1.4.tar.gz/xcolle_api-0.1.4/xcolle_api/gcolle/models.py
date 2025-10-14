from __future__ import annotations

import dataclasses

from xcolle_api._common import Jsonable, Product


@dataclasses.dataclass(slots=True, kw_only=True)
class GcolleProduct(Product):
    tags: tuple[str, ...]
    category_id: int
    category: GcolleCategory = dataclasses.field(repr=False)
    manufacturer_id: str = dataclasses.field(repr=False)
    video_preview: str | None = dataclasses.field(repr=False)


@dataclasses.dataclass(slots=True, order=True)
class GcolleCategory(Jsonable):
    id: int
    name: str
    full_id: str
