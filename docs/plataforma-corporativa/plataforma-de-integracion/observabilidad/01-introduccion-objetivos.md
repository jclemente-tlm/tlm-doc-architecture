---
sidebar_position: 1
title: Introducción y Objetivos
description: Propósito, capacidades y partes interesadas del stack de observabilidad corporativo.
---

# 1. Introducción y Objetivos

## Descripción

El **stack de observabilidad corporativo** centraliza la recolección, almacenamiento y visualización de **logs, métricas y trazas distribuidas** de todos los servicios de Talma. Está implementado con el stack Grafana OSS (Loki + Mimir + Tempo + Grafana + Alloy), desplegado en arquitectura de 3 capas con multi-tenancy estratégica por país, ambiente y dominio de servicio (ADR-014).

## Objetivos del Sistema

| Objetivo                        | Descripción                                                                   |
| ------------------------------- | ----------------------------------------------------------------------------- |
| **Telemetría unificada**        | Logs, métricas y trazas en una única plataforma correlacionados por Trace ID  |
| **Multi-tenancy**               | Segregación de datos por país (logs), ambiente (métricas) y servicio (trazas) |
| **Troubleshooting distribuido** | Navegación fluida de log → métrica → traza en un solo contexto                |
| **Alertas proactivas**          | SLOs/SLIs con notificaciones a Slack, MS Teams, email y PagerDuty             |
| **Bajo costo**                  | Stack OSS sin licencias; reduce costos ~80% frente a opciones SaaS            |

## Capacidades Principales

- **Ingestión OTLP**: los agentes Alloy reciben telemetría via OTLP gRPC (`:4317`) y HTTP (`:4318`).
- **Routing de tenants**: Envoy Proxy inyecta el header `X-Scope-OrgID` según el tipo de señal antes de reenviar a los backends.
- **Almacenamiento escalable**: Loki, Mimir y Tempo persisten en MinIO (S3-compatible).
- **Queries con caché**: Memcached acelera queries repetidas en dashboards de largo plazo.
- **Correlación automática**: Grafana enlaza logs con trazas mediante `traceId`; métricas con logs mediante `serviceInstanceId`.
- **Snapshots**: Grafana admite alertas de screenshots y reportes PDF automáticos.

## Métricas de Calidad Objetivo

| Métrica                                 | Umbral                 |
| --------------------------------------- | ---------------------- |
| Latencia de ingestión de logs           | < 500 ms p95           |
| Latencia de query de logs (últimas 6 h) | < 2 s p95              |
| Latencia de query de métricas           | < 100 ms p95           |
| Latencia de query de trazas             | < 500 ms p95           |
| Disponibilidad del stack (server layer) | ≥ 99,5% mensual        |
| Retención de logs                       | 30 días (configurable) |
| Retención de métricas                   | 90 días (configurable) |
| Retención de trazas                     | 14 días (configurable) |

## Partes Interesadas

| Rol                   | Interés principal                                                |
| --------------------- | ---------------------------------------------------------------- |
| Equipo de Plataforma  | Operación, upgrades, configuración de nuevos tenants y agentes   |
| Equipos de Desarrollo | Troubleshooting, análisis de performance, correlación de errores |
| Equipo de Seguridad   | Auditoría de accesos, segregación de tenants, retención de logs  |
| Arquitectura          | Cumplimiento de ADR-014, integración con OpenTelemetry en .NET   |
| Operaciones           | Dashboards de disponibilidad y alertas de SLO                    |
