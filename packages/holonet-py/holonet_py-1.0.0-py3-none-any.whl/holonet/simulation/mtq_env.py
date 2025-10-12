"""Entorno de simulación MTQ con dinámica de red cuántica."""
from __future__ import annotations

import random
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Dict, Iterable, List, Optional, Tuple

import numpy as np

from holonet.core.nodes import HoloNode
from holonet.mtq.quantum_packet import LeptonicSignature, QuantumPacket
from holonet.mtq.state_models import NodeQuantumState, ThermalNoiseModel


@dataclass
class MTQNode:
    """Representa un nodo holográfico con estado cuántico dinámico."""

    holo_node: HoloNode
    quantum_state: NodeQuantumState
    noise_model: ThermalNoiseModel = field(default_factory=ThermalNoiseModel)
    last_updated: datetime = field(default_factory=lambda: datetime.now(UTC))

    def update_state(self, rng: random.Random, elapsed_s: float) -> None:
        """Aplica fluctuaciones aleatorias a las variables termodinámicas."""

        temperature_drift = rng.gauss(0.0, 0.02 * max(1.0, self.quantum_state.temperature_k))
        entropy_drift = rng.gauss(0.0, 0.01)
        stability_drift = rng.gauss(0.0, 0.015)

        self.quantum_state.temperature_k = max(
            0.1, self.quantum_state.temperature_k + temperature_drift * elapsed_s
        )
        self.quantum_state.entanglement_entropy = min(
            1.0,
            max(0.0, self.quantum_state.entanglement_entropy + entropy_drift * elapsed_s),
        )
        self.quantum_state.stability_index = min(
            1.5,
            max(0.0, self.quantum_state.stability_index + stability_drift * elapsed_s),
        )
        self.last_updated = datetime.now(UTC)

    def noise_for(self, packet: QuantumPacket) -> float:
        """Calcula el ruido macroscópico aplicado al paquete."""

        return self.noise_model.noise_for(self.quantum_state, packet)


@dataclass
class MTQLink:
    """Conexión entre nodos MTQ con parámetros dinámicos."""

    source: str
    target: str
    base_fidelity: float
    max_bandwidth: int
    latency_ms: float
    _congestion: float = field(default=0.0, init=False)
    _instability: float = field(default=0.0, init=False)

    def update_dynamics(self, rng: random.Random, load_ratio: float) -> None:
        """Actualiza congestión e inestabilidad en función de la carga observada."""

        self._congestion = max(0.0, min(1.0, load_ratio))
        self._instability = max(0.0, rng.random() * 0.1 + self._congestion * 0.3)

    @property
    def congestion(self) -> float:
        return self._congestion

    @property
    def instability(self) -> float:
        return self._instability

    def fidelity(self) -> float:
        penalty = self._instability + 0.2 * self._congestion
        return max(0.0, min(1.0, self.base_fidelity - penalty))

    def latency(self) -> float:
        return self.latency_ms * (1.0 + self._congestion * 0.5)

    def decoherence_penalty(self) -> float:
        return self._instability + self._congestion * 0.4


@dataclass
class TrafficProfile:
    """Describe una fuente de tráfico cuántico para benchmarking."""

    name: str
    source: str
    target: str
    mean_rate: float
    energy_range_ev: Tuple[float, float]
    coherence_range: Tuple[float, float]
    leptonic_flavors: Iterable[str] = field(default_factory=lambda: ["muon", "tau"])
    generations: Iterable[int] = field(default_factory=lambda: [1, 2, 3])
    metadata: Dict[str, float | str] = field(default_factory=dict)


@dataclass
class TrafficRequest:
    """Representa un paquete cuántico generado para la simulación."""

    profile: str
    source: str
    target: str
    packet: QuantumPacket


class QuantumTrafficGenerator:
    """Genera tráfico cuántico heterogéneo basado en perfiles configurables."""

    def __init__(self, profiles: Iterable[TrafficProfile], *, seed: Optional[int] = None) -> None:
        self._profiles = list(profiles)
        if not self._profiles:
            raise ValueError("Se requiere al menos un perfil de tráfico")
        self._rng = np.random.default_rng(seed)

    def generate(self, *, step_seconds: float = 1.0) -> List[TrafficRequest]:
        requests: List[TrafficRequest] = []
        for profile in self._profiles:
            expected_packets = max(0.0, profile.mean_rate * step_seconds)
            count = int(self._rng.poisson(expected_packets))
            if count == 0:
                continue
            for _ in range(count):
                energy = float(self._rng.uniform(*profile.energy_range_ev))
                coherence = float(self._rng.uniform(*profile.coherence_range))
                polarization = float(self._rng.uniform(-1.0, 1.0))
                flavor = str(self._rng.choice(list(profile.leptonic_flavors)))
                generation = int(self._rng.choice(list(profile.generations)))
                signature = LeptonicSignature(flavor, generation, polarization)
                metadata = dict(profile.metadata)
                metadata.update({
                    "profile": profile.name,
                    "generated_at": datetime.now(UTC).isoformat(),
                })
                packet = QuantumPacket(signature, energy_ev=energy, coherence=coherence, metadata=metadata)
                requests.append(
                    TrafficRequest(
                        profile=profile.name,
                        source=profile.source,
                        target=profile.target,
                        packet=packet,
                    )
                )
        return requests


