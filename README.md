<div align="center">
  <h1> Corte Vertical: Arquitectura de Sistemas I</h1>
  <p><strong>Clasificador de Residuos IA con Persistencia y Módulo Estadístico </strong></p>
  
  <!-- Badges / Insignias -->
  <p>
    <img src="https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB" alt="React" />
    <img src="https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white" alt="Tailwind" />
    <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
    <img src="https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi" alt="FastAPI" />
    <img src="https://img.shields.io/badge/TensorFlow-FF6F00?style=for-the-badge&logo=tensorflow&logoColor=white" alt="TensorFlow" />
    <br/>
    <img src="https://img.shields.io/badge/Supabase-3ECF8E?style=for-the-badge&logo=supabase&logoColor=white" alt="Supabase" />
    <img src="https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white" alt="PostgreSQL" />
    <img src="https://img.shields.io/badge/Vercel-000000?style=for-the-badge&logo=vercel&logoColor=white" alt="Vercel" />
    <img src="https://img.shields.io/badge/Render-46E3B7?style=for-the-badge&logo=render&logoColor=white" alt="Render" />
    <img src="https://img.shields.io/badge/Docker-2CA5E0?style=for-the-badge&logo=docker&logoColor=white" alt="Docker" />
  </p>
</div>

---
## 🌐 Link:https://corte-vertical-ia-clasificador-de-r.vercel.app/

## 🫡 Integrantes:Jose Camilo Oyola , Juan David Villa , Juan Caucayo
---


---

## 📖 1. Descripción del Corte Vertical

Este repositorio contiene la implementación del **Corte Vertical** para la asignatura de **Arquitectura de Sistemas I**. El proyecto original consistía en un prototipo web para clasificar residuos mediante Inteligencia Artificial (sin base de datos). 

Para este corte, la arquitectura evolucionó de un modelo **Stateless** (sin estado) a un modelo **Stateful** (con estado), integrando una capa de persistencia en la nube y un módulo de observabilidad . El nuevo flujo transversal atraviesa todas las capas del sistema:

1.  **Captura:** El usuario sube o toma una foto desde el frontend .
2.  **Inferencia:** El backend (FastAPI) procesa la imagen con MobileNetV2.
3.  **Persistencia:** Se guardan los metadatos de la predicción en **Supabase** (PostgreSQL).
4.  **Observabilidad:** El usuario puede acceder a un Dashboard estadístico que consume los datos agregados de la base de datos.

---

## 🏗️ 2. Arquitectura del Sistema

El sistema sigue un patrón **Cliente-Servidor desacoplado** en la nube:

```mermaid
graph TD
    User((Usuario)) -->|HTTPS| Vercel[Frontend React - Vercel]
    Vercel -->|POST /predict| Render[Backend FastAPI - Render]
    Vercel -->|GET /stats| Render
    Render -->|Carga| Model[TensorFlow/Keras MobileNetV2]
    Render -->|INSERT & SELECT| Supabase[(Supabase PostgreSQL)]
```
---

---

## 📋 3. Plantilla de Alcance del Corte Vertical (Guia Semana 12) -Actualizada

| Elemento | Descripción del Grupo |
| :--- | :--- |
| **Funcionalidad priorizada** | Clasificación de un residuo dentro de 5 categorías (cartón, papel, metal, plásticos, orgánicos), persistencia del historial de consultas y visualización estadística en un panel con la viabilidad del modelo. |
| **Actor principal** | Usuario final y Administrador técnico. |
| **Capa de presentación prevista** | Aplicación web en React. Incluye el componente de captura, la tarjeta de resultados y un nuevo módulo de Dashboard con gráficas (usando librerías como Recharts). |
| **Endpoint(s) requeridos** | 1. `POST /predict` (Recibe la imagen, clasifica, guarda el registro en BD y retorna el JSON).<br>2. `GET /stats` (Recupera los datos agregados de la base de datos para las gráficas). |
| **Servicio(s) de aplicación o negocio** | 1. **Preprocesamiento:** Validación y transformación de la imagen.<br>2. **Inferencia:** Ejecución del modelo MobileNetV2.<br>3. **Persistencia:** Registro asíncrono de los metadatos en la base de datos.<br>4. **Agregación Estadística:** Consultas agrupadas para calcular promedios de confianza y frecuencias por clase. |
| **Regla de negocio principal** | **Umbral de Ética Algorítmica:** Si la probabilidad es < 60%, el sistema alerta al usuario.<br>**Regla de Privacidad (Ley 1581 de 2012):** El sistema persiste el resultado y metadatos (fecha, clase, nivel de confianza), pero NUNCA almacena la imagen del residuo ni datos personales. |
| **Repositorio o componente de persistencia** | Base de Datos Relacional. El modelo `.keras` sigue actuando como repositorio estático de IA. |
| **Tabla(s) o colección(es) involucradas** | Tabla `prediction_logs` (historical_predicciones). |
| **Validaciones mínimas** | **Frontend:** Tipo de archivo y tamaño.<br>**Backend:** Imagen no corrupta.<br>**BD:** Restricciones de tipo de datos (ej. confianza entre 0.0 y 1.0). |
| **Qué sí se implementaría** | - Flujo completo de captura y envío.<br>- Inferencia de IA en 5 categorías.<br>- Persistencia segura en BD.<br>- Endpoint de consulta de métricas.<br>- Gráficas en el frontend (histogramas de confianza y distribución de clases). |

---

## 🧪 4.Pruebas de Persistencia y Base de Datos (Guia Semana 13)

## Link Tablas de requerimientos: [Tablas de requerimientos](DOCS/Tablas%20de%20requerimientos.docx.pdf)

### 1. Requisitos y Configuración
- **Base de Datos:** PostgreSQL (Alojada en Supabase).
- **ORM:** SQLAlchemy 2.0.0
- **Driver:** psycopg2-binary 2.9.9
- **Tabla:** `prediction_logs`

### 1.1 Patrón Repositorio (Separación de Responsabilidades)
Se implementó el archivo `app/crud.py` para encapsular las consultas SQL y las escrituras en la base de datos. En `app/routes.py` ahora solo estan las llamadas y no contienen sentencias SQLAlchemy, usando asi  el principio de responsabilidad única.

### 2. Prueba de Escritura (Write)
- **Endpoint:** `POST /predict`
- **Acción:** Enviar una imagen de prueba .
- **Resultado Esperado:** Respuesta HTTP 200 con JSON de predicción. Un nuevo registro debe insertarse en la tabla `prediction_logs`.
- **Evidencia:**
![Tabla en Supabase](imgs/Base_de_datos.png) .

### 3. Prueba de Lectura y Agregación (Read)
- **Endpoint:** `GET /stats`
- **Acción:** Acceder al Dashboard desde el frontend .
- **Resultado Esperado:** Respuesta HTTP 200 con el conteo de clases y promedios. La gráfica de pastel debe renderizar los datos.
- **Evidencia:** 
![Dashboard Estadísticas](imgs/Estadisticas.png).

### 4. Prueba de Integridad de Datos
- **Objetivo:** Validar que la base de datos rechaza datos inconsistentes (ej. un nivel de confianza mayor a 1.0) directamente a nivel de motor de base de datos.
- **Ejecución:** En el SQL Editor de Supabase, se intentó insertar un registro con `confianza = 1.5`.
  ```sql
  INSERT INTO prediction_logs (fecha, clase_predicha, confianza, tiempo_inferencia, advertencia_activada)
  VALUES (NOW(), 'metal', 1.5, 300, false);
  ```
- **Evidencia:** 
![Integridad de datos](imgs/Integridad_de_datos.png).

### 5. Manejo de Identificadores Inexistentes
- **Objetivo:** Validar que el sistema responde controladamente (HTTP 404) cuando se busca un recurso que no existe.
- **Ejecución:** Consumir el endpoint `GET /predict/99999` (un ID que no está en la BD).
- 1. Abrimos el  backend/app/crud.py y agregamos  esta función al final:

```def get_prediction_by_id(db: Session, prediction_id: int):
    """Busca una predicción por su ID. Retorna None si no existe."""
    return db.query(models.PredictionLog).filter(models.PredictionLog.id == prediction_id).first()
```
- 2. Abrimos backend/app/routes.py y agregamos esta ruta (puede ser debajo del endpoint /stats):

```@router.get("/predict/{prediction_id}", tags=["Clasificación"])
async def get_prediction_by_id(prediction_id: int, db: Session = Depends(get_db)):
    """Recupera el registro de una predicción específica por su ID."""
    log = crud.get_prediction_by_id(db, prediction_id)
    if not log:
        # Aquí ocurre la prueba de calidad: en lugar de fallar, responde con un 404 controlado
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Registro no encontrado"
        )
    return log
```
- **Resultado Obtenido:** El servidor retornó un código HTTP 404 con el JSON `{"detail": "Registro no encontrado"}`.
- **Evidencia:** 
![Manejo de Identificadores](imgs/Manejo_de_identificadores.png).

---