"""Utilidades de validación de imágenes """
import logging
from io import BytesIO

from fastapi import HTTPException, UploadFile, status
from PIL import Image, UnidentifiedImageError

from app import config

logger = logging.getLogger(__name__)


async def validate_image(file: UploadFile) -> Image.Image:
    """
    Valida el archivo subido y devuelve un objeto PIL.Image en RGB.

    Aplica:
      - FR-09:  formato y tamaño permitidos
      - FR-19:  mensajes claros de error
      - NFR-10: límite de tamaño
      - NFR-11: tipo MIME permitido
    """
    # 1) Tipo MIME declarado por el cliente
    if file.content_type not in config.ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Formato no permitido. Use JPG, PNG o WEBP.",
        )

    # 2) Leer contenido (en memoria — nunca a disco)
    contents = await file.read()

    # 3) Validar tamaño
    if len(contents) > config.MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"El archivo supera el tamaño máximo de {config.MAX_FILE_SIZE_MB} MB.",
        )

    # 4) Validar que sea una imagen decodificable
    try:
        Image.open(BytesIO(contents)).verify()   # detecta archivos corruptos
        image = Image.open(BytesIO(contents)).convert("RGB")
    except (UnidentifiedImageError, Exception) as exc:
        logger.warning(f"Imagen inválida: {exc}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La imagen no pudo ser procesada. Verifique que el archivo sea válido.",
        )

    return image