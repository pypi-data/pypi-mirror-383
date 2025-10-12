"""Herramientas para comparar MTQ con protocolos TCP/UDP clásicos."""
from __future__ import annotations

from dataclasses import dataclass
from statistics import fmean
from typing import Iterable, List, Sequence

import numpy as np

from holonet.core.nodes import HoloNode
from holonet.mtq.state_models import NodeQuantumState
from holonet.simulation.mtq_env import (
    MTQEnvironment,
    MTQEvent,
    QuantumTrafficGenerator,
    TrafficProfile,
)


@dataclass(frozen=True)
class BenchmarkMetrics:
    """Representa métricas agregadas para un protocolo determinado."""

    protocol: str
    variant: str
    latency_ms: float
    throughput_mbps: float
    failure_rate: float
    logical_energy_ev: float
    security_index: float

    def as_dict(self) -> dict[str, float | str]:
        """Convierte la estructura en un diccionario serializable."""

        return {
            "protocol": self.protocol,
            "variant": self.variant,
            "latency_ms": round(self.latency_ms, 6),
            "throughput_mbps": round(self.throughput_mbps, 6),
            "failure_rate": round(self.failure_rate, 6),
            "logical_energy_ev": round(self.logical_energy_ev, 6),
            "security_index": round(self.security_index, 6),
        }


@dataclass(frozen=True)
class BenchmarkConfig:
    """Configura los parámetros base para ejecutar la comparación."""

    steps: int = 24
    step_seconds: float = 1.0
    payload_bytes: int = 1024
    random_seed: int = 424242


