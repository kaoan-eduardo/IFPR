from __future__ import annotations

from types import SimpleNamespace

import pandas as pd

from src.services import evaluation_service


def test_evaluation_service_com_mock(monkeypatch):
    df_fake = pd.DataFrame({"a": [1]})

    monkeypatch.setattr(
        evaluation_service,
        "CAMINHO_METRICAS",
        SimpleNamespace(exists=lambda: True),
    )

    monkeypatch.setattr(
        evaluation_service,
        "pd",
        SimpleNamespace(read_excel=lambda *args, **kwargs: df_fake),
    )

    resultado = evaluation_service.carregar_dados_avaliacao()

    assert len(resultado) == 3
    assert all(df.equals(df_fake) for df in resultado)


def test_evaluation_service_arquivo_nao_existe(monkeypatch):
    monkeypatch.setattr(
        evaluation_service,
        "CAMINHO_METRICAS",
        SimpleNamespace(exists=lambda: False),
    )

    resultado = evaluation_service.carregar_dados_avaliacao()

    assert resultado == (None, None, None)