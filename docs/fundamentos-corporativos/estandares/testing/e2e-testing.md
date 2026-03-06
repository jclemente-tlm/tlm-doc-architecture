---
id: e2e-testing
sidebar_position: 7
title: Pruebas End-to-End
description: Estándares para E2E testing con Playwright y smoke tests post-deploy
tags: [testing, e2e, playwright, smoke-tests, restsharp]
---

# Pruebas End-to-End

## Contexto

Este estándar define los **patrones para pruebas End-to-End**: validación de user journeys completos desde la perspectiva del usuario, incluyendo UI, APIs, databases y servicios externos.

---

## Stack Tecnológico

| Componente      | Tecnología       | Versión | Uso                     |
| --------------- | ---------------- | ------- | ----------------------- |
| **E2E Browser** | Playwright       | 1.41+   | Browser automation      |
| **API E2E**     | RestSharp        | 110.2+  | API testing sin UI      |
| **Assertions**  | FluentAssertions | 6.12+   | Assertions expresivas   |
| **CI/CD**       | GitHub Actions   | Latest  | Smoke tests post-deploy |

---

## Pruebas End-to-End

### ¿Qué es E2E Testing?

Tests que validan user journeys completos desde perspectiva del usuario, incluyendo UI, APIs, databases y servicios externos. Simula interacción real del usuario.

**Propósito:** Validar que el sistema completo funciona correctamente para casos de uso críticos.

**Estrategia:**

- **Smoke Tests**: Subset crítico de E2E post-deploy (5–10 tests, < 5 min)
- **Full E2E Suite**: Tests comprehensivos pre-release (20–50 tests)
- **User Journeys**: Flujos reales de negocio (login → order → payment → confirmation)

**Beneficios:**
✅ Alta confianza en releases
✅ Detecta problemas de integración sistémica
✅ Valida UX real
✅ Smoke tests verifican producción post-deploy

### Playwright: Browser E2E Tests

```csharp
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
            Headless = true,
            SlowMo = 50
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

        // 8. Screenshot para documentación
        await _page.ScreenshotAsync(new PageScreenshotOptions { Path = "order-confirmation.png" });
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

        await _page.FillAsync("input[name='cardNumber']", "4111111111111111");
        await _page.ClickAsync("button:has-text('Pay Now')");

        // Assert
        var errorMessage = await _page.Locator(".error-message").TextContentAsync();
        errorMessage.Should().Contain("Payment declined");

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
            if (i > 0) await _page.ClickAsync("button:has-text('Add Item')");
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
[Collection("E2E")]
[Trait("Category", "E2E")]
public class ApiOrderJourneyTests
{
    private readonly RestClient _client;
    private readonly string _baseUrl = "https://staging-api.talma.com";

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
        var authToken = loginResponse.Data.AccessToken;

        // 2. Create order
        var createOrderRequest = new RestRequest("/api/orders", Method.Post);
        createOrderRequest.AddHeader("Authorization", $"Bearer {authToken}");
        createOrderRequest.AddJsonBody(new
        {
            customerId = "CUST-123",
            items = new[] { new { sku = "SKU-001", quantity = 2, unitPrice = 100.00 } },
            paymentMethod = "credit_card"
        });
        var createOrderResponse = await _client.ExecuteAsync<OrderResponse>(createOrderRequest);
        createOrderResponse.StatusCode.Should().Be(HttpStatusCode.Created);
        var orderId = createOrderResponse.Data.OrderId;

        // 3. Get order details
        var getOrderRequest = new RestRequest($"/api/orders/{orderId}", Method.Get);
        getOrderRequest.AddHeader("Authorization", $"Bearer {authToken}");
        var getOrderResponse = await _client.ExecuteAsync<OrderResponse>(getOrderRequest);
        getOrderResponse.IsSuccessful.Should().BeTrue();
        getOrderResponse.Data.Status.Should().Be("Pending");

        // 4. Process payment
        var paymentRequest = new RestRequest($"/api/orders/{orderId}/payment", Method.Post);
        paymentRequest.AddHeader("Authorization", $"Bearer {authToken}");
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
      - uses: actions/checkout@v3

      - uses: actions/setup-dotnet@v3
        with:
          dotnet-version: "8.0.x"

      - name: Install Playwright
        run: |
          dotnet tool install -g Microsoft.Playwright.CLI
          playwright install chromium

      - name: Run smoke tests
        env:
          BASE_URL: ${{ github.event.deployment_status.environment_url }}
        run: dotnet test --filter "Category=Smoke" tests/OrderService.E2ETests

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

## Monitoreo y Observabilidad

Los E2E tests generan artefactos en CI/CD para diagnóstico:

- **Screenshots** en failures para debugging visual
- **Video recording** de tests fallidos (configurar en Playwright)
- **Reporte de duración** para detectar degradación de performance

---

## Requisitos Técnicos

### MUST (Obligatorio)

- **MUST** smoke tests post-deploy en staging y producción
- **MUST** smoke tests ejecutarse en < 5 minutos
- **MUST** tests aislados (setup/cleanup propio, sin estado compartido)
- **MUST** screenshots en failures para debugging
- **MUST** E2E tests solo en critical user journeys (< 10 tests críticos)

### SHOULD (Fuertemente recomendado)

- **SHOULD** Playwright para E2E con UI
- **SHOULD** parallel execution de E2E tests
- **SHOULD** video recording de failures
- **SHOULD** API E2E tests para flows sin UI

### MUST NOT (Prohibido)

- **MUST NOT** substituir unit/integration tests con E2E tests
- **MUST NOT** E2E tests con `sleep`/waits fijos (usar `WaitForSelector`)
- **MUST NOT** hardcodear URLs (usar environment variables)
- **MUST NOT** compartir estado entre E2E tests

---

## Referencias

- [Playwright .NET](https://playwright.dev/dotnet/)
- [RestSharp](https://restsharp.dev/)
- [Contract Testing](./contract-testing.md)
- [Pirámide de Testing](./testing-pyramid.md)
- [Automatización de Tests](./test-automation.md)
