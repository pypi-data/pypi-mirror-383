"""Paquete principal de Holonet.

Proporciona acceso directo a los submódulos clave y expone la versión
instalada desde la distribución ``holonet-py``.
"""
from __future__ import annotations

from importlib import import_module
from importlib.metadata import PackageNotFoundError, version

try:  # pragma: no cover - durante el desarrollo no hay paquete instalado
    __version__ = version("holonet-py")
except PackageNotFoundError:  # pragma: no cover - fallback cuando no existe el paquete
    __version__ = "0.0.0"

core = import_module("holonet.core")
decoding = import_module("holonet.decoding")
hardware = import_module("holonet.hardware")
interface = import_module("holonet.interface")
modulation = import_module("holonet.modulation")
mtq = import_module("holonet.mtq")
network = import_module("holonet.network")
security = import_module("holonet.security")
simulation = import_module("holonet.simulation")
transmission = import_module("holonet.transmission")

__all__ = [
    "core",
    "decoding",
    "hardware",
    "interface",
    "modulation",
    "mtq",
    "network",
    "security",
    "simulation",
    "transmission",
    "__version__",
]
