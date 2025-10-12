"""Enrutamiento híbrido priorizando saltos MTQ."""
from __future__ import annotations

import heapq
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

from holonet.core.nodes import NodeRegistry
from holonet.mtq.optimizer import MTQOptimizer, TrainingSample
from holonet.mtq.quantum_packet import QuantumPacket

from .holo_node import MTQNetworkNode
from .topology import NetworkTopology


@dataclass
class EdgeMetrics:
    """Estadísticas básicas de rendimiento por enlace."""

    attempts: int = 0
    successes: int = 0
    avg_latency: float = 0.0
    latency_samples: int = 0
    avg_energy: float = 0.0

    def record(self, *, success: bool, energy: float, latency: Optional[float]) -> None:
        self.attempts += 1
        if success:
            self.successes += 1
        self.avg_energy += (energy - self.avg_energy) / self.attempts
        if latency is not None:
            self.latency_samples += 1
            self.avg_latency += (latency - self.avg_latency) / self.latency_samples

    def success_rate(self) -> float:
        if self.attempts == 0:
            return 0.0
        return self.successes / self.attempts


@dataclass
class QuantumRouter:
    """Selecciona rutas priorizando túneles MTQ con retroceso clásico."""

    topology: NetworkTopology
    nodes: Dict[str, MTQNetworkNode] = field(default_factory=dict)
    energy_ledger: Dict[Tuple[str, str], float] = field(default_factory=dict)
    optimizer: MTQOptimizer = field(default_factory=MTQOptimizer)
    routing_mode: str = "balanced"
    edge_metrics: Dict[Tuple[str, str], EdgeMetrics] = field(default_factory=dict)

    def register_node(self, node: MTQNetworkNode) -> None:
        """Registra un nodo MTQ dentro del enrutador."""

        self.nodes[node.identifier] = node
        self._refresh_topology_from_node(node)

    def _refresh_topology_from_node(self, node: MTQNetworkNode) -> None:
        neighbors = sorted(node.neighbors())
        if not neighbors:
            self.topology.links.pop(node.identifier, None)
            return
        self.topology.links[node.identifier] = neighbors

    def update_dynamic_links(
        self,
        identifier: str,
        *,
        tunnel_links: Optional[Dict[str, float]] = None,
        classical_links: Optional[Dict[str, float]] = None,
        role: Optional[str] = None,
    ) -> None:
        """Actualiza enlaces y rol de un nodo en caliente."""

        node = self.nodes[identifier]
        node.configure_tunnel_links(tunnel_links)
        node.configure_classical_links(classical_links)
        if role is not None:
            node.set_role(role)
        self._refresh_topology_from_node(node)

    def simulate_tick(self, metrics: Mapping[str, float]) -> None:
        """Ajusta roles y pesos energéticos según métricas dinámicas."""

        if not metrics:
            return
        values = list(metrics.values())
        max_value = max(values)
        min_value = min(values)
        span = max_value - min_value or 1.0

        for identifier, score in metrics.items():
            node = self.nodes.get(identifier)
            if node is None:
                continue
            normalized = (score - min_value) / span
            if normalized >= 0.66:
                node.set_role("coordinador")
            elif normalized >= 0.33:
                node.set_role("puente")
            else:
                node.set_role("periferico")

            for neighbor, cost in list(node.tunnel_links.items()):
                adjusted = max(0.05, cost * (1.0 - 0.4 * normalized))
                node.tunnel_links[neighbor] = adjusted
            for neighbor, cost in list(node.classical_links.items()):
                penalty = 1.0 + 0.2 * (1.0 - normalized)
                node.classical_links[neighbor] = cost * penalty
            self._refresh_topology_from_node(node)

    def set_routing_mode(self, mode: str) -> None:
        """Activa el modo de enrutamiento especificado."""

        normalized = mode.lower()
        if normalized not in {"balanced", "smart-routing"}:
            raise ValueError("Modo de enrutamiento desconocido")
        self.routing_mode = normalized

    def route(
        self,
        source: str,
        destination: str,
        *,
        packet: Optional[QuantumPacket] = None,
        mode: Optional[str] = None,
        latency_hint: Optional[Mapping[Tuple[str, str] | str, float]] = None,
    ) -> List[str]:
        """Calcula la ruta de menor coste priorizando túneles activos."""

        if source == destination:
            return [source]
        if source not in self.nodes or destination not in self.nodes:
            raise KeyError("Ambos nodos deben estar registrados en el enrutador")

        routing_mode = (mode or self.routing_mode).lower()
        if routing_mode == "smart-routing" and packet is not None and self.optimizer.has_samples():
            self.optimizer.optimal_parameters().apply(packet)

        frontier: List[Tuple[float, str]] = [(0.0, source)]
        distances: Dict[str, float] = {source: 0.0}
        previous: Dict[str, str] = {}
        visited: set[str] = set()

        while frontier:
            cost, current = heapq.heappop(frontier)
            if current in visited:
                continue
            visited.add(current)
            if current == destination:
                break
            node = self.nodes.get(current)
            if node is None:
                continue
            neighbors = set(node.neighbors()) | set(self.topology.links.get(current, []))
            for neighbor in neighbors:
                if neighbor not in self.nodes:
                    continue
                edge_cost, _ = node.link_choice(neighbor, packet=packet)
                if edge_cost == float("inf"):
                    continue
                incremental_cost = edge_cost
                if routing_mode == "smart-routing":
                    features = self._features_for(node, neighbor, packet, edge_cost, latency_hint)
                    probability = self.optimizer.predict_success(features)
                    latency_penalty = self._latency_estimate(node.identifier, neighbor, latency_hint)
                    probability = max(probability, 0.1)
                    incremental_cost = edge_cost / probability + latency_penalty
                new_cost = cost + incremental_cost
                if new_cost < distances.get(neighbor, float("inf")):
                    distances[neighbor] = new_cost
                    previous[neighbor] = current
                    heapq.heappush(frontier, (new_cost, neighbor))

        if destination not in distances:
            raise RuntimeError(f"No existe ruta entre {source} y {destination}")

        return self._build_path(
            source,
            destination,
            previous,
            packet,
            routing_mode=routing_mode,
            latency_hint=latency_hint,
        )

    def _build_path(
        self,
        source: str,
        destination: str,
        previous: Dict[str, str],
        packet: Optional[QuantumPacket],
        *,
        routing_mode: str,
        latency_hint: Optional[Mapping[Tuple[str, str] | str, float]],
    ) -> List[str]:
        path: List[str] = [destination]
        current = destination
        while current != source:
            if current not in previous:
                raise RuntimeError(f"Ruta incompleta entre {source} y {destination}")
            current = previous[current]
            path.append(current)
        path.reverse()
        self._record_energy_usage(path, packet, latency_hint=latency_hint, routing_mode=routing_mode)
        return path

    def _record_energy_usage(
        self,
        path: Iterable[str],
        packet: Optional[QuantumPacket],
        *,
        latency_hint: Optional[Mapping[Tuple[str, str] | str, float]],
        routing_mode: str,
    ) -> None:
        nodes = list(path)
        for index in range(len(nodes) - 1):
            source = nodes[index]
            target = nodes[index + 1]
            node = self.nodes.get(source)
            if node is None:
                continue
            cost, tunneled = node.link_choice(target, packet=packet)
            if cost == float("inf"):
                cost = 1.0
            if not tunneled and node.tunnel_operational and target in node.tunnel_links:
                # Si no se logró el túnel se asume retroceso clásico.
                cost = node.classical_links.get(target, cost)
            node.register_energy_usage(cost)
            self.energy_ledger[(source, target)] = cost
            latency = self._resolve_latency_hint(latency_hint, source, target)
            self._update_learning(
                source,
                target,
                node,
                packet,
                energy=cost,
                tunneled=tunneled,
                latency=latency,
                routing_mode=routing_mode,
            )

    def _update_learning(
        self,
        source: str,
        target: str,
        node: MTQNetworkNode | None,
        packet: Optional[QuantumPacket],
        *,
        energy: float,
        tunneled: bool,
        latency: Optional[float],
        routing_mode: str,
    ) -> None:
        metrics = self.edge_metrics.setdefault((source, target), EdgeMetrics())
        metrics.record(success=tunneled, energy=energy, latency=latency)
        if packet is None:
            coherence = 0.5
        else:
            coherence = packet.coherence
        noise = 1.0
        if node and node.mtq_state is not None:
            noise = 1.0 - node.mtq_state.stability_factor()
        latency_value = latency
        if latency_value is None:
            if metrics.latency_samples:
                latency_value = metrics.avg_latency
            else:
                latency_value = 1.0
        sample = TrainingSample(
            energy_ev=energy,
            coherence=coherence,
            latency=latency_value,
            success=tunneled,
            noise=noise,
        )
        self.optimizer.add_sample(sample)
        if routing_mode == "smart-routing" and packet is not None:
            # Ajuste incremental sobre la marcha.
            self.optimizer.optimal_parameters()

    def handle_mtq_failure(self, identifier: str, *, penalty: float = 1.5) -> None:
        """Gestiona fallos MTQ forzando retrocesos clásicos."""

        node = self.nodes[identifier]
        node.mark_mtq_failure()
        for neighbor, tunnel_cost in list(node.tunnel_links.items()):
            fallback_base = node.classical_links.get(neighbor, tunnel_cost)
            node.classical_links[neighbor] = fallback_base * penalty
        node.tunnel_links.clear()
        self._refresh_topology_from_node(node)

        for neighbor_id, neighbor_node in self.nodes.items():
            if neighbor_id == identifier:
                continue
            if identifier in neighbor_node.tunnel_links:
                tunnel_cost = neighbor_node.tunnel_links.pop(identifier)
                fallback_base = neighbor_node.classical_links.get(identifier, tunnel_cost)
                neighbor_node.classical_links[identifier] = fallback_base * penalty
                self._refresh_topology_from_node(neighbor_node)

        for edge, value in list(self.energy_ledger.items()):
            if identifier in edge:
                self.energy_ledger[edge] = value * penalty

    def last_energy_cost(self, source: str, target: str) -> Optional[float]:
        """Devuelve el último coste energético registrado para un salto."""

        return self.energy_ledger.get((source, target))

    def roles_snapshot(self) -> Dict[str, str]:
        """Exposición rápida de los roles asignados actualmente."""

        return {identifier: node.role for identifier, node in self.nodes.items()}

    def _features_for(
        self,
        node: MTQNetworkNode,
        neighbor: str,
        packet: Optional[QuantumPacket],
        energy: float,
        latency_hint: Optional[Mapping[Tuple[str, str] | str, float]],
    ) -> Sequence[float]:
        coherence = packet.coherence if packet is not None else 0.5
        noise = 1.0
        if node.mtq_state is not None:
            noise = 1.0 - node.mtq_state.stability_factor()
        latency = self._latency_estimate(node.identifier, neighbor, latency_hint)
        return [energy, coherence, latency, noise]

    def _resolve_latency_hint(
        self,
        latency_hint: Optional[Mapping[Tuple[str, str] | str, float]],
        source: str,
        target: str,
    ) -> Optional[float]:
        if latency_hint is None:
            return None
        tuple_key = (source, target)
        if tuple_key in latency_hint:
            return latency_hint[tuple_key]
        string_key = f"{source}->{target}"
        if string_key in latency_hint:
            return latency_hint[string_key]
        return None

    def _latency_estimate(
        self,
        source: str,
        target: str,
        latency_hint: Optional[Mapping[Tuple[str, str] | str, float]],
    ) -> float:
        hint = self._resolve_latency_hint(latency_hint, source, target)
        if hint is not None:
            return hint
        metrics = self.edge_metrics.get((source, target))
        if metrics and metrics.latency_samples:
            return metrics.avg_latency
        reverse = self.edge_metrics.get((target, source))
        if reverse and reverse.latency_samples:
            return reverse.avg_latency
        return 1.0


def bootstrap_router(registry: NodeRegistry) -> QuantumRouter:
    """Utilidad para instanciar un enrutador con topología básica."""

    topology = NetworkTopology(registry)
    return QuantumRouter(topology)
