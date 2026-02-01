"""Rate cache facade."""

from valutatrade_hub.core.usecases.rates import RatesUseCases


class RateCache:
    """Facade over rates usecases to check TTL freshness."""

    def __init__(self, rates_uc: RatesUseCases) -> None:
        self._rates_uc = rates_uc

    def ensure_fresh(self) -> bool:
        """Return True if rates are fresh, False if expired by TTL."""
        return not self._rates_uc.is_rates_expired()