@dataclass
class MTQTeachingTrace:
    """Describe los cálculos realizados al evaluar un paquete MTQ."""

    profile: str
    source: str
    target: str
    steps: List[Dict[str, float | str]]
    summary: Dict[str, float | str]

    def as_dict(self) -> Dict[str, float | str]:
        return {
            "profile": self.profile,
            "source": self.source,
            "target": self.target,
            "steps": self.steps,
            "summary": self.summary,
        }


@dataclass
class MTQEvent:
    """Evento generado por el entorno MTQ tras propagar un paquete."""

    timestamp: datetime
    profile: str
    source: str
    target: str
    energy_ev: float
    initial_coherence: float
    final_coherence: float
    link_fidelity: float
    link_latency_ms: float
    applied_noise: float
    node_temperature_k: float
    entanglement_entropy: float
    stability_index: float
    congestion: float
    delivered: bool
    teaching_trace: Optional[MTQTeachingTrace] = None

    def as_dict(self) -> Dict[str, float | str | Dict[str, float | str]]:
        payload: Dict[str, float | str | Dict[str, float | str]] = {
            "timestamp": self.timestamp.isoformat(),
            "profile": self.profile,
            "source": self.source,
            "target": self.target,
            "energy_ev": self.energy_ev,
            "initial_coherence": self.initial_coherence,
            "final_coherence": self.final_coherence,
            "link_fidelity": self.link_fidelity,
            "link_latency_ms": self.link_latency_ms,
            "applied_noise": self.applied_noise,
            "node_temperature_k": self.node_temperature_k,
            "entanglement_entropy": self.entanglement_entropy,
            "stability_index": self.stability_index,
            "congestion": self.congestion,
            "delivered": int(self.delivered),
        }
        payload["teaching_trace"] = (
            self.teaching_trace.as_dict() if self.teaching_trace is not None else None
        )
        return payload


