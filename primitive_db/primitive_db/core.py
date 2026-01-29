from __future__ import annotations

from prettytable import PrettyTable

from primitive_db.decorators import confirm_action, handle_db_errors, log_time
from primitive_db.engine import DbEngine
from primitive_db.parser import WhereClause, compare


class DbCore:
    """Business logic layer: executes commands using DbEngine."""

    def __init__(self, engine: DbEngine) -> None:
        self.engine = engine

    @handle_db_errors
    @log_time
    def create_table(self, name: str, schema: dict[str, str]) -> None:
        self.engine.create_table(name, schema)
        print(f"Таблица создана: {name}")

    @handle_db_errors
    @confirm_action("Удалить таблицу?")
    @log_time
    def drop_table(self, name: str) -> None:
        self.engine.drop_table(name)
        print(f"Таблица удалена: {name}")

    @handle_db_errors
    @log_time
    def list_tables(self) -> None:
        tables = self.engine.list_tables()
        if not tables:
            print("Таблиц нет.")
            return
        t = PrettyTable()
        t.field_names = ["tables"]
        for name in tables:
            t.add_row([name])
        print(t)

    @handle_db_errors
    @log_time
    def insert(self, table: str, assignments: dict[str, str]) -> None:
        row = self.engine.validate_and_build_row(table, assignments)
        rows = self.engine.read_rows(table)
        rows.append(row)
        self.engine.write_rows(table, rows)
        print("OK (insert)")

    @handle_db_errors
    @log_time
    def select(self, table: str, where_clause: WhereClause | None) -> None:
        rows = self.engine.read_rows(table)

        where = None
        if where_clause is not None:
            value = self.engine.cast_where_value(table, where_clause.column, where_clause.value_raw)
            where = (where_clause.column, where_clause.op, value)

        result = rows if where is None else [r for r in rows if compare(r.get(where[0]), where[1], where[2])]
        schema = self.engine.get_schema(table)

        if not result:
            print("Пусто.")
            return

        t = PrettyTable()
        t.field_names = list(schema.keys())
        for r in result:
            t.add_row([r.get(c) for c in schema.keys()])
        print(t)

    @handle_db_errors
    @log_time
    def update(self, table: str, updates_raw: dict[str, str], where_clause: WhereClause | None) -> None:
        rows = self.engine.read_rows(table)

        where = None
        if where_clause is not None:
            value = self.engine.cast_where_value(table, where_clause.column, where_clause.value_raw)
            where = (where_clause.column, where_clause.op, value)

        updates = self.engine.cast_update_values(table, updates_raw)

        updated = 0
        for r in rows:
            if where is None or compare(r.get(where[0]), where[1], where[2]):
                r.update(updates)
                updated += 1

        self.engine.write_rows(table, rows)
        print(f"OK (update): {updated} rows")

    @handle_db_errors
    @confirm_action("Удалить записи?")
    @log_time
    def delete(self, table: str, where_clause: WhereClause | None) -> None:
        rows = self.engine.read_rows(table)

        if where_clause is None:
            self.engine.write_rows(table, [])
            print(f"OK (delete): {len(rows)} rows")
            return

        value = self.engine.cast_where_value(table, where_clause.column, where_clause.value_raw)
        where = (where_clause.column, where_clause.op, value)

        kept = [r for r in rows if not compare(r.get(where[0]), where[1], where[2])]
        deleted = len(rows) - len(kept)
        self.engine.write_rows(table, kept)
        print(f"OK (delete): {deleted} rows")
