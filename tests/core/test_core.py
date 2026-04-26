from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np
import pytest

from src.core import dataset, features, predict


def test_listar_imagens_pasta_retorna_apenas_imagens_validas(tmp_path: Path):
    (tmp_path / "img1.jpg").write_bytes(b"fake")
    (tmp_path / "img2.png").write_bytes(b"fake")
    (tmp_path / "documento.txt").write_text("teste", encoding="utf-8")

    arquivos = dataset.listar_imagens_pasta(tmp_path)

    nomes = sorted(arquivo.name for arquivo in arquivos)

    assert nomes == ["img1.jpg", "img2.png"]


def test_listar_imagens_pasta_retorna_lista_vazia_se_pasta_nao_existe(tmp_path: Path):
    pasta_inexistente = tmp_path / "nao_existe"

    assert dataset.listar_imagens_pasta(pasta_inexistente) == []


def test_carregar_dataset_carrega_features(monkeypatch, tmp_path: Path):
    pasta_bom = tmp_path / "bom"
    pasta_ruim = tmp_path / "ruim"
    pasta_bom.mkdir()
    pasta_ruim.mkdir()

    (pasta_bom / "bom.jpg").write_bytes(b"fake")
    (pasta_ruim / "ruim.jpg").write_bytes(b"fake")

    monkeypatch.setattr(
        dataset.cv2,
        "imread",
        lambda caminho: np.zeros((32, 32, 3), dtype=np.uint8),
    )

    monkeypatch.setattr(
        dataset,
        "extrair_features",
        lambda imagem: np.array([1.0, 2.0, 3.0], dtype=np.float32),
    )

    X, y = dataset.carregar_dataset(tmp_path)

    assert X.shape == (2, 3)
    assert set(y.tolist()) == {"bom", "ruim"}


def test_carregar_dataset_gera_erro_quando_pasta_classe_nao_existe(tmp_path: Path):
    (tmp_path / "bom").mkdir()

    with pytest.raises(FileNotFoundError):
        dataset.carregar_dataset(tmp_path)


def test_carregar_dataset_gera_erro_quando_nao_tem_imagem_valida(monkeypatch, tmp_path: Path):
    pasta_bom = tmp_path / "bom"
    pasta_ruim = tmp_path / "ruim"
    pasta_bom.mkdir()
    pasta_ruim.mkdir()

    (pasta_bom / "bom.jpg").write_bytes(b"fake")
    (pasta_ruim / "ruim.jpg").write_bytes(b"fake")

    monkeypatch.setattr(dataset.cv2, "imread", lambda caminho: None)

    with pytest.raises(ValueError):
        dataset.carregar_dataset(tmp_path)


def test_carregar_imagem_retorna_imagem_valida(tmp_path: Path):
    caminho = tmp_path / "imagem.png"
    imagem = np.zeros((20, 20, 3), dtype=np.uint8)

    cv2.imwrite(str(caminho), imagem)

    resultado = features.carregar_imagem(str(caminho))

    assert isinstance(resultado, np.ndarray)
    assert resultado.shape == (20, 20, 3)


def test_carregar_imagem_gera_erro_para_caminho_invalido():
    with pytest.raises(ValueError):
        features.carregar_imagem("imagem_inexistente.jpg")


def test_converter_para_cinza_retorna_imagem_2d():
    imagem = np.zeros((20, 20, 3), dtype=np.uint8)

    gray = features.converter_para_cinza(imagem)

    assert gray.ndim == 2
    assert gray.shape == (20, 20)


def test_extrair_lbp_gray_retorna_histograma_normalizado():
    gray = np.random.randint(0, 255, (32, 32), dtype=np.uint8)

    hist = features.extrair_lbp_gray(gray)

    assert isinstance(hist, np.ndarray)
    assert hist.dtype == np.float32
    assert hist.ndim == 1
    assert hist.sum() == pytest.approx(1.0, rel=1e-3)


def test_extrair_haralick_gray_retorna_vetor():
    gray = np.random.randint(0, 255, (32, 32), dtype=np.uint8)

    vetor = features.extrair_haralick_gray(gray)

    assert isinstance(vetor, np.ndarray)
    assert vetor.dtype == np.float32
    assert vetor.ndim == 1
    assert vetor.size > 0


def test_extrair_features_comuns_gray_retorna_10_features():
    gray = np.random.randint(0, 255, (32, 32), dtype=np.uint8)

    vetor = features.extrair_features_comuns_gray(gray)

    assert isinstance(vetor, np.ndarray)
    assert vetor.dtype == np.float32
    assert vetor.shape == (10,)


def test_extrair_features_retorna_vetor_final():
    imagem = np.random.randint(0, 255, (32, 32, 3), dtype=np.uint8)

    vetor = features.extrair_features(imagem)

    assert isinstance(vetor, np.ndarray)
    assert vetor.dtype == np.float32
    assert vetor.ndim == 1
    assert vetor.size >= 20


def test_interpretar_classe_ruim():
    assert predict.interpretar_classe("ruim") == "Rachado"


def test_interpretar_classe_bom():
    assert predict.interpretar_classe("bom") == "Não Rachado"


def test_interpretar_classe_desconhecida():
    assert predict.interpretar_classe("outra") == "outra"


def test_prever_imagem_retorna_erro_quando_imagem_invalida(monkeypatch):
    monkeypatch.setattr(predict.cv2, "imread", lambda caminho: None)

    resultado = predict.prever_imagem("invalida.jpg")

    assert "erro" in resultado


def test_prever_imagem_com_modelo_mockado(monkeypatch):
    class ModeloFake:
        classes_ = np.array(["bom", "ruim"])

        def predict(self, X):
            return np.array(["ruim"])

        def predict_proba(self, X):
            return np.array([[0.2, 0.8]])

    monkeypatch.setattr(
        predict.cv2,
        "imread",
        lambda caminho: np.zeros((32, 32, 3), dtype=np.uint8),
    )

    monkeypatch.setattr(
        predict,
        "extrair_features",
        lambda imagem: np.array([1.0, 2.0, 3.0], dtype=np.float32),
    )

    monkeypatch.setattr(
        predict,
        "carregar_modelos",
        lambda: {"random_forest": ModeloFake()},
    )

    resultado = predict.prever_imagem("imagem.jpg")

    assert "random_forest" in resultado
    assert resultado["random_forest"]["classe"] == "Rachado"
    assert resultado["random_forest"]["probabilidade"] == pytest.approx(0.8)
    assert resultado["random_forest"]["prob_ruim"] == pytest.approx(0.8)
    assert resultado["random_forest"]["prob_bom"] == pytest.approx(0.2)