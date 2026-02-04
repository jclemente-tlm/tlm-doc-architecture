---
id: testing
sidebar_position: 2
title: Estrategia de Pruebas
description: Estrategia de testing automatizado multinivel para garantizar calidad del software
---

# Estrategia de Pruebas

La ausencia de testing automatizado genera código frágil, regresiones frecuentes y acumulación de deuda técnica que ralentiza entregas y compromete estabilidad de producción. Dependencia exclusiva de testing manual limita cobertura, velocidad de validación y capacidad de refactoring seguro. Implementar estrategia de pruebas multinivel (unitarias, integración, contrato) con continuous testing en CI/CD detecta defectos tempranamente, permite entregas frecuentes con confianza y mantiene calidad sostenible del software.

> **Nota:** Para monitoreo, alertas y observabilidad ver [Observabilidad](../arquitectura/05-observabilidad.md).

**Este lineamiento aplica a:** Pruebas automatizadas (unitarias, integración, e2e), testing de contratos entre servicios, cobertura de código, continuous testing en CI/CD, frameworks de testing (xUnit, Moq).

**No aplica a:** Monitoreo y alertas en producción, gestión de incidentes operativos, estándares de calidad de código (ver [Calidad de Código](./01-calidad-codigo.md)).

## Estándares Obligatorios

- [Implementar pruebas automatizadas en múltiples niveles (unitarias, integración, e2e)](../../estandares/desarrollo/testing-standards.md)
- [Escribir pruebas unitarias con cobertura mínima del 80%](../../estandares/desarrollo/testing-standards.md#unit-tests)
- [Implementar pruebas de integración para validar interacciones entre componentes](../../estandares/desarrollo/testing-standards.md#integration-tests)
- [Usar contract testing para validar contratos entre servicios](../../estandares/desarrollo/testing-standards.md#contract-tests)

## Referencias Relacionadas

- [Calidad de Código](./01-calidad-codigo.md) (estándares de código y revisiones)
- [Observabilidad](../arquitectura/05-observabilidad.md) (monitoreo y alertas en producción)
