from __future__ import annotations

import hashlib


from api.application.use_cases import analisar_imagem


class DbFake:
    def __init__(self):
        self.fechado = False

    def close(self):
        self.fechado = True


class AnaliseFake:
    id = 123


def test_analisar_imagem_use_case_executar(monkeypatch):
    db_fake = DbFake()

    class ImageServiceFake:
        def carregar(self, conteudo):
            return "imagem_carregada"

    class ModelServiceFake:
        def prever(self, imagem):
            assert imagem == "imagem_carregada"
            return {
                "random_forest": {
                    "classe": "Rachado",
                    "probabilidade": 0.91,
                }
            }

    class ResultadoServiceFake:
        def processar(self, resultados):
            return {
                "resultado_final": "Pavimento com rachaduras detectadas",
                "observacao": "Recomenda-se inspeção ou manutenção.",
                "modelo_mais_confiante": "random_forest",
                "confianca": 0.91,
                "modelos": resultados,
            }

    def salvar_analise_fake(**kwargs):
        assert kwargs["hash_arquivo"] == hashlib.sha256(b"abc").hexdigest()
        assert kwargs["nome_arquivo"] == "teste.jpg"
        assert kwargs["resultado_final"] == "Pavimento com rachaduras detectadas"
        assert kwargs["modelo_mais_confiante"] == "random_forest"
        assert kwargs["confianca"] == 0.91
        return AnaliseFake()

    monkeypatch.setattr(analisar_imagem, "ImageService", ImageServiceFake)
    monkeypatch.setattr(analisar_imagem, "ModelService", ModelServiceFake)
    monkeypatch.setattr(analisar_imagem, "ResultadoService", ResultadoServiceFake)
    monkeypatch.setattr(analisar_imagem, "SessionLocal", lambda: db_fake)
    monkeypatch.setattr(analisar_imagem, "salvar_analise", salvar_analise_fake)

    use_case = analisar_imagem.AnalisarImagemUseCase()
    resultado = use_case.executar("teste.jpg", b"abc")

    assert resultado["status"] == "sucesso"
    assert resultado["id_analise"] == 123
    assert resultado["arquivo"] == "teste.jpg"
    assert resultado["hash_arquivo"] == hashlib.sha256(b"abc").hexdigest()
    assert resultado["resultado_final"] == "Pavimento com rachaduras detectadas"
    assert resultado["modelo_mais_confiante"] == "random_forest"
    assert resultado["confianca"] == 0.91
    assert db_fake.fechado is True


def test_analisar_imagem_use_case_fecha_db_mesmo_com_erro(monkeypatch):
    db_fake = DbFake()

    class ImageServiceFake:
        def carregar(self, conteudo):
            return "imagem"

    class ModelServiceFake:
        def prever(self, imagem):
            return {"random_forest": {"classe": "Rachado", "probabilidade": 0.9}}

    class ResultadoServiceFake:
        def processar(self, resultados):
            return {
                "resultado_final": "Pavimento com rachaduras detectadas",
                "observacao": None,
                "modelo_mais_confiante": "random_forest",
                "confianca": 0.9,
                "modelos": resultados,
            }

    def salvar_analise_erro(**kwargs):
        raise RuntimeError("falha ao salvar")

    monkeypatch.setattr(analisar_imagem, "ImageService", ImageServiceFake)
    monkeypatch.setattr(analisar_imagem, "ModelService", ModelServiceFake)
    monkeypatch.setattr(analisar_imagem, "ResultadoService", ResultadoServiceFake)
    monkeypatch.setattr(analisar_imagem, "SessionLocal", lambda: db_fake)
    monkeypatch.setattr(analisar_imagem, "salvar_analise", salvar_analise_erro)

    use_case = analisar_imagem.AnalisarImagemUseCase()

    try:
        use_case.executar("teste.jpg", b"abc")
    except RuntimeError:
        pass

    assert db_fake.fechado is True