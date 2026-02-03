---
id: testing-y-calidad
sidebar_position: 4
title: Testing y Calidad
description: Testing y calidad integrados en el ciclo de desarrollo desde el diseño
---

# Testing y Calidad

La ausencia de testing automatizado y controles de calidad genera código frágil, regresiones frecuentes y acumulación de deuda técnica que ralentiza entregas y compromete estabilidad de producción. Dependencia de testing manual exclusivo limita cobertura y velocidad de validación. Integrar pruebas automatizadas multinivel, análisis estático, code review obligatorio y quality gates en CI/CD establece barreras de calidad tempranas que detectan defectos antes de producción, permiten refactoring seguro y mantienen mantenibilidad del código a largo plazo.

> **Nota:** Para monitoreo, alertas y observabilidad ver [Observabilidad](../arquitectura/05-observabilidad.md).

**Este lineamiento aplica a:** Pruebas automatizadas (unitarias, integración, e2e), análisis estático de código (linters, SonarQube), code reviews y revisión por pares, cobertura de código y métricas de calidad, continuous testing en CI/CD.

**No aplica a:** Monitoreo y alertas en producción, gestión de incidentes operativos.

## Estándares Obligatorios

- [Implementar pruebas automatizadas en múltiples niveles (unitarias, integración, e2e)](../../estandares/operabilidad/testing-pyramid.md)
- [Mantener cobertura de código mínima del 80% en lógica de negocio crítica](../../estandares/operabilidad/cobertura-codigo.md)
- [Ejecutar análisis estático de código en pipeline CI/CD](../../estandares/operabilidad/analisis-estatico.md)
- [Realizar code review obligatorio antes de merge a ramas principales](../../estandares/operabilidad/code-review-policy.md)
- [Aplicar estrategia de testing según pirámide de tests](../../estandares/operabilidad/estrategia-testing.md)

## Referencias Relacionadas

- [Observabilidad](../arquitectura/05-observabilidad.md) (para monitoreo y alertas en producción)
