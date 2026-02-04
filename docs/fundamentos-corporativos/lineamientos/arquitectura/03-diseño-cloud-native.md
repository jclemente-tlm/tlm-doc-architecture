---
id: diseno-cloud-native
sidebar_position: 3
title: Diseño Cloud Native
description: Principios de diseño para sistemas que operan en entornos cloud dinámicos y escalables
---

# Diseño Cloud Native

Sistemas diseñados para cloud aprovechan elasticidad, resiliencia y dinamismo mediante arquitecturas stateless, configuración externalizada y resiliencia ante fallos. Aplicaciones que no siguen estos principios pierden beneficios de escalabilidad automática, recuperación rápida y optimización de costos. Adoptar 12-Factor App y patrones cloud-native desde el diseño reduce complejidad operativa y facilita despliegues automatizados.

**Este lineamiento aplica a:** aplicaciones en cloud público/privado/híbrido, servicios containerizados, plataformas multi-tenant y migraciones a cloud.

## Estándares Obligatorios

- [Externalizar configuración en variables de entorno](../../estandares/infraestructura/externalize-configuration.md)
- [Diseñar servicios stateless con estado en backing services](../../estandares/arquitectura/stateless-services.md)
- [Implementar health checks liveness y readiness](../../estandares/observabilidad/health-checks.md)
- [Preparar servicios para escalabilidad horizontal](../../estandares/arquitectura/horizontal-scaling.md)
- [Aplicar graceful shutdown para terminación ordenada](../../estandares/arquitectura/resilience-patterns.md#8-graceful-shutdown)

## Referencias Relacionadas

- [Gestionar secretos en AWS Secrets Manager](../../../decisiones-de-arquitectura/adr-003-aws-secrets-manager.md)
