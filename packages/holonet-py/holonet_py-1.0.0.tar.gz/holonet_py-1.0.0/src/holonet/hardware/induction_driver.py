"""Drivers simulados de hardware de inducción."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from threading import RLock
from typing import Dict, List, Tuple

from holonet.core.packets import MuonSignal


@dataclass
class InductionDevice:
    identifier: str
    calibration_factor: float = 1.0
    calibration_history: List[Tuple[datetime, float]] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.calibration_history:
            baseline = datetime.min.replace(tzinfo=timezone.utc)
            self.calibration_history.append((baseline, self.calibration_factor))
        else:
            self.calibration_history.sort(key=lambda entry: entry[0])
            self.calibration_factor = self.calibration_history[-1][1]

    def update_calibration(self, timestamp: datetime, factor: float) -> None:
        """Registra un nuevo factor de calibración para un instante dado."""
        self.calibration_history.append((timestamp, factor))
        self.calibration_history.sort(key=lambda entry: entry[0])
        self.calibration_factor = self.calibration_history[-1][1]

    def _resolve_calibration(self, timestamp: datetime | None) -> float:
        if not self.calibration_history:
            return self.calibration_factor
        if timestamp is None:
            return self.calibration_history[-1][1]
        applicable = [factor for moment, factor in self.calibration_history if moment <= timestamp]
        if applicable:
            return applicable[-1]
        return self.calibration_history[0][1]

    def sense(self, signal: MuonSignal) -> float:
        timestamp = self._extract_timestamp(signal)
        factor = self._resolve_calibration(timestamp)
        return signal.intensity() * factor

    @staticmethod
    def _extract_timestamp(signal: MuonSignal) -> datetime | None:
        metadata_value = signal.metadata.get("timestamp") if signal.metadata else None
        if isinstance(metadata_value, datetime):
            return metadata_value
        if isinstance(metadata_value, str):
            try:
                return datetime.fromisoformat(metadata_value)
            except ValueError:
                return None
        return None


class DeviceRegistry:
    """Registro de dispositivos de inducción."""

    def __init__(self) -> None:
        self._devices: Dict[str, InductionDevice] = {}
        self._lock = RLock()

    def register(self, device: InductionDevice) -> None:
        with self._lock:
            self._devices[device.identifier] = device

    def list_devices(self) -> Dict[str, float]:
        with self._lock:
            return {
                identifier: dev.calibration_factor
                for identifier, dev in self._devices.items()
            }

