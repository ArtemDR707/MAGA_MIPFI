"""Authentication use cases."""

from valutatrade_hub.core.exceptions import AuthError
from valutatrade_hub.core.models.user import User
from valutatrade_hub.decorators import log_action


class AuthUseCases:
    """Register and login operations."""

    def __init__(self, users_repo) -> None:
        self._users_repo = users_repo

    @log_action("register")
    def register(self, username: str, password: str) -> User:
        if self._users_repo.get(username) is not None:
            raise AuthError("Пользователь уже существует.")
        user = User.register(username=username, password=password)
        self._users_repo.add(user)
        return user

    @log_action("login")
    def login(self, username: str, password: str) -> User:
        user = self._users_repo.get(username)
        if user is None:
            raise AuthError("Пользователь не найден.")
        if not user.verify_password(password):
            raise AuthError("Неверный пароль.")
        return user
