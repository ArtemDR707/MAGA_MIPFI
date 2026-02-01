"""Parser Service configuration."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


@dataclass(frozen=True)
class ParserConfig:
    """Parser service config loaded from environment (.env)."""

    base_currency: str
    fiat_symbols: list[str]
    crypto_symbols: list[str]
    timeout_seconds: int
    rates_path: Path
    history_path: Path
    exchange_rate_api_key: str | None


def load_parser_config(project_root: Path, data_dir: Path) -> ParserConfig:
    """Load parser config from .env / environment variables."""
    load_dotenv(project_root / ".env")

    base = os.getenv("VTH_BASE", "USD").upper()
    fiats = [x.strip().upper() for x in os.getenv("VTH_FIATS", "USD,EUR,RUB").split(",") if x.strip()]
    cryptos = [x.strip().upper() for x in os.getenv("VTH_CRYPTOS", "BTC,ETH,USDT").split(",") if x.strip()]
    timeout = int(os.getenv("VTH_TIMEOUT", "10"))
    api_key = os.getenv("EXCHANGERATE_API_KEY")

    return ParserConfig(
        base_currency=base,
        fiat_symbols=fiats,
        crypto_symbols=cryptos,
        timeout_seconds=timeout,
        rates_path=data_dir / "rates.json",
        history_path=data_dir / "exchange_rates.json",
        exchange_rate_api_key=api_key,
    )
