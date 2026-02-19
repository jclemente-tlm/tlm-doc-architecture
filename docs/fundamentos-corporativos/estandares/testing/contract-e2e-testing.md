---
id: contract-e2e-testing
sidebar_position: 3
title: Contract & E2E Testing
description: Estándares para contract testing con Pact y E2E testing con Playwright
---

# Contract & E2E Testing

## Contexto

Este estándar consolida **2 conceptos relacionados** con testing de contratos entre servicios (contract) y flujos completos end-to-end (E2E). Define consumer-driven contracts y testing de user journeys críticos.

**Conceptos incluidos:**

- **Contract Testing** → Validar contratos entre consumer/provider (Pact)
- **E2E Testing** → Validar flujos completos de usuario (Playwright, smoke tests)

---

## Stack Tecnológico

| Componente           | Tecnología       | Versión | Uso                                    |
| -------------------- | ---------------- | ------- | -------------------------------------- |
| **Contract Testing** | PactNet          | 4.6+    | Consumer-driven contract testing       |
| **Pact Broker**      | Pactflow         | SaaS    | Almacenamiento y verificación de pacts |
| **E2E Framework**    | Playwright       | 1.41+   | Browser automation                     |
| **API E2E**          | RestSharp        | 110.2+  | API testing sin UI                     |
| **Assertions**       | FluentAssertions | 6.12+   | Assertions expresivas                  |
| **CI/CD**            | GitHub Actions   | Latest  | Automatización de tests                |

---

## Conceptos Fundamentales

Este estándar cubre **2 tipos** de tests avanzados:

### Índice de Conceptos

1. **Contract Testing**: Validar API contracts sin integration testing completo
2. **E2E Testing**: Validar user journeys críticos end-to-end

### Comparación Contract vs E2E

| Aspecto             | Contract Tests                  | E2E Tests                            |
| ------------------- | ------------------------------- | ------------------------------------ |
| **Alcance**         | API contract (request/response) | Usuario completo (UI → API → DB)     |
| **Velocidad**       | Segundos                        | Minutos                              |
| **Infraestructura** | Mínima (mock provider)          | Completa (browsers, services)        |
| **Mantenimiento**   | Bajo (solo contract)            | Alto (UI changes, timing)            |
| **Propósito**       | Prevenir breaking changes       | Validar flows críticos               |
| **Frecuencia**      | Cada commit                     | Pre-release, smoke tests post-deploy |

---

## 1. Contract Testing

### ¿Qué es Contract Testing?

