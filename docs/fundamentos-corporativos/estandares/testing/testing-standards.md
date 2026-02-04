---
id: testing-standards
sidebar_position: 2
title: Estándares de Testing
description: Estándares consolidados de testing con Testing Pyramid, unit tests, integration tests y contract testing
---

# Estándar Técnico — Estándares de Testing

## 1. Propósito

Garantizar código confiable mediante Testing Pyramid: unit tests (70%), integration tests (20%), contract tests (10%).

## 2. Alcance

**Aplica a:**

- Aplicaciones backend (.NET 8+)
- APIs REST
- Microservicios
- Servicios de mensajería (Apache Kafka)
- Librerías compartidas
- Integraciones entre servicios

**No aplica a:**

- Scripts one-off sin lógica de negocio
- Configuración de infraestructura (IaC tiene otros mecanismos)
- Prototipos/spikes técnicos sin deployment

## 3. Tecnologías Aprobadas

| Componente           | Tecnología            | Versión mínima | Observaciones               |
| -------------------- | --------------------- | -------------- | --------------------------- |
| **Framework**        | xUnit                 | 2.6+           | Testing .NET                |
| **Mocking**          | Moq                   | 4.20+          | Mocks/stubs                 |
| **Assertions**       | FluentAssertions      | 6.12+          | Expresividad                |
| **Coverage**         | Coverlet              | 6.0+           | Cobertura de código         |
| **Integration**      | WebApplicationFactory | 8.0+           | API testing                 |
| **Containers**       | Testcontainers        | 3.7+           | PostgreSQL, Redis, Kafka    |
| **Contract Testing** | PactNet               | 5.0+           | Consumer-provider contracts |
| **Broker**           | Pact Broker           | 2.100+         | Contract repository         |
| **Análisis**         | SonarQube             | 10.0+          | Calidad y cobertura         |

> El uso de tecnologías no listadas requiere aprobación de Arquitectura.

## 4. Testing Pyramid

```
         /\
        /E2E\ 10% - UI tests (Playwright, Selenium)
       /------\
      /  INT   \ 20% - API/DB integration tests
     /----------\
    /    UNIT    \ 70% - Unit tests (lógica de negocio)
   /--------------\
```

| Tipo                  | % Cobertura     | Velocidad    | Fragilidad | Costo | Scope                       |
| --------------------- | --------------- | ------------ | ---------- | ----- | --------------------------- |
| **Unit Tests**        | 70%             | <500ms suite | Baja       | Bajo  | Función/método aislado      |
| **Integration Tests** | 20%             | <5min suite  | Media      | Medio | API + BD real               |
| **Contract Tests**    | 10% (adicional) | <1min suite  | Baja       | Bajo  | Consumer-provider contracts |
| **E2E Tests**         | 10%             | <30min suite | Alta       | Alto  | User journey completo       |

## 5. Requisitos Obligatorios 🔴

### Testing Strategy

- [ ] Implementar Testing Pyramid (70% unit, 20% integration, 10% E2E)
- [ ] Code coverage >80% en Services/Repositories (unit tests)
- [ ] Contract testing para comunicación entre microservicios
- [ ] Integración en CI/CD (tests fallan → build falla)
- [ ] Ejecución paralela habilitada cuando sea posible

### Unit Tests

- [ ] xUnit 2.6+ en todos los proyectos
- [ ] Patrón AAA (Arrange-Act-Assert) obligatorio
- [ ] Mocks con Moq 4.20+ (NO dependencias reales)
- [ ] Tests aislados (NO compartir estado entre tests)
- [ ] Naming: `MethodName_Scenario_ExpectedResult`
- [ ] Ejecución <500ms para suite completa
- [ ] FluentAssertions para legibilidad

### Integration Tests

- [ ] WebApplicationFactory para APIs .NET
- [ ] Testcontainers para dependencias externas (PostgreSQL, Redis, Kafka)
- [ ] BD real (NO in-memory DB)
- [ ] IClassFixture para compartir setup (performance)
- [ ] Cleanup después de cada test (transaction rollback o BD limpia)
- [ ] Ejecución <5min para suite completa
- [ ] Tests ejecutables localmente SIN infraestructura externa

### Contract Testing

- [ ] PactNet 5.0+ para microservicios
- [ ] Contratos publicados en Pact Broker
- [ ] Verificación de contratos en CI/CD
- [ ] Can-I-Deploy check antes de producción

---

## 6. Ejemplos de Configuración

### 6.1. Unit Test con Moq

