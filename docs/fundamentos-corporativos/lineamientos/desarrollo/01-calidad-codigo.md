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

- [Seguir convenciones de código C# y .NET](../../estandares/desarrollo/csharp-dotnet.md)
- [Aplicar buenas prácticas SQL](../../estandares/desarrollo/sql-standards.md)
- [Implementar análisis estático con linters](../../estandares/desarrollo/static-analysis.md)
- [Realizar SAST en pipelines CI/CD](../../estandares/desarrollo/sast.md)
- [Ejecutar code review obligatorio](../../estandares/desarrollo/code-review.md)
- [Definir quality gates con métricas mínimas](../../estandares/desarrollo/quality-gates.md)

## Referencias Relacionadas

- [Estrategia de Pruebas](./02-estrategia-pruebas.md) (testing automatizado)
- [CI/CD y Automatización](../operabilidad/01-cicd-pipelines.md) (quality gates en pipelines)
