---
id: testing-standards
sidebar_position: 2
title: Estándares de Testing
description: Estándares consolidados de testing con Testing Pyramid, unit tests, integration tests y contract testing
---

# Estándar Técnico — Estándares de Testing

## 1. Propósito

Garantizar código confiable y arquitectura escalable mediante estrategia de testing basada en Testing Pyramid de Mike Cohn, priorizando tests rápidos y aislados (unit tests 70%), tests de integración con dependencias reales (20%) y contract testing para microservicios (10% adicional), maximizando cobertura y velocidad de feedback.

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
- [ ] Provider states implementados

## 6. Unit Tests — Testing Unitario

### 6.1 Propósito

Validar lógica de negocio aislada con mocks, sin dependencias externas, garantizando tests rápidos (<500ms suite completa) y confiables.

### 6.2 Qué Testear

- ✅ Lógica de negocio (validaciones, cálculos, transformaciones)
- ✅ Edge cases (null, empty, límites)
- ✅ Manejo de errores (excepciones, validaciones)
- ✅ Funciones puras (Utilities, Helpers)
- ❌ Getters/setters triviales
- ❌ Configuración/dependency injection
- ❌ Integraciones con BD/HTTP (usar integration tests)

### 6.3 Configuración

```xml
<!-- Tests.csproj -->
<ItemGroup>
  <PackageReference Include="xUnit" Version="2.6.*" />
  <PackageReference Include="xunit.runner.visualstudio" Version="2.5.*" />
  <PackageReference Include="Moq" Version="4.20.*" />
  <PackageReference Include="FluentAssertions" Version="6.12.*" />
  <PackageReference Include="coverlet.collector" Version="6.0.*" />
</ItemGroup>
```

### 6.4 Ejemplo Completo

```csharp
// OrderServiceTests.cs
public class OrderServiceTests
{
    private readonly Mock<IOrderRepository> _mockRepository;
    private readonly Mock<IPaymentService> _mockPaymentService;
    private readonly Mock<ILogger<OrderService>> _mockLogger;
    private readonly OrderService _sut; // System Under Test

    public OrderServiceTests()
    {
        _mockRepository = new Mock<IOrderRepository>();
        _mockPaymentService = new Mock<IPaymentService>();
        _mockLogger = new Mock<ILogger<OrderService>>();

        _sut = new OrderService(
            _mockRepository.Object,
            _mockPaymentService.Object,
            _mockLogger.Object);
    }

    [Fact]
    public async Task CreateOrderAsync_ValidRequest_ReturnsOrderId()
    {
        // Arrange
        var orderId = Guid.NewGuid();
        var request = new CreateOrderRequest
        {
            UserId = "user-123",
            Items = new[] { new OrderItem { ProductId = "prod-1", Quantity = 2 } },
            Total = 100.50m
        };

        _mockRepository
            .Setup(r => r.AddAsync(It.IsAny<Order>(), default))
            .ReturnsAsync(orderId);

        _mockPaymentService
            .Setup(p => p.AuthorizePaymentAsync(It.IsAny<decimal>(), default))
            .ReturnsAsync(new PaymentResult { Success = true });

        // Act
        var result = await _sut.CreateOrderAsync(request, default);

        // Assert
        result.Should().NotBeEmpty();
        result.Should().Be(orderId);

        _mockRepository.Verify(
            r => r.AddAsync(It.Is<Order>(o => o.UserId == "user-123"), default),
            Times.Once);

        _mockPaymentService.Verify(
            p => p.AuthorizePaymentAsync(100.50m, default),
            Times.Once);
    }

    [Theory]
    [InlineData("")]
    [InlineData(null)]
    [InlineData("   ")]
    public async Task CreateOrderAsync_InvalidUserId_ThrowsArgumentException(string invalidUserId)
    {
        // Arrange
        var request = new CreateOrderRequest { UserId = invalidUserId };

        // Act & Assert
        await Assert.ThrowsAsync<ArgumentException>(
            () => _sut.CreateOrderAsync(request, default));

        _mockRepository.Verify(r => r.AddAsync(It.IsAny<Order>(), default), Times.Never);
    }

    [Fact]
    public async Task CreateOrderAsync_PaymentFails_ThrowsPaymentException()
    {
        // Arrange
        var request = new CreateOrderRequest
        {
            UserId = "user-123",
            Items = new[] { new OrderItem { ProductId = "prod-1", Quantity = 1 } },
            Total = 50.00m
        };

        _mockPaymentService
            .Setup(p => p.AuthorizePaymentAsync(It.IsAny<decimal>(), default))
            .ReturnsAsync(new PaymentResult { Success = false, ErrorMessage = "Insufficient funds" });

        // Act & Assert
        var exception = await Assert.ThrowsAsync<PaymentException>(
            () => _sut.CreateOrderAsync(request, default));

        exception.Message.Should().Contain("Payment failed");
        _mockRepository.Verify(r => r.AddAsync(It.IsAny<Order>(), default), Times.Never);
    }

    [Fact]
    public async Task GetOrderAsync_OrderExists_ReturnsOrder()
    {
        // Arrange
        var orderId = Guid.NewGuid();
        var expectedOrder = new Order
        {
            OrderId = orderId,
            UserId = "user-123",
            Status = OrderStatus.Pending,
            Total = 100.50m
        };

        _mockRepository
            .Setup(r => r.GetByIdAsync(orderId, default))
            .ReturnsAsync(expectedOrder);

        // Act
        var result = await _sut.GetOrderAsync(orderId, default);

        // Assert
        result.Should().NotBeNull();
        result.OrderId.Should().Be(orderId);
        result.Status.Should().Be(OrderStatus.Pending);
    }

    [Fact]
    public async Task GetOrderAsync_OrderNotFound_ReturnsNull()
    {
        // Arrange
        var orderId = Guid.NewGuid();
        _mockRepository
            .Setup(r => r.GetByIdAsync(orderId, default))
            .ReturnsAsync((Order)null);

        // Act
        var result = await _sut.GetOrderAsync(orderId, default);

        // Assert
        result.Should().BeNull();
    }
}
```

