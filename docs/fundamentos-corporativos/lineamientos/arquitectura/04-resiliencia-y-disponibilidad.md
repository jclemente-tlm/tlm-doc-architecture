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

- [Implementar circuit breakers para dependencias externas](../../estandares/arquitectura/circuit-breakers.md)
- [Aplicar timeouts apropiados en llamadas remotas](../../estandares/arquitectura/timeouts.md)
- [Configurar retry con backoff exponencial](../../estandares/arquitectura/retry-patterns.md)
- [Diseñar degradación graceful ante fallos](../../estandares/arquitectura/graceful-degradation.md)
- [Definir SLOs y SLAs documentados](../../estandares/operabilidad/slos-slas.md)
- [Implementar Dead Letter Queue para mensajes fallidos](../../estandares/mensajeria/dlq.md)
