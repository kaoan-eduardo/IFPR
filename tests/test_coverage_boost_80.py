from __future__ import annotations

import io
import json
from contextlib import nullcontext
from datetime import datetime
from types import SimpleNamespace

import pandas as pd

from src.services import analysis_service, evaluation_service
from src.ui.tabs import tab_dashboard, tab_multiplas_imagens, tab_upload_unico


class FakeColumn:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


def fake_columns(spec, **kwargs):
    if isinstance(spec, int):
        return [FakeColumn() for _ in range(spec)]
    return [FakeColumn() for _ in range(len(spec))]


def patch_st(monkeypatch, modulo):
    monkeypatch.setattr(modulo.st, "markdown", lambda *args, **kwargs: None)
    monkeypatch.setattr(modulo.st, "columns", fake_columns)
    monkeypatch.setattr(modulo.st, "plotly_chart", lambda *args, **kwargs: None)
    monkeypatch.setattr(modulo.st, "dataframe", lambda *args, **kwargs: None)
    monkeypatch.setattr(modulo.st, "download_button", lambda *args, **kwargs: None)
    monkeypatch.setattr(modulo.st, "info", lambda *args, **kwargs: None)
    monkeypatch.setattr(modulo.st, "caption", lambda *args, **kwargs: None)
    monkeypatch.setattr(modulo.st, "error", lambda *args, **kwargs: None)
    monkeypatch.setattr(modulo.st, "image", lambda *args, **kwargs: None)
    monkeypatch.setattr(modulo.st, "container", lambda *args, **kwargs: nullcontext())
    monkeypatch.setattr(modulo.st, "expander", lambda *args, **kwargs: nullcontext())
    monkeypatch.setattr(modulo.st, "button", lambda *args, **kwargs: False)
    monkeypatch.setattr(modulo.st, "rerun", lambda *args, **kwargs: None)


def test_analysis_service_gerar_hash_bytes():
    resultado = analysis_service.gerar_hash_bytes(b"abc")

    assert isinstance(resultado, str)
    assert len(resultado) == 64


def test_analysis_service_registrar_analise(monkeypatch):
    class DbFake:
        def close(self):
            pass

    chamadas = []

    monkeypatch.setattr(analysis_service, "SessionLocal", lambda: DbFake())

    monkeypatch.setattr(
        analysis_service,
        "salvar_analise",
        lambda **kwargs: chamadas.append(kwargs) or SimpleNamespace(id=1),
    )

    resultados = {
        "random_forest": {"classe": "Rachado", "probabilidade": 0.91},
        "svm": {"classe": "Rachado", "probabilidade": 0.70},
    }

    analysis_service.registrar_analise(
        nome_arquivo="img.jpg",
        resultados=resultados,
        hash_arquivo="hash123",
    )

    assert chamadas[0]["nome_arquivo"] == "img.jpg"
    assert chamadas[0]["hash_arquivo"] == "hash123"
    assert chamadas[0]["resultado_final"] == "Pavimento com rachaduras detectadas"
    assert chamadas[0]["modelo_mais_confiante"] == "🌲 Random Forest"
    assert chamadas[0]["confianca"] == 0.91


def test_evaluation_service_com_mock(monkeypatch):
    import pandas as pd

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
    assert resultado[0].equals(df_fake)
    assert resultado[1].equals(df_fake)
    assert resultado[2].equals(df_fake)


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
    assert resultado[0].equals(df_fake)
    assert resultado[1].equals(df_fake)
    assert resultado[2].equals(df_fake)


def test_dashboard_carregar_analises_fecha_db(monkeypatch):
    class DbFake:
        fechado = False

        def close(self):
            self.fechado = True

    db_fake = DbFake()

    monkeypatch.setattr(tab_dashboard, "SessionLocal", lambda: db_fake)
    monkeypatch.setattr(tab_dashboard, "listar_analises", lambda db: ["a", "b"])

    resultado = tab_dashboard._carregar_analises()

    assert resultado == ["a", "b"]
    assert db_fake.fechado is True


def test_dashboard_render_topo(monkeypatch):
    patch_st(monkeypatch, tab_dashboard)

    tab_dashboard._render_topo()


def test_dashboard_render_visao_geral(monkeypatch):
    patch_st(monkeypatch, tab_dashboard)

    metricas = {
        "total_analises": 10,
        "qtd_rachado": 4,
        "qtd_bom": 6,
        "perc_rachado": 40.0,
        "perc_bom": 60.0,
        "confianca_media": 0.85,
        "taxa_incerteza": 12.5,
    }

    tab_dashboard._render_visao_geral(metricas)


def test_dashboard_render_exportacao(monkeypatch):
    patch_st(monkeypatch, tab_dashboard)

    monkeypatch.setattr(tab_dashboard, "exportar_excel", lambda df: b"excel")
    monkeypatch.setattr(tab_dashboard, "gerar_pdf_dashboard", lambda **kwargs: b"%PDF")

    df = pd.DataFrame({"a": [1]})
    metricas = {
        "total_analises": 1,
        "qtd_rachado": 0,
        "qtd_bom": 1,
        "confianca_media": 0.9,
        "taxa_incerteza": 0.0,
    }

    tab_dashboard._render_exportacao_dashboard(df, metricas)


