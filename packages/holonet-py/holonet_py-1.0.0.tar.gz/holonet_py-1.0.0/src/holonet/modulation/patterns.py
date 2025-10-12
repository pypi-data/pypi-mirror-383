"""Herramientas para construir patrones leptónicos."""
from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, List

import yaml

from holonet.core.packets import LeptonicPattern


@dataclass
class PatternLibrary:
    """Gestor simple de patrones prediseñados."""

    patterns: List[LeptonicPattern]

    @classmethod
    def load_from_yaml(cls, path: str | Path) -> PatternLibrary:
        """Construye una biblioteca de patrones a partir de un archivo YAML."""

        file_path = Path(path)
        raw_data = yaml.safe_load(file_path.read_text(encoding="utf-8"))

        if isinstance(raw_data, dict):
            patterns_data = raw_data.get("patterns")
            if patterns_data is None:
                raise ValueError("El archivo YAML debe contener la clave 'patterns'.")
        elif isinstance(raw_data, list):
            patterns_data = raw_data
        else:
            raise TypeError("El archivo YAML debe describir una lista o un diccionario de patrones.")

        patterns: List[LeptonicPattern] = []
        for entry in patterns_data:
            if not isinstance(entry, dict):
                raise TypeError("Cada patrón debe representarse como un objeto mapeado.")

            try:
                name = entry["name"]
                sequence = entry["sequence"]
            except KeyError as exc:
                raise ValueError("Cada patrón debe incluir 'name' y 'sequence'.") from exc

            description = entry.get("description", "")
            if not isinstance(sequence, Iterable) or isinstance(sequence, (str, bytes)):
                raise TypeError("'sequence' debe ser una colección iterable de valores numéricos.")

            sanitized_sequence: list[float] = []
            for index, value in enumerate(sequence):
                try:
                    sanitized_sequence.append(float(value))
                except (TypeError, ValueError) as exc:
                    raise ValueError(
                        f"El elemento {index} de 'sequence' no es un número válido."
                    ) from exc

            patterns.append(
                LeptonicPattern(
                    name=name,
                    sequence=sanitized_sequence,
                    description=description,
                )
            )

        return cls(patterns=patterns)

    def find(self, name: str) -> LeptonicPattern:
        for pattern in self.patterns:
            if pattern.name == name:
                return pattern
        raise KeyError(name)

    def register(self, pattern: LeptonicPattern) -> None:
        self.patterns.append(pattern)


def generate_sine_pattern(samples: int, amplitude: float, frequency: float) -> LeptonicPattern:
    import math

    sequence = [amplitude * math.sin(frequency * i) for i in range(samples)]
    return LeptonicPattern(name=f"seno_{samples}", sequence=sequence, description="Patrón senoide básico")


def custom_pattern(name: str, generator: Callable[[int], Iterable[float]], size: int) -> LeptonicPattern:
    return LeptonicPattern(name=name, sequence=list(generator(size)))

