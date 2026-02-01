"""Rates repository backed by rates.json."""

from pathlib import Path

from valutatrade_hub.infra.storage.json_store import JsonStore


class RatesRepository:
    """Read/write current rates doc."""

    def __init__(self, path: Path) -> None:
        self._store = JsonStore(path)

    def read(self) -> dict:
        doc = self._store.read()
        if doc is None:
            raise RuntimeError("rates.json не найден. Запустите update-rates.")
        return doc

    def write(self, doc: dict) -> None:
        self._store.write_atomic(doc)
