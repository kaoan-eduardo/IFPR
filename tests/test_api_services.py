from __future__ import annotations

import io

import numpy as np
import pytest
from PIL import Image

from api.domain.services.resultado_service import ResultadoService
from api.infrastructure.image.image_service import ImageService
from api.infrastructure.ml.model_service import ModelService
from api.infrastructure.ml import predict


def test_image_service_carregar_retorna_array_bgr():
    imagem = Image.new("RGB", (10, 10), color=(255, 0, 0))
    buffer = io.BytesIO()
    imagem.save(buffer, format="PNG")

    resultado = ImageService().carregar(buffer.getvalue())

    assert isinstance(resultado, np.ndarray)
    assert resultado.shape == (10, 10, 3)


def test_model_service_chama_prever_imagem(monkeypatch):
    imagem = np.zeros((10, 10, 3), dtype=np.uint8)

    monkeypatch.setattr(
        "api.infrastructure.ml.model_service.prever_imagem",
        lambda img: {"random_forest": {"classe": "Rachado", "probabilidade": 0.9}},
    )

    resultado = ModelService().prever(imagem)

    assert resultado["random_forest"]["classe"] == "Rachado"


def test_resultado_service_processar():
    resultados = {
        "random_forest": {"classe": "Rachado", "probabilidade": 0.9},
        "svm": {"classe": "Rachado", "probabilidade": 0.8},
        "knn": {"classe": "Não Rachado", "probabilidade": 0.7},
    }

    resultado = ResultadoService().processar(resultados)

    assert resultado["resultado_final"] == "Pavimento com rachaduras detectadas"
    assert resultado["modelo_mais_confiante"] == "random_forest"
    assert resultado["confianca"] == 0.9
    assert resultado["modelos"] == resultados


def test_interpretar_classe_api_predict():
    assert predict.interpretar_classe("ruim") == "Rachado"
    assert predict.interpretar_classe("bom") == "Não Rachado"
    assert predict.interpretar_classe("x") == "x"


def test_prever_imagem_retorna_erro_para_imagem_none():
    resultado = predict.prever_imagem(None)

    assert resultado == {"erro": "Imagem inválida ou não carregada."}


def test_prever_imagem_retorna_erro_ao_extrair_features(monkeypatch):
    imagem = np.zeros((10, 10, 3), dtype=np.uint8)

    def extrair_features_erro(img):
        raise ValueError("falha features")

    monkeypatch.setattr(predict, "extrair_features", extrair_features_erro)

    resultado = predict.prever_imagem(imagem)

    assert "erro" in resultado
    assert "Erro ao extrair features" in resultado["erro"]


def test_prever_imagem_retorna_erro_ao_carregar_modelos(monkeypatch):
    imagem = np.zeros((10, 10, 3), dtype=np.uint8)

    monkeypatch.setattr(
        predict,
        "extrair_features",
        lambda img: np.array([1.0, 2.0], dtype=np.float32),
    )

    def carregar_modelos_erro():
        raise FileNotFoundError("sem modelos")

    monkeypatch.setattr(predict, "carregar_modelos", carregar_modelos_erro)

    resultado = predict.prever_imagem(imagem)

    assert "erro" in resultado
    assert "Erro ao carregar modelos" in resultado["erro"]


def test_prever_imagem_com_modelo_mockado(monkeypatch):
    class ModeloFake:
        classes_ = np.array(["bom", "ruim"])

        def predict(self, X):
            return np.array(["ruim"])

        def predict_proba(self, X):
            return np.array([[0.2, 0.8]])

    imagem = np.zeros((10, 10, 3), dtype=np.uint8)

    monkeypatch.setattr(
        predict,
        "extrair_features",
        lambda img: np.array([1.0, 2.0], dtype=np.float32),
    )
    monkeypatch.setattr(
        predict,
        "carregar_modelos",
        lambda: {"random_forest": ModeloFake()},
    )

    resultado = predict.prever_imagem(imagem)

    assert resultado["random_forest"]["classe"] == "Rachado"
    assert resultado["random_forest"]["probabilidade"] == pytest.approx(0.8)
    assert resultado["random_forest"]["prob_ruim"] == pytest.approx(0.8)
    assert resultado["random_forest"]["prob_bom"] == pytest.approx(0.2)


def test_prever_imagem_registra_erro_por_modelo(monkeypatch):
    class ModeloComErro:
        def predict(self, X):
            raise RuntimeError("modelo falhou")

    imagem = np.zeros((10, 10, 3), dtype=np.uint8)

    monkeypatch.setattr(
        predict,
        "extrair_features",
        lambda img: np.array([1.0, 2.0], dtype=np.float32),
    )
    monkeypatch.setattr(
        predict,
        "carregar_modelos",
        lambda: {"svm": ModeloComErro()},
    )

    resultado = predict.prever_imagem(imagem)

    assert resultado["svm"]["classe"] == "Erro"
    assert resultado["svm"]["probabilidade"] == 0.0
    assert "erro" in resultado["svm"]