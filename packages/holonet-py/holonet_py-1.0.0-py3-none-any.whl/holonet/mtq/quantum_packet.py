"""Modelos de paquetes cuánticos utilizados por el subsistema MTQ."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass(frozen=True)
class LeptonicSignature:
    """Describe la impronta leptónica asociada a un paquete cuántico."""

    flavor: str
    generation: int
    polarization: float

    def normalized_polarization(self) -> float:
        """Devuelve la polarización restringida al rango ``[-1.0, 1.0]``."""

        return max(-1.0, min(1.0, self.polarization))


@dataclass
class QuantumPacket:
    """Representa un paquete cuántico con información leptónica y coherencia."""

    leptonic_signature: LeptonicSignature
    energy_ev: float
    coherence: float
    metadata: Dict[str, Any] = field(default_factory=dict)

    MIN_COHERENCE: float = field(default=0.0, init=False, repr=False)
    MAX_COHERENCE: float = field(default=1.0, init=False, repr=False)

    def __post_init__(self) -> None:
        self.coherence = self._clamp_coherence(self.coherence)

    def _clamp_coherence(self, value: float) -> float:
        return max(self.MIN_COHERENCE, min(self.MAX_COHERENCE, value))

    def update_coherence(self, delta: float) -> float:
        """Actualiza el grado de coherencia dentro de los márgenes permitidos."""

        self.coherence = self._clamp_coherence(self.coherence + delta)
        return self.coherence

    def degrade(self, noise_factor: float) -> float:
        """Reduce la coherencia en función del ruido macroscópico observado."""

        return self.update_coherence(-abs(noise_factor))

    def effective_energy(self) -> float:
        """Calcula la energía efectiva considerando la pérdida de coherencia."""

        return self.energy_ev * self.coherence
