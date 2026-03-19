---
sidebar_position: 10
title: Requisitos de Calidad
description: Atributos de calidad y escenarios de evaluación del stack de observabilidad.
---

# 10. Requisitos de Calidad

## Metas de Calidad

| Prioridad | Atributo                 | Meta                                                                       |
| --------- | ------------------------ | -------------------------------------------------------------------------- |
| 1         | Disponibilidad           | Stack de servidor disponible ≥ 99,5% mensual                               |
| 2         | Rendimiento de ingestión | Ingesta sin pérdida hasta 50 000 líneas de log/s y 100 000 métricas/min    |
| 3         | Latencia de query        | Métricas < 100 ms p95; logs < 2 s p95; trazas < 500 ms p95                 |
| 4         | Aislamiento de tenants   | Ningún query de un tenant devuelve datos de otro tenant                    |
| 5         | Mantenibilidad           | Agregar un nuevo tenant (agente) en < 15 minutos sin redeploy del servidor |

## Requisitos de Rendimiento

| Métrica                   | Umbral                       | Medición                                            |
| ------------------------- | ---------------------------- | --------------------------------------------------- |
| Ingestión de logs         | ≥ 50 000 líneas/s sostenidas | `loki_ingester_streams_created_total`               |
| Ingestión de métricas     | ≥ 100 000 series/min         | `mimir_ingester_samples_in_total`                   |
| Ingestión de trazas       | ≥ 10 000 spans/s             | `tempo_ingester_traces_created_total`               |
| Latencia query logs (6 h) | < 2 s p95                    | Grafana query inspector                             |
| Latencia query métricas   | < 100 ms p95                 | `mimir_query_frontend_query_range_duration_seconds` |
| Latencia query trazas     | < 500 ms p95                 | `tempo_query_frontend_duration_seconds`             |

## Requisitos de Disponibilidad

| Métrica                           | Umbral                  | Mecanismo                                                             |
| --------------------------------- | ----------------------- | --------------------------------------------------------------------- |
| Disponibilidad mensual            | ≥ 99,5%                 | Docker `restart: unless-stopped` en todos los servicios               |
| RTO (server layer)                | < 5 min                 | Reinicio de contenedores Docker; WAL local preserva datos en tránsito |
| RPO (sin pérdida de datos)        | 0 señales tras reinicio | WAL de Loki/Mimir/Tempo; offsets de Alloy                             |
| Agente independiente del servidor | Sí                      | Alloy bufferiza si Envoy no está disponible                           |

## Escenarios de Calidad

### Q-01 — Ingestión masiva de logs sin pérdida

| Campo         | Detalle                                                                                |
| ------------- | -------------------------------------------------------------------------------------- |
| **Estímulo**  | Despliegue de nueva versión genera 5 000 líneas de log/s durante 5 minutos en `tlm-pe` |
| **Respuesta** | Loki ingesta todas las líneas sin rechazo; latencia de ingestión < 500 ms p95          |
| **Riesgo**    | RT-01 — disco de MinIO insuficiente para el volumen generado                           |

### Q-02 — Query de métricas en dashboard ejecutivo con caché

| Campo         | Detalle                                                                                |
| ------------- | -------------------------------------------------------------------------------------- |
| **Estímulo**  | 10 usuarios consultan el dashboard de disponibilidad del tenant `prod` al mismo tiempo |
| **Respuesta** | Latencia < 100 ms p95 gracias al caché Memcached; Mimir no re-computa la query         |
| **Riesgo**    | RO-02 — Memcached no disponible eleva latencia a 500 ms–1 s (aceptable)                |

### Q-03 — Correlación log → traza en troubleshooting

| Campo         | Detalle                                                                                |
| ------------- | -------------------------------------------------------------------------------------- |
| **Estímulo**  | Desarrollador detecta error en Grafana Explore para `tlm-pe`, hace clic en `traceId`   |
| **Respuesta** | Grafana abre la traza completa en Tempo tenant `orders` en < 500 ms                    |
| **Riesgo**    | DT-02 — derived fields en el data source Loki no configurados para todos los servicios |

### Q-04 — Aislamiento de tenants

| Campo         | Detalle                                                                                                  |
| ------------- | -------------------------------------------------------------------------------------------------------- |
| **Estímulo**  | Usuario con acceso solo al tenant `tlm-pe` ejecuta LogQL sin filtro de tenant                            |
| **Respuesta** | Grafana data source está configurado con `X-Scope-OrgID: tlm-pe`; Loki devuelve solo datos de ese tenant |
| **Riesgo**    | RO-03 — data source de Grafana mal configurado sin header fijo expone datos cross-tenant                 |

### Q-05 — Nuevo agente activo en < 15 minutos

| Campo         | Detalle                                                                                                                           |
| ------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| **Estímulo**  | El equipo de Plataforma debe instrumentar un nuevo país (Ecuador)                                                                 |
| **Respuesta** | Copiar `agents/.env.example`, configurar `TENANT_ID=tlm-ec`, `docker-compose up -d`; el agente comienza a enviar datos en < 5 min |
| **Riesgo**    | Ninguno identificado                                                                                                              |

### Q-06 — Recuperación de Loki tras reinicio

| Campo         | Detalle                                                                                     |
| ------------- | ------------------------------------------------------------------------------------------- |
| **Estímulo**  | El contenedor Loki se reinicia por OOM                                                      |
| **Respuesta** | Docker reinicia el contenedor; Loki recupera el WAL local y continúa ingestando sin pérdida |
| **Riesgo**    | RT-02 — WAL corrupto si el disco EC2 tiene fallo de I/O durante el reinicio                 |
