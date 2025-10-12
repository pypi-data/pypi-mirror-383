"""Visualización interactiva de entornos MTQ usando Plotly."""
from __future__ import annotations

import math
from collections import defaultdict
from typing import Iterable, List, Sequence

from .mtq_env import MTQEnvironment, MTQEvent


class PlotlyUnavailableError(RuntimeError):
    """Se lanza cuando Plotly no está disponible en el entorno de ejecución."""


def _require_plotly():  # type: ignore[override]
    try:
        import plotly.graph_objects as go  # type: ignore
    except ModuleNotFoundError as exc:  # pragma: no cover - depende del entorno
        raise PlotlyUnavailableError(
            "Plotly no está instalado. Añádelo a tus dependencias para habilitar la "
            "visualización interactiva."
        ) from exc
    return go


def build_network_figure(environment: MTQEnvironment, *, show_history: bool = True):
    """Construye una figura Plotly que resume nodos, enlaces y coherencia."""

    go = _require_plotly()

    node_snapshot = environment.node_snapshot()
    if not node_snapshot:
        raise ValueError("El entorno no contiene nodos registrados")

    node_ids: List[str] = list(node_snapshot.keys())
    angle_step = 2 * math.pi / max(1, len(node_ids))
    positions = {
        node_id: (
            math.cos(index * angle_step),
            math.sin(index * angle_step),
        )
        for index, node_id in enumerate(node_ids)
    }

    history = environment.history if show_history else []
    coherence_by_node = defaultdict(list)
    for event in history:
        coherence_by_node[event.source].append(event.final_coherence)

    node_colors = [
        sum(values) / len(values) if values else node_snapshot[node_id]["stability_index"]
        for node_id, values in (
            (node_id, coherence_by_node.get(node_id, [])) for node_id in node_ids
        )
    ]

    node_sizes = [
        max(12.0, node_snapshot[node_id]["temperature_k"]) * 2
        for node_id in node_ids
    ]

    link_snapshot = environment.link_snapshot()
    edge_x: List[float] = []
    edge_y: List[float] = []
    edge_text: List[str] = []
    for link in link_snapshot:
        start = positions[link["source"]]
        end = positions[link["target"]]
        edge_x.extend([start[0], end[0], None])
        edge_y.extend([start[1], end[1], None])
        edge_text.append(
            f"{link['source']}→{link['target']}<br>fidelidad: {link['fidelity']:.2f}<br>"
            f"congestión: {link['congestion']:.2f}"
        )

    edge_trace = go.Scatter(
        x=edge_x,
        y=edge_y,
        mode="lines",
        line=dict(width=2, color="rgba(100, 100, 100, 0.6)"),
        hoverinfo="text",
        text=edge_text,
    )

    node_trace = go.Scatter(
        x=[positions[node_id][0] for node_id in node_ids],
        y=[positions[node_id][1] for node_id in node_ids],
        mode="markers+text",
        marker=dict(
            size=node_sizes,
            color=node_colors,
            colorscale="Viridis",
            showscale=True,
            colorbar=dict(title="Coherencia media"),
        ),
        text=node_ids,
        textposition="top center",
        hovertext=[
            (
                f"Nodo {node_id}<br>Temperatura: {node_snapshot[node_id]['temperature_k']:.2f}K"
                f"<br>Entropía: {node_snapshot[node_id]['entanglement_entropy']:.2f}"
                f"<br>Estabilidad: {node_snapshot[node_id]['stability_index']:.2f}"
            )
            for node_id in node_ids
        ],
        hoverinfo="text",
    )

    layout = go.Layout(
        title="Estado dinámico de la red MTQ",
        showlegend=False,
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        margin=dict(l=20, r=20, t=60, b=20),
        plot_bgcolor="white",
    )

    figure = go.Figure(data=[edge_trace, node_trace], layout=layout)
    if history:
        figure.add_annotation(
            xref="paper",
            yref="paper",
            x=0.01,
            y=0.01,
            text=f"Eventos registrados: {len(history)}",
            showarrow=False,
            font=dict(size=12),
        )
    return figure


def build_timeline_figure(
    events: Sequence[MTQEvent] | Iterable[MTQEvent], *, metric: str = "final_coherence"
):
    """Crea una figura temporal de métricas MTQ a partir de eventos."""

    go = _require_plotly()

    events_list = list(events)

    if not events_list:
        raise ValueError("Se requieren eventos MTQ para generar la visualización")

    if not hasattr(events_list[0], metric):
        raise ValueError(f"La métrica {metric!r} no existe en MTQEvent")

    x = [event.timestamp for event in events_list]
    y = [getattr(event, metric) for event in events_list]

    scatter = go.Scatter(x=x, y=y, mode="lines+markers", name=metric)
    layout = go.Layout(
        title=f"Evolución temporal de {metric}",
        xaxis_title="Tiempo",
        yaxis_title=metric,
        hovermode="x",
        template="plotly_white",
    )
    return go.Figure(data=[scatter], layout=layout)
