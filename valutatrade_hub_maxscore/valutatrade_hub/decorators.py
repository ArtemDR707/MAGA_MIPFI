"""Project decorators (logging, etc.)."""

import functools
import logging
from collections.abc import Callable
from typing import Any, TypeVar

T = TypeVar("T")


def log_action(action_name: str) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Log start/finish of an action.

    Args:
        action_name: Human-readable action name for logs.

    Returns:
        Decorator.
    """
    logger = logging.getLogger("valutatrade_hub.actions")

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            logger.info("START %s", action_name)
            result = func(*args, **kwargs)
            logger.info("OK %s", action_name)
            return result

        return wrapper

    return decorator
