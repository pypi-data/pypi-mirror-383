"""Almacenes para tokens emitidos por :class:`LeptonicGuard`."""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from typing import Protocol, runtime_checkable

try:
    import redis
    from redis.client import Redis
except Exception:  # pragma: no cover - redis es opcional
    redis = None
    Redis = "Redis"  # type: ignore[assignment]


@dataclass
class TokenRecord:
    """Representa un token emitido y su metadato de caducidad."""

    token: str
    expires_at: datetime | None = None


@runtime_checkable
class TokenStoreProtocol(Protocol):
    """Contrato mínimo para almacenes de tokens."""

    def store(self, node_id: str, token: str, expires_at: datetime | None = None) -> None:
        """Guarda el token para el nodo indicado."""

    def retrieve(self, node_id: str) -> TokenRecord | None:
        """Recupera el token asociado al nodo o ``None`` si no existe."""

    def revoke(self, node_id: str) -> None:
        """Elimina el token asociado al nodo."""


class InMemoryTokenStore(TokenStoreProtocol):
    """Almacén en memoria respaldado por un diccionario."""

    def __init__(self) -> None:
        self._tokens: dict[str, TokenRecord] = {}

    def store(self, node_id: str, token: str, expires_at: datetime | None = None) -> None:
        self._tokens[node_id] = TokenRecord(token=token, expires_at=expires_at)

    def retrieve(self, node_id: str) -> TokenRecord | None:
        return self._tokens.get(node_id)

    def revoke(self, node_id: str) -> None:
        self._tokens.pop(node_id, None)


@dataclass
class RedisTokenStore(TokenStoreProtocol):
    """Almacén basado en Redis.

    Para utilizar esta implementación es necesario instalar ``redis`` y
    proporcionar un cliente configurado. Si ``redis`` no está disponible se
    lanza :class:`RuntimeError` al inicializar la clase.
    """

    client: Redis
    prefix: str = "leptonic_guard:token"

    def __post_init__(self) -> None:  # pragma: no cover - validación rápida
        if redis is None:
            raise RuntimeError(
                "RedisTokenStore requiere la dependencia opcional 'redis'."
            )

    def _key(self, node_id: str) -> str:
        return f"{self.prefix}:{node_id}"

    def store(self, node_id: str, token: str, expires_at: datetime | None = None) -> None:
        payload = {"token": token, "expires_at": expires_at.isoformat() if expires_at else None}
        self.client.set(self._key(node_id), json.dumps(payload))
        if expires_at is not None:
            self.client.expireat(self._key(node_id), int(expires_at.timestamp()))

    def retrieve(self, node_id: str) -> TokenRecord | None:
        value = self.client.get(self._key(node_id))
        if value is None:
            return None
        if isinstance(value, bytes):
            value = value.decode("utf-8")
        data = json.loads(value)
        expires_raw = data.get("expires_at")
        expires_at = datetime.fromisoformat(expires_raw) if expires_raw else None
        return TokenRecord(token=data["token"], expires_at=expires_at)

    def revoke(self, node_id: str) -> None:
        self.client.delete(self._key(node_id))
