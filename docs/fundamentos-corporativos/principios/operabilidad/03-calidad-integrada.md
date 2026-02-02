---
id: calidad-integrada
sidebar_position: 3
title: Calidad Integrada
description: La calidad es responsabilidad de todos y se integra en cada etapa del flujo de desarrollo y operación
---

# Calidad Integrada

## 1. Declaración

La calidad es responsabilidad compartida de todo el equipo y debe integrarse en cada etapa del ciclo de desarrollo, desde la definición de requisitos hasta la operación en producción.

## 2. Justificación

Este principio busca construir sistemas confiables, mantenibles y predecibles mediante la integración de prácticas de calidad en cada etapa del flujo de valor.

La calidad integrada reduce el costo de corrección de defectos al detectarlos tempranamente, disminuye el retrabajo, y acelera la entrega de valor al evitar ciclos largos de validación al final del proceso.

Al hacer de la calidad una responsabilidad compartida, se fomenta la colaboración entre roles (desarrollo, QA, operaciones, producto) y se establece una cultura de mejora continua basada en validación temprana y automatizada.

## 3. Alcance y Contexto

Aplica a:

- **Desarrollo:** Testing automatizado (unitario, integración, E2E), code reviews, pair programming
- **CI/CD:** Quality gates en pipelines, análisis estático de código, validación de seguridad
- **Operaciones:** Monitoreo proactivo, alertas tempranas, validación de deployments
- **Colaboración:** Definición de criterios de aceptación, validación temprana de requisitos

No se limita a testing, sino a integrar validación, retroalimentación y mejora en cada actividad del flujo de desarrollo y operación.

## 4. Implicaciones

- Todos los pipelines de CI/CD deben incluir quality gates automatizados (pruebas, análisis estático, validación de seguridad).
- Los equipos deben adoptar prácticas de testing temprano (TDD, shift-left testing) y code reviews sistemáticas.
- La arquitectura debe diseñarse para facilitar testabilidad, observabilidad y validación automatizada.
- Las métricas de calidad (cobertura, bugs, deuda técnica) deben ser visibles y monitoreadas continuamente.
- Los criterios de aceptación deben definirse colaborativamente antes del desarrollo y validarse de forma automatizada.

**Compensaciones (Trade-offs):**

Requiere inversión inicial en automatización, herramientas y capacitación del equipo. A cambio, reduce significativamente el retrabajo, acelera la entrega, y aumenta la confiabilidad del sistema en producción.