```csharp
public class OrderServiceTests
{
    private readonly Mock<IOrderRepository> _mockRepository;
    private readonly OrderService _sut;

    public OrderServiceTests()
    {
        _mockRepository = new Mock<IOrderRepository>();
        _sut = new OrderService(_mockRepository.Object);
    }

    [Fact]
    public async Task CreateOrderAsync_ValidRequest_ReturnsOrderId()
    {
        // Arrange
        var orderId = Guid.NewGuid();
        var request = new CreateOrderRequest { UserId = "user-123", Total = 100.50m };

        _mockRepository
            .Setup(r => r.AddAsync(It.IsAny<Order>(), default))
            .ReturnsAsync(orderId);

        // Act
        var result = await _sut.CreateOrderAsync(request, default);

        // Assert
        result.Should().Be(orderId);
        _mockRepository.Verify(r => r.AddAsync(It.IsAny<Order>(), default), Times.Once);
    }
}
```

### 6.2. Integration Test con Testcontainers

```csharp
public class IntegrationTestFactory : WebApplicationFactory<Program>, IAsyncLifetime
{
    private readonly PostgreSqlContainer _dbContainer = new PostgreSqlBuilder()
        .WithImage("postgres:16-alpine")
        .Build();

    protected override void ConfigureWebHost(IWebHostBuilder builder)
    {
        builder.ConfigureServices(services =>
        {
            services.RemoveAll<DbContextOptions<ApplicationDbContext>>();
            services.AddDbContext<ApplicationDbContext>(options =>
                options.UseNpgsql(_dbContainer.GetConnectionString()));
        });
    }

    public async Task InitializeAsync() => await _dbContainer.StartAsync();
    public new async Task DisposeAsync() => await _dbContainer.DisposeAsync();
}

public class OrdersControllerTests : IClassFixture<IntegrationTestFactory>
{
    private readonly HttpClient _client;

    public OrdersControllerTests(IntegrationTestFactory factory)
    {
        _client = factory.CreateClient();
    }

    [Fact]
    public async Task POST_Orders_ValidRequest_ReturnsCreated()
    {
        var request = new CreateOrderRequest { UserId = "user-123" };
        var response = await _client.PostAsJsonAsync("/api/v1/orders", request);
        response.StatusCode.Should().Be(HttpStatusCode.Created);
    }
}
```

### 6.3. Contract Test con PactNet

```csharp
public class PaymentServiceConsumerTests : IDisposable
{
    private readonly IPactBuilderV4 _pactBuilder;

    public PaymentServiceConsumerTests()
    {
        _pactBuilder = Pact.V4("order-api", "payment-api", new PactConfig { PactDir = "../pacts" })
            .WithHttpInteractions();
    }

    [Fact]
    public async Task CreatePayment_ValidRequest_ReturnsCreated()
    {
        _pactBuilder
            .UponReceiving("a request to create payment")
                .WithRequest(HttpMethod.Post, "/api/v1/payments")
                .WithJsonBody(new { orderId = Match.Type("ord-123"), amount = Match.Decimal(100.50m) })
            .WillRespond()
                .WithStatus(201)
                .WithJsonBody(new { paymentId = Match.Type("pay-456"), status = "pending" });

        await _pactBuilder.VerifyAsync(async ctx =>
        {
            var client = new HttpClient { BaseAddress = ctx.MockServerUri };
            var response = await client.PostAsJsonAsync("/api/v1/payments", new { orderId = "ord-123", amount = 100.50m });
            response.StatusCode.Should().Be(HttpStatusCode.Created);
        });
    }

    public void Dispose() { } // Pact file generado aquí
}
```

---

## 7. CI/CD Integration — All Tests

```yaml
# .github/workflows/test-pipeline.yml
name: Test Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-dotnet@v4
        with:
          dotnet-version: "8.0"

      - name: Run Unit Tests
        run: dotnet test --filter "Category=Unit" --logger "trx"

      - name: Check duration (<500ms)
        run: |
          duration=$(grep -oP 'duration="\K[^"]+' TestResults/*.trx | awk '{sum+=$1} END {print sum}')
          if (( $(echo "$duration > 500" | bc -l) )); then
            echo "Unit tests took ${duration}ms (target: <500ms)"
            exit 1
          fi

      - name: Coverage Report
        run: dotnet test --filter "Category=Unit" /p:CollectCoverage=true /p:CoverletOutputFormat=opencover

      - name: Upload to Codecov
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage.opencover.xml

  integration-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-dotnet@v4

      - name: Run Integration Tests
        run: dotnet test --filter "Category=Integration"
        timeout-minutes: 10

  contract-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Run Consumer Tests
        run: dotnet test Tests/ConsumerTests.csproj

      - name: Publish Contracts
        if: github.ref == 'refs/heads/main'
        run: |
          docker run --rm -v $(pwd)/pacts:/pacts \
            pactfoundation/pact-cli:latest \
            publish /pacts \
            --consumer-app-version=${{ github.sha }} \
            --broker-base-url=${{ secrets.PACT_BROKER_URL }} \
            --broker-token=${{ secrets.PACT_BROKER_TOKEN }}

  sonarqube:
    runs-on: ubuntu-latest
    needs: [unit-tests, integration-tests]
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: SonarQube Scan
        uses: sonarsource/sonarqube-scan-action@master
        env:
          SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
          SONAR_HOST_URL: ${{ secrets.SONAR_HOST_URL }}

      - name: Quality Gate
        run: |
          sleep 10
          curl -u "${{ secrets.SONAR_TOKEN }}:" \
            "${{ secrets.SONAR_HOST_URL }}/api/qualitygates/project_status?projectKey=payment-service" \
            | jq -e '.projectStatus.status == "OK"'
```

