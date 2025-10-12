"""Cliente simulado para Chord OS con métricas de latencia agregadas."""
from __future__ import annotations

from collections import Counter, deque
from dataclasses import dataclass, field
from typing import Deque, Dict, Iterable, Mapping


@dataclass
class ChordNodeInfo:
    identifier: str
    address: str
    latency_ms: float


@dataclass
class LatencyWindow:
    """Mantiene estadísticas móviles para la latencia de un nodo."""

    window_size: int = 20
    histogram_bin_ms: float = 5.0
    samples: Deque[float] = field(default_factory=deque)

    def update(self, latency_ms: float) -> None:
        if latency_ms < 0:
            raise ValueError("La latencia no puede ser negativa")
        if len(self.samples) == self.window_size:
            self.samples.popleft()
        self.samples.append(latency_ms)

    def average(self) -> float:
        if not self.samples:
            return 0.0
        return sum(self.samples) / len(self.samples)

    def std_deviation(self) -> float:
        if not self.samples:
            return 0.0
        mean = self.average()
        variance = sum((sample - mean) ** 2 for sample in self.samples) / len(self.samples)
        return variance**0.5

    def last(self) -> float | None:
        if not self.samples:
            return None
        return self.samples[-1]

    def histogram(self) -> Mapping[str, int]:
        counter: Counter[str] = Counter()
        for sample in self.samples:
            bucket_start = (sample // self.histogram_bin_ms) * self.histogram_bin_ms
            bucket_end = bucket_start + self.histogram_bin_ms
            label = f"{bucket_start:.0f}-{bucket_end:.0f}ms"
            counter[label] += 1
        return dict(counter)


class ChordClient:
    """Cliente que almacena nodos remotos y métricas agregadas de latencia."""

    def __init__(self, *, window_size: int = 20, histogram_bin_ms: float = 5.0) -> None:
        self._nodes: Dict[str, ChordNodeInfo] = {}
        self._latency_windows: Dict[str, LatencyWindow] = {}
        self._window_size = window_size
        self._histogram_bin_ms = histogram_bin_ms

    def register_node(self, info: ChordNodeInfo) -> None:
        self._nodes[info.identifier] = info
        self._latency_windows.setdefault(
            info.identifier,
            LatencyWindow(window_size=self._window_size, histogram_bin_ms=self._histogram_bin_ms),
        )
        window = self._latency_windows[info.identifier]
        window.update(max(info.latency_ms, 0.0))
        info.latency_ms = window.average()

    def list_nodes(self) -> Dict[str, float]:
        return {identifier: info.latency_ms for identifier, info in self._nodes.items()}

    def update_latency(self, identifier: str, latency_ms: float) -> None:
        """Actualiza la latencia de un nodo y recalcula sus métricas móviles."""

        if identifier not in self._nodes:
            raise KeyError(f"Nodo {identifier} no registrado")
        window = self._latency_windows.setdefault(
            identifier,
            LatencyWindow(window_size=self._window_size, histogram_bin_ms=self._histogram_bin_ms),
        )
        window.update(latency_ms)
        self._nodes[identifier].latency_ms = window.average()

    def aggregated_latency(self, identifier: str) -> Dict[str, float | Mapping[str, int] | None]:
        """Devuelve métricas agregadas de latencia para un nodo."""

        window = self._latency_windows.get(identifier)
        if window is None:
            return {"average": 0.0, "std_deviation": 0.0, "last": None, "histogram": {}}
        return {
            "average": window.average(),
            "std_deviation": window.std_deviation(),
            "last": window.last(),
            "histogram": window.histogram(),
        }

    def aggregated_latencies(self) -> Dict[str, Dict[str, float | Mapping[str, int] | None]]:
        """Expone las métricas agregadas de todos los nodos registrados."""

        return {identifier: self.aggregated_latency(identifier) for identifier in self._nodes}

    def bulk_update(self, latencies: Mapping[str, float]) -> None:
        """Permite actualizar múltiples latencias de una sola vez."""

        for identifier, value in latencies.items():
            self.update_latency(identifier, value)

    def load_initial_latencies(self, data: Iterable[ChordNodeInfo]) -> None:
        """Carga un conjunto de nodos iniciales y sus latencias asociadas."""

        for info in data:
            self.register_node(info)

