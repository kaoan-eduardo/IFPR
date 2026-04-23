from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def grafico_metricas(df: pd.DataFrame) -> go.Figure:
    colunas_metricas = [
        "Accuracy Média",
        "Precision Média",
        "Recall Média",
        "F1-score Média",
    ]

    df_plot = df.melt(
        id_vars="Modelo",
        value_vars=colunas_metricas,
        var_name="Métrica",
        value_name="Valor",
    )

    fig = px.bar(
        df_plot,
        x="Modelo",
        y="Valor",
        color="Métrica",
        barmode="group",
        text="Valor",
    )

    fig.update_traces(texttemplate="%{text:.2%}", textposition="outside")

    fig.update_layout(
        height=420,
        margin=dict(l=10, r=10, t=30, b=40),
        yaxis=dict(range=[0, 1.05], title="Valor"),
        xaxis_title="Modelo",
        legend_title="Métrica",
    )

    return fig


def grafico_folds(df: pd.DataFrame, metrica_escolhida: str) -> go.Figure:
    fig = px.line(
        df,
        x="Fold",
        y=metrica_escolhida,
        color="Modelo",
        markers=True,
    )

    fig.update_layout(
        height=400,
        margin=dict(l=10, r=10, t=30, b=40),
        yaxis=dict(range=[0, 1.05], title=metrica_escolhida),
        xaxis_title="Fold",
        legend_title="Modelo",
    )

    return fig


def heatmap_matriz(tn: int, fp: int, fn: int, tp: int, titulo: str) -> go.Figure:
    matriz = [[tn, fp], [fn, tp]]

    fig = go.Figure(
        data=go.Heatmap(
            z=matriz,
            x=["Pred: Não Rachado", "Pred: Rachado"],
            y=["Real: Não Rachado", "Real: Rachado"],
            text=matriz,
            texttemplate="%{text}",
            hovertemplate="Valor: %{z}<extra></extra>",
        )
    )

    fig.update_layout(
        title=titulo,
        height=400,
        margin=dict(l=10, r=10, t=50, b=20),
    )

    return fig