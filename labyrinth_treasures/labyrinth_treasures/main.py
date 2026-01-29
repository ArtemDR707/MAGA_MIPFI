from __future__ import annotations

from labyrinth_treasures.constants import WELCOME_TEXT
from labyrinth_treasures.player_actions import (
    GameState,
    check_victory,
    describe_room,
    go,
    help_text,
    quit_game,
    show_inventory,
    show_status,
    solve,
    take,
    use,
)
from labyrinth_treasures.utils import init_rng, parse_command


def main() -> None:
    rng = init_rng()
    state = GameState()

    print(WELCOME_TEXT)
    print()
    print(describe_room(state))

    while not state.game_over:
        raw = input("\n> ")
        cmd = parse_command(raw)

        if cmd.name == "":
            print("Введите команду. help — список команд.")
            continue

        if cmd.name == "help":
            print(help_text())
            continue

        if cmd.name == "look":
            print(describe_room(state))
            continue

        if cmd.name == "inventory":
            print(show_inventory(state))
            continue

        if cmd.name == "status":
            print(show_status(state))
            continue

        if cmd.name == "go":
            print(go(state, cmd.arg, rng))
            check_victory(state)
            continue

        if cmd.name == "take":
            print(take(state, cmd.arg))
            check_victory(state)
            continue

        if cmd.name == "use":
            print(use(state, cmd.arg))
            check_victory(state)
            continue

        if cmd.name == "solve":
            print(solve(state))
            check_victory(state)
            continue

        if cmd.name == "quit":
            print(quit_game(state))
            break

        print("Неизвестная команда. help — список команд.")

    if state.victory:
        print("\n🏆 Победа! Вы вынесли сокровище и выбрались живым!")
    elif state.player.hp <= 0:
        print("\n☠️ Игра окончена: вы погибли в лабиринте.")
    else:
        print("\nИгра завершена.")


if __name__ == "__main__":
    main()
