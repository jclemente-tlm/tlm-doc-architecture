---
id: test-automation
sidebar_position: 2
title: Automatización de Tests
description: Estándares para ejecución automática en CI/CD, quality gates y ejecución paralela de tests
tags: [testing, automatizacion, ci-cd, github-actions, sonarqube]
---

# Automatización de Tests

## Contexto

Este estándar define la **automatización de tests en CI/CD**: ejecución automática con quality gates que bloquean merges/deployments si tests fallan o la cobertura baja.

---

## Stack Tecnológico

| Componente       | Tecnología       | Versión | Uso                            |
| ---------------- | ---------------- | ------- | ------------------------------ |
| **Unit Testing** | xUnit            | 2.6+    | Framework de testing principal |
| **Assertions**   | FluentAssertions | 6.12+   | Assertions expresivas          |
| **Coverage**     | Coverlet         | 6.0+    | Code coverage collection       |
| **Analysis**     | SonarQube        | 9.9+    | Quality gates y análisis       |
| **CI/CD**        | GitHub Actions   | Latest  | Ejecución automática de tests  |

---

## Automatización de Tests

### ¿Qué es Test Automation?

Ejecución automática de tests en CI/CD con gates de calidad que bloquean merges/deployments si tests fallan o coverage baja.

**Propósito:** Prevenir regresiones y garantizar calidad consistente sin intervención manual.

**Componentes:**

- **CI Pipeline**: Ejecutar tests en cada PR
- **Quality Gates**: Bloquear si tests fallan o coverage < threshold
- **Fast Feedback**: Resultados en < 15 minutos
- **Parallel Execution**: Tests en paralelo por velocidad

**Beneficios:**
✅ Detección temprana de bugs (shift-left)
✅ Prevención de regresiones
✅ Confidence para refactoring
✅ Deployment seguro

### Pipeline CI/CD con GitHub Actions

```yaml
# .github/workflows/test.yml
name: Test Suite

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  unit-tests:
    name: Unit Tests
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Setup .NET
        uses: actions/setup-dotnet@v3
        with:
          dotnet-version: "8.0.x"

      - name: Restore dependencies
        run: dotnet restore

      - name: Run unit tests
        run: |
          dotnet test \
            --filter "Category=Unit" \
            --no-restore \
            --logger "trx;LogFileName=unit-test-results.trx" \
            --collect:"XPlat Code Coverage" \
            --results-directory ./TestResults \
            -- DataCollectionRunSettings.DataCollectors.DataCollector.Configuration.Format=opencover

      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: unit-test-results
          path: TestResults/unit-test-results.trx

      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          files: ./TestResults/**/coverage.opencover.xml
          flags: unit
          fail_ci_if_error: true

  integration-tests:
    name: Integration Tests
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: orders_test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432

    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Setup .NET
        uses: actions/setup-dotnet@v3
        with:
          dotnet-version: "8.0.x"

      - name: Run integration tests
        env:
          ConnectionStrings__OrdersDb: "Host=localhost;Port=5432;Database=orders_test;Username=postgres;Password=postgres"
        run: |
          dotnet test \
            --filter "Category=Integration" \
            --no-restore \
            --logger "trx;LogFileName=integration-test-results.trx" \
            --results-directory ./TestResults

  quality-gate:
    name: Quality Gate
    runs-on: ubuntu-latest
    needs: [unit-tests, integration-tests]

    steps:
      - name: Download coverage reports
        uses: actions/download-artifact@v3

      - name: SonarQube Scan
        uses: sonarsource/sonarqube-scan-action@master
        env:
          SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
          SONAR_HOST_URL: ${{ secrets.SONAR_HOST_URL }}
        with:
          args: >
            -Dsonar.projectKey=order-service
            -Dsonar.coverage.exclusions=**/*.generated.cs,**/Program.cs
            -Dsonar.cs.opencover.reportsPaths=TestResults/**/coverage.opencover.xml
            -Dsonar.qualitygate.wait=true
```

### Quality Gate en SonarQube

```json
{
  "qualityGate": {
    "name": "Talma Quality Gate",
    "conditions": [
      {
        "metric": "coverage",
        "operator": "LESS_THAN",
        "threshold": "80",
        "status": "ERROR"
      },
      {
        "metric": "new_coverage",
        "operator": "LESS_THAN",
        "threshold": "80",
        "status": "ERROR"
      },
      {
        "metric": "duplicated_lines_density",
        "operator": "GREATER_THAN",
        "threshold": "3",
        "status": "WARNING"
      },
      {
        "metric": "new_bugs",
        "operator": "GREATER_THAN",
        "threshold": "0",
        "status": "ERROR"
      },
      {
        "metric": "new_vulnerabilities",
        "operator": "GREATER_THAN",
        "threshold": "0",
        "status": "ERROR"
      }
    ]
  }
}
```

### Ejecución Paralela de Tests

