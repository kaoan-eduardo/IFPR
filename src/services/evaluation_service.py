from __future__ import annotations

from pathlib import Path

import pandas as pd

CAMINHO_METRICAS = Path("results/metricas_cross_validation.xlsx")


def carregar_dados_avaliacao() -> tuple[pd.DataFrame | None, pd.DataFrame | None, pd.DataFrame | None]:
    """
    Carrega os dados de avaliação a partir do arquivo Excel de métricas.
    Retorna três DataFrames (Resumo, Folds e Matriz_Confusao) ou
    (None, None, None) caso o arquivo não exista.
    """
    if not CAMINHO_METRICAS.exists():
        return None, None, None

    df_resumo = pd.read_excel(CAMINHO_METRICAS, sheet_name="Resumo")
    df_folds = pd.read_excel(CAMINHO_METRICAS, sheet_name="Folds")
    df_matriz = pd.read_excel(CAMINHO_METRICAS, sheet_name="Matriz_Confusao")

    return df_resumo, df_folds, df_matriz