---
id: contract-testing
sidebar_position: 6
title: Contract Testing
description: Estándares para consumer-driven contract testing con PactNet y Pact Broker
tags: [testing, contract-testing, pact, pactnet, consumer-driven]
---

# Contract Testing

## Contexto

Este estándar define los **patrones para contract testing**: validación de que el API provider cumple el contrato esperado por los consumers, sin necesidad de integration testing end-to-end.

---

## Stack Tecnológico

| Componente           | Tecnología       | Versión | Uso                                    |
| -------------------- | ---------------- | ------- | -------------------------------------- |
| **Contract Testing** | PactNet          | 4.6+    | Consumer-driven contract testing       |
| **Pact Broker**      | Pactflow         | SaaS    | Almacenamiento y verificación de pacts |
| **Assertions**       | FluentAssertions | 6.12+   | Assertions expresivas                  |
| **CI/CD**            | GitHub Actions   | Latest  | Automatización de tests                |

---

## Contract Testing

### ¿Qué es Contract Testing?

Consumer-Driven Contract Testing valida que el API provider cumple el contrato esperado por consumers, sin necesidad de integration testing end-to-end. El consumer define las expectations (pact) y el provider las verifica.

**Propósito:** Detectar breaking changes en APIs antes de deploy.

**Flujo:**

1. **Consumer**: Define expectations (pact) y genera pact file
2. **Pact Broker**: Almacena pacts centralmente
3. **Provider**: Verifica cumplir todos los pacts de consumers
4. **Can-I-Deploy**: Valida que versiones son compatibles

**Beneficios:**
✅ Detecta breaking changes temprano
✅ No requiere environment compartido
✅ Tests más rápidos que integration E2E
✅ Living documentation de APIs

### Ejemplo: Payment Service Consumer

```csharp
// tests/OrderService.Tests/Contracts/PaymentServiceConsumerTests.cs
using PactNet;
using PactNet.Matchers;
using Xunit;
using FluentAssertions;

public class PaymentServiceConsumerTests : IDisposable
{
    private readonly IPactBuilderV3 _pact;
    private readonly int _mockServerPort = 9001;

    public PaymentServiceConsumerTests()
    {
        var config = new PactConfig
        {
            PactDir = "../../../pacts",
            LogLevel = PactLogLevel.Debug
        };

        _pact = Pact.V3("OrderService", "PaymentService", config)
            .WithHttpInteractions(_mockServerPort);
    }

    [Fact]
    public async Task ProcessPayment_WithValidRequest_ShouldReturn200WithTransactionId()
    {
        // Arrange - Define expected interaction
        _pact
            .UponReceiving("A request to process payment")
                .WithRequest(HttpMethod.Post, "/api/payments")
                .WithHeader("Content-Type", "application/json")
                .WithJsonBody(new
                {
                    amount = Match.Decimal(100.00m),
                    customerId = Match.Type("CUST-123"),
                    paymentMethod = Match.Regex("credit_card", "^(credit_card|debit_card)$")
                })
            .WillRespond()
                .WithStatus(200)
                .WithHeader("Content-Type", "application/json")
                .WithJsonBody(new
                {
                    success = true,
                    transactionId = Match.Type("TXN-ABC123"),
                    processedAt = Match.ISO8601DateTime("2026-02-19T10:00:00Z")
                });

        // Act & Assert
        await _pact.VerifyAsync(async ctx =>
        {
            var client = new HttpClient { BaseAddress = ctx.MockServerUri };
            var response = await client.PostAsJsonAsync("/api/payments", new
            {
                amount = 100.00m,
                customerId = "CUST-123",
                paymentMethod = "credit_card"
            });

            response.StatusCode.Should().Be(HttpStatusCode.OK);

            var result = await response.Content.ReadFromJsonAsync<PaymentResponse>();
            result.Success.Should().BeTrue();
            result.TransactionId.Should().NotBeNullOrEmpty();
        });
    }

    [Fact]
    public async Task ProcessPayment_WithInsufficientFunds_ShouldReturn400WithError()
    {
        // Arrange
        _pact
            .UponReceiving("A request to process payment with insufficient funds")
                .WithRequest(HttpMethod.Post, "/api/payments")
                .WithJsonBody(new
                {
                    amount = Match.Decimal(10000.00m),
                    customerId = Match.Type("CUST-POOR"),
                    paymentMethod = Match.Type("credit_card")
                })
            .WillRespond()
                .WithStatus(400)
                .WithJsonBody(new
                {
                    success = false,
                    errorCode = "INSUFFICIENT_FUNDS",
                    errorMessage = Match.Type("Insufficient funds available")
                });

        // Act & Assert
        await _pact.VerifyAsync(async ctx =>
        {
            var client = new HttpClient { BaseAddress = ctx.MockServerUri };
            var response = await client.PostAsJsonAsync("/api/payments", new
            {
                amount = 10000.00m,
                customerId = "CUST-POOR",
                paymentMethod = "credit_card"
            });

            response.StatusCode.Should().Be(HttpStatusCode.BadRequest);

            var result = await response.Content.ReadFromJsonAsync<PaymentResponse>();
            result.Success.Should().BeFalse();
            result.ErrorCode.Should().Be("INSUFFICIENT_FUNDS");
        });
    }

    public void Dispose() { }
}
```

### Provider Verification

