"""Trading use cases: buy/sell operations."""

from valutatrade_hub.core.exceptions import ValidationError
from valutatrade_hub.decorators import log_action


class TradingUseCases:
    """Buy/sell currencies within user's portfolio."""

    def __init__(self, portfolios_repo, rates_usecases) -> None:
        self._portfolios_repo = portfolios_repo
        self._rates = rates_usecases

    @log_action("buy")
    def buy(self, username: str, currency: str, amount: float) -> dict:
        currency = (currency or "").upper().strip()
        if not currency:
            raise ValidationError("Валюта покупки не задана.")
        if amount <= 0:
            raise ValidationError("Amount должен быть > 0.")

        portfolio = self._portfolios_repo.get_or_create(username)
        wallet = portfolio.get_wallet(currency)
        wallet.deposit(amount)
        self._portfolios_repo.save(portfolio)
        est_usd = self._estimate_usd(currency, amount)
        return {"wallet": wallet.get_balance_info(), "estimated_usd": est_usd}

    @log_action("sell")
    def sell(self, username: str, currency: str, amount: float) -> dict:
        currency = (currency or "").upper().strip()
        if not currency:
            raise ValidationError("Валюта продажи не задана.")
        if amount <= 0:
            raise ValidationError("Amount должен быть > 0.")

        portfolio = self._portfolios_repo.get_or_create(username)
        wallet = portfolio.get_wallet(currency)
        wallet.withdraw(amount)
        self._portfolios_repo.save(portfolio)
        revenue_usd = self._estimate_usd(currency, amount)
        return {"wallet": wallet.get_balance_info(), "revenue_usd": revenue_usd}

    def _estimate_usd(self, currency: str, amount: float) -> float:
        r = self._rates.get_rate(currency, "USD")
        return float(amount) * float(r)
