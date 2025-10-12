"""API FastAPI para interactuar con la simulación."""
from __future__ import annotations

import logging
import os
import hmac
from collections import deque
from datetime import datetime, timedelta, timezone
from threading import Lock, RLock
from typing import Any, Iterable

from fastapi import FastAPI, Header, HTTPException, Query
from fastapi.exception_handlers import request_validation_exception_handler
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator
from pydantic_core import PydanticCustomError
from starlette import status

from holonet.core.nodes import HoloNode, NodeRegistry
from holonet.core.packets import LeptonicPattern, MuonPacket
from holonet.hardware.induction_driver import DeviceRegistry
from holonet.network.adaptive_topology import AdaptiveTopology
from holonet.network.metrics import AdaptiveMetricCollector
from holonet.security.leptonic_guard import LeptonicGuard, TokenIssuanceBlocked
from holonet.simulation.adaptive_controller import AdaptiveController
from holonet.simulation.engine import QueueSaturatedError, SimulationEngine
from holonet.network.topology import DEFAULT_TOPOLOGY_PATH, bootstrap_topology

LOGGER = logging.getLogger(__name__)

MAX_PAYLOAD_BYTES = 4096
AUDIT_RATE_WINDOW = timedelta(seconds=5)
AUDIT_RATE_LIMIT = 5
MAX_PENDING_EVENTS = 2048


app = FastAPI(title="Holonet Muónica")
registry = NodeRegistry()
engine = SimulationEngine(max_pending_events=MAX_PENDING_EVENTS)
guard = LeptonicGuard()
topology = bootstrap_topology(registry, DEFAULT_TOPOLOGY_PATH)

device_registry = DeviceRegistry()
adaptive_controller = AdaptiveController()
adaptive_topology = AdaptiveTopology(adaptive_controller)
adaptive_metric_collector = AdaptiveMetricCollector(adaptive_controller, device_registry)

REGISTRATION_TOKEN_HEADER = "X-Registration-Token"
REGISTRATION_TOKEN_ENV = "HOLONET_REGISTRATION_TOKENS"


class RegistrationAuthorizer:
    """Valida tokens administrativos para el registro de nodos."""

    def __init__(self, guard_instance: LeptonicGuard) -> None:
        self._guard = guard_instance
        self._lock = RLock()
        self._tokens: tuple[str, ...] = ()

    def configure(self, tokens: Iterable[str]) -> None:
        normalized = tuple(
            token.strip()
            for token in tokens
            if isinstance(token, str) and token.strip()
        )
        with self._lock:
            self._tokens = normalized

    def tokens_configured(self) -> bool:
        with self._lock:
            return bool(self._tokens)

    def authorize(self, presented: str | None, node_id: str) -> None:
        with self._lock:
            tokens = self._tokens

        if not tokens:
            LOGGER.error(
                "Intento de registro rechazado: no hay tokens administrativos configurados",
            )
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="El registro de nodos está temporalmente deshabilitado",
            )

        if presented is None:
            self._guard.audit_log.record(
                "registration_denied",
                node_id,
                reason="missing_admin_token",
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Se requiere un token administrativo válido",
            )

        for expected in tokens:
            if hmac.compare_digest(expected, presented):
                self._guard.audit_log.record(
                    "registration_authorized",
                    node_id,
                )
                return

        self._guard.audit_log.record(
            "registration_denied",
            node_id,
            reason="invalid_admin_token",
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Token administrativo inválido",
        )


registration_authorizer = RegistrationAuthorizer(guard)


def _load_registration_tokens_from_env() -> tuple[str, ...]:
    raw_value = os.getenv(REGISTRATION_TOKEN_ENV, "")
    if not raw_value:
        return ()
    tokens = [token.strip() for token in raw_value.split(",") if token.strip()]
    return tuple(tokens)


registration_authorizer.configure(_load_registration_tokens_from_env())


def configure_registration_tokens(tokens: Iterable[str]) -> None:
    """Permite establecer tokens administrativos válidos en tiempo de ejecución."""

    registration_authorizer.configure(tokens)

class AuditRateLimiter:
    """Controla peticiones por nodo con limpieza automática."""

    def __init__(self, limit: int, window: timedelta) -> None:
        if limit <= 0:
            raise ValueError("limit debe ser mayor que cero")
        if window <= timedelta(0):
            raise ValueError("window debe ser positivo")
        self._limit = limit
        self._window = window
        self._entries: dict[str, deque[datetime]] = {}
        self._lock = Lock()
        self._next_cleanup = datetime.now(timezone.utc)

    def try_acquire(self, key: str, now: datetime) -> tuple[bool, float]:
        with self._lock:
            self._cleanup_if_needed(now)
            history = self._entries.get(key)
            if history is None:
                history = deque()
                self._entries[key] = history
            else:
                window = self._window
                while history and now - history[0] > window:
                    history.popleft()
                if not history:
                    self._entries.pop(key, None)
                    history = deque()
                    self._entries[key] = history

            if len(history) >= self._limit:
                window = self._window
                retry_after = (history[0] + window - now).total_seconds()
                if retry_after < 0:
                    retry_after = 0.0
                return False, retry_after

            history.append(now)
            return True, 0.0

    def reset(self) -> None:
        with self._lock:
            self._entries.clear()
            self._next_cleanup = datetime.now(timezone.utc)

    def _cleanup_if_needed(self, now: datetime) -> None:
        if now < self._next_cleanup:
            return
        cutoff = now - self._window
        stale_keys = [
            key
            for key, history in self._entries.items()
            if not history or history[-1] < cutoff
        ]
        for key in stale_keys:
            self._entries.pop(key, None)
        self._next_cleanup = now + self._window


