"""Wallet model: balance operations with invariants."""

from dataclasses import dataclass

from valutatrade_hub.core.exceptions import InsufficientFundsError, ValidationError


@dataclass
class Wallet:
    """Wallet for a single currency."""

    _currency: str
    _balance: float = 0.0

    @property
    def currency(self) -> str:
        return self._currency

    @property
    def balance(self) -> float:
        return self._balance

    @balance.setter
    def balance(self, value: float) -> None:
        if not isinstance(value, (int, float)):
            raise ValidationError("Баланс должен быть числом.")
        if value < 0:
            raise ValidationError("Баланс не может быть отрицательным.")
        self._balance = float(value)

    def deposit(self, amount: float) -> None:
        """Increase wallet balance."""
        amount = self._validate_amount(amount)
        self.balance = self.balance + amount

    def withdraw(self, amount: float) -> None:
        """Decrease wallet balance (cannot go below zero)."""
        amount = self._validate_amount(amount)
        if self.balance < amount:
            raise InsufficientFundsError(
                f"Недостаточно средств: доступно {self.balance:.2f} {self.currency}, нужно {amount:.2f}."
            )
        self.balance = self.balance - amount

    def get_balance_info(self) -> str:
        """Human-readable info string."""
        return f"{self.currency}: {self.balance:.2f}"

    @staticmethod
    def _validate_amount(amount: float) -> float:
        if not isinstance(amount, (int, float)):
            raise ValidationError("Сумма должна быть числом.")
        amount = float(amount)
        if amount <= 0:
            raise ValidationError("Сумма должна быть > 0.")
        return amount

    def to_dict(self) -> dict:
        return {"currency": self.currency, "balance": self.balance}

    @classmethod
    def from_dict(cls, data: dict) -> "Wallet":
        return cls(_currency=data["currency"], _balance=float(data["balance"]))
