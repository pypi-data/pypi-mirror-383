"""Controlador para mantener la coherencia de paquetes cuánticos MTQ."""
from __future__ import annotations

from dataclasses import dataclass

from .quantum_packet import QuantumPacket


@dataclass
class CoherenceController:
    """Gestiona los ajustes dinámicos de coherencia."""

    max_gain: float = 0.25
    max_loss: float = 0.35

    def drive_to_target(self, packet: QuantumPacket, target: float, feedback: float = 1.0) -> float:
        """Ajusta la coherencia del paquete hacia un objetivo específico."""

        delta = (target - packet.coherence) * feedback
        delta = max(-self.max_loss, min(self.max_gain, delta))
        return packet.update_coherence(delta)

    def compensate_noise(self, packet: QuantumPacket, noise_level: float) -> float:
        """Aplica una realimentación para mitigar el ruido detectado."""

        compensation = min(self.max_gain, noise_level)
        return packet.update_coherence(compensation)

    def dampen(self, packet: QuantumPacket, factor: float) -> float:
        """Reduce la coherencia para evitar saturación en el túnel."""

        reduction = min(self.max_loss, abs(factor))
        return packet.update_coherence(-reduction)
