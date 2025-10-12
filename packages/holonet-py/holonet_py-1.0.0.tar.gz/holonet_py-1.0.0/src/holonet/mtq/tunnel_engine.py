"""Motor probabilístico para evaluar túneles cuánticos en la red MTQ."""
from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Callable

from .quantum_packet import QuantumPacket
from .state_models import NodeQuantumState, ThermalNoiseModel


@dataclass
class TunnelEngine:
    """Calcula probabilidades de túnel para paquetes cuánticos."""

    noise_model: ThermalNoiseModel = field(default_factory=ThermalNoiseModel)
    random_source: Callable[[], float] = field(default_factory=random.random)

    def tunnel_probability(self, packet: QuantumPacket, state: NodeQuantumState) -> float:
        """Evalúa la probabilidad de túnel considerando el ruido térmico."""

        noise = self.noise_model.noise_for(state, packet)
        base_probability = packet.coherence * state.stability_factor()
        probability = max(0.0, min(1.0, base_probability - noise))
        return probability

    def attempt_tunnel(self, packet: QuantumPacket, state: NodeQuantumState) -> bool:
        """Realiza un intento de túnel con componente aleatoria controlable."""

        probability = self.tunnel_probability(packet, state)
        outcome = self.random_source()
        return outcome <= probability
