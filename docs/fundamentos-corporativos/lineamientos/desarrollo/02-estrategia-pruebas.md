---
id: estrategia-pruebas
sidebar_position: 2
title: Estrategia de Pruebas
description: Estrategia de testing automatizado multinivel para garantizar calidad del software
---

# Estrategia de Pruebas

La ausencia de testing automatizado genera código frágil, regresiones frecuentes y acumulación de deuda técnica que ralentiza entregas y compromete estabilidad de producción. Dependencia exclusiva de testing manual limita cobertura, velocidad de validación y capacidad de refactoring seguro. Implementar estrategia de pruebas multinivel (unitarias, integración, contrato) con continuous testing en CI/CD detecta defectos tempranamente, permite entregas frecuentes con confianza y mantiene calidad sostenible del software.

> **Nota:** Para monitoreo, alertas y observabilidad ver [Observabilidad](../arquitectura/06-observabilidad.md).

**Este lineamiento aplica a:** Pruebas automatizadas (unitarias, integración, e2e), testing de contratos entre servicios, cobertura de código, continuous testing en CI/CD, frameworks de testing (xUnit, Moq).

**No aplica a:** Monitoreo y alertas en producción, gestión de incidentes operativos, estándares de calidad de código (ver [Calidad de Código](./01-calidad-codigo.md)).

## Estándares Obligatorios

- [Implementar pruebas unitarias](../../estandares/testing/unit-integration-testing.md#1-unit-testing)
- [Implementar pruebas de integración](../../estandares/testing/unit-integration-testing.md#2-integration-testing)
- [Implementar contract testing](../../estandares/testing/contract-e2e-testing.md#1-contract-testing)
- [Implementar pruebas end-to-end](../../estandares/testing/contract-e2e-testing.md#2-e2e-testing)
- [Definir cobertura mínima de código](../../estandares/testing/testing-strategy.md#3-test-coverage)
- [Automatizar ejecución de pruebas en CI/CD](../../estandares/testing/testing-strategy.md#2-test-automation)
- [Realizar performance testing](../../estandares/testing/performance-testing.md)

## Referencias Relacionadas

- [Calidad de Código](./01-calidad-codigo.md) (estándares de código y revisiones)
- [Observabilidad](../arquitectura/06-observabilidad.md) (monitoreo y alertas en producción)
