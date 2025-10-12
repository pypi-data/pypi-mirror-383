"""Herramientas de optimización y aprendizaje para saltos MTQ."""
from __future__ import annotations

from dataclasses import dataclass, field
import math
from typing import Dict, Iterable, MutableSequence, Optional, Sequence

import numpy as np

from .quantum_packet import QuantumPacket


@dataclass(frozen=True)
class TrainingSample:
    """Observación de un salto MTQ útil para entrenar modelos."""

    energy_ev: float
    coherence: float
    latency: float
    success: bool
    noise: float = 0.0

    def as_features(self) -> np.ndarray:
        """Transforma la muestra en un vector de características numéricas."""

        return np.array([self.energy_ev, self.coherence, self.latency, self.noise], dtype=np.float64)

    def label(self) -> float:
        """Devuelve la etiqueta de éxito como valor flotante."""

        return 1.0 if self.success else 0.0


@dataclass
class OptimizedParameters:
    """Resultado del entrenamiento para energía/coherencia óptimas."""

    target_energy_ev: float
    target_coherence: float
    energy_spread: float
    coherence_spread: float

    def apply(self, packet: QuantumPacket) -> QuantumPacket:
        """Ajusta la coherencia del paquete con los valores aprendidos."""

        delta = self.target_coherence - packet.coherence
        packet.update_coherence(delta)
        packet.metadata.setdefault("optimizer", {})
        packet.metadata["optimizer"]["target_energy_ev"] = self.target_energy_ev
        packet.metadata["optimizer"]["coherence_spread"] = self.coherence_spread
        return packet


class SuccessPredictor:
    """Interfaz mínima para predictores de éxito MTQ."""

    def fit(self, samples: Sequence[TrainingSample]) -> None:  # pragma: no cover - interfaz
        raise NotImplementedError

    def predict_proba(self, features: Sequence[float]) -> float:  # pragma: no cover - interfaz
        raise NotImplementedError

    def predict(self, features: Sequence[float]) -> bool:
        """Clasifica el salto como exitoso o no."""

        return self.predict_proba(features) >= 0.5


@dataclass
class BaselineSuccessModel(SuccessPredictor):
    """Modelo trivial que devuelve una probabilidad constante."""

    probability: float = 0.5

    def fit(self, samples: Sequence[TrainingSample]) -> None:
        if samples:
            labels = [sample.label() for sample in samples]
            self.probability = float(sum(labels) / len(labels))

    def predict_proba(self, features: Sequence[float]) -> float:
        return self.probability


class LogisticSuccessModel(SuccessPredictor):
    """Regresión logística ligera optimizada mediante gradiente."""

    def __init__(self, *, learning_rate: float = 0.1, epochs: int = 400) -> None:
        self.learning_rate = learning_rate
        self.epochs = epochs
        self.weights: Optional[np.ndarray] = None
        self.mean_: Optional[np.ndarray] = None
        self.std_: Optional[np.ndarray] = None

    def fit(self, samples: Sequence[TrainingSample]) -> None:
        if not samples:
            self.weights = None
            return
        features = np.stack([sample.as_features() for sample in samples])
        labels = np.array([sample.label() for sample in samples])
        self.mean_ = features.mean(axis=0)
        self.std_ = features.std(axis=0)
        self.std_[self.std_ == 0.0] = 1.0
        normalized = (features - self.mean_) / self.std_
        augmented = np.concatenate([normalized, np.ones((normalized.shape[0], 1))], axis=1)
        self.weights = np.zeros(augmented.shape[1], dtype=np.float64)
        for _ in range(self.epochs):
            logits = augmented @ self.weights
            predictions = 1.0 / (1.0 + np.exp(-logits))
            gradient = augmented.T @ (predictions - labels) / len(samples)
            if np.linalg.norm(gradient) < 1e-6:
                break
            self.weights -= self.learning_rate * gradient

    def predict_proba(self, features: Sequence[float]) -> float:
        if self.weights is None or self.mean_ is None or self.std_ is None:
            return 0.5
        vector = np.asarray(features, dtype=np.float64)
        normalized = (vector - self.mean_) / self.std_
        augmented = np.append(normalized, 1.0)
        logit = float(augmented @ self.weights)
        return 1.0 / (1.0 + math.exp(-logit))


