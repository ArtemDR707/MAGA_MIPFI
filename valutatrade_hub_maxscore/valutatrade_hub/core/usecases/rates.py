"""Rates use cases: rate calculation and TTL check."""

from datetime import datetime, timezone

from valutatrade_hub.core.exceptions import CurrencyNotFoundError, ValidationError


class RatesUseCases:
    """Get rates from repository and validate freshness via TTL."""

    def __init__(self, rates_repo, settings_loader) -> None:
        self._rates_repo = rates_repo
        self._settings = settings_loader

    def get_rate(self, src: str, dst: str) -> float:
        src = (src or "").upper().strip()
        dst = (dst or "").upper().strip()
        if not src or not dst:
            raise ValidationError("Нужно указать обе валюты: SRC и DST.")

        rates_doc = self._rates_repo.read()
        rates = rates_doc["rates"]

        if src not in rates:
            raise CurrencyNotFoundError(f"Неизвестная валюта: {src}. Обновите курсы (update-rates).")
        if dst not in rates:
            raise CurrencyNotFoundError(f"Неизвестная валюта: {dst}. Обновите курсы (update-rates).")

        # rates[x] is x per base (USD). Then src->dst = rate[dst] / rate[src].
        return float(rates[dst]) / float(rates[src])

    def is_rates_expired(self) -> bool:
        rates_doc = self._rates_repo.read()
        updated_at = datetime.fromisoformat(rates_doc["updated_at"])
        ttl = int(self._settings.ttl_seconds)
        age = (datetime.now(timezone.utc) - updated_at).total_seconds()
        return age > ttl
