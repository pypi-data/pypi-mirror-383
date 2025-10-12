"""Puente WebSocket simplificado."""
from __future__ import annotations

import asyncio
import logging
from typing import AsyncIterator

from holonet.security.leptonic_guard import LeptonicGuard
from holonet.simulation.engine import SimulationEngine, SimulationEvent


LOGGER = logging.getLogger(__name__)


class WebSocketBridge:
    """Adaptador ligero para publicar paquetes por WebSocket."""

    def __init__(
        self,
        engine: SimulationEngine,
        guard: LeptonicGuard,
        queue: asyncio.Queue[SimulationEvent] | None = None,
    ) -> None:
        self._engine = engine
        self._queue = queue
        self._guard = guard

    async def stream_packets(
        self, node_id: str, token: str
    ) -> AsyncIterator[dict[str, str]]:
        if not node_id or not token:
            self._guard.audit_log.record(
                "ws_handshake_denied",
                node_id or "unknown",
                reason="missing_credentials",
            )
            raise PermissionError("Se requieren credenciales para suscribirse al puente")

        if not self._guard.verify_token(node_id, token):
            self._guard.audit_log.record(
                "ws_handshake_denied", node_id, reason="invalid_token"
            )
            raise PermissionError("Token inválido para el nodo")

        self._guard.audit_log.record("ws_handshake_accepted", node_id)

        queue: asyncio.Queue[SimulationEvent]
        if self._queue is not None:
            queue = self._queue
        else:
            queue = self._engine.create_async_queue()
        self._engine.register_listener(queue, node_filter=node_id)

        try:
            while True:
                event = await queue.get()
                if event.recipient != node_id:
                    self._guard.audit_log.record(
                        "ws_packet_filtered",
                        node_id,
                        expected=node_id,
                        received=event.recipient,
                    )
                    LOGGER.warning(
                        "Evento recibido para nodo %s pero asignado a %s", node_id, event.recipient
                    )
                    raise PermissionError(
                        "Se recibió un paquete no autorizado para este nodo"
                    )

                yield event.packet.as_dict()
        finally:
            self._engine.unregister_listener(queue)

