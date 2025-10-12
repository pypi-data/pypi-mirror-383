"""Decoradores asociados al subsistema MTQ."""
from __future__ import annotations

import asyncio
from collections.abc import Iterable
from functools import wraps
from inspect import signature
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional

from .quantum_packet import QuantumPacket
from .state_models import NodeQuantumState

if TYPE_CHECKING:  # pragma: no cover - solo para tipeo
    from ..transmission.mtq_bridge import MTQBridge, TunnelResult


def _ensure_bridge(kwargs: Dict[str, Any], key: str) -> "MTQBridge":
    from ..transmission.mtq_bridge import MTQBridge

    bridge = kwargs.get(key)
    if not isinstance(bridge, MTQBridge):
        raise ValueError(
            "Se requiere un argumento 'mtq_bridge' que sea instancia de MTQBridge para utilizar @tunnelable.",
        )
    return bridge


def _ensure_state(kwargs: Dict[str, Any], key: str) -> NodeQuantumState:
    state = kwargs.get(key)
    if not isinstance(state, NodeQuantumState):
        raise ValueError(
            "Se requiere un argumento 'quantum_state' que sea instancia de NodeQuantumState para utilizar @tunnelable.",
        )
    return state


def _serialize_results(results: List["TunnelResult"]) -> Dict[str, Any]:
    payload = {
        "results": [result.as_dict() for result in results],
    }
    payload["tunneled"] = any(result.tunneled for result in results)
    payload["probabilities"] = [result.probability for result in results]
    return payload


def _handle_result(
    result: Any,
    bridge: "MTQBridge",
    state: NodeQuantumState,
) -> Dict[str, Any]:
    from ..transmission.mtq_bridge import TunnelResult

    if isinstance(result, TunnelResult):
        return result.as_dict()

    if isinstance(result, QuantumPacket):
        tunnel_result = bridge.transmit(result, state)
        return tunnel_result.as_dict()

    if isinstance(result, dict) and isinstance(result.get("results"), list):
        return result

    if isinstance(result, Iterable) and not isinstance(result, (bytes, str, dict)):
        items = list(result)
        if not items:
            return _serialize_results([])
        if all(isinstance(item, TunnelResult) for item in items):
            return _serialize_results(items)
        if all(isinstance(item, QuantumPacket) for item in items):
            tunnel_results = [bridge.transmit(packet, state) for packet in items]
            return _serialize_results(tunnel_results)
        raise TypeError("@tunnelable solo soporta iterables de QuantumPacket o TunnelResult.")

    raise TypeError(
        "Las funciones decoradas con @tunnelable deben devolver QuantumPacket, TunnelResult o un iterable de ellos.",
    )


def tunnelable(
    func: Optional[Callable[..., Any]] = None,
    *,
    bridge_key: str = "mtq_bridge",
    state_key: str = "quantum_state",
) -> Callable[..., Any]:
    """Decora funciones o rutas que producen paquetes cuánticos MTQ."""

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        sig = signature(func)
        accepts_bridge = bridge_key in sig.parameters
        accepts_state = state_key in sig.parameters

        if asyncio.iscoroutinefunction(func):

            @wraps(func)
            async def async_wrapper(*args: Any, **kwargs: Any) -> Dict[str, Any]:
                bridge = _ensure_bridge(kwargs, bridge_key)
                state = _ensure_state(kwargs, state_key)

                call_kwargs = dict(kwargs)
                if not accepts_bridge:
                    call_kwargs.pop(bridge_key, None)
                if not accepts_state:
                    call_kwargs.pop(state_key, None)

                result = await func(*args, **call_kwargs)
                return _handle_result(result, bridge, state)

            return async_wrapper

        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Dict[str, Any]:
            bridge = _ensure_bridge(kwargs, bridge_key)
            state = _ensure_state(kwargs, state_key)

            call_kwargs = dict(kwargs)
            if not accepts_bridge:
                call_kwargs.pop(bridge_key, None)
            if not accepts_state:
                call_kwargs.pop(state_key, None)

            result = func(*args, **call_kwargs)
            return _handle_result(result, bridge, state)

        return wrapper

    if func is not None:
        return decorator(func)

    return decorator


__all__ = ["tunnelable"]
