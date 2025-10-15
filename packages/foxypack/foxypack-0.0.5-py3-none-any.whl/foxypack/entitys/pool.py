import logging
import uuid
from typing import Type, Optional, Any, Union

from .entitys import Entity
from .storage import Storage
from .exceptions import (
    StorageLoadError,
    StorageSaveError,
    EntityPermanentlyBlockedError,
)
from .types import Status


class EntityPool:
    def __init__(self, path: Optional[str] = None):
        self._entities: dict[uuid.UUID, Entity] = {}
        self._in_use: set[uuid.UUID] = set()
        self._storage: Optional[Storage] = None

        if path:
            try:
                self._storage = Storage(path)
                data = self._storage.init()
                self._load_from_data(data)
            except Exception as e:
                raise StorageLoadError(
                    f"Storage initialization error on the path {path}: {e}"
                ) from e

    def add(self, entity: Entity):
        if any(
            self._is_duplicate(entity, existing) for existing in self._entities.values()
        ):
            logging.warning(f"The {entity} already exists and cannot be added again")
            return
        self._entities[entity.id] = entity
        self._save()

    def remove(self, entity_id: uuid.UUID):
        self._entities.pop(entity_id, None)
        self._in_use.discard(entity_id)
        self._save()

    def get_by_id(self, entity_id: uuid.UUID) -> Optional[Entity]:
        return self._entities.get(entity_id)

    def get_available_of_type(self, entity: Type[Entity]) -> list[Entity]:
        return [
            e.try_as(entity)
            for e in self._entities.values()
            if e.status == Status.WORKING
            and e.id not in self._in_use
            and e.is_of_type(entity)
        ]

    def mark_in_use(self, entity: Entity):
        entity.uses += 1
        self._in_use.add(entity.id)

    def release(self, entity: Entity):
        self._in_use.discard(entity.id)

    def mark_failure(self, entity: Entity):
        entity.fails += 1
        if entity.fails >= 5:
            entity.status = Status.PERMANENTLY_BLOCKED
            self._save()
            logging.warning(f"Entity {entity.id} permanently blocked")
        elif entity.fails >= 3:
            entity.status = Status.TEMPORARILY_BLOCKED
        self._save()

    def restore(self, entity: Entity):
        entity.status = Status.WORKING
        entity.fails = 0
        self._save()

    @staticmethod
    def check_entity(entity: Entity):
        if entity.status == Status.PERMANENTLY_BLOCKED:
            raise EntityPermanentlyBlockedError(
                f"Entity {entity.id} is permanently blocked"
            )

    def _is_duplicate(self, new_entity: Entity, existing_entity: Entity) -> bool:
        if type(new_entity) != type(existing_entity):
            return False
        fields = self._get_match_fields_for_type(type(new_entity))
        return all(
            getattr(new_entity, f) == getattr(existing_entity, f) for f in fields
        )

    def _load_from_data(self, data: Any):
        if isinstance(data, list):
            for entity in data:
                if isinstance(entity, Entity):
                    if not getattr(entity, "id", None) or str(entity.id).strip() == "":
                        entity.id = uuid.uuid4()
                    self._entities[entity.id] = entity

    def _save(self):
        if not self._storage:
            return
        try:
            self._storage.save(list(self._entities.values()))
        except Exception as e:
            raise StorageSaveError(f"Error saving: {e}") from e

    def _get_match_fields_for_type(self, t: type[Entity]) -> list[str]:
        if t.__name__ == "Proxy":
            return ["_proxy_str"]
        if t.__name__ == "TelegramAccount":
            return ["_api_id", "_api_hash"]
        if t.__name__ == "InstagramAccount":
            return ["_login"]
        return ["id"]
