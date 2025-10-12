"""Primitivas criptográficas leptónicas y registros hashados."""

from __future__ import annotations

import hashlib
import secrets
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Sequence


MERKLE_EMPTY_ROOT = "0" * 64


def _normalize_float(value: float) -> str:
    """Normaliza un flotante para obtener representaciones consistentes."""

    return f"{value:.12f}".rstrip("0").rstrip(".")


def _hash_bytes(*parts: bytes) -> str:
    """Calcula SHA3-256 sobre los fragmentos concatenados."""

    digest = hashlib.sha3_256()
    for part in parts:
        digest.update(part)
    return digest.hexdigest()


def generate_energy_token(
    node_id: str,
    energy_ev: float,
    coherence: float,
    *,
    nonce: bytes | None = None,
) -> str:
    """Genera un token energético único para el nodo indicado.

    El token incorpora la energía instantánea del nodo, su coherencia y un
    ``nonce`` aleatorio de alta entropía. Estos elementos se combinan mediante
    ``blake2b`` con personalización específica para el dominio leptónico.
    """

    if nonce is None:
        nonce = secrets.token_bytes(16)
    context = "|".join(
        (
            node_id,
            _normalize_float(energy_ev),
            _normalize_float(coherence),
        )
    ).encode("utf-8")
    hasher = hashlib.blake2b(person=b"LEPTONIC", digest_size=32)
    hasher.update(context)
    hasher.update(nonce)
    return hasher.hexdigest()


@dataclass(frozen=True)
class QuantumSignature:
    """Representa la firma cuántica simulada asociada a un paquete."""

    payload_hash: str
    signature: str
    energy_token: str
    issued_at: datetime
    coherence_window: tuple[float, float]


def simulate_quantum_signature(
    payload: bytes,
    *,
    node_id: str,
    secret: str,
    energy_ev: float,
    coherence: float,
    nonce: bytes | None = None,
    issued_at: datetime | None = None,
) -> QuantumSignature:
    """Crea una firma cuántica determinística a partir del contexto dado.

    Aunque no se apoya en hardware cuántico real, la construcción mezcla el
    ``payload`` con la energía instantánea, un secreto compartido y una ventana
    de coherencia. El resultado es una firma estable que puede validarse al
    recrear las condiciones originales.
    """

    if issued_at is None:
        issued_at = datetime.now(timezone.utc)
    energy_token = generate_energy_token(
        node_id, energy_ev, coherence, nonce=nonce
    )
    payload_hash = _hash_bytes(payload)
    coherence_window = (
        max(0.0, round(coherence - 0.05, 6)),
        min(1.0, round(coherence + 0.05, 6)),
    )
    signature_context = "|".join(
        (
            payload_hash,
            node_id,
            energy_token,
            _normalize_float(energy_ev),
            _normalize_float(coherence),
            issued_at.isoformat(),
        )
    ).encode("utf-8")
    signer = hashlib.shake_256()
    signer.update(signature_context)
    signer.update(secret.encode("utf-8"))
    signature = signer.hexdigest(128)
    return QuantumSignature(
        payload_hash=payload_hash,
        signature=signature,
        energy_token=energy_token,
        issued_at=issued_at,
        coherence_window=coherence_window,
    )


@dataclass(frozen=True)
class NodeCoherenceState:
    """Estado energético y de coherencia para un nodo participante."""

    node_id: str
    energy_ev: float
    coherence: float
    energy_token: str


class CoherenceSecureChannel:
    """Coordina canales seguros basados en sincronía energética."""

    def __init__(self, *, energy_tolerance: float = 0.25, coherence_tolerance: float = 0.05) -> None:
        self.energy_tolerance = energy_tolerance
        self.coherence_tolerance = coherence_tolerance
        self._established: dict[frozenset[str], str] = {}

    def _is_synchronized(self, one: NodeCoherenceState, two: NodeCoherenceState) -> bool:
        energy_diff = abs(one.energy_ev - two.energy_ev)
        coherence_diff = abs(one.coherence - two.coherence)
        return energy_diff <= self.energy_tolerance and coherence_diff <= self.coherence_tolerance

    def establish(self, one: NodeCoherenceState, two: NodeCoherenceState) -> str | None:
        """Intenta establecer un canal seguro entre dos nodos.

        Devuelve el token de canal generado cuando la sincronización energética
        es suficiente. En caso contrario retorna ``None``.
        """

        if not self._is_synchronized(one, two):
            return None
        pair_key = frozenset({one.node_id, two.node_id})
        shared_material = "|".join(
            sorted((one.energy_token, two.energy_token))
        ).encode("utf-8")
        channel_token = _hash_bytes(
            shared_material,
            _normalize_float((one.energy_ev + two.energy_ev) / 2).encode("utf-8"),
            _normalize_float((one.coherence + two.coherence) / 2).encode("utf-8"),
        )
        self._established[pair_key] = channel_token
        return channel_token

    def can_decode(self, node_a: str, node_b: str, token: str) -> bool:
        """Valida si dos nodos pueden decodificar usando el token indicado."""

        pair_key = frozenset({node_a, node_b})
        stored = self._established.get(pair_key)
        return stored is not None and secrets.compare_digest(stored, token)


class SignatureMerkleLog:
    """Registro trazable de firmas basado en un árbol de Merkle."""

    def __init__(self) -> None:
        self._leaves: list[str] = []

    def register(self, signature: QuantumSignature) -> str:
        """Agrega una firma al registro y devuelve la raíz actual."""

        leaf = _hash_bytes(
            signature.signature.encode("utf-8"),
            signature.energy_token.encode("utf-8"),
            signature.payload_hash.encode("utf-8"),
        )
        self._leaves.append(leaf)
        return self.root()

    def root(self) -> str:
        """Calcula la raíz del árbol de Merkle con las hojas actuales."""

        if not self._leaves:
            return MERKLE_EMPTY_ROOT
        level: Sequence[str] = self._leaves
        while len(level) > 1:
            level = _next_merkle_level(level)
        return level[0]

    def proof(self, index: int) -> list[str]:
        """Devuelve el camino de Merkle para la hoja indicada."""

        if index < 0 or index >= len(self._leaves):
            raise IndexError("Índice de hoja fuera de rango")
        path: list[str] = []
        level = list(self._leaves)
        idx = index
        while len(level) > 1:
            if len(level) % 2 == 1:
                level.append(level[-1])
            sibling_index = idx ^ 1
            path.append(level[sibling_index])
            idx //= 2
            level = _next_merkle_level(level)
        return path


def _next_merkle_level(level: Sequence[str]) -> list[str]:
    output: list[str] = []
    items = list(level)
    if len(items) % 2 == 1:
        items.append(items[-1])
    for idx in range(0, len(items), 2):
        left, right = items[idx], items[idx + 1]
        combined = _hash_bytes(left.encode("utf-8"), right.encode("utf-8"))
        output.append(combined)
    return output


__all__ = [
    "CoherenceSecureChannel",
    "MERKLE_EMPTY_ROOT",
    "NodeCoherenceState",
    "QuantumSignature",
    "SignatureMerkleLog",
    "generate_energy_token",
    "simulate_quantum_signature",
]
