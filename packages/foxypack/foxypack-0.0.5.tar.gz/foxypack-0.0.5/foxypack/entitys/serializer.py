from enum import Enum
from typing import Type


class EnumSerializer:
    _registered_enums: dict[str, Type[Enum]] = {}

    @classmethod
    def register_enum(cls, enum_cls: Type[Enum]):
        cls._registered_enums[enum_cls.__name__] = enum_cls
        return enum_cls

    @staticmethod
    def resolve_enum(enum_str: str) -> Enum:
        enum_class_name, member_name = enum_str.split(".")
        enum_cls = EnumSerializer._registered_enums.get(enum_class_name)
        if enum_cls is None:
            raise ValueError(
                f"The registered Enum class was not found: {enum_class_name}"
            )
        return enum_cls[member_name]
