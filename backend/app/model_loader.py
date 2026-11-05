"""Carga del modelo y ejecución de inferencia (Sección 9.4 del documento)."""
import logging
import time
from functools import lru_cache
from typing import Dict

import numpy as np
from PIL import Image

from app import config

logger = logging.getLogger(__name__)

# ─── Importación diferida de TensorFlow (evita arranque lento si falla) ───
try:
    from tensorflow.keras.models import load_model
    from tensorflow.keras.applications.mobilenet_v2 import (
        preprocess_input as mobilenet_preprocess,
    )
    from tensorflow.keras.applications.resnet50 import (
        preprocess_input as resnet_preprocess,
    )
    TF_AVAILABLE = True
except ImportError:  # pragma: no cover
    TF_AVAILABLE = False
    logger.warning("TensorFlow no disponible. La inferencia fallará.")

# Mapa de funciones de preprocesamiento según el modelo
_PREPROCESS_MAP = {
    "MobileNetV2": mobilenet_preprocess,
    "ResNet50":    resnet_preprocess,
}


@lru_cache(maxsize=1)
def get_model():
    """
    Carga el modelo una sola vez y lo mantiene en memoria.
    Llamado al arrancar (lifespan) para cumplir NFR-04 (≤ 30 s).
    """
    if not TF_AVAILABLE:
        raise RuntimeError("TensorFlow no está instalado. Ejecute: pip install tensorflow-cpu")

    if not config.MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Modelo no encontrado en {config.MODEL_PATH}. "
            "Ejecuta scripts/create_mock_model.py o entrena el modelo real."
        )

    logger.info(f"Cargando modelo desde: {config.MODEL_PATH}")
    model = load_model(str(config.MODEL_PATH))
    logger.info(f"Modelo '{config.MODEL_NAME}' cargado correctamente.")
    return model


def preprocess_image(image: Image.Image) -> np.ndarray:
    """Redimensiona, normaliza y prepara la imagen para inferencia."""
    img = image.convert("RGB").resize((config.INPUT_SIZE, config.INPUT_SIZE))
    arr = np.array(img, dtype=np.float32)
    arr = np.expand_dims(arr, axis=0)   # (1, 224, 224, 3)

    # FIX: Usamos la misma normalización que en el entrenamiento (0 a 1)
    arr = arr / 255.0

    return arr


def predict(image: Image.Image) -> Dict:
    """
    Ejecuta la inferencia y devuelve el diccionario con la predicción
    (contrato de la Sección 7.2 del SRS).
    """
    model = get_model()
    arr = preprocess_image(image)

    start = time.perf_counter()
    probs = model.predict(arr, verbose=0)[0]
    elapsed_ms = int((time.perf_counter() - start) * 1000)

    idx = int(np.argmax(probs))
    clase = config.CLASSES[idx]
    confianza = float(probs[idx])

    probabilidades = {
        cls: round(float(p), 4) for cls, p in zip(config.CLASSES, probs)
    }

    return {
        "clase": clase,
        "clase_etiqueta": config.CLASSES_LABELS_ES[clase],
        "confianza": round(confianza, 4),
        "probabilidades": probabilidades,
        "color_disposicion": config.CLASSES_COLORS[clase],
        "advertencia": confianza < config.LOW_CONFIDENCE_THRESHOLD,
        "modelo": config.MODEL_NAME,
        "tiempo_inferencia_ms": elapsed_ms,
    }