---
id: testing-pyramid
sidebar_position: 1
title: Pirámide de Testing
description: Estándares para proporciones óptimas entre unit, integration y E2E tests
tags: [testing, piramide, calidad, xunit, sonarqube]
---

# Pirámide de Testing

## Contexto

Este estándar define la **pirámide de testing**: proporciones óptimas entre tipos de tests para balance entre velocidad, costo y confianza. Tests unitarios en la base (rápidos, baratos, abundantes), E2E en la cima (lentos, caros, selectivos).

---

## Stack Tecnológico

| Componente       | Tecnología       | Versión | Uso                             |
| ---------------- | ---------------- | ------- | ------------------------------- |
| **Unit Testing** | xUnit            | 2.6+    | Framework de testing principal  |
| **Assertions**   | FluentAssertions | 6.12+   | Assertions expresivas           |
| **Mocking**      | Moq              | 4.20+   | Mocking de dependencias         |
| **Analysis**     | SonarQube        | 9.9+    | Análisis de cobertura y calidad |
| **CI/CD**        | GitHub Actions   | Latest  | Ejecución automática de tests   |

---

## Pirámide de Testing

### ¿Qué es la Testing Pyramid?

Estrategia que define proporciones óptimas entre tipos de tests para balance entre velocidad, costo y confianza.

**Propósito:** Optimizar ROI de testing maximizando cobertura con mínimo tiempo de ejecución.

**Proporciones recomendadas:**

- **Unit Tests**: 70-80% del total (milisegundos por test)
- **Integration Tests**: 15-20% del total (segundos por test)
- **E2E Tests**: 5-10% del total (minutos por test)

**Beneficios:**
✅ Fast feedback loops (suite completa < 10 minutos)
✅ Menor costo de mantenimiento
✅ Alta confianza con cobertura estratificada
✅ Facilita TDD/BDD

### Ejemplo: Distribución en Order Service

```plaintext
Order Service Testing Distribution
=====================================
Total tests: 450

📊 Unit Tests (360 tests - 80%)
  ├─ Domain Models: 120 tests
  ├─ Business Logic: 150 tests
  ├─ Validators: 40 tests
  ├─ Mappers: 30 tests
  └─ Utilities: 20 tests
  Execution time: ~2 minutes

📊 Integration Tests (70 tests - 15.5%)
  ├─ API Endpoints: 30 tests
  ├─ Database Operations: 20 tests
  ├─ Message Publishing: 10 tests
  ├─ External API Calls: 10 tests
  Execution time: ~5 minutes

📊 E2E Tests (20 tests - 4.5%)
  ├─ Critical User Journeys: 15 tests
  ├─ Smoke Tests: 5 tests
  Execution time: ~8 minutes

Total execution time: ~15 minutes
```

### Anti-Pattern: Pirámide Invertida (Ice Cream Cone)

```csharp
// ❌ MALO: Demasiados E2E tests, pocos unit tests
public class AntiPatternTestSuite
{
    // 10 unit tests
    [Fact]
    public void Order_ShouldCalculateTotal() { }

    // 50 E2E tests (LENTO, FRÁGIL)
    [Fact]
    public async Task E2E_CreateOrder_PayWithCreditCard_SendEmail()
    {
        // Setup browser → Navigate → Fill form → Submit → Check email → Cleanup
        // Takes 2-3 minutes per test
    }
}

// ❌ Problemas:
// - Suite toma 2+ horas en ejecutar
// - Flaky tests (timeouts, race conditions)
// - Difícil debugging (muchas capas involucradas)
// - Costoso mantener (cambios en UI rompen muchos tests)
```

```csharp
// ✅ BUENO: Mayoría unit tests, selectivos E2E
[Theory]
[InlineData(100, 0.18, 18)]
[InlineData(1000, 0.18, 180)]
public void CalculateOrderTax_ShouldApplyCorrectRate(
    decimal subtotal, decimal taxRate, decimal expectedTax)
{
    var order = new Order { Subtotal = subtotal };
    var tax = order.CalculateTax(taxRate);
    tax.Should().Be(expectedTax);
}

// 15 integration tests → verifican integración real
// 5 E2E tests → solo flujos críticos
```

### Matriz de Decisión: ¿Qué tipo de test usar?

| Escenario                            | Unit | Integration | E2E | Justificación                           |
| ------------------------------------ | ---- | ----------- | --- | --------------------------------------- |
| Validar lógica de negocio (cálculos) | ✅   | -           | -   | Rápido, aislado, deterministico         |
| Validar esquema de BD                | -    | ✅          | -   | Requiere DB real                        |
| Validar serialización JSON           | ✅   | -           | -   | No requiere infraestructura             |
| Validar API contract                 | -    | ✅          | -   | Requiere HTTP pero no UI                |
| Validar integración con Kafka        | -    | ✅          | -   | Requiere message broker                 |
| Validar journey usuario crítico      | -    | -           | ✅  | Requiere todos los sistemas             |
| Validar formato error 400            | ✅   | ✅          | -   | Unit primero, integration para detalles |
| Validar autenticación JWT            | -    | ✅          | -   | Requiere token real pero no UI          |

---

## Monitoreo y Observabilidad

```plaintext
Order Service - Testing Distribution Dashboard
===============================================

Proporciones actuales:
  Unit Tests:         80%  ✅ (target: 70-80%)
  Integration Tests:  15%  ✅ (target: 15-20%)
  E2E Tests:          5%   ✅ (target: 5-10%)

Execution times:
  Unit suite:         2m 10s  ✅ (target: < 5min)
  Integration suite:  5m 30s  ✅ (target: < 10min)
  Full suite:         15m 40s ✅ (target: < 15min)

Quality Gate:         PASSED ✅
```

---

## Requisitos Técnicos

### MUST (Obligatorio)

- **MUST** mantener 70-80% unit tests, 15-20% integration, 5-10% E2E
- **MUST** ejecutar suite completa en < 15 minutos
- **MUST** unit tests ejecutarse en < 5 minutos
- **MUST** tests aislados (sin dependencias entre ellos)

### SHOULD (Fuertemente recomendado)

- **SHOULD** ejecutar tests en paralelo para reducir tiempo total
- **SHOULD** documentar distribución explícita del proyecto

### MUST NOT (Prohibido)

- **MUST NOT** ejecutar E2E tests en cada commit (solo en main/release)
- **MUST NOT** utilizar E2E para escenarios cubiertos por unit tests
- **MUST NOT** ignorar métricas de distribución en code reviews

---

## Referencias

- [Test Pyramid - Martin Fowler](https://martinfowler.com/articles/practical-test-pyramid.html)
- [Testing Best Practices - Microsoft](https://learn.microsoft.com/en-us/dotnet/core/testing/unit-testing-best-practices)
- [xUnit Documentation](https://xunit.net/)
- [Automatización de Tests](./test-automation.md)
- [Cobertura de Código](./test-coverage.md)
- [Pruebas Unitarias](./unit-testing.md)