### 6.5 Prohibiciones Unit Tests

- ❌ Dependencias reales (BD, HTTP, filesystem)
- ❌ Tests interdependientes (cada test aislado)
- ❌ `Thread.Sleep()` o delays arbitrarios
- ❌ Lógica condicional en tests (evitar if/else)
- ❌ Tests sin asserts (no-op tests)
- ❌ Nombres genéricos (`Test1`, `TestMethod`)
- ❌ Multiple assertions no relacionadas (un concepto por test)

## 7. Integration Tests — Testing de Integración

### 7.1 Propósito

Validar interacción entre componentes reales (APIs, PostgreSQL, Redis, Kafka) usando WebApplicationFactory y Testcontainers.

### 7.2 Qué Testear

- ✅ Endpoints API (request → Controller → Service → Repository → DB → response)
- ✅ Queries complejas (joins, aggregations)
- ✅ Transacciones (rollback en caso de error)
- ✅ Integración con cache (Redis)
- ✅ Integración con message brokers (Kafka)
- ❌ Lógica aislada (usar unit tests)
- ❌ Tests con mocks (NO es integración real)

### 7.3 Configuración

```xml
<!-- IntegrationTests.csproj -->
<ItemGroup>
  <PackageReference Include="Microsoft.AspNetCore.Mvc.Testing" Version="8.0.*" />
  <PackageReference Include="Testcontainers" Version="3.7.*" />
  <PackageReference Include="Testcontainers.PostgreSql" Version="3.7.*" />
  <PackageReference Include="Testcontainers.Redis" Version="3.7.*" />
  <PackageReference Include="xunit" Version="2.6.*" />
  <PackageReference Include="FluentAssertions" Version="6.12.*" />
</ItemGroup>
```

### 7.4 Ejemplo Completo

