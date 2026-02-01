"""Portfolios repository backed by portfolios.json."""

from pathlib import Path

from valutatrade_hub.core.models.portfolio import Portfolio
from valutatrade_hub.infra.storage.json_store import JsonStore


class PortfoliosRepository:
    """Persist portfolios in JSON."""

    def __init__(self, path: Path) -> None:
        self._store = JsonStore(path)

    def _all(self) -> list[Portfolio]:
        raw = self._store.read() or []
        return [Portfolio.from_dict(x) for x in raw]

    def get_or_create(self, username: str) -> Portfolio:
        username = (username or "").strip()
        all_p = self._all()
        for p in all_p:
            if p.user == username:
                return p
        p = Portfolio(_username=username)
        all_p.append(p)
        self._store.write_atomic([x.to_dict() for x in all_p])
        return p

    def save(self, portfolio: Portfolio) -> None:
        all_p = self._all()
        for i, p in enumerate(all_p):
            if p.user == portfolio.user:
                all_p[i] = portfolio
                break
        else:
            all_p.append(portfolio)
        self._store.write_atomic([x.to_dict() for x in all_p])
