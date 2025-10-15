import asyncio
import uuid
from datetime import timedelta
from typing import Type

from .entitys import Entity
from .pool import EntityPool
from .exceptions import EntityPermanentlyBlockedError
from .types import Status


class BaseEntityBalancer:
    def __init__(self, pool: EntityPool):
        self.pool = pool

    def get(self, entity: Type[Entity]) -> Entity:
        candidates = self.pool.get_available_of_type(entity)
        if not candidates:
            raise LookupError(
                f"There are no available entities of the {entity.__name__} type"
            )
        entity = candidates[0]
        self.pool.check_entity(entity)
        self.pool.mark_in_use(entity)
        return entity

    def release(self, entity: Entity):
        self.pool.release(entity)

    def mark_failure(self, entity: Entity):
        self.pool.mark_failure(entity)
        self.pool.release(entity)

    def restore(self, entity: Entity):
        self.pool.restore(entity)


class AsyncEntityBalancer(BaseEntityBalancer):
    def __init__(self, pool: EntityPool, refresh_time: timedelta):
        super().__init__(pool)
        self.refresh_time = refresh_time
        self._refresh_tasks: dict[uuid.UUID, asyncio.Task] = {}

    def mark_failure(self, entity: Entity):
        try:
            self.pool.mark_failure(entity)
        except EntityPermanentlyBlockedError:
            raise
        finally:
            self.pool.release(entity)
        if (
            entity.status == Status.TEMPORARILY_BLOCKED
            and entity.id not in self._refresh_tasks
        ):
            task = asyncio.create_task(self._refresh_later(entity))
            self._refresh_tasks[entity.id] = task

    async def _refresh_later(self, entity: Entity):
        try:
            await asyncio.sleep(self.refresh_time.total_seconds())
            self.pool.restore(entity)
        finally:
            await self._refresh_tasks.pop(entity.id, None)
