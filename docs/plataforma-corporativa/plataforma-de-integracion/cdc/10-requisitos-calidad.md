---
sidebar_position: 10
title: Requisitos de Calidad
description: Atributos de calidad y escenarios de evaluación del servicio CDC con Debezium.
---

# 10. Requisitos de Calidad

## Metas de Calidad

| Prioridad | Atributo       | Meta                                                                          |
| --------- | -------------- | ----------------------------------------------------------------------------- |
| 1         | Exactitud      | Cero pérdida de eventos. Cada cambio confirmado en la BD debe llegar a Kafka. |
| 2         | Latencia       | Latencia de captura < 100 ms (p95) entre el commit en la BD y la publicación. |
| 3         | Disponibilidad | El servicio de captura tiene disponibilidad ≥ 99,9% mensual.                  |
| 4         | Rendimiento    | Capacidad de captura ≥ 10 000 eventos/segundo sostenidos.                     |
| 5         | Mantenibilidad | Registro de nuevo conector < 30 minutos sin redeploy del worker.              |

## Requisitos de Rendimiento

| Métrica                    | Umbral   | Medición                                    |
| -------------------------- | -------- | ------------------------------------------- |
| Latencia captura (p95)     | < 100 ms | `debezium_metrics_MilliSecondsBehindSource` |
| Latencia captura (p99)     | < 500 ms | `debezium_metrics_MilliSecondsBehindSource` |
| Eventos por segundo        | ≥ 10 000 | `source_record_write_total` / intervalo     |
| Tiempo de snapshot inicial | < 4 h    | Para tablas con hasta 50 M de filas         |

## Requisitos de Disponibilidad

| Métrica                      | Umbral    | Mecanismo                                                                       |
| ---------------------------- | --------- | ------------------------------------------------------------------------------- |
| Disponibilidad mensual       | ≥ 99,9%   | Docker reinicia el contenedor automáticamente (restart policy `unless-stopped`) |
| Tiempo de recuperación (RTO) | < 2 min   | Restart del contenedor Docker + reanudación de offset                           |
| Punto de recuperación (RPO)  | 0 eventos | Offset almacenado en Kafka; reanuda sin pérdida                                 |

## Escenarios de Calidad

### Q-01 — Latencia en carga pico

| Campo         | Detalle                                                                |
| ------------- | ---------------------------------------------------------------------- |
| **Estímulo**  | 10 000 operaciones/s en la tabla `operaciones` de PostgreSQL           |
| **Respuesta** | Debezium captura y publica todos los cambios con latencia p95 < 100 ms |
| **Riesgo**    | RT-03 — saturación del pipeline WAL bajo carga extrema                 |

### Q-02 — Cero pérdida de eventos ante reinicio

| Campo         | Detalle                                                                      |
| ------------- | ---------------------------------------------------------------------------- |
| **Estímulo**  | El contenedor del worker es reiniciado por OOM u otro fallo                  |
| **Respuesta** | El worker reanuda desde el último offset confirmado; ningún evento se pierde |
| **Riesgo**    | RO-02 — offset no confirmado entre el último reinicio y el siguiente poll    |

### Q-03 — Registro rápido de nuevo conector

| Campo         | Detalle                                                                                                          |
| ------------- | ---------------------------------------------------------------------------------------------------------------- |
| **Estímulo**  | El equipo de Plataforma necesita capturar una nueva tabla de la BD origen                                        |
| **Respuesta** | Se ejecuta un `POST /connectors` con la configuración; el conector arranca y comienza el snapshot en < 5 minutos |
| **Riesgo**    | Ninguno identificado                                                                                             |

### Q-04 — Detección de conector fallido

| Campo         | Detalle                                                              |
| ------------- | -------------------------------------------------------------------- |
| **Estímulo**  | Un conector pasa a estado FAILED por credenciales expiradas en la BD |
| **Respuesta** | Grafana dispara alerta en < 2 minutos; equipo recibe notificación    |
| **Riesgo**    | DT-03 — dashboards de lag no configurados aún                        |

### Q-05 — Cambio de esquema en tabla origen

| Campo         | Detalle                                                                                                                 |
| ------------- | ----------------------------------------------------------------------------------------------------------------------- |
| **Estímulo**  | Un DBA agrega una columna a la tabla `operaciones`                                                                      |
| **Respuesta** | Debezium detecta el cambio de esquema, lo registra en `connect-schema-changes` y continúa el streaming sin interrupción |
| **Riesgo**    | DEC-01 — sin Schema Registry, el consumidor puede fallar si no espera la nueva columna                                  |

### Q-06 — Enmascaramiento de PII

| Campo         | Detalle                                                                                                                                                   |
| ------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Estímulo**  | Se registra un conector para una tabla que contiene columnas con DNI y email de clientes                                                                  |
| **Respuesta** | La configuración del conector incluye el SMT `MaskField` para esas columnas; los eventos en Kafka contienen `"***MASKED***"` en lugar de los datos reales |
| **Riesgo**    | DT-02 — enmascaramiento PII no obligatorio en el proceso actual de registro de conectores                                                                 |
