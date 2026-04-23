from __future__ import annotations

from pathlib import Path

# =========================
# BASE DO PROJETO
# =========================
BASE_DIR = Path(__file__).resolve().parent.parent

# =========================
# PASTAS PRINCIPAIS
# =========================
ASSETS_DIR = BASE_DIR / "assets"
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
DATASET_DIR = RAW_DATA_DIR / "dataset"
SAMPLES_DIR = DATA_DIR / "samples"
SPREADSHEETS_DIR = DATA_DIR / "spreadsheets"

MODELS_DIR = BASE_DIR / "models"
RESULTS_DIR = BASE_DIR / "results"

# =========================
# ARQUIVOS
# =========================
LOGO_PATH = ASSETS_DIR / "logo_ifpr_icon.png"
METRICS_FILE_PATH = RESULTS_DIR / "metricas_cross_validation.xlsx"

# =========================
# APP
# =========================
APP_TITLE = "IFPR — Identificação de Fissuras em Pavimentos Rodoviários"
APP_ICON = "🛣️"
APP_LAYOUT = "wide"

# =========================
# CLASSES
# =========================
CLASS_CRACKED = "Rachado"
CLASS_NOT_CRACKED = "Não Rachado"
INVALID_IMAGE_LABEL = "Imagem inválida"

# =========================
# MODELOS
# =========================
MODEL_FILES = {
    "decision_tree": MODELS_DIR / "decision_tree.pkl",
    "knn": MODELS_DIR / "knn.pkl",
    "random_forest": MODELS_DIR / "random_forest.pkl",
    "svm": MODELS_DIR / "svm.pkl",
}

MODEL_DISPLAY_NAMES = {
    "decision_tree": "🌳 Árvore de Decisão",
    "knn": "📍 K-Nearest Neighbors",
    "random_forest": "🌲 Random Forest",
    "svm": "📈 SVM",
}

# =========================
# UPLOAD
# =========================
ALLOWED_IMAGE_EXTENSIONS = ["jpg", "jpeg", "png", "bmp", "webp", "tif", "tiff"]

# =========================
# LIMITES DE UI
# =========================
LIMITE_GALERIA = 60
LIMITE_DETALHAMENTO = 20
LIMITE_GALERIA_COMPLETA = 100