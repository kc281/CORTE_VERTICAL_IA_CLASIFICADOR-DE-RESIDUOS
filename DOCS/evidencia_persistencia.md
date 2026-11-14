# Evidencia: persistencia real y ausencia de escrituras indebidas

- **Fecha de ejecución:** 2026-11-14 17:03:02
- **API:** http://localhost:8000
- **Base de datos:** postgresql (aws-0-us-east-2.pooler.supabase.com)
- **Empresa (company_id):** 4
- **Imagen usada:** Imagen_papel.jpg
- **Registros de la empresa:** 5 -> 6 (solo P1 escribe)
- **Registro creado:** id=68 (eliminado con --limpiar)

| Prueba | Escenario                                           | Esperado                                                            | Obtenido                                                                                    | Resultado |
| :----- | :-------------------------------------------------- | :------------------------------------------------------------------ | :------------------------------------------------------------------------------------------ | :-------- |
| P1     | RF-01 válido: POST /predict con imagen              | 201, ID real, +1 registro y mismos datos leídos desde otra conexión | 201; id=68; registros 5->6; BD: clase=metal, confianza=0.4567                               | ✅ Cumple |
| P2     | RF-01 rechazo: archivo .txt                         | 400; registros sin cambio                                           | 400 'Formato no permitido. Use JPG, PNG o WEBP.'; registros 6->6                            | ✅ Cumple |
| P3     | RF-01 rechazo: imagen corrupta                      | 400; registros sin cambio                                           | 400 'La imagen no pudo ser procesada. Verifique que el archivo sea válido.'; registros 6->6 | ✅ Cumple |
| P4     | RF-01 rechazo: petición sin archivo                 | 400; registros sin cambio                                           | 400 'Solicitud inválida. Verifique los datos enviados.'; registros 6->6                     | ✅ Cumple |
| P5     | RF-01 rechazo: imagen de 6 MB                       | 413; registros sin cambio                                           | 413 'El archivo supera el tamaño máximo de 5 MB.'; registros 6->6                           | ✅ Cumple |
| P6     | RF-01 rechazo: sin token                            | 401; registros sin cambio                                           | 401 'No se envió el token de autenticación.'; registros 6->6                                | ✅ Cumple |
| P7     | RF-02 válido: GET /predict/68                       | 200; tabla y registro sin cambios                                   | 200 (datos coinciden con la BD); registros 6->6; registro sin cambios                       | ✅ Cumple |
| P8     | RF-02 ausencia: GET /predict/999999999              | 404; tabla y registro sin cambios                                   | 404; registros 6->6; registro sin cambios                                                   | ✅ Cumple |
| P9     | RF-02 entrada inválida: GET /predict/0              | 400; tabla y registro sin cambios                                   | 400; registros 6->6; registro sin cambios                                                   | ✅ Cumple |
| P10    | RF-02 válido: GET /history                          | 200; tabla y registro sin cambios                                   | 200; registros 6->6; registro sin cambios                                                   | ✅ Cumple |
| P11    | RF-02 rechazo: PATCH /verify con categoría 'vidrio' | 400; categoria_confirmada sin cambio                                | 400; categoria_confirmada None->None                                                        | ✅ Cumple |
| P12    | RF-03 válido: GET /stats                            | 200; tabla y registro sin cambios                                   | 200 (total API=6, BD=6); registros 6->6; registro sin cambios                               | ✅ Cumple |

**Resultado:** 12/12 pruebas cumplen.
