---
sidebar_position: 2
title: Restricciones de Arquitectura
description: Restricciones técnicas, organizacionales y de despliegue del stack de observabilidad.
---

# 2. Restricciones de Arquitectura

## Restricciones Técnicas

| Restricción              | Valor                                                                         | Justificación                                                                                |
| ------------------------ | ----------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------- |
| Stack de observabilidad  | Grafana OSS (Loki + Mimir + Tempo + Grafana + Alloy)                          | ADR-014; stack unificado, sin lock-in, OSS                                                   |
| Proxy de routing         | Envoy Proxy v1.36.2                                                           | Gestión de multi-tenancy via headers HTTP sin modificar clientes                             |
| Almacenamiento           | MinIO (S3-compatible)                                                         | Backend objeto unificado para los tres backends; compatible S3                               |
| Recolector de telemetría | Grafana Alloy v1.11.3                                                         | Recolector único para logs, métricas y trazas; reemplaza Promtail + Prometheus Agent         |
| Protocolo de telemetría  | OTLP (gRPC y HTTP) + Prometheus Remote Write                                  | OTLP para logs y trazas; métricas usan Prometheus Remote Write (Mimir no acepta OTLP nativo) |
| Despliegue               | Contenedores Docker (docker-compose)                                          | Consistente con el modelo operacional del stack Kafka y CDC                                  |
| Multi-tenancy header     | `X-Tenant` + `X-Environment` (Alloy → Envoy); Envoy construye `X-Scope-OrgID` | Headers desacoplados permiten a Envoy aplicar la fórmula de tenant sin modificar agentes     |
| Caché de queries         | Memcached 1.6.39-alpine                                                       | Queries repetidas en dashboards ejecutivos sin costo de re-computo                           |

## Restricciones de Multi-Tenancy

| Señal                | Criterio de tenant | Formato del tenant resultante                             | Razón                                                                        |
| -------------------- | ------------------ | --------------------------------------------------------- | ---------------------------------------------------------------------------- |
| **Logs** (Loki)      | País + Ambiente    | `logs-{TENANT_ID}-{ENVIRONMENT}` (ej. `logs-tlm-pe-prod`) | Cumplimiento regulatorio por localización + separación por ambiente          |
| **Métricas** (Mimir) | Ambiente           | `metrics-{ENVIRONMENT}` (ej. `metrics-prod`)              | Dashboards consolidados por ambiente                                         |
| **Trazas** (Tempo)   | Ambiente           | `traces-{ENVIRONMENT}` (ej. `traces-prod`)                | Integridad de la cadena de spans entre servicios dentro de un mismo ambiente |

## Restricciones de Seguridad

| Restricción             | Detalle                                                                                        |
| ----------------------- | ---------------------------------------------------------------------------------------------- |
| Credenciales            | Nunca en repositorio; archivos `.env` excluidos de Git                                         |
| Rotación de contraseñas | Admin: 90 días; API Keys: 180 días; claves S3: 12 meses                                        |
| Red de backends         | Loki, Mimir y Tempo en red Docker interna (`observability-backend`); no expuestos directamente |
| Único punto de entrada  | Todo el tráfico ingresa por Envoy (`:8080` HTTP, `:4317`/`:4318` OTLP)                         |
| Autenticación Grafana   | Integración con Keycloak para SSO corporativo                                                  |

## Restricciones Organizacionales

| Restricción          | Detalle                                                                                     |
| -------------------- | ------------------------------------------------------------------------------------------- |
| Versiones            | Usar versiones fijadas en `.env`; nunca `latest` en producción                              |
| IaC                  | Configuración de backends gestionada mediante archivos YAML versionados en `server/config/` |
| Agentes              | Cada país/región despliega su propio agente Alloy con su `TENANT_ID` configurado            |
| Capacidad de cómputo | Server layer en EC2 dedicado; UI Grafana puede correr en instancia separada                 |