## 10. Métricas de Cumplimiento

| Métrica                       | Target                     | Verificación       |
| ----------------------------- | -------------------------- | ------------------ |
| **Unit test coverage**        | >80% Services/Repositories | Coverlet/SonarQube |
| **Integration test coverage** | 20% endpoints críticos     | Manual count       |
| **Contract test coverage**    | 100% inter-service APIs    | Pact Broker        |
| **Unit test duration**        | <500ms suite completa      | CI logs            |
| **Integration test duration** | <5min suite completa       | CI logs            |
| **Contract test duration**    | <1min suite completa       | CI logs            |
| **Test success rate**         | >95% (flaky <5%)           | CI history         |
| **Tests en CI/CD**            | 100% ejecutados            | Pipeline status    |

## 11. Validación de Cumplimiento

### Checklist

- [ ] Tests unitarios cubren >80% de Services/Repositories
- [ ] Suite de unit tests ejecuta en <500ms
- [ ] Integration tests usan Testcontainers (NO in-memory DB)
- [ ] Contract tests publicados en Pact Broker
- [ ] Can-I-Deploy check antes de producción
- [ ] CI/CD bloquea merge si tests fallan
- [ ] Tests ejecutables localmente sin infraestructura externa
- [ ] Patrón AAA aplicado en todos los tests

### Comandos de Validación

```bash
# Unit tests
dotnet test --filter "Category=Unit"

# Coverage report
dotnet test /p:CollectCoverage=true /p:CoverletOutputFormat=opencover
grep -A 5 "line rate" coverage.opencover.xml

# Integration tests
dotnet test --filter "Category=Integration"

# Contract tests
dotnet test Tests/ConsumerTests.csproj
dotnet test Tests/ProviderTests.csproj

# Verificar contratos en Broker
curl -u pact:pact123 https://pact-broker.company.com/pacts

# Can-I-Deploy check
docker run --rm pactfoundation/pact-cli:latest \
  can-i-deploy \
  --pacticipant payment-api \
  --version 1.2.3 \
  --to-environment production \
  --broker-base-url https://pact-broker.company.com
```

## 12. Prohibiciones Generales

- ❌ Mayoría de tests en E2E (pirámide invertida)
- ❌ Unit tests con BD/HTTP real (usar mocks)
- ❌ In-memory DB (SQLite) para integration tests
- ❌ Tests interdependientes (orden de ejecución)
- ❌ Tests >30 segundos sin justificación
- ❌ Coverage <80% en Services/Repositories
- ❌ Tests flaky (>5% tasa de fallo intermitente)
- ❌ Hardcoded secrets en tests
- ❌ Tests sin cleanup (contamina siguientes tests)
- ❌ Deploy a producción sin verificación de contratos

## 13. Referencias

**Testing Strategy:**

- [Mike Cohn — Test Pyramid](https://www.mountaingoatsoftware.com/blog/the-forgotten-layer-of-the-test-automation-pyramid)
- [Martin Fowler — Test Pyramid](https://martinfowler.com/articles/practical-test-pyramid.html)
- [Martin Fowler — Consumer-Driven Contracts](https://martinfowler.com/articles/consumerDrivenContracts.html)

**Frameworks:**

- [xUnit Documentation](https://xunit.net/)
- [Moq Quickstart](https://github.com/moq/moq4)
- [FluentAssertions](https://fluentassertions.com/)
- [Testcontainers .NET](https://dotnet.testcontainers.org/)
- [Pact.io Documentation](https://docs.pact.io/)
- [PactNet GitHub](https://github.com/pact-foundation/pact-net)

**Microsoft:**

- [Testing in ASP.NET Core](https://learn.microsoft.com/aspnet/core/test/)
- [Integration tests with WebApplicationFactory](https://learn.microsoft.com/aspnet/core/test/integration-tests)
- [Unit testing best practices](https://learn.microsoft.com/dotnet/core/testing/unit-testing-best-practices)
