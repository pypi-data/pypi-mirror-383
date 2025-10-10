"""Settings Manager using BearBase backend."""

from __future__ import annotations

from contextlib import contextmanager
from typing import TYPE_CHECKING, Any, Self

from pydantic import BaseModel
from pydantic.fields import FieldInfo

from bear_dereth.datastore import BearBase
from bear_dereth.datastore.columns import Columns
from bear_dereth.datastore.record import NullRecord, NullRecords, Record, Records
from bear_dereth.datastore.storage import StorageChoices  # noqa: TC001
from bear_dereth.files import derive_settings_path
from bear_dereth.query.query_mapping import where
from bear_dereth.typing_tools import str_to_bool, str_to_type

if TYPE_CHECKING:
    from collections.abc import Generator, Iterator
    from pathlib import Path

    from bear_dereth.datastore.tables.table import Table


class SettingsModel(BaseModel):
    """Pydantic model for settings storage."""

    id: Columns[int] = Columns(name="id", type="int", default=0, primary_key=True, auto_increment=True)
    key: Columns[str] = Columns(name="key", type="str")
    value: Columns[str] = Columns(name="value", type="str")
    type: Columns[str] = Columns(name="type", type="str")

    def fields(self) -> list[str]:
        """Get the list of field names."""
        return list(type(self).model_fields.keys())

    def to_record(self, key: str, value: Any, cls_type: object) -> Record:
        """Convert the settings model instance to a Record."""
        return Record(
            {
                "id": 0,
                "key": key,
                "value": value,
                "type": cls_type.__name__ if hasattr(cls_type, "__name__") else str(cls_type),  # type: ignore[arg-type]
            }
        )


def get_columns(cls: SettingsModel) -> list[Columns]:
    """Get the list of columns for the settings model."""
    columns: list[Columns] = []
    for _, field in type(cls).model_fields.items():
        if isinstance(field, FieldInfo) and hasattr(field, "annotation") and issubclass(field.annotation, Columns):  # type: ignore[attr-defined]
            col: Columns = field.default
            # if the column field is missing its type, grab it from the type annotation
            if col.type is None and hasattr(field, "annotation") and hasattr(field.annotation, "__args__"):  # type: ignore[attr-defined]
                args = getattr(field.annotation, "__args__", ())
                if args and len(args) == 1:
                    col.type = args[0].__name__ if hasattr(args[0], "__name__") else str(args[0])  # type: ignore[attr-defined]
            if not isinstance(col, Columns):
                continue
            columns.append(col)
    return columns


class DefaultSettings(BaseModel):
    """Default settings schema."""

    default_name: str = "settings"
    default_table: type[SettingsModel] = SettingsModel
    storage_type: StorageChoices = "jsonl"


