"""Modelos de estado para nodos del motor cuántico-macroscópico."""
from __future__ import annotations

from dataclasses import dataclass

from .quantum_packet import QuantumPacket


@dataclass
class NodeQuantumState:
    """Representa las condiciones cuánticas y térmicas de un nodo MTQ."""

    temperature_k: float
    entanglement_entropy: float
    stability_index: float

    def normalized_entropy(self) -> float:
        """Normaliza la entropía al rango [0, 1] para cálculos probabilísticos."""

        return max(0.0, min(1.0, self.entanglement_entropy))

    def stability_factor(self) -> float:
        """Calcula un factor de estabilidad ajustado por la entropía cuántica."""

        entropy_penalty = 1.0 - 0.5 * self.normalized_entropy()
        return max(0.0, min(1.0, self.stability_index * entropy_penalty))


@dataclass
class ThermalNoiseModel:
    """Evalúa la cantidad de ruido térmico aplicado a un paquete cuántico."""

    base_noise: float = 0.05
    temperature_coeff: float = 1e-3

    def noise_for(self, state: NodeQuantumState, packet: QuantumPacket) -> float:
        """Calcula el ruido térmico aplicable a un paquete concreto."""

        thermal_component = state.temperature_k * self.temperature_coeff
        entropy_component = state.normalized_entropy() * 0.1
        energy_component = packet.energy_ev * 1e-6
        return self.base_noise + thermal_component + entropy_component + energy_component