```csharp
// IntegrationTestFactory.cs
using DotNet.Testcontainers.Builders;
using Microsoft.AspNetCore.Mvc.Testing;
using Microsoft.EntityFrameworkCore;
using Testcontainers.PostgreSql;
using Testcontainers.Redis;

public class IntegrationTestFactory : WebApplicationFactory<Program>, IAsyncLifetime
{
    private readonly PostgreSqlContainer _dbContainer;
    private readonly RedisContainer _cacheContainer;

    public IntegrationTestFactory()
    {
        _dbContainer = new PostgreSqlBuilder()
            .WithImage("postgres:16-alpine")
            .WithDatabase("test_db")
            .WithUsername("test")
            .WithPassword("test123")
            .Build();

        _cacheContainer = new RedisBuilder()
            .WithImage("redis:7-alpine")
            .Build();
    }

    protected override void ConfigureWebHost(IWebHostBuilder builder)
    {
        builder.ConfigureServices(services =>
        {
            // Replace DbContext con Testcontainer
            services.RemoveAll<DbContextOptions<ApplicationDbContext>>();
            services.AddDbContext<ApplicationDbContext>(options =>
                options.UseNpgsql(_dbContainer.GetConnectionString()));

            // Replace Redis
            services.RemoveAll<IDistributedCache>();
            services.AddStackExchangeRedisCache(options =>
            {
                options.Configuration = _cacheContainer.GetConnectionString();
            });

            // Aplicar migraciones
            var sp = services.BuildServiceProvider();
            using var scope = sp.CreateScope();
            var db = scope.ServiceProvider.GetRequiredService<ApplicationDbContext>();
            db.Database.Migrate();
        });

        builder.UseEnvironment("Testing");
    }

    public async Task InitializeAsync()
    {
        await _dbContainer.StartAsync();
        await _cacheContainer.StartAsync();
    }

    public new async Task DisposeAsync()
    {
        await _dbContainer.DisposeAsync();
        await _cacheContainer.DisposeAsync();
    }
}
```

```csharp
// OrdersControllerIntegrationTests.cs
public class OrdersControllerIntegrationTests : IClassFixture<IntegrationTestFactory>
{
    private readonly HttpClient _client;
    private readonly IntegrationTestFactory _factory;

    public OrdersControllerIntegrationTests(IntegrationTestFactory factory)
    {
        _factory = factory;
        _client = factory.CreateClient();
    }

    [Fact]
    public async Task POST_Orders_ValidRequest_ReturnsCreated()
    {
        // Arrange
        var request = new CreateOrderRequest
        {
            UserId = "user-123",
            Items = new[]
            {
                new OrderItemRequest { ProductId = "prod-1", Quantity = 2, Price = 50.25m }
            }
        };

        // Act
        var response = await _client.PostAsJsonAsync("/api/v1/orders", request);

        // Assert
        response.StatusCode.Should().Be(HttpStatusCode.Created);
        response.Headers.Location.Should().NotBeNull();

        var order = await response.Content.ReadFromJsonAsync<OrderDto>();
        order.Should().NotBeNull();
        order!.OrderId.Should().NotBeEmpty();
        order.UserId.Should().Be("user-123");
        order.Status.Should().Be("PENDING");
        order.Total.Should().Be(100.50m);
    }

    [Fact]
    public async Task GET_Orders_OrderExists_ReturnsOk()
    {
        // Arrange: Crear orden en BD
        using var scope = _factory.Services.CreateScope();
        var db = scope.ServiceProvider.GetRequiredService<ApplicationDbContext>();

        var order = new Order
        {
            OrderId = Guid.NewGuid(),
            UserId = "user-456",
            Status = "PENDING",
            Total = 75.00m,
            CreatedAt = DateTime.UtcNow
        };

        db.Orders.Add(order);
        await db.SaveChangesAsync();

        // Act
        var response = await _client.GetAsync($"/api/v1/orders/{order.OrderId}");

        // Assert
        response.StatusCode.Should().Be(HttpStatusCode.OK);

        var orderDto = await response.Content.ReadFromJsonAsync<OrderDto>();
        orderDto.Should().NotBeNull();
        orderDto!.OrderId.Should().Be(order.OrderId);
        orderDto.UserId.Should().Be("user-456");
    }

    [Fact]
    public async Task GET_Orders_OrderNotFound_ReturnsNotFound()
    {
        // Arrange
        var nonExistentId = Guid.NewGuid();

        // Act
        var response = await _client.GetAsync($"/api/v1/orders/{nonExistentId}");

        // Assert
        response.StatusCode.Should().Be(HttpStatusCode.NotFound);
    }

    [Fact]
    public async Task POST_Orders_DuplicateRequest_ReturnsConflict()
    {
        // Arrange
        var idempotencyKey = Guid.NewGuid().ToString();
        var request = new CreateOrderRequest { UserId = "user-789" };

        _client.DefaultRequestHeaders.Add("Idempotency-Key", idempotencyKey);

        // Act: Primera request
        var response1 = await _client.PostAsJsonAsync("/api/v1/orders", request);

        // Act: Segunda request con mismo idempotency key
        var response2 = await _client.PostAsJsonAsync("/api/v1/orders", request);

        // Assert
        response1.StatusCode.Should().Be(HttpStatusCode.Created);
        response2.StatusCode.Should().Be(HttpStatusCode.Conflict);
    }

    [Fact]
    public async Task GET_Orders_UsesCacheOnSecondRequest()
    {
        // Arrange: Crear orden en BD
        using var scope = _factory.Services.CreateScope();
        var db = scope.ServiceProvider.GetRequiredService<ApplicationDbContext>();
        var cache = scope.ServiceProvider.GetRequiredService<IDistributedCache>();

        var order = new Order
        {
            OrderId = Guid.NewGuid(),
            UserId = "user-cache",
            Status = "PENDING",
            Total = 100.00m
        };

        db.Orders.Add(order);
        await db.SaveChangesAsync();

        // Act: Primera request (miss cache, hit DB)
        var response1 = await _client.GetAsync($"/api/v1/orders/{order.OrderId}");

        // Act: Segunda request (hit cache)
        var response2 = await _client.GetAsync($"/api/v1/orders/{order.OrderId}");

        // Assert
        response1.StatusCode.Should().Be(HttpStatusCode.OK);
        response2.StatusCode.Should().Be(HttpStatusCode.OK);

        // Verificar que está en cache
        var cacheKey = $"order:{order.OrderId}";
        var cachedData = await cache.GetStringAsync(cacheKey);
        cachedData.Should().NotBeNull();
    }
}
```

