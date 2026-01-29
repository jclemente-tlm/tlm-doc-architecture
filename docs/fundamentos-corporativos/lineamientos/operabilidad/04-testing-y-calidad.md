---
id: testing-y-calidad
sidebar_position: 4
title: Testing y Calidad
description: Testing y calidad integrados en el ciclo de desarrollo desde el diseño
---

# Testing y Calidad

## 1. Propósito

Establecer que testing y calidad de código deben integrarse desde el diseño y desarrollo, garantizando software confiable y mantenible mediante prácticas automatizadas.

> **Nota:** Para monitoreo, alertas y observabilidad ver [Observabilidad](../arquitectura/05-observabilidad.md).

---

## 2. Alcance

Aplica a:

- Pruebas automatizadas (unitarias, integración, e2e)
- Análisis estático de código (linters, SonarQube)
- Code reviews y revisión por pares
- Cobertura de código y métricas de calidad
- Continuous testing en CI/CD

No aplica a:

- Monitoreo y alertas en producción (ver Arquitectura/Observabilidad)
- Gestión de incidentes operativos (ver Arquitectura/Observabilidad)

---

## 3. Lineamientos Obligatorios

- Implementar pruebas automatizadas en múltiples niveles (unitarias, integración, e2e)
- Mantener cobertura de código mínima del 80% en lógica de negocio crítica
- Ejecutar análisis estático de código en pipeline CI/CD
- Realizar code review obligatorio antes de merge a ramas principales
- Aplicar estrategia de testing según pirámide de tests

**Pirámide de tests:**

- Base: Pruebas unitarias (70%) - rápidas, aisladas
- Medio: Pruebas de integración (20%) - componentes integrados
- Cima: Pruebas e2e (10%) - flujos completos

---

## 4. Decisiones de Diseño Esperadas

- Estrategia de testing (niveles, herramientas, frameworks)
- Cobertura mínima de código por tipo de componente
- Herramientas de análisis estático (SonarQube, StyleCop, SQL Lint)
- Proceso de code review (aprobadores, criterios)
- Estrategia de test data y fixtures
- Políticas de quality gates en CI/CD

---

## 5. Antipatrones y Prácticas Prohibidas

- Testing exclusivamente manual sin automatización
- Código sin pruebas unitarias en lógica crítica
- Merge a main/master sin code review
- Ignorar warnings de análisis estático
- Tests e2e como única capa de testing
- Cobertura de código artificial (tests vacíos)
- Deshabilitar quality gates para cumplir plazos

---

## 6. Principios Relacionados

- [Calidad desde el Diseño](../../principios/operabilidad/03-calidad-desde-el-diseno.md)
- Automatización como Principio
- Arquitectura Limpia
- Simplicidad Intencional

---

## 7. Validación y Cumplimiento

- Revisión de cobertura de pruebas en reportes CI/CD
- Verificación de quality gates activos en pipelines
- Auditoría de métricas de calidad (code smells, bugs, vulnerabilidades)
- Revisión de configuración de herramientas de análisis estático
- Validación de proceso de code review en pull requests
- Análisis de tendencias de calidad (deuda técnica, cobertura)
