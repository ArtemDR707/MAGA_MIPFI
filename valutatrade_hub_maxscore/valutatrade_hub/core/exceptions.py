"""Domain exceptions for ValutaTrade Hub."""


class ValutaTradeError(Exception):
    """Base domain exception."""


class ValidationError(ValutaTradeError):
    """Invalid input or broken invariant."""


class AuthError(ValutaTradeError):
    """Login/register errors."""


class InsufficientFundsError(ValutaTradeError):
    """Not enough balance to withdraw."""


class CurrencyNotFoundError(ValutaTradeError):
    """Unknown currency in rates."""


class ApiRequestError(ValutaTradeError):
    """External API request failed."""
