from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np

from src.config import DATASET_DIR
from src.core.features import extrair_features


CLASS_NAMES = ("bom", "ruim")
VALID_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tif", ".tiff"}


def listar_imagens_pasta(pasta: Path) -> list[Path]:
    if not pasta.exists():
        return []

    return [
        arquivo
        for arquivo in pasta.iterdir()
        if arquivo.is_file() and arquivo.suffix.lower() in VALID_IMAGE_EXTENSIONS
    ]


def carregar_dataset(dataset_dir: Path = DATASET_DIR) -> tuple[np.ndarray, np.ndarray]:
    X: list[np.ndarray] = []
    y: list[str] = []

    for nome_classe in CLASS_NAMES:
        pasta_classe = dataset_dir / nome_classe

        if not pasta_classe.exists():
            raise FileNotFoundError(f"Pasta não encontrada: {pasta_classe}")

        for caminho_imagem in listar_imagens_pasta(pasta_classe):
            imagem = cv2.imread(str(caminho_imagem))

            if imagem is None:
                continue

            try:
                features = extrair_features(imagem)
            except Exception as exc:
                print(f"[AVISO] Falha ao extrair features de {caminho_imagem.name}: {exc}")
                continue

            X.append(features)
            y.append(nome_classe)

    if not X:
        raise ValueError("Nenhuma imagem válida foi carregada do dataset.")

    return np.asarray(X, dtype=np.float32), np.asarray(y, dtype=object)