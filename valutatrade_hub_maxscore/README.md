# ValutaTrade Hub

CLI‑приложение для регистрации пользователей, ведения портфеля валют/криптовалют и получения курсов
с TTL‑валидацией. Отдельный `parser_service` обновляет курсы и ведёт историю.

## Структура
- `valutatrade_hub/core` — доменная модель и usecases (без IO)
- `valutatrade_hub/infra` — настройки, JSON‑хранилища, простая “сессия”
- `valutatrade_hub/parser_service` — API‑клиенты + updater + storage/history
- `valutatrade_hub/cli` — интерфейс CLI (оркестрация, UX, обработка исключений)
- `data/` — `users.json`, `portfolios.json`, `rates.json`, `exchange_rates.json`

## Установка
```bash
cd valutatrade_hub
make install
make lint
```

## Запуск
```bash
make project
# или напрямую:
poetry run project --help
```

## Примеры CLI (сценарий демо)
```bash
poetry run project register --username art --password password123
poetry run project login --username art --password password123

# обновление курсов (CoinGecko + ExchangeRate-API если есть ключ)
poetry run project update-rates

poetry run project buy --currency EUR --amount 100
poetry run project sell --currency EUR --amount 20
poetry run project show-portfolio
poetry run project get-rate --src EUR --dst USD

# служебное
poetry run project show-rates
```

## TTL / кэш
- TTL задаётся через `VTH_TTL_SECONDS` (по умолчанию 3600).
- Если курсы старше TTL, CLI выводит предупреждение и предлагает `update-rates`.

## Parser Service: ключи и env
Создайте `.env` в корне `valutatrade_hub/` (пример):

```
VTH_TTL_SECONDS=3600
VTH_BASE=USD
VTH_FIATS=USD,EUR,RUB
VTH_CRYPTOS=BTC,ETH,USDT
VTH_TIMEOUT=10
EXCHANGERATE_API_KEY=your_key_here
```

## Логи
- Логи пишутся в `logs/valutatrade_hub.log` с ротацией.
- Можно включить JSON‑логи: `VTH_JSON_LOGS=1`.

## Демо (asciinema/GIF)
Для максимального балла запишите короткий демо‑ролик:
1) `register` → `login` → `buy` → `sell` → `show-portfolio` → `get-rate`
2) `update-rates` → `show-rates`
3) Ошибки: `sell` больше баланса (InsufficientFundsError) и `get-rate` по неизвестной валюте.