### 7.5 Prohibiciones Integration Tests

- ❌ In-memory DB (SQLite) para tests de integración
- ❌ Dependencias reales en producción (usar containers)
- ❌ Tests sin cleanup (contamina siguientes tests)
- ❌ Hardcoded ports (usar dynamic ports de Testcontainers)
- ❌ Tests interdependientes (orden de ejecución)
- ❌ Secrets en código (usar variables de entorno)
- ❌ Tests que modifican estado global

## 8. Contract Testing — Testing de Contratos

### 8.1 Propósito

Garantizar compatibilidad entre microservicios (consumer-provider) mediante PactNet, generando contratos en tests de consumer y validándolos en provider.

### 8.2 Cuándo Usar Contract Testing

- ✅ Comunicación entre microservicios REST
- ✅ APIs REST consumidas por otros equipos
- ✅ Servicios con múltiples consumers
- ✅ Evoluciones de API con versionado
- ❌ APIs externas de terceros (usar mocks o integration tests)
- ❌ Mensajería asíncrona Kafka (usar schema validation separado)

### 8.3 Configuración

```xml
<!-- ConsumerTests.csproj -->
<ItemGroup>
  <PackageReference Include="PactNet" Version="5.0.*" />
  <PackageReference Include="xunit" Version="2.6.*" />
  <PackageReference Include="FluentAssertions" Version="6.12.*" />
</ItemGroup>
```

### 8.4 Consumer Tests — Generar Contrato

