"""Pruebas de la API FastAPI."""
import asyncio

import base64
from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient

from holonet.interface.fastapi_app import (
    MAX_PAYLOAD_BYTES,
    MAX_PENDING_EVENTS,
    AUDIT_RATE_LIMIT,
    REGISTRATION_TOKEN_HEADER,
    app,
    audit_rate_limiter,
    configure_adaptive,
    configure_registration_tokens,
    engine,
    guard,
    registry,
)
from holonet.network.adaptive_topology import AdaptiveTopology
from holonet.interface.websocket_bridge import WebSocketBridge
from holonet.core.nodes import HoloNode
from holonet.core.packets import LeptonicPattern
from holonet.simulation.adaptive_controller import AdaptiveController
from holonet.simulation.engine import SimulationEngine

STRONG_SECRET = "ClaveUltraSegura123!"
STATUS_SECRET = "ClaveStatus456$"
ADAPTIVE_SECRET = "ClaveAdaptativa789?"
CORRECT_SECRET = "CorrectaSegura890#"
WRONG_SECRET = "IncorrectaSegura901$"
LIMIT_SECRET = "LimiteSeguro654?"
AUDIT_SECRET = "AuditoriaSegura321!"
ROTATED_SECRET = "ClaveRotada789!"
INITIAL_SECRET = "ClaveInicial654$"
ADMIN_TOKEN = "test-admin-token"


def setup_function() -> None:
    registry._nodes.clear()
    store = getattr(guard, "_store", None)
    if store is not None and hasattr(store, "_tokens"):
        store._tokens.clear()
    secrets = getattr(guard, "_secrets", None)
    if isinstance(secrets, dict):
        secrets.clear()
    audit = getattr(guard, "audit_log", None)
    if audit is not None:
        audit.clear()
    engine.flush()
    engine.reset_metrics()
    engine.max_pending_events = MAX_PENDING_EVENTS
    engine.listeners.clear()
    engine.async_queues.clear()
    audit_rate_limiter.reset()
    attempts = getattr(guard, "_failed_attempts", None)
    if isinstance(attempts, dict):
        attempts.clear()
    lockouts = getattr(guard, "_lockouts", None)
    if isinstance(lockouts, dict):
        lockouts.clear()
    guard._max_failed_attempts = 3
    guard._failed_attempt_window = timedelta(seconds=30)
    guard._lockout_duration = timedelta(seconds=1)
    configure_adaptive(AdaptiveTopology(AdaptiveController()))
    configure_registration_tokens([ADMIN_TOKEN])


def registration_headers(extra: dict[str, str] | None = None) -> dict[str, str]:
    headers = {REGISTRATION_TOKEN_HEADER: ADMIN_TOKEN}
    if extra:
        headers.update(extra)
    return headers


def decode_payload_dict(payload: dict[str, str]) -> bytes:
    assert payload["encoding"] == "base64"
    return base64.b64decode(payload["data"])


