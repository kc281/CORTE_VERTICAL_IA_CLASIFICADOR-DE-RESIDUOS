INSERT INTO public.prediction_logs
(id, fecha, clase_predicha, confianza, tiempo_inferencia, advertencia_activada)
VALUES
(1, '2026-11-07 09:00:00', 'metal', 0.95, 850, false),
(2, '2026-11-07 09:05:00', 'plastico', 0.91, 920, false),
(3, '2026-11-07 09:10:00', 'carton', 0.87, 780, true),
(4, '2026-11-07 09:15:00', 'papel', 0.96, 690, false),
(5, '2026-11-07 09:20:00', 'organico', 0.89, 1100, true);