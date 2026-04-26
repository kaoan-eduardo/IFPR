from __future__ import annotations

from contextlib import nullcontext


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


def fake_columns(spec, **kwargs):
    if isinstance(spec, int):
        return [FakeColumn() for _ in range(spec)]

    return [FakeColumn() for _ in range(len(spec))]


def patch_streamlit_basico(monkeypatch, modulo):
    monkeypatch.setattr(modulo.st, "markdown", lambda *args, **kwargs: None)
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
    monkeypatch.setattr(modulo.st, "rerun", lambda *args, **kwargs: None)