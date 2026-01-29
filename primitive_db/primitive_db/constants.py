from __future__ import annotations

from typing import Final

DATA_DIR: Final[str] = "data"
META_FILE: Final[str] = "db_meta.json"

SUPPORTED_TYPES: Final[dict[str, type]] = {
    "int": int,
    "float": float,
    "str": str,
    "bool": bool,
}

TRUE_VALUES: Final[set[str]] = {"true", "1", "yes", "y", "t"}
FALSE_VALUES: Final[set[str]] = {"false", "0", "no", "n", "f"}

PROMPT_TEXT: Final[str] = "db> "
WELCOME_TEXT: Final[str] = (
    "Primitive DB\n"
    "Команды: help, create_table, drop_table, list_tables, insert, select, update, delete, quit\n"
    "Подсказка: help"
)
