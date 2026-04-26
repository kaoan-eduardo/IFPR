from __future__ import annotations

from contextlib import nullcontext
from types import SimpleNamespace

import pandas as pd

from src.ui import header
from src.ui.tabs import (
    tab_avaliacao_modelo,
    tab_glossario,
    tab_multiplas_imagens,
    tab_upload_unico,
)


class FakeColumn:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


class FakeProgress:
    def progress(self, value):
        pass

    def empty(self):
        pass


class FakeEmpty:
    def markdown(self, *args, **kwargs):
        pass

    def empty(self):
        pass


def _patch_streamlit_basico(monkeypatch, modulo):
    monkeypatch.setattr(modulo.st, "markdown", lambda *args, **kwargs: None)
    def fake_columns(spec, **kwargs):
        if isinstance(spec, int):
            return [FakeColumn() for _ in range(spec)]
        return [FakeColumn() for _ in range(len(spec))]

    monkeypatch.setattr(modulo.st, "columns", fake_columns)
    monkeypatch.setattr(modulo.st, "plotly_chart", lambda *args, **kwargs: None)
    monkeypatch.setattr(modulo.st, "dataframe", lambda *args, **kwargs: None)
    monkeypatch.setattr(modulo.st, "download_button", lambda *args, **kwargs: None)
    monkeypatch.setattr(modulo.st, "selectbox", lambda label, options, **kwargs: options[0])
    monkeypatch.setattr(modulo.st, "warning", lambda *args, **kwargs: None)
    monkeypatch.setattr(modulo.st, "info", lambda *args, **kwargs: None)
    monkeypatch.setattr(modulo.st, "error", lambda *args, **kwargs: None)
    monkeypatch.setattr(modulo.st, "caption", lambda *args, **kwargs: None)
    monkeypatch.setattr(modulo.st, "image", lambda *args, **kwargs: None)
    monkeypatch.setattr(modulo.st, "button", lambda *args, **kwargs: False)
    monkeypatch.setattr(modulo.st, "file_uploader", lambda *args, **kwargs: None)
    monkeypatch.setattr(modulo.st, "spinner", lambda *args, **kwargs: nullcontext())
    monkeypatch.setattr(modulo.st, "container", lambda *args, **kwargs: nullcontext())
    monkeypatch.setattr(modulo.st, "expander", lambda *args, **kwargs: nullcontext())
    monkeypatch.setattr(modulo.st, "progress", lambda *args, **kwargs: FakeProgress())
    monkeypatch.setattr(modulo.st, "empty", lambda *args, **kwargs: FakeEmpty())


def test_render_tab_glossario(monkeypatch):
    chamadas = []

    monkeypatch.setattr(tab_glossario.st, "markdown", lambda *args, **kwargs: chamadas.append(args[0]))
    monkeypatch.setattr(tab_glossario.st, "expander", lambda *args, **kwargs: nullcontext())

    tab_glossario.render_tab_glossario()

    assert any("Glossário" in str(chamada) for chamada in chamadas)
    assert len(chamadas) > 10


def test_renderizar_header_sem_logo(monkeypatch):
    _patch_streamlit_basico(monkeypatch, header)
    monkeypatch.setattr(header, "carregar_logo_base64", lambda: None)

    header.renderizar_header()


def test_renderizar_header_com_logo(monkeypatch):
    _patch_streamlit_basico(monkeypatch, header)
    monkeypatch.setattr(header, "carregar_logo_base64", lambda: "abc123")

    header.renderizar_header()


def test_render_tab_avaliacao_modelo_sem_dados(monkeypatch):
    _patch_streamlit_basico(monkeypatch, tab_avaliacao_modelo)

    monkeypatch.setattr(
        tab_avaliacao_modelo,
        "carregar_dados_avaliacao",
        lambda: (None, None, None),
    )

    tab_avaliacao_modelo.render_tab_avaliacao_modelo()


def test_render_tab_avaliacao_modelo_com_dados(monkeypatch):
    _patch_streamlit_basico(monkeypatch, tab_avaliacao_modelo)

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


