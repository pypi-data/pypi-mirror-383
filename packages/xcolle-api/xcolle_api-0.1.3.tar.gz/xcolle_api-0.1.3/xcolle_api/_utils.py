from __future__ import annotations

import asyncio
import logging
import re
from collections.abc import AsyncIterable
from typing import TYPE_CHECKING, TypeVar

import yarl

if TYPE_CHECKING:
    from collections.abc import AsyncIterable, Awaitable, Generator, Iterable

    _R = TypeVar("_R")


logger = logging.getLogger(__name__)


def digits(input_string: str) -> tuple[int, ...]:
    numbers_str = re.sub(r"\D", " ", input_string).strip()
    return tuple(map(int, numbers_str.split(" ")))


def number(input_string: str) -> int:
    return int(re.sub(r"\D", "", input_string).strip())


def parse_url(link_str: str, relative_to: yarl.URL) -> yarl.URL:
    url = yarl.URL(link_str, encoded="%" in link_str)
    if not url.absolute:
        url = relative_to.join(url)
    if not url.scheme:
        url = url.with_scheme(relative_to.scheme or "https")
    return url


def clean_single_line(string: str) -> str:
    string = string.replace("\n", " ").replace("\t", " ").strip()
    string_no_double_spaces = " ".join(string.split())
    return string_no_double_spaces


def check_string_input(locals: dict[str, object]) -> None:
    for name, value in locals.items():
        if name in ("self", "cls"):
            continue
        if not isinstance(value, str):
            raise TypeError(f"Invalid {name}. Expected string, got: {value = !r}")

        if not value.isalnum():
            raise ValueError(f"Invalid {name}. Got: {value}")


async def batched_gather(
    coro_factory: Iterable[Awaitable[_R]], batch_size: int = 10
) -> AsyncIterable[_R]:
    """Batch coroutines in a rotating window of 2 groups, scheduling the next group while awaiting the current group"""

    def get_batch() -> Generator[list[Awaitable[_R]]]:
        batch: list[Awaitable[_R]] = []
        for coro in coro_factory:
            batch.append(coro)
            if len(batch) == batch_size:
                yield batch
                batch = []
        if batch:
            yield batch

    async def gather(coros: list[Awaitable[_R]]) -> list[_R | BaseException]:
        return await asyncio.gather(*coros, return_exceptions=True)

    iterator = iter(get_batch())
    try:
        next_task: asyncio.Task | None = asyncio.create_task(gather(next(iterator)))
    except StopIteration:
        return

    while next_task:
        current_task = next_task
        try:
            next_task = asyncio.create_task(gather(next(iterator)))
        except StopIteration:
            next_task = None

        results = await current_task
        for result in results:
            if isinstance(result, BaseException):
                logger.error(repr(result), exc_info=result)
                continue
            yield result