```csharp
// PaymentServiceConsumerTests.cs
using PactNet;
using PactNet.Matchers;

public class PaymentServiceConsumerTests : IDisposable
{
    private readonly IPactBuilderV4 _pactBuilder;
    private readonly string _providerName = "payment-api";
    private readonly string _consumerName = "order-api";

    public PaymentServiceConsumerTests()
    {
        var pactConfig = new PactConfig
        {
            PactDir = "../../../pacts",
            DefaultJsonSettings = new JsonSerializerSettings
            {
                ContractResolver = new CamelCasePropertyNamesContractResolver()
            }
        };

        _pactBuilder = Pact.V4(_consumerName, _providerName, pactConfig)
            .WithHttpInteractions();
    }

    [Fact]
    public async Task CreatePayment_ValidRequest_ReturnsCreated()
    {
        // Arrange: Definir contrato esperado
        _pactBuilder
            .UponReceiving("a request to create payment")
                .WithRequest(HttpMethod.Post, "/api/v1/payments")
                .WithHeader("Content-Type", "application/json")
                .WithHeader("Authorization", Match.Regex("Bearer .*", "^Bearer .+$"))
                .WithJsonBody(new
                {
                    orderId = Match.Type("ord-123"),
                    amount = Match.Decimal(100.50m),
                    currency = Match.Regex("USD", "^[A-Z]{3}$")
                })
            .WillRespond()
                .WithStatus(201)
                .WithHeader("Content-Type", "application/json")
                .WithJsonBody(new
                {
                    paymentId = Match.Type("pay-456"),
                    status = Match.Regex("pending", "^(pending|completed|failed)$"),
                    createdAt = Match.DateTime("yyyy-MM-dd'T'HH:mm:ss'Z'", DateTime.UtcNow)
                });

        // Act: Ejecutar request contra mock server
        await _pactBuilder.VerifyAsync(async ctx =>
        {
            var client = new HttpClient { BaseAddress = ctx.MockServerUri };
            client.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", "test-token");

            var request = new
            {
                orderId = "ord-123",
                amount = 100.50m,
                currency = "USD"
            };

            var response = await client.PostAsJsonAsync("/api/v1/payments", request);

            // Assert
            response.StatusCode.Should().Be(HttpStatusCode.Created);
            var payment = await response.Content.ReadFromJsonAsync<PaymentResponse>();
            payment.PaymentId.Should().NotBeNullOrEmpty();
            payment.Status.Should().BeOneOf("pending", "completed", "failed");
        });

        // Contrato generado en: pacts/order-api-payment-api.json
    }

    [Fact]
    public async Task GetPayment_PaymentExists_ReturnsOk()
    {
        _pactBuilder
            .UponReceiving("a request to get payment by ID")
                .WithRequest(HttpMethod.Get, "/api/v1/payments/pay-456")
                .WithHeader("Authorization", Match.Regex("Bearer token", "^Bearer .+$"))
            .WillRespond()
                .WithStatus(200)
                .WithJsonBody(new
                {
                    paymentId = "pay-456",
                    orderId = "ord-123",
                    amount = 100.50m,
                    currency = "USD",
                    status = "completed"
                });

        await _pactBuilder.VerifyAsync(async ctx =>
        {
            var client = new HttpClient { BaseAddress = ctx.MockServerUri };
            client.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", "token");

            var response = await client.GetAsync("/api/v1/payments/pay-456");

            response.StatusCode.Should().Be(HttpStatusCode.OK);
            var payment = await response.Content.ReadFromJsonAsync<PaymentResponse>();
            payment.PaymentId.Should().Be("pay-456");
        });
    }

    public void Dispose()
    {
        // Pact file generado automáticamente en Dispose
    }
}
```

### 8.5 Provider Verification — Validar Contrato

```csharp
// PaymentApiProviderTests.cs
using PactNet.Verifier;
using Xunit;

public class PaymentApiProviderTests
{
    private readonly ITestOutputHelper _output;

    public PaymentApiProviderTests(ITestOutputHelper output)
    {
        _output = output;
    }

    [Fact]
    public void ProviderHonoursPactWithConsumers()
    {
        // Arrange
        var config = new PactVerifierConfig
        {
            Outputters = new List<IOutput> { new XUnitOutput(_output) }
        };

        var verifier = new PactVerifier(config);

        // Act: Verificar contratos desde Pact Broker
        verifier
            .ServiceProvider("payment-api", new Uri("http://localhost:5000"))
            .WithPactBrokerSource(new Uri("https://pact-broker.company.com"), options =>
            {
                options.ConsumerVersionSelectors(new ConsumerVersionSelector
                {
                    Branch = "main",
                    Latest = true
                });
                options.ProviderVersionBranch("main");
                options.ProviderVersion("1.2.3");
                options.PublishResults = true;
                options.Token = Environment.GetEnvironmentVariable("PACT_BROKER_TOKEN");
            })
            .WithProviderStateUrl(new Uri("http://localhost:5000/provider-states"))
            .Verify();
    }
}
```