class MTQEnvironment:
    """Simulador de red cuántica-macroscópica con historial de eventos."""

    def __init__(
        self,
        *,
        random_seed: Optional[int] = None,
        history_size: int = 10_000,
    ) -> None:
        self._rng = random.Random(random_seed)
        self._nodes: Dict[str, MTQNode] = {}
        self._links: Dict[Tuple[str, str], MTQLink] = {}
        self._history: List[MTQEvent] = []
        self._history_size = history_size
        self._last_step: Optional[datetime] = None
        self._last_teaching_trace: List[MTQTeachingTrace] = []

    def register_node(
        self,
        node: HoloNode,
        quantum_state: NodeQuantumState,
        *,
        noise_model: Optional[ThermalNoiseModel] = None,
    ) -> None:
        if node.identifier in self._nodes:
            raise ValueError(f"El nodo {node.identifier} ya fue registrado")
        self._nodes[node.identifier] = MTQNode(
            holo_node=node,
            quantum_state=quantum_state,
            noise_model=noise_model or ThermalNoiseModel(),
        )

    def connect(
        self,
        source: str,
        target: str,
        *,
        base_fidelity: float,
        max_bandwidth: int,
        latency_ms: float,
    ) -> None:
        if source not in self._nodes or target not in self._nodes:
            raise ValueError("Ambos nodos deben estar registrados antes de conectar")
        self._links[(source, target)] = MTQLink(
            source=source,
            target=target,
            base_fidelity=base_fidelity,
            max_bandwidth=max(1, max_bandwidth),
            latency_ms=latency_ms,
        )

    def nodes(self) -> Dict[str, MTQNode]:
        return dict(self._nodes)

    def links(self) -> Dict[Tuple[str, str], MTQLink]:
        return dict(self._links)

    def reset_history(self) -> None:
        self._history.clear()

    def step(
        self,
        *,
        traffic: Optional[QuantumTrafficGenerator] = None,
        now: Optional[datetime] = None,
        step_seconds: float = 1.0,
        teaching: bool = False,
    ) -> List[MTQEvent]:
        if not self._nodes:
            return []
        now = now or datetime.now(UTC)
        if self._last_step is None:
            elapsed_s = step_seconds
        else:
            elapsed_s = max(step_seconds, (now - self._last_step).total_seconds())
        self._last_step = now

        self._last_teaching_trace = []

        for node in self._nodes.values():
            node.update_state(self._rng, elapsed_s)

        requests: List[TrafficRequest] = []
        if traffic is not None:
            requests = traffic.generate(step_seconds=elapsed_s)

        if not requests:
            return []

        link_counts: Dict[Tuple[str, str], int] = {}
        events: List[MTQEvent] = []

        for request in requests:
            link = self._links.get((request.source, request.target))
            if link is None:
                continue
            key = (link.source, link.target)
            link_counts[key] = link_counts.get(key, 0) + 1
            load_ratio = link_counts[key] / float(link.max_bandwidth)
            link.update_dynamics(self._rng, load_ratio)

            node = self._nodes[request.source]
            packet = request.packet
            initial_coherence = packet.coherence
            node_noise = node.noise_for(packet)
            link_penalty = link.decoherence_penalty()
            noise = node_noise + link_penalty
            final_coherence = packet.degrade(noise)
            stability_factor = node.quantum_state.stability_factor()
            delivered = final_coherence >= 0.2 * stability_factor

            teaching_trace: Optional[MTQTeachingTrace] = None
            if teaching:
                steps = [
                    {
                        "paso": "Coherencia inicial",
                        "valor": round(initial_coherence, 6),
                    },
                    {
                        "paso": "Ruido térmico nodo",
                        "valor": round(node_noise, 6),
                    },
                    {
                        "paso": "Penalización decoherencia enlace",
                        "valor": round(link_penalty, 6),
                    },
                    {
                        "paso": "Ruido total aplicado",
                        "valor": round(noise, 6),
                    },
                    {
                        "paso": "Coherencia final",
                        "valor": round(final_coherence, 6),
                    },
                    {
                        "paso": "Factor estabilidad nodo",
                        "valor": round(stability_factor, 6),
                    },
                ]
                summary = {
                    "criterio_entrega": ">= 20% de estabilidad",
                    "umbral": round(0.2 * stability_factor, 6),
                    "entregado": delivered,
                }
                teaching_trace = MTQTeachingTrace(
                    profile=request.profile,
                    source=request.source,
                    target=request.target,
                    steps=steps,
                    summary=summary,
                )
                self._last_teaching_trace.append(teaching_trace)

            event = MTQEvent(
                timestamp=now,
                profile=request.profile,
                source=request.source,
                target=request.target,
                energy_ev=packet.energy_ev,
                initial_coherence=initial_coherence,
                final_coherence=final_coherence,
                link_fidelity=link.fidelity(),
                link_latency_ms=link.latency(),
                applied_noise=noise,
                node_temperature_k=node.quantum_state.temperature_k,
                entanglement_entropy=node.quantum_state.entanglement_entropy,
                stability_index=node.quantum_state.stability_index,
                congestion=link.congestion,
                delivered=delivered,
                teaching_trace=teaching_trace,
            )
            events.append(event)
            self._history.append(event)

        if len(self._history) > self._history_size:
            self._history = self._history[-self._history_size :]

        return events

    @property
    def history(self) -> List[MTQEvent]:
        return list(self._history)

    def node_snapshot(self) -> Dict[str, Dict[str, float]]:
        snapshot: Dict[str, Dict[str, float]] = {}
        for node_id, node in self._nodes.items():
            snapshot[node_id] = {
                "temperature_k": node.quantum_state.temperature_k,
                "entanglement_entropy": node.quantum_state.entanglement_entropy,
                "stability_index": node.quantum_state.stability_index,
            }
        return snapshot

    def link_snapshot(self) -> List[Dict[str, float | str]]:
        data: List[Dict[str, float | str]] = []
        for link in self._links.values():
            data.append(
                {
                    "source": link.source,
                    "target": link.target,
                    "fidelity": link.fidelity(),
                    "latency_ms": link.latency(),
                    "congestion": link.congestion,
                    "instability": link.instability,
                }
            )
        return data

    def export_history_json(self, path: str) -> None:
        import json

        with open(path, "w", encoding="utf-8") as handle:
            json.dump([event.as_dict() for event in self._history], handle, ensure_ascii=False, indent=2)

    def export_history_csv(self, path: str) -> None:
        import csv

        with open(path, "w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=[
                    "timestamp",
                    "profile",
                    "source",
                    "target",
                    "energy_ev",
                    "initial_coherence",
                    "final_coherence",
                    "link_fidelity",
                    "link_latency_ms",
                    "applied_noise",
                    "node_temperature_k",
                    "entanglement_entropy",
                    "stability_index",
                    "congestion",
                    "delivered",
                    "teaching_trace",
                ],
            )
            writer.writeheader()
            for event in self._history:
                row = event.as_dict()
                if row["teaching_trace"] is not None:
                    import json

                    row["teaching_trace"] = json.dumps(row["teaching_trace"], ensure_ascii=False)
                writer.writerow(row)

    def summary_metrics(self) -> Dict[str, float]:
        if not self._history:
            return {
                "events": 0,
                "delivery_ratio": 0.0,
                "mean_fidelity": 0.0,
                "mean_latency_ms": 0.0,
            }
        delivery_ratio = sum(1 for event in self._history if event.delivered) / len(self._history)
        mean_fidelity = float(sum(event.link_fidelity for event in self._history) / len(self._history))
        mean_latency = float(sum(event.link_latency_ms for event in self._history) / len(self._history))
        return {
            "events": float(len(self._history)),
            "delivery_ratio": delivery_ratio,
            "mean_fidelity": mean_fidelity,
            "mean_latency_ms": mean_latency,
        }

    @property
    def last_teaching_trace(self) -> List[MTQTeachingTrace]:
        """Devuelve el último rastro detallado generado en modo educativo."""

        return list(self._last_teaching_trace)
