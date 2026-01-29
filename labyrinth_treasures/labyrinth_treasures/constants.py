from __future__ import annotations

from typing import Final, TypedDict


class RoomData(TypedDict, total=False):
    name: str
    description: str
    exits: dict[str, str]
    items: list[str]
    puzzle_question: str
    puzzle_answer: str
    puzzle_reward: str
    requires_item: str
    requires_any_of: list[str]
    unlocks_exit: str
    trap_chance: float
    trap_damage: int


WELCOME_TEXT: Final[str] = (
    "Добро пожаловать в «Лабиринт сокровищ»!\n"
    "Цель: найти сокровище и выбраться.\n"
    "Команды: help, look, go <dir>, take <item>, use <item>, solve, inventory, status, quit"
)

HELP_TEXT: Final[str] = (
    "Команды:\n"
    "  help                 — показать справку\n"
    "  look                 — осмотреть комнату\n"
    "  go <dir>             — пойти в направлении (north/south/east/west)\n"
    "  take <item>          — взять предмет\n"
    "  use <item>           — использовать предмет\n"
    "  solve                — решить загадку в комнате (если есть)\n"
    "  inventory            — показать инвентарь\n"
    "  status               — показать здоровье/статус\n"
    "  quit                 — выйти из игры"
)

DIRECTIONS: Final[set[str]] = {"north", "south", "east", "west"}

START_ROOM_ID: Final[str] = "entrance"

MAX_HP: Final[int] = 3

WIN_TREASURE_ITEM: Final[str] = "treasure"
WIN_EXIT_ROOM_ID: Final[str] = "entrance"


ROOMS: Final[dict[str, RoomData]] = {
    "entrance": {
        "name": "Вход",
        "description": "Вы стоите у входа в древний лабиринт. Позади — безопасный мир.",
        "exits": {"north": "hall"},
        "items": [],
    },
    "hall": {
        "name": "Зал эха",
        "description": "Шаги отдаются многократным эхом. На полу что-то блестит.",
        "exits": {"south": "entrance", "east": "library", "west": "armory"},
        "items": ["coin"],
        "trap_chance": 0.15,
        "trap_damage": 1,
    },
    "armory": {
        "name": "Оружейная",
        "description": "Старые стойки, ржавые цепи. На крюке висит ключ.",
        "exits": {"east": "hall"},
        "items": ["key"],
        "trap_chance": 0.10,
        "trap_damage": 1,
    },
    "library": {
        "name": "Библиотека",
        "description": "Пыльные книги. На столе записка: «Ответ откроет путь к сокровищу».",
        "exits": {"west": "hall", "north": "puzzle_room"},
        "items": ["note"],
    },
    "puzzle_room": {
        "name": "Комната загадки",
        "description": (
            "На стене высечен вопрос. Похоже, правильный ответ даст руну, "
            "которая может пригодиться у врат."
        ),
        "exits": {"south": "library", "east": "treasure_gate"},
        "items": [],
        "puzzle_question": "Что всегда растёт, но никогда не уменьшается?",
        "puzzle_answer": "возраст",
        "puzzle_reward": "rune",
        "requires_any_of": ["rune", "key"],
        "unlocks_exit": "east",
    },
    "treasure_gate": {
        "name": "Врата",
        "description": (
            "Тяжёлая дверь. На ней старый замок и символ руны. "
            "Открыть можно либо руной (rune), либо ключом (key)."
        ),
        "exits": {"west": "puzzle_room", "east": "treasure_room"},
        "items": [],
        "requires_any_of": ["rune", "key"],
        "unlocks_exit": "east",
        "trap_chance": 0.20,
        "trap_damage": 1,
    },
    "treasure_room": {
        "name": "Сокровищница",
        "description": "Сверкающие горы золота. В центре — главное сокровище.",
        "exits": {"west": "treasure_gate"},
        "items": ["treasure"],
        "trap_chance": 0.05,
        "trap_damage": 1,
    },
}
