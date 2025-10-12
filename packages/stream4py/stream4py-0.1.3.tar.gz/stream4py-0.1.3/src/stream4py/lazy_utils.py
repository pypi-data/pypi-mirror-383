from __future__ import annotations

import functools
import time
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Generator
    from collections.abc import Iterable
    from typing import Callable
    from typing import TypeVar

    from typing_extensions import ParamSpec

    P = ParamSpec("P")
    R = TypeVar("R")


def lazy_yield() -> Callable[[Callable[P, R]], Callable[P, Generator[R]]]:
    def inner(func: Callable[P, R]) -> Callable[P, Generator[R]]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> Generator[R]:
            yield func(*args, **kwargs)

        return wrapper

    return inner


def lazy_yield_from() -> Callable[[Callable[P, Iterable[R]]], Callable[P, Generator[R]]]:
    def inner(func: Callable[P, Iterable[R]]) -> Callable[P, Generator[R]]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> Generator[R]:
            yield from func(*args, **kwargs)

        return wrapper

    return inner


def interval_lazy_yield(seconds: float) -> Callable[[Callable[P, R]], Callable[P, Generator[R]]]:
    def inner(func: Callable[P, R]) -> Callable[P, Generator[R]]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> Generator[R]:
            while True:
                yield func(*args, **kwargs)
                time.sleep(seconds)

        return wrapper

    return inner


def interval_lazy_yield_from(
    seconds: float,
) -> Callable[[Callable[P, Iterable[R]]], Callable[P, Generator[R]]]:
    def inner(func: Callable[P, Iterable[R]]) -> Callable[P, Generator[R]]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> Generator[R]:
            while True:
                yield from func(*args, **kwargs)
                time.sleep(seconds)

        return wrapper

    return inner
