from __future__ import annotations

import io

import numpy as np
import pytest
from PIL import Image

from src.ui.components import _ler_bytes_arquivo, preparar_thumbnail


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

def test_ler_bytes_arquivo_retorna_erro_quando_read_nao_retorna_bytes():
    class ArquivoFake:
        def read(self):
            return "texto"

        def seek(self, pos):
            pass

    with pytest.raises(ValueError):
        _ler_bytes_arquivo(ArquivoFake())


def test_ler_bytes_arquivo_retorna_erro_quando_sem_metodo_valido():
    class ArquivoFake:
        pass

    with pytest.raises(ValueError):
        _ler_bytes_arquivo(ArquivoFake())


def test_ler_bytes_arquivo_com_getbuffer():
    arquivo = io.BytesIO(b"abc")

    resultado = _ler_bytes_arquivo(arquivo)

    assert resultado == b"abc"