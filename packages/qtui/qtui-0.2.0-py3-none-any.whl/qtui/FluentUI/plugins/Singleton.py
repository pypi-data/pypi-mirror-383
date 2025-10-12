# ruff: noqa: N815 N802

from collections.abc import Callable
from typing import Any, TypeVar

T = TypeVar("T")


# noinspection PyPep8Naming
def Singleton(cls: type[T]) -> Callable[..., T]:
    instances: dict[type[T], T] = {}

    def wrapper(*args: Any, **kwargs: Any) -> T:
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return wrapper