audit_rate_limiter = AuditRateLimiter(AUDIT_RATE_LIMIT, AUDIT_RATE_WINDOW)




def _retry_after_header(seconds: float) -> str:
    if seconds <= 0:
        return "0"
    whole = int(seconds)
    if float(whole) == seconds:
        return str(whole)
    return str(whole + 1)


def _extract_bearer_token(header: str) -> str:
    parts = header.strip().split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise ValueError("La cabecera Authorization debe usar el esquema Bearer")
    token = parts[1].strip()
    if not token:
        raise ValueError("El token Bearer no puede estar vacío")
    return token


def configure_adaptive(
    topology_instance: AdaptiveTopology,
    metric_collector: AdaptiveMetricCollector | None = None,
) -> None:
    """Permite inyectar instancias adaptativas personalizadas."""

    global adaptive_controller, adaptive_topology, adaptive_metric_collector
    adaptive_topology = topology_instance
    adaptive_controller = topology_instance.controller
    if metric_collector is not None:
        adaptive_metric_collector = metric_collector
    else:
        adaptive_metric_collector = AdaptiveMetricCollector(
            adaptive_controller, device_registry
        )


class EmitRequest(BaseModel):
    node_id: str
    payload: str = Field(..., min_length=1)
    pattern_name: str
    pattern_sequence: list[float] | None = None
    density: float = 1.0
    token: str

    @field_validator("payload")
    @classmethod
    def validate_payload(cls, value: str) -> str:
        if len(value.encode("utf-8")) > MAX_PAYLOAD_BYTES:
            raise PydanticCustomError(
                "payload.too_large",
                f"payload excede {MAX_PAYLOAD_BYTES} bytes",
                {"limit": MAX_PAYLOAD_BYTES},
            )
        return value


class TokenRequest(BaseModel):
    node_id: str
    shared_secret: str


class NodeRegistrationRequest(BaseModel):
    node_id: str
    location: str
    shared_secret: str
    capabilities: list[str] | None = None
    current_token: str | None = None
    current_shared_secret: str | None = None


class AuditQuery(BaseModel):
    node_id: str
    token: str
    limit: int = Field(20, ge=1, le=200)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Any, exc: RequestValidationError
):
    for error in exc.errors():
        if error.get("type") in {"payload.too_large", "value_error.payload.too_large"}:
            return JSONResponse(
                status_code=status.HTTP_413_CONTENT_TOO_LARGE,
                content={"detail": f"El payload excede {MAX_PAYLOAD_BYTES} bytes"},
            )
    return await request_validation_exception_handler(request, exc)


@app.post("/emit")
def emit(req: EmitRequest) -> JSONResponse:
    if req.pattern_sequence:
        pattern = LeptonicPattern(req.pattern_name, req.pattern_sequence)
    else:
        pattern = LeptonicPattern(req.pattern_name, [1.0])
    signal = pattern.to_signal(req.density)
    packet = MuonPacket(req.payload.encode("utf-8"), signal)
    if not guard.verify(req.node_id, req.token, packet):
        raise HTTPException(status_code=403, detail="Token inválido para el nodo")

    node = registry.get(req.node_id)
    if node is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El nodo no está registrado",
        )

    try:
        result = engine.emit(
            node,
            req.payload.encode("utf-8"),
            signal,
        )
    except QueueSaturatedError as exc:
        metrics = engine.metrics
        guard.audit_log.record(
            "emit_rejected",
            req.node_id,
            reason="queue_saturated",
            max_pending=metrics.get("max_pending_events"),
            queue_size=metrics.get("queue_size"),
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
    event = result.event

    metric = adaptive_metric_collector.collect(event.packet, device_id=req.node_id)
    adaptive_topology.adjust(node, metric)

    payload: dict[str, object] = {
        "status": "ok" if result.delivered else "partial",
        "node": event.node.identifier,
    }
    if result.listener_errors:
        payload["listener_errors"] = result.listener_errors

    status_code = (
        status.HTTP_200_OK if result.delivered else status.HTTP_207_MULTI_STATUS
    )
    return JSONResponse(status_code=status_code, content=payload)


@app.post("/token")
def issue_token(req: TokenRequest) -> dict[str, str]:
    node = registry.get(req.node_id)
    if node is None:
        raise HTTPException(
            status_code=404, detail="El nodo debe registrarse antes de solicitar token"
        )
    try:
        token = guard.issue_token(node.identifier, req.shared_secret)
    except TokenIssuanceBlocked as exc:
        retry_after = _retry_after_header(exc.retry_after)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=str(exc),
            headers={"Retry-After": retry_after},
        ) from exc
    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc
    return {"token": token}


