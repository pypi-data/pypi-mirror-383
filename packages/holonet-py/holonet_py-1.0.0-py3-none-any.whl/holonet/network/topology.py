"""Topologías básicas de red muónica."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

from holonet.core.nodes import HoloNode, NodeRegistry

try:  # pragma: no cover - la importación se valida en pruebas
    import yaml
except Exception:  # pragma: no cover - PyYAML es opcional en ejecución
    yaml = None


@dataclass
class NetworkTopology:
    """Representa conexiones lógicas entre nodos holográficos."""

    registry: NodeRegistry
    links: Dict[str, List[str]] = field(default_factory=dict)

    def connect(self, source_id: str, target_id: str) -> None:
        self.links.setdefault(source_id, []).append(target_id)

    def neighbors(self, identifier: str) -> List[HoloNode]:
        return [self.registry.get(node_id) for node_id in self.links.get(identifier, []) if self.registry.get(node_id)]

    def summary(self) -> List[Tuple[str, List[str]]]:
        return [(source, targets.copy()) for source, targets in self.links.items()]

    def to_dict(self) -> Dict[str, List[str]]:
        """Serializa la topología a un diccionario simple."""

        return {source: targets.copy() for source, targets in self.links.items()}

    def save_to_file(self, path: str | Path) -> None:
        """Guarda los enlaces de la topología en formato JSON o YAML."""

        file_path = Path(path)
        data = {"links": self.to_dict()}
        if file_path.suffix.lower() in {".yaml", ".yml"}:
            if yaml is None:
                raise RuntimeError("PyYAML no está disponible para exportar a YAML")
            with file_path.open("w", encoding="utf-8") as handler:
                yaml.safe_dump(data, handler, allow_unicode=True, sort_keys=True)
        else:
            with file_path.open("w", encoding="utf-8") as handler:
                json.dump(data, handler, ensure_ascii=False, indent=2)

    @classmethod
    def load_from_file(cls, registry: NodeRegistry, path: str | Path) -> NetworkTopology:
        """Crea una topología a partir de un archivo persistido."""

        file_path = Path(path)
        if not file_path.exists():
            raise FileNotFoundError(f"No se encontró la topología en {file_path}")

        if file_path.suffix.lower() in {".yaml", ".yml"}:
            if yaml is None:
                raise RuntimeError("PyYAML no está disponible para importar YAML")
            with file_path.open("r", encoding="utf-8") as handler:
                raw_data = yaml.safe_load(handler) or {}
        else:
            with file_path.open("r", encoding="utf-8") as handler:
                raw_data = json.load(handler)

        links_data = raw_data.get("links", {}) if isinstance(raw_data, dict) else {}
        topology = cls(registry)
        for source, targets in _normalize_links(links_data).items():
            topology.links[source] = targets
        return topology


def _normalize_links(data: Dict[str, Iterable[str]]) -> Dict[str, List[str]]:
    """Normaliza estructuras de enlaces arbitrarias a listas de cadenas."""

    normalized: Dict[str, List[str]] = {}
    for source, targets in data.items():
        if targets is None:
            normalized[source] = []
            continue
        if isinstance(targets, str):
            normalized[source] = [targets]
            continue
        normalized[source] = [str(target) for target in list(targets)]
    return normalized


def bootstrap_topology(
    registry: NodeRegistry, path: str | Path | None = None
) -> NetworkTopology:
    """Carga una topología persistida si existe, de lo contrario crea una vacía."""

    file_path = Path(path) if path is not None else DEFAULT_TOPOLOGY_PATH
    if file_path.exists():
        return NetworkTopology.load_from_file(registry, file_path)
    return NetworkTopology(registry)


DEFAULT_TOPOLOGY_PATH = Path("network_topology.yaml")

