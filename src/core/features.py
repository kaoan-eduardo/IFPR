from __future__ import annotations

import cv2
import mahotas
import numpy as np
from skimage.feature import graycomatrix, graycoprops, local_binary_pattern
from skimage.measure import shannon_entropy
from skimage.morphology import skeletonize


def carregar_imagem(caminho_imagem: str) -> np.ndarray:
    imagem = cv2.imread(caminho_imagem)

    if imagem is None:
        raise ValueError(f"Não foi possível carregar a imagem: {caminho_imagem}")

    return imagem


def converter_para_cinza(imagem: np.ndarray) -> np.ndarray:
    return cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)


def extrair_lbp_gray(gray: np.ndarray) -> np.ndarray:
    raio = 1
    pontos = 8 * raio

    lbp = local_binary_pattern(gray, pontos, raio, method="uniform")
    hist, _ = np.histogram(
        lbp.ravel(),
        bins=np.arange(0, pontos + 3),
        range=(0, pontos + 2),
    )

    hist = hist.astype(np.float32)
    hist /= (hist.sum() + 1e-6)

    return hist


def extrair_lbp(imagem: np.ndarray) -> np.ndarray:
    gray = converter_para_cinza(imagem)
    return extrair_lbp_gray(gray)


def extrair_haralick_gray(gray: np.ndarray) -> np.ndarray:
    haralick = mahotas.features.haralick(gray).mean(axis=0)
    return haralick.astype(np.float32)


def extrair_haralick(imagem: np.ndarray) -> np.ndarray:
    gray = converter_para_cinza(imagem)
    return extrair_haralick_gray(gray)


def extrair_features_comuns_gray(gray: np.ndarray) -> np.ndarray:
    gray_float = gray.astype(np.float32)

    mean_intensity = float(np.mean(gray))
    std_intensity = float(np.std(gray))

    media_local = cv2.blur(gray_float, (7, 7))
    local_contrast = float(np.mean(np.abs(gray_float - media_local)))

    edges = cv2.Canny(gray, 50, 150)
    edge_density = float(np.sum(edges > 0) / edges.size)

    grad_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
    grad_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
    gradient_magnitude = np.sqrt(grad_x**2 + grad_y**2)
    gradient_mean = float(np.mean(gradient_magnitude))

    entropy = float(shannon_entropy(gray))

    glcm = graycomatrix(
        gray,
        distances=[1],
        angles=[0],
        levels=256,
        symmetric=True,
        normed=True,
    )
    glcm_homogeneity = float(graycoprops(glcm, "homogeneity")[0, 0])

    _, thresh_dark = cv2.threshold(
        gray,
        0,
        255,
        cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU,
    )
    dark_pixel_ratio = float(np.sum(thresh_dark > 0) / thresh_dark.size)

    binario = thresh_dark > 0
    skeleton = skeletonize(binario)
    line_length = float(np.sum(skeleton))

    lbp_hist = extrair_lbp_gray(gray)
    lbp_uniformity = float(np.max(lbp_hist))

    return np.array(
        [
            mean_intensity,
            std_intensity,
            local_contrast,
            edge_density,
            gradient_mean,
            entropy,
            glcm_homogeneity,
            dark_pixel_ratio,
            line_length,
            lbp_uniformity,
        ],
        dtype=np.float32,
    )


def extrair_features_comuns(imagem: np.ndarray) -> np.ndarray:
    gray = converter_para_cinza(imagem)
    return extrair_features_comuns_gray(gray)


def extrair_features(imagem: np.ndarray) -> np.ndarray:
    gray = converter_para_cinza(imagem)

    features_comuns = extrair_features_comuns_gray(gray)
    lbp = extrair_lbp_gray(gray)
    haralick = extrair_haralick_gray(gray)

    return np.hstack([features_comuns, lbp, haralick]).astype(np.float32)


def extrair_features_de_arquivo(caminho_imagem: str) -> np.ndarray:
    imagem = carregar_imagem(caminho_imagem)
    return extrair_features(imagem)