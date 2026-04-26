from __future__ import annotations

import pandas as pd

from conftest import patch_streamlit_basico
from src.ui.tabs import tab_avaliacao_modelo


def test_formatar_nome_modelo_avaliacao():
    assert tab_avaliacao_modelo._formatar_nome_modelo("random_forest") == "Random Forest"
    assert tab_avaliacao_modelo._formatar_nome_modelo("decision_tree") == "Árvore de Decisão"
    assert tab_avaliacao_modelo._formatar_nome_modelo("modelo_x") == "modelo_x"


def test_padronizar_modelos_altera_coluna_modelo():
    df_resumo = pd.DataFrame({"Modelo": ["random_forest"]})
    df_folds = pd.DataFrame({"Modelo": ["svm"]})
    df_matriz = pd.DataFrame({"Modelo": ["knn"]})

    r, f, m = tab_avaliacao_modelo._padronizar_modelos(df_resumo, df_folds, df_matriz)

    assert r.loc[0, "Modelo"] == "Random Forest"
    assert f.loc[0, "Modelo"] == "SVM"
    assert m.loc[0, "Modelo"] == "K-Nearest Neighbors"


def test_formatar_tabela_resumo_converte_percentuais():
    df = pd.DataFrame(
        {
            "Modelo": ["Random Forest"],
            "Accuracy Média": [0.91234],
            "Precision Média": [0.8],
            "Recall Média": [None],
        }
    )

    resultado = tab_avaliacao_modelo._formatar_tabela_resumo(df)

    assert resultado.loc[0, "Accuracy Média"] == "91.23%"
    assert resultado.loc[0, "Precision Média"] == "80.00%"
    assert resultado.loc[0, "Recall Média"] == "-"


def test_render_tab_avaliacao_modelo_sem_dados(monkeypatch):
    patch_streamlit_basico(monkeypatch, tab_avaliacao_modelo)

    monkeypatch.setattr(
        tab_avaliacao_modelo,
        "carregar_dados_avaliacao",
        lambda: (None, None, None),
    )

    tab_avaliacao_modelo.render_tab_avaliacao_modelo()


def test_render_tab_avaliacao_modelo_com_dados(monkeypatch):
    patch_streamlit_basico(monkeypatch, tab_avaliacao_modelo)

    df_resumo = pd.DataFrame(
        {
            "Modelo": ["random_forest", "svm"],
            "Accuracy Média": [0.91, 0.85],
            "Accuracy Desvio": [0.01, 0.02],
            "Precision Média": [0.90, 0.84],
            "Precision Desvio": [0.01, 0.02],
            "Recall Média": [0.89, 0.83],
            "Recall Desvio": [0.01, 0.02],
            "F1-score Média": [0.895, 0.835],
            "F1-score Desvio": [0.01, 0.02],
            "Specificity Média": [0.92, 0.86],
            "Specificity Desvio": [0.01, 0.02],
        }
    )

    df_folds = pd.DataFrame(
        {
            "Modelo": ["random_forest", "random_forest"],
            "Fold": [1, 2],
            "Accuracy": [0.91, 0.90],
            "Precision": [0.90, 0.89],
            "Recall": [0.89, 0.88],
            "F1-score": [0.895, 0.885],
            "Specificity": [0.92, 0.91],
        }
    )

    df_matriz = pd.DataFrame(
        {
            "Modelo": ["random_forest"],
            "TN (bom->bom)": [10],
            "FP (bom->ruim)": [1],
            "FN (ruim->bom)": [2],
            "TP (ruim->ruim)": [20],
        }
    )

    monkeypatch.setattr(
        tab_avaliacao_modelo,
        "carregar_dados_avaliacao",
        lambda: (df_resumo, df_folds, df_matriz),
    )

    tab_avaliacao_modelo.render_tab_avaliacao_modelo()