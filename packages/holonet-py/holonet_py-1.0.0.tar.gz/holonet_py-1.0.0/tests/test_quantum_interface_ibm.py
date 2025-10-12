"""Pruebas para el manejo robusto de errores en IBMQuantumInterface."""
from __future__ import annotations

import pytest

from holonet.mtq.quantum_interface_ibm import IBMQuantumInterface, IBMQuantumInterfaceError


def test_resolve_backend_propagates_account_errors(monkeypatch: pytest.MonkeyPatch) -> None:
    interface = IBMQuantumInterface(token="bad-token", local_fallback=False)

    def failing_loader() -> None:
        raise IBMQuantumInterfaceError(
            "No se pudo habilitar la cuenta IBMQ con el token proporcionado"
        )

    monkeypatch.setattr(
        interface,
        "_load_qiskit",
        lambda: {"providers": [failing_loader], "local_backends": []},
        raising=False,
    )

    with pytest.raises(IBMQuantumInterfaceError) as exc:
        interface._resolve_backend()

    assert "No se pudo habilitar la cuenta IBMQ" in str(exc.value)


def test_resolve_backend_reports_local_backend_failures(monkeypatch: pytest.MonkeyPatch) -> None:
    interface = IBMQuantumInterface(local_fallback=True)

    def local_loader() -> None:
        raise LookupError("sin backends locales")

    monkeypatch.setattr(
        interface,
        "_load_qiskit",
        lambda: {"providers": [], "local_backends": [local_loader]},
        raising=False,
    )

    with pytest.raises(IBMQuantumInterfaceError) as exc:
        interface._resolve_backend()

    assert "No hay backends locales disponibles" in str(exc.value)
