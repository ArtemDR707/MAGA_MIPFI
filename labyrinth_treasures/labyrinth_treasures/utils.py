from __future__ import annotations

import os
import random
from dataclasses import dataclass
from typing import Iterable

from labyrinth_treasures.constants import DIRECTIONS


@dataclass(frozen=True)
class Command:
    name: str
    arg: str | None = None


def init_rng() -> random.Random:
    """Initialize RNG.

    If environment variable SEED is set, randomness becomes deterministic (useful for tests).
    """

    seed_raw = os.getenv("SEED")
    if seed_raw is None:
        return random.Random()

    try:
        seed = int(seed_raw)
    except ValueError:
        seed = sum(ord(ch) for ch in seed_raw)

    return random.Random(seed)


def parse_command(raw: str) -> Command:
    raw = raw.strip()
    if not raw:
        return Command(name="")

    parts = raw.split(maxsplit=1)
    name = parts[0].lower()
    arg = parts[1].strip() if len(parts) == 2 else None
    return Command(name=name, arg=arg)


def normalize_direction(direction: str | None) -> str | None:
    if direction is None:
        return None
    d = direction.lower().strip()
    return d if d in DIRECTIONS else None


def normalize_item(item: str | None) -> str | None:
    if item is None:
        return None
    it = item.lower().strip()
    return it if it else None


def format_list(items: Iterable[str]) -> str:
    items_list = list(items)
    if not items_list:
        return "—"
    return ", ".join(items_list)
