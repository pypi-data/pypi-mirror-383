"""Pruebas unitarias del módulo de seguridad leptónica."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from holonet.security.leptonic_guard import LeptonicGuard
from holonet.security.token_store import InMemoryTokenStore


def test_expired_tokens_are_rejected_and_revoked() -> None:
    store = InMemoryTokenStore()
    guard = LeptonicGuard(store=store, token_ttl=timedelta(minutes=1))
    guard.register_shared_secret("node", "ClaveExpirada123!")
    token = guard.issue_token("node", "ClaveExpirada123!")

    expired_at = datetime.now(timezone.utc) - timedelta(seconds=1)
    store.store("node", token, expires_at=expired_at)

    assert not guard.verify_token("node", token)
    assert store.retrieve("node") is None


def test_tokens_with_different_length_are_rejected() -> None:
    store = InMemoryTokenStore()
    guard = LeptonicGuard(store=store)
    guard.register_shared_secret("node", "LongitudSegura456!")
    token = guard.issue_token("node", "LongitudSegura456!")

    assert not guard.verify_token("node", token + "extra")
    assert not guard.verify_token("node", "short")


def test_audit_log_rotation_and_metrics() -> None:
    guard = LeptonicGuard(audit_max_events=3)

    for idx in range(5):
        guard.audit_log.record("custom_event", f"node-{idx}")

    events = list(guard.export_audit_events(10))
    assert len(events) == 3
    assert events[0].node_id == "node-2"
    metrics = guard.audit_metrics()
    assert metrics["capacity"] == 3
    assert metrics["dropped_events"] == 2


def test_secrets_use_unique_salt_and_require_strength() -> None:
    guard = LeptonicGuard()
    guard.register_shared_secret("node-1", "ClaveUnica789#")
    guard.register_shared_secret("node-2", "ClaveUnica789#")

    stored_one = guard._secrets["node-1"]
    stored_two = guard._secrets["node-2"]
    assert stored_one.salt != stored_two.salt
    assert stored_one.derived_key != stored_two.derived_key

    with pytest.raises(ValueError):
        guard.register_shared_secret("node-weak", "corta123")


def test_secret_rotation_revokes_existing_tokens() -> None:
    store = InMemoryTokenStore()
    guard = LeptonicGuard(store=store)
    guard.register_shared_secret("node", "ClaveOriginal123!")
    token = guard.issue_token("node", "ClaveOriginal123!")

    guard.update_shared_secret("node", "NuevaClave456$?", token=token)

    assert not guard.verify_token("node", token)
    events = list(guard.export_audit_events(10))
    assert any(
        event.event == "token_revoked" and event.details.get("reason") == "secret_rotated"
        for event in events
    )


def test_revoking_secret_removes_tokens() -> None:
    store = InMemoryTokenStore()
    guard = LeptonicGuard(store=store)
    guard.register_shared_secret("node", "ClaveRevocable789#")
    token = guard.issue_token("node", "ClaveRevocable789#")

    guard.revoke_shared_secret("node")

    assert not guard.verify_token("node", token)
    assert "node" not in guard._secrets
    events = list(guard.export_audit_events(10))
    assert any(
        event.event == "token_revoked" and event.details.get("reason") == "secret_revoked"
        for event in events
    )
