import time
import uuid
from abc import ABC
from dataclasses import dataclass, field

from .entity_descriptors import (
    StrProxyDescriptor,
    IntTelegramApiIdDescriptor,
    StrTelegramApiHashDescriptor,
    StrTelegramTokenSessionDescriptor,
    BoolTelegramIsInitializedDescriptor,
)
from .storage import Storage
from .types import CastableMixin, EntityListenerMixin, Status
from .validators import validate_count


@dataclass
class Entity(ABC, CastableMixin):
    id: uuid.UUID = uuid.uuid4()
    _subscribers: list[EntityListenerMixin] | None = None
    _uses: int = 0
    _fails: int = 0
    _status: Status = Status.WORKING
    _in_use: bool = False
    _last_used: float = field(default_factory=time.time)

    @property
    def subscribers(self):
        return self._subscribers

    @subscribers.setter
    def subscribers(self, value: list[EntityListenerMixin]):
        self._subscribers = value

    @property
    def uses(self):
        return self._uses

    @uses.setter
    def uses(self, value: int):
        validate_count(value, "Number of uses")
        self._uses = value
        # self.ping_change()

    @property
    def fails(self):
        return self._fails

    @fails.setter
    def fails(self, value: int):
        validate_count(value, "Number of fails")
        self._fails = value
        # self.ping_change()

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value: Status):
        self._status = value
        # self.ping_change()

    @property
    def in_use(self):
        return self._in_use

    @in_use.setter
    def in_use(self, value: bool):
        self._in_use = value
        # self.ping_change()

    @property
    def last_used(self):
        return self._last_used

    @last_used.setter
    def last_used(self, value):
        self._last_used = value
        # self.ping_change()

    def add_subscriber(self, subscriber):
        if self.subscribers is None:
            self.subscribers = []
        self.subscribers.append(subscriber)

    def ping_change(self):
        if self.subscribers:
            for subscriber in self.subscribers:
                subscriber.notify()
