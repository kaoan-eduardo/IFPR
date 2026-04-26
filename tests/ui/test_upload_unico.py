from __future__ import annotations

import io
from types import SimpleNamespace

from conftest import patch_streamlit_basico
from src.ui.tabs import tab_upload_unico


def test_upload_unico_render_preview(monkeypatch):
    patch_streamlit_basico(monkeypatch, tab_upload_unico)

    tab_upload_unico._render_preview_imagem(SimpleNamespace(name="img.jpg"))


def test_upload_unico_render_resultado_validado(monkeypatch):
    patch_streamlit_basico(monkeypatch, tab_upload_unico)

    monkeypatch.setattr(tab_upload_unico, "montar_grafico", lambda x: None)
    monkeypatch.setattr(tab_upload_unico, "exibir_detalhamento", lambda x: None)
    monkeypatch.setattr(tab_upload_unico, "gerar_pdf_analise", lambda **kwargs: b"%PDF")

    tab_upload_unico._render_resultado_validado(
        SimpleNamespace(name="img.jpg"),
        {"rf": {"classe": "Rachado", "probabilidade": 0.9}},
    )


def test_upload_unico_sem_arquivo(monkeypatch):
    patch_streamlit_basico(monkeypatch, tab_upload_unico)

    monkeypatch.setattr(tab_upload_unico.st, "file_uploader", lambda *args, **kwargs: None)

    tab_upload_unico.render_tab_upload_unico()


def test_upload_unico_resetar_resultado_nova_imagem():
    tab_upload_unico.st.session_state.ultima_imagem_unica = ("antiga.jpg", 10)
    tab_upload_unico.st.session_state.resultado_unico = {"algo": "teste"}

    arquivo = SimpleNamespace(name="nova.jpg", size=20)

    tab_upload_unico._resetar_resultado_se_nova_imagem(arquivo)

    assert tab_upload_unico.st.session_state.resultado_unico is None
    assert tab_upload_unico.st.session_state.ultima_imagem_unica == ("nova.jpg", 20)


def test_upload_unico_render_resultado_com_erro(monkeypatch):
    patch_streamlit_basico(monkeypatch, tab_upload_unico)

    arquivo = SimpleNamespace(name="img.jpg")

    tab_upload_unico._render_resultado(arquivo, {"erro": "imagem inválida"})


def test_upload_unico_executar_analise_sucesso(monkeypatch):
    patch_streamlit_basico(monkeypatch, tab_upload_unico)

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
    patch_streamlit_basico(monkeypatch, tab_upload_unico)

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


def test_ler_bytes_arquivo_upload_unico():
    arquivo = io.BytesIO(b"abc")
    arquivo.name = "teste.jpg"

    resultado = tab_upload_unico._ler_bytes_arquivo(arquivo)

    assert resultado == b"abc"
    assert arquivo.tell() == 0