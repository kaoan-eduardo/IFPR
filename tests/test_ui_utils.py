from __future__ import annotations

import io
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from PIL import Image

from src.ui import charts, evaluation_charts, header, styles
from src.ui.components import _ler_bytes_arquivo, preparar_thumbnail
from src.utils import formatters


def test_nome_modelo_amigavel_retorna_nome_conhecido():
    assert formatters.nome_modelo_amigavel("random_forest") == "🌲 Random Forest"


def test_nome_modelo_amigavel_retorna_original_quando_desconhecido():
    assert formatters.nome_modelo_amigavel("modelo_x") == "modelo_x"


def test_resumir_votacao_retorna_rachado_quando_maioria_rachado():
    resultados = {
        "m1": {"classe": "Rachado"},
        "m2": {"classe": "Rachado"},
        "m3": {"classe": "Não Rachado"},
    }

    resumo = formatters.resumir_votacao(resultados)

    assert resumo["classe_final"] == "Rachado"
    assert resumo["texto_final"] == "Pavimento com rachaduras detectadas"
    assert resumo["votos_rachado"] == 2
    assert resumo["votos_nao_rachado"] == 1


def test_resumir_votacao_ignora_modelos_com_erro():
    resultados = {
        "m1": {"classe": "Não Rachado"},
        "m2": {"erro": "falhou"},
    }

    resumo = formatters.resumir_votacao(resultados)

    assert resumo["classe_final"] == "Não Rachado"
    assert resumo["votos_rachado"] == 0
    assert resumo["votos_nao_rachado"] == 1


def test_obter_modelo_mais_confiante_retorna_maior_probabilidade():
    resultados = {
        "m1": {"classe": "Rachado", "probabilidade": 0.7},
        "m2": {"classe": "Não Rachado", "probabilidade": 0.9},
        "m3": {"erro": "falhou"},
    }

    nome, dados = formatters.obter_modelo_mais_confiante(resultados)

    assert nome == "m2"
    assert dados["probabilidade"] == 0.9


def test_obter_modelo_mais_confiante_retorna_none_sem_validos():
    nome, dados = formatters.obter_modelo_mais_confiante({"m1": {"erro": "falhou"}})

    assert nome is None
    assert dados is None


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


def test_ler_bytes_arquivo_com_getvalue():
    arquivo = io.BytesIO(b"abc")
    arquivo.name = "teste.txt"

    conteudo = _ler_bytes_arquivo(arquivo)

    assert conteudo == b"abc"
    assert arquivo.tell() == 0


def test_ler_bytes_arquivo_com_read():
    class ArquivoFake:
        def __init__(self):
            self.pos = 0

        def read(self):
            return b"conteudo"

        def seek(self, pos):
            self.pos = pos

    arquivo = ArquivoFake()

    assert _ler_bytes_arquivo(arquivo) == b"conteudo"
    assert arquivo.pos == 0


def test_preparar_thumbnail_retorna_imagem_pil():
    imagem = Image.fromarray(np.zeros((100, 100, 3), dtype=np.uint8))
    buffer = io.BytesIO()
    imagem.save(buffer, format="PNG")
    buffer.seek(0)

    thumb = preparar_thumbnail(buffer, tamanho=(50, 40))

    assert isinstance(thumb, Image.Image)
    assert thumb.size == (50, 40)


def test_carregar_logo_base64_retorna_none_quando_nao_existe(monkeypatch, tmp_path: Path):
    monkeypatch.setattr(header, "LOGO_PATH", tmp_path / "inexistente.png")

    assert header.carregar_logo_base64() is None


def test_carregar_logo_base64_retorna_string(monkeypatch, tmp_path: Path):
    caminho_logo = tmp_path / "logo.png"
    caminho_logo.write_bytes(b"abc")

    monkeypatch.setattr(header, "LOGO_PATH", caminho_logo)

    resultado = header.carregar_logo_base64()

    assert isinstance(resultado, str)
    assert resultado != ""


def test_aplicar_estilos_chama_markdown(monkeypatch):
    chamadas = []

    monkeypatch.setattr(styles.st, "markdown", lambda *args, **kwargs: chamadas.append((args, kwargs)))

    styles.aplicar_estilos()

    assert len(chamadas) == 1
    assert "<style>" in chamadas[0][0][0]