def test_upload_unico_resetar_resultado_nova_imagem(monkeypatch):
    tab_upload_unico.st.session_state.ultima_imagem_unica = ("antiga.jpg", 10)
    tab_upload_unico.st.session_state.resultado_unico = {"algo": "teste"}

    arquivo = SimpleNamespace(name="nova.jpg", size=20)

    tab_upload_unico._resetar_resultado_se_nova_imagem(arquivo)

    assert tab_upload_unico.st.session_state.resultado_unico is None
    assert tab_upload_unico.st.session_state.ultima_imagem_unica == ("nova.jpg", 20)


def test_upload_unico_render_resultado_com_erro(monkeypatch):
    _patch_streamlit_basico(monkeypatch, tab_upload_unico)

    arquivo = SimpleNamespace(name="img.jpg")

    tab_upload_unico._render_resultado(arquivo, {"erro": "imagem inválida"})


def test_upload_unico_executar_analise_sucesso(monkeypatch):
    _patch_streamlit_basico(monkeypatch, tab_upload_unico)

    arquivo = SimpleNamespace(
        name="img.jpg",
        size=3,
        getvalue=lambda: b"abc",
        seek=lambda pos: None,
    )

    chamadas_registro = []

    monkeypatch.setattr(tab_upload_unico, "gerar_hash_bytes", lambda conteudo: "hash123")
    monkeypatch.setattr(
        tab_upload_unico,
        "analisar_arquivo",
        lambda arquivo: {"random_forest": {"classe": "Rachado", "probabilidade": 0.9}},
    )
    monkeypatch.setattr(
        tab_upload_unico,
        "registrar_analise",
        lambda **kwargs: chamadas_registro.append(kwargs),
    )

    tab_upload_unico.st.session_state.processando_unico = False
    tab_upload_unico.st.session_state.resultado_unico = None

    tab_upload_unico._executar_analise(arquivo)

    assert tab_upload_unico.st.session_state.processando_unico is False
    assert chamadas_registro[0]["nome_arquivo"] == "img.jpg"
    assert chamadas_registro[0]["hash_arquivo"] == "hash123"


def test_upload_unico_executar_analise_com_erro_nao_registra(monkeypatch):
    _patch_streamlit_basico(monkeypatch, tab_upload_unico)

    arquivo = SimpleNamespace(
        name="img.jpg",
        size=3,
        getvalue=lambda: b"abc",
        seek=lambda pos: None,
    )

    chamadas_registro = []

    monkeypatch.setattr(tab_upload_unico, "gerar_hash_bytes", lambda conteudo: "hash123")
    monkeypatch.setattr(tab_upload_unico, "analisar_arquivo", lambda arquivo: {"erro": "falhou"})
    monkeypatch.setattr(
        tab_upload_unico,
        "registrar_analise",
        lambda **kwargs: chamadas_registro.append(kwargs),
    )

    tab_upload_unico.st.session_state.processando_unico = False
    tab_upload_unico.st.session_state.resultado_unico = None

    tab_upload_unico._executar_analise(arquivo)

    assert chamadas_registro == []
    assert tab_upload_unico.st.session_state.processando_unico is False


def test_multiplas_imagens_inicializar_estado():
    if "resultado_lote" in tab_multiplas_imagens.st.session_state:
        del tab_multiplas_imagens.st.session_state["resultado_lote"]

    if "ultimo_lote" in tab_multiplas_imagens.st.session_state:
        del tab_multiplas_imagens.st.session_state["ultimo_lote"]

    tab_multiplas_imagens._inicializar_estado_lote()

    assert tab_multiplas_imagens.st.session_state.resultado_lote is None
    assert tab_multiplas_imagens.st.session_state.ultimo_lote is None


def test_multiplas_imagens_obter_identificador_upload_multiplo():
    arquivos = [
        SimpleNamespace(name="a.jpg", size=10),
        SimpleNamespace(name="b.jpg", size=20),
    ]

    resultado = tab_multiplas_imagens._obter_identificador_lote(
        "Upload múltiplo",
        arquivos,
        None,
    )

    assert resultado == (("a.jpg", 10), ("b.jpg", 20))