class DecisionTreeSuccessModel(SuccessPredictor):
    """Árbol de decisión muy ligero (stump) para clasificación binaria."""

    def __init__(self) -> None:
        self.feature_index: Optional[int] = None
        self.threshold: float = 0.0
        self.left_prob: float = 0.5
        self.right_prob: float = 0.5
        self.default_prob: float = 0.5

    def fit(self, samples: Sequence[TrainingSample]) -> None:
        if not samples:
            self.feature_index = None
            self.default_prob = 0.5
            return
        features = np.stack([sample.as_features() for sample in samples])
        labels = np.array([sample.label() for sample in samples])
        self.default_prob = float(labels.mean()) if labels.size else 0.5
        best_impurity = math.inf
        best_feature: Optional[int] = None
        best_threshold = 0.0
        best_left_prob = self.default_prob
        best_right_prob = self.default_prob
        num_features = features.shape[1]
        for feature_idx in range(num_features):
            values = np.unique(features[:, feature_idx])
            if values.size <= 1:
                continue
            candidates = (values[:-1] + values[1:]) / 2.0
            for threshold in candidates:
                mask = features[:, feature_idx] <= threshold
                left_labels = labels[mask]
                right_labels = labels[~mask]
                if left_labels.size == 0 or right_labels.size == 0:
                    continue
                impurity = (
                    left_labels.size * self._gini(left_labels)
                    + right_labels.size * self._gini(right_labels)
                ) / labels.size
                if impurity < best_impurity:
                    best_impurity = impurity
                    best_feature = feature_idx
                    best_threshold = float(threshold)
                    best_left_prob = float(left_labels.mean())
                    best_right_prob = float(right_labels.mean())
        self.feature_index = best_feature
        if self.feature_index is None:
            return
        self.threshold = best_threshold
        self.left_prob = best_left_prob
        self.right_prob = best_right_prob

    def predict_proba(self, features: Sequence[float]) -> float:
        if self.feature_index is None:
            return self.default_prob
        value = float(features[self.feature_index])
        if value <= self.threshold:
            return self.left_prob
        return self.right_prob

    @staticmethod
    def _gini(labels: np.ndarray) -> float:
        if labels.size == 0:
            return 0.0
        probability = float(labels.mean())
        return 2.0 * probability * (1.0 - probability)


class LightweightNeuralPredictor(SuccessPredictor):
    """Red neuronal diminuta (una capa oculta) entrenada con gradiente."""

    def __init__(
        self,
        *,
        hidden_units: int = 6,
        learning_rate: float = 0.05,
        epochs: int = 600,
        seed: Optional[int] = None,
    ) -> None:
        self.hidden_units = hidden_units
        self.learning_rate = learning_rate
        self.epochs = epochs
        self.seed = seed
        self.mean_: Optional[np.ndarray] = None
        self.std_: Optional[np.ndarray] = None
        self.w1: Optional[np.ndarray] = None
        self.b1: Optional[np.ndarray] = None
        self.w2: Optional[np.ndarray] = None
        self.b2: Optional[np.ndarray] = None

    def fit(self, samples: Sequence[TrainingSample]) -> None:
        if not samples:
            self.w1 = None
            return
        rng = np.random.default_rng(self.seed)
        features = np.stack([sample.as_features() for sample in samples])
        labels = np.array([sample.label() for sample in samples]).reshape(-1, 1)
        self.mean_ = features.mean(axis=0)
        self.std_ = features.std(axis=0)
        self.std_[self.std_ == 0.0] = 1.0
        normalized = (features - self.mean_) / self.std_
        input_dim = normalized.shape[1]
        self.w1 = rng.normal(scale=0.2, size=(input_dim, self.hidden_units))
        self.b1 = np.zeros((1, self.hidden_units))
        self.w2 = rng.normal(scale=0.2, size=(self.hidden_units, 1))
        self.b2 = np.zeros((1, 1))
        for _ in range(self.epochs):
            hidden = np.tanh(normalized @ self.w1 + self.b1)
            logits = hidden @ self.w2 + self.b2
            predictions = 1.0 / (1.0 + np.exp(-logits))
            error = predictions - labels
            grad_w2 = hidden.T @ error / labels.shape[0]
            grad_b2 = error.mean(axis=0, keepdims=True)
            grad_hidden = (error @ self.w2.T) * (1.0 - hidden**2)
            grad_w1 = normalized.T @ grad_hidden / labels.shape[0]
            grad_b1 = grad_hidden.mean(axis=0, keepdims=True)
            max_grad = max(
                float(np.max(np.abs(grad_w2))),
                float(np.max(np.abs(grad_w1))),
            )
            if max_grad < 1e-6:
                break
            self.w2 -= self.learning_rate * grad_w2
            self.b2 -= self.learning_rate * grad_b2
            self.w1 -= self.learning_rate * grad_w1
            self.b1 -= self.learning_rate * grad_b1

    def predict_proba(self, features: Sequence[float]) -> float:
        if (
            self.w1 is None
            or self.b1 is None
            or self.w2 is None
            or self.b2 is None
            or self.mean_ is None
            or self.std_ is None
        ):
            return 0.5
        vector = np.asarray(features, dtype=np.float64)
        normalized = (vector - self.mean_) / self.std_
        hidden = np.tanh(normalized @ self.w1 + self.b1)
        logits = hidden @ self.w2 + self.b2
        probability = 1.0 / (1.0 + np.exp(-logits))
        return float(probability.squeeze())


