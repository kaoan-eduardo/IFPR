from __future__ import annotations

from pathlib import Path

from conftest import patch_streamlit_basico
from src.ui import header


def test_renderizar_header_sem_logo(monkeypatch):
    patch_streamlit_basico(monkeypatch, header)
    monkeypatch.setattr(header, "carregar_logo_base64", lambda: None)

    header.renderizar_header()


def test_renderizar_header_com_logo(monkeypatch):
    patch_streamlit_basico(monkeypatch, header)
    monkeypatch.setattr(header, "carregar_logo_base64", lambda: "abc123")

    header.renderizar_header()


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