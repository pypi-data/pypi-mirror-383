import json
import uuid
from dataclasses import is_dataclass, fields
from enum import Enum
from pathlib import Path
from typing import Any, Type

from .validators import resolve_enum


class Storage:
    _registered_types: dict[str, [Any]] = {}

    def __init__(self, storage_path: str):
        self.path = Path(storage_path)

    def init(self, default_data: Any = None):
        try:
            if not self.path.exists():
                self.path.parent.mkdir(parents=True, exist_ok=True)
                if default_data is not None and not self._is_serializable(default_data):
                    raise ValueError(
                        "default_data must be a dataclass or a collection of datacasses."
                    )
                self.save(default_data if default_data is not None else {})
                return self.load() if default_data is not None else {}
            else:
                return self.load()
        except Exception as e:
            raise RuntimeError(f"Error processing the {self.path} file: {e}") from e

    def save(self, data: Any) -> None:
        try:
            serializable = self._to_serializable(data)
            with self.path.open("w", encoding="utf-8") as f:
                json.dump(serializable, f, ensure_ascii=False, indent=4)
        except Exception as e:
            raise RuntimeError(f"Error when saving to the {self.path} file: {e}") from e

    def load(self) -> Any:
        try:
            with self.path.open("r", encoding="utf-8") as f:
                raw = json.load(f)
            return self._from_serializable(raw)
        except Exception as e:
            raise RuntimeError(f"Error when uploading from the {self.path} file: {e}")

    @classmethod
    def register_type(cls, dataclass_type: Type[Any]) -> Type[Any]:
        cls._registered_types[dataclass_type.__name__] = dataclass_type
        return dataclass_type

    @classmethod
    def _is_serializable(cls, obj: Any) -> bool:
        if is_dataclass(obj):
            return True
        if isinstance(obj, list):
            return all(is_dataclass(item) for item in obj)
        if isinstance(obj, dict):
            return all(is_dataclass(item) for item in obj.values())
        return False

    @classmethod
    def _dict_to_dataclass(cls, data: dict) -> Any:
        type_name = data.get("__type__")
        dataclass_type = cls._registered_types.get(type_name)
        if not dataclass_type:
            raise ValueError(f"Unknown dataclass type: {type_name}")

        init_data = {}
        for field in fields(dataclass_type):
            value = data.get(field.name)
            init_data[field.name] = cls._from_serializable(value)
        return dataclass_type(**init_data)

    @classmethod
    def _to_serializable(cls, obj: Any) -> Any:
        if is_dataclass(obj):
            return cls._dataclass_to_dict(obj)
        if isinstance(obj, uuid.UUID):
            return {"__uuid__": str(obj)}
        if isinstance(obj, Enum):
            return {"__enum__": f"{obj.__class__.__name__}.{obj.name}"}
        if isinstance(obj, list):
            return [cls._to_serializable(item) for item in obj]
        if isinstance(obj, dict):
            return {str(k): cls._to_serializable(v) for k, v in obj.items()}
        return obj

    @classmethod
    def _dataclass_to_dict(cls, obj: Any) -> dict:
        result = {}
        for field in fields(obj):
            value = getattr(obj, field.name)
            result[field.name] = cls._to_serializable(value)
        result["__type__"] = type(obj).__name__
        return result

    @classmethod
    def _from_serializable(cls, data: Any) -> Any:
        if isinstance(data, list):
            return [cls._from_serializable(item) for item in data]
        if isinstance(data, dict):
            if "__uuid__" in data:
                return uuid.UUID(data["__uuid__"])
            if "__enum__" in data:
                return resolve_enum(data["__enum__"])
            if "__type__" in data:
                return cls._dict_to_dataclass(data)
            return {k: cls._from_serializable(v) for k, v in data.items()}
        return data
