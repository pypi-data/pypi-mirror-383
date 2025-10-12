from pathlib import Path

from holonet.core.nodes import HoloNode
from holonet.mtq.quantum_packet import LeptonicSignature, QuantumPacket
from holonet.mtq.state_models import NodeQuantumState
from holonet.simulation.mtq_env import (
    MTQEnvironment,
    MTQTeachingTrace,
    TrafficRequest,
)


class StaticGenerator:
    def __init__(self, requests):
        self._requests = list(requests)

    def generate(self, *, step_seconds: float = 1.0):
        return list(self._requests)


def _build_environment() -> MTQEnvironment:
    env = MTQEnvironment(random_seed=42)
    env.register_node(
        HoloNode("n1", "Nodo 1", ["procesamiento"]),
        NodeQuantumState(temperature_k=4.5, entanglement_entropy=0.2, stability_index=1.1),
    )
    env.register_node(
        HoloNode("n2", "Nodo 2", ["receptor"]),
        NodeQuantumState(temperature_k=3.8, entanglement_entropy=0.25, stability_index=0.95),
    )
    env.connect("n1", "n2", base_fidelity=0.92, max_bandwidth=8, latency_ms=2.6)
    return env


def test_teaching_trace_is_attached(tmp_path: Path) -> None:
    env = _build_environment()
    packet = QuantumPacket(LeptonicSignature("muon", 1, 0.3), energy_ev=3.2, coherence=0.88)
    generator = StaticGenerator(
        [
            TrafficRequest(
                profile="manual",
                source="n1",
                target="n2",
                packet=packet,
            )
        ]
    )

    events = env.step(traffic=generator, teaching=True)
    assert len(events) == 1

    event = events[0]
    assert isinstance(event.teaching_trace, MTQTeachingTrace)
    assert len(event.teaching_trace.steps) == 6
    assert event.teaching_trace.summary["entregado"] in {True, False}

    last_trace = env.last_teaching_trace
    assert len(last_trace) == 1
    assert last_trace[0] == event.teaching_trace

    serialized = event.as_dict()
    assert "teaching_trace" in serialized
    assert isinstance(serialized["teaching_trace"], dict)

    csv_path = tmp_path / "history.csv"
    env.export_history_csv(csv_path.as_posix())
    assert csv_path.exists()
    content = csv_path.read_text(encoding="utf-8")
    assert "teaching_trace" in content
