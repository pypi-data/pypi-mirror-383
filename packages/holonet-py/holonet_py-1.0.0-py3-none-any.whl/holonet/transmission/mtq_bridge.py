"""Puente entre el subsistema MTQ y la transmisión clásica."""
from __future__ import annotations

import json
import logging
import math
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional

from holonet.core.packets import MuonPacket, MuonSignal

from .fiber import LocalFiber, OpticalFiber, OpticalFrame

from ..mtq.quantum_packet import LeptonicSignature, QuantumPacket
from ..mtq.state_models import NodeQuantumState
from ..mtq.tunnel_engine import TunnelEngine
from ..mtq.coherence_controller import CoherenceController


LOGGER = logging.getLogger(__name__)


def _safe_float(value: Any, default: float, field: str) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError):
        LOGGER.warning("Valor inválido para %s: %r", field, value)
        return default
    if not math.isfinite(result):
        LOGGER.warning("Valor no finito para %s: %r", field, value)
        return default
    return result


def _safe_int(value: Any, default: int, field: str) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        LOGGER.warning("Valor inválido para %s: %r", field, value)
        return default


@dataclass(frozen=True)
class TunnelResult:
    """Resultado de un intento de túnel a través del puente MTQ."""

    probability: float
    tunneled: bool
    quantum_packet: QuantumPacket
    muon_packet: Optional[MuonPacket]

    def as_dict(self) -> Dict[str, Any]:
        """Serializa el resultado para uso en APIs o registros."""

        leptonic = self.quantum_packet.leptonic_signature
        data: Dict[str, Any] = {
            "tunneled": self.tunneled,
            "probability": self.probability,
            "quantum_metadata": {
                "energy_ev": self.quantum_packet.energy_ev,
                "coherence": self.quantum_packet.coherence,
                "leptonic_signature": {
                    "flavor": leptonic.flavor,
                    "generation": leptonic.generation,
                    "polarization": leptonic.polarization,
                },
                "metadata": self.quantum_packet.metadata,
            },
        }
        data["muon_packet"] = self.muon_packet.as_dict() if self.muon_packet else None
        return data


class MTQBridge:
    """Puente transparente entre paquetes cuánticos y muónicos."""

    def __init__(
        self,
        tunnel_engine: Optional[TunnelEngine] = None,
        coherence_controller: Optional[CoherenceController] = None,
        fiber: Optional[LocalFiber] = None,
        optical_fiber: Optional[OpticalFiber] = None,
    ) -> None:
        self._tunnel_engine = tunnel_engine or TunnelEngine()
        self._coherence_controller = coherence_controller or CoherenceController()
        self._fiber = fiber
        self._optical_fiber = optical_fiber

    @property
    def fiber(self) -> Optional[LocalFiber]:
        return self._fiber

    @fiber.setter
    def fiber(self, new_fiber: Optional[LocalFiber]) -> None:
        self._fiber = new_fiber

    @property
    def optical_fiber(self) -> Optional[OpticalFiber]:
        return self._optical_fiber

    @optical_fiber.setter
    def optical_fiber(self, new_fiber: Optional[OpticalFiber]) -> None:
        self._optical_fiber = new_fiber

    def transmit(
        self,
        packet: QuantumPacket,
        state: NodeQuantumState,
        *,
        wavelength_nm: Optional[float] = None,
    ) -> TunnelResult:
        """Intenta transportar un paquete cuántico hacia el dominio clásico."""

        probability = self._tunnel_engine.tunnel_probability(packet, state)
        tunneled = self._tunnel_engine.attempt_tunnel(packet, state)

        muon_packet = None
        if tunneled:
            muon_packet = self._quantum_to_muon(packet)
            if self._fiber is not None:
                self._fiber.send(muon_packet)
            if self._optical_fiber is not None and wavelength_nm is not None:
                frame = OpticalFrame.from_muon_packet(muon_packet, wavelength_nm=wavelength_nm)
                self._optical_fiber.send(frame)
            self._coherence_controller.dampen(packet, 0.1)
        else:
            self._coherence_controller.compensate_noise(packet, 0.05)

        return TunnelResult(probability, tunneled, packet, muon_packet)

    def receive(self) -> Optional[QuantumPacket]:
        """Recupera el siguiente paquete clásico y lo proyecta al dominio MTQ."""

        if self._fiber is None:
            return None
        muon_packet = self._fiber.receive()
        if muon_packet is None:
            return None
        return self._muon_to_quantum(muon_packet)

    def drain_quantum(self) -> Iterable[QuantumPacket]:
        """Extrae todos los paquetes disponibles del canal clásico."""

        if self._fiber is None:
            return []
        drained: List[QuantumPacket] = []
        for packet in self._fiber.drain():
            drained.append(self._muon_to_quantum(packet))
        return drained

    def to_optical_frame(
        self,
        muon_packet: MuonPacket,
        *,
        wavelength_nm: float,
        src_ip: str,
        dst_ip: str,
        src_port: int,
        dst_port: int,
    ) -> OpticalFrame:
        """Empaqueta un paquete muónico en una trama óptica lista para TCP/IP."""

        frame = OpticalFrame.from_muon_packet(muon_packet, wavelength_nm=wavelength_nm)
        frame.encapsulate_tcp_ip(src_ip, dst_ip, src_port, dst_port)
        return frame

    def from_optical_frame(self, frame: OpticalFrame) -> QuantumPacket:
        """Proyecta una trama óptica de vuelta al dominio MTQ."""

        muon_packet = frame.to_muon_packet()
        return self._muon_to_quantum(muon_packet)

    def receive_optical(self) -> Optional[QuantumPacket]:
        """Recupera y proyecta una trama óptica desde el canal óptico configurado."""

        if self._optical_fiber is None:
            return None
        frame = self._optical_fiber.receive()
        if frame is None:
            return None
        return self.from_optical_frame(frame)

    def _quantum_to_muon(self, packet: QuantumPacket) -> MuonPacket:
        signature = packet.leptonic_signature
        metadata = {
            "flavor": signature.flavor,
            "generation": signature.generation,
            "polarization": signature.polarization,
            "coherence": packet.coherence,
            "energy_ev": packet.energy_ev,
        }
        metadata.update(packet.metadata)
        payload = json.dumps(metadata, ensure_ascii=False).encode("utf-8")
        signal = MuonSignal(
            frequencies=[packet.energy_ev],
            leptonic_density=packet.coherence,
            metadata={
                "flavor": signature.flavor,
                "generation": signature.generation,
                "polarization": signature.polarization,
                "coherence": packet.coherence,
                **packet.metadata,
            },
        )
        return MuonPacket(payload=payload, signal=signal)

    def _muon_to_quantum(self, packet: MuonPacket) -> QuantumPacket:
        raw_metadata = getattr(packet.signal, "metadata", {})
        if isinstance(raw_metadata, dict):
            signature_data = dict(raw_metadata)
        else:
            LOGGER.warning("Metadata de señal inválida: %r", raw_metadata)
            signature_data = {}

        payload_data: Dict[str, Any] = {}
        try:
            payload_data = json.loads(packet.payload.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            if packet.payload:
                payload_data["payload"] = packet.payload.decode("utf-8", errors="ignore")
        if not isinstance(payload_data, dict):
            LOGGER.warning("Payload JSON inválido: %r", payload_data)
            payload_data = {}

        flavor = signature_data.pop("flavor", payload_data.get("flavor", "unknown"))
        generation = _safe_int(
            signature_data.pop("generation", payload_data.get("generation", 0)),
            0,
            "generation",
        )

        default_density = _safe_float(
            getattr(packet.signal, "leptonic_density", 0.0),
            0.0,
            "signal.leptonic_density",
        )

        polarization_source = signature_data.pop(
            "polarization",
            payload_data.get("polarization"),
        )
        if polarization_source is None:
            polarization_source = default_density
        polarization = _safe_float(polarization_source, default_density, "polarization")

        coherence_source = signature_data.pop(
            "coherence",
            payload_data.get("coherence"),
        )
        if coherence_source is None:
            coherence_source = default_density
        coherence = _safe_float(coherence_source, default_density, "coherence")

        default_energy = 0.0
        if getattr(packet.signal, "frequencies", None):
            first_frequency = packet.signal.frequencies[0]
            default_energy = _safe_float(first_frequency, 0.0, "signal.frequency")

        energy = _safe_float(
            payload_data.get("energy_ev", default_energy),
            default_energy,
            "energy_ev",
        )

        metadata = {**payload_data, **signature_data}
        metadata.pop("flavor", None)
        metadata.pop("generation", None)
        metadata.pop("polarization", None)
        metadata.pop("coherence", None)
        metadata.pop("energy_ev", None)

        signature = LeptonicSignature(flavor=flavor, generation=generation, polarization=polarization)
        quantum_packet = QuantumPacket(
            leptonic_signature=signature,
            energy_ev=energy,
            coherence=coherence,
            metadata=metadata,
        )
        return quantum_packet


__all__ = ["MTQBridge", "TunnelResult"]
