"""Definiciones de paquetes y señales muónicas."""
from __future__ import annotations

import base64
import hashlib
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, Dict, Iterable, List


@dataclass
class MuonSignal:
    """Representa una señal muónica capturada en la simulación."""

    frequencies: List[float]
    leptonic_density: float
    metadata: Dict[str, Any] = field(default_factory=dict)

    def intensity(self) -> float:
        """Calcula una medida simple de intensidad."""
        return sum(self.frequencies) * self.leptonic_density


@dataclass
class MuonPacket:
    """Unidad de información transportada por la red muónica."""

    payload: bytes
    signal: MuonSignal
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def as_dict(self) -> Dict[str, Any]:
        """Serializa el paquete a un diccionario para su transmisión."""

        payload_encoded = base64.b64encode(self.payload).decode("ascii")
        payload_info: Dict[str, Any] = {
            "encoding": "base64",  # Se evita pérdida de información binaria.
            "data": payload_encoded,
            "length": len(self.payload),
        }
        if self.payload:
            payload_info["sha256"] = hashlib.sha256(self.payload).hexdigest()

        return {
            "payload": payload_info,
            "signal": {
                "frequencies": self.signal.frequencies,
                "leptonic_density": self.signal.leptonic_density,
                "metadata": self.signal.metadata,
            },
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class LeptonicPattern:
    """Describe un patrón de modulación leptónica."""

    name: str
    sequence: Iterable[float]
    description: str = ""

    def to_signal(self, density: float, metadata: Dict[str, Any] | None = None) -> MuonSignal:
        """Construye una señal a partir del patrón y la densidad especificada."""
        metadata = dict(metadata or {})
        metadata.setdefault("pattern", self.name)
        return MuonSignal(list(self.sequence), density, metadata)

