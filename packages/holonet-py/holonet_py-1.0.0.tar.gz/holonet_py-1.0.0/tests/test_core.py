"""Pruebas de las abstracciones núcleo."""
from holonet.core.nodes import HoloNode, NodeRegistry
import base64
import os

import pytest

from holonet.core.packets import LeptonicPattern, MuonPacket, MuonSignal
from holonet.network.decorators import muon_broadcast, muon_receive


def test_muon_signal_intensity():
    signal = MuonSignal([1.0, 2.0, 3.0], 0.5)
    assert signal.intensity() == 3.0


def test_muon_packet_serialization():
    signal = MuonSignal([1.0], 1.0, {"meta": True})
    packet = MuonPacket(b"hola", signal)
    data = packet.as_dict()
    payload = data["payload"]
    assert payload["encoding"] == "base64"
    assert base64.b64decode(payload["data"]) == b"hola"
    assert data["signal"]["leptonic_density"] == 1.0


@pytest.mark.parametrize("size", [0, 1, 32, 257])
def test_muon_packet_serialization_roundtrip_binary(size: int) -> None:
    raw = os.urandom(size)
    packet = MuonPacket(raw, MuonSignal([0.1], 0.5))
    payload = packet.as_dict()["payload"]
    assert payload["encoding"] == "base64"
    assert payload["length"] == size
    assert base64.b64decode(payload["data"]) == raw
    if size:
        assert payload["sha256"]
    else:
        assert "sha256" not in payload


def test_leptonic_pattern_to_signal():
    pattern = LeptonicPattern("test", [0.1, 0.2])
    signal = pattern.to_signal(2.0)
    assert signal.metadata["pattern"] == "test"


def test_node_registry_and_processing():
    registry = NodeRegistry()
    node = HoloNode("A", "Lunar", ["procesamiento"])
    registry.add(node)
    retrieved = registry.get("A")
    assert retrieved is node
    packet = MuonPacket(b"datos", MuonSignal([1.0], 1.0))
    assert "procesó" in node.process(packet)


def test_node_registry_subscribe_idempotent():
    registry = NodeRegistry()
    node = HoloNode("B", "Orbital")
    events = []

    def listener(registered_node: HoloNode) -> None:
        events.append(registered_node.identifier)

    registry.subscribe(listener)
    registry.subscribe(listener)

    registry.add(node)

    assert events == ["B"]


def test_muon_decorators_wrap_return_values():
    @muon_broadcast
    def emitir():
        return "ok"

    @muon_receive
    def recibir():
        return "ok"

    assert emitir()["mode"] == "broadcast"
    assert recibir()["mode"] == "receive"

