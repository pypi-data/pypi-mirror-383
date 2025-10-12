"""Topología con ajustes dinámicos."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from holonet.core.nodes import HoloNode
from holonet.network.metrics import CompositeMetric
from holonet.simulation.adaptive_controller import AdaptiveController


@dataclass
class AdaptiveTopology:
    controller: AdaptiveController
    weights: Dict[str, float] = field(default_factory=dict)

    def adjust(self, node: HoloNode, metric: CompositeMetric | float) -> None:
        if isinstance(metric, CompositeMetric):
            value = metric.normalized
        else:
            value = metric
        self.weights[node.identifier] = value

    def preferred_nodes(self) -> List[str]:
        return sorted(self.weights, key=self.weights.get, reverse=True)

