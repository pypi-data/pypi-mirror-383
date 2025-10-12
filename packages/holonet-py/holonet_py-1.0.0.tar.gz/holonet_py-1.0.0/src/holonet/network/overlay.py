"""Adaptadores de overlay para transportar tramas ópticas MTQ."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from holonet.transmission.fiber import OpticalFrame


@dataclass
class OverlayAdapter:
    """Adaptador base para plataformas de red superpuesta."""

    name: str
    mtu: int = 1400
    connected_peers: Dict[str, str] = field(default_factory=dict)
    routed_frames: List[tuple[str, OpticalFrame]] = field(default_factory=list)

    def connect_peer(self, peer_id: str, address: str) -> None:
        """Establece una sesión con un par del overlay."""

        self.connected_peers[peer_id] = address

    def disconnect_peer(self, peer_id: str) -> None:
        """Elimina un par conocido."""

        self.connected_peers.pop(peer_id, None)

    def send_frame(self, peer_id: str, frame: OpticalFrame) -> None:
        """Envía una trama óptica hacia el par especificado."""

        if peer_id not in self.connected_peers:
            raise ValueError(f"El par {peer_id} no está conectado al overlay {self.name}")
        if len(frame.payload) > self.mtu:
            raise ValueError("La trama óptica excede la MTU configurada para el túnel")
        self.routed_frames.append((peer_id, frame))


@dataclass
class ZeroTierAdapter(OverlayAdapter):
    """Simulación sencilla de un adaptador ZeroTier."""

    network_id: str = ""

    def connect_peer(self, peer_id: str, address: str) -> None:  # type: ignore[override]
        super().connect_peer(peer_id, f"zt://{self.network_id}/{address}")


@dataclass
class WireGuardAdapter(OverlayAdapter):
    """Simulación de un túnel WireGuard."""

    tunnel_name: str = "wg-mtq"
    allowed_ips: Dict[str, str] = field(default_factory=dict)

    def connect_peer(self, peer_id: str, address: str) -> None:  # type: ignore[override]
        super().connect_peer(peer_id, address)
        self.allowed_ips[peer_id] = address


@dataclass
class MTQOverlaySession:
    """Coordina múltiples saltos MTQ dentro de un overlay."""

    adapter: OverlayAdapter
    hops: List[str] = field(default_factory=list)

    def register_hop(self, hop_id: str, address: str) -> None:
        """Añade un salto y establece la conexión en el overlay."""

        if hop_id not in self.hops:
            self.hops.append(hop_id)
        self.adapter.connect_peer(hop_id, address)

    def transmit(self, frame: OpticalFrame) -> List[str]:
        """Envía la trama a cada salto registrado."""

        delivered: List[str] = []
        for hop_id in self.hops:
            self.adapter.send_frame(hop_id, frame)
            delivered.append(hop_id)
        return delivered


@dataclass
class LocalMTQHop:
    """Representa un dispositivo local (Raspberry Pi/servidor) en la cadena MTQ."""

    hop_id: str
    adapter: OverlayAdapter
    processed_frames: List[OpticalFrame] = field(default_factory=list)
    address: Optional[str] = None

    def attach(self, address: str) -> None:
        """Asocia el salto al overlay usando la dirección indicada."""

        self.address = address
        self.adapter.connect_peer(self.hop_id, address)

    def process(self, frame: OpticalFrame) -> Dict[str, str]:
        """Registra la trama recibida y devuelve un resumen operativo."""

        self.processed_frames.append(frame)
        return {
            "hop_id": self.hop_id,
            "frame_id": frame.frame_id,
            "wavelength_nm": f"{frame.wavelength_nm:.2f}",
            "overlay": self.adapter.name,
        }

    def forward(self, next_hop: str, frame: OpticalFrame) -> None:
        """Reenvía la trama a otro salto dentro del overlay."""

        self.adapter.send_frame(next_hop, frame)


__all__ = [
    "OverlayAdapter",
    "ZeroTierAdapter",
    "WireGuardAdapter",
    "MTQOverlaySession",
    "LocalMTQHop",
]
