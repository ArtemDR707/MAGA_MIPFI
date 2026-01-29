from __future__ import annotations

from primitive_db.constants import PROMPT_TEXT, WELCOME_TEXT
from primitive_db.core import DbCore
from primitive_db.engine import DbEngine
from primitive_db.parser import (
    ParsedCommand,
    parse_assignments,
    parse_col_types,
    parse_command,
    parse_where,
    split_set_tokens,
)


def _read_input() -> str:
    try:
        from prompt_toolkit import prompt  # type: ignore

        return prompt(PROMPT_TEXT)
    except Exception:  # noqa: BLE001
        return input(PROMPT_TEXT)


def print_help() -> None:
    print(
        "Команды:\n"
        "  help\n"
        "  create_table <name> <col:type> <col:type> ...\n"
        "  drop_table <name>\n"
        "  list_tables\n"
        "  insert <table> <col=value> ...\n"
        "  select <table> [where <col> <op> <value>]\n"
        "  update <table> set <col=value>[,<col=value>...] [where <col> <op> <value>]\n"
        "  delete <table> [where <col> <op> <value>]\n"
        "  quit\n"
    )


def main() -> None:
    engine = DbEngine()
    core = DbCore(engine)

    print(WELCOME_TEXT)

    while True:
        raw = _read_input()
        cmd = parse_command(raw)
        if cmd.name == "":
            continue

        name = cmd.name.lower()

        if name in {"quit", "exit"}:
            print("Пока!")
            return

        if name == "help":
            print_help()
            continue

        try:
            dispatch(core, cmd)
        except ValueError as exc:
            print(f"Ошибка: {exc}")


def dispatch(core: DbCore, cmd: ParsedCommand) -> None:
    name = cmd.name.lower()
    args = cmd.args

    if name == "create_table":
        if len(args) < 1:
            raise ValueError("create_table <name> <col:type> ...")
        table = args[0]
        schema = parse_col_types(args[1:])
        core.create_table(table, schema)
        return

    if name == "drop_table":
        if len(args) != 1:
            raise ValueError("drop_table <name>")
        core.drop_table(args[0])
        return

    if name == "list_tables":
        if args:
            raise ValueError("list_tables (без аргументов)")
        core.list_tables()
        return

    if name == "insert":
        if len(args) < 2:
            raise ValueError("insert <table> <col=value> ...")
        table = args[0]
        assigns = parse_assignments(args[1:])
        core.insert(table, assigns)
        return

    if name == "select":
        if len(args) < 1:
            raise ValueError("select <table> [where ...]")
        table = args[0]
        where_clause = None
        if len(args) > 1:
            if args[1].lower() != "where":
                raise ValueError("select: ожидается 'where'")
            where_clause = parse_where(args[2:])
        core.select(table, where_clause)
        return

    if name == "update":
        if len(args) < 2:
            raise ValueError("update <table> set ...")
        table = args[0]
        set_part, where_tokens = split_set_tokens(args[1:])
        updates = parse_assignments(set_part)
        where_clause = parse_where(where_tokens) if where_tokens else None
        core.update(table, updates, where_clause)
        return

    if name == "delete":
        if len(args) < 1:
            raise ValueError("delete <table> [where ...]")
        table = args[0]
        where_clause = None
        if len(args) > 1:
            if args[1].lower() != "where":
                raise ValueError("delete: ожидается 'where'")
            where_clause = parse_where(args[2:])
        core.delete(table, where_clause)
        return

    raise ValueError("Неизвестная команда. help — список команд.")