```csharp
// tests/PaymentService.Tests/Contracts/PaymentServiceProviderTests.cs
public class PaymentServiceProviderTests : IDisposable
{
    private readonly TestServer _testServer;

    public PaymentServiceProviderTests()
    {
        _testServer = new TestServer(
            new WebHostBuilder()
                .UseStartup<Startup>()
                .UseEnvironment("Test"));
    }

    [Fact]
    public void EnsurePaymentServiceHonoursPactWithOrderService()
    {
        var config = new PactVerifierConfig
        {
            Verbose = true,
            ProviderVersion = "1.2.3",
            PublishVerificationResults = true
        };

        new PactVerifier(config)
            .ServiceProvider("PaymentService", _testServer.BaseAddress)
            .WithFileSource(new FileInfo("../../../pacts/OrderService-PaymentService.json"))
            .WithProviderStateUrl(new Uri(_testServer.BaseAddress, "/provider-states"))
            .Verify();
    }

    public void Dispose() => _testServer?.Dispose();
}

// src/PaymentService.Api/Controllers/ProviderStatesController.cs
[ApiController]
[Route("provider-states")]
public class ProviderStatesController : ControllerBase
{
    private readonly AppDbContext _context;

    [HttpPost]
    public async Task<IActionResult> SetupProviderState([FromBody] ProviderStateRequest request)
    {
        switch (request.State)
        {
            case "A customer with sufficient funds exists":
                _context.Customers.Add(new Customer { Id = "CUST-123", Balance = 10000m });
                await _context.SaveChangesAsync();
                break;

            case "A customer with insufficient funds exists":
                _context.Customers.Add(new Customer { Id = "CUST-POOR", Balance = 10m });
                await _context.SaveChangesAsync();
                break;
        }

        return Ok();
    }
}
```

### Pact Broker Integration (CI/CD)

```yaml
# .github/workflows/contract-tests.yml
name: Contract Tests

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  consumer-tests:
    name: Consumer Pact Tests
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-dotnet@v3
        with:
          dotnet-version: "8.0.x"

      - name: Run consumer contract tests
        run: dotnet test --filter "Category=Contract" tests/OrderService.Tests

      - name: Publish pacts to Pact Broker
        env:
          PACT_BROKER_BASE_URL: ${{ secrets.PACT_BROKER_BASE_URL }}
          PACT_BROKER_TOKEN: ${{ secrets.PACT_BROKER_TOKEN }}
        run: |
          dotnet tool install -g pact-cli
          pact-broker publish tests/OrderService.Tests/pacts \
            --consumer-app-version ${{ github.sha }} \
            --branch ${{ github.ref_name }} \
            --broker-base-url $PACT_BROKER_BASE_URL \
            --broker-token $PACT_BROKER_TOKEN

  provider-tests:
    name: Provider Verification
    runs-on: ubuntu-latest
    needs: consumer-tests
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-dotnet@v3
        with:
          dotnet-version: "8.0.x"

      - name: Verify provider against pacts
        env:
          PACT_BROKER_BASE_URL: ${{ secrets.PACT_BROKER_BASE_URL }}
          PACT_BROKER_TOKEN: ${{ secrets.PACT_BROKER_TOKEN }}
        run: dotnet test --filter "Category=ProviderContract" tests/PaymentService.Tests

  can-i-deploy:
    name: Can I Deploy?
    runs-on: ubuntu-latest
    needs: [consumer-tests, provider-tests]
    steps:
      - name: Check deployment compatibility
        env:
          PACT_BROKER_BASE_URL: ${{ secrets.PACT_BROKER_BASE_URL }}
          PACT_BROKER_TOKEN: ${{ secrets.PACT_BROKER_TOKEN }}
        run: |
          pact-broker can-i-deploy \
            --pacticipant OrderService \
            --version ${{ github.sha }} \
            --to-environment production \
            --broker-base-url $PACT_BROKER_BASE_URL \
            --broker-token $PACT_BROKER_TOKEN
```

---

## Monitoreo y Observabilidad

El Pact Broker provee dashboards de compatibilidad entre versiones. Monitorear:

- Estado de verificación de cada consumer-provider pair
- Historial de versiones publicadas
- Resultado de can-i-deploy por environment

---

## Requisitos Técnicos

### MUST (Obligatorio)

- **MUST** definir pacts para todas las integraciones sincrónicas (HTTP)
- **MUST** verificar provider contra todos los pacts de consumers
- **MUST** usar Pact Broker para almacenar pacts centralmente
- **MUST** ejecutar can-i-deploy antes de producción
- **MUST** versionar pacts con consumer version (commit SHA)

### SHOULD (Fuertemente recomendado)

- **SHOULD** contract tests en CI/CD en cada PR
- **SHOULD** incluir provider states para cada escenario de test
- **SHOULD** publicar resultados de verificación al Pact Broker

### MUST NOT (Prohibido)

- **MUST NOT** substituir integration tests con contract tests para lógica interna
- **MUST NOT** hardcodear URLs del Pact Broker en código fuente
- **MUST NOT** omitir can-i-deploy check antes de producción

---

## Referencias

- [Pact Documentation](https://docs.pact.io/)
- [PactNet](https://github.com/pact-foundation/pact-net)
- [Consumer-Driven Contracts - Martin Fowler](https://martinfowler.com/articles/consumerDrivenContracts.html)
- [Pruebas de Integración](./integration-testing.md)
- [Pruebas E2E](./e2e-testing.md)
- [Contratos de APIs](../apis/api-contracts.md)
