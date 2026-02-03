---
id: testing-pyramid
sidebar_position: 2
title: Testing Pyramid (Mike Cohn)
description: Estándar para estrategia de testing según Testing Pyramid de Mike Cohn, priorizando unit tests (70%) sobre integration (20%) y E2E (10%).
---

# Estándar Técnico — Testing Pyramid (Mike Cohn)

---

## 1. Propósito

Implementar estrategia de testing según **Testing Pyramid** de Mike Cohn, priorizando tests rápidos y aislados (unit tests 70%) sobre tests lentos y frágiles (E2E 10%), maximizando cobertura y velocidad de feedback.

---

## 2. Alcance

**Aplica a:**

- Aplicaciones backend (.NET, Node.js, Python)
- Aplicaciones frontend (React, Angular, Vue)
- APIs REST/GraphQL
- Microservicios
- Librerías compartidas

**No aplica a:**

- Scripts one-off sin lógica de negocio
- Configuración de infraestructura (IaC tiene otros mecanismos de validación)
- Prototipos/spikes técnicos

---

## 3. Testing Pyramid

```
        /\
       /E2E\ 10% - UI tests (Selenium, Playwright)
      /------\
     /  INT   \ 20% - API/DB integration tests
    /----------\
   /    UNIT    \ 70% - Unit tests (lógica de negocio)
  /--------------\
```

| Tipo                  | % Cobertura Target | Velocidad             | Fragilidad | Costo Mantenimiento | Scope                  |
| --------------------- | ------------------ | --------------------- | ---------- | ------------------- | ---------------------- |
| **Unit Tests**        | 70%                | <500ms suite completa | Baja       | Bajo                | Función/método aislado |
| **Integration Tests** | 20%                | <5min suite completa  | Media      | Medio               | API + BD real          |
| **E2E Tests**         | 10%                | <30min suite completa | Alta       | Alto                | User journey completo  |

---

## 4. Requisitos Obligatorios 🔴

### 4.1 Unit Tests (70% de cobertura)

- [ ] **Lógica de negocio 100% cubierta** (Services, Use Cases, Domain Models)
- [ ] Ejecución **<500ms** para suite completa
- [ ] **Mocks/stubs** para dependencias externas (BD, HTTP, filesystem)
- [ ] Tests **aislados** (NO compartir estado entre tests)
- [ ] Framework: xUnit (.NET), Jest (Node.js), pytest (Python)
- [ ] Ejecutados en **cada commit** (pre-commit hook + CI)

**Qué testear:**

- ✅ Lógica de negocio (validaciones, cálculos, transformaciones)
- ✅ Edge cases (null, empty, límites)
- ✅ Manejo de errores (excepciones, validaciones)
- ❌ Getters/setters triviales
- ❌ Configuración/dependency injection

### 4.2 Integration Tests (20% de cobertura)

- [ ] **APIs + BD real** (PostgreSQL, Redis en containers)
- [ ] Ejecución **<5min** para suite completa
- [ ] **Testcontainers** para BD/cache/message queues
- [ ] Limpieza de BD entre tests (migrations rollback o truncate)
- [ ] Ejecutados en **CI/CD** antes de deploy a staging

**Qué testear:**

- ✅ Endpoints API (request → DB → response)
- ✅ Queries complejas (joins, aggregations)
- ✅ Transacciones (rollback en caso de error)
- ✅ Integración con servicios externos (APIs third-party con mocks)
- ❌ UI rendering (dejar para E2E)

### 4.3 E2E Tests (10% de cobertura)

- [ ] **User journeys críticos** (login, checkout, payment)
- [ ] Ejecución **<30min** para suite completa
- [ ] Framework: Playwright (preferido), Selenium, Cypress
- [ ] Ejecutados en **staging** antes de deploy a producción
- [ ] **NO ejecutar en cada commit** (solo pre-release)

**Qué testear:**

- ✅ Happy paths críticos (registro → login → compra)
- ✅ Flujos multi-paso (wizards, checkout)
- ✅ Interacción UI real (clicks, forms, navigation)
- ❌ Edge cases (dejar para unit/integration)
- ❌ Tests exhaustivos de validación (costosos)

---

## 5. Configuración por Tipo

### 5.1 Unit Tests (.NET)

```csharp
// OrderServiceTests.cs
public class OrderServiceTests
{
    private readonly Mock<IOrderRepository> _mockRepo;
    private readonly OrderService _sut;

    public OrderServiceTests()
    {
        _mockRepo = new Mock<IOrderRepository>();
        _sut = new OrderService(_mockRepo.Object);
    }

    [Fact]
    public async Task CreateOrder_ValidInput_ReturnsOrderId()
    {
        // Arrange
        var request = new CreateOrderRequest { UserId = "123", Total = 100 };
        _mockRepo.Setup(r => r.AddAsync(It.IsAny<Order>(), default))
                 .ReturnsAsync(Guid.NewGuid());

        // Act
        var result = await _sut.CreateOrderAsync(request, default);

        // Assert
        result.Should().NotBeEmpty();
        _mockRepo.Verify(r => r.AddAsync(It.IsAny<Order>(), default), Times.Once);
    }
}
```

**Ejecución:**

```bash
dotnet test --filter "Category=Unit" # <500ms
```

### 5.2 Integration Tests (.NET + Testcontainers)

