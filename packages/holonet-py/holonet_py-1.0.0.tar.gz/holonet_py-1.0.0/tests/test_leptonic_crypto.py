"""Pruebas del módulo ``leptonic_crypto``."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from holonet.security.leptonic_crypto import (
    CoherenceSecureChannel,
    MERKLE_EMPTY_ROOT,
    NodeCoherenceState,
    SignatureMerkleLog,
    generate_energy_token,
    simulate_quantum_signature,
)


def test_energy_tokens_are_unique_with_nonce() -> None:
    token_one = generate_energy_token(
        "node-a", 12.5, 0.87, nonce=b"alpha-nonce-0001"
    )
    token_two = generate_energy_token(
        "node-a", 12.5, 0.87, nonce=b"alpha-nonce-0002"
    )
    assert token_one != token_two


def test_simulated_signature_is_deterministic() -> None:
    payload = b"muonic-payload"
    issued_at = datetime(2042, 5, 17, tzinfo=timezone.utc)
    signature_one = simulate_quantum_signature(
        payload,
        node_id="node-a",
        secret="ClaveUltraSecreta$1",
        energy_ev=14.2,
        coherence=0.92,
        nonce=b"firmado",
        issued_at=issued_at,
    )
    signature_two = simulate_quantum_signature(
        payload,
        node_id="node-a",
        secret="ClaveUltraSecreta$1",
        energy_ev=14.2,
        coherence=0.92,
        nonce=b"firmado",
        issued_at=issued_at,
    )
    assert signature_one == signature_two


def test_coherence_channel_requires_synchronization() -> None:
    channel = CoherenceSecureChannel(energy_tolerance=0.5, coherence_tolerance=0.02)
    token_a = generate_energy_token("node-a", 10.0, 0.8, nonce=b"sync-a")
    token_b = generate_energy_token("node-b", 10.1, 0.81, nonce=b"sync-b")
    state_a = NodeCoherenceState("node-a", 10.0, 0.8, token_a)
    state_b = NodeCoherenceState("node-b", 10.1, 0.81, token_b)

    channel_token = channel.establish(state_a, state_b)
    assert channel_token is not None
    assert channel.can_decode("node-a", "node-b", channel_token)

    token_c = generate_energy_token("node-c", 11.5, 0.7, nonce=b"out-sync")
    state_c = NodeCoherenceState("node-c", 11.5, 0.7, token_c)
    assert channel.establish(state_a, state_c) is None


def test_merkle_log_tracks_signatures() -> None:
    log = SignatureMerkleLog()
    assert log.root() == MERKLE_EMPTY_ROOT

    signature = simulate_quantum_signature(
        b"packet-one",
        node_id="node-a",
        secret="ClaveFirmante!",
        energy_ev=9.5,
        coherence=0.77,
        nonce=b"leaf-1",
        issued_at=datetime(2040, 1, 1, tzinfo=timezone.utc),
    )
    root_after_first = log.register(signature)
    assert root_after_first != MERKLE_EMPTY_ROOT

    second_signature = simulate_quantum_signature(
        b"packet-two",
        node_id="node-b",
        secret="ClaveFirmante!",
        energy_ev=9.6,
        coherence=0.75,
        nonce=b"leaf-2",
        issued_at=datetime(2040, 1, 1, tzinfo=timezone.utc),
    )
    root_after_second = log.register(second_signature)
    assert root_after_second != root_after_first

    proof = log.proof(0)
    assert proof  # Debe contener al menos el hash hermano
    with pytest.raises(IndexError):
        log.proof(5)
