"""External API clients for rates."""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod

import requests

from valutatrade_hub.core.exceptions import ApiRequestError

logger = logging.getLogger("valutatrade_hub.parser")

CRYPTO_ID_MAP = {
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "USDT": "tether",
}


class BaseApiClient(ABC):
    """Base client interface."""

    @abstractmethod
    def fetch_rates(self) -> dict[str, float]:
        """Return mapping currency -> rate relative to base (e.g. USD)."""


class CoinGeckoClient(BaseApiClient):
    """CoinGecko client for crypto rates."""

    def __init__(self, timeout: int, base: str, cryptos: list[str]) -> None:
        self._timeout = timeout
        self._base = base.lower()
        self._cryptos = cryptos

    def fetch_rates(self) -> dict[str, float]:
        ids: list[str] = []
        for sym in self._cryptos:
            sym = sym.upper()
            if sym in CRYPTO_ID_MAP:
                ids.append(CRYPTO_ID_MAP[sym])
        if not ids:
            return {}

        url = "https://api.coingecko.com/api/v3/simple/price"
        params = {"ids": ",".join(ids), "vs_currencies": self._base}

        try:
            resp = requests.get(url, params=params, timeout=self._timeout)
        except requests.RequestException as e:
            raise ApiRequestError(f"CoinGecko request failed: {e}") from e

        if resp.status_code != 200:
            raise ApiRequestError(f"CoinGecko HTTP {resp.status_code}: {resp.text[:200]}")

        data = resp.json()
        out: dict[str, float] = {}
        for sym, cg_id in CRYPTO_ID_MAP.items():
            if cg_id in data and self._base in data[cg_id]:
                out[sym] = float(data[cg_id][self._base])
        logger.info("CoinGecko returned %d crypto rates", len(out))
        return out


class ExchangeRateApiClient(BaseApiClient):
    """ExchangeRate-API client for fiat rates."""

    def __init__(self, timeout: int, api_key: str | None, base: str, fiats: list[str]) -> None:
        self._timeout = timeout
        self._api_key = api_key
        self._base = base.upper()
        self._fiats = [x.upper() for x in fiats]

    def fetch_rates(self) -> dict[str, float]:
        if not self._api_key:
            return {}

        url = f"https://v6.exchangerate-api.com/v6/{self._api_key}/latest/{self._base}"
        try:
            resp = requests.get(url, timeout=self._timeout)
        except requests.RequestException as e:
            raise ApiRequestError(f"ExchangeRate-API request failed: {e}") from e

        if resp.status_code == 401:
            raise ApiRequestError("ExchangeRate-API: 401 Unauthorized (проверьте ключ).")
        if resp.status_code == 429:
            raise ApiRequestError("ExchangeRate-API: 429 Too Many Requests (лимит).")
        if resp.status_code != 200:
            raise ApiRequestError(f"ExchangeRate-API HTTP {resp.status_code}: {resp.text[:200]}")

        data = resp.json()
        conv = data.get("conversion_rates", {})
        out: dict[str, float] = {}
        for sym in self._fiats:
            if sym in conv:
                out[sym] = float(conv[sym])
        out[self._base] = 1.0
        logger.info("ExchangeRate-API returned %d fiat rates", len(out))
        return out
