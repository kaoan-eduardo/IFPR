from __future__ import annotations

from types import SimpleNamespace

from src.services import analysis_service


def test_analysis_service_gerar_hash_bytes():
    resultado = analysis_service.gerar_hash_bytes(b"abc")

    assert isinstance(resultado, str)
    assert len(resultado) == 64


def test_analysis_service_registrar_analise(monkeypatch):
    class DbFake:
        def close(self):
            pass

    chamadas = []

    monkeypatch.setattr(analysis_service, "SessionLocal", lambda: DbFake())
    monkeypatch.setattr(
        analysis_service,
        "salvar_analise",
        lambda **kwargs: chamadas.append(kwargs) or SimpleNamespace(id=1),
    )

    resultados = {
        "random_forest": {"classe": "Rachado", "probabilidade": 0.91},
        "svm": {"classe": "Rachado", "probabilidade": 0.70},
    }

    resultado = analysis_service.registrar_analise(
        nome_arquivo="img.jpg",
        resultados=resultados,
        hash_arquivo="hash123",
    )

    assert resultado is not None
    assert chamadas[0]["modelo_mais_confiante"] == "🌲 Random Forest"


def test_analysis_service_sem_modelos():
    resultado = analysis_service.registrar_analise(
        nome_arquivo="img.jpg",
        resultados={},
        hash_arquivo="hash",
    )

    assert resultado is None