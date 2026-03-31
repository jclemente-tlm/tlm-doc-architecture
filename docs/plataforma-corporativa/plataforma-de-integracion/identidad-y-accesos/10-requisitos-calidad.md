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
| Usuarios   | `100k` por `tenant` (`realm`) | Escalado vertical EC2 |
| Tenants    | `5 definidos` (3 configurados, 2 pendientes) | Multi-tenant |
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

## Escenarios de Calidad

| ID   | Estímulo                                                  | Respuesta Esperada                                              |
| ---- | --------------------------------------------------------- | --------------------------------------------------------------- |
| Q-01 | 5,000 usuarios inician sesión simultáneamente             | Latencia p95 < 800ms; sin errores HTTP 5xx                      |
| Q-02 | Token JWT presentado en Kong para validación              | Validación local < 50ms (JWKS cacheado)                         |
| Q-03 | Instancia EC2 de Keycloak se reinicia inesperadamente     | Docker Compose reinicia contenedor; disponibilidad > 99.5%      |
| Q-04 | Atacante intenta fuerza bruta contra cuenta de usuario     | Bloqueo tras 30 intentos fallidos; alerta generada              |
| Q-05 | Administrador solicita acceso a consola de Keycloak       | MFA (TOTP) requerido; acceso auditado                           |
| Q-06 | Se requiere agregar un nuevo tenant (país)                | Crear realm JSON + `--import-realm`; operativo en < 1 día       |
| Q-07 | Base de datos RDS falla en producción                     | Failover automático RDS; RPO < 15min, RTO < 4h                  |
