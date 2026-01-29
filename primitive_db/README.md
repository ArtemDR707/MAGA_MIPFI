# Примитивная база данных (Primitive DB)

Файловая база данных с консольным интерфейсом: управление таблицами и CRUD-операции.
Хранение данных — в JSON-файлах в директории `data/`, метаданные — `db_meta.json`.

## Установка

Требования: Python 3.11+ и Poetry.

```bash
make install
```

## Запуск

```bash
make project
```

## Команды

### Таблицы
- `create_table <name> <col:type> <col:type> ...`
  - `id:int` добавляется автоматически.
  - типы: `int`, `float`, `str`, `bool`
- `drop_table <name>`
- `list_tables`

### Данные (CRUD)
- `insert <table> <col=value> <col=value> ...`
- `select <table> [where <col> <op> <value>]`
- `update <table> set <col=value>[,<col=value>...] [where <col> <op> <value>]`
- `delete <table> [where <col> <op> <value>]`

Операторы `op`: `=`, `!=`, `<`, `<=`, `>`, `>=`

Значения строк можно писать в кавычках:
- `name="Ivan Petrov"`

## Пример полного цикла (для asciinema)

1) `create_table users name:str age:int active:bool`
2) `insert users name="Ivan" age=30 active=true`
3) `select users`
4) `update users set age=31 where name = "Ivan"`
5) `delete users where id = 1` (будет подтверждение `confirm_action`)
6) `drop_table users`

## Демонстрация (asciinema)

Вставь ссылку на запись полного цикла (создание таблицы + все CRUD + confirm_action + удаление таблицы):

https://asciinema.org/a/<YOUR_CAST_ID>
