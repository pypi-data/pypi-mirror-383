"""Pruebas para tramas ópticas y empaquetado MTQ."""
from __future__ import annotations

import pytest

import pytest

from holonet.mtq import LeptonicSignature, NodeQuantumState, QuantumPacket, TunnelEngine
from holonet.transmission import LocalFiber, MTQBridge, OpticalFiber, OpticalFrame


def _make_packet() -> QuantumPacket:
    signature = LeptonicSignature(flavor="muon", generation=2, polarization=0.33)
    metadata = {"payload": "fibra", "channel": "beta"}
    return QuantumPacket(leptonic_signature=signature, energy_ev=2.3, coherence=0.92, metadata=metadata)


def _make_state() -> NodeQuantumState:
    return NodeQuantumState(temperature_k=245.0, entanglement_entropy=0.2, stability_index=0.97)


def test_optical_frame_roundtrip_from_muon_packet() -> None:
    bridge = MTQBridge(tunnel_engine=TunnelEngine(random_source=lambda: 0.0), fiber=LocalFiber())
    state = _make_state()
    packet = _make_packet()

    result = bridge.transmit(packet, state)
    assert result.muon_packet is not None

    frame = OpticalFrame.from_muon_packet(result.muon_packet, wavelength_nm=1550.12)
    frame.encapsulate_tcp_ip("10.0.0.1", "10.0.0.2", 4000, 5000)

    serialized = frame.to_bytes()
    reconstructed = OpticalFrame.from_bytes(serialized)
    muon_roundtrip = reconstructed.to_muon_packet()

    assert reconstructed.ip_encapsulation["ip"]["src"] == "10.0.0.1"
    assert muon_roundtrip.payload == result.muon_packet.payload
    assert muon_roundtrip.signal.metadata == result.muon_packet.signal.metadata


def test_mtq_bridge_to_optical_frame_and_back() -> None:
    optical_fiber = OpticalFiber()
    bridge = MTQBridge(
        tunnel_engine=TunnelEngine(random_source=lambda: 0.0),
        fiber=LocalFiber(),
        optical_fiber=optical_fiber,
    )
    state = _make_state()
    packet = _make_packet()

    result = bridge.transmit(packet, state, wavelength_nm=1310.0)
    assert result.muon_packet is not None
    assert len(optical_fiber) == 1

    muon_packet = result.muon_packet
    frame = bridge.to_optical_frame(
        muon_packet,
        wavelength_nm=1310.0,
        src_ip="192.0.2.10",
        dst_ip="192.0.2.20",
        src_port=6000,
        dst_port=7000,
    )
    assert frame.ip_encapsulation["tcp"]["dst_port"] == 7000

    quantum_roundtrip = bridge.from_optical_frame(frame)
    assert quantum_roundtrip.metadata["payload"] == packet.metadata["payload"]
    assert quantum_roundtrip.coherence == pytest.approx(packet.coherence + 0.1)


def test_bridge_receive_optical_from_channel() -> None:
    optical_fiber = OpticalFiber()
    bridge = MTQBridge(
        tunnel_engine=TunnelEngine(random_source=lambda: 0.0),
        fiber=LocalFiber(),
        optical_fiber=optical_fiber,
    )
    state = _make_state()
    packet = _make_packet()

    bridge.transmit(packet, state, wavelength_nm=1550.0)
    frame = optical_fiber.receive()
    assert frame is not None

    # reenviar la trama por el canal para probar receive_optical
    optical_fiber.send(frame)
    quantum = bridge.receive_optical()
    assert quantum is not None
    assert quantum.metadata["payload"] == packet.metadata["payload"]


def test_optical_frame_from_bytes_validates_lengths() -> None:
    payload = b"abc"
    frame = OpticalFrame(payload=payload, wavelength_nm=1550.0)
    serialized = frame.to_bytes()

    # recorta un byte del payload declarado
    corrupted = serialized[:-1]
    with pytest.raises(ValueError):
        OpticalFrame.from_bytes(corrupted)

    # longitud de payload inconsistente
    header_len = int.from_bytes(serialized[:2], "big")
    bad_length = (len(payload) + 10).to_bytes(4, "big")
    tampered = serialized[: 2 + header_len] + bad_length + payload
    with pytest.raises(ValueError):
        OpticalFrame.from_bytes(tampered)


def test_optical_frame_to_muon_packet_handles_invalid_metadata() -> None:
    frame = OpticalFrame(
        payload=b"test",
        wavelength_nm=1310.0,
        metadata={
            "signal": {
                "frequencies": ["not-a-number", 200.5],
                "leptonic_density": "NaN",
                "metadata": "no-es-dict",
            },
            "created_at": "fecha-invalida",
        },
    )

    packet = frame.to_muon_packet()
    assert packet.signal.frequencies == [0.0, 200.5]
    assert packet.signal.leptonic_density == 0.0
    assert packet.signal.metadata == {}