```csharp
// OrdersApiIntegrationTests.cs
public class OrdersApiIntegrationTests : IClassFixture<WebApplicationFactory<Program>>
{
    private readonly HttpClient _client;
    private readonly PostgreSqlContainer _postgres;

    public OrdersApiIntegrationTests(WebApplicationFactory<Program> factory)
    {
        _postgres = new PostgreSqlBuilder()
            .WithImage("postgres:15.5-alpine")
            .Build();
        _postgres.StartAsync().Wait();

        _client = factory.WithWebHostBuilder(builder =>
        {
            builder.ConfigureServices(services =>
            {
                // Replace DB with Testcontainers instance
                services.RemoveAll<DbContextOptions<OrdersContext>>();
                services.AddDbContext<OrdersContext>(options =>
                    options.UseNpgsql(_postgres.GetConnectionString()));
            });
        }).CreateClient();
    }

    [Fact]
    public async Task POST_Orders_ReturnsCreated()
    {
        // Arrange
        var request = new { UserId = "123", Total = 100 };

        // Act
        var response = await _client.PostAsJsonAsync("/api/orders", request);

        // Assert
        response.StatusCode.Should().Be(HttpStatusCode.Created);
        var order = await response.Content.ReadFromJsonAsync<OrderDto>();
        order.OrderId.Should().NotBeEmpty();
    }
}
```

**Ejecución:**

```bash
dotnet test --filter "Category=Integration" # <5min
```

### 5.3 E2E Tests (Playwright)

```typescript
// checkout.spec.ts
import { test, expect } from "@playwright/test";

test("complete checkout flow", async ({ page }) => {
  // Login
  await page.goto("https://staging.talma.com/login");
  await page.fill("#email", "test@example.com");
  await page.fill("#password", "test123");
  await page.click('button[type="submit"]');
  await expect(page).toHaveURL("/dashboard");

  // Add product to cart
  await page.goto("/products/123");
  await page.click('button:has-text("Add to Cart")');
  await expect(page.locator(".cart-count")).toHaveText("1");

  // Checkout
  await page.click('a:has-text("Cart")');
  await page.click('button:has-text("Checkout")');
  await page.fill("#card-number", "4111111111111111");
  await page.fill("#cvv", "123");
  await page.click('button:has-text("Pay")');

  // Verify success
  await expect(page.locator(".success-message")).toContainText(
    "Order confirmed",
  );
});
```

**Ejecución:**

```bash
npx playwright test --project=chromium # <30min para suite completa
```

---

## 6. CI/CD Integration

```yaml
# .github/workflows/test.yml
name: Test Pipeline

on: [push, pull_request]

jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-dotnet@v3
      - run: dotnet test --filter "Category=Unit" --logger "trx"
      - name: Check duration
        run: |
          duration=$(grep -oP 'duration="\K[^"]+' TestResults/*.trx | awk '{sum+=$1} END {print sum}')
          if (( $(echo "$duration > 500" | bc -l) )); then
            echo "Unit tests took ${duration}ms (target: <500ms)"
            exit 1
          fi

  integration-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-dotnet@v3
      - run: dotnet test --filter "Category=Integration"

  e2e-tests:
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main' # Solo en releases
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
      - run: npm ci
      - run: npx playwright install
      - run: npx playwright test
        env:
          BASE_URL: https://staging.talma.com
```

---

## 7. Métricas de Cumplimiento

| Métrica                       | Target                 | Verificación       |
| ----------------------------- | ---------------------- | ------------------ |
| **Unit tests coverage**       | >70% lógica de negocio | Coverlet/SonarQube |
| **Integration tests**         | 20% endpoints críticos | Manual count       |
| **E2E tests**                 | 10% user journeys      | Manual count       |
| **Unit test duration**        | <500ms suite completa  | CI logs            |
| **Integration test duration** | <5min suite completa   | CI logs            |
| **E2E test duration**         | <30min suite completa  | CI logs            |
| **Test success rate**         | >95% (flaky <5%)       | CI history         |

**Anti-pattern: Inverted Pyramid** ❌

```
   /----------\
  /    E2E     \ 70% - MALO: lento, frágil, costoso
 /    INT      \
/     UNIT      \ 10% - Cobertura insuficiente
```

---

## 8. Prohibiciones

- ❌ Mayoría de tests en E2E (pirámide invertida)
- ❌ Unit tests con BD/HTTP real (usar mocks)
- ❌ E2E tests en cada commit (solo pre-release)
- ❌ Tests interdependientes (cada test debe ser aislado)
- ❌ Tests >30 segundos sin justificación (refactorizar)
- ❌ Coverage <70% en Services/Repositories
- ❌ Tests flaky (>5% tasa de fallo intermitente)

---

## 9. Validación

**Checklist de cumplimiento:**

- [ ] `dotnet test --filter Category=Unit` → <500ms
- [ ] `dotnet test /p:CollectCoverage=true` → >70% en Services
- [ ] `dotnet test --filter Category=Integration` → <5min
- [ ] Playwright tests ejecutados solo en staging (NO en cada PR)
- [ ] CI bloquea merge si unit tests fallan
- [ ] Testcontainers usado para integration tests (NO BD en memoria)

---

## 10. Referencias

- [Mike Cohn — Test Pyramid](https://www.mountaingoatsoftware.com/blog/the-forgotten-layer-of-the-test-automation-pyramid)
- [Martin Fowler — Test Pyramid](https://martinfowler.com/articles/practical-test-pyramid.html)
- [Playwright Documentation](https://playwright.dev/)
- [Testcontainers](https://testcontainers.com/)
- [Estándar: Unit Tests](../testing/01-unit-tests.md)
- [Estándar: Integration Tests](../testing/02-integration-tests.md)
