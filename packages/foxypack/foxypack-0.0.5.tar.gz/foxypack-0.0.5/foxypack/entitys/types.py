from abc import abstractmethod
from enum import Enum
from typing import Type, Optional, cast

from .casting import T
from .serializer import EnumSerializer


@EnumSerializer.register_enum
class Status(Enum):
    WORKING = 0
    TEMPORARILY_BLOCKED = 1
    PERMANENTLY_BLOCKED = 2


class CastableMixin:
    def as_type(self, t: Type[T]) -> T:
        if not isinstance(self, t):
            raise TypeError(f"Cannot cast {type(self).__name__} to {t.__name__}")
        return cast(T, self)

    def try_as(self, t: Type[T]) -> Optional[T]:
        return cast(Optional[T], self) if isinstance(self, t) else None

    def is_of_type(self, t: Type[T]) -> bool:
        return isinstance(self, t)


class EntityListenerMixin:
    @abstractmethod
    def notify(self):
        pass