class BearSettings[T: BearBase]:
    """Settings manager backed by BearBase instead of temp storage."""

    __slots__: tuple = (
        "_db",
        "_default_table",
        "_settings",
        "_storage_type",
        "_table",
        "_table_name",
        "file_path",
        "name",
    )
    _default_settings: type[DefaultSettings] = DefaultSettings

    def __init__(
        self,
        name: str,
        file_name: str | None = None,
        path: Path | str | None = None,
        table_name: str | None = None,
        table: type[SettingsModel] | None = None,
        storage: StorageChoices = "json",
    ) -> None:
        """Initialize BearBase-backed settings manager.

        Args:
            name: Name of the settings
            file_name: Optional specific file name
            path: Optional path to settings file
            table_name: Optional specific table name
            table: Optional specific settings table model
            storage (StorageChoices): Storage backend type
        """
        self.name: str = name
        self._settings = self._default_settings()
        self._storage_type = storage or self._settings.storage_type
        self.file_path: Path = derive_settings_path(name, file_name, path, ext=self._storage_type)
        self._db: BearBase | None = None
        self._table_name: str = table_name or self._settings.default_name
        tbl: type[SettingsModel] = table or self._settings.default_table
        self._default_table: SettingsModel = tbl()
        self._table: Table | None = None

    @property
    def db(self) -> BearBase:
        """Get or create the database instance."""
        if self._db is None:
            self._db = BearBase(file=self.file_path, storage=self._storage_type)
            self._ensure_table()
        return self._db

    def _ensure_table(self) -> None:
        """Ensure settings table exists with proper schema."""
        if self._table_name not in self.db.tables():
            columns: list[Columns] = get_columns(self._default_table)
            self.db.create_table(name=self._table_name, columns=columns)

    @property
    def table(self) -> Table:
        """Get the settings table."""
        if self._table is None:
            self._ensure_table()
            self._table = self.db.table(self._table_name)
        return self._table

    @property
    def closed(self) -> bool:
        """Check if database is closed."""
        return self._db is None

    def get(self, key: str, default: Any = None) -> Any:
        """Get a setting value."""
        table: Table = self.db.table(self._table_name)
        result: Records = table.get(key=key)
        if result is not NullRecords:
            record: Record = result.first()
            if record is NullRecord:
                return default
            value_type: str = record.get("type", "str")
            value: Any = record["value"]
            if value_type == "NoneType" and value is None:
                return None
            return str_to_bool(value) if value_type == "bool" else str_to_type(value_type)(value)
        return default

    def set(self, key: str, value: Any, as_type: str | None = None) -> None:
        """Set a setting value."""
        record: Record = self._default_table.to_record(
            key, value, str_to_type(as_type) if as_type is not None else type(value)
        )
        if not self.has(key):
            self.table.insert(record=record)
            return
        del record["id"]
        self.table.upsert(record=record, cond=where("key") == key)

    def upsert(self, record: Any, **kwargs) -> None:
        """Upsert a setting value (alias for set)."""
        self.table.upsert(record=record, **kwargs)

    def get_all(self) -> dict[str, Any]:
        """Get all settings as dictionary."""
        return {rec["key"]: rec["value"] for rec in self.table.all()}

    def has(self, key: str) -> bool:
        """Check if setting exists."""
        return self.table.get(key=key) is not NullRecords

    def keys(self) -> list[str]:
        """Get all setting keys."""
        return list(self.get_all().keys())

    def values(self) -> list[Any]:
        """Get all setting values."""
        return list(self.get_all().values())

    def items(self) -> list[tuple[str, Any]]:
        """Get all key-value pairs."""
        return list(self.get_all().items())

    def close(self) -> None:
        """Close the database."""
        if self._db is not None:
            self._db.close()
            self._db = None

    def __getattr__(self, key: str) -> Any:
        """Handle dot notation access for settings."""
        if key in self.__slots__:
            raise AttributeError(f"'{key}' not initialized")
        if key.startswith("_"):
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{key}'")
        return self.get(key)

    def __setattr__(self, key: str, value: Any) -> None:
        """Handle dot notation assignment for settings."""
        if key in self.__slots__:
            object.__setattr__(self, key, value)
            return
        self.set(key=key, value=value)

    def __getitem__(self, key: str) -> Any:
        return self.get(key)

    def __setitem__(self, key: str, value: Any) -> None:
        self.set(key, value)

    def __enter__(self) -> Self:
        return self

    def __exit__(self, exc_type: object, exc_value: object, traceback: object) -> None:
        self.close()

    def __contains__(self, key: str) -> bool:
        return self.has(key)

    def __len__(self) -> int:
        return len(self.keys())

    def __iter__(self) -> Iterator[str]:
        return iter(self.keys())

    def __del__(self) -> None:
        self.close()

    def __bool__(self) -> bool:
        return not self.closed and len(self) > 0

    @property
    def _class_name(self) -> str:
        return self.__class__.__name__

    def __repr__(self) -> str:
        return f"<{self._class_name} name='{self.name}'>"

    def __str__(self) -> str:
        return f"{self._class_name} for '{self.name}' with {len(self)} settings."


@contextmanager
def settings(
    name: str,
    file_name: str | None = None,
    path: str | Path | None = None,
    **kwargs,
) -> Generator[BearSettings]:
    """Context manager for SettingsManager.

    Args:
        name: Name of the settings
        file_name: Optional specific file name
        path: Optional path to settings file
        **kwargs: Additional arguments for BearSettings
    """
    sm: BearSettings = BearSettings(name, file_name=file_name, path=path, **kwargs)
    try:
        yield sm
    finally:
        sm.close()


SettingsManager = BearSettings


__all__ = ["BearSettings", "SettingsManager", "settings"]

# if __name__ == "__main__":
#     sm = BearSettings("test")
#     import random

#     sm.set("a", 1)
#     sm.set("b", value=True)
#     sm.set("c", value=random.uniform(0, 1))
#     sm.set("d", value="hello")
#     sm.set("e", value=None)

#     print(sm.get_all())
