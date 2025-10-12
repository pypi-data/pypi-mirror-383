"""Módulo básico de seguridad leptónica."""
from __future__ import annotations

import hashlib
import logging
import secrets
from collections import defaultdict, deque
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from threading import Lock
from typing import Deque, Dict, Iterable

from holonet.core.packets import MuonPacket
from holonet.security.token_store import (
    InMemoryTokenStore,
    TokenRecord,
    TokenStoreProtocol,
)


LOGGER = logging.getLogger(__name__)

DEFAULT_PBKDF2_ITERATIONS = 150_000
MIN_SECRET_LENGTH = 12


@dataclass
class AuditEvent:
    """Evento registrado por :class:`LeptonicGuard`."""

    timestamp: datetime
    event: str
    node_id: str
    details: dict[str, object]


class AuditLog:
    """Backend mínimo en memoria para auditoría."""

    def __init__(self, max_events: int = 1000) -> None:
        if max_events <= 0:
            raise ValueError("max_events debe ser mayor que cero")
        self._events: Deque[AuditEvent] = deque(maxlen=max_events)
        self._dropped_events = 0

    def record(self, event: str, node_id: str, **details: object) -> None:
        audit_event = AuditEvent(
            timestamp=datetime.now(timezone.utc),
            event=event,
            node_id=node_id,
            details=details,
        )
        if len(self._events) == self._events.maxlen:
            self._dropped_events += 1
        self._events.append(audit_event)
        LOGGER.info(
            "audit_event",
            extra={
                "event": audit_event.event,
                "node_id": audit_event.node_id,
                "details": audit_event.details,
                "timestamp": audit_event.timestamp.isoformat(),
            },
        )

    def recent(self, limit: int = 50) -> list[AuditEvent]:
        if limit <= 0:
            return []
        events = list(self._events)
        if limit >= len(events):
            return events
        return events[-limit:]

    def recent_for_node(self, node_id: str, limit: int = 50) -> list[AuditEvent]:
        if limit <= 0:
            return []
        filtered = [event for event in self._events if event.node_id == node_id]
        if limit >= len(filtered):
            return filtered
        return filtered[-limit:]

    def clear(self) -> None:
        self._events.clear()
        self._dropped_events = 0

    def metrics(self) -> dict[str, int]:
        return {
            "stored_events": len(self._events),
            "dropped_events": self._dropped_events,
            "capacity": self._events.maxlen or 0,
        }


@dataclass
class StoredSecret:
    """Representa un secreto derivado mediante PBKDF2."""

    salt: bytes
    derived_key: bytes
    iterations: int


class TokenIssuanceBlocked(PermissionError):
    """Excepción para indicar que la emisión está temporalmente bloqueada."""

    def __init__(self, node_id: str, retry_after: float) -> None:
        message = (
            "Emisión de token temporalmente bloqueada para el nodo "
            f"{node_id}. Intente nuevamente en {retry_after:.0f} segundos"
        )
        super().__init__(message)
        self.node_id = node_id
        self.retry_after = retry_after


