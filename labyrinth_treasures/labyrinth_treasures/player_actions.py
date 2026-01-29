from __future__ import annotations

from dataclasses import dataclass, field

from labyrinth_treasures.constants import (
    HELP_TEXT,
    MAX_HP,
    ROOMS,
    START_ROOM_ID,
    WIN_EXIT_ROOM_ID,
    WIN_TREASURE_ITEM,
)
from labyrinth_treasures.utils import format_list, normalize_direction, normalize_item


@dataclass
class Player:
    room_id: str = START_ROOM_ID
    hp: int = MAX_HP
    inventory: list[str] = field(default_factory=list)


@dataclass
class GameState:
    player: Player = field(default_factory=Player)
    game_over: bool = False
    victory: bool = False
    solved_puzzles: set[str] = field(default_factory=set)
    unlocked_exits: dict[str, set[str]] = field(default_factory=dict)


def is_exit_unlocked(state: GameState, room_id: str, direction: str) -> bool:
    return direction in state.unlocked_exits.get(room_id, set())


def unlock_exit(state: GameState, room_id: str, direction: str) -> None:
    state.unlocked_exits.setdefault(room_id, set()).add(direction)


def get_room(room_id: str) -> dict:
    return ROOMS[room_id]


def help_text() -> str:
    return HELP_TEXT


def describe_room(state: GameState) -> str:
    room = get_room(state.player.room_id)
    items = room.get("items", [])
    exits = room.get("exits", {})

    lines = [
        f"== {room['name']} ==",
        room["description"],
        f"Выходы: {format_list(exits.keys())}",
        f"Предметы: {format_list(items)}",
    ]

    if "puzzle_question" in room and state.player.room_id not in state.solved_puzzles:
        lines.append("Здесь есть загадка. Команда: solve")

    return "\n".join(lines)


def show_inventory(state: GameState) -> str:
    return f"Инвентарь: {format_list(state.player.inventory)}"


def show_status(state: GameState) -> str:
    return f"HP: {state.player.hp}/{MAX_HP} | Победа: {state.victory} | Game Over: {state.game_over}"


def apply_trap_if_needed(state: GameState, rng) -> str | None:
    room = get_room(state.player.room_id)
    chance = float(room.get("trap_chance", 0.0))
    if chance <= 0:
        return None

    if rng.random() < chance:
        damage = int(room.get("trap_damage", 1))
        state.player.hp -= damage
        if state.player.hp <= 0:
            state.player.hp = 0
            state.game_over = True
            return f"ЛОВУШКА! Урон: -{damage}. Вы погибли."
        return f"ЛОВУШКА! Урон: -{damage}. HP: {state.player.hp}/{MAX_HP}"

    return None


def random_event(state: GameState, rng) -> str | None:
    """Random events that slightly affect the player but do not break the game."""

    if state.game_over or state.victory:
        return None

    if rng.random() >= 0.10:
        return None

    if rng.random() < 0.5:
        state.player.inventory.append("coin")
        return "Случайное событие: вы нашли монетку (coin)!"

    if "coin" in state.player.inventory:
        state.player.inventory.remove("coin")
        return "Случайное событие: вы выронили монетку (coin)!"

    return "Случайное событие: странный шорох в темноте..."


def go(state: GameState, direction_raw: str | None, rng) -> str:
    direction = normalize_direction(direction_raw)
    if direction is None:
        return "Неверное направление. Используй: north/south/east/west"

    room = get_room(state.player.room_id)
    exits = room.get("exits", {})
    if direction not in exits:
        return "Туда пройти нельзя."

    unlocks_exit = room.get("unlocks_exit")
    requires_any_of = room.get("requires_any_of", [])

    if unlocks_exit == direction and requires_any_of and not is_exit_unlocked(state, state.player.room_id, direction):
        needed = ", ".join(requires_any_of)
        return (
            f"Проход закрыт. Нужен один из предметов: {needed}. "
            f"Используй: use <item> или реши загадку (если она есть)."
        )

    state.player.room_id = exits[direction]

    trap_msg = apply_trap_if_needed(state, rng)
    if trap_msg is not None:
        return f"{trap_msg}\n\n{describe_room(state)}"

    event_msg = random_event(state, rng)
    if event_msg is not None:
        return f"{event_msg}\n\n{describe_room(state)}"

    return describe_room(state)


def take(state: GameState, item_raw: str | None) -> str:
    item = normalize_item(item_raw)
    if item is None:
        return "Укажи предмет: take <item>"

    room = get_room(state.player.room_id)
    items = room.get("items", [])

    if item not in items:
        return "Такого предмета здесь нет."

    items.remove(item)
    state.player.inventory.append(item)
    return f"Вы взяли предмет: {item}"


def use(state: GameState, item_raw: str | None) -> str:
    item = normalize_item(item_raw)
    if item is None:
        return "Укажи предмет: use <item>"

    if item not in state.player.inventory:
        return "У вас нет этого предмета."

    # Если предмет подходит для открытия текущего закрытого прохода — используем его по назначению.
    room_id = state.player.room_id
    room = get_room(room_id)
    unlocks_exit = room.get("unlocks_exit")
    requires_any_of = room.get("requires_any_of", [])

    if (
        unlocks_exit
        and item in requires_any_of
        and not is_exit_unlocked(state, room_id, unlocks_exit)
    ):
        unlock_exit(state, room_id, unlocks_exit)
        state.player.inventory.remove(item)
        return f"Вы использовали {item} и открыли проход: {unlocks_exit}."

    if item == "key":
        if state.player.hp >= MAX_HP:
            return "Вы и так в полном порядке."
        state.player.hp += 1
        state.player.inventory.remove(item)
        return f"Вы использовали key и восстановили 1 HP. Сейчас HP: {state.player.hp}/{MAX_HP}"

    return f"Предмет {item} сейчас нельзя использовать напрямую."


def solve(state: GameState) -> str:
    room_id = state.player.room_id
    room = get_room(room_id)

    if "puzzle_question" not in room:
        return "Здесь нет загадки."

    if room_id in state.solved_puzzles:
        return "Вы уже решили загадку здесь."

    question = room["puzzle_question"]
    expected = room["puzzle_answer"].strip().lower()

    user_answer = input(f"Загадка: {question}\nОтвет: ").strip().lower()
    if user_answer != expected:
        return "Неверно. Попробуйте позже."

    state.solved_puzzles.add(room_id)

    unlocks_exit = room.get("unlocks_exit")
    if unlocks_exit:
        unlock_exit(state, room_id, unlocks_exit)

    reward = room.get("puzzle_reward")
    if reward:
        state.player.inventory.append(reward)
        return f"Верно! Вы получили награду: {reward}"

    return "Верно! Загадка решена."


def check_victory(state: GameState) -> None:
    if WIN_TREASURE_ITEM in state.player.inventory and state.player.room_id == WIN_EXIT_ROOM_ID:
        state.victory = True
        state.game_over = True


def quit_game(state: GameState) -> str:
    state.game_over = True
    return "Вы вышли из игры."
