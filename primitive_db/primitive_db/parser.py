from __future__ import annotations

import shlex
from dataclasses import dataclass
from typing import Any, Iterable

from primitive_db.constants import SUPPORTED_TYPES


@dataclass(frozen=True)
class ParsedCommand:
    name: str
    args: list[str]


@dataclass(frozen=True)
class WhereClause:
    column: str
    op: str
    value_raw: str


OPS = {"=", "!=", "<", "<=", ">", ">="}


def parse_command(raw: str) -> ParsedCommand:
    raw = raw.strip()
    if not raw:
        return ParsedCommand(name="", args=[])
    parts = shlex.split(raw)
    return ParsedCommand(name=parts[0], args=parts[1:])


def parse_col_types(items: Iterable[str]) -> dict[str, str]:
    schema: dict[str, str] = {}
    for token in items:
        if ":" not in token:
            raise ValueError(f"Ожидалось <col:type>, получено: {token}")
        col, typ = token.split(":", 1)
        col = col.strip()
        typ = typ.strip()
        if not col:
            raise ValueError("Пустое имя столбца.")
        if typ not in SUPPORTED_TYPES:
            raise ValueError(f"Неподдерживаемый тип: {typ}")
        if col in schema:
            raise ValueError(f"Повтор столбца: {col}")
        schema[col] = typ
    return schema


def parse_assignments(tokens: list[str]) -> dict[str, str]:
    """Parse col=value pairs."""
    result: dict[str, str] = {}
    for t in tokens:
        if "=" not in t:
            raise ValueError(f"Ожидалось col=value, получено: {t}")
        col, val = t.split("=", 1)
        col = col.strip()
        if not col:
            raise ValueError("Пустое имя столбца в присваивании.")
        result[col] = val
    return result


def split_set_tokens(args: list[str]) -> tuple[list[str], list[str]]:
    """Split update args into set part and optional where part."""
    if not args or args[0].lower() != "set":
        raise ValueError("Ожидалось: update <table> set ...")

    joined = " ".join(args[1:])
    before_where, sep, after_where = joined.partition(" where ")
    set_part = [x.strip() for x in before_where.split(",") if x.strip()]
    where_part = shlex.split(after_where) if sep else []
    return set_part, where_part


def parse_where(tokens: list[str]) -> WhereClause:
    if len(tokens) < 3:
        raise ValueError("Ожидалось: where <col> <op> <value>")
    column, op, value_raw = tokens[0], tokens[1], tokens[2]
    if op not in OPS:
        raise ValueError(f"Неверный оператор where: {op}")
    return WhereClause(column=column, op=op, value_raw=value_raw)


def compare(left: Any, op: str, right: Any) -> bool:
    if op == "=":
        return left == right
    if op == "!=":
        return left != right
    if op == "<":
        return left < right
    if op == "<=":
        return left <= right
    if op == ">":
        return left > right
    if op == ">=":
        return left >= right
    raise ValueError(f"Неверный оператор: {op}")
