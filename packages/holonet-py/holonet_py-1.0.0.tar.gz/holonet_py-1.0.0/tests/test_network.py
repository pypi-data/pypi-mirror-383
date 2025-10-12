"""Pruebas del módulo de red."""
import pytest

from holonet.core.nodes import HoloNode, NodeRegistry
from holonet.network import MTQNetworkNode, QuantumRouter
from holonet.network.chord_client import ChordClient, ChordNodeInfo
from holonet.network.topology import NetworkTopology
from holonet.mtq.quantum_packet import LeptonicSignature, QuantumPacket
from holonet.mtq.state_models import NodeQuantumState


def test_network_topology_neighbors():
    registry = NodeRegistry()
    node_a = HoloNode("A", "Base")
    node_b = HoloNode("B", "Orbital")
    registry.add(node_a)
    registry.add(node_b)

    topology = NetworkTopology(registry)
    topology.connect("A", "B")

    neighbors = topology.neighbors("A")
    assert neighbors == [node_b]
    assert topology.summary() == [("A", ["B"])]


@pytest.mark.parametrize("suffix", [".json", ".yaml"])
def test_network_topology_persistence(tmp_path, suffix):
    registry = NodeRegistry()
    node_a = HoloNode("A", "Base")
    node_b = HoloNode("B", "Orbital")
    registry.add(node_a)
    registry.add(node_b)

    topology = NetworkTopology(registry)
    topology.connect("A", "B")

    file_path = tmp_path / f"topology{suffix}"
    topology.save_to_file(file_path)

    new_registry = NodeRegistry()
    new_registry.add(node_a)
    new_registry.add(node_b)

    loaded = NetworkTopology.load_from_file(new_registry, file_path)
    assert loaded.summary() == [("A", ["B"])]
    assert loaded.neighbors("A") == [node_b]


def test_chord_client_latency_metrics():
    client = ChordClient(window_size=3, histogram_bin_ms=5.0)
    client.register_node(ChordNodeInfo("node-1", "orbital:9000", 10.0))

    client.update_latency("node-1", 15.0)
    client.update_latency("node-1", 20.0)

    metrics = client.aggregated_latency("node-1")
    assert metrics["last"] == 20.0
    assert metrics["average"] == pytest.approx((10.0 + 15.0 + 20.0) / 3)
    assert metrics["std_deviation"] > 0
    assert client.list_nodes()["node-1"] == pytest.approx(metrics["average"])
    histogram = metrics["histogram"]
    assert histogram["10-15ms"] == 1
    assert histogram["15-20ms"] == 1
    assert histogram["20-25ms"] == 1


def test_chord_client_rejects_negative_latency():
    client = ChordClient()
    client.register_node(ChordNodeInfo("node-2", "orbital:9100", 5.0))

    with pytest.raises(ValueError):
        client.update_latency("node-2", -1.0)


def _sample_packet(coherence: float = 0.9) -> QuantumPacket:
    signature = LeptonicSignature("muon", 2, 0.1)
    return QuantumPacket(signature, energy_ev=1_000.0, coherence=coherence)


def _sample_state() -> NodeQuantumState:
    return NodeQuantumState(temperature_k=4.2, entanglement_entropy=0.05, stability_index=0.85)


def test_mtq_network_node_link_selection():
    base_node = HoloNode("A", "Base")
    network_node = MTQNetworkNode(base=base_node, mtq_state=_sample_state())
    network_node.configure_tunnel_links({"B": 0.4})
    network_node.configure_classical_links({"B": 2.0})

    cost, tunneled = network_node.link_choice("B", packet=_sample_packet())
    assert tunneled is True
    assert cost == pytest.approx(0.4)

    network_node.mark_mtq_failure()
    cost, tunneled = network_node.link_choice("B", packet=_sample_packet())
    assert tunneled is False
    assert cost == pytest.approx(2.0)


def test_quantum_router_prefers_tunnel_and_records_energy():
    registry = NodeRegistry()
    base_a = HoloNode("A", "Base")
    base_b = HoloNode("B", "Orbital")
    registry.add(base_a)
    registry.add(base_b)

    topology = NetworkTopology(registry)
    router = QuantumRouter(topology)

    node_a = MTQNetworkNode(base=base_a, mtq_state=_sample_state())
    node_b = MTQNetworkNode(base=base_b, mtq_state=_sample_state())
    node_a.configure_tunnel_links({"B": 0.5})
    node_a.configure_classical_links({"B": 3.0})
    node_b.configure_tunnel_links({"A": 0.5})
    node_b.configure_classical_links({"A": 3.0})

    router.register_node(node_a)
    router.register_node(node_b)

    packet = _sample_packet()
    path = router.route("A", "B", packet=packet)
    assert path == ["A", "B"]
    assert router.last_energy_cost("A", "B") == pytest.approx(0.5)
    assert node_a.energy_budget == pytest.approx(0.5)


def test_quantum_router_dynamic_roles_and_failure():
    registry = NodeRegistry()
    base_a = HoloNode("A", "Base")
    base_b = HoloNode("B", "Orbital")
    base_c = HoloNode("C", "Orbital")
    for node in (base_a, base_b, base_c):
        registry.add(node)

    router = QuantumRouter(NetworkTopology(registry))

    node_a = MTQNetworkNode(base=base_a, mtq_state=_sample_state())
    node_b = MTQNetworkNode(base=base_b, mtq_state=_sample_state())
    node_c = MTQNetworkNode(base=base_c, mtq_state=_sample_state())

    node_a.configure_tunnel_links({"B": 0.4})
    node_a.configure_classical_links({"B": 2.0, "C": 8.0})
    node_b.configure_tunnel_links({"A": 0.4, "C": 0.5})
    node_b.configure_classical_links({"A": 2.0, "C": 2.5})
    node_c.configure_tunnel_links({"B": 0.5})
    node_c.configure_classical_links({"A": 8.0, "B": 2.5})

    for node in (node_a, node_b, node_c):
        router.register_node(node)

    router.simulate_tick({"A": 0.9, "B": 0.6, "C": 0.1})
    roles = router.roles_snapshot()
    assert roles["A"] == "coordinador"
    assert roles["B"] == "puente"
    assert roles["C"] == "periferico"
    assert node_a.tunnel_links["B"] < 0.4  # reducción energética por buen desempeño

    pre_failure_b_a = node_b.classical_links["A"]
    pre_failure_b_c = node_b.classical_links["C"]
    router.handle_mtq_failure("B")
    assert node_b.tunnel_links == {}
    assert node_b.classical_links["A"] == pytest.approx(pre_failure_b_a * 1.5)
    assert node_b.classical_links["C"] == pytest.approx(pre_failure_b_c * 1.5)

    packet = _sample_packet()
    path = router.route("A", "C", packet=packet)
    assert path == ["A", "B", "C"]
    assert router.last_energy_cost("A", "B") == pytest.approx(node_a.classical_links["B"])
    assert router.last_energy_cost("B", "C") == pytest.approx(node_b.classical_links["C"])

