---
id: calidad-codigo
sidebar_position: 1
title: Calidad de Código
description: Estándares de calidad de código, convenciones y revisiones
---

# Calidad de Código

Código sin estándares consistentes, análisis estático ni revisiones genera deuda técnica, bugs ocultos y mantenibilidad decreciente que encarece evolución del software. Convenciones inconsistentes entre equipos dificultan colaboración y transferencia de conocimiento. Establecer estándares de código (C#, SQL), análisis estático automatizado (SonarQube, StyleCop), code review obligatorio y quality gates en CI/CD garantiza legibilidad, detecta vulnerabilidades tempranamente y mantiene calidad sostenible del código base.

**Este lineamiento aplica a:** Convenciones de código (C#, SQL), análisis estático y linters (SonarQube, StyleCop), code reviews y revisión por pares, métricas de calidad (complejidad ciclomática, duplicación), herramientas de formateo y estilo.

**No aplica a:** Testing automatizado (ver [Estrategia de Pruebas](./04-testing.md)), monitoreo en producción.

## Estándares Obligatorios

- [Aplicar estándares de calidad de código: análisis estático y cobertura mínima](../../estandares/desarrollo/code-quality-review.md)
- [Seguir convenciones de código C# y .NET](../../estandares/desarrollo/csharp-dotnet.md)
- [Aplicar buenas prácticas de desarrollo SQL](../../estandares/desarrollo/sql.md)
- [Realizar code review obligatorio antes de merge a ramas principales](../../estandares/desarrollo/code-quality-review.md#4-requisitos-obligatorios)

## Referencias Relacionadas

- [Estrategia de Pruebas](./02-estrategia-pruebas.md) (testing automatizado)
- [CI/CD](../operabilidad/01-automatizacion-iac.md) (quality gates en pipelines)
