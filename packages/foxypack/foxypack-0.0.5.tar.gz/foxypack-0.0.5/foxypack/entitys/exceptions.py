import traceback


class SocNetError(Exception):
    def __init__(self, message: str):
        super().__init__(message)
        self.stack = "".join(traceback.format_stack()[:-1])

    def __str__(self):
        return f"{super().__str__()}\nStack trace:\n{self.stack}"


class ValidationError(SocNetError, ValueError):
    pass


class ProxyValidationError(ValidationError):
    pass


class InstagramValidationError(ValidationError):
    pass


class TelegramValidationError(ValidationError):
    pass


class EntityError(SocNetError):
    pass


class NoAvailableEntityError(EntityError):
    pass


class EntityPermanentlyBlockedError(EntityError):
    pass


class StorageError(SocNetError):
    pass


class StorageLoadError(StorageError):
    pass


class StorageSaveError(StorageError):
    pass
