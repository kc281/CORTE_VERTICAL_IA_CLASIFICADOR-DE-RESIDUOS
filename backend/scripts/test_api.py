"""Smoke test del backend. Ejecutar con el servidor corriendo en :8000."""
import io
import sys

import requests
from PIL import Image

BASE = "http://localhost:8000"


def make_test_image() -> io.BytesIO:
    img = Image.new("RGB", (300, 300), color=(180, 120, 60))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    buf.seek(0)
    buf.name = "test.jpg"
    return buf


def test_health():
    r = requests.get(f"{BASE}/health", timeout=5)
    assert r.status_code == 200, r.text
    print("✅ /health OK:", r.json())


def test_model_info():
    r = requests.get(f"{BASE}/model-info", timeout=5)
    assert r.status_code == 200, r.text
    print("✅ /model-info OK:", r.json()["modelo"])


def test_predict():
    files = {"file": ("test.jpg", make_test_image(), "image/jpeg")}
    r = requests.post(f"{BASE}/predict", files=files, timeout=15)
    assert r.status_code == 200, r.text
    data = r.json()
    print(f"✅ /predict OK: clase={data['clase']} confianza={data['confianza']}")
    assert "probabilidades" in data and len(data["probabilidades"]) == 5


def test_invalid_file():
    files = {"file": ("test.txt", b"no soy imagen", "text/plain")}
    r = requests.post(f"{BASE}/predict", files=files, timeout=5)
    assert r.status_code == 400, r.text
    print("✅ Rechazo de formato inválido OK:", r.json()["error"])


if __name__ == "__main__":
    try:
        test_health()
        test_model_info()
        test_predict()
        test_invalid_file()
        print("\n🎉 Todos los tests pasaron.")
    except Exception as exc:
        print(f"\n❌ Falló: {exc}")
        sys.exit(1)