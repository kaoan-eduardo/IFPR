from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import cv2
import joblib
import numpy as np

from src.config import (
    CLASS_CRACKED,
    CLASS_NOT_CRACKED,
    MODEL_FILES,
)
from src.core.features import extrair_features


@lru_cache(maxsize=1)
def carregar_modelos() -> dict:
    """
    Carrega todos os modelos disponíveis.
    Os .pkl já são pipelines treinados com scaler + modelo.
    """
    modelos = {}

    for nome_modelo, caminho_modelo in MODEL_FILES.items():
        caminho = Path(caminho_modelo)

        if not caminho.exists():
            continue

        obj = joblib.load(caminho)

        if hasattr(obj, "predict"):
            modelos[nome_modelo] = obj

    if not modelos:
        raise FileNotFoundError("Nenhum modelo válido foi encontrado na pasta de modelos.")

    return modelos


def interpretar_classe(predicao) -> str:
    """
    Converte a classe bruta do modelo em classe amigável.
    """
    if str(predicao) == "ruim":
        return CLASS_CRACKED
    return CLASS_NOT_CRACKED


def prever_imagem(caminho_imagem: str) -> dict:
    """
    Executa a predição da imagem em todos os modelos.
    """
    imagem = cv2.imread(caminho_imagem)

    if imagem is None:
        return {"erro": f"Erro ao carregar imagem: {caminho_imagem}"}

    try:
        features = np.asarray(extrair_features(imagem), dtype=np.float32).reshape(1, -1)
    except Exception as e:
        return {"erro": f"Erro ao extrair features: {e}"}

    try:
        modelos = carregar_modelos()
    except Exception as e:
        return {"erro": f"Erro ao carregar modelos: {e}"}

    resultados = {}

    for nome_modelo, pipeline in modelos.items():
        try:
            pred = pipeline.predict(features)[0]

            resultado = {
                "classe_bruta": str(pred),
                "classe": interpretar_classe(pred),
                "probabilidade": 0.0,
                "prob_ruim": 0.0,
                "prob_bom": 0.0
            }

            if hasattr(pipeline, "predict_proba"):
                prob = pipeline.predict_proba(features)[0]
                classes = list(pipeline.classes_)

                if "ruim" in classes:
                    idx_ruim = classes.index("ruim")
                    resultado["prob_ruim"] = float(prob[idx_ruim])

                if "bom" in classes:
                    idx_bom = classes.index("bom")
                    resultado["prob_bom"] = float(prob[idx_bom])

                idx_pred = classes.index(pred)
                resultado["probabilidade"] = float(prob[idx_pred])

            resultados[nome_modelo] = resultado

        except Exception as e:
            resultados[nome_modelo] = {
                "classe": "Erro",
                "probabilidade": 0.0,
                "erro": str(e)
            }

    return resultados