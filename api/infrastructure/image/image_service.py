from __future__ import annotations

import io

import cv2
import numpy as np
from PIL import Image


class ImageService:
    def carregar(self, conteudo: bytes) -> np.ndarray:
        imagem = Image.open(io.BytesIO(conteudo)).convert("RGB")
        imagem_np = np.array(imagem)

        return cv2.cvtColor(imagem_np, cv2.COLOR_RGB2BGR)