<div align="center">
  <h1> Clasificador de Residuos IA </h1>
  <p>PROTOTIPO WEB PARA LA CLASIFICACIÓN DE RESIDUOS MEDIANTE RECONOCIMIENTO DE IMÁGENES E INTELIGENCIA ARTIFICIAL
.</p>

  <!-- Badges / Insignias -->
  <p>
    <img src="https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB" alt="React" />
    <img src="https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white" alt="Tailwind" />
    <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
    <img src="https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi" alt="FastAPI" />
    <img src="https://img.shields.io/badge/TensorFlow-FF6F00?style=for-the-badge&logo=tensorflow&logoColor=white" alt="TensorFlow" />
    <img src="https://img.shields.io/badge/Vercel-000000?style=for-the-badge&logo=vercel&logoColor=white" alt="Vercel" />
    <img src="https://img.shields.io/badge/Render-46E3B7?style=for-the-badge&logo=render&logoColor=white" alt="Render" />
  </p>
</div>

---
## Link web:https://ia-clasificador-de-residuos.vercel.app/

## 📋 Tabla de Contenidos
1. [Descripción del Proyecto](#-descripción-del-proyecto)
2. [Características Principales](#-características-principales)
3. [Arquitectura y Tecnologías](#-arquitectura-y-tecnologías)
4. [ Deep Dive: Entrenamiento del Modelo de IA](#-deep-dive-entrenamiento-del-modelo-de-ia)
5. [Cronograma del Proyecto (Roadmap)](#️-cronograma-del-proyecto-roadmap)
6. [Despliegue en la Nube](#-despliegue-en-la-nube)
7. [Ética, Privacidad y Normativa](#-ética-privacidad-y-normativa)
8. [Autores](#-autores)

---

## 🌱 Descripción del Proyecto
El **Clasificador de Residuos IA** es una aplicación web Full-Stack que permite a los usuarios identificar el tipo de residuo que tienen en sus manos (biológicos, metal, cartón, papel o plástico) utilizando la cámara de su computador o subiendo una fotografía. 

El sistema procesa la imagen en el backend mediante un modelo de Deep Learning y devuelve la categoría predicha junto con su nivel de confianza y el color de la caneca correspondiente según la normativa colombiana.

## ✨ Características Principales
- **Captura en tiempo real:** Integración con la API `MediaDevices` para usar la cámara web.
- **Carga de archivos:** Opción alternativa para subir imágenes locales.
- **Sistema de Confianza:** Si la IA predice con menos del 60% de seguridad, el sistema despliega una alerta amarilla advirtiendo al usuario que verifique manualmente.
- **Privacidad por diseño:** Las imágenes se procesan en memoria volátil y nunca se almacenan en disco (Cumplimiento de la Ley 1581 de 2012).
- **Despliegue Serverless/Cloud:** Backend contenerizado en Docker y Frontend estático en CDN.

## 🏗️ Arquitectura y Tecnologías
El proyecto sigue una arquitectura Cliente-Servidor separada:

- **Frontend:** React (Vite), Tailwind CSS, Axios, `react-webcam`.
- **Backend:** Python 3.12, FastAPI, Uvicorn, Docker.
- **Inteligencia Artificial:** TensorFlow/Keras 2.21, MobileNetV2 (Transfer Learning), OpenCV/Pillow.
## 📁 Estructura del Proyecto
```text
PROYECTO_IA/
├── backend/               # Código fuente del servidor (FastAPI)
│   ├── app/               # Módulos de la API
│   ├── models/            # Modelo entrenado (.keras)
│   ├── Dockerfile         # Configuración para Render
│   └── requirements.txt   # Dependencias de Python
└── frontend/              # Código fuente de la interfaz (React)
    ├── src/               # Componentes y lógica
    └── package.json       # Dependencias de Node.js
```
## 🧠 Deep Dive: Entrenamiento del Modelo de IA

Esta sección documenta el proceso técnico de construcción del modelo de Visión por Computadora.

### 1. Dataset y Preprocesamiento
- **Fuente:** Kaggle.
- **Total de imágenes:** 5.973 (5 clases: `biological`, `cardboard`, `metal`, `paper`, `plastic`).
- **Partición:** 
  - Entrenamiento: 4.181 imágenes (70%)
  - Validación: 896 imágenes (15%)
  - Prueba: 896 imágenes (15%)
- **Aumentación de Datos (Data Augmentation):** Rotación (±20°), volteo horizontal, zoom (15%), y variación de brillo. Esto ayuda a que el modelo no memorice las imágenes (evita el sobreajuste).
- **Manejo del Desbalance:** Se calcularon **Pesos de Clase** . La clase `biological` tenía menos imágenes (699), por lo que sus errores pesaron más (1.71) durante el entrenamiento para equilibrar el aprendizaje.

### 2. Arquitectura y Hiperparámetros
Se utilizó **MobileNetV2** preentrenado en ImageNet, adaptando su capa de salida a nuestras 5 clases.
- **Fase 1 (Feature Extraction):** Base convolucional congelada. 
  - *Optimizador:* Adam (LR = 1e-3)
  - *Épocas:* 10
  - *Batch Size:* 32
- **Fase 2 (Fine-Tuning):** Descongelamiento de las últimas 30 capas de la red base.
  - *Optimizador:* Adam (LR = 1e-5)
  - *Épocas:* 10
- **Callbacks:** `EarlyStopping` (paciencia de 5 épocas) para detener el entrenamiento si el modelo dejaba de mejorar en validación.

### 3. Resultados y Métricas 
- **Accuracy Global:** ~72%
- **F1-Macro:** 0.72
- **Matriz de Confusión:** El modelo es altamente preciso identificando plástico (F1: 0.78) y biológicos (F1: 0.83). Presenta confusiones lógicas entre **cartón y papel** (texturas visuales similares) y entre metal y plástico.
- **Nota sobre Limitaciones:** Durante las pruebas reales, se detectó *Domain Shift* (el modelo se confunde con fondos oscuros o texturas atípicas). Por ello, se implementó un umbral de rechazo: si la confianza es < 60%, la app web muestra una alerta al usuario.

## 🗺️ Cronograma del Proyecto 

El proyecto tiene una duracion de  **13 semanas** (28 de agosto al 25 de noviembre). 

### Gráfico 
```mermaid
gantt
    title Cronograma del Proyecto - 13 Semanas
    dateFormat YYYY-MM-DD
    section Fases
    F1 Propuesta inicial          :done, des1, 2026-08-28, 2026-09-17
    F2 Requerimientos y Dataset   :done, des2, 2026-09-18, 2026-10-01
    F3 Arquitectura y Modelo      :done, des3, 2026-10-02, 2026-10-08
    F4 Entrenamiento de IA        :done, des4, 2026-10-09, 2026-10-15
    F5 Desarrollo y Despliegue    :active, des5, 2026-10-16, 2026-10-29
    F6 Pruebas y Sustentación     : des6, 2026-10-30, 2026-11-25
```
## ☁️ Despliegue en la Nube

El proyecto está preparado para producción usando servicios gratuitos:

**Backend (Render):** Se despliega utilizando un `Dockerfile (Python 3.12-slim)`. Nota: El plan gratuito de Render `"duerme"` el servicio tras 15 min de inactividad, tardando hasta 60s en la primera petición.

**Frontend (Vercel):** Se despliega automáticamente mediante integración continua conectada a este repositorio. Vercel genera HTTPS automático, lo cual es obligatorio para que los navegadores permitan el acceso a la cámara web (`getUserMedia`).

## 🛡️ Ética, Privacidad y Normativa

Este proyecto académico esto  diseñado bajo  principios éticos y legales:

**No Almacenamiento (Privacidad):** Las imágenes capturadas se procesan en memoria (`BytesIO`) y se destruyen tras la inferencia, en cumplimiento de la Ley 1581 de 2012 (Protección de Datos Personales).

**Transparencia Algorítmica:** El sistema muestra las probabilidades en tiempo real y advierte si la confianza es menor al 60%, evitando la "ceguera" del usuario ante errores de la IA.

**Normativa Ambiental:** Los colores de las canecas mostrados en el frontend están alineados con la Resolución 2184 de 2019 (Código de Colores Nacional: Verde para residuos orgánicos aprovechables, Blanco para residuos aprovechables).

## 👨‍💻 Autores
José Camilo Oyola

Juan David Villa

Juan Esteban Caucayo

**Institución:** Universidad Central - Facultad de Ingeniería y Ciencias Básicas
**Director del Proyecto:** Elias Buitrago Bolivar
**Año:** 2026





