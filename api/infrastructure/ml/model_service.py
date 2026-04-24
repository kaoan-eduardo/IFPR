from __future__ import annotations

import numpy as np

from api.infrastructure.ml.predict import prever_imagem


class ModelService:
    def prever(self, imagem: np.ndarray) -> dict:
        return prever_imagem(imagem)