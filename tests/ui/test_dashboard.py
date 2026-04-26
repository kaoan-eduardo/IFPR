from __future__ import annotations

import json
from datetime import datetime
from types import SimpleNamespace

import pandas as pd

from src.ui.tabs import tab_dashboard


def test_montar_dataframe_analises():
    analises = [
        SimpleNamespace(
            id=1,
            nome_arquivo="img.jpg",
            data_analise=datetime(2026, 1, 2, 10, 30),
            resultado_final="Pavimento em bom estado",
            modelo_mais_confiante="random_forest",
            confianca=0.91,
            observacao="ok",
            detalhes_modelos=None,
        )
    ]

    df = tab_dashboard._montar_dataframe_analises(analises)

    assert len(df) == 1
    assert df.loc[0, "nome_arquivo"] == "img.jpg"
    assert df.loc[0, "modelo_mais_confiante_nome"] == "🌲 Random Forest"
    assert df.loc[0, "dia"] == "02/01/2026"


def test_extrair_probabilidades_valido():
    df = pd.DataFrame(
        [{"detalhes_modelos": '{"rf": {"probabilidade": 0.85}}'}]
    )

    resultado = tab_dashboard._extrair_probabilidades_modelos(df)

    assert not resultado.empty
    assert resultado.iloc[0]["Confianca"] == 0.85


def test_extrair_probabilidades_json_invalido():
    df = pd.DataFrame(
        [{"detalhes_modelos": '{"rf": '}]
    )

    resultado = tab_dashboard._extrair_probabilidades_modelos(df)

    assert resultado.empty


def test_extrair_probabilidades_sem_probabilidade():
    df = pd.DataFrame(
        [{"detalhes_modelos": '{"rf": {}}'}]
    )

    resultado = tab_dashboard._extrair_probabilidades_modelos(df)

    assert resultado.empty


def test_extrair_probabilidades_com_erro_no_modelo():
    df = pd.DataFrame(
        [{"detalhes_modelos": '{"rf": {"erro": "falha"}}'}]
    )

    resultado = tab_dashboard._extrair_probabilidades_modelos(df)

    assert resultado.empty


def test_extrair_probabilidades_multiplos_modelos():
    df = pd.DataFrame(
        [{"detalhes_modelos": '{"rf": {"probabilidade": 0.8}, "svm": {"probabilidade": 0.6}}'}]
    )

    resultado = tab_dashboard._extrair_probabilidades_modelos(df)

    assert len(resultado) == 2


def test_extrair_probabilidades_probabilidade_invalida():
    df = pd.DataFrame(
        [{"detalhes_modelos": '{"rf": {"probabilidade": "abc"}}'}]
    )

    resultado = tab_dashboard._extrair_probabilidades_modelos(df)

    assert resultado.empty


def test_extrair_probabilidades_json_nao_dicionario():
    df = pd.DataFrame(
        [{"detalhes_modelos": '["rf", "svm"]'}]
    )

    resultado = tab_dashboard._extrair_probabilidades_modelos(df)

    assert resultado.empty


def test_extrair_probabilidades_modelos_retorna_dataframe():
    detalhes = {
        "random_forest": {"probabilidade": 0.9},
        "svm": {"probabilidade": 0.7},
        "knn": {"erro": "falhou"},
    }

    df = pd.DataFrame({"detalhes_modelos": [json.dumps(detalhes)]})

    resultado = tab_dashboard._extrair_probabilidades_modelos(df)

    assert len(resultado) == 2
    assert set(resultado["Modelo"]) == {"🌲 Random Forest", "📈 SVM"}
    assert resultado["Confianca"].tolist() == [0.9, 0.7]


def test_calcular_metricas_basico():
    df = pd.DataFrame(
        [
            {"resultado_final": "Pavimento com rachaduras detectadas"},
            {"resultado_final": "Pavimento em bom estado"},
        ]
    )

    metricas = tab_dashboard._calcular_metricas_dashboard(df)

    assert metricas["total_analises"] == 2
    assert metricas["qtd_rachado"] == 1
    assert metricas["qtd_bom"] == 1


def test_calcular_metricas_vazio():
    df = pd.DataFrame(columns=["resultado_final", "detalhes_modelos"])

    metricas = tab_dashboard._calcular_metricas_dashboard(df)

    assert metricas["total_analises"] == 0
    assert metricas["qtd_rachado"] == 0
    assert metricas["qtd_bom"] == 0
    assert metricas["perc_rachado"] == 0.0
    assert metricas["perc_bom"] == 0.0
    assert metricas["confianca_media"] == 0.0
    assert metricas["taxa_incerteza"] == 0.0


def test_calcular_metricas_dashboard():
    detalhes = {
        "random_forest": {"probabilidade": 0.9},
        "svm": {"probabilidade": 0.5},
    }

    df = pd.DataFrame(
        {
            "resultado_final": [
                tab_dashboard.RESULTADO_RACHADO,
                tab_dashboard.RESULTADO_BOM,
            ],
            "detalhes_modelos": [
                json.dumps(detalhes),
                json.dumps(detalhes),
            ],
        }
    )

    metricas = tab_dashboard._calcular_metricas_dashboard(df)

    assert metricas["total_analises"] == 2
    assert metricas["qtd_rachado"] == 1
    assert metricas["qtd_bom"] == 1
    assert metricas["perc_rachado"] == 50.0
    assert metricas["perc_bom"] == 50.0
    assert metricas["confianca_media"] == 0.7
    assert metricas["taxa_incerteza"] == 50.0


def test_extrair_confianca_media_todos_modelos():
    detalhes = {
        "random_forest": {"probabilidade": 0.9},
        "svm": {"probabilidade": 0.7},
    }

    df = pd.DataFrame({"detalhes_modelos": [json.dumps(detalhes)]})

    resultado = tab_dashboard._extrair_confianca_media_todos_modelos(df)

    assert len(resultado) == 2
    assert resultado.iloc[0]["Confianca"] == 0.9