Consumer-Driven Contract Testing valida que API provider cumple el contrato esperado por consumers, sin necesidad de integration testing end-to-end. Consumer define expectations (pact), provider las verifica.

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

        // Act
        await _pact.VerifyAsync(async ctx =>
        {
            var client = new HttpClient { BaseAddress = ctx.MockServerUri };
            var request = new
            {
                amount = 100.00m,
                customerId = "CUST-123",
                paymentMethod = "credit_card"
            };

            var response = await client.PostAsJsonAsync("/api/payments", request);

            // Assert
            response.StatusCode.Should().Be(HttpStatusCode.OK);

            var result = await response.Content.ReadFromJsonAsync<PaymentResponse>();
            result.Should().NotBeNull();
            result.Success.Should().BeTrue();
            result.TransactionId.Should().NotBeNullOrEmpty();
            result.ProcessedAt.Should().BeAfter(DateTime.UtcNow.AddMinutes(-1));
        });
    }

    [Fact]
    public async Task ProcessPayment_WithInsufficientFunds_ShouldReturn400WithError()
    {
        // Arrange
        _pact
            .UponReceiving("A request to process payment with insufficient funds")
                .WithRequest(HttpMethod.Post, "/api/payments")
                .WithHeader("Content-Type", "application/json")
                .WithJsonBody(new
                {
                    amount = Match.Decimal(10000.00m),
                    customerId = Match.Type("CUST-POOR"),
                    paymentMethod = Match.Type("credit_card")
                })
            .WillRespond()
                .WithStatus(400)
                .WithHeader("Content-Type", "application/json")
                .WithJsonBody(new
                {
                    success = false,
                    errorCode = "INSUFFICIENT_FUNDS",
                    errorMessage = Match.Type("Insufficient funds available")
                });

        // Act
        await _pact.VerifyAsync(async ctx =>
        {
            var client = new HttpClient { BaseAddress = ctx.MockServerUri };
            var request = new
            {
                amount = 10000.00m,
                customerId = "CUST-POOR",
                paymentMethod = "credit_card"
            };

            var response = await client.PostAsJsonAsync("/api/payments", request);

            // Assert
            response.StatusCode.Should().Be(HttpStatusCode.BadRequest);

            var result = await response.Content.ReadFromJsonAsync<PaymentResponse>();
            result.Should().NotBeNull();
            result.Success.Should().BeFalse();
            result.ErrorCode.Should().Be("INSUFFICIENT_FUNDS");
        });
    }

    public void Dispose()
    {
        // Pact file generado en pacts/OrderService-PaymentService.json
    }
}
```

### Provider Verification

```csharp
// tests/PaymentService.Tests/Contracts/PaymentServiceProviderTests.cs
using PactNet.Verifier;
using Xunit;
using Microsoft.AspNetCore.Hosting;
using Microsoft.AspNetCore.TestHost;

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
        // Arrange
        var config = new PactVerifierConfig
        {
            Verbose = true,
            ProviderVersion = "1.2.3",
            PublishVerificationResults = true
        };

        // Act & Assert
        new PactVerifier(config)
            .ServiceProvider("PaymentService", _testServer.BaseAddress)
            .WithFileSource(new FileInfo("../../../pacts/OrderService-PaymentService.json"))
            .WithProviderStateUrl(new Uri(_testServer.BaseAddress, "/provider-states"))
            .Verify();
    }

    public void Dispose()
    {
        _testServer?.Dispose();
    }
}

// src/PaymentService.Api/Controllers/ProviderStatesController.cs
// Controller para setup de test data según provider state
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
                _context.Customers.Add(new Customer
                {
                    Id = "CUST-123",
                    Balance = 10000m
                });
                await _context.SaveChangesAsync();
                break;

            case "A customer with insufficient funds exists":
                _context.Customers.Add(new Customer
                {
                    Id = "CUST-POOR",
                    Balance = 10m
                });
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
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Setup .NET
        uses: actions/setup-dotnet@v3
        with:
          dotnet-version: "8.0.x"

      - name: Run consumer contract tests
        run: |
          dotnet test \
            --filter "Category=Contract" \
            tests/OrderService.Tests

      - name: Publish pacts to Pact Broker
        env:
          PACT_BROKER_BASE_URL: ${{ secrets.PACT_BROKER_BASE_URL }}
          PACT_BROKER_TOKEN: ${{ secrets.PACT_BROKER_TOKEN }}
        run: |
          dotnet tool install -g pact-cli

          pact-broker publish \
            tests/OrderService.Tests/pacts \
            --consumer-app-version ${{ github.sha }} \
            --branch ${{ github.ref_name }} \
            --broker-base-url $PACT_BROKER_BASE_URL \
            --broker-token $PACT_BROKER_TOKEN

  provider-tests:
    name: Provider Verification
    runs-on: ubuntu-latest
    needs: consumer-tests

    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Setup .NET
        uses: actions/setup-dotnet@v3
        with:
          dotnet-version: "8.0.x"

      - name: Verify provider against pacts
        env:
          PACT_BROKER_BASE_URL: ${{ secrets.PACT_BROKER_BASE_URL }}
          PACT_BROKER_TOKEN: ${{ secrets.PACT_BROKER_TOKEN }}
        run: |
          dotnet test \
            --filter "Category=ProviderContract" \
            tests/PaymentService.Tests

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

## 2. E2E Testing

### ¿Qué es E2E Testing?

Tests que validan user journeys completos desde perspectiva del usuario, incluyendo UI, APIs, databases y servicios externos. Simula interacción real del usuario.

**Propósito:** Validar que sistema completo funciona correctamente para casos de uso críticos.

