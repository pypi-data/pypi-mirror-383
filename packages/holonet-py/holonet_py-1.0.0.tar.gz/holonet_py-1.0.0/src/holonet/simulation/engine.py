"""Motor de simulación muónica básico."""
from __future__ import annotations

import asyncio
import logging
from collections import deque
from dataclasses import dataclass, field
from datetime import UTC, datetime
from threading import RLock
from typing import Callable, Deque, Dict, Iterable, List, Optional

from holonet.core.packets import MuonPacket, MuonSignal
from holonet.core.nodes import HoloNode
from holonet.transmission.fiber import LocalFiber


LOGGER = logging.getLogger(__name__)


@dataclass
class SimulationEvent:
    """Representa un evento generado por el simulador."""

    node: HoloNode
    packet: MuonPacket
    recipient: str


@dataclass
class EmissionResult:
    """Resumen del resultado al propagar un paquete."""

    event: SimulationEvent
    listener_errors: List[str] = field(default_factory=list)

    @property
    def delivered(self) -> bool:
        """Indica si todas las notificaciones se completaron sin errores."""

        return not self.listener_errors


class QueueSaturatedError(RuntimeError):
    """Señaliza que la cola interna alcanzó el máximo permitido."""

    def __init__(self, max_pending: int) -> None:
        message = (
            "La cola de eventos pendientes alcanzó el límite "
            f"configurado ({max_pending})."
        )
        super().__init__(message)
        self.max_pending = max_pending


