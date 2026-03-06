---
id: test-coverage
sidebar_position: 3
title: Cobertura de Código
description: Estándares para objetivos de cobertura, configuración de Coverlet y tracking con SonarQube
tags: [testing, cobertura, coverlet, sonarqube, calidad]
---

# Cobertura de Código

## Contexto

Este estándar define los **objetivos y configuración de cobertura de código**: mide el porcentaje de código ejecutado por tests, identifica gaps y garantiza compliance con estándares de calidad.

---

## Stack Tecnológico

| Componente    | Tecnología      | Versión | Uso                                |
| ------------- | --------------- | ------- | ---------------------------------- |
| **Coverage**  | Coverlet        | 6.0+    | Code coverage collection           |
| **Reporting** | ReportGenerator | 5.2+    | Reportes HTML de coverage          |
| **Analysis**  | SonarQube       | 9.9+    | Análisis de coverage y tendencias  |
| **CI/CD**     | GitHub Actions  | Latest  | Publicación automática de reportes |

---

## Cobertura de Código

### ¿Qué es Test Coverage?

Métrica que mide porcentaje de código ejecutado por tests. Incluye line coverage, branch coverage y method coverage.

**Propósito:** Asegurar que código crítico está testeado, identificar gaps de testing.

**Métricas:**

- **Line Coverage**: % de líneas ejecutadas
- **Branch Coverage**: % de branches (if/else) ejecutadas
- **Method Coverage**: % de métodos ejecutados
- **Mutation Coverage**: % de mutaciones detectadas (avanzado)

**Objetivos por tipo:**

- **Unit Tests**: 90% line coverage
- **Integration Tests**: 80% line coverage
- **Overall**: 85% line coverage mínimo

**Beneficios:**
✅ Identificar código no testeado
✅ Prevenir regresiones
✅ Guiar esfuerzos de testing
✅ Compliance con estándares de calidad

### Configuración: Coverlet y ReportGenerator

```xml
<!-- OrderService.Tests.csproj -->
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net8.0</TargetFramework>
    <IsPackable>false</IsPackable>
  </PropertyGroup>

  <ItemGroup>
    <PackageReference Include="xunit" Version="2.6.6" />
    <PackageReference Include="xunit.runner.visualstudio" Version="2.5.6" />
    <PackageReference Include="coverlet.collector" Version="6.0.0" />
    <PackageReference Include="coverlet.msbuild" Version="6.0.0" />
  </ItemGroup>
</Project>
```

```bash
# Generar coverage report localmente
dotnet test \
  --collect:"XPlat Code Coverage" \
  --results-directory ./TestResults \
  -- DataCollectionRunSettings.DataCollectors.DataCollector.Configuration.Format=opencover

# Generar HTML report
dotnet tool install -g dotnet-reportgenerator-globaltool

reportgenerator \
  -reports:"TestResults/**/coverage.opencover.xml" \
  -targetdir:"CoverageReport" \
  -reporttypes:"Html;Badges"
```

### Coverage Thresholds

```xml
<!-- coverlet.runsettings -->
<?xml version="1.0" encoding="utf-8"?>
<RunSettings>
  <DataCollectionRunSettings>
    <DataCollectors>
      <DataCollector friendlyName="XPlat code coverage">
        <Configuration>
          <Format>opencover</Format>
          <Exclude>[*.Tests]*,[*]*.Migrations.*</Exclude>
          <Include>[OrderService.*]*</Include>
          <!-- Fail build si coverage < 80% -->
          <Threshold>80</Threshold>
          <ThresholdType>line,branch,method</ThresholdType>
          <ThresholdStat>total</ThresholdStat>
        </Configuration>
      </DataCollector>
    </DataCollectors>
  </DataCollectionRunSettings>
</RunSettings>
```

### Excluir Código de Coverage

```csharp
// Excluir código generado por EF Core
[ExcludeFromCodeCoverage]
public partial class OrderEntityTypeConfiguration { }

// Excluir Program.cs (bootstrap)
[ExcludeFromCodeCoverage]
public class Program
{
    public static void Main(string[] args) =>
        CreateHostBuilder(args).Build().Run();
}

// Excluir DTOs simples (solo properties)
[ExcludeFromCodeCoverage]
public record OrderDto
{
    public int Id { get; init; }
    public string CustomerName { get; init; }
}
```

### Reporte de Cobertura Ejemplo

```plaintext
Coverage Report - Order Service
=====================================

Summary:
  Line Coverage:    92.5% (850/920 lines)
  Branch Coverage:  87.3% (245/281 branches)
  Method Coverage:  94.1% (160/170 methods)

By Assembly:
  OrderService.Domain:          95.2% ✅
  OrderService.Application:     91.8% ✅
  OrderService.Infrastructure:  89.5% ✅
  OrderService.Api:             88.7% ✅

Uncovered Areas:
  ⚠️ OrderService.Application.Services.NotificationService
     Lines: 15-23 (9 lines not covered)
     Reason: External API call not mocked

  ⚠️ OrderService.Domain.Aggregates.Order.Cancel()
     Branches: 1/2 covered
     Missing: Exception handling path

Action Items:
  1. Add tests for NotificationService error scenarios
  2. Add test for Order.Cancel() when already cancelled
```

---

## Monitoreo y Observabilidad

```plaintext
Order Service - Coverage Dashboard (SonarQube)
==============================================

Coverage Metrics:
  Overall Coverage:     87.2% ✅  (target: > 85%)
  New Code Coverage:    92.1% ✅  (target: > 80%)

  By Type:
    Unit:               92.5%
    Integration:        81.3%
    E2E:                N/A (excluído)

Quality Gate:           PASSED ✅

Trends (last 30 days):
  Coverage:             📈 +2.3%
  Test Count:           📈 +15 tests
  Execution Time:       📉 -45s
  Flaky Tests:          📉 -3
```

---

## Requisitos Técnicos

### MUST (Obligatorio)

- **MUST** 90% line coverage en unit tests
- **MUST** 80% line coverage en integration tests
- **MUST** 85% line coverage overall mínimo
- **MUST** excluir código generado (`[ExcludeFromCodeCoverage]`) de métricas
- **MUST** reportar coverage en SonarQube en cada PR

### SHOULD (Fuertemente recomendado)

- **SHOULD** generar HTML coverage reports localmente
- **SHOULD** tracking de coverage trends en el tiempo
- **SHOULD** mutation testing para código de negocio crítico

### MUST NOT (Prohibido)

- **MUST NOT** bajar coverage para hacer pasar el build
- **MUST NOT** aplicar `[ExcludeFromCodeCoverage]` a lógica de negocio
- **MUST NOT** contar archivos de migración en la métrica total

---

## Referencias

- [Coverlet Documentation](https://github.com/coverlet-coverage/coverlet)
- [ReportGenerator](https://reportgenerator.io/)
- [SonarQube .NET](https://docs.sonarqube.org/latest/analysis/languages/csharp/)
- [Pirámide de Testing](./testing-pyramid.md)
- [Automatización de Tests](./test-automation.md)
