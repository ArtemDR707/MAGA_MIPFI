"""Storage helpers for parser service (current rates + history)."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from valutatrade_hub.infra.storage.json_store import JsonStore


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class RatesStorage:
    """Write current rates doc and append to history."""

    def __init__(self, rates_path: Path, history_path: Path) -> None:
        self._rates_store = JsonStore(rates_path)
        self._history_store = JsonStore(history_path)

    def write_rates(self, base: str, ttl_seconds: int, rates: dict[str, float], errors: list[str]) -> None:
        now = utc_now_iso()
        doc = {
            "base": base,
            "updated_at": now,
            "last_refresh": now,
            "ttl_seconds": ttl_seconds,
            "rates": rates,
            "errors": errors,
        }
        self._rates_store.write_atomic(doc)

        history = self._history_store.read() or []
        history.append({"updated_at": now, "base": base, "rates": rates, "errors": errors})
        self._history_store.write_atomic(history)
