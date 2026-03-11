---
sidebar_position: 1
title: Introducción y Objetivos
description: Objetivos, requisitos y partes interesadas del API Gateway corporativo basado en Kong OSS.
---

# 1. Introducción y Objetivos

El **API Gateway corporativo** es el punto de entrada unificado y seguro para todos los servicios corporativos.
Está implementado con **Kong OSS**, desplegado en contenedores sobre AWS ECS Fargate (ADR-010).

## Objetivos Principales

| Objetivo                     | Descripción                                                                                            |
| ---------------------------- | ------------------------------------------------------------------------------------------------------ |
| Enrutamiento centralizado    | Un único punto de entrada para microservicios: Identity, Notifications, Track & Trace, SITA            |
| Autenticación y autorización | Validación de JWT emitidos por Keycloak mediante el plugin `jwt` de Kong                               |
| Rate limiting                | Control de tráfico por tenant y endpoint mediante el plugin `rate-limiting` con Redis                  |
| Observabilidad               | Métricas, logs y trazas distribuidas integradas con el stack corporativo (Grafana, Mimir, Loki, Tempo) |
| Multi-tenancy                | Enrutamiento por país/cliente mediante Kong Workspaces y anotaciones de ruta                           |
| Resiliencia                  | Circuit breaking pasivo por upstream, health checks activos y pasivos                                  |
| Agnosticidad tecnológica     | Kong no impone stack tecnológico en los servicios backend                                              |

## Requisitos de Calidad

| Atributo             | Objetivo                     | Crítico        |
| -------------------- | ---------------------------- | -------------- |
| Latencia p95         | `< 10ms` overhead de gateway | `< 20ms`       |
| Throughput           | `> 10,000 RPS`               | `> 5,000 RPS`  |
| Disponibilidad       | `99.9%`                      | `99.5%`        |
| Tiempo de despliegue | `< 5 minutos` (deck sync)    | `< 15 minutos` |

## Partes Interesadas

| Rol                    | Interés                                                   |
| ---------------------- | --------------------------------------------------------- |
| Equipo de Plataforma   | Operación, despliegue y monitoreo de Kong                 |
| Equipo de Arquitectura | Definición de estándares, plugins y topología             |
| Equipos de Desarrollo  | Registro de servicios y rutas; consumo de APIs            |
| Equipo de Seguridad    | Configuración de autenticación, TLS y políticas de acceso |

## Decisión de Tecnología

Kong OSS fue seleccionado en [ADR-010](../../../adrs/adr-010-kong-api-gateway.md).