**Estrategia:**

- **Smoke Tests**: Subset crítico de E2E ejecutado post-deploy (5-10 tests)
- **Full E2E Suite**: Tests comprehensivos pre-release (20-50 tests)
- **User Journeys**: Flujos reales de negocio (login → order → payment → confirmation)

**Beneficios:**
✅ Alta confianza en releases
✅ Detecta problemas de integración sistémica
✅ Valida UX real
✅ Smoke tests post-deploy

### Playwright: Browser E2E Tests

```csharp
// tests/OrderService.E2ETests/OrderService.E2ETests.csproj
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net8.0</TargetFramework>
  </PropertyGroup>

  <ItemGroup>
    <PackageReference Include="Microsoft.Playwright" Version="1.41.0" />
    <PackageReference Include="xunit" Version="2.6.6" />
    <PackageReference Include="FluentAssertions" Version="6.12.0" />
  </ItemGroup>
</Project>

// tests/OrderService.E2ETests/OrderJourneyTests.cs
using Microsoft.Playwright;
using Xunit;
using FluentAssertions;

[Collection("E2E")]
[Trait("Category", "E2E")]
public class OrderJourneyTests : IAsyncLifetime
{
    private IPlaywright _playwright;
    private IBrowser _browser;
    private IPage _page;
    private readonly string _baseUrl = "https://staging.talma.com";

    public async Task InitializeAsync()
    {
        _playwright = await Playwright.CreateAsync();
        _browser = await _playwright.Chromium.LaunchAsync(new BrowserTypeLaunchOptions
        {
            Headless = true, // false para debugging
            SlowMo = 50 // Slow down para observar acciones
        });
        _page = await _browser.NewPageAsync();
    }

    [Fact]
    public async Task CompleteOrderFlow_HappyPath_ShouldCreateOrderSuccessfully()
    {
        // 1. Login
        await _page.GotoAsync($"{_baseUrl}/login");
        await _page.FillAsync("input[name='email']", "test@talma.pe");
        await _page.FillAsync("input[name='password']", "Test123!");
        await _page.ClickAsync("button[type='submit']");

        await _page.WaitForURLAsync("**/dashboard");

        // 2. Navigate to create order
        await _page.ClickAsync("text=Create Order");
        await _page.WaitForURLAsync("**/orders/new");

        // 3. Fill order form
        await _page.SelectOptionAsync("select[name='customerId']", "CUST-123");

        await _page.ClickAsync("button:has-text('Add Item')");
        await _page.FillAsync("input[name='items[0].sku']", "SKU-001");
        await _page.FillAsync("input[name='items[0].quantity']", "2");

        // 4. Verify calculated total
        var totalElement = await _page.Locator(".order-total").TextContentAsync();
        totalElement.Should().Contain("236.00"); // 200 + 18% tax

        // 5. Submit order
        await _page.ClickAsync("button:has-text('Submit Order')");

        // 6. Payment step
        await _page.WaitForURLAsync("**/payment");
        await _page.FillAsync("input[name='cardNumber']", "4532123456789010");
        await _page.FillAsync("input[name='cvv']", "123");
        await _page.SelectOptionAsync("select[name='expiryMonth']", "12");
        await _page.SelectOptionAsync("select[name='expiryYear']", "2028");

        await _page.ClickAsync("button:has-text('Pay Now')");

        // 7. Verify success
        await _page.WaitForURLAsync("**/orders/*/confirmation");

        var successMessage = await _page.Locator(".success-message").TextContentAsync();
        successMessage.Should().Contain("Order created successfully");

        var orderNumber = await _page.Locator(".order-number").TextContentAsync();
        orderNumber.Should().MatchRegex(@"#\d+");

        // 8. Screenshot for documentation
        await _page.ScreenshotAsync(new PageScreenshotOptions
        {
            Path = "order-confirmation.png"
        });
    }

    [Fact]
    public async Task CreateOrder_WithInvalidPayment_ShouldShowError()
    {
        // Arrange - Login y navigate
        await LoginAsync("test@talma.pe", "Test123!");
        await NavigateToCreateOrderAsync();

        // Act - Fill order con tarjeta inválida
        await FillOrderFormAsync("CUST-123", new[] { ("SKU-001", 1) });
        await _page.ClickAsync("button:has-text('Submit Order')");

        await _page.FillAsync("input[name='cardNumber']", "4111111111111111"); // Tarjeta de prueba que falla
        await _page.ClickAsync("button:has-text('Pay Now')");

        // Assert
        var errorMessage = await _page.Locator(".error-message").TextContentAsync();
        errorMessage.Should().Contain("Payment declined");

        // Verify order NO fue creado
        await _page.GotoAsync($"{_baseUrl}/orders");
        var noOrdersMessage = await _page.Locator(".no-orders").IsVisibleAsync();
        noOrdersMessage.Should().BeTrue();
    }

    // Helper methods
    private async Task LoginAsync(string email, string password)
    {
        await _page.GotoAsync($"{_baseUrl}/login");
        await _page.FillAsync("input[name='email']", email);
        await _page.FillAsync("input[name='password']", password);
        await _page.ClickAsync("button[type='submit']");
        await _page.WaitForURLAsync("**/dashboard");
    }

    private async Task NavigateToCreateOrderAsync()
    {
        await _page.ClickAsync("text=Create Order");
        await _page.WaitForURLAsync("**/orders/new");
    }

    private async Task FillOrderFormAsync(string customerId, (string sku, int quantity)[] items)
    {
        await _page.SelectOptionAsync("select[name='customerId']", customerId);

        for (int i = 0; i < items.Length; i++)
        {
            if (i > 0)
                await _page.ClickAsync("button:has-text('Add Item')");

            await _page.FillAsync($"input[name='items[{i}].sku']", items[i].sku);
            await _page.FillAsync($"input[name='items[{i}].quantity']", items[i].quantity.ToString());
        }
    }

    public async Task DisposeAsync()
    {
        await _page?.CloseAsync();
        await _browser?.CloseAsync();
        _playwright?.Dispose();
    }
}
```

