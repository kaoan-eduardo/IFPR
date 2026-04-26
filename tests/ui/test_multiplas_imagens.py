from __future__ import annotations

import io
import zipfile
from types import SimpleNamespace

from conftest import patch_streamlit_basico
from src.ui.tabs import tab_multiplas_imagens


def test_multiplas_render_metricas_lote(monkeypatch):
    patch_streamlit_basico(monkeypatch, tab_multiplas_imagens)

    tab_multiplas_imagens._render_metricas_lote(
        [
            {"resultado_final": tab_multiplas_imagens.RESULTADO_BOM},
            {"resultado_final": tab_multiplas_imagens.RESULTADO_RACHADO},
        ]
    )


def test_multiplas_render_galeria_lote(monkeypatch):
    patch_streamlit_basico(monkeypatch, tab_multiplas_imagens)

    monkeypatch.setattr(
        tab_multiplas_imagens,
        "preparar_thumbnail",
        lambda arquivo, tamanho=None: "thumb",
    )

    monkeypatch.setattr(tab_multiplas_imagens, "exibir_detalhamento", lambda x: None)

    tab_multiplas_imagens._render_galeria_lote(
        [
            {
                "arquivo": io.BytesIO(b"abc"),
                "nome": "img.jpg",
                "resultado_final": tab_multiplas_imagens.RESULTADO_BOM,
                "melhor_modelo": "🌲 Random Forest",
                "classe_melhor_modelo": "Não Rachado",
                "confianca": 0.91,
                "detalhamento_disponivel": True,
                "resultados_completos": {
                    "random_forest": {
                        "classe": "Não Rachado",
                        "probabilidade": 0.91,
                    }
                },
            }
        ]
    )


def test_multiplas_sem_arquivos(monkeypatch):
    patch_streamlit_basico(monkeypatch, tab_multiplas_imagens)

    monkeypatch.setattr(tab_multiplas_imagens.st, "file_uploader", lambda *args, **kwargs: None)

    tab_multiplas_imagens.render_tab_multiplas_imagens()


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
    patch_streamlit_basico(monkeypatch, tab_multiplas_imagens)

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
    patch_streamlit_basico(monkeypatch, tab_multiplas_imagens)

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


def test_listar_arquivos_zip_retorna_imagens_validas():
    buffer = io.BytesIO()

    with zipfile.ZipFile(buffer, "w") as zf:
        zf.writestr("pasta/imagem.jpg", b"fake")
        zf.writestr("pasta/texto.txt", b"texto")

    buffer.seek(0)

    arquivos, erro = tab_multiplas_imagens._listar_arquivos_zip(buffer)

    assert erro is None
    assert len(arquivos) == 1
    assert arquivos[0]["name"] == "imagem.jpg"
    assert arquivos[0]["full_name"] == "pasta/imagem.jpg"


def test_listar_arquivos_zip_retorna_erro_para_zip_invalido():
    buffer = io.BytesIO(b"nao eh zip")

    arquivos, erro = tab_multiplas_imagens._listar_arquivos_zip(buffer)

    assert arquivos == []
    assert erro == "Arquivo ZIP inválido ou corrompido."


def test_converter_arquivo_zip_para_buffer():
    arquivo_dict = {
        "name": "teste.jpg",
        "bytes": b"abc",
    }

    buffer = tab_multiplas_imagens._converter_arquivo_zip_para_buffer(arquivo_dict)

    assert buffer.getvalue() == b"abc"
    assert buffer.name == "teste.jpg"


def test_gerar_excel_lote_retorna_bytesio():
    resultados = [
        {
            "nome": "img.jpg",
            "resultado_final": tab_multiplas_imagens.RESULTADO_BOM,
            "melhor_modelo": "Random Forest",
            "classe_melhor_modelo": "Não Rachado",
            "confianca": 0.91,
        }
    ]

    arquivo = tab_multiplas_imagens._gerar_excel_lote(resultados)

    assert isinstance(arquivo, io.BytesIO)
    assert arquivo.getbuffer().nbytes > 0


def test_gerar_pdf_lote_retorna_bytesio():
    resultados = [
        {
            "nome": "img.jpg",
            "resultado_final": tab_multiplas_imagens.RESULTADO_BOM,
            "melhor_modelo": "Random Forest",
            "classe_melhor_modelo": "Não Rachado",
            "confianca": 0.91,
        }
    ]

    arquivo = tab_multiplas_imagens._gerar_pdf_lote(resultados)

    assert isinstance(arquivo, io.BytesIO)
    assert arquivo.getvalue().startswith(b"%PDF")


def test_montar_resultado_erro_lote():
    resultado = tab_multiplas_imagens._montar_resultado_erro("arquivo", "img.jpg")

    assert resultado["arquivo"] == "arquivo"
    assert resultado["nome"] == "img.jpg"
    assert resultado["resultado_final"] == "Imagem inválida"
    assert resultado["detalhamento_disponivel"] is False