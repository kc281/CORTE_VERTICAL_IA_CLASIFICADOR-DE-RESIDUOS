# Usamos una imagen ligera de Python
FROM python:3.12-slim

# Evita que Python escriba archivos .pyc y permite ver logs en tiempo real
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

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