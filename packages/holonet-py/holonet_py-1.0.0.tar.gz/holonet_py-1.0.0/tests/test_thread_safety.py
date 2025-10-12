"""Pruebas de seguridad frente a condiciones de carrera."""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from threading import Lock

import pytest

from holonet.core.nodes import HoloNode, NodeRegistry
from holonet.hardware.induction_driver import DeviceRegistry, InductionDevice
from holonet.simulation.engine import SimulationEngine
from holonet.core.packets import MuonSignal


def test_node_registry_is_thread_safe() -> None:
    registry = NodeRegistry()
    received: list[str] = []
    listener_lock = Lock()

    def listener(node: HoloNode) -> None:
        with listener_lock:
            received.append(node.identifier)

    registry.subscribe(listener)

    def register_node(index: int) -> None:
        registry.add(HoloNode(identifier=f"node-{index}", location="orbita"))

    with ThreadPoolExecutor(max_workers=8) as executor:
        list(executor.map(register_node, range(40)))

    identifiers = {node.identifier for node in registry.all()}
    assert len(identifiers) == 40
    assert identifiers == {f"node-{index}" for index in range(40)}
    assert set(received) == identifiers

    # Comprobar que la paginación opera sobre una instantánea coherente
    page = list(registry.paginate(offset=5, limit=10))
    assert len(page) == 10
    assert {node.identifier for node in page}.issubset(identifiers)


def test_device_registry_concurrent_registration() -> None:
    registry = DeviceRegistry()

    def register_device(index: int) -> None:
        device = InductionDevice(identifier=f"dev-{index}", calibration_factor=1.0 + index)
        registry.register(device)

    with ThreadPoolExecutor(max_workers=8) as executor:
        list(executor.map(register_device, range(25)))

    devices = registry.list_devices()
    assert len(devices) == 25
    for index in range(25):
        assert devices[f"dev-{index}"] == pytest.approx(1.0 + index)


def test_simulation_engine_emits_without_race_conditions() -> None:
    engine = SimulationEngine(max_pending_events=1024)
    node = HoloNode(identifier="alpha", location="orbita")
    signal = MuonSignal([1.0, 0.5, 0.2], 1.5)

    def emit_payload(index: int) -> None:
        payload = f"mensaje-{index}".encode("utf-8")
        result = engine.emit(node, payload, signal, recipients=[node.identifier])
        assert result.event is not None

    with ThreadPoolExecutor(max_workers=12) as executor:
        list(executor.map(emit_payload, range(120)))

    packets = engine.flush()
    assert len(packets) == 120
    # Tras flush, la métrica de cola debe reflejar el estado vacío
    assert engine.metrics["queue_size"] == 0