class LeptonicGuard:
    """Validador que delega el almacenamiento de tokens en un almacén."""

    def __init__(
        self,
        store: TokenStoreProtocol | None = None,
        token_ttl: timedelta = timedelta(minutes=5),
        audit_log: AuditLog | None = None,
        audit_max_events: int = 1000,
        *,
        max_failed_attempts: int = 5,
        failed_attempt_window: timedelta = timedelta(minutes=1),
        lockout_duration: timedelta = timedelta(minutes=5),
    ) -> None:
        self._store = store or InMemoryTokenStore()
        self._token_ttl = token_ttl
        self._secrets: Dict[str, StoredSecret] = {}
        self._audit = audit_log or AuditLog(max_events=audit_max_events)
        if max_failed_attempts <= 0:
            raise ValueError("max_failed_attempts debe ser mayor que cero")
        if failed_attempt_window <= timedelta(0):
            raise ValueError("failed_attempt_window debe ser positivo")
        if lockout_duration <= timedelta(0):
            raise ValueError("lockout_duration debe ser positivo")
        self._max_failed_attempts = max_failed_attempts
        self._failed_attempt_window = failed_attempt_window
        self._lockout_duration = lockout_duration
        self._failed_attempts: Dict[str, Deque[datetime]] = defaultdict(deque)
        self._lockouts: Dict[str, datetime] = {}
        self._rate_lock = Lock()

    @property
    def audit_log(self) -> AuditLog:
        return self._audit

    def audit_metrics(self) -> dict[str, int]:
        """Expone métricas del registro de auditoría."""

        return self._audit.metrics()

    def register_shared_secret(self, node_id: str, secret: str, *, event: str = "secret_registered") -> None:
        """Registra o actualiza el secreto compartido asociado al nodo."""

        self._validate_secret_strength(secret)
        stored = self._derive_secret(secret)
        self._secrets[node_id] = stored
        self._audit.record(event, node_id)

    def revoke_shared_secret(self, node_id: str) -> None:
        self.revoke_token(node_id, reason="secret_revoked")
        self._secrets.pop(node_id, None)
        self._audit.record("secret_revoked", node_id)

    def update_shared_secret(
        self,
        node_id: str,
        new_secret: str,
        *,
        token: str | None = None,
        previous_secret: str | None = None,
    ) -> None:
        """Actualiza el secreto compartido validando las credenciales previas."""

        if node_id not in self._secrets:
            raise KeyError(f"El nodo {node_id} no tiene un secreto registrado")

        if token:
            if not self.verify_token(node_id, token):
                self._audit.record(
                    "secret_update_denied", node_id, reason="invalid_token"
                )
                raise PermissionError("Token inválido para actualizar el nodo")
        elif previous_secret:
            if not self._authenticate(node_id, previous_secret):
                self._audit.record(
                    "secret_update_denied", node_id, reason="invalid_secret"
                )
                raise PermissionError("Secreto anterior inválido")
        else:
            self._audit.record(
                "secret_update_denied", node_id, reason="missing_credentials"
            )
            raise PermissionError(
                "Se requiere un token vigente o el secreto anterior para actualizar"
            )

        try:
            self.register_shared_secret(
                node_id, new_secret, event="secret_rotated"
            )
        except ValueError as exc:
            self._audit.record(
                "secret_update_denied", node_id, reason="weak_secret"
            )
            raise exc

        self.revoke_token(node_id, reason="secret_rotated")

    def issue_token(self, node_id: str, shared_secret: str) -> str:
        now = datetime.now(timezone.utc)
        lockout_until = self._current_lockout(node_id, now)
        if lockout_until is not None:
            retry_after = max((lockout_until - now).total_seconds(), 0.0)
            self._audit.record(
                "token_issue_blocked",
                node_id,
                retry_after=retry_after,
            )
            raise TokenIssuanceBlocked(node_id, retry_after)

        if not self._authenticate(node_id, shared_secret):
            retry_after = self._register_failed_attempt(node_id, now)
            self._audit.record("token_issue_denied", node_id)
            if retry_after is not None:
                self._audit.record(
                    "token_issue_blocked",
                    node_id,
                    retry_after=retry_after,
                )
                raise TokenIssuanceBlocked(node_id, retry_after)
            raise PermissionError("Secreto inválido para el nodo solicitado")

        token = secrets.token_urlsafe(16)
        expires_at = datetime.now(timezone.utc) + self._token_ttl
        self._store.store(node_id, token, expires_at=expires_at)
        self._audit.record("token_issued", node_id, expires_at=expires_at.isoformat())
        self._reset_failed_attempts(node_id)
        return token

    def verify(self, node_id: str, token: str, packet: MuonPacket | None = None) -> bool:
        record = self._store.retrieve(node_id)
        if record is None:
            self._audit.record("token_missing", node_id)
            return False

        if not self._is_token_valid(node_id, record, token):
            return False

        if packet is not None and packet.signal.leptonic_density <= 0:
            self._audit.record("signal_rejected", node_id, density=packet.signal.leptonic_density)
            return False

        self._audit.record("token_verified", node_id)
        return True

    def verify_token(self, node_id: str, token: str) -> bool:
        """Valida un token sin asociarlo a un paquete específico."""

        record = self._store.retrieve(node_id)
        if record is None:
            self._audit.record("token_missing", node_id)
            return False
        valid = self._is_token_valid(node_id, record, token)
        if valid:
            self._audit.record("token_verified", node_id)
        return valid

    def revoke_token(self, node_id: str, *, reason: str | None = None) -> None:
        record = self._store.retrieve(node_id)
        self._store.revoke(node_id)
        if record is None:
            if reason is not None:
                self._audit.record(
                    "token_revoked", node_id, reason=reason, found=False
                )
            else:
                self._audit.record("token_revoked", node_id, found=False)
            return

        if reason is not None:
            self._audit.record("token_revoked", node_id, reason=reason)
        else:
            self._audit.record("token_revoked", node_id)

    def export_audit_events(
        self, limit: int = 50, *, node_id: str | None = None
    ) -> Iterable[AuditEvent]:
        if node_id is None:
            return self._audit.recent(limit)
        return self._audit.recent_for_node(node_id, limit)

    def _authenticate(self, node_id: str, shared_secret: str) -> bool:
        stored = self._secrets.get(node_id)
        if stored is None:
            return False
        candidate = self._derive_secret(shared_secret, salt=stored.salt, iterations=stored.iterations)
        return secrets.compare_digest(stored.derived_key, candidate.derived_key)

    def _current_lockout(self, node_id: str, now: datetime) -> datetime | None:
        with self._rate_lock:
            lockout_until = self._lockouts.get(node_id)
            if lockout_until is None:
                return None
            if lockout_until <= now:
                self._lockouts.pop(node_id, None)
                return None
            return lockout_until

    def _register_failed_attempt(self, node_id: str, now: datetime) -> float | None:
        with self._rate_lock:
            attempts = self._failed_attempts[node_id]
            window = self._failed_attempt_window
            while attempts and now - attempts[0] > window:
                attempts.popleft()
            attempts.append(now)
            if len(attempts) < self._max_failed_attempts:
                return None
            lockout_until = now + self._lockout_duration
            self._lockouts[node_id] = lockout_until
            attempts.clear()
            retry_after = (lockout_until - now).total_seconds()
            return retry_after

    def _reset_failed_attempts(self, node_id: str) -> None:
        with self._rate_lock:
            self._failed_attempts.pop(node_id, None)
            self._lockouts.pop(node_id, None)

    def _derive_secret(
        self,
        secret: str,
        *,
        salt: bytes | None = None,
        iterations: int = DEFAULT_PBKDF2_ITERATIONS,
    ) -> StoredSecret:
        actual_salt = salt or secrets.token_bytes(16)
        derived = hashlib.pbkdf2_hmac(
            "sha256",
            secret.encode("utf-8"),
            actual_salt,
            iterations,
        )
        return StoredSecret(salt=actual_salt, derived_key=derived, iterations=iterations)

    def _validate_secret_strength(self, secret: str) -> None:
        if len(secret) < MIN_SECRET_LENGTH:
            raise ValueError(
                "El secreto debe tener al menos 12 caracteres"
            )

        has_upper = any(ch.isupper() for ch in secret)
        has_lower = any(ch.islower() for ch in secret)
        has_digit = any(ch.isdigit() for ch in secret)
        has_symbol = any(not ch.isalnum() for ch in secret)

        categories = sum([has_upper, has_lower, has_digit, has_symbol])
        if categories < 3:
            raise ValueError(
                "El secreto debe combinar al menos tres tipos de caracteres"
            )

    def _is_token_valid(self, node_id: str, record: TokenRecord, candidate: str) -> bool:
        now = datetime.now(timezone.utc)
        if record.expires_at is not None and record.expires_at <= now:
            self._store.revoke(node_id)
            self._audit.record(
                "token_expired",
                node_id,
                expired_at=record.expires_at.isoformat(),
            )
            return False

        if not secrets.compare_digest(record.token, candidate):
            self._audit.record(
                "token_invalid",
                node_id,
                presented_length=len(candidate),
            )
            return False

        return True