### API E2E Tests (Sin UI)

```csharp
// tests/OrderService.E2ETests/ApiOrderJourneyTests.cs
using RestSharp;
using FluentAssertions;

[Collection("E2E")]
[Trait("Category", "E2E")]
public class ApiOrderJourneyTests
{
    private readonly RestClient _client;
    private readonly string _baseUrl = "https://staging-api.talma.com";
    private string _authToken;

    public ApiOrderJourneyTests()
    {
        _client = new RestClient(_baseUrl);
    }

    [Fact]
    public async Task CompleteOrderFlow_ViaAPI_ShouldSucceed()
    {
        // 1. Authenticate
        var loginRequest = new RestRequest("/api/auth/login", Method.Post);
        loginRequest.AddJsonBody(new { email = "test@talma.pe", password = "Test123!" });

        var loginResponse = await _client.ExecuteAsync<AuthResponse>(loginRequest);
        loginResponse.IsSuccessful.Should().BeTrue();
        _authToken = loginResponse.Data.AccessToken;

        // 2. Create order
        var createOrderRequest = new RestRequest("/api/orders", Method.Post);
        createOrderRequest.AddHeader("Authorization", $"Bearer {_authToken}");
        createOrderRequest.AddJsonBody(new
        {
            customerId = "CUST-123",
            items = new[]
            {
                new { sku = "SKU-001", quantity = 2, unitPrice = 100.00 }
            },
            paymentMethod = "credit_card"
        });

        var createOrderResponse = await _client.ExecuteAsync<OrderResponse>(createOrderRequest);
        createOrderResponse.StatusCode.Should().Be(HttpStatusCode.Created);
        var orderId = createOrderResponse.Data.OrderId;

        // 3. Get order details
        var getOrderRequest = new RestRequest($"/api/orders/{orderId}", Method.Get);
        getOrderRequest.AddHeader("Authorization", $"Bearer {_authToken}");

        var getOrderResponse = await _client.ExecuteAsync<OrderResponse>(getOrderRequest);
        getOrderResponse.IsSuccessful.Should().BeTrue();
        getOrderResponse.Data.Status.Should().Be("Pending");

        // 4. Process payment
        var paymentRequest = new RestRequest($"/api/orders/{orderId}/payment", Method.Post);
        paymentRequest.AddHeader("Authorization", $"Bearer {_authToken}");
        paymentRequest.AddJsonBody(new
        {
            cardNumber = "4532123456789010",
            cvv = "123",
            expiryMonth = 12,
            expiryYear = 2028
        });

        var paymentResponse = await _client.ExecuteAsync(paymentRequest);
        paymentResponse.StatusCode.Should().Be(HttpStatusCode.OK);

        // 5. Verify order status updated
        await Task.Delay(2000); // Wait for async processing

        var finalOrderResponse = await _client.ExecuteAsync<OrderResponse>(getOrderRequest);
        finalOrderResponse.Data.Status.Should().Be("Paid");
    }
}
```

### Smoke Tests Post-Deploy

```yaml
# .github/workflows/smoke-tests.yml
name: Smoke Tests

on:
  deployment_status:

jobs:
  smoke-tests:
    name: Post-Deploy Smoke Tests
    runs-on: ubuntu-latest
    if: github.event.deployment_status.state == 'success'

    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Setup .NET
        uses: actions/setup-dotnet@v3
        with:
          dotnet-version: "8.0.x"

      - name: Install Playwright
        run: |
          dotnet tool install -g Microsoft.Playwright.CLI
          playwright install chromium

      - name: Run smoke tests
        env:
          BASE_URL: ${{ github.event.deployment_status.environment_url }}
        run: |
          dotnet test \
            --filter "Category=Smoke" \
            tests/OrderService.E2ETests

      - name: Notify on failure
        if: failure()
        run: |
          curl -X POST ${{ secrets.SLACK_WEBHOOK_URL }} \
            -H 'Content-Type: application/json' \
            -d '{
              "text": "🚨 Smoke tests FAILED in ${{ github.event.deployment_status.environment }}",
              "channel": "#deployments"
            }'
```

---

## Requisitos Técnicos

### MUST (Obligatorio)

**Contract Testing:**

- **MUST** definir pacts para todas las integraciones sincrónicas (HTTP)
- **MUST** verificar provider contra todos los pacts de consumers
- **MUST** usar Pact Broker para almacenar pacts centralmente
- **MUST** ejecutar can-i-deploy antes de producción
- **MUST** versionar pacts con consumer version

**E2E Testing:**

- **MUST** smoke tests post-deploy en staging/producción
- **MUST** smoke tests ejecutarse en < 5 minutos
- **MUST** tests aislados (setup/cleanup propio)
- **MUST** screenshots en failures para debugging
- **MUST** ejecutar solo en critical user journeys (< 10 tests)

### SHOULD (Fuertemente recomendado)

- **SHOULD** contract tests en CI/CD en cada PR
- **SHOULD** Playwright para E2E con UI
- **SHOULD** parallel execution de E2E tests
- **SHOULD** video recording de E2E failures
- **SHOULD** API E2E tests para flows sin UI

### MUST NOT (Prohibido)

- **MUST NOT** substituir unit/integration tests con E2E
- **MUST NOT** E2E tests con sleep/waits fijos (usar WaitForSelector)
- **MUST NOT** hardcodear URLs (usar environment variables)
- **MUST NOT** compartir estado entre E2E tests

---

## Referencias

- [Pact Documentation](https://docs.pact.io/)
- [PactNet](https://github.com/pact-foundation/pact-net)
- [Playwright .NET](https://playwright.dev/dotnet/)
- [Consumer-Driven Contracts - Martin Fowler](https://martinfowler.com/articles/consumerDrivenContracts.html)

**Relacionados:**

- [Testing Strategy](./testing-strategy.md)
- [Unit & Integration Testing](./unit-integration-testing.md)
- [REST API Design](../apis/rest-api-design.md)

---

**Última actualización**: 2026-02-19
**Responsable**: Equipo de Arquitectura
