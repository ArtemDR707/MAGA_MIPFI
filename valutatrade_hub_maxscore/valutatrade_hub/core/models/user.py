"""User model with salted password hashing."""

from __future__ import annotations

import hashlib
import secrets
from dataclasses import dataclass
from datetime import datetime, timezone

from valutatrade_hub.core.exceptions import ValidationError

MIN_PASSWORD_LEN = 8


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class User:
    """User domain entity.

    Attributes are stored as "private" to prevent accidental leakage (e.g. password hash).
    """

    _username: str
    _password_hash: str
    _salt: str
    _registered_at: datetime

    @classmethod
    def register(cls, username: str, password: str) -> "User":
        """Create a new user instance after validation and hashing."""
        username = (username or "").strip()
        if not username:
            raise ValidationError("Имя пользователя не должно быть пустым.")
        if len(password) < MIN_PASSWORD_LEN:
            raise ValidationError(f"Пароль должен быть минимум {MIN_PASSWORD_LEN} символов.")

        salt = secrets.token_hex(16)
        password_hash = cls._hash_password(password=password, salt=salt)
        return cls(
            _username=username,
            _password_hash=password_hash,
            _salt=salt,
            _registered_at=_utc_now(),
        )

    @staticmethod
    def _hash_password(password: str, salt: str) -> str:
        return hashlib.sha256((salt + password).encode("utf-8")).hexdigest()

    @property
    def username(self) -> str:
        """Username (public)."""
        return self._username

    @property
    def registered_at(self) -> datetime:
        """UTC registration datetime."""
        return self._registered_at

    def verify_password(self, password: str) -> bool:
        """Verify input password."""
        return self._password_hash == self._hash_password(password=password, salt=self._salt)

    def get_user_info(self) -> dict:
        """Public user info without sensitive fields."""
        return {
            "username": self._username,
            "registered_at": self._registered_at.isoformat(),
        }

    def to_dict(self) -> dict:
        """Serialize to JSON-compatible dict (includes hash and salt)."""
        return {
            "username": self._username,
            "password_hash": self._password_hash,
            "salt": self._salt,
            "registered_at": self._registered_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "User":
        """Deserialize from dict."""
        return cls(
            _username=data["username"],
            _password_hash=data["password_hash"],
            _salt=data["salt"],
            _registered_at=datetime.fromisoformat(data["registered_at"]),
        )
