import io
import pytest
from unittest.mock import patch

from src.services.inference_service import (
    analisar_arquivo,
    _obter_bytes_arquivo,
)


# =========================
# TESTES DE LEITURA DE ARQUIVO
# =========================

def test_obter_bytes_arquivo_com_getbuffer():
    fake_file = io.BytesIO(b"conteudo teste")

    resultado = _obter_bytes_arquivo(fake_file)

    assert isinstance(resultado, bytes)
    assert resultado == b"conteudo teste"


def test_obter_bytes_arquivo_com_read():
    class FakeFile:
        def read(self):
            return b"abc123"

    fake_file = FakeFile()

    resultado = _obter_bytes_arquivo(fake_file)

    assert resultado == b"abc123"


def test_obter_bytes_arquivo_invalido():
    class FakeFile:
        pass

    with pytest.raises(ValueError):
        _obter_bytes_arquivo(FakeFile())


# =========================
# TESTES DE INFERÊNCIA (COM MOCK)
# =========================

def test_analisar_arquivo_com_mock_do_modelo():
    fake_file = io.BytesIO(b"imagem fake")
    fake_file.name = "teste.jpg"

    retorno_mock = {
        "resultado_final": "Pavimento em bom estado",
        "confianca": 0.95,
    }

    with patch(
        "src.services.inference_service.prever_imagem",
        return_value=retorno_mock,
    ):
        resultado = analisar_arquivo(fake_file)

    assert resultado == retorno_mock


def test_analisar_arquivo_remove_arquivo_temp():
    fake_file = io.BytesIO(b"imagem fake")
    fake_file.name = "teste.jpg"

    retorno_mock = {"ok": True}

    with patch(
        "src.services.inference_service.prever_imagem",
        return_value=retorno_mock,
    ):
        resultado = analisar_arquivo(fake_file)

    assert resultado == retorno_mock