from __future__ import annotations

from typing import Any

import plotly.graph_objects as go

from src.utils.formatters import nome_modelo_amigavel


MODEL_COLORS = {
    "random_forest": "#1B5E20",
    "decision_tree": "#4CAF50",
    "knn": "#2196F3",
    "svm": "#9C27B0",
}

HIGHLIGHT_COLOR = "#00E676"
DEFAULT_COLOR = "#888888"


def montar_grafico(resultados: dict[str, dict[str, Any]]) -> go.Figure:
    resultados_validos = {
        modelo: info
        for modelo, info in resultados.items()
        if isinstance(info, dict) and "erro" not in info
    }

    fig = go.Figure()

    if not resultados_validos:
        fig.update_layout(
            height=360,
            margin=dict(l=10, r=10, t=20, b=40),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            annotations=[
                dict(
                    text="Nenhum resultado válido disponível para exibir.",
                    x=0.5,
                    y=0.5,
                    xref="paper",
                    yref="paper",
                    showarrow=False,
                )
            ],
        )
        return fig

    melhor_modelo = max(
        resultados_validos.items(),
        key=lambda x: float(x[1].get("probabilidade", 0.0)),
    )[0]

    labels: list[str] = []
    valores: list[float] = []
    cores: list[str] = []

    for modelo, info in resultados_validos.items():
        labels.append(nome_modelo_amigavel(modelo))
        valores.append(float(info.get("probabilidade", 0.0)))

        if modelo == melhor_modelo:
            cores.append(HIGHLIGHT_COLOR)
        else:
            cores.append(MODEL_COLORS.get(modelo, DEFAULT_COLOR))

    fig.add_trace(
        go.Bar(
            x=labels,
            y=valores,
            marker_color=cores,
            text=[f"{v:.1%}" for v in valores],
            textposition="outside",
            hovertemplate="<b>%{x}</b><br>Confiança: %{y:.2%}<extra></extra>",
        )
    )

    fig.update_layout(
        yaxis=dict(range=[0, 1], title="Confiança"),
        xaxis_tickangle=-25,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        margin=dict(l=10, r=10, t=20, b=40),
        height=360,
    )

    return fig