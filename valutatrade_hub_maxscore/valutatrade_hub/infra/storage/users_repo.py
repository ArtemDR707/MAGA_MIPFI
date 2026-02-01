"""Users repository backed by users.json."""

from pathlib import Path

from valutatrade_hub.core.models.user import User
from valutatrade_hub.infra.storage.json_store import JsonStore


class UsersRepository:
    """Persist users in JSON."""

    def __init__(self, path: Path) -> None:
        self._store = JsonStore(path)

    def _all(self) -> list[User]:
        raw = self._store.read() or []
        return [User.from_dict(x) for x in raw]

    def get(self, username: str) -> User | None:
        username = (username or "").strip()
        for u in self._all():
            if u.username == username:
                return u
        return None

    def add(self, user: User) -> None:
        users = self._all()
        users.append(user)
        self._store.write_atomic([u.to_dict() for u in users])
