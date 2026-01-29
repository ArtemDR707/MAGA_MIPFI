from __future__ import annotations

from typing import Any

from primitive_db.constants import META_FILE
from primitive_db.utils import (
    cast_value,
    ensure_storage,
    get_table_cache,
    read_json,
    table_path,
    write_json,
)


class DbEngine:
    """Low-level storage engine: reads/writes meta and table files."""

    def __init__(self) -> None:
        ensure_storage()
        self._read_table_cached = get_table_cache()

    def load_meta(self) -> dict[str, Any]:
        meta = read_json(META_FILE)
        if "tables" not in meta or not isinstance(meta["tables"], dict):
            raise ValueError("Метаданные повреждены: отсутствует 'tables'.")
        return meta

    def save_meta(self, meta: dict[str, Any]) -> None:
        write_json(META_FILE, meta)

    def create_table(self, name: str, schema: dict[str, str]) -> None:
        meta = self.load_meta()
        if name in meta["tables"]:
            raise ValueError(f"Таблица уже существует: {name}")
        if "id" in schema:
            raise ValueError("Столбец 'id' создаётся автоматически, не указывай его.")

        full_schema = {"id": "int", **schema}
        meta["tables"][name] = {"schema": full_schema, "next_id": 1}
        self.save_meta(meta)
        write_json(table_path(name), [])

    def drop_table(self, name: str) -> None:
        meta = self.load_meta()
        if name not in meta["tables"]:
            raise ValueError(f"Таблица не найдена: {name}")

        meta["tables"].pop(name)
        self.save_meta(meta)

        import os

        path = table_path(name)
        if os.path.exists(path):
            os.remove(path)

    def list_tables(self) -> list[str]:
        meta = self.load_meta()
        return sorted(meta["tables"].keys())

    def get_schema(self, table: str) -> dict[str, str]:
        meta = self.load_meta()
        if table not in meta["tables"]:
            raise ValueError(f"Таблица не найдена: {table}")
        return dict(meta["tables"][table]["schema"])

    def _next_id(self, table: str) -> int:
        meta = self.load_meta()
        next_id = int(meta["tables"][table]["next_id"])
        meta["tables"][table]["next_id"] = next_id + 1
        self.save_meta(meta)
        return next_id

    def read_rows(self, table: str) -> list[dict[str, Any]]:
        _ = self.get_schema(table)
        return self._read_table_cached(table_path(table))

    def write_rows(self, table: str, rows: list[dict[str, Any]]) -> None:
        write_json(table_path(table), rows)

    def validate_and_build_row(self, table: str, assignments: dict[str, str]) -> dict[str, Any]:
        schema = self.get_schema(table)
        row: dict[str, Any] = {"id": self._next_id(table)}

        for col, typ in schema.items():
            if col == "id":
                continue
            if col not in assignments:
                raise ValueError(f"Не задано значение для столбца: {col}")
            row[col] = cast_value(typ, assignments[col])

        extra = set(assignments.keys()) - set(schema.keys())
        if extra:
            raise ValueError(f"Лишние столбцы: {sorted(extra)}")

        return row

    def cast_where_value(self, table: str, column: str, value_raw: str) -> Any:
        schema = self.get_schema(table)
        if column not in schema:
            raise ValueError(f"Неизвестный столбец: {column}")
        return cast_value(schema[column], value_raw)

    def cast_update_values(self, table: str, updates: dict[str, str]) -> dict[str, Any]:
        schema = self.get_schema(table)
        if "id" in updates:
            raise ValueError("Нельзя обновлять столбец id.")
        result: dict[str, Any] = {}
        for col, raw in updates.items():
            if col not in schema:
                raise ValueError(f"Неизвестный столбец: {col}")
            result[col] = cast_value(schema[col], raw)
        return result
