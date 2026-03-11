---
sidebar_position: 10
title: Requisitos de Calidad
description: Atributos y escenarios de calidad del Servicio de Identidad.
---

# 10. Requisitos de Calidad

## Rendimiento

| Métrica          | Objetivo        | Medición           |
| ---------------- | --------------- | ------------------ |
| Latencia auth    | `< 200ms p95`   | `Prometheus/Mimir` |
| Throughput       | `5k logins/min` | Load testing       |
| Disponibilidad   | `99.9%`         | Health checks      |
| Token validation | `< 50ms`        | Benchmarks         |

- Instrumentación y monitoreo continuo en todos los entornos.
- Criterios de aceptación claros y cuantificables para cada métrica.

## Escalabilidad

| Aspecto    | Objetivo                      | Estrategia   |
| ---------- | ----------------------------- | ------------ |
| Usuarios   | `100k` por `tenant` (`realm`) | Autoescalado |
| Tenants    | `4 países` (pe, ec, co, mx)   | Multi-tenant |
| Sessions   | `10k` concurrentes            | `PostgreSQL` |
| Federación | Múltiples IdP                 | Híbrida      |

- Arquitectura multi-tenant y autoescalable.
- Pruebas de carga periódicas para validar límites y crecimiento.

## Latencia y Capacidad

| Operación                   | P50   | P95   | P99   | SLA Crítico |
| --------------------------- | ----- | ----- | ----- | ----------- |
| Inicio de sesión inicial    | 300ms | 800ms | 1.5s  | `< 2s`      |
| Validación token (cache)    | 5ms   | 15ms  | 30ms  | `< 50ms`    |
| Validación token (no cache) | 50ms  | 120ms | 200ms | `< 300ms`   |
| Renovación token            | 80ms  | 200ms | 400ms | `< 500ms`   |
| Cierre sesión               | 100ms | 250ms | 500ms | `< 1s`      |
| Desafío MFA                 | 200ms | 500ms | 1s    | `< 2s`      |
| Federación externa          | 800ms | 2s    | 4s    | `< 5s`      |

- SLAs definidos y medidos para operaciones críticas.
- Alertas automáticas ante degradación de performance.
