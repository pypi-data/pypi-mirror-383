"""Pruebas del módulo de modulación."""
from pathlib import Path

import pytest
import yaml

from holonet.modulation.patterns import PatternLibrary, custom_pattern, generate_sine_pattern


def test_generate_sine_pattern():
    pattern = generate_sine_pattern(samples=3, amplitude=1.0, frequency=0.5)
    assert pattern.name == "seno_3"
    assert len(list(pattern.sequence)) == 3


def test_pattern_library_registration():
    library = PatternLibrary(patterns=[])
    sine = generate_sine_pattern(2, 1.0, 0.1)
    library.register(sine)
    assert library.find(sine.name) is sine


def test_custom_pattern():
    pattern = custom_pattern("lineal", lambda size: range(size), 3)
    assert pattern.to_signal(1.0).frequencies == [0, 1, 2]


def test_pattern_library_load_from_yaml():
    yaml_path = Path(__file__).resolve().parents[1] / "docs/examples/patrones.yaml"
    library = PatternLibrary.load_from_yaml(yaml_path)

    assert len(library.patterns) == 2
    pulso = library.find("pulso_basico")
    assert list(pulso.sequence) == [0.1, 0.1, 0.1, 0.1]
    escalera = library.find("escalera_incremental")
    assert escalera.description == "Incremento lineal para calibrar densidad."
    assert escalera.to_signal(0.8).frequencies[-1] == 2.0


def test_pattern_library_rejects_invalid_sequence(tmp_path: Path) -> None:
    data = {
        "patterns": [
            {
                "name": "defectuoso",
                "sequence": [1.0, "no es numero"],
            }
        ]
    }
    yaml_path = tmp_path / "patterns.yaml"
    yaml_path.write_text(yaml.safe_dump(data), encoding="utf-8")

    with pytest.raises(ValueError, match="elemento 1"):
        PatternLibrary.load_from_yaml(yaml_path)


def test_pattern_library_casts_numeric_strings(tmp_path: Path) -> None:
    yaml_path = tmp_path / "patterns.yaml"
    yaml_path.write_text(
        yaml.safe_dump(
            {
                "patterns": [
                    {
                        "name": "cadena",
                        "sequence": ["1", "2.5", 3],
                        "description": "mezcla",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    library = PatternLibrary.load_from_yaml(yaml_path)
    pattern = library.find("cadena")
    assert list(pattern.sequence) == [1.0, 2.5, 3.0]

