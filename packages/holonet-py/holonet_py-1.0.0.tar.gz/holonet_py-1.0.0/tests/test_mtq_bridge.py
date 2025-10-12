"""Pruebas para MTQBridge y el decorador ``tunnelable``."""
from __future__ import annotations

import asyncio
import base64
import json

import pytest

from holonet.mtq import (
    LeptonicSignature,
    NodeQuantumState,
    QuantumPacket,
    TunnelEngine,
    tunnelable,
)
from holonet.transmission import LocalFiber, MTQBridge
from holonet.core.packets import MuonPacket, MuonSignal


def _make_signature() -> LeptonicSignature:
    return LeptonicSignature(flavor="muon", generation=2, polarization=0.45)


def _make_state() -> NodeQuantumState:
    return NodeQuantumState(temperature_k=250.0, entanglement_entropy=0.1, stability_index=0.95)


def _make_packet(payload: str = "demo", coherence: float = 0.9) -> QuantumPacket:
    signature = _make_signature()
    metadata = {"payload": payload, "channel": "alpha"}
    return QuantumPacket(leptonic_signature=signature, energy_ev=1.5, coherence=coherence, metadata=metadata)


def _decode_payload(payload: dict[str, str]) -> str:
    assert payload["encoding"] == "base64"
    return base64.b64decode(payload["data"]).decode("utf-8")


def test_mtq_bridge_transmit_and_receive_roundtrip() -> None:
    fiber = LocalFiber()
    engine = TunnelEngine(random_source=lambda: 0.0)
    bridge = MTQBridge(tunnel_engine=engine, fiber=fiber)
    state = _make_state()

    packet = _make_packet()
    original_coherence = packet.coherence

    result = bridge.transmit(packet, state)
    assert result.tunneled is True
    assert result.muon_packet is not None
    assert result.muon_packet.payload
    assert json.loads(result.muon_packet.payload.decode("utf-8"))["payload"] == "demo"

    received = bridge.receive()
    assert isinstance(received, QuantumPacket)
    assert received.leptonic_signature == _make_signature()
    assert received.energy_ev == pytest.approx(1.5)
    assert received.coherence == pytest.approx(original_coherence)
    assert received.metadata["channel"] == "alpha"


def test_mtq_bridge_drain_multiple_packets() -> None:
    fiber = LocalFiber()
    engine = TunnelEngine(random_source=lambda: 0.0)
    bridge = MTQBridge(tunnel_engine=engine, fiber=fiber)
    state = _make_state()

    packets = [_make_packet(payload=f"pkt-{idx}", coherence=0.8 + idx * 0.05) for idx in range(3)]
    expected_payloads = []
    for packet in packets:
        expected_payloads.append(packet.metadata["payload"])
        bridge.transmit(packet, state)

    drained = list(bridge.drain_quantum())
    assert len(drained) == len(expected_payloads)
    assert [pkt.metadata["payload"] for pkt in drained] == expected_payloads


def test_mtq_bridge_receive_without_fiber_returns_none() -> None:
    bridge = MTQBridge(tunnel_engine=TunnelEngine(random_source=lambda: 0.0))
    assert bridge.receive() is None


def test_tunnelable_sync_function() -> None:
    bridge = MTQBridge(tunnel_engine=TunnelEngine(random_source=lambda: 0.0), fiber=LocalFiber())
    state = _make_state()

    @tunnelable
    def emit_packet() -> QuantumPacket:
        return _make_packet(payload="sync")

    response = emit_packet(mtq_bridge=bridge, quantum_state=state)
    assert response["tunneled"] is True
    muon_payload = json.loads(_decode_payload(response["muon_packet"]["payload"]))
    assert muon_payload["payload"] == "sync"
    assert muon_payload["flavor"] == "muon"


def test_tunnelable_async_function_returns_multiple_packets() -> None:
    bridge = MTQBridge(tunnel_engine=TunnelEngine(random_source=lambda: 0.0), fiber=LocalFiber())
    state = _make_state()

    @tunnelable
    async def emit_many(count: int) -> list[QuantumPacket]:
        await asyncio.sleep(0)
        return [_make_packet(payload=f"async-{idx}", coherence=0.85) for idx in range(count)]

    response = asyncio.run(emit_many(2, mtq_bridge=bridge, quantum_state=state))
    assert response["tunneled"] is True
    assert len(response["results"]) == 2
    assert len(response["probabilities"]) == 2
    payloads = [json.loads(_decode_payload(entry["muon_packet"]["payload"])) for entry in response["results"]]
    assert all(data["payload"].startswith("async-") for data in payloads)


def test_tunnelable_requires_bridge_and_state() -> None:
    bridge = MTQBridge(tunnel_engine=TunnelEngine(random_source=lambda: 0.0), fiber=LocalFiber())
    state = _make_state()

    @tunnelable
    def emit_packet() -> QuantumPacket:
        return _make_packet(payload="sync")

    with pytest.raises(ValueError):
        emit_packet(quantum_state=state)

    with pytest.raises(ValueError):
        emit_packet(mtq_bridge=bridge)


def test_muon_to_quantum_handles_corrupted_values() -> None:
    bridge = MTQBridge()
    payload = json.dumps(
        {
            "generation": "invalid",
            "polarization": "nan",
            "coherence": "???",
            "energy_ev": "oops",
            "metadata": "payload-metadata",
        }
    ).encode("utf-8")
    signal = MuonSignal(
        frequencies=["bad", 3.2],
        leptonic_density="NaN",
        metadata={
            "flavor": "tau",
            "generation": "no-int",
            "polarization": float("inf"),
            "coherence": "NaN",
        },
    )
    packet = MuonPacket(payload=payload, signal=signal)

    quantum = bridge._muon_to_quantum(packet)
    assert quantum.leptonic_signature.flavor == "tau"
    assert quantum.leptonic_signature.generation == 0
    assert quantum.leptonic_signature.polarization == 0.0
    assert quantum.coherence == 0.0
    assert quantum.energy_ev == 0.0
    assert quantum.metadata.get("metadata") == "payload-metadata"