class ProtocolComparator:
    """Ejecuta la comparación entre Holonet-MTQ y TCP/UDP."""

    def __init__(self, config: BenchmarkConfig | None = None) -> None:
        self._config = config or BenchmarkConfig()
        self._rng = np.random.default_rng(self._config.random_seed)

    def run(self) -> List[BenchmarkMetrics]:
        """Devuelve métricas para MTQ, TCP y UDP bajo la misma carga."""

        mtq_metrics = self._run_mtq_protocol()
        tcp_metrics = self._simulate_classical_protocol("TCP/IP", base_latency=2.3, jitter=0.35)
        udp_metrics = self._simulate_classical_protocol("UDP/IP", base_latency=1.7, jitter=0.45)
        return [mtq_metrics, tcp_metrics, udp_metrics]

    # ------------------------------------------------------------------
    # MTQ benchmarking
    # ------------------------------------------------------------------
    def _run_mtq_protocol(self) -> BenchmarkMetrics:
        config = self._config
        env = MTQEnvironment(random_seed=config.random_seed)
        self._configure_default_topology(env)

        traffic = QuantumTrafficGenerator(
            [
                TrafficProfile(
                    name="orbital",
                    source="orbital-alpha",
                    target="orbital-beta",
                    mean_rate=6.5,
                    energy_range_ev=(2.5, 5.0),
                    coherence_range=(0.65, 0.95),
                    metadata={"tier": "orbital"},
                ),
                TrafficProfile(
                    name="superficie",
                    source="orbital-beta",
                    target="base-surface",
                    mean_rate=4.2,
                    energy_range_ev=(1.5, 3.5),
                    coherence_range=(0.55, 0.85),
                    metadata={"tier": "superficie"},
                ),
            ],
            seed=config.random_seed,
        )

        for _ in range(config.steps):
            env.step(traffic=traffic, step_seconds=config.step_seconds)

        history = env.history
        payload_bits = config.payload_bytes * 8
        total_time = max(config.step_seconds * config.steps, config.step_seconds)
        return self._aggregate_mtq_metrics(history, payload_bits, total_time)

    def _configure_default_topology(self, env: MTQEnvironment) -> None:
        env.register_node(
            HoloNode("orbital-alpha", "Anillo orbital", ["procesamiento"]),
            NodeQuantumState(temperature_k=5.0, entanglement_entropy=0.18, stability_index=1.1),
        )
        env.register_node(
            HoloNode("orbital-beta", "Anillo orbital", ["buffer", "enlace"]),
            NodeQuantumState(temperature_k=4.2, entanglement_entropy=0.22, stability_index=1.05),
        )
        env.register_node(
            HoloNode("base-surface", "Base en superficie", ["receptor"]),
            NodeQuantumState(temperature_k=3.6, entanglement_entropy=0.28, stability_index=0.92),
        )
        env.connect("orbital-alpha", "orbital-beta", base_fidelity=0.93, max_bandwidth=16, latency_ms=2.5)
        env.connect("orbital-beta", "base-surface", base_fidelity=0.91, max_bandwidth=12, latency_ms=3.3)

    def _aggregate_mtq_metrics(
        self,
        history: Sequence[MTQEvent],
        payload_bits: int,
        total_time_seconds: float,
    ) -> BenchmarkMetrics:
        if not history:
            return BenchmarkMetrics(
                protocol="Holonet-MTQ",
                variant="MTQ",
                latency_ms=0.0,
                throughput_mbps=0.0,
                failure_rate=0.0,
                logical_energy_ev=0.0,
                security_index=0.0,
            )

        delivered = sum(1 for event in history if event.delivered)
        latency = fmean(event.link_latency_ms for event in history)
        throughput = 0.0
        if total_time_seconds > 0:
            throughput = (delivered * payload_bits) / (total_time_seconds * 1_000_000)
        failure_rate = 1.0 - (delivered / float(len(history)))
        avg_energy = fmean(event.energy_ev for event in history)
        avg_coherence = fmean(event.final_coherence for event in history)
        logical_energy = avg_energy * avg_coherence
        fidelity = fmean(event.link_fidelity for event in history)
        security_index = self._clamp(fidelity * 0.7 + (1.0 - failure_rate) * 0.3)

        return BenchmarkMetrics(
            protocol="Holonet-MTQ",
            variant="MTQ",
            latency_ms=latency,
            throughput_mbps=throughput,
            failure_rate=failure_rate,
            logical_energy_ev=logical_energy,
            security_index=security_index,
        )

    # ------------------------------------------------------------------
    # Clásicos
    # ------------------------------------------------------------------
    def _simulate_classical_protocol(
        self,
        protocol: str,
        *,
        base_latency: float,
        jitter: float,
    ) -> BenchmarkMetrics:
        gaussian = self._rng.normal
        latency = float(max(0.2, gaussian(base_latency, jitter * 0.25)))
        load_factor = float(np.clip(gaussian(0.72, 0.08), 0.4, 0.95))
        reliability = float(np.clip(gaussian(0.97 if protocol == "TCP/IP" else 0.9, 0.03), 0.6, 0.999))
        throughput_capacity = 1_000.0 if protocol == "UDP/IP" else 920.0
        throughput = throughput_capacity * load_factor * reliability / 1000.0
        failure_rate = max(0.0, 1.0 - reliability)
        baseline_energy = 1.55 if protocol == "TCP/IP" else 1.35
        logical_energy = baseline_energy * (1.0 - 0.15 * load_factor)
        security_bias = 0.82 if protocol == "TCP/IP" else 0.68
        security_index = self._clamp(security_bias * reliability)

        return BenchmarkMetrics(
            protocol=protocol,
            variant="Local",
            latency_ms=latency,
            throughput_mbps=throughput,
            failure_rate=failure_rate,
            logical_energy_ev=logical_energy,
            security_index=security_index,
        )

    @staticmethod
    def _clamp(value: float, minimum: float = 0.0, maximum: float = 1.0) -> float:
        return max(minimum, min(maximum, value))


