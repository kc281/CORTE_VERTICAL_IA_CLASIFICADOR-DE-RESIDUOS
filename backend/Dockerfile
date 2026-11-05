# Usamos una imagen ligera de Python
FROM python:3.11-slim

# Evita que Python escriba archivos .pyc y permite ver logs en tiempo real
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
# ... después de tus ENV existentes ...
# Desactiva las optimizaciones oneDNN que causan Segmentation Fault en algunas CPUs
ENV TF_ENABLE_ONEDNN_OPTS=0
# Limita los hilos de CPU para evitar conflictos en entornos con recursos limitados
ENV TF_NUM_INTRAOP_THREADS=1
ENV TF_NUM_INTEROP_THREADS=1

WORKDIR /app

# Copiamos e instalamos dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el resto del código (incluyendo la carpeta models/ con .keras)
COPY . .

# Exponemos el puerto (Render usa la variable $PORT)
EXPOSE 8000

# Comando de arranque: 1 solo worker para ahorrar RAM
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1"]