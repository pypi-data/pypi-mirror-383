from typing import Optional

from ._counter import Counter


def configure(api_token: str):
    """
    Configures the Counter instance with the provided API token.
    """
    Counter.configure(api_token)


def get_value(
    name: str,
) -> int:
    """
    Retrieves the current value of a counter by its name.

    Parameters:
        name: The name of the counter.
    """
    counter = Counter.get_instance()
    return counter.get_value(name)


def increment(
    name: str,
    limit: Optional[int] = None,
    ttl: Optional[int] = None,
) -> bool:
    """
    Increments a counter unless it reaches the specified limit.

    Parameters:
        name: The name of the counter.
        limit: Optional maximum value the counter should not exceed.
        ttl: Optional time-to-live in seconds for each increment.
    """
    counter = Counter.get_instance()
    return counter.increment(name, limit, ttl)


__all__ = [
    "configure",
    "get_value",
    "increment",
]
