"""Enlace con backends de IBM Quantum para validar paquetes MTQ."""
from __future__ import annotations

import logging
from contextlib import suppress
from dataclasses import dataclass
from importlib import import_module
from typing import Any, Callable, Dict, Mapping, MutableMapping

from .quantum_packet import QuantumPacket


LOGGER = logging.getLogger(__name__)


def _load_exception_types(*specs: tuple[str, str]) -> tuple[type[Exception], ...]:
    error_types: list[type[Exception]] = []
    for module_path, attribute in specs:
        with suppress(ImportError, AttributeError):
            module = import_module(module_path)
            candidate = getattr(module, attribute)
            if isinstance(candidate, type) and issubclass(candidate, Exception):
                error_types.append(candidate)
    return tuple(error_types)


class IBMQuantumInterfaceError(RuntimeError):
    """Errores producidos al interactuar con IBM Quantum."""


@dataclass(slots=True)
class ValidationResult:
    """Resultado de una validación ejecutada en un backend IBM Quantum."""

    backend_name: str
    counts: Mapping[str, int]
    fidelity: float
    threshold: float
    accepted: bool
    metadata: MutableMapping[str, Any]


class IBMQuantumInterface:
    """Gestiona la conexión con IBM Quantum para validar paquetes."""

    _ACCOUNT_ERRORS = _load_exception_types(
        ("qiskit.providers.ibmq.exceptions", "IBMQAccountError"),
        ("qiskit.exceptions", "QiskitError"),
    )
    _BACKEND_ERRORS = _load_exception_types(
        ("qiskit.exceptions", "QiskitError"),
        ("qiskit.providers.exceptions", "QiskitBackendNotFoundError"),
        ("qiskit_aer.aererror", "AerError"),
    )
    if not _ACCOUNT_ERRORS:
        _ACCOUNT_ERRORS = (ValueError, RuntimeError)
    if not _BACKEND_ERRORS:
        _BACKEND_ERRORS = (RuntimeError, ValueError)

    def __init__(
        self,
        backend_name: str | None = "ibmq_qasm_simulator",
        token: str | None = None,
        hub: str | None = None,
        group: str | None = None,
        project: str | None = None,
        local_fallback: bool = True,
    ) -> None:
        self._backend_name = backend_name
        self._token = token
        self._hub = hub
        self._group = group
        self._project = project
        self._local_fallback = local_fallback

        self._backend = None
        self._imports: Dict[str, Any] | None = None

    # ---------------------------------------------------------------
    # Gestión de imports y proveedores
    # ---------------------------------------------------------------
    def _load_qiskit(self) -> Dict[str, Any]:
        if self._imports is not None:
            return self._imports

        try:
            from qiskit import QuantumCircuit  # type: ignore
        except ImportError as exc:  # pragma: no cover - qiskit no instalado
            raise IBMQuantumInterfaceError(
                "qiskit no está disponible en el entorno actual"
            ) from exc

        imports: Dict[str, Any] = {"QuantumCircuit": QuantumCircuit}

        # Backends locales
        aer_loader: list[Callable[[], Any]] = []
        try:  # pragma: no cover - dependencias opcionales
            from qiskit_aer import Aer

            aer_loader.append(lambda: Aer)
        except ImportError:  # pragma: no cover - fallback
            pass

        try:
            from qiskit import Aer

            aer_loader.append(lambda: Aer)
        except ImportError:  # pragma: no cover - fallback
            pass

        try:
            from qiskit import BasicAer

            aer_loader.append(lambda: BasicAer)
        except ImportError:  # pragma: no cover - fallback
            pass

        imports["local_backends"] = aer_loader

        # Proveedores IBM Quantum (dos APIs posibles)
        providers: list[Callable[[], Any]] = []
        try:  # pragma: no cover - depende de qiskit_ibm_provider
            from qiskit_ibm_provider import IBMProvider

            providers.append(lambda: IBMProvider(token=self._token) if self._token else IBMProvider())
        except ImportError:  # pragma: no cover - fallback al API clásico
            try:
                from qiskit import IBMQ

                def _old_provider_loader() -> Any:
                    if self._token:
                        try:
                            IBMQ.enable_account(self._token, overwrite=True)
                        except self._ACCOUNT_ERRORS as error:  # pragma: no cover - depende de IBMQ
                            LOGGER.error(
                                "No se pudo habilitar la cuenta IBMQ con el token proporcionado: %s",
                                error,
                            )
                            raise IBMQuantumInterfaceError(
                                "No se pudo habilitar la cuenta IBMQ con el token proporcionado"
                            ) from error
                    if self._hub and self._group and self._project:
                        return IBMQ.get_provider(hub=self._hub, group=self._group, project=self._project)
                    return IBMQ.get_provider()

                providers.append(_old_provider_loader)
            except ImportError:  # pragma: no cover - sin soporte IBM
                pass

        imports["providers"] = providers

        try:
            from qiskit.transpiler import PassManager
        except ImportError:  # pragma: no cover - versiones antiguas
            PassManager = None
        imports["PassManager"] = PassManager

        try:
            from qiskit import transpile
        except ImportError as exc:  # pragma: no cover - qiskit incompatible
            raise IBMQuantumInterfaceError("No se pudo importar qiskit.transpile") from exc
        imports["transpile"] = transpile

        self._imports = imports
        return imports

    def _resolve_backend(self) -> Any:
        if self._backend is not None:
            return self._backend

        imports = self._load_qiskit()
        providers = imports["providers"]
        last_error: Exception | None = None

        for provider_loader in providers:  # pragma: no cover - requiere credenciales IBM
            try:
                provider = provider_loader()
                if self._backend_name:
                    backend = provider.get_backend(self._backend_name)
                else:
                    simulator_backends = [
                        backend for backend in provider.backends(simulator=True)
                        if getattr(backend.configuration(), "n_qubits", 1) >= 1
                    ]
                    backend = simulator_backends[0] if simulator_backends else provider.backends()[0]
                self._backend = backend
                return backend
            except IBMQuantumInterfaceError:
                raise
            except self._BACKEND_ERRORS as error:  # pragma: no cover - depende de proveedor
                last_error = error
                LOGGER.warning(
                    "Proveedor IBM Quantum rechazado (%s): %s",
                    getattr(provider_loader, "__name__", repr(provider_loader)),
                    error,
                )
                continue
            except Exception as error:  # pragma: no cover - error inesperado
                LOGGER.exception("Error inesperado al inicializar proveedor IBM Quantum")
                raise IBMQuantumInterfaceError(
                    "Error inesperado al inicializar proveedor IBM Quantum"
                ) from error

        if not self._local_fallback:
            raise IBMQuantumInterfaceError(
                "No fue posible conectar con un backend IBM Quantum"
            ) from last_error

        backend = self._resolve_local_backend(imports)
        if backend is None:
            raise IBMQuantumInterfaceError(
                "No hay backends locales disponibles para realizar la validación"
            ) from last_error

        self._backend = backend
        return backend

    def _resolve_local_backend(self, imports: Dict[str, Any]) -> Any | None:
        backend_errors = self._BACKEND_ERRORS + (LookupError, KeyError, AttributeError)
        for loader in imports["local_backends"]:
            try:
                aer_module = loader()
            except backend_errors as error:  # pragma: no cover - depende del entorno local
                LOGGER.warning("Backend local inoperativo al cargar el módulo: %s", error)
                continue
            except Exception as error:  # pragma: no cover - error inesperado
                LOGGER.exception("Error inesperado al cargar backend local")
                raise IBMQuantumInterfaceError(
                    "Error inesperado al cargar un backend local"
                ) from error

            for candidate in ("aer_simulator", "qasm_simulator", "statevector_simulator"):
                try:
                    return aer_module.get_backend(candidate)
                except backend_errors as error:  # pragma: no cover - depende del backend
                    LOGGER.debug(
                        "Backend local %s no disponible en %s: %s",
                        candidate,
                        getattr(aer_module, "__name__", type(aer_module).__name__),
                        error,
                    )
                    continue
                except Exception as error:  # pragma: no cover - error inesperado
                    LOGGER.exception(
                        "Error inesperado al obtener el backend local %s",
                        candidate,
                    )
                    raise IBMQuantumInterfaceError(
                        f"Error inesperado al obtener el backend local {candidate}"
                    ) from error
        return None

    # ---------------------------------------------------------------
    # Ejecución de validaciones
    # ---------------------------------------------------------------
    def _build_circuit(self, packet: QuantumPacket) -> Any:
        imports = self._load_qiskit()
        QuantumCircuit = imports["QuantumCircuit"]
        circuit = QuantumCircuit(1, 1)

        # Convertimos la coherencia en un ángulo de rotación.
        angle = max(0.0, min(1.0, packet.coherence)) * 3.141592653589793
        circuit.ry(2 * angle, 0)
        circuit.measure(0, 0)
        return circuit

    def validate_packet(
        self,
        packet: QuantumPacket,
        shots: int = 512,
        threshold: float = 0.6,
        transpile_kwargs: Dict[str, Any] | None = None,
    ) -> ValidationResult:
        """Ejecuta una validación del paquete en el backend seleccionado."""

        backend = self._resolve_backend()
        imports = self._load_qiskit()
        circuit = self._build_circuit(packet)

        transpile_kwargs = transpile_kwargs or {}
        transpiled = imports["transpile"](circuit, backend, **transpile_kwargs)

        try:
            job = backend.run(transpiled, shots=shots)
            result = job.result()
            counts = result.get_counts()
        except Exception as exc:  # pragma: no cover - diferencias entre backends
            raise IBMQuantumInterfaceError(
                "El backend no devolvió resultados válidos"
            ) from exc

        zero_counts = counts.get("0", 0)
        fidelity = zero_counts / shots if shots else 0.0
        accepted = fidelity >= threshold

        metadata: Dict[str, Any] = {
            "board_metadata": packet.metadata,
            "energy_ev": packet.energy_ev,
        }

        return ValidationResult(
            backend_name=getattr(backend, "name", lambda: str(backend))(),
            counts=dict(counts),
            fidelity=fidelity,
            threshold=threshold,
            accepted=accepted,
            metadata=metadata,
        )

    # ---------------------------------------------------------------
    # Utilidades
    # ---------------------------------------------------------------
    def clear_cache(self) -> None:
        """Olvida el backend actual para forzar una nueva conexión."""

        self._backend = None

    def backend_name(self) -> str | None:
        if self._backend is None:
            return self._backend_name
        backend = self._backend
        name_attr = getattr(backend, "name", None)
        if callable(name_attr):
            try:
                return name_attr()  # type: ignore[no-any-return]
            except Exception:  # pragma: no cover - compatibilidad
                return str(backend)
        if name_attr is not None:
            return str(name_attr)
        return str(backend)
