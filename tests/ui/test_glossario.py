from __future__ import annotations

from contextlib import nullcontext

from src.ui.tabs import tab_glossario


def test_render_tab_glossario(monkeypatch):
    chamadas = []

    monkeypatch.setattr(
        tab_glossario.st,
        "markdown",
        lambda *args, **kwargs: chamadas.append(args[0]),
    )
    monkeypatch.setattr(tab_glossario.st, "expander", lambda *args, **kwargs: nullcontext())

    tab_glossario.render_tab_glossario()

    assert any("Glossário" in str(chamada) for chamada in chamadas)
    assert len(chamadas) > 10