---
id: documentacion-tecnica
sidebar_position: 3
title: Documentación Técnica
description: README, ADRs, arc42, C4 y documentación técnica de servicios
---

# Documentación Técnica

Código sin documentación clara genera dependencia de autores originales, dificulta onboarding y eleva costos de mantenimiento. Decisiones arquitectónicas no documentadas se pierden con rotación de personal, provocando repetición de errores y debates recurrentes. Ausencia de documentación de interfaces (APIs, eventos, contratos) causa integración errónea y debugging prolongado. Documentar decisiones mediante ADRs, arquitectura con arc42 y C4, interfaces con especificaciones OpenAPI y mantener READMEs actualizados garantiza transferencia de conocimiento efectiva, reduce dependencia de individuos, acelera onboarding y permite evolución informada del sistema.

**Este lineamiento aplica a:** Documentación de repositorios (README), decisiones arquitectónicas (ADRs), arquitectura de sistemas (arc42, C4, Structurizr DSL), especificaciones de APIs (OpenAPI), contratos de eventos y mensajería, guías de onboarding y contribución.

**No aplica a:** Documentación de código fuente (comentarios inline), manuales de usuario final, documentación de procesos de negocio.

## Estándares Obligatorios

- [Mantener README actualizado en repositorios](../../estandares/documentacion/readme-standards.md)
- [Documentar decisiones con ADRs](../../estandares/documentacion/architecture-decision-records.md)
- [Documentar arquitectura con arc42](../../estandares/documentacion/arc42.md)
- [Modelar con C4 Model](../../estandares/documentacion/c4-model.md)
- [Especificar APIs REST con OpenAPI](../../estandares/apis/openapi-specification.md)
- [Documentar APIs asíncronas con AsyncAPI](../../estandares/apis/asyncapi-specification.md)
- [Mantener runbooks operacionales](../../estandares/documentacion/runbooks.md)
- [Crear guías de onboarding](../../estandares/documentacion/onboarding-guides.md)
- [Documentar guías de contribución](../../estandares/documentacion/contributing-guides.md)

## Referencias Relacionadas

- [Estilo y Enfoque Arquitectónico](../../lineamientos/arquitectura/01-estilo-y-enfoque-arquitectonico.md)
- [ADRs del proyecto](../../../decisiones-de-arquitectura/README.md)
