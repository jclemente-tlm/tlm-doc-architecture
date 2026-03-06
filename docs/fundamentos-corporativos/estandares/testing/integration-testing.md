---
id: integration-testing
sidebar_position: 5
title: Pruebas de Integración
description: Estándares para integration tests con WebApplicationFactory y Testcontainers
tags:
  [testing, pruebas-integracion, testcontainers, webapplicationfactory, xunit]
---

# Pruebas de Integración

## Contexto

Este estándar define los **patrones para pruebas de integración**: tests que verifican que los componentes trabajan correctamente en conjunto, usando infraestructura real mediante Testcontainers.

---

## Stack Tecnológico

| Componente             | Tecnología            | Versión | Uso                                 |
| ---------------------- | --------------------- | ------- | ----------------------------------- |
| **Test Host**          | WebApplicationFactory | 8.0+    | In-memory test server               |
| **Containers**         | Testcontainers        | 3.7+    | PostgreSQL, Kafka, Redis containers |
| **Fixture Management** | xUnit IClassFixture   | 2.6+    | Shared test context                 |
| **Assertions**         | FluentAssertions      | 6.12+   | Assertions legibles                 |
| **Fake Data**          | Bogus                 | 35.0+   | Generación de datos de prueba       |

---

## Pruebas de Integración

### ¿Qué es Integration Testing?

Tests que verifican integración real entre componentes usando infraestructura real (DB, message brokers) vía Testcontainers.

**Propósito:** Validar que componentes trabajan juntos correctamente.

**Componentes:**

- **WebApplicationFactory**: In-memory test server
- **Testcontainers**: Docker containers para dependencias
- **Test Fixtures**: Shared context entre tests

**Beneficios:**
✅ Alta confianza (infraestructura real)
✅ Detecta problemas de integración
✅ Valida migrations, queries, serialization
✅ Fast feedback (segundos, no minutos)

### WebApplicationFactory: API Integration Tests

```csharp
// tests/OrderService.IntegrationTests/CustomWebApplicationFactory.cs
using Microsoft.AspNetCore.Hosting;
using Microsoft.AspNetCore.Mvc.Testing;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.DependencyInjection;
using Testcontainers.PostgreSql;

public class CustomWebApplicationFactory<TProgram>
    : WebApplicationFactory<TProgram>, IAsyncLifetime where TProgram : class
{
    private readonly PostgreSqlContainer _postgresContainer = new PostgreSqlBuilder()
        .WithImage("postgres:15")
        .WithDatabase("orders_test")
        .WithUsername("postgres")
        .WithPassword("postgres")
        .Build();

    protected override void ConfigureWebHost(IWebHostBuilder builder)
    {
        builder.ConfigureServices(services =>
        {
            // Remover DbContext real
            var descriptor = services.SingleOrDefault(
                d => d.ServiceType == typeof(DbContextOptions<AppDbContext>));
            if (descriptor != null)
                services.Remove(descriptor);

            // Agregar DbContext de test con Testcontainer
            services.AddDbContext<AppDbContext>(options =>
            {
                options.UseNpgsql(_postgresContainer.GetConnectionString());
            });

            // Seed database
            var sp = services.BuildServiceProvider();
            using var scope = sp.CreateScope();
            var db = scope.ServiceProvider.GetRequiredService<AppDbContext>();
            db.Database.Migrate(); // Ejecutar migrations
            SeedTestData(db);
        });
    }

    private void SeedTestData(AppDbContext db)
    {
        db.Customers.AddRange(
            new Customer { Id = "CUST-123", Name = "John Doe", Email = "john@example.com" },
            new Customer { Id = "CUST-456", Name = "Jane Smith", Email = "jane@example.com" }
        );
        db.SaveChanges();
    }

    public async Task InitializeAsync()
    {
        await _postgresContainer.StartAsync();
    }

    public new async Task DisposeAsync()
    {
        await _postgresContainer.StopAsync();
    }
}

// tests/OrderService.IntegrationTests/Controllers/OrdersControllerTests.cs
public class OrdersControllerTests : IClassFixture<CustomWebApplicationFactory<Program>>
{
    private readonly HttpClient _client;

    public OrdersControllerTests(CustomWebApplicationFactory<Program> factory)
    {
        _client = factory.CreateClient();
    }

    [Fact]
    public async Task CreateOrder_WithValidRequest_ShouldReturn201Created()
    {
        // Arrange
        var request = new
        {
            customerId = "CUST-123",
            items = new[] { new { sku = "SKU-001", quantity = 2, unitPrice = 100.00 } },
            paymentMethod = "credit_card"
        };

        // Act
        var response = await _client.PostAsJsonAsync("/api/orders", request);

        // Assert
        response.StatusCode.Should().Be(HttpStatusCode.Created);

        var createdOrder = await response.Content.ReadFromJsonAsync<OrderResponse>();
        createdOrder.Should().NotBeNull();
        createdOrder.TotalAmount.Should().Be(236m); // 200 + 18% tax
        response.Headers.Location.ToString().Should().Contain($"/api/orders/{createdOrder.OrderId}");
    }

    [Fact]
    public async Task CreateOrder_WithInvalidCustomer_ShouldReturn404NotFound()
    {
        // Arrange
        var request = new
        {
            customerId = "INVALID",
            items = new[] { new { sku = "SKU-001", quantity = 1, unitPrice = 100.00 } }
        };

        // Act
        var response = await _client.PostAsJsonAsync("/api/orders", request);

        // Assert
        response.StatusCode.Should().Be(HttpStatusCode.NotFound);

        var error = await response.Content.ReadFromJsonAsync<ProblemDetails>();
        error.Title.Should().Be("Customer not found");
    }

    [Fact]
    public async Task GetOrder_WhenExists_ShouldReturn200OK()
    {
        // Arrange - Crear order primero
        var createRequest = new
        {
            customerId = "CUST-123",
            items = new[] { new { sku = "SKU-001", quantity = 1, unitPrice = 100.00 } }
        };
        var createResponse = await _client.PostAsJsonAsync("/api/orders", createRequest);
        var createdOrder = await createResponse.Content.ReadFromJsonAsync<OrderResponse>();

        // Act
        var response = await _client.GetAsync($"/api/orders/{createdOrder.OrderId}");

        // Assert
        response.StatusCode.Should().Be(HttpStatusCode.OK);

        var order = await response.Content.ReadFromJsonAsync<OrderResponse>();
        order.CustomerId.Should().Be("CUST-123");
        order.Items.Should().HaveCount(1);
    }

    [Fact]
    public async Task GetOrder_WhenNotExists_ShouldReturn404NotFound()
    {
        var response = await _client.GetAsync("/api/orders/99999");
        response.StatusCode.Should().Be(HttpStatusCode.NotFound);
    }
}
```

