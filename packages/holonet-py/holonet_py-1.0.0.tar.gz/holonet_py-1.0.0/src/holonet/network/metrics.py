"""Recolectores y estructuras de métricas adaptativas."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from holonet.hardware.induction_driver import DeviceRegistry
from holonet.simulation.adaptive_controller import AdaptiveController
from holonet.core.packets import MuonPacket


@dataclass(frozen=True)
class CompositeMetric:
    """Representa métricas combinadas y normalizadas."""

    controller_metric: float
    device_factor: float
    normalized: float


class AdaptiveMetricCollector:
    """Combina métricas del controlador y el registro de dispositivos."""

    def __init__(self, controller: AdaptiveController, registry: DeviceRegistry) -> None:
        self._controller = controller
        self._registry = registry

    def collect(self, packet: MuonPacket, device_id: Optional[str] = None) -> CompositeMetric:
        """Obtiene métricas y devuelve una medición compuesta normalizada."""

        controller_metric = self._controller.update(packet)
        device_factor = self._resolve_device_factor(device_id)
        normalized = self._normalize(controller_metric, device_factor)
        return CompositeMetric(controller_metric, device_factor, normalized)

    def _resolve_device_factor(self, device_id: Optional[str]) -> float:
        devices = self._registry.list_devices()
        if device_id and device_id in devices:
            return devices[device_id]
        if not devices:
            return 1.0
        return sum(devices.values()) / len(devices)

    @staticmethod
    def _normalize(controller_metric: float, device_factor: float) -> float:
        combined = controller_metric * device_factor
        if combined <= 0:
            return 0.0
        return combined / (1.0 + combined)