```csharp
// ProviderStatesController.cs - Provider States Setup
[ApiController]
[Route("provider-states")]
public class ProviderStatesController : ControllerBase
{
    private readonly ApplicationDbContext _dbContext;

    [HttpPost]
    public async Task<IActionResult> SetupProviderState([FromBody] ProviderState state)
    {
        // Setup state para tests
        switch (state.State)
        {
            case "payment pay-456 exists":
                _dbContext.Payments.Add(new Payment
                {
                    Id = "pay-456",
                    OrderId = "ord-123",
                    Amount = 100.50m,
                    Currency = "USD",
                    Status = "completed"
                });
                await _dbContext.SaveChangesAsync();
                break;

            case "no payments exist":
                _dbContext.Payments.RemoveRange(_dbContext.Payments);
                await _dbContext.SaveChangesAsync();
                break;

            default:
                return BadRequest($"Unknown provider state: {state.State}");
        }

        return Ok();
    }
}

public class ProviderState
{
    public string State { get; set; }
    public Dictionary<string, object> Params { get; set; }
}
```

### 8.6 Pact Broker — Docker Compose

```yaml
# docker-compose.pact.yml
version: "3.8"

services:
  pact-broker:
    image: pactfoundation/pact-broker:2.100
    ports:
      - "9292:9292"
    environment:
      PACT_BROKER_DATABASE_URL: postgres://pact:pact@postgres:5432/pact_broker
      PACT_BROKER_BASIC_AUTH_USERNAME: pact
      PACT_BROKER_BASIC_AUTH_PASSWORD: pact123
    depends_on:
      - postgres

  postgres:
    image: postgres:15
    environment:
      POSTGRES_USER: pact
      POSTGRES_PASSWORD: pact
      POSTGRES_DB: pact_broker
    volumes:
      - pact-db:/var/lib/postgresql/data

volumes:
  pact-db:
```

### 8.7 CI/CD Integration — Contract Testing

```yaml
# .github/workflows/contract-tests.yml
name: Contract Tests

on:
  pull_request:
    branches: [main]
  push:
    branches: [main]

jobs:
  consumer-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup .NET
        uses: actions/setup-dotnet@v4
        with:
          dotnet-version: "8.0"

      - name: Run Consumer Tests
        run: dotnet test Tests/ConsumerTests.csproj

      - name: Publish Pact to Broker
        run: |
          docker run --rm -v $(pwd)/pacts:/pacts \
            pactfoundation/pact-cli:latest \
            publish /pacts \
            --consumer-app-version=${{ github.sha }} \
            --broker-base-url=${{ secrets.PACT_BROKER_URL }} \
            --broker-token=${{ secrets.PACT_BROKER_TOKEN }} \
            --branch=${{ github.head_ref || github.ref_name }}

  provider-verification:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Start Provider API
        run: |
          dotnet run --project PaymentApi &
          sleep 10

      - name: Verify Contracts
        run: dotnet test Tests/ProviderTests.csproj
        env:
          PACT_BROKER_URL: ${{ secrets.PACT_BROKER_URL }}
          PACT_BROKER_TOKEN: ${{ secrets.PACT_BROKER_TOKEN }}

  can-i-deploy:
    needs: [consumer-tests, provider-verification]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - name: Check deployment safety
        run: |
          docker run --rm pactfoundation/pact-cli:latest \
            can-i-deploy \
            --pacticipant payment-api \
            --version ${{ github.sha }} \
            --to-environment production \
            --broker-base-url ${{ secrets.PACT_BROKER_URL }} \
            --broker-token ${{ secrets.PACT_BROKER_TOKEN }}
```

## 9. CI/CD Integration — All Tests

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
