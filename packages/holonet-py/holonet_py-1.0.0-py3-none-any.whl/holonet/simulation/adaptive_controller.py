"""Controlador adaptativo simplificado."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from holonet.core.packets import MuonPacket


@dataclass
class AdaptiveController:
    """Ajusta parámetros mediante un promedio móvil sencillo."""

    history: List[float] = field(default_factory=list)

    def update(self, packet: MuonPacket) -> float:
        self.history.append(packet.signal.leptonic_density)
        if len(self.history) > 10:
            self.history.pop(0)
        return sum(self.history) / len(self.history)

