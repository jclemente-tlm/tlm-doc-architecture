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

- [Implementar circuit breakers para dependencias externas](../../estandares/arquitectura/circuit-breaker.md)
- [Aplicar timeouts apropiados en llamadas remotas](../../estandares/arquitectura/timeout-patterns.md)
- [Configurar retry con backoff exponencial](../../estandares/arquitectura/retry-patterns.md)
- [Diseñar degradación graceful ante fallos](../../estandares/arquitectura/graceful-degradation.md)
- [Implementar bulkhead para aislamiento de recursos](../../estandares/arquitectura/bulkhead-pattern.md)
- [Aplicar rate limiting para protección de sobrecarga](../../estandares/arquitectura/rate-limiting.md)
- [Configurar health checks para detección de fallos](../../estandares/infraestructura/health-checks.md)
- [Definir SLOs y SLAs documentados](../../estandares/observabilidad/slo-sla.md)
- [Implementar Dead Letter Queue para mensajes fallidos](../../estandares/mensajeria/dead-letter-queue.md)
- [Diseñar alta disponibilidad con multi-AZ y redundancia](../../estandares/arquitectura/high-availability.md)
