"""Rutinas simples de decodificación."""
from __future__ import annotations

from typing import Iterable, List

from holonet.core.packets import MuonPacket


class SignalReader:
    """Reconstruye cadenas a partir de paquetes muónicos."""

    def decode_payloads(self, packets: Iterable[MuonPacket]) -> List[str]:
        return [packet.payload.decode("utf-8", errors="ignore") for packet in packets]

    def average_density(self, packets: Iterable[MuonPacket]) -> float:
        total_density = 0.0
        count = 0
        for packet in packets:
            total_density += packet.signal.leptonic_density
            count += 1
        return total_density / count if count else 0.0

