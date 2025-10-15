from typing import Type, TypeVar, Optional, cast

T = TypeVar("T")


def as_type(obj: object, t: Type[T]) -> T:
    if not isinstance(obj, t):
        raise TypeError(
            f"Cannot cast object of type {type(obj).__name__} to {t.__name__}"
        )
    return cast(T, obj)


def try_as(obj: object, t: Type[T]) -> Optional[T]:
    return cast(Optional[T], obj) if isinstance(obj, t) else None


def is_of_type(obj: object, t: Type[T]) -> bool:
    return isinstance(obj, t)
