"""Crea un modelo dummy (NO entrenado) para probar el backend."""
from pathlib import Path

from tensorflow.keras import layers, models
from tensorflow.keras.applications import MobileNetV2


def main():
    out = Path("models/mobilenetv2_waste.h5")
    out.parent.mkdir(parents=True, exist_ok=True)

    base = MobileNetV2(
        weights="imagenet",
        include_top=False,
        input_shape=(224, 224, 3),
    )
    base.trainable = False

    model = models.Sequential([
        base,
        layers.GlobalAveragePooling2D(),
        layers.Dropout(0.2),
        layers.Dense(5, activation="softmax"),  # 5 clases
    ])
    model.compile(optimizer="adam", loss="categorical_crossentropy")

    model.save(str(out))
    print(f"✅ Modelo mock guardado en {out}")
    print("⚠️  Este modelo NO está entrenado. Solo sirve para probar el API.")


if __name__ == "__main__":
    main()