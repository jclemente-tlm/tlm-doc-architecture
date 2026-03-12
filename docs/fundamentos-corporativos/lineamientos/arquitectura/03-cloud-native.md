---
id: cloud-native
sidebar_position: 3
title: Cloud Native
description: Principios de diseño para sistemas que operan en entornos cloud dinámicos y escalables
---

# Cloud Native

Sistemas diseñados para cloud aprovechan elasticidad, resiliencia y dinamismo mediante arquitecturas stateless, configuración externalizada y resiliencia ante fallos. Aplicaciones que no siguen estos principios pierden beneficios de escalabilidad automática, recuperación rápida y optimización de costos. Adoptar 12-Factor App y patrones cloud-native desde el diseño reduce complejidad operativa y facilita despliegues automatizados.

**Este lineamiento aplica a:** aplicaciones en cloud público/privado/híbrido, servicios contenerizados, plataformas multi-tenant y migraciones a cloud.

## Prácticas Obligatorias

- [Aplicar estándares cloud-native (stateless, health checks, disposability, container-first)](../../estandares/arquitectura/cloud-native.md)
- [Seguir metodología 12-Factor App](../../estandares/arquitectura/architecture-evolution.md#4-twelve-factor-app)
- [Contenerizar aplicaciones](../../estandares/infraestructura/containerization.md)
- [Externalizar configuración en variables de entorno](../../estandares/infraestructura/configuration-management.md)
- [Diseñar servicios stateless](../../estandares/arquitectura/scalability-performance.md#1-stateless-design)
- [Aplicar graceful shutdown](../../estandares/arquitectura/resilience-patterns.md#7-graceful-shutdown)
- [Optimizar costos en cloud](../../estandares/infraestructura/cloud-cost-optimization.md)

## Referencias Relacionadas

- [Gestionar secretos en AWS Secrets Manager](/docs/adrs/adr-004-aws-secrets-manager)
