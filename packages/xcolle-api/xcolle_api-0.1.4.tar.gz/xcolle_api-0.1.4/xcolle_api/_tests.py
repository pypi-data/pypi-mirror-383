from __future__ import annotations

import asyncio
import dataclasses
import json
import logging
from pathlib import Path
from typing import TYPE_CHECKING, TypeVar

from xcolle_api import GcolleAPI

API = GcolleAPI

if TYPE_CHECKING:
    from collections.abc import Awaitable

    from xcolle_api.gcolle.models import GcolleProduct
    from xcolle_api.pcolle.models import PcolleSeller

    _T = TypeVar("_T")

logging.basicConfig(level=10)
REPO_ROOT = Path(__file__).resolve().parents[1]
PRODUCTS = REPO_ROOT / "products"
SELLERS = REPO_ROOT / "sellers"

logger = logging.getLogger(__name__)


async def try_call(coro: Awaitable[_T]) -> _T | None:
    try:
        return await coro
    except Exception as e:
        raise
        logger.error(str(e))
        return None


async def test_sellers(*manage_ids: str) -> None:
    tasks: set[asyncio.Task[PcolleSeller | None]] = set()
    async with API() as api, asyncio.TaskGroup() as tg:
        for manager_id in manage_ids:
            coro = try_call(api.seller(manager_id))
            tasks.add(tg.create_task(coro))

    for task in asyncio.as_completed(tasks):
        seller = await task
        if seller is not None:
            as_json = seller.to_json()
            (REPO_ROOT / f"seller_{seller.id}.json").write_text(as_json)


async def test_products(*product_ids: str) -> None:
    tasks: set[asyncio.Task[GcolleProduct | None]] = set()
    async with API() as api, asyncio.TaskGroup() as tg:
        for product_id in product_ids:
            coro = try_call(api.product(product_id))
            tasks.add(tg.create_task(coro))

    for task in asyncio.as_completed(tasks):
        product = await task
        if product is not None:
            as_json = product.to_json()
            (REPO_ROOT / f"product_{product.id}.json").write_text(as_json)


async def test_tags() -> None:
    async with API() as api:
        product = await api.tags()

    dump = json.dumps(
        [dataclasses.asdict(r) for r in product],
        default=str,
        ensure_ascii=False,
        indent=2,
    )
    (REPO_ROOT / "tags.json").write_text(dump)


async def async_main() -> None:
    # sellers = "68295face62b17354", "62645f468a47ab90f"
    products = ("987595",)

    # await test_sellers(*sellers)
    await test_products(*products)


def run() -> None:
    asyncio.run(async_main())
