"""Session store (current user) for CLI UX."""

from pathlib import Path

from valutatrade_hub.infra.storage.json_store import JsonStore


class SessionStore:
    """Persist current logged-in user in data/session.json."""

    def __init__(self, path: Path) -> None:
        self._store = JsonStore(path)

    def set_user(self, username: str) -> None:
        self._store.write_atomic({"username": username})

    def get_user(self) -> str | None:
        doc = self._store.read() or {}
        return doc.get("username")

    def clear(self) -> None:
        self._store.write_atomic({})
