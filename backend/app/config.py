"""Configuración centralizada del backend (lee de .env)."""
import os
from pathlib import Path
from typing import Dict, List, Set

from dotenv import load_dotenv

load_dotenv()

# ─── Rutas ───────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = Path(os.getenv("MODEL_PATH", BASE_DIR / "models" / "mobilenetv2_waste.h5"))

# ─── Modelo ──────────────────────────────────────
MODEL_NAME = os.getenv("MODEL_NAME", "MobileNetV2")   # "MobileNetV2" | "ResNet50"
INPUT_SIZE = int(os.getenv("INPUT_SIZE", 224))

# ─── Clases (el ORDEN debe coincidir con el entrenamiento) ────
CLASSES: List[str] = ["biological", "cardboard", "metal", "paper", "plastic"]

CLASSES_LABELS_ES: Dict[str, str] = {
    "biological": "Biológicos",
    "cardboard":  "Cartón",
    "metal":      "Metal",
    "paper":      "Papel",
    "plastic":    "Plástico",
}

# Colores según Resolución 2184 de 2019 
CLASSES_COLORS: Dict[str, str] = {
    "biological": "verde",
    "cardboard":  "blanco",
    "metal":      "blanco",
    "paper":      "blanco",
    "plastic":    "blanco",
}

# ─── Validación de archivos  ─────
MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", 5))
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
ALLOWED_MIME_TYPES: Set[str] = {"image/jpeg", "image/png", "image/webp"}

# ─── Umbral de confianza  ─────────────────
LOW_CONFIDENCE_THRESHOLD = float(os.getenv("LOW_CONFIDENCE_THRESHOLD", 0.60))

# ─── CORS  ───────────────────────────────
ALLOWED_ORIGINS: List[str] = [
    o.strip() for o in os.getenv(
        "ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:5173"
    ).split(",") if o.strip()
]