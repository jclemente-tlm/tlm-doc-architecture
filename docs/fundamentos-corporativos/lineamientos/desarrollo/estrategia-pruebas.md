---
id: estrategia-pruebas
sidebar_position: 2
title: Estrategia de Pruebas
description: Estrategia de testing automatizado multinivel para garantizar calidad del software
---

# Estrategia de Pruebas

La ausencia de testing automatizado genera código frágil, regresiones frecuentes y acumulación de deuda técnica que ralentiza entregas y compromete estabilidad de producción. Dependencia exclusiva de testing manual limita cobertura, velocidad de validación y capacidad de refactoring seguro. Implementar estrategia de pruebas multinivel (unitarias, integración, contrato) con continuous testing en CI/CD detecta defectos tempranamente, permite entregas frecuentes con confianza y mantiene calidad sostenible del software.

> **Nota:** Para monitoreo, alertas y observabilidad ver [Observabilidad](../operabilidad/observabilidad.md).

**Este lineamiento aplica a:** pruebas automatizadas (unitarias, integración, e2e), testing de contratos entre servicios, cobertura de código, continuous testing en CI/CD, frameworks de testing (xUnit, Moq).

## Prácticas Obligatorias

- [Seguir pirámide de testing (unitarias → integración → e2e)](../../estandares/testing/testing-pyramid.md)
- [Implementar pruebas unitarias](../../estandares/testing/unit-testing.md)
- [Implementar pruebas de integración](../../estandares/testing/integration-testing.md)
- [Implementar contract testing](../../estandares/testing/contract-testing.md)
- [Implementar pruebas end-to-end](../../estandares/testing/e2e-testing.md)
- [Definir cobertura mínima de código](../../estandares/testing/test-coverage.md)
- [Automatizar ejecución de pruebas en CI/CD](../../estandares/testing/test-automation.md)
- [Realizar performance testing](../../estandares/testing/performance-testing.md)
- [Realizar security testing en pipelines CI/CD](../../estandares/testing/security-testing.md)

## Referencias Relacionadas

- [Calidad de Código](./calidad-codigo.md) (estándares de código y revisiones)
- [Observabilidad](../operabilidad/observabilidad.md) (monitoreo y alertas en producción)
