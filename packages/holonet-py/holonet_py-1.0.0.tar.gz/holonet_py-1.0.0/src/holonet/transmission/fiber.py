"""Canales de transmisión y tramas ópticas para MTQ."""
from __future__ import annotations

import json
import logging
import math
import uuid
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Deque, Dict, Iterable, Optional

from holonet.core.packets import MuonPacket, MuonSignal


LOGGER = logging.getLogger(__name__)


def _safe_float(value: Any, default: float, field: str) -> float:
    try:
        candidate = float(value)
    except (TypeError, ValueError):
        LOGGER.warning("Valor inválido para %s: %r", field, value)
        return default
    if not math.isfinite(candidate):
        LOGGER.warning("Valor no finito para %s: %r", field, value)
        return default
    return candidate


def _ensure_dict(value: Any, field: str) -> Dict[str, Any]:
    if isinstance(value, dict):
        return dict(value)
    LOGGER.warning("Se esperaba un objeto tipo dict en %s, se obtuvo: %r", field, value)
    return {}


@dataclass
class OpticalFrame:
    """Trama óptica que encapsula un paquete muónico para fibra."""

    payload: bytes
    wavelength_nm: float
    frame_id: str = field(default_factory=lambda: uuid.uuid4().hex)
    metadata: Dict[str, Any] = field(default_factory=dict)
    ip_encapsulation: Dict[str, Any] = field(default_factory=dict)

    def encapsulate_tcp_ip(
        self,
        src_ip: str,
        dst_ip: str,
        src_port: int,
        dst_port: int,
        *,
        ttl: int = 64,
        protocol: str = "MTQ",
    ) -> Dict[str, Any]:
        """Construye encabezados TCP/IP simulados para interoperabilidad."""

        total_length = len(self.payload)
        ip_header = {
            "version": 4,
            "ihl": 5,
            "tos": 0,
            "total_length": total_length,
            "id": hash((self.frame_id, src_ip, dst_ip)) & 0xFFFF,
            "flags": "DF",
            "ttl": ttl,
            "protocol": protocol,
            "src": src_ip,
            "dst": dst_ip,
        }
        tcp_header = {
            "src_port": src_port,
            "dst_port": dst_port,
            "sequence": hash((self.frame_id, src_port, dst_port)) & 0xFFFFFFFF,
            "acknowledgment": 0,
            "flags": ["PSH", "ACK"],
        }
        self.ip_encapsulation = {"ip": ip_header, "tcp": tcp_header}
        return self.ip_encapsulation

    def to_bytes(self) -> bytes:
        """Serializa la trama con un encabezado auto descriptivo."""

        header = {
            "frame_id": self.frame_id,
            "wavelength_nm": self.wavelength_nm,
            "metadata": self.metadata,
            "ip": self.ip_encapsulation,
        }
        header_bytes = json.dumps(header, sort_keys=True).encode("utf-8")
        header_length = len(header_bytes).to_bytes(2, "big")
        payload_length = len(self.payload).to_bytes(4, "big")
        return header_length + header_bytes + payload_length + self.payload

    @classmethod
    def from_bytes(cls, data: bytes) -> "OpticalFrame":
        """Reconstruye una trama óptica a partir de su representación binaria."""

        if len(data) < 6:
            raise ValueError("Los datos proporcionados no contienen una trama válida")

        header_length = int.from_bytes(data[:2], "big")
        header_end = 2 + header_length
        if header_end > len(data):
            raise ValueError("La longitud declarada del encabezado excede el buffer disponible")
        header_bytes = data[2:header_end]
        if header_end + 4 > len(data):
            raise ValueError("Los datos no contienen un campo de longitud de payload completo")
        payload_length = int.from_bytes(data[header_end : header_end + 4], "big")
        payload_start = header_end + 4
        payload_end = payload_start + payload_length
        if payload_end > len(data):
            raise ValueError("La longitud declarada del payload excede los datos disponibles")
        payload = data[payload_start:payload_end]

        try:
            header = json.loads(header_bytes.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise ValueError("El encabezado de la trama no es un JSON válido") from exc
        if not isinstance(header, dict):
            raise ValueError("El encabezado de la trama debe ser un objeto JSON")

        frame = cls(
            payload=payload,
            wavelength_nm=_safe_float(header.get("wavelength_nm", 0.0), 0.0, "wavelength_nm"),
            frame_id=header.get("frame_id", uuid.uuid4().hex)
            if isinstance(header.get("frame_id"), str)
            else uuid.uuid4().hex,
            metadata=_ensure_dict(header.get("metadata", {}), "metadata"),
            ip_encapsulation=_ensure_dict(header.get("ip", {}), "ip"),
        )
        return frame

    @classmethod
    def from_muon_packet(cls, packet: MuonPacket, wavelength_nm: float) -> "OpticalFrame":
        """Crea una trama óptica a partir de un paquete muónico."""

        metadata = {
            "signal": {
                "frequencies": packet.signal.frequencies,
                "leptonic_density": packet.signal.leptonic_density,
                "metadata": packet.signal.metadata,
            },
            "created_at": packet.created_at.isoformat(),
        }
        return cls(payload=packet.payload, wavelength_nm=wavelength_nm, metadata=metadata)

    def to_muon_packet(self) -> MuonPacket:
        """Reconstruye el paquete muónico original."""

        signal_data = _ensure_dict(self.metadata.get("signal", {}), "signal")
        created_at = self.metadata.get("created_at")

        raw_frequencies = signal_data.get("frequencies", [])
        frequencies: list[float] = []
        if isinstance(raw_frequencies, Iterable) and not isinstance(raw_frequencies, (bytes, str)):
            for entry in raw_frequencies:
                safe_freq = _safe_float(entry, 0.0, "signal.frequencies")
                frequencies.append(safe_freq)
        elif raw_frequencies:
            LOGGER.warning("Formato inválido para signal.frequencies: %r", raw_frequencies)

        density = _safe_float(signal_data.get("leptonic_density", 0.0), 0.0, "signal.leptonic_density")
        signal_metadata = _ensure_dict(signal_data.get("metadata", {}), "signal.metadata")

        signal = MuonSignal(
            frequencies=frequencies,
            leptonic_density=density,
            metadata=signal_metadata,
        )
        timestamp = datetime.now()
        if isinstance(created_at, str):
            try:
                timestamp = datetime.fromisoformat(created_at)
            except ValueError:
                LOGGER.warning("Fecha de creación inválida en trama óptica: %r", created_at)
        return MuonPacket(payload=self.payload, signal=signal, created_at=timestamp)


class LocalFiber:
    """Canal local para enviar y recibir paquetes muónicos."""

    def __init__(self) -> None:
        self._queue: Deque[MuonPacket] = deque()

    def send(self, packet: MuonPacket) -> None:
        self._queue.append(packet)

    def receive(self) -> Optional[MuonPacket]:
        if self._queue:
            return self._queue.popleft()
        return None

    def drain(self) -> Iterable[MuonPacket]:
        while self._queue:
            yield self._queue.popleft()

    def __len__(self) -> int:
        """Devuelve el número de paquetes en cola."""

        return len(self._queue)


class OpticalFiber:
    """Canal que opera con tramas ópticas."""

    def __init__(self) -> None:
        self._queue: Deque[OpticalFrame] = deque()

    def send(self, frame: OpticalFrame) -> None:
        self._queue.append(frame)

    def receive(self) -> Optional[OpticalFrame]:
        if self._queue:
            return self._queue.popleft()
        return None

    def drain(self) -> Iterable[OpticalFrame]:
        while self._queue:
            yield self._queue.popleft()

    def __len__(self) -> int:
        return len(self._queue)