# ----------------------------------------------------------------------
# Export helpers
# ----------------------------------------------------------------------
def export_results_csv(path: str, results: Iterable[BenchmarkMetrics]) -> None:
    """Genera un archivo CSV con la comparación de protocolos."""

    import csv

    with open(path, "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "protocol",
                "variant",
                "latency_ms",
                "throughput_mbps",
                "failure_rate",
                "logical_energy_ev",
                "security_index",
            ],
        )
        writer.writeheader()
        for metric in results:
            writer.writerow(metric.as_dict())


def export_results_html(path: str, results: Iterable[BenchmarkMetrics]) -> None:
    """Crea un reporte HTML con tabla comparativa y métricas destacadas."""

    metrics_list = list(results)
    if not metrics_list:
        raise ValueError("Se requiere al menos un resultado para exportar")

    best_throughput = max(metrics_list, key=lambda metric: metric.throughput_mbps)
    best_security = max(metrics_list, key=lambda metric: metric.security_index)

    def _format_row(metric: BenchmarkMetrics) -> str:
        return """
            <tr>
                <td>{protocol}</td>
                <td>{variant}</td>
                <td>{latency:.3f}</td>
                <td>{throughput:.3f}</td>
                <td>{failure:.4f}</td>
                <td>{energy:.3f}</td>
                <td>{security:.3f}</td>
            </tr>
        """.format(
            protocol=metric.protocol,
            variant=metric.variant,
            latency=metric.latency_ms,
            throughput=metric.throughput_mbps,
            failure=metric.failure_rate,
            energy=metric.logical_energy_ev,
            security=metric.security_index,
        )

    rows = "\n".join(_format_row(metric) for metric in metrics_list)
    highlights = f"""
        <ul>
            <li><strong>Máximo throughput:</strong> {best_throughput.protocol} ({best_throughput.throughput_mbps:.3f} Mbps)</li>
            <li><strong>Índice de seguridad superior:</strong> {best_security.protocol} ({best_security.security_index:.3f})</li>
        </ul>
    """
    html = f"""<!DOCTYPE html>
<html lang=\"es\">
<head>
    <meta charset=\"utf-8\">
    <title>Comparativa de protocolos Holonet vs TCP/UDP</title>
    <style>
        body {{ font-family: system-ui, sans-serif; margin: 2rem; }}
        table {{ border-collapse: collapse; width: 100%; margin-top: 1rem; }}
        th, td {{ border: 1px solid #ccc; padding: 0.5rem; text-align: center; }}
        th {{ background: #f6f6f6; }}
        caption {{ font-weight: bold; margin-bottom: 0.5rem; }}
    </style>
</head>
<body>
    <h1>Benchmark Holonet-MTQ vs TCP/UDP</h1>
    <p>Los valores reflejan una ejecución local con carga sintética controlada.</p>
    {highlights}
    <table>
        <caption>Métricas clave (latencia en ms, throughput en Mbps)</caption>
        <thead>
            <tr>
                <th>Protocolo</th>
                <th>Variante</th>
                <th>Latencia</th>
                <th>Throughput</th>
                <th>Tasa de fallo</th>
                <th>Energía lógica</th>
                <th>Índice de seguridad</th>
            </tr>
        </thead>
        <tbody>
            {rows}
        </tbody>
    </table>
</body>
</html>
"""

    with open(path, "w", encoding="utf-8") as handle:
        handle.write(html)


def run_default_benchmark() -> List[BenchmarkMetrics]:
    """Atajo para ejecutar la comparación con la configuración por defecto."""

    comparator = ProtocolComparator()
    return comparator.run()


if __name__ == "__main__":  # pragma: no cover - CLI auxiliar
    results = run_default_benchmark()
    for metric in results:
        print(
            f"{metric.protocol:<12} | latencia={metric.latency_ms:.3f} ms | "
            f"throughput={metric.throughput_mbps:.3f} Mbps | fallos={metric.failure_rate:.4f} | "
            f"energía={metric.logical_energy_ev:.3f} eV | seguridad={metric.security_index:.3f}"
        )
