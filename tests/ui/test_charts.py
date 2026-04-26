from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go

from src.ui import charts, evaluation_charts


def test_montar_grafico_sem_resultados_validos():
    fig = charts.montar_grafico({"m1": {"erro": "falhou"}})

    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 0
    assert fig.layout.annotations[0].text == "Nenhum resultado válido disponível para exibir."


def test_montar_grafico_com_resultados_validos():
    resultados = {
        "random_forest": {"classe": "Rachado", "probabilidade": 0.91},
        "svm": {"classe": "Não Rachado", "probabilidade": 0.72},
    }

    fig = charts.montar_grafico(resultados)

    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 1
    assert list(fig.data[0].y) == [0.91, 0.72]


def test_grafico_metricas_retorna_figure():
    df = pd.DataFrame(
        {
            "Modelo": ["Random Forest"],
            "Accuracy Média": [0.9],
            "Precision Média": [0.8],
            "Recall Média": [0.7],
            "F1-score Média": [0.75],
        }
    )

    fig = evaluation_charts.grafico_metricas(df)

    assert isinstance(fig, go.Figure)


def test_grafico_folds_retorna_figure():
    df = pd.DataFrame(
        {
            "Modelo": ["Random Forest", "Random Forest"],
            "Fold": [1, 2],
            "Accuracy": [0.9, 0.85],
        }
    )

    fig = evaluation_charts.grafico_folds(df, "Accuracy")

    assert isinstance(fig, go.Figure)


def test_heatmap_matriz_retorna_figure():
    fig = evaluation_charts.heatmap_matriz(10, 2, 3, 15, "Matriz")

    assert isinstance(fig, go.Figure)
    assert fig.layout.title.text == "Matriz"