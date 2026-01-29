from __future__ import annotations

import time
from functools import wraps
from typing import Any, Callable, TypeVar

T = TypeVar("T")


def handle_db_errors(func: Callable[..., T]) -> Callable[..., T | None]:
    """Catch common errors and print a readable message instead of crashing."""

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> T | None:
        try:
            return func(*args, **kwargs)
        except ValueError as exc:
            print(f"Ошибка: {exc}")
            return None
        except FileNotFoundError as exc:
            print(f"Файл не найден: {exc}")
            return None
        except KeyError as exc:
            print(f"Неизвестный ключ/поле: {exc}")
            return None

    return wrapper


def confirm_action(message: str) -> Callable[[Callable[..., T]], Callable[..., T | None]]:
    """Ask for confirmation before destructive operations (drop/delete)."""

    def decorator(func: Callable[..., T]) -> Callable[..., T | None]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T | None:
            answer = input(f"{message} [y/N]: ").strip().lower()
            if answer not in {"y", "yes"}:
                print("Отменено.")
                return None
            return func(*args, **kwargs)

        return wrapper

    return decorator


def log_time(func: Callable[..., T]) -> Callable[..., T]:
    """Measure and print execution time."""

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> T:
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed_ms = (time.perf_counter() - start) * 1000
        print(f"[time] {func.__name__}: {elapsed_ms:.2f} ms")
        return result

    return wrapper