def _weighted_average(values: Iterable[float], weights: Iterable[float]) -> float:
    values_list = list(values)
    weights_list = list(weights)
    denominator = sum(weights_list)
    if denominator == 0.0:
        denominator = float(len(values_list)) or 1.0
        weights_list = [1.0] * len(values_list)
    return sum(value * weight for value, weight in zip(values_list, weights_list)) / denominator


@dataclass
class MTQOptimizer:
    """Orquestador del aprendizaje de parámetros MTQ."""

    samples: MutableSequence[TrainingSample] = field(default_factory=list)
    _optimized_parameters: Optional[OptimizedParameters] = field(default=None, init=False, repr=False)
    _predictor_cache: Dict[str, SuccessPredictor] = field(default_factory=dict, init=False, repr=False)

    def add_sample(self, sample: TrainingSample) -> None:
        """Añade una muestra y marca los modelos como desactualizados."""

        self.samples.append(sample)
        self._optimized_parameters = None
        self._predictor_cache.clear()

    def extend(self, samples: Iterable[TrainingSample]) -> None:
        for sample in samples:
            self.add_sample(sample)

    def has_samples(self) -> bool:
        return bool(self.samples)

    def optimal_parameters(self) -> OptimizedParameters:
        """Calcula (o reutiliza) los parámetros óptimos."""

        if self._optimized_parameters is not None:
            return self._optimized_parameters
        if not self.samples:
            self._optimized_parameters = OptimizedParameters(0.0, 0.5, 0.0, 0.25)
            return self._optimized_parameters
        successes = [sample for sample in self.samples if sample.success]
        reference = successes or list(self.samples)
        energies = [sample.energy_ev for sample in reference]
        coherences = [sample.coherence for sample in reference]
        latencies = [sample.latency for sample in reference]
        energy_weights = [1.0 / (1.0 + latency) for latency in latencies]
        coherence_weights = [1.0 + (1.0 - min(1.0, latency)) for latency in latencies]
        target_energy = _weighted_average(energies, energy_weights)
        target_coherence = _weighted_average(coherences, coherence_weights)
        energy_spread = float(np.std(energies)) if energies else 0.0
        coherence_spread = float(np.std(coherences)) if coherences else 0.0
        self._optimized_parameters = OptimizedParameters(
            target_energy_ev=target_energy,
            target_coherence=target_coherence,
            energy_spread=energy_spread,
            coherence_spread=coherence_spread,
        )
        return self._optimized_parameters

    def success_predictor(self, model: str = "logistic") -> SuccessPredictor:
        """Obtiene un predictor entrenado con el modelo indicado."""

        key = model.lower()
        predictor = self._predictor_cache.get(key)
        if predictor is not None:
            return predictor
        predictor = self._build_predictor(key)
        self._predictor_cache[key] = predictor
        return predictor

    def predict_success(self, features: Sequence[float], model: str = "logistic") -> float:
        """Conveniencia para obtener la probabilidad de éxito."""

        predictor = self.success_predictor(model=model)
        return float(predictor.predict_proba(features))

    def _build_predictor(self, model: str) -> SuccessPredictor:
        usable_samples = list(self.samples)
        if not usable_samples:
            return BaselineSuccessModel()
        distinct_labels = {sample.success for sample in usable_samples}
        if len(distinct_labels) == 1:
            predictor = BaselineSuccessModel()
            predictor.fit(usable_samples)
            return predictor
        if model in {"logistic", "logit"}:
            predictor = LogisticSuccessModel()
        elif model in {"tree", "decision-tree", "stump"}:
            predictor = DecisionTreeSuccessModel()
        elif model in {"nn", "neural", "neural-network"}:
            predictor = LightweightNeuralPredictor()
        else:
            raise ValueError(f"Modelo de predictor desconocido: {model}")
        predictor.fit(usable_samples)
        return predictor


def build_optimizer(samples: Optional[Iterable[TrainingSample]] = None) -> MTQOptimizer:
    """Factoría de comodidad para crear un optimizador pre-cargado."""

    optimizer = MTQOptimizer()
    if samples is not None:
        optimizer.extend(samples)
    return optimizer