@app.post("/nodes/register", status_code=status.HTTP_201_CREATED)
def register_node(
    req: NodeRegistrationRequest,
    admin_token: str | None = Header(
        None,
        alias=REGISTRATION_TOKEN_HEADER,
        description="Token administrativo necesario para registrar nodos",
    ),
) -> dict[str, str]:
    registration_authorizer.authorize(admin_token, req.node_id)
    existing = registry.get(req.node_id)
    if existing is None:
        try:
            guard.register_shared_secret(req.node_id, req.shared_secret)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

        node = HoloNode(req.node_id, req.location, req.capabilities or [])
        try:
            registry.add(node)
        except Exception:
            guard.revoke_shared_secret(req.node_id)
            raise
    else:
        try:
            guard.update_shared_secret(
                req.node_id,
                req.shared_secret,
                token=req.current_token,
                previous_secret=req.current_shared_secret,
            )
        except PermissionError as exc:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)
            ) from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

        existing.location = req.location
        if req.capabilities is not None:
            existing.capabilities = req.capabilities
        node = existing

    LOGGER.info("Nodo %s registrado para emisión", req.node_id)
    return {"status": "registered", "node": node.identifier}


@app.get("/listen")
def listen(
    node_id: str | None = Query(None, description="Identificador del nodo autorizado"),
    authorization: str | None = Header(
        None,
        alias="Authorization",
        description="Cabecera Bearer con el token emitido por el guardián leptónico",
    ),
    legacy_token: str | None = Query(
        None,
        alias="token",
        include_in_schema=False,
        description="Token legado en la URL (rechazado)",
    ),
) -> dict[str, object]:
    if node_id is None:
        guard.audit_log.record(
            "listen_denied",
            "unknown",
            reason="missing_node_id",
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Se requieren credenciales válidas",
        )

    if legacy_token is not None:
        guard.audit_log.record(
            "listen_denied",
            node_id,
            reason="token_in_query",
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El token debe enviarse en la cabecera Authorization",
        )

    if authorization is None:
        guard.audit_log.record(
            "listen_denied",
            node_id,
            reason="missing_authorization",
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Se requieren credenciales válidas",
        )

    try:
        token = _extract_bearer_token(authorization)
    except ValueError as exc:
        guard.audit_log.record(
            "listen_denied",
            node_id,
            reason="invalid_authorization_format",
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    if not guard.verify_token(node_id, token):
        guard.audit_log.record("listen_denied", node_id, reason="invalid_token")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Token inválido",
        )

    packet = engine.listen(node_id)
    if packet is None:
        raise HTTPException(status_code=404, detail="No hay paquetes disponibles")
    return packet.as_dict()


@app.get("/status")
def read_status() -> dict[str, float | int]:
    metrics = engine.metrics
    return {"nodes": len(registry.all()), **metrics}


@app.get("/nodes")
def list_nodes(
    limit: int = Query(50, ge=1, le=100), offset: int = Query(0, ge=0)
) -> list[dict[str, str]]:
    try:
        nodes = registry.paginate(offset=offset, limit=limit)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return [
        {"identifier": node.identifier, "location": node.location}
        for node in nodes
    ]


@app.get("/adaptive/status")
def adaptive_status() -> dict[str, object]:
    """Devuelve el orden preferido de nodos y las métricas registradas."""

    order = adaptive_topology.preferred_nodes()
    weights = adaptive_topology.weights.copy()
    history = list(adaptive_topology.controller.history)
    return {"order": order, "weights": weights, "history": history}


@app.post("/audit/events")
def audit_events(query: AuditQuery) -> dict[str, object]:
    if not guard.verify_token(query.node_id, query.token):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Token inválido")

    now = datetime.now(timezone.utc)
    allowed, retry_after = audit_rate_limiter.try_acquire(query.node_id, now)
    if not allowed:
        guard.audit_log.record(
            "audit_rate_limited",
            query.node_id,
            limit=query.limit,
            window=str(AUDIT_RATE_WINDOW),
            retry_after=retry_after,
        )
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Demasiadas consultas de auditoría, intente más tarde",
            headers={"Retry-After": _retry_after_header(retry_after)},
        )

    events = [
        {
            "timestamp": event.timestamp.isoformat(),
            "event": event.event,
            "node_id": event.node_id,
            "details": event.details,
        }
        for event in guard.export_audit_events(query.limit, node_id=query.node_id)
    ]

    guard.audit_log.record(
        "audit_events_served",
        query.node_id,
        returned=len(events),
        limit=query.limit,
    )

    return {"events": events}