### Testcontainers: Múltiples Dependencias

```csharp
// tests/OrderService.IntegrationTests/Fixtures/IntegrationTestFixture.cs
public class IntegrationTestFixture : IAsyncLifetime
{
    public PostgreSqlContainer PostgresContainer { get; }
    public KafkaContainer KafkaContainer { get; }
    public RedisContainer RedisContainer { get; }

    public IntegrationTestFixture()
    {
        PostgresContainer = new PostgreSqlBuilder()
            .WithImage("postgres:15").WithDatabase("orders_test").Build();

        KafkaContainer = new KafkaBuilder()
            .WithImage("confluentinc/cp-kafka:7.5.0").Build();

        RedisContainer = new RedisBuilder()
            .WithImage("redis:7-alpine").Build();
    }

    public async Task InitializeAsync()
    {
        await Task.WhenAll(
            PostgresContainer.StartAsync(),
            KafkaContainer.StartAsync(),
            RedisContainer.StartAsync());
    }

    public async Task DisposeAsync()
    {
        await Task.WhenAll(
            PostgresContainer.StopAsync(),
            KafkaContainer.StopAsync(),
            RedisContainer.StopAsync());
    }
}

// Uso en tests con múltiples containers
[Collection("Integration")]
public class OrderEventPublisherTests : IClassFixture<IntegrationTestFixture>
{
    private readonly IntegrationTestFixture _fixture;

    public OrderEventPublisherTests(IntegrationTestFixture fixture)
    {
        _fixture = fixture;
    }

    [Fact]
    public async Task PublishOrderCreatedEvent_ShouldPersistToKafka()
    {
        // Arrange
        var producer = new ProducerBuilder<string, string>(new ProducerConfig
        {
            BootstrapServers = _fixture.KafkaContainer.GetBootstrapAddress()
        }).Build();

        var orderEvent = new OrderCreatedEvent
        {
            OrderId = 123,
            CustomerId = "CUST-123",
            TotalAmount = 236m
        };

        // Act
        var result = await producer.ProduceAsync(
            "order-events",
            new Message<string, string>
            {
                Key = orderEvent.OrderId.ToString(),
                Value = JsonSerializer.Serialize(orderEvent)
            });

        // Assert
        result.Status.Should().Be(PersistenceStatus.Persisted);
        result.Partition.Should().BeGreaterOrEqualTo(0);
    }
}
```

---

## Monitoreo y Observabilidad

Los resultados de integration tests se publican a SonarQube en cada PR. Métricas clave:

- Tiempo total de ejecución del suite de integración (target: < 10 min)
- Tests deterministicos (cero flaky tests)
- Coverage de endpoints de API

Ver [Automatización de Tests](./test-automation.md) para la configuración del pipeline CI/CD.

---

## Requisitos Técnicos

### MUST (Obligatorio)

- **MUST** usar Testcontainers para dependencias reales (no mocks de DB/Kafka/Redis)
- **MUST** ejecutar migrations en la database de test antes de los tests
- **MUST** cleanup entre tests (transactions o recrear containers)
- **MUST** WebApplicationFactory para API integration tests
- **MUST** tests deterministicos (no depender de timing)

### SHOULD (Fuertemente recomendado)

- **SHOULD** usar class fixtures para setup costoso compartido
- **SHOULD** suite de integration tests ejecutarse en < 10 minutos
- **SHOULD** Bogus para generar fake data realista en seeds

### MUST NOT (Prohibido)

- **MUST NOT** usar mocks para reemplazar infraestructura real (DB en memoria excepto con propósito específico)
- **MUST NOT** tests con `sleep`/delays fijos
- **MUST NOT** dependencias entre tests (orden de ejecución)

---

## Referencias

- [Testcontainers .NET](https://dotnet.testcontainers.org/)
- [WebApplicationFactory](https://learn.microsoft.com/en-us/aspnet/core/test/integration-tests)
- [xUnit IClassFixture](https://xunit.net/docs/shared-context)
- [Pruebas Unitarias](./unit-testing.md)
- [Contract Testing](./contract-testing.md)
- [Pirámide de Testing](./testing-pyramid.md)
