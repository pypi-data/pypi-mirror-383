"""Nodos de red con estado MTQ y enlaces energéticos dinámicos."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, Tuple

from holonet.core.nodes import HoloNode
from holonet.mtq.quantum_packet import QuantumPacket
from holonet.mtq.state_models import NodeQuantumState
from holonet.mtq.tunnel_engine import TunnelEngine


@dataclass
class MTQNetworkNode:
    """Envuelve un :class:`HoloNode` con información MTQ y enlaces dinámicos."""

    base: HoloNode
    mtq_state: NodeQuantumState | None = None
    tunnel_engine: TunnelEngine = field(default_factory=TunnelEngine)
    role: str = "relay"
    tunnel_links: Dict[str, float] = field(default_factory=dict)
    classical_links: Dict[str, float] = field(default_factory=dict)
    energy_budget: float = 0.0

    @property
    def identifier(self) -> str:
        """Identificador del nodo asociado."""

        return self.base.identifier

    def update_mtq_state(self, state: NodeQuantumState | None) -> None:
        """Actualiza el estado cuántico del nodo."""

        self.mtq_state = state

    def set_role(self, role: str) -> None:
        """Define el rol lógico del nodo dentro de la topología."""

        self.role = role

    def configure_tunnel_links(self, links: Dict[str, float] | None) -> None:
        """Sobrescribe los enlaces de túnel conocidos."""

        if links is None:
            return
        self.tunnel_links = {identifier: max(0.0, energy) for identifier, energy in links.items()}

    def configure_classical_links(self, links: Dict[str, float] | None) -> None:
        """Sobrescribe los enlaces clásicos conocidos."""

        if links is None:
            return
        self.classical_links = {identifier: max(0.0, energy) for identifier, energy in links.items()}

    def upsert_tunnel_link(self, identifier: str, energy_cost: float) -> None:
        """Inserta o actualiza un enlace de túnel hacia ``identifier``."""

        self.tunnel_links[identifier] = max(0.0, energy_cost)

    def upsert_classical_link(self, identifier: str, energy_cost: float) -> None:
        """Inserta o actualiza un enlace clásico hacia ``identifier``."""

        self.classical_links[identifier] = max(0.0, energy_cost)

    def remove_link(self, identifier: str) -> None:
        """Elimina cualquier referencia a un enlace con el nodo indicado."""

        self.tunnel_links.pop(identifier, None)
        self.classical_links.pop(identifier, None)

    def mark_mtq_failure(self) -> None:
        """Marca el nodo como fuera de servicio para saltos MTQ."""

        self.mtq_state = None

    @property
    def tunnel_operational(self) -> bool:
        """Indica si existe un estado MTQ utilizable."""

        return self.mtq_state is not None

    def tunnel_probability(self, packet: QuantumPacket) -> float:
        """Calcula la probabilidad de éxito de un salto MTQ."""

        if not self.mtq_state:
            return 0.0
        return self.tunnel_engine.tunnel_probability(packet, self.mtq_state)

    def link_choice(
        self,
        identifier: str,
        *,
        packet: QuantumPacket | None = None,
    ) -> Tuple[float, bool]:
        """Devuelve el coste energético y el tipo de enlace elegido.

        El valor booleano indica si se utilizó un túnel cuántico. Si no existe
        un enlace disponible se devuelve ``(float("inf"), False)``.
        """

        prefer_tunnel = self.tunnel_operational and identifier in self.tunnel_links
        if prefer_tunnel and packet is not None:
            if self.tunnel_probability(packet) <= 0.0:
                prefer_tunnel = False
        if prefer_tunnel:
            return self.tunnel_links[identifier], True

        if identifier in self.classical_links:
            return self.classical_links[identifier], False

        return float("inf"), False

    def link_energy(
        self,
        identifier: str,
        *,
        packet: QuantumPacket | None = None,
    ) -> float:
        """Devuelve el coste energético elegido para un enlace determinado."""

        cost, _ = self.link_choice(identifier, packet=packet)
        return cost

    def register_energy_usage(self, amount: float) -> None:
        """Acumula el uso energético del nodo."""

        if amount == float("inf"):
            return
        self.energy_budget += max(0.0, amount)

    def neighbors(self) -> Iterable[str]:
        """Obtiene todos los vecinos conocidos por cualquier medio."""

        return set(self.tunnel_links) | set(self.classical_links)
