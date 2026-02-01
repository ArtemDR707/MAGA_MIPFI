"""Portfolio model: wallet collection and valuation."""

from __future__ import annotations

from dataclasses import dataclass, field

from valutatrade_hub.core.exceptions import ValidationError
from valutatrade_hub.core.models.wallet import Wallet

DEFAULT_BASE = "USD"


@dataclass
class Portfolio:
    """User portfolio: set of currency wallets."""

    _username: str
    _wallets: dict[str, Wallet] = field(default_factory=dict)

    @property
    def user(self) -> str:
        """Portfolio owner username."""
        return self._username

    @property
    def wallets(self) -> dict[str, Wallet]:
        """Return a copy to keep internal mapping encapsulated."""
        return dict(self._wallets)

    def add_currency(self, currency: str) -> Wallet:
        """Ensure wallet exists for currency; return wallet."""
        currency = (currency or "").upper().strip()
        if not currency:
            raise ValidationError("Валюта не должна быть пустой.")
        if currency not in self._wallets:
            self._wallets[currency] = Wallet(_currency=currency, _balance=0.0)
        return self._wallets[currency]

    def get_wallet(self, currency: str) -> Wallet:
        """Alias for add_currency to provide access."""
        return self.add_currency(currency)

    def get_total_value(self, base: str = DEFAULT_BASE, rate_provider: callable = None) -> float:
        """Total portfolio value in `base` using provided rate_provider."""
        if rate_provider is None:
            raise ValidationError("rate_provider должен быть задан.")
        base = (base or DEFAULT_BASE).upper().strip()
        total = 0.0
        for cur, wallet in self._wallets.items():
            rate = rate_provider(cur, base)
            total += wallet.balance * rate
        return total

    def to_dict(self) -> dict:
        return {
            "username": self._username,
            "wallets": [w.to_dict() for w in self._wallets.values()],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Portfolio":
        p = cls(_username=data["username"])
        for w in data.get("wallets", []):
            wallet = Wallet.from_dict(w)
            p._wallets[wallet.currency] = wallet
        return p
