from .validators import (
    validate_proxy,
    validate_telegram_session_token,
    validate_telegram_api_hash,
    validate_telegram_api_id,
)


class StrProxyDescriptor:
    def __init__(self, *, default: str | None):
        self._default = default

    def __set_name__(self, owner, name):
        self._name = "_" + name

    def __get__(self, obj, type):
        if obj is None:
            return self._default

        return getattr(obj, self._name, self._default)

    def __set__(self, obj, value):
        validate_proxy(value)
        setattr(obj, self._name, value)

    def __str__(self):
        return self._default


class IntTelegramApiIdDescriptor:
    def __init__(self, *, default: int | None):
        self._default = default

    def __set_name__(self, owner, name):
        self._name = "_" + name

    def __get__(self, obj, type):
        if obj is None:
            return self._default
        return getattr(obj, self._name, self._default)

    def __set__(self, obj, value: int):
        validate_telegram_api_id(value)
        setattr(obj, self._name, value)
        obj.ping_change()


class StrTelegramApiHashDescriptor:
    def __init__(self, *, default: str | None):
        self._default = default

    def __set_name__(self, owner, name):
        self._name = "_" + name

    def __get__(self, obj, type):
        if obj is None:
            return self._default
        return getattr(obj, self._name, self._default)

    def __set__(self, obj, value: str):
        validate_telegram_api_hash(value)
        setattr(obj, self._name, value)
        obj.ping_change()


class StrTelegramTokenSessionDescriptor:
    def __init__(self, *, default: str | None):
        self._default = default

    def __set_name__(self, owner, name):
        self._name = "_" + name

    def __get__(self, obj, type):
        if obj is None:
            return self._default
        return getattr(obj, self._name, self._default)

    def __set__(self, obj, value: str):
        validate_telegram_session_token(value)
        setattr(obj, self._name, value)
        obj.ping_change()


class BoolTelegramIsInitializedDescriptor:
    def __init__(self, *, default: bool | None):
        self._default = default

    def __set_name__(self, owner, name):
        self._name = "_" + name

    def __get__(self, obj, type):
        if obj is None:
            return self._default
        return getattr(obj, self._name, self._default)

    def __set__(self, obj, value: bool):
        self._is_initialized = value  # No specific validation function provided for this. If there is, add it here.
        setattr(obj, self._name, value)
        obj.ping_change()
