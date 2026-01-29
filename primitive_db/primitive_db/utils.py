from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from primitive_db.constants import DATA_DIR, FALSE_VALUES, META_FILE, SUPPORTED_TYPES, TRUE_VALUES


def ensure_storage() -> None:
    """Create storage directory and meta file if needed."""
    Path(DATA_DIR).mkdir(parents=True, exist_ok=True)
    if not Path(META_FILE).exists():
        write_json(META_FILE, {"tables": {}})


def read_json(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: str, data: Any) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def table_path(table_name: str) -> str:
    return str(Path(DATA_DIR) / f"{table_name}.json")


def cast_value(type_name: str, raw: str) -> Any:
    """Cast string value to the declared type."""
    if type_name not in SUPPORTED_TYPES:
        raise ValueError(f"Неподдерживаемый тип: {type_name}")

    if type_name == "str":
        return raw

    if type_name == "bool":
        v = raw.strip().lower()
        if v in TRUE_VALUES:
            return True
        if v in FALSE_VALUES:
            return False
        raise ValueError(f"Невалидное bool значение: {raw}")

    py_type = SUPPORTED_TYPES[type_name]
    try:
        return py_type(raw)
    except Exception as exc:  # noqa: BLE001
        raise ValueError(f"Невалидное значение для {type_name}: {raw}") from exc


def get_table_cache():
    """Closure-based cache for reading table data (mtime-based)."""
    cache: dict[str, tuple[float, list[dict[str, Any]]]] = {}

    def read_table_cached(path: str) -> list[dict[str, Any]]:
        if not os.path.exists(path):
            return []
        mtime = os.path.getmtime(path)
        if path in cache and cache[path][0] == mtime:
            return cache[path][1]
        data = read_json(path)
        if not isinstance(data, list):
            raise ValueError("Файл таблицы повреждён (ожидался список записей).")
        cache[path] = (mtime, data)
        return data

    return read_table_cached
