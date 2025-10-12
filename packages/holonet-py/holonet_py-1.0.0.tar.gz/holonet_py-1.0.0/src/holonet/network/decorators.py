"""Decoradores auxiliares para emular comunicación muónica."""
from __future__ import annotations

from functools import wraps
from typing import Any, Callable


def muon_broadcast(func: Callable[..., Any]) -> Callable[..., Any]:
    """Decorador que marca una función como emisora muónica."""

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        result = func(*args, **kwargs)
        return {
            "mode": "broadcast",
            "result": result,
        }

    return wrapper


def muon_receive(func: Callable[..., Any]) -> Callable[..., Any]:
    """Decorador que marca una función como receptora muónica."""

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        result = func(*args, **kwargs)
        return {
            "mode": "receive",
            "result": result,
        }

    return wrapper

