from __future__ import annotations

import sys
from functools import lru_cache
from pathlib import Path
from typing import Any

ROOT_DIR = Path(__file__).resolve().parents[3]

if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

import joblib
import numpy as np

from src.config import (
    CLASS_CRACKED,
    CLASS_NOT_CRACKED,
    MODEL_FILES,
)
from src.core.features import extrair_features


def _resultado_erro_modelo(mensagem: str) -> dict[str, Any]:
    return {
        "classe_bruta": None,
        "classe": "Erro",
        "probabilidade": 0.0,
        "prob_ruim": 0.0,
        "prob_bom": 0.0,
        "erro": mensagem,
    }


@lru_cache(maxsize=1)
def carregar_modelos() -> dict[str, Any]:
    modelos: dict[str, Any] = {}

    for nome_modelo, caminho_modelo in MODEL_FILES.items():
        caminho = ROOT_DIR / caminho_modelo

        if not caminho.exists():
            continue

        obj = joblib.load(caminho)

        if hasattr(obj, "predict"):
            modelos[nome_modelo] = obj

    if not modelos:
        raise FileNotFoundError("Nenhum modelo válido foi encontrado na pasta de modelos.")

    return modelos


def interpretar_classe(predicao: Any) -> str:
    predicao_str = str(predicao).strip().lower()

    if predicao_str == "ruim":
        return CLASS_CRACKED

    if predicao_str == "bom":
        return CLASS_NOT_CRACKED

    return str(predicao)


def prever_imagem(imagem: np.ndarray) -> dict[str, Any]:
    if imagem is None:
        return {"erro": "Imagem inválida ou não carregada."}

    try:
        features = np.asarray(extrair_features(imagem), dtype=np.float32).reshape(1, -1)
    except Exception as exc:
        return {"erro": f"Erro ao extrair features: {exc}"}

    try:
        modelos = carregar_modelos()
    except Exception as exc:
        return {"erro": f"Erro ao carregar modelos: {exc}"}

    resultados: dict[str, Any] = {}

    for nome_modelo, pipeline in modelos.items():
        try:
            pred = pipeline.predict(features)[0]

            resultado = {
                "classe_bruta": str(pred),
                "classe": interpretar_classe(pred),
                "probabilidade": 0.0,
                "prob_ruim": 0.0,
                "prob_bom": 0.0,
            }

            if hasattr(pipeline, "predict_proba") and hasattr(pipeline, "classes_"):
                prob = pipeline.predict_proba(features)[0]
                classes = [str(classe) for classe in pipeline.classes_]

                if "ruim" in classes:
                    idx_ruim = classes.index("ruim")
                    resultado["prob_ruim"] = float(prob[idx_ruim])

                if "bom" in classes:
                    idx_bom = classes.index("bom")
                    resultado["prob_bom"] = float(prob[idx_bom])

                pred_str = str(pred)

                if pred_str in classes:
                    idx_pred = classes.index(pred_str)
                    resultado["probabilidade"] = float(prob[idx_pred])

            resultados[nome_modelo] = resultado

        except Exception as exc:
            resultados[nome_modelo] = _resultado_erro_modelo(str(exc))

    return resultados