def test_emit_and_listen_endpoint():
    client = TestClient(app)
    register_response = client.post(
        "/nodes/register",
        json={
            "node_id": "api-node",
            "location": "Orbital",
            "shared_secret": STRONG_SECRET,
        },
        headers=registration_headers(),
    )
    assert register_response.status_code == 201

    token_response = client.post(
        "/token",
        json={"node_id": "api-node", "shared_secret": STRONG_SECRET},
    )
    assert token_response.status_code == 200
    token = token_response.json()["token"]

    response = client.post(
        "/emit",
        json={
            "node_id": "api-node",
            "payload": "hola",
            "pattern_name": "simple",
            "pattern_sequence": [1.0],
            "density": 1.0,
            "token": token,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"

    forbidden = client.post(
        "/emit",
        json={
            "node_id": "api-node",
            "payload": "hola",
            "pattern_name": "simple",
            "pattern_sequence": [1.0],
            "density": 1.0,
            "token": "token-invalido",
        },
    )
    assert forbidden.status_code == 403

    missing_credentials = client.get("/listen")
    assert missing_credentials.status_code == 401

    query_token = client.get(
        "/listen", params={"node_id": "api-node", "token": token}
    )
    assert query_token.status_code == 400

    invalid_token = client.get(
        "/listen",
        params={"node_id": "api-node"},
        headers={"Authorization": "Bearer token-invalido"},
    )
    assert invalid_token.status_code == 403

    listen = client.get(
        "/listen",
        params={"node_id": "api-node"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert listen.status_code == 200
    payload = listen.json()["payload"]
    assert decode_payload_dict(payload) == b"hola"


def test_listen_requires_bearer_authorization_header():
    client = TestClient(app)
    client.post(
        "/nodes/register",
        json={
            "node_id": "api-node",
            "location": "Orbital",
            "shared_secret": STRONG_SECRET,
        },
        headers=registration_headers(),
    )
    token = client.post(
        "/token", json={"node_id": "api-node", "shared_secret": STRONG_SECRET}
    ).json()["token"]

    malformed = client.get(
        "/listen",
        params={"node_id": "api-node"},
        headers={"Authorization": token},
    )
    assert malformed.status_code == 400
    assert "Bearer" in malformed.json()["detail"]

    audit_events = guard.audit_log.recent()
    assert any(
        event.event == "listen_denied"
        and event.node_id == "api-node"
        and event.details.get("reason") == "invalid_authorization_format"
        for event in audit_events
    )


def test_emit_reports_listener_errors():
    client = TestClient(app)
    client.post(
        "/nodes/register",
        json={
            "node_id": "api-node",
            "location": "Orbital",
            "shared_secret": STRONG_SECRET,
        },
        headers=registration_headers(),
    )
    token = client.post(
        "/token", json={"node_id": "api-node", "shared_secret": STRONG_SECRET}
    ).json()["token"]

    def faulty_listener(event):  # type: ignore[unused-argument]
        raise RuntimeError("fallo de adaptador")

    engine.register_listener(faulty_listener)

    try:
        response = client.post(
            "/emit",
            json={
                "node_id": "api-node",
                "payload": "hola",
                "pattern_name": "simple",
                "pattern_sequence": [1.0],
                "density": 1.0,
                "token": token,
            },
        )
    finally:
        engine.unregister_listener(faulty_listener)

    assert response.status_code == 207
    data = response.json()
    assert data["status"] == "partial"
    assert any("RuntimeError" in error for error in data["listener_errors"])


def test_listen_prevents_cross_node_consumption():
    client = TestClient(app)
    client.post(
        "/nodes/register",
        json={
            "node_id": "alpha",
            "location": "Orbital",
            "shared_secret": STRONG_SECRET,
        },
        headers=registration_headers(),
    )
    client.post(
        "/nodes/register",
        json={
            "node_id": "beta",
            "location": "Orbital",
            "shared_secret": STATUS_SECRET,
        },
        headers=registration_headers(),
    )

    alpha_token = client.post(
        "/token", json={"node_id": "alpha", "shared_secret": STRONG_SECRET}
    ).json()["token"]
    beta_token = client.post(
        "/token", json={"node_id": "beta", "shared_secret": STATUS_SECRET}
    ).json()["token"]

    client.post(
        "/emit",
        json={
            "node_id": "alpha",
            "payload": "sigilo",
            "pattern_name": "simple",
            "pattern_sequence": [1.0],
            "density": 1.0,
            "token": alpha_token,
        },
    )

    foreign_attempt = client.get(
        "/listen",
        params={"node_id": "beta"},
        headers={"Authorization": f"Bearer {beta_token}"},
    )
    assert foreign_attempt.status_code == 404

    rightful = client.get(
        "/listen",
        params={"node_id": "alpha"},
        headers={"Authorization": f"Bearer {alpha_token}"},
    )
    assert rightful.status_code == 200
    rightful_payload = rightful.json()["payload"]
    assert decode_payload_dict(rightful_payload) == b"sigilo"

    empty = client.get(
        "/listen",
        params={"node_id": "alpha"},
        headers={"Authorization": f"Bearer {alpha_token}"},
    )
    assert empty.status_code == 404


def test_status_and_nodes():
    client = TestClient(app)
    register_response = client.post(
        "/nodes/register",
        json={
            "node_id": "status-node",
            "location": "Orbital",
            "shared_secret": STATUS_SECRET,
        },
        headers=registration_headers(),
    )
    assert register_response.status_code == 201

    baseline = client.get("/status")
    assert baseline.status_code == 200
    baseline_data = baseline.json()
    assert baseline_data["nodes"] == 1
    assert baseline_data["events_emitted"] == 0
    assert baseline_data["queue_size"] == 0
    assert baseline_data["average_latency_ms"] == 0.0
    assert baseline_data["rejected_events"] == 0
    assert baseline_data["max_pending_events"] == MAX_PENDING_EVENTS

    token_response = client.post(
        "/token", json={"node_id": "status-node", "shared_secret": STATUS_SECRET}
    )
    assert token_response.status_code == 200
    token = token_response.json()["token"]
    emit_response = client.post(
        "/emit",
        json={
            "node_id": "status-node",
            "payload": "ping",
            "pattern_name": "simple",
            "pattern_sequence": [1.0],
            "density": 1.0,
            "token": token,
        },
    )
    assert emit_response.status_code == 200

    after_emit = client.get("/status")
    assert after_emit.status_code == 200
    after_emit_data = after_emit.json()
    assert after_emit_data["events_emitted"] == 1
    assert after_emit_data["queue_size"] == 1
    assert after_emit_data["average_latency_ms"] == 0.0
    assert after_emit_data["nodes"] == 1
    assert after_emit_data["rejected_events"] == 0

    unauthenticated = client.get("/listen")
    assert unauthenticated.status_code == 401

    listen_response = client.get(
        "/listen",
        params={"node_id": "status-node"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert listen_response.status_code == 200

    after_listen = client.get("/status")
    assert after_listen.status_code == 200
    after_listen_data = after_listen.json()
    assert after_listen_data["queue_size"] == 0
    assert after_listen_data["events_emitted"] == 1
    assert after_listen_data["average_latency_ms"] >= 0.0
    assert after_listen_data["rejected_events"] == 0

    nodes = client.get("/nodes")
    assert nodes.status_code == 200
    assert isinstance(nodes.json(), list)


def test_emit_returns_503_when_queue_saturated():
    client = TestClient(app)
    previous_limit = engine.max_pending_events
    try:
        engine.max_pending_events = 1

        client.post(
            "/nodes/register",
            json={
                "node_id": "saturado",
                "location": "Orbital",
                "shared_secret": STRONG_SECRET,
            },
            headers=registration_headers(),
        )
        token = client.post(
            "/token",
            json={"node_id": "saturado", "shared_secret": STRONG_SECRET},
        ).json()["token"]

        first = client.post(
            "/emit",
            json={
                "node_id": "saturado",
                "payload": "uno",
                "pattern_name": "simple",
                "pattern_sequence": [1.0],
                "density": 1.0,
                "token": token,
            },
        )
        assert first.status_code == 200

        saturated = client.post(
            "/emit",
            json={
                "node_id": "saturado",
                "payload": "dos",
                "pattern_name": "simple",
                "pattern_sequence": [1.0],
                "density": 1.0,
                "token": token,
            },
        )
        assert saturated.status_code == 503
        assert "límite" in saturated.json()["detail"]

        metrics = engine.metrics
        assert metrics["rejected_events"] == 1
        assert metrics["queue_size"] == 1

        audit_events = guard.audit_log.recent_for_node("saturado")
        assert any(event.event == "emit_rejected" for event in audit_events)
    finally:
        engine.flush()
        engine.reset_metrics()
        engine.max_pending_events = previous_limit


def test_nodes_pagination():
    client = TestClient(app)
    for idx in range(10):
        registry.add(HoloNode(f"node-{idx}", f"Sector-{idx}"))
        guard.register_shared_secret(
            f"node-{idx}", f"Clave{idx:02d}Segura!"
        )

    # Página intermedia
    page = client.get("/nodes", params={"limit": 3, "offset": 4})
    assert page.status_code == 200
    data = page.json()
    assert len(data) == 3
    assert data[0]["identifier"] == "node-4"
    assert data[1]["identifier"] == "node-5"
    assert data[2]["identifier"] == "node-6"

    # Valores por defecto recuperan todos los nodos disponibles
    default_page = client.get("/nodes")
    assert default_page.status_code == 200
    assert len(default_page.json()) == 10

    # Validación de parámetros fuera de rango
    invalid_limit = client.get("/nodes", params={"limit": 0})
    assert invalid_limit.status_code == 422

    invalid_offset = client.get("/nodes", params={"offset": -1})
    assert invalid_offset.status_code == 422


def test_register_requires_credentials_for_updates():
    client = TestClient(app)
    initial = client.post(
        "/nodes/register",
        json={
            "node_id": "secure-node",
            "location": "Orbital",
            "shared_secret": INITIAL_SECRET,
        },
        headers=registration_headers(),
    )
    assert initial.status_code == 201

    unauthorized = client.post(
        "/nodes/register",
        json={
            "node_id": "secure-node",
            "location": "Orbital-2",
            "shared_secret": ROTATED_SECRET,
        },
        headers=registration_headers(),
    )
    assert unauthorized.status_code == 403

    wrong_secret = client.post(
        "/nodes/register",
        json={
            "node_id": "secure-node",
            "location": "Orbital-2",
            "shared_secret": ROTATED_SECRET,
            "current_shared_secret": WRONG_SECRET,
        },
        headers=registration_headers(),
    )
    assert wrong_secret.status_code == 403

    token_response = client.post(
        "/token",
        json={"node_id": "secure-node", "shared_secret": INITIAL_SECRET},
    )
    assert token_response.status_code == 200
    token = token_response.json()["token"]

    update = client.post(
        "/nodes/register",
        json={
            "node_id": "secure-node",
            "location": "Orbital-2",
            "shared_secret": ROTATED_SECRET,
            "current_token": token,
            "capabilities": ["sensor"],
        },
        headers=registration_headers(),
    )
    assert update.status_code == 201

    new_token = client.post(
        "/token",
        json={"node_id": "secure-node", "shared_secret": ROTATED_SECRET},
    )
    assert new_token.status_code == 200

    legacy_token = client.post(
        "/token",
        json={"node_id": "secure-node", "shared_secret": INITIAL_SECRET},
    )
    assert legacy_token.status_code == 403

    nodes = client.get("/nodes")
    assert nodes.status_code == 200
    payload = nodes.json()
    assert payload[0]["location"] == "Orbital-2"


def test_register_rejects_missing_admin_token():
    client = TestClient(app)

    response = client.post(
        "/nodes/register",
        json={
            "node_id": "missing-admin",
            "location": "Orbital",
            "shared_secret": STRONG_SECRET,
        },
    )

    assert response.status_code == 401
    detail = response.json()["detail"].lower()
    assert "token" in detail
    events = guard.audit_log.recent()
    assert any(
        entry.event == "registration_denied"
        and entry.node_id == "missing-admin"
        and entry.details.get("reason") == "missing_admin_token"
        for entry in events
    )


def test_register_rejects_invalid_admin_token():
    client = TestClient(app)

    response = client.post(
        "/nodes/register",
        json={
            "node_id": "invalid-admin",
            "location": "Orbital",
            "shared_secret": STRONG_SECRET,
        },
        headers={REGISTRATION_TOKEN_HEADER: "wrong-token"},
    )

    assert response.status_code == 403
    events = guard.audit_log.recent()
    assert any(
        entry.event == "registration_denied"
        and entry.node_id == "invalid-admin"
        and entry.details.get("reason") == "invalid_admin_token"
        for entry in events
    )


def test_token_endpoint_enforces_rate_limit():
    client = TestClient(app)
    client.post(
        "/nodes/register",
        json={
            "node_id": "rate-node",
            "location": "Orbital",
            "shared_secret": LIMIT_SECRET,
        },
        headers=registration_headers(),
    )

    for _ in range(guard._max_failed_attempts - 1):
        response = client.post(
            "/token",
            json={"node_id": "rate-node", "shared_secret": WRONG_SECRET},
        )
        assert response.status_code == 403

    blocked = client.post(
        "/token",
        json={"node_id": "rate-node", "shared_secret": WRONG_SECRET},
    )
    assert blocked.status_code == 429
    assert blocked.headers.get("Retry-After") is not None

    guard._lockouts["rate-node"] = datetime.now(timezone.utc) - guard._lockout_duration

    recovered = client.post(
        "/token",
        json={"node_id": "rate-node", "shared_secret": LIMIT_SECRET},
    )
    assert recovered.status_code == 200


def test_register_does_not_leave_orphan_node_on_secret_error():
    client = TestClient(app)

    response = client.post(
        "/nodes/register",
        json={
            "node_id": "weak-node",
            "location": "Orbital",
            "shared_secret": "corta123",
        },
        headers=registration_headers(),
    )

    assert response.status_code == 400
    assert registry.get("weak-node") is None


def test_adaptive_status_endpoint():
    client = TestClient(app)

    baseline = client.get("/adaptive/status")
    assert baseline.status_code == 200
    assert baseline.json() == {"order": [], "weights": {}, "history": []}

    client.post(
        "/nodes/register",
        json={
            "node_id": "adaptive-node",
            "location": "Orbital",
            "shared_secret": ADAPTIVE_SECRET,
        },
        headers=registration_headers(),
    )
    token_response = client.post(
        "/token",
        json={"node_id": "adaptive-node", "shared_secret": ADAPTIVE_SECRET},
    )
    assert token_response.status_code == 200
    token = token_response.json()["token"]

    emit_response = client.post(
        "/emit",
        json={
            "node_id": "adaptive-node",
            "payload": "hola",
            "pattern_name": "simple",
            "pattern_sequence": [1.0, 0.5],
            "density": 1.5,
            "token": token,
        },
    )
    assert emit_response.status_code == 200

    status = client.get("/adaptive/status")
    assert status.status_code == 200
    payload = status.json()
    assert payload["order"] == ["adaptive-node"]
    assert "adaptive-node" in payload["weights"]
    assert payload["weights"]["adaptive-node"] > 0
    assert payload["history"]
    assert payload["history"][-1] > 0


def test_websocket_stream_waits_and_resumes():
    asyncio.run(_assert_websocket_stream())


async def _assert_websocket_stream() -> None:
    engine = SimulationEngine()
    bridge = WebSocketBridge(engine, guard)
    node = HoloNode("ws-node", "Orbital")
    pattern = LeptonicPattern("simple", [1.0])
    signal = pattern.to_signal(0.5)

    guard.register_shared_secret("ws-listener", "EscuchaSegura123!?")
    listener_token = guard.issue_token("ws-listener", "EscuchaSegura123!?")

    stream = bridge.stream_packets("ws-listener", listener_token)
    agen = stream.__aiter__()

    pending = asyncio.create_task(agen.__anext__())
    await asyncio.sleep(0)
    assert not pending.done()

    engine.emit(node, b"uno", signal, recipients=["ws-listener"])
    first = await pending
    assert decode_payload_dict(first["payload"]) == b"uno"

    follow_up = asyncio.create_task(agen.__anext__())
    await asyncio.sleep(0)
    assert not follow_up.done()

    engine.emit(node, b"dos", signal, recipients=["ws-listener"])
    second = await follow_up
    assert decode_payload_dict(second["payload"]) == b"dos"

    await agen.aclose()


def test_websocket_stream_rejects_invalid_token():
    async def runner() -> None:
        engine = SimulationEngine()
        bridge = WebSocketBridge(engine, guard)
        guard.register_shared_secret("ws-listener", "EscuchaSegura123!?")

        stream = bridge.stream_packets("ws-listener", "token-invalido")
        agen = stream.__aiter__()

        with pytest.raises(PermissionError):
            await agen.__anext__()

        assert not engine.async_queues

    asyncio.run(runner())


def test_token_request_rejects_invalid_secret():
    client = TestClient(app)
    client.post(
        "/nodes/register",
        json={
            "node_id": "invalid-secret-node",
            "location": "Orbital",
            "shared_secret": CORRECT_SECRET,
        },
        headers=registration_headers(),
    )

    response = client.post(
        "/token",
        json={"node_id": "invalid-secret-node", "shared_secret": WRONG_SECRET},
    )
    assert response.status_code == 403


def test_emit_rejects_large_payload():
    client = TestClient(app)
    client.post(
        "/nodes/register",
        json={
            "node_id": "limite-node",
            "location": "Orbital",
            "shared_secret": LIMIT_SECRET,
        },
        headers=registration_headers(),
    )
    token = client.post(
        "/token", json={"node_id": "limite-node", "shared_secret": LIMIT_SECRET}
    ).json()["token"]

    oversized = "x" * (MAX_PAYLOAD_BYTES + 1)
    response = client.post(
        "/emit",
        json={
            "node_id": "limite-node",
            "payload": oversized,
            "pattern_name": "simple",
            "pattern_sequence": [1.0],
            "density": 1.0,
            "token": token,
        },
    )
    assert response.status_code == 413


def test_audit_endpoint_returns_recent_events():
    client = TestClient(app)
    client.post(
        "/nodes/register",
        json={
            "node_id": "auditable",
            "location": "Orbital",
            "shared_secret": AUDIT_SECRET,
        },
        headers=registration_headers(),
    )
    token = client.post(
        "/token", json={"node_id": "auditable", "shared_secret": AUDIT_SECRET}
    ).json()["token"]

    client.post(
        "/emit",
        json={
            "node_id": "auditable",
            "payload": "ping",
            "pattern_name": "simple",
            "pattern_sequence": [1.0],
            "density": 1.0,
            "token": token,
        },
    )

    guard.audit_log.record("intruder_probe", "intruder", context="manual")

    audit_response = client.post(
        "/audit/events",
        json={"node_id": "auditable", "token": token, "limit": 5},
    )
    assert audit_response.status_code == 200
    events = audit_response.json()["events"]
    assert events
    assert all(event["node_id"] == "auditable" for event in events)
    assert any(event["event"] == "token_issued" for event in events)

    audit_events = guard.audit_log.recent()
    assert any(
        entry.event == "audit_events_served"
        and entry.node_id == "auditable"
        and entry.details.get("returned") == len(events)
        for entry in audit_events
    )
    assert not any(entry.event == "audit_access_denied" for entry in audit_events)


def test_audit_endpoint_rate_limits_requests():
    client = TestClient(app)
    client.post(
        "/nodes/register",
        json={
            "node_id": "auditable",
            "location": "Orbital",
            "shared_secret": AUDIT_SECRET,
        },
        headers=registration_headers(),
    )
    token = client.post(
        "/token", json={"node_id": "auditable", "shared_secret": AUDIT_SECRET}
    ).json()["token"]

    for _ in range(AUDIT_RATE_LIMIT):
        response = client.post(
            "/audit/events",
            json={"node_id": "auditable", "token": token, "limit": 5},
        )
        assert response.status_code == 200

    limited = client.post(
        "/audit/events",
        json={"node_id": "auditable", "token": token, "limit": 5},
    )
    assert limited.status_code == 429
    assert limited.headers.get("Retry-After") is not None

    audit_events = guard.audit_log.recent()
    assert any(
        entry.event == "audit_rate_limited"
        and entry.node_id == "auditable"
        and "retry_after" in entry.details
        for entry in audit_events
    )
