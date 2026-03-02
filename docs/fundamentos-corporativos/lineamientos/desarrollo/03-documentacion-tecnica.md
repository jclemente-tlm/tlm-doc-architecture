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

- [Mantener README actualizado en repositorios](../../estandares/documentacion/technical-documentation.md#1-readme-standards)
- [Documentar decisiones con ADRs](../../estandares/documentacion/architecture-documentation.md#3-architecture-decision-records-adrs)
- [Documentar arquitectura con arc42](../../estandares/documentacion/architecture-documentation.md#1-arc42-template)
- [Modelar con C4 Model](../../estandares/documentacion/architecture-documentation.md#2-c4-model)
- [Mantener runbooks operacionales](../../estandares/documentacion/technical-documentation.md#4-runbooks)
- [Crear guías de onboarding](../../estandares/documentacion/technical-documentation.md#3-onboarding-guides)
- [Documentar guías de contribución](../../estandares/documentacion/technical-documentation.md#2-contributing-guides)

## Referencias Relacionadas

- [Estilo y Enfoque Arquitectónico](../../lineamientos/arquitectura/01-estilo-y-enfoque-arquitectonico.md)
- [ADRs del proyecto](../../../adrs/README.md)
