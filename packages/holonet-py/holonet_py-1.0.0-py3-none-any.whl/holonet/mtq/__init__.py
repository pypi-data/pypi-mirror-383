"""Módulo de modelado cuántico-macroscópico (MTQ)."""

from .quantum_packet import QuantumPacket, LeptonicSignature
from .state_models import NodeQuantumState, ThermalNoiseModel
from .tunnel_engine import TunnelEngine
from .coherence_controller import CoherenceController
from .decorators import tunnelable
from .optimizer import (
    MTQOptimizer,
    OptimizedParameters,
    TrainingSample,
    build_optimizer,
)
from .quantum_interface_ibm import (
    IBMQuantumInterface,
    IBMQuantumInterfaceError,
    ValidationResult,
)

__all__ = [
    "QuantumPacket",
    "LeptonicSignature",
    "NodeQuantumState",
    "ThermalNoiseModel",
    "TunnelEngine",
    "CoherenceController",
    "tunnelable",
    "MTQOptimizer",
    "OptimizedParameters",
    "TrainingSample",
    "build_optimizer",
    "IBMQuantumInterface",
    "ValidationResult",
    "IBMQuantumInterfaceError",
]
