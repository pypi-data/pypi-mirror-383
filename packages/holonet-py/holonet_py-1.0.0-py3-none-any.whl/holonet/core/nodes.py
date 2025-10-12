"""Gestión de nodos holográficos."""
from __future__ import annotations

from dataclasses import dataclass, field
from threading import RLock
from typing import Callable, Dict, Iterator, List, Optional

from .packets import MuonPacket


@dataclass
class HoloNode:
    """Nodo holográfico básico de la red muónica."""

    identifier: str
    location: str
    capabilities: List[str] = field(default_factory=list)

    def can_handle(self, capability: str) -> bool:
        """Indica si el nodo soporta una capacidad específica."""
        return capability in self.capabilities

    def process(self, packet: MuonPacket) -> str:
        """Procesa un paquete retornando un resumen de la acción realizada."""
        return (
            f"Nodo {self.identifier} procesó {len(packet.payload)} bytes "
            f"con densidad {packet.signal.leptonic_density:.2f}"
        )


class NodeRegistry:
    """Registro sencillo de nodos holográficos."""

    def __init__(self) -> None:
        self._nodes: Dict[str, HoloNode] = {}
        self._listeners: List[Callable[[HoloNode], None]] = []
        self._lock = RLock()

    def add(self, node: HoloNode) -> None:
        with self._lock:
            self._nodes[node.identifier] = node
            listeners = list(self._listeners)
        for listener in listeners:
            listener(node)

    def get(self, identifier: str) -> Optional[HoloNode]:
        with self._lock:
            return self._nodes.get(identifier)

    def all(self) -> List[HoloNode]:
        with self._lock:
            return list(self._nodes.values())

    def paginate(self, offset: int = 0, limit: int = 50) -> Iterator[HoloNode]:
        """Itera sobre una vista paginada sin materializar todos los nodos."""

        if offset < 0:
            raise ValueError("offset no puede ser negativo")
        if limit < 0:
            raise ValueError("limit no puede ser negativo")

        with self._lock:
            nodes = list(self._nodes.values())

        for index, node in enumerate(nodes):
            if index < offset:
                continue
            if index >= offset + limit:
                break
            yield node

    def subscribe(self, listener: Callable[[HoloNode], None]) -> None:
        with self._lock:
            if listener not in self._listeners:
                self._listeners.append(listener)

