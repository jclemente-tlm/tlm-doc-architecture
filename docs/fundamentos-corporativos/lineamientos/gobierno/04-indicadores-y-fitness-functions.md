---
id: indicadores-y-fitness-functions
sidebar_position: 4
title: Indicadores y Fitness Functions
description: Métricas objetivas y validaciones automatizadas para guiar la evolución de la arquitectura
---

# Indicadores y Fitness Functions

Las decisiones arquitectónicas sin validación continua se degradan silenciosamente: el acoplamiento aumenta, los SLOs se incumplen y la deuda técnica crece sin señales visibles hasta que el costo de corrección es alto. Las fitness functions son mecanismos de validación automatizados que miden si la arquitectura sigue cumpliendo sus objetivos (latencia, acoplamiento, cobertura, dependencias), convirtiéndose en la forma objetiva de gobernar la evolución del sistema.

**Este lineamiento aplica a:** atributos de calidad definidos en ADRs, SLOs de servicios en producción, restricciones de acoplamiento entre módulos/servicios, métricas de deuda técnica y umbrales de complejidad ciclomática.

**No aplica a:** métricas de negocio o KPIs de producto — ver [Observabilidad](../operabilidad/05-observabilidad.md) para SLIs/SLOs operacionales.

## Estándares Obligatorios

- [Definir fitness functions para cada atributo de calidad crítico](../../estandares/arquitectura/architecture-evolution.md#1-fitness-functions)
- [Automatizar validación de fitness functions en pipelines CI/CD](../../estandares/arquitectura/architecture-evolution.md#1-fitness-functions)
- [Vincular cada fitness function a un ADR o decisión de arquitectura](../../estandares/gobierno/adr-management.md)
- [Revisar resultados de fitness functions en architecture reviews periódicos](../../estandares/gobierno/architecture-review-process.md#architecture-review)
- [Alertar y bloquear merge cuando una fitness function supera umbral crítico](../../estandares/gobierno/compliance-validation.md)
- [Documentar fitness functions junto al código que validan](../../estandares/gobierno/adr-management.md)

## Referencias Relacionadas

- [Decisiones Arquitectónicas](./01-decisiones-arquitectonicas.md)
- [Revisiones Arquitectónicas](./02-revisiones-arquitectonicas.md)
- [Cumplimiento y Excepciones](./03-cumplimiento-y-excepciones.md)
- [Arquitectura Evolutiva](../arquitectura/09-arquitectura-evolutiva.md)
