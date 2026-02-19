---
id: resiliencia-y-disponibilidad
sidebar_position: 4
title: Resiliencia y Disponibilidad
description: Lineamientos para diseñar sistemas tolerantes a fallos y altamente disponibles
---

# Resiliencia y Disponibilidad

Sistemas distribuidos enfrentan fallos inevitables: dependencias caídas, latencias inesperadas, picos de carga. Diseñar sin estrategias de resiliencia genera cascading failures, pérdida de datos y experiencias degradadas para usuarios. Implementar circuit breakers, timeouts, retries y degradación graceful mantiene la funcionalidad esencial y reduce MTTR, garantizando disponibilidad incluso ante condiciones adversas.

**Este lineamiento aplica a:** servicios críticos, APIs públicas/privadas, sistemas distribuidos e integraciones con terceros.

## Estándares Obligatorios

- [Implementar circuit breakers para dependencias externas](../../estandares/arquitectura/resilience-patterns.md#1-circuit-breaker)
- [Aplicar timeouts apropiados en llamadas remotas](../../estandares/arquitectura/resilience-patterns.md#3-timeout)
- [Configurar retry con backoff exponencial](../../estandares/arquitectura/resilience-patterns.md#2-retry)
- [Diseñar degradación graceful ante fallos](../../estandares/arquitectura/resilience-patterns.md#6-graceful-degradation)
- [Implementar bulkhead para aislamiento de recursos](../../estandares/arquitectura/resilience-patterns.md#4-bulkhead)
- [Aplicar rate limiting para protección de sobrecarga](../../estandares/arquitectura/resilience-patterns.md#5-rate-limiting)
- [Configurar health checks para detección de fallos](../../estandares/arquitectura/scalability-performance.md#5-health-checks)
