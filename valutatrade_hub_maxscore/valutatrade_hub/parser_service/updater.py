"""Rates updater: merges multiple sources and persists results."""

import logging

from valutatrade_hub.core.exceptions import ApiRequestError

logger = logging.getLogger("valutatrade_hub.parser")


class RatesUpdater:
    """Poll all clients, merge rates, persist atomically, keep history."""

    def __init__(self, clients: list, storage, base: str, ttl_seconds: int) -> None:
        self._clients = clients
        self._storage = storage
        self._base = base
        self._ttl = ttl_seconds

    def run_update(self) -> dict:
        merged: dict[str, float] = {self._base: 1.0}
        errors: list[str] = []

        for client in self._clients:
            try:
                part = client.fetch_rates()
                merged.update(part)
            except ApiRequestError as e:
                msg = str(e)
                errors.append(msg)
                logger.warning("Client failed: %s", msg)

        self._storage.write_rates(base=self._base, ttl_seconds=self._ttl, rates=merged, errors=errors)
        logger.info("Update complete: %d rates, %d errors", len(merged), len(errors))
        return {"rates_count": len(merged), "errors": errors}