```xml
<!-- Directory.Build.props -->
<Project>
  <PropertyGroup>
    <ParallelizeAssembly>true</ParallelizeAssembly>
    <ParallelizeTestCollections>true</ParallelizeTestCollections>
    <MaxParallelThreads>8</MaxParallelThreads>
  </PropertyGroup>
</Project>
```

```csharp
// Tests con estado compartido → misma Collection (NO paralelos entre sí)
[Collection("OrderTests")]
public class OrderServiceTests { }

// Tests aislados → sin Collection (paralelos entre sí)
public class CalculatorTests
{
    [Fact]
    public void Add_ShouldReturnSum() { }
}
```

### Estructura del Proyecto de Tests

```csharp
// tests/OrderService.Tests/OrderService.Tests.csproj
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net8.0</TargetFramework>
    <IsPackable>false</IsPackable>
    <RootNamespace>OrderService.Tests</RootNamespace>
  </PropertyGroup>

  <ItemGroup>
    <PackageReference Include="xUnit" Version="2.6.6" />
    <PackageReference Include="xunit.runner.visualstudio" Version="2.5.6" />
    <PackageReference Include="FluentAssertions" Version="6.12.0" />
    <PackageReference Include="Moq" Version="4.20.70" />
    <PackageReference Include="coverlet.collector" Version="6.0.0" />
    <PackageReference Include="Microsoft.AspNetCore.Mvc.Testing" Version="8.0.0" />
    <PackageReference Include="Testcontainers.PostgreSql" Version="3.7.0" />
  </ItemGroup>

  <ItemGroup>
    <ProjectReference Include="..\..\src\OrderService.Api\OrderService.Api.csproj" />
  </ItemGroup>
</Project>
```

```csharp
// tests/OrderService.Tests/Common/TestBase.cs
// Clases base que categorizan tests automáticamente

[Trait("Category", "Unit")]
public abstract class UnitTest { }

[Trait("Category", "Integration")]
public abstract class IntegrationTest : IAsyncLifetime
{
    protected WebApplicationFactory<Program> Factory { get; private set; }
    protected HttpClient Client { get; private set; }

    public async Task InitializeAsync()
    {
        Factory = new WebApplicationFactory<Program>();
        Client = Factory.CreateClient();
        await Task.CompletedTask;
    }

    public async Task DisposeAsync()
    {
        Client?.Dispose();
        await Factory.DisposeAsync();
    }
}

[Trait("Category", "E2E")]
public abstract class E2ETest { }
```

---

## Monitoreo y Observabilidad

```csharp
// Métricas de ejecución de tests para Prometheus
public class TestMetricsCollector
{
    private readonly Counter _testsExecuted = Metrics.CreateCounter(
        "tests_executed_total",
        "Total number of tests executed",
        new CounterConfiguration { LabelNames = new[] { "type", "result" } });

    private readonly Histogram _testDuration = Metrics.CreateHistogram(
        "test_duration_seconds",
        "Test execution duration",
        new HistogramConfiguration { LabelNames = new[] { "type", "name" } });

    public void RecordTestExecution(string type, string name, bool passed, TimeSpan duration)
    {
        _testsExecuted.WithLabels(type, passed ? "pass" : "fail").Inc();
        _testDuration.WithLabels(type, name).Observe(duration.TotalSeconds);
    }
}
```

```promql
# Tests fallando en el último build
sum by (type) (tests_executed_total{result="fail"}) > 0

# Tiempo de ejecución de suite superando umbral (> 15 min)
sum(test_duration_seconds_sum{type="unit"}) > 900
```

---

## Requisitos Técnicos

### MUST (Obligatorio)

- **MUST** ejecutar tests en CI/CD en cada PR
- **MUST** bloquear merge si tests fallan
- **MUST** ejecutar tests antes de deploy a producción
- **MUST** tests aislados (sin dependencias entre ellos)
- **MUST** quality gate en SonarQube con coverage ≥ 80%

### SHOULD (Fuertemente recomendado)

- **SHOULD** ejecutar tests en paralelo para reducir tiempos
- **SHOULD** generar reportes de test results en formato TRX
- **SHOULD** usar clases base para categorización automática de tests

### MUST NOT (Prohibido)

- **MUST NOT** commitear código sin tests
- **MUST NOT** saltarse quality gates manualmente
- **MUST NOT** tests con sleep/delays fijos (usar polling)

---

## Referencias

- [GitHub Actions .NET](https://docs.github.com/en/actions/automating-builds-and-tests/building-and-testing-net)
- [SonarQube Quality Gates](https://docs.sonarqube.org/latest/user-guide/quality-gates/)
- [xUnit Parallelism](https://xunit.net/docs/running-tests-in-parallel)
- [Pirámide de Testing](./testing-pyramid.md)
- [Cobertura de Código](./test-coverage.md)
- [CI/CD Pipelines y Build](../operabilidad/ci-pipeline.md)