def test_dashboard_render_indicadores_visuais(monkeypatch):
    patch_st(monkeypatch, tab_dashboard)

    detalhes = {
        "random_forest": {"probabilidade": 0.9},
        "svm": {"probabilidade": 0.7},
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
            "dia": ["01/01/2026", "02/01/2026"],
        }
    )

    metricas = tab_dashboard._calcular_metricas_dashboard(df)

    tab_dashboard._render_indicadores_visuais(df, metricas)


def test_dashboard_render_historico_detalhado(monkeypatch):
    patch_st(monkeypatch, tab_dashboard)

    analises = [
        SimpleNamespace(
            id=1,
            nome_arquivo="img.jpg",
            resultado_final=tab_dashboard.RESULTADO_BOM,
            observacao="ok",
            modelo_mais_confiante="random_forest",
            confianca=0.9,
            data_analise=datetime(2026, 1, 1, 10, 0),
            detalhes_modelos=json.dumps(
                {"random_forest": {"classe": "Não Rachado", "probabilidade": 0.9}}
            ),
        )
    ]

    monkeypatch.setattr(tab_dashboard, "exibir_detalhamento", lambda resultados: None)
    monkeypatch.setattr(tab_dashboard, "gerar_pdf_analise", lambda **kwargs: b"%PDF")

    tab_dashboard._render_historico_detalhado(analises)


def test_upload_unico_render_preview(monkeypatch):
    patch_st(monkeypatch, tab_upload_unico)

    arquivo = SimpleNamespace(name="img.jpg")

    tab_upload_unico._render_preview_imagem(arquivo)


def test_upload_unico_render_resultado_validado(monkeypatch):
    patch_st(monkeypatch, tab_upload_unico)

    monkeypatch.setattr(tab_upload_unico, "montar_grafico", lambda resultados: None)
    monkeypatch.setattr(tab_upload_unico, "exibir_detalhamento", lambda resultados: None)
    monkeypatch.setattr(tab_upload_unico, "gerar_pdf_analise", lambda **kwargs: b"%PDF")

    arquivo = SimpleNamespace(name="img.jpg")

    resultados = {
        "random_forest": {"classe": "Rachado", "probabilidade": 0.91},
        "svm": {"classe": "Rachado", "probabilidade": 0.80},
    }

    tab_upload_unico._render_resultado_validado(arquivo, resultados)


def test_multiplas_render_metricas_lote(monkeypatch):
    patch_st(monkeypatch, tab_multiplas_imagens)

    resultados = [
        {"resultado_final": tab_multiplas_imagens.RESULTADO_BOM},
        {"resultado_final": tab_multiplas_imagens.RESULTADO_RACHADO},
        {"resultado_final": "Imagem inválida"},
    ]

    tab_multiplas_imagens._render_metricas_lote(resultados)


def test_multiplas_render_tabela_lote(monkeypatch):
    patch_st(monkeypatch, tab_multiplas_imagens)

    resultados = [
        {
            "nome": "img.jpg",
            "resultado_final": tab_multiplas_imagens.RESULTADO_BOM,
            "melhor_modelo": "Random Forest",
            "classe_melhor_modelo": "Não Rachado",
            "confianca": 0.91,
        }
    ]

    tab_multiplas_imagens._render_tabela_lote(resultados)


def test_multiplas_render_exportacao_lote(monkeypatch):
    patch_st(monkeypatch, tab_multiplas_imagens)

    resultados = [
        {
            "nome": "img.jpg",
            "resultado_final": tab_multiplas_imagens.RESULTADO_BOM,
            "melhor_modelo": "Random Forest",
            "classe_melhor_modelo": "Não Rachado",
            "confianca": 0.91,
        }
    ]

    tab_multiplas_imagens._render_exportacao_lote(resultados)


def test_multiplas_render_galeria_lote(monkeypatch):
    patch_st(monkeypatch, tab_multiplas_imagens)

    monkeypatch.setattr(tab_multiplas_imagens, "preparar_thumbnail", lambda arquivo, tamanho: "thumb")
    monkeypatch.setattr(tab_multiplas_imagens, "exibir_detalhamento", lambda resultados: None)

    resultados = [
        {
            "arquivo": io.BytesIO(b"abc"),
            "nome": "img.jpg",
            "resultado_final": tab_multiplas_imagens.RESULTADO_BOM,
            "melhor_modelo": "Random Forest",
            "classe_melhor_modelo": "Não Rachado",
            "confianca": 0.91,
            "detalhamento_disponivel": True,
            "resultados_completos": {
                "random_forest": {"classe": "Não Rachado", "probabilidade": 0.91}
            },
        }
    ]

    tab_multiplas_imagens._render_galeria_lote(resultados)