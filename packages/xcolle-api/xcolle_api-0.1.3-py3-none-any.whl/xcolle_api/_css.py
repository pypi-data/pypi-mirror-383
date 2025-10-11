from __future__ import annotations

import functools
from typing import TYPE_CHECKING, ParamSpec, TypeVar

if TYPE_CHECKING:
    from collections.abc import Callable

    import bs4

    _P = ParamSpec("_P")
    _R = TypeVar("_R")


class SelectorError(Exception):
    def __init__(self, message: str | None = None) -> None:
        super().__init__(message)


def not_none(func: Callable[_P, _R | None]) -> Callable[_P, _R]:
    @functools.wraps(func)
    def wrapper(*args: _P.args, **kwargs: _P.kwargs) -> _R:
        result = func(*args, **kwargs)
        if result is None:
            raise SelectorError
        return result

    return wrapper


def get_attr(tag: bs4.Tag, attribute: str) -> str | None:
    """Same as `tag.get(attribute)` but asserts the result is not multiple strings"""
    attribute_ = attribute
    if attribute_ == "src":
        value = tag.get("data-src") or tag.get(attribute_)
    else:
        value = tag.get(attribute_)
    if isinstance(value, list):
        raise SelectorError(f"Expected a single value for {attribute = !r}, got multiple")
    return value


@not_none
def attr(tag: bs4.Tag, attribute: str) -> str | None:
    """Same as `tag.get(attribute)` but asserts the result is not `None` and is a single string"""
    return get_attr(tag, attribute)


@not_none
def select_one(tag: bs4.Tag, selector: str) -> bs4.Tag | None:
    """Same as `tag.select_one` but asserts the result is not `None`"""
    return tag.select_one(selector)


def decompose(tag: bs4.Tag, selector: str) -> None:
    for inner_tag in tag.select(selector):
        inner_tag.decompose()


def get_td(tag: bs4.Tag, td_value: str) -> bs4.Tag:
    return select_one(tag, f"th:-soup-contains('{td_value}') + td")


def get_dd(tag: bs4.Tag, dt_value: str) -> bs4.Tag:
    return select_one(tag, f"dt:-soup-contains('{dt_value}') + dd")
