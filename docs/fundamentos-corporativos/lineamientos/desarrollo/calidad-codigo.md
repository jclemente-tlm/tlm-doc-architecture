---
id: calidad-codigo
sidebar_position: 1
title: Calidad de Código
description: Estándares de calidad de código, convenciones y revisiones
---

# Calidad de Código

Código sin estándares consistentes, análisis estático ni revisiones genera deuda técnica, bugs ocultos y mantenibilidad decreciente que encarece evolución del software. Convenciones inconsistentes entre equipos dificultan colaboración y transferencia de conocimiento. Establecer estándares de código (C#, SQL), análisis estático automatizado (SonarQube, StyleCop), code review obligatorio y quality gates en CI/CD garantiza legibilidad, detecta vulnerabilidades tempranamente y mantiene calidad sostenible del código base.

**Este lineamiento aplica a:** convenciones de código (C#, SQL), análisis estático y linters (SonarQube, StyleCop), code reviews y revisión por pares, métricas de calidad (complejidad ciclomática, duplicación), herramientas de formateo y estilo.

## Prácticas Obligatorias

- [Seguir convenciones de código del stack tecnológico](../../estandares/desarrollo/code-quality.md#1-code-conventions)
- [Refactorizar aplicando principios SOLID y eliminando deuda técnica](../../estandares/desarrollo/code-quality.md#3-refactoring-practices)
- [Implementar análisis estático con linters](../../estandares/desarrollo/code-quality.md#5-static-analysis)
- [Realizar SAST en pipelines CI/CD](../../estandares/desarrollo/code-quality.md#4-sast-static-application-security-testing)
- [Ejecutar code review obligatorio](../../estandares/desarrollo/code-quality.md#2-code-review)
- [Definir quality gates con métricas mínimas](../../estandares/desarrollo/code-quality.md#6-quality-gates)

## Referencias Relacionadas

- [Estrategia de Pruebas](./estrategia-pruebas.md) (testing automatizado)
- [CI/CD y Automatización](../operabilidad/cicd-pipelines.md) (quality gates en pipelines)
