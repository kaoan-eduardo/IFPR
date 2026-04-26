from __future__ import annotations

from src.ui import styles


def test_aplicar_estilos_chama_markdown(monkeypatch):
    chamadas = []

    monkeypatch.setattr(
        styles.st,
        "markdown",
        lambda *args, **kwargs: chamadas.append((args, kwargs)),
    )

    styles.aplicar_estilos()

    assert len(chamadas) == 1
    assert "<style>" in chamadas[0][0][0]