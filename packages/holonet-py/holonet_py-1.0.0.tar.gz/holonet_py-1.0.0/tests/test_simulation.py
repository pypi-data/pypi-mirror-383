"""Pruebas del motor de simulación muónica."""
import asyncio

import pytest

from holonet.core.nodes import HoloNode
from holonet.core.packets import LeptonicPattern
from holonet.decoding.signal_reader import SignalReader
from holonet.interface.websocket_bridge import WebSocketBridge
from holonet.security.leptonic_guard import LeptonicGuard
from holonet.simulation.engine import QueueSaturatedError, SimulationEngine


def test_simulation_emit_and_listen():
    engine = SimulationEngine()
    node = HoloNode("Sim", "Orbital")
    pattern = LeptonicPattern("simple", [1.0, 2.0, 3.0])
    signal = pattern.to_signal(0.5)

    events = []
    engine.register_listener(events.append)

    result = engine.emit(node, b"ping", signal)

    packet = engine.listen(node.identifier)
    assert packet is not None
    assert packet.payload == b"ping"
    assert events[0].node.identifier == "Sim"
    assert result.delivered


def test_signal_reader_metrics():
    engine = SimulationEngine()
    node = HoloNode("Sim", "Orbital")
    pattern = LeptonicPattern("simple", [0.1])
    signal = pattern.to_signal(1.0)

    engine.emit(node, b"a", signal)
    engine.emit(node, b"b", signal)

    reader = SignalReader()
    packets = engine.flush()
    payloads = reader.decode_payloads(packets)
    assert payloads == ["a", "b"]
    assert reader.average_density(packets) == 1.0


def test_async_queue_factory_respects_limit():
    engine = SimulationEngine(async_queue_maxsize=2)
    queue = engine.create_async_queue()
    assert queue.maxsize == 2


def test_async_queue_limit_discards_events():
    engine = SimulationEngine(async_queue_maxsize=1)
    queue = engine.create_async_queue()
    engine.register_listener(queue)

    node = HoloNode("Lim", "Orbital")
    pattern = LeptonicPattern("burst", [0.2])
    signal = pattern.to_signal(0.8)

    engine.emit(node, b"uno", signal)
    engine.emit(node, b"dos", signal)

    assert queue.qsize() == 1
    first_event = queue.get_nowait()
    assert first_event.packet.payload == b"uno"
    with pytest.raises(asyncio.QueueEmpty):
        queue.get_nowait()


def test_websocket_bridge_uses_provided_queue():
    engine = SimulationEngine()
    limited_queue: asyncio.Queue = asyncio.Queue(maxsize=1)
    guard = LeptonicGuard()
    guard.register_shared_secret("listener", "EscuchaSegura123!?")
    token = guard.issue_token("listener", "EscuchaSegura123!?")
    bridge = WebSocketBridge(engine, guard, queue=limited_queue)

    async def runner() -> None:
        stream = bridge.stream_packets("listener", token)
        task = asyncio.create_task(stream.__anext__())
        await asyncio.sleep(0)

        assert engine.async_queues[-1][0] is limited_queue

        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task

    asyncio.run(runner())


def test_engine_rejects_when_queue_saturated():
    engine = SimulationEngine(max_pending_events=1)
    node = HoloNode("Sat", "Orbital")
    pattern = LeptonicPattern("simple", [0.5])
    signal = pattern.to_signal(0.2)

    engine.emit(node, b"uno", signal)

    with pytest.raises(QueueSaturatedError):
        engine.emit(node, b"dos", signal)

    metrics = engine.metrics
    assert metrics["queue_size"] == 1
    assert metrics["rejected_events"] == 1