def test_multiplas_imagens_obter_identificador_zip():
    arquivos_zip = [
        {"full_name": "pasta/a.jpg", "size": 10},
        {"full_name": "pasta/b.jpg", "size": 20},
    ]

    resultado = tab_multiplas_imagens._obter_identificador_lote(
        "Arquivo ZIP",
        None,
        arquivos_zip,
    )

    assert resultado == (("pasta/a.jpg", 10), ("pasta/b.jpg", 20))


def test_multiplas_imagens_montar_resultado_sucesso(monkeypatch):
    chamadas_registro = []

    monkeypatch.setattr(
        tab_multiplas_imagens,
        "registrar_analise",
        lambda **kwargs: chamadas_registro.append(kwargs),
    )

    resultados = {
        "random_forest": {"classe": "Rachado", "probabilidade": 0.9},
        "svm": {"classe": "Rachado", "probabilidade": 0.8},
    }

    resultado = tab_multiplas_imagens._montar_resultado_sucesso(
        arquivo_lote="arquivo",
        nome_arquivo="img.jpg",
        resultados=resultados,
        detalhamento_disponivel=True,
        hash_arquivo="hash123",
    )

    assert resultado["nome"] == "img.jpg"
    assert resultado["resultado_final"] == "Pavimento com rachaduras detectadas"
    assert resultado["melhor_modelo"] == "🌲 Random Forest"
    assert resultado["classe_melhor_modelo"] == "Rachado"
    assert resultado["confianca"] == 0.9
    assert resultado["resultados_completos"] == resultados
    assert chamadas_registro[0]["hash_arquivo"] == "hash123"


def test_multiplas_imagens_processar_lote_upload_multiplo(monkeypatch):
    _patch_streamlit_basico(monkeypatch, tab_multiplas_imagens)

    arquivo = SimpleNamespace(
        name="img.jpg",
        size=3,
        getvalue=lambda: b"abc",
    )

    resultados_fake = {
        "random_forest": {"classe": "Não Rachado", "probabilidade": 0.91},
    }

    monkeypatch.setattr(tab_multiplas_imagens, "gerar_hash_bytes", lambda conteudo: "hash123")
    monkeypatch.setattr(tab_multiplas_imagens, "analisar_arquivo", lambda arquivo: resultados_fake)
    monkeypatch.setattr(tab_multiplas_imagens, "registrar_analise", lambda **kwargs: None)

    tab_multiplas_imagens.st.session_state.processando_lote = False

    resultado = tab_multiplas_imagens._processar_lote(
        modo_envio="Upload múltiplo",
        arquivos=[arquivo],
        arquivos_zip=None,
    )

    assert len(resultado) == 1
    assert resultado[0]["nome"] == "img.jpg"
    assert resultado[0]["resultado_final"] == "Pavimento em bom estado"
    assert tab_multiplas_imagens.st.session_state.processando_lote is False


def test_multiplas_imagens_processar_lote_com_erro(monkeypatch):
    _patch_streamlit_basico(monkeypatch, tab_multiplas_imagens)

    arquivo = SimpleNamespace(
        name="img.jpg",
        size=3,
        getvalue=lambda: b"abc",
    )

    monkeypatch.setattr(tab_multiplas_imagens, "gerar_hash_bytes", lambda conteudo: "hash123")
    monkeypatch.setattr(tab_multiplas_imagens, "analisar_arquivo", lambda arquivo: {"erro": "falhou"})

    tab_multiplas_imagens.st.session_state.processando_lote = False

    resultado = tab_multiplas_imagens._processar_lote(
        modo_envio="Upload múltiplo",
        arquivos=[arquivo],
        arquivos_zip=None,
    )

    assert len(resultado) == 1
    assert resultado[0]["resultado_final"] == "Imagem inválida"
    assert tab_multiplas_imagens.st.session_state.processando_lote is False