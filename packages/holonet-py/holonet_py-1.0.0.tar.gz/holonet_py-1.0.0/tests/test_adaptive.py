"""Pruebas de componentes adaptativos."""
from holonet.core.nodes import HoloNode
from holonet.core.packets import LeptonicPattern, MuonPacket
from holonet.hardware.induction_driver import DeviceRegistry, InductionDevice
from holonet.network.adaptive_topology import AdaptiveTopology
from holonet.network.metrics import AdaptiveMetricCollector, CompositeMetric
from holonet.simulation.adaptive_controller import AdaptiveController


def test_adaptive_controller_updates_history():
    controller = AdaptiveController()
    pattern = LeptonicPattern("p", [1.0])
    signal = pattern.to_signal(2.0)
    packet = MuonPacket(b"data", signal)
    avg = controller.update(packet)
    assert avg == 2.0


def test_adaptive_metric_collector_combines_metrics():
    controller = AdaptiveController()
    registry = DeviceRegistry()
    registry.register(InductionDevice("A", calibration_factor=2.0))
    collector = AdaptiveMetricCollector(controller, registry)
    pattern = LeptonicPattern("p", [1.0])
    signal = pattern.to_signal(2.0)
    packet = MuonPacket(b"data", signal)
    metric = collector.collect(packet, device_id="A")
    assert metric.controller_metric == 2.0
    assert metric.device_factor == 2.0
    assert metric.normalized == 0.8


def test_adaptive_topology_preferred_nodes():
    controller = AdaptiveController()
    topology = AdaptiveTopology(controller)
    node_a = HoloNode("A", "Base")
    node_b = HoloNode("B", "Orbital")
    metric_a = CompositeMetric(1.0, 1.0, 0.5)
    metric_b = CompositeMetric(2.0, 2.0, 0.8)
    topology.adjust(node_a, metric_a)
    topology.adjust(node_b, metric_b)
    assert topology.preferred_nodes() == ["B", "A"]


def test_adaptive_topology_accepts_scalar_metric():
    controller = AdaptiveController()
    topology = AdaptiveTopology(controller)
    node = HoloNode("Scalar", "Orbital")
    topology.adjust(node, 0.3)
    assert topology.preferred_nodes() == ["Scalar"]

