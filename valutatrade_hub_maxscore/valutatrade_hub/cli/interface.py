"""CLI interface: parses args, orchestrates usecases, renders friendly messages."""

from __future__ import annotations

import argparse
from pathlib import Path

from prettytable import PrettyTable

from valutatrade_hub.core.exceptions import (
    ApiRequestError,
    AuthError,
    CurrencyNotFoundError,
    InsufficientFundsError,
    ValidationError,
)
from valutatrade_hub.core.usecases.auth import AuthUseCases
from valutatrade_hub.core.usecases.rates import RatesUseCases
from valutatrade_hub.core.usecases.trading import TradingUseCases
from valutatrade_hub.infra.settings import SettingsLoader
from valutatrade_hub.infra.storage.portfolios_repo import PortfoliosRepository
from valutatrade_hub.infra.storage.rates_repo import RatesRepository
from valutatrade_hub.infra.storage.users_repo import UsersRepository
from valutatrade_hub.infra.services.session import SessionStore
from valutatrade_hub.logging_config import setup_logging
from valutatrade_hub.parser_service.api_clients import CoinGeckoClient, ExchangeRateApiClient
from valutatrade_hub.parser_service.config import load_parser_config
from valutatrade_hub.parser_service.storage import RatesStorage
from valutatrade_hub.parser_service.updater import RatesUpdater


def build_parser() -> argparse.ArgumentParser:
    """Build CLI argument parser."""
    p = argparse.ArgumentParser(prog="project", description="ValutaTrade Hub")
    sub = p.add_subparsers(dest="cmd", required=True)

    r = sub.add_parser("register", help="Register new user")
    r.add_argument("--username", required=True)
    r.add_argument("--password", required=True)

    l = sub.add_parser("login", help="Login user")
    l.add_argument("--username", required=True)
    l.add_argument("--password", required=True)

    sub.add_parser("show-portfolio", help="Show current user's portfolio")

    b = sub.add_parser("buy", help="Buy currency (deposit to wallet)")
    b.add_argument("--currency", required=True)
    b.add_argument("--amount", type=float, required=True)

    s = sub.add_parser("sell", help="Sell currency (withdraw from wallet)")
    s.add_argument("--currency", required=True)
    s.add_argument("--amount", type=float, required=True)

    gr = sub.add_parser("get-rate", help="Get rate SRC->DST")
    gr.add_argument("--src", required=True)
    gr.add_argument("--dst", required=True)

    sub.add_parser("update-rates", help="Update rates via parser service")
    sub.add_parser("show-rates", help="Print rates doc info")

    return p


def _require_user(session: SessionStore) -> str:
    """Return current user or raise AuthError."""
    u = session.get_user()
    if not u:
        raise AuthError("Сначала выполните login.")
    return u


def main() -> None:
    """CLI entry point."""
    project_root = Path(__file__).resolve().parents[2]
    settings = SettingsLoader().load(project_root=project_root)

    setup_logging(log_dir=settings.log_dir, json_logs=settings.json_logs)

    users_repo = UsersRepository(settings.data_dir / "users.json")
    portfolios_repo = PortfoliosRepository(settings.data_dir / "portfolios.json")
    rates_repo = RatesRepository(settings.data_dir / "rates.json")
    session = SessionStore(settings.data_dir / "session.json")

    auth_uc = AuthUseCases(users_repo)
    rates_uc = RatesUseCases(rates_repo=rates_repo, settings_loader=SettingsLoader())
    trade_uc = TradingUseCases(portfolios_repo=portfolios_repo, rates_usecases=rates_uc)

    parser = build_parser()
    args = parser.parse_args()

    try:
        if args.cmd == "register":
            user = auth_uc.register(args.username, args.password)
            print(f"OK: зарегистрирован {user.username}, дата {user.registered_at.isoformat()}")

        elif args.cmd == "login":
            user = auth_uc.login(args.username, args.password)
            session.set_user(user.username)
            print(f"OK: вход выполнен: {user.username}")

        elif args.cmd == "show-portfolio":
            username = _require_user(session)
            portfolio = portfolios_repo.get_or_create(username)

            t = PrettyTable(["Currency", "Balance"])
            for cur in sorted(portfolio.wallets.keys()):
                t.add_row([cur, f"{portfolio.wallets[cur].balance:.2f}"])
            print(t)

            total_usd = portfolio.get_total_value(base="USD", rate_provider=rates_uc.get_rate)
            print(f"Total (USD): {total_usd:.2f}")

        elif args.cmd == "buy":
            username = _require_user(session)
            if rates_uc.is_rates_expired():
                print("WARN: курсы устарели по TTL. Запустите: project update-rates")
            res = trade_uc.buy(username=username, currency=args.currency, amount=args.amount)
            print(f"OK: {res['wallet']}, оценка в USD: {res['estimated_usd']:.2f}")

        elif args.cmd == "sell":
            username = _require_user(session)
            if rates_uc.is_rates_expired():
                print("WARN: курсы устарели по TTL. Запустите: project update-rates")
            res = trade_uc.sell(username=username, currency=args.currency, amount=args.amount)
            print(f"OK: {res['wallet']}, выручка в USD: {res['revenue_usd']:.2f}")

        elif args.cmd == "get-rate":
            if rates_uc.is_rates_expired():
                print("WARN: курсы устарели по TTL. Запустите: project update-rates")
            r = rates_uc.get_rate(args.src, args.dst)
            print(f"{args.src.upper()} -> {args.dst.upper()} = {r:.8f}")

        elif args.cmd == "update-rates":
            parser_cfg = load_parser_config(project_root=project_root, data_dir=settings.data_dir)
            ttl = settings.ttl_seconds

            storage = RatesStorage(rates_path=parser_cfg.rates_path, history_path=parser_cfg.history_path)
            clients = [
                CoinGeckoClient(timeout=parser_cfg.timeout_seconds, base=parser_cfg.base_currency, cryptos=parser_cfg.crypto_symbols),
                ExchangeRateApiClient(
                    timeout=parser_cfg.timeout_seconds,
                    api_key=parser_cfg.exchange_rate_api_key,
                    base=parser_cfg.base_currency,
                    fiats=parser_cfg.fiat_symbols,
                ),
            ]
            updater = RatesUpdater(clients=clients, storage=storage, base=parser_cfg.base_currency, ttl_seconds=ttl)
            out = updater.run_update()

            print(f"OK: обновлено курсов: {out['rates_count']}")
            if out["errors"]:
                print("WARN: были ошибки клиентов (но обновление продолжилось):")
                for e in out["errors"]:
                    print(f" - {e}")

        elif args.cmd == "show-rates":
            doc = rates_repo.read()
            print(f"Base: {doc['base']}")
            print(f"Updated: {doc['updated_at']}")
            print(f"TTL seconds: {doc['ttl_seconds']}")
            print(f"Rates count: {len(doc['rates'])}")
            if doc.get("errors"):
                print("Last errors:")
                for e in doc["errors"]:
                    print(f" - {e}")

        else:
            raise ValidationError("Неизвестная команда.")

    except (ValidationError, AuthError, InsufficientFundsError, CurrencyNotFoundError, ApiRequestError) as e:
        print(f"ERROR: {e}")