@dataclass
class SimulationEngine:
    """Coordina nodos y eventos sobre un canal local."""

    fiber: LocalFiber = field(default_factory=LocalFiber)
    listeners: List[tuple[Callable[[SimulationEvent], None], Optional[str]]] = field(
        default_factory=list
    )
    async_queues: List[tuple[asyncio.Queue[SimulationEvent], Optional[str]]] = field(
        default_factory=list
    )
    async_queue_maxsize: Optional[int] = None
    max_pending_events: Optional[int] = None
    _emitted_events: int = field(init=False, default=0)
    _last_queue_size: int = field(init=False, default=0)
    _latency_accumulator_ms: float = field(init=False, default=0.0)
    _latency_samples: int = field(init=False, default=0)
    _pending_events: Deque[SimulationEvent] = field(
        init=False, default_factory=deque
    )
    _rejected_events: int = field(init=False, default=0)
    _lock: RLock = field(init=False, repr=False, default_factory=RLock)

    def __post_init__(self) -> None:
        if self.async_queue_maxsize is not None and self.async_queue_maxsize < 0:
            raise ValueError("async_queue_maxsize debe ser un entero no negativo o None")
        if self.max_pending_events is not None:
            if self.max_pending_events <= 0:
                raise ValueError(
                    "max_pending_events debe ser un entero positivo o None"
                )
        with self._lock:
            self._last_queue_size = len(self._pending_events)

    def create_async_queue(self) -> asyncio.Queue[SimulationEvent]:
        """Crea una cola asíncrona respetando el límite configurado."""

        maxsize = 0 if self.async_queue_maxsize is None else self.async_queue_maxsize
        return asyncio.Queue(maxsize=maxsize)

    def register_listener(
        self,
        listener: Callable[[SimulationEvent], None] | asyncio.Queue[SimulationEvent],
        *,
        node_filter: Optional[str] = None,
    ) -> None:
        """Registra listeners síncronos o colas asíncronas."""

        with self._lock:
            if isinstance(listener, asyncio.Queue):
                self.async_queues.append((listener, node_filter))
            else:
                self.listeners.append((listener, node_filter))

    def unregister_listener(
        self, listener: Callable[[SimulationEvent], None] | asyncio.Queue[SimulationEvent]
    ) -> None:
        """Elimina listeners previamente registrados si siguen activos."""

        with self._lock:
            collections = (
                self.async_queues if isinstance(listener, asyncio.Queue) else self.listeners
            )
            for index, entry in enumerate(list(collections)):
                registered, _ = entry
                if registered is listener:
                    try:
                        collections.pop(index)
                    except IndexError:
                        pass
                    break

    def emit(
        self,
        node: HoloNode,
        payload: bytes,
        signal: MuonSignal,
        *,
        recipients: Iterable[str] | None = None,
    ) -> EmissionResult:
        packet = MuonPacket(payload, signal)

        target_nodes = list(recipients or [node.identifier])
        listener_errors: List[str] = []
        primary_event: Optional[SimulationEvent] = None

        for recipient in target_nodes:
            with self._lock:
                if (
                    self.max_pending_events is not None
                    and len(self._pending_events) >= self.max_pending_events
                ):
                    self._rejected_events += 1
                    self._last_queue_size = len(self._pending_events)
                    raise QueueSaturatedError(self.max_pending_events)
                event = SimulationEvent(node=node, packet=packet, recipient=recipient)
                self._pending_events.append(event)
                self._emitted_events += 1
                listeners_snapshot = list(self.listeners)
                async_snapshot = list(self.async_queues)

            for listener, node_filter in listeners_snapshot:
                if node_filter is not None and node_filter != recipient:
                    continue
                try:
                    listener(event)
                except Exception as exc:  # pragma: no cover - defensive
                    LOGGER.exception("Listener error for node %s", recipient)
                    listener_errors.append(f"{type(exc).__name__}: {exc}")

            for queue, node_filter in async_snapshot:
                if node_filter is not None and node_filter != recipient:
                    continue
                try:
                    queue.put_nowait(event)
                except asyncio.QueueFull:
                    # Si una cola impone límite se descarta el evento en lugar de bloquear.
                    continue

            if primary_event is None:
                primary_event = event

        with self._lock:
            self._last_queue_size = len(self._pending_events)
        return EmissionResult(event=primary_event, listener_errors=listener_errors)

    def listen(self, node_id: str) -> Optional[MuonPacket]:
        with self._lock:
            matched: Optional[SimulationEvent] = None
            remaining: Deque[SimulationEvent] = deque()

            while self._pending_events:
                event = self._pending_events.popleft()
                if matched is None and event.recipient == node_id:
                    matched = event
                    continue
                remaining.append(event)

            self._pending_events = remaining
            self._last_queue_size = len(self._pending_events)

        if matched is None:
            return None

        packet = matched.packet
        self._record_latency(packet)
        return packet

    def flush(self, node_id: Optional[str] = None) -> List[MuonPacket]:
        with self._lock:
            packets: List[MuonPacket] = []
            if node_id is None:
                while self._pending_events:
                    event = self._pending_events.popleft()
                    packets.append(event.packet)
            else:
                remaining: Deque[SimulationEvent] = deque()
                while self._pending_events:
                    event = self._pending_events.popleft()
                    if event.recipient == node_id:
                        packets.append(event.packet)
                    else:
                        remaining.append(event)
                self._pending_events = remaining

            self._last_queue_size = len(self._pending_events)

        for packet in packets:
            self._record_latency(packet)
        return packets

    def reset_metrics(self) -> None:
        """Restablece los contadores internos."""

        with self._lock:
            self._emitted_events = 0
            self._last_queue_size = len(self._pending_events)
            self._latency_accumulator_ms = 0.0
            self._latency_samples = 0
            self._rejected_events = 0

    def _record_latency(self, packet: MuonPacket) -> None:
        now = datetime.now(UTC)
        latency_ms = (now - packet.created_at).total_seconds() * 1000
        if latency_ms < 0:
            latency_ms = 0.0
        with self._lock:
            self._latency_accumulator_ms += latency_ms
            self._latency_samples += 1

    @property
    def average_latency_ms(self) -> float:
        with self._lock:
            if self._latency_samples == 0:
                return 0.0
            return self._latency_accumulator_ms / self._latency_samples

    @property
    def metrics(self) -> Dict[str, float | int]:
        """Expone un resumen de métricas para el motor."""

        with self._lock:
            return {
                "events_emitted": self._emitted_events,
                "queue_size": self._last_queue_size,
                "average_latency_ms": self.average_latency_ms,
                "rejected_events": self._rejected_events,
                "max_pending_events": self.max_pending_events or 0,
            }

