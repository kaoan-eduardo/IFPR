from __future__ import annotations

import json
from datetime import datetime
from types import SimpleNamespace

from fastapi.testclient import TestClient

from api.main import app
from api.routes import analise_routes


client = TestClient(app)


def test_home_api():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {"status": "API online 🚀"}


def test_post_analisar_imagem(monkeypatch):
    class UseCaseFake:
        def executar(self, nome_arquivo, conteudo):
            assert nome_arquivo == "imagem.jpg"
            assert conteudo == b"abc"
            return {
                "status": "sucesso",
                "id_analise": 1,
                "arquivo": nome_arquivo,
                "hash_arquivo": "hash123",
                "data_analise": "26/04/2026 10:00:00",
                "resultado_final": "Pavimento em bom estado",
                "observacao": "Nenhuma anomalia significativa detectada.",
                "modelo_mais_confiante": "random_forest",
                "confianca": 0.91,
                "modelos": {
                    "random_forest": {
                        "classe": "Não Rachado",
                        "probabilidade": 0.91,
                    }
                },
            }

    monkeypatch.setattr(analise_routes, "AnalisarImagemUseCase", UseCaseFake)

    response = client.post(
        "/analise/imagem",
        files={"file": ("imagem.jpg", b"abc", "image/jpeg")},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "sucesso"
    assert body["arquivo"] == "imagem.jpg"
    assert body["confianca"] == 0.91


def test_get_historico(monkeypatch):
    class DbFake:
        def __init__(self):
            self.fechado = False

        def close(self):
            self.fechado = True

    db_fake = DbFake()

    analises = [
        SimpleNamespace(
            id=1,
            nome_arquivo="img.jpg",
            hash_arquivo="hash123",
            data_analise=datetime(2026, 4, 26, 10, 30, 0),
            resultado_final="Pavimento em bom estado",
            observacao="ok",
            modelo_mais_confiante="random_forest",
            confianca=0.91,
            detalhes_modelos=json.dumps(
                {"random_forest": {"classe": "Não Rachado", "probabilidade": 0.91}}
            ),
        )
    ]

    monkeypatch.setattr(analise_routes, "SessionLocal", lambda: db_fake)
    monkeypatch.setattr(analise_routes, "listar_analises", lambda db: analises)

    response = client.get("/analise/historico")

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["id_analise"] == 1
    assert body[0]["arquivo"] == "img.jpg"
    assert body[0]["modelos"]["random_forest"]["classe"] == "Não Rachado"
    assert db_fake.fechado is True


def test_get_historico_com_json_invalido(monkeypatch):
    class DbFake:
        def close(self):
            pass

    analises = [
        SimpleNamespace(
            id=1,
            nome_arquivo="img.jpg",
            hash_arquivo="hash123",
            data_analise=datetime(2026, 4, 26, 10, 30, 0),
            resultado_final="Pavimento em bom estado",
            observacao=None,
            modelo_mais_confiante="random_forest",
            confianca=0.91,
            detalhes_modelos="{json invalido",
        )
    ]

    monkeypatch.setattr(analise_routes, "SessionLocal", lambda: DbFake())
    monkeypatch.setattr(analise_routes, "listar_analises", lambda db: analises)

    response = client.get("/analise/historico")

    assert response.status_code == 200
    assert response.json()[0]["modelos"] is None