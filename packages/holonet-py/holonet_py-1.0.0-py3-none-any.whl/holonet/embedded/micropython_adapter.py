"""Adaptador para ejecutar Holonet en placas MicroPython."""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Callable, Deque, Dict, Iterable, Mapping, MutableMapping

from holonet.core.packets import MuonSignal
from holonet.mtq import LeptonicSignature, NodeQuantumState, QuantumPacket


@dataclass(slots=True)
class SensorConfig:
    """Configuración de un sensor de coherencia conectado a la placa."""

    name: str
    reader: Callable[[], float]
    scale: float = 1.0
    offset: float = 0.0

    def read(self) -> float:
        """Lee el valor bruto del sensor."""

        return float(self.reader())

    def apply_calibration(self, value: float) -> float:
        """Aplica la calibración básica ``scale`` y ``offset``."""

        return value * self.scale + self.offset


@dataclass(slots=True)
class SensorReading:
    """Representa una muestra agregada de todos los sensores disponibles."""

    timestamp: datetime
    values: Mapping[str, float]
    raw_values: Mapping[str, float]

    def as_dict(self) -> Dict[str, float]:
        return dict(self.values)


class MicroPythonAdapter:
    """Gestiona sensores MicroPython y los traduce a estados MTQ."""

    def __init__(self, board_id: str, history: int = 128) -> None:
        self.board_id = board_id
        self._history: Deque[SensorReading] = deque(maxlen=history)
        self._sensors: Dict[str, SensorConfig] = {}

    # ---------------------------------------------------------------
    # Gestión de sensores
    # ---------------------------------------------------------------
    def register_sensor(self, config: SensorConfig) -> None:
        """Registra un sensor para ser muestreado periódicamente."""

        self._sensors[config.name] = config

    def registered_sensors(self) -> Iterable[str]:
        return tuple(self._sensors.keys())

    # ---------------------------------------------------------------
    # Muestreo
    # ---------------------------------------------------------------
    def capture_sample(self) -> SensorReading:
        """Lee todos los sensores registrados y almacena la muestra."""

        if not self._sensors:
            raise RuntimeError("No hay sensores registrados en el adaptador MicroPython")

        raw_values: Dict[str, float] = {}
        calibrated: Dict[str, float] = {}
        for name, sensor in self._sensors.items():
            raw = sensor.read()
            raw_values[name] = raw
            calibrated[name] = sensor.apply_calibration(raw)

        reading = SensorReading(
            timestamp=datetime.now(UTC),
            values=calibrated,
            raw_values=raw_values,
        )
        self._history.append(reading)
        return reading

    def last_sample(self) -> SensorReading | None:
        return self._history[-1] if self._history else None

    def history(self) -> Iterable[SensorReading]:
        return tuple(self._history)

    # ---------------------------------------------------------------
    # Conversión de datos
    # ---------------------------------------------------------------
    def estimate_coherence(
        self,
        sample: SensorReading | None = None,
        window: int | None = None,
    ) -> float:
        """Estima la coherencia media en ``[0, 1]``."""

        if sample is not None:
            samples = [sample]
        else:
            samples = list(self._history)

        if not samples:
            return 0.0

        if window is not None:
            samples = samples[-window:]

        values = [value for entry in samples for value in entry.values.values()]
        if not values:
            return 0.0
        normalized = [max(0.0, min(1.0, value)) for value in values]
        return sum(normalized) / len(normalized)

    def to_muon_signal(self, reading: SensorReading) -> MuonSignal:
        """Traduce una lectura a una señal muónica utilizable por la red."""

        frequencies = list(reading.values.values())
        density = sum(frequencies) / len(frequencies) if frequencies else 0.0
        metadata: MutableMapping[str, object] = {
            "board_id": self.board_id,
            "timestamp": reading.timestamp.isoformat(),
            "raw": dict(reading.raw_values),
        }
        metadata.update(reading.as_dict())
        return MuonSignal(frequencies=frequencies, leptonic_density=density, metadata=metadata)

    def to_quantum_packet(
        self,
        signature: LeptonicSignature,
        energy_ev: float,
        reading: SensorReading | None = None,
    ) -> QuantumPacket:
        """Construye un ``QuantumPacket`` a partir de una lectura disponible."""

        sample = reading or self.last_sample() or self.capture_sample()
        coherence = self.estimate_coherence(sample)
        metadata: Dict[str, object] = {
            "board_id": self.board_id,
            "timestamp": sample.timestamp.isoformat(),
            "sensors": sample.as_dict(),
        }
        return QuantumPacket(
            leptonic_signature=signature,
            energy_ev=energy_ev,
            coherence=coherence,
            metadata=metadata,
        )

    def derive_node_state(
        self,
        reading: SensorReading | None = None,
        default_temperature: float = 295.0,
    ) -> NodeQuantumState:
        """Crea un ``NodeQuantumState`` basado en los sensores disponibles."""

        sample = reading or self.last_sample() or self.capture_sample()
        temperature = float(sample.values.get("temperature", default_temperature))
        entropy = float(sample.values.get("entropy", self.estimate_coherence(sample)))
        stability_raw = float(sample.values.get("stability", 1.0 - abs(entropy - self.estimate_coherence(sample))))
        stability = max(0.0, min(1.0, stability_raw))
        return NodeQuantumState(
            temperature_k=temperature,
            entanglement_entropy=max(0.0, min(1.0, entropy)),
            stability_index=stability,
        )

    # ---------------------------------------------------------------
    # Utilidades
    # ---------------------------------------------------------------
    def reset_history(self) -> None:
        self._history.clear()
