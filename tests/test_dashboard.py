import pandas as pd

from src.ui.tabs.tab_dashboard import (
    _extrair_probabilidades_modelos,
    _calcular_metricas_dashboard,
)


# =========================
# TESTES EXTRAÇÃO
# =========================

def test_extrair_probabilidades_valido():
    df = pd.DataFrame([
        {
            "detalhes_modelos": '{"rf": {"probabilidade": 0.85}}'
        }
    ])

    resultado = _extrair_probabilidades_modelos(df)

    assert not resultado.empty
    assert resultado.iloc[0]["Confianca"] == 0.85


def test_extrair_probabilidades_json_invalido():
    df = pd.DataFrame([
        {
            "detalhes_modelos": '{"rf": '  # JSON quebrado
        }
    ])

    resultado = _extrair_probabilidades_modelos(df)

    assert resultado.empty


def test_extrair_probabilidades_sem_probabilidade():
    df = pd.DataFrame([
        {
            "detalhes_modelos": '{"rf": {}}'
        }
    ])

    resultado = _extrair_probabilidades_modelos(df)

    assert resultado.empty


def test_extrair_probabilidades_com_erro_no_modelo():
    df = pd.DataFrame([
        {
            "detalhes_modelos": '{"rf": {"erro": "falha"}}'
        }
    ])

    resultado = _extrair_probabilidades_modelos(df)

    assert resultado.empty


def test_extrair_probabilidades_multiplos_modelos():
    df = pd.DataFrame([
        {
            "detalhes_modelos": '{"rf": {"probabilidade": 0.8}, "svm": {"probabilidade": 0.6}}'
        }
    ])

    resultado = _extrair_probabilidades_modelos(df)

    assert len(resultado) == 2


# =========================
# TESTES MÉTRICAS
# =========================

def test_calcular_metricas_basico():
    df = pd.DataFrame([
        {"resultado_final": "Pavimento com rachaduras detectadas"},
        {"resultado_final": "Pavimento em bom estado"},
    ])

    metricas = _calcular_metricas_dashboard(df)

    assert metricas["total_analises"] == 2
    assert metricas["qtd_rachado"] == 1
    assert metricas["qtd_bom"] == 1


def test_calcular_metricas_vazio():
    df = pd.DataFrame(columns=["resultado_final", "detalhes_modelos"])

    metricas = _calcular_metricas_dashboard(df)

    assert metricas["total_analises"] == 0
    assert metricas["qtd_rachado"] == 0
    assert metricas["qtd_bom"] == 0
    assert metricas["perc_rachado"] == 0.0
    assert metricas["perc_bom"] == 0.0
    assert metricas["confianca_media"] == 0.0
    assert metricas["taxa_incerteza"] == 0.0
    

def test_calcular_metricas_com_probabilidades():
    df = pd.DataFrame([
        {
            "resultado_final": "Pavimento com rachaduras detectadas",
            "detalhes_modelos": '{"rf": {"probabilidade": 0.9}}'
        },
        {
            "resultado_final": "Pavimento em bom estado",
            "detalhes_modelos": '{"rf": {"probabilidade": 0.5}}'
        }
    ])

    metricas = _calcular_metricas_dashboard(df)

    assert metricas["confianca_media"] > 0
    assert metricas["taxa_incerteza"] >= 0