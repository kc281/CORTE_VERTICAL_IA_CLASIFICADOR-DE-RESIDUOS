CREATE TABLE public.prediction_logs (
    id INT4 PRIMARY KEY,
    fecha TIMESTAMP,
    clase_predicha VARCHAR,
    confianza NUMERIC,
    tiempo_inferencia INT4,
    advertencia_activada BOOLEAN
);