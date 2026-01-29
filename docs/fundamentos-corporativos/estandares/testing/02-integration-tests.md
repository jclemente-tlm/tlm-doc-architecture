---
id: integration-tests
sidebar_position: 2
title: Testing de Integración
description: Estándar para pruebas de integración con TestContainers, WebApplicationFactory, bases de datos reales y servicios externos.
---

# Estándar Técnico — Testing de Integración

---

## 1. Propósito
Validar interacción entre componentes reales (APIs, PostgreSQL, Redis, Kafka) usando WebApplicationFactory, Testcontainers (PostgreSQL 16, Redis 7, Kafka) y fixtures compartidos con IClassFixture.

---

## 2. Alcance

**Aplica a:**
- APIs REST (Controllers + Services + Repository + BD)
- Integración con PostgreSQL, Oracle, Redis
- Integración con Kafka, S3
- Tests de infraestructura (Docker)

**No aplica a:**
- Lógica aislada (usar unit tests)
- Tests con dependencias mock (NO es integración)
- Tests de performance (usar benchmarks)

---

## 3. Tecnologías Aprobadas

| Componente | Tecnología | Versión mínima | Observaciones |
|-----------|------------|----------------|---------------|
| **Factory** | WebApplicationFactory | 8.0+ | Testing API .NET |
| **Containers** | Testcontainers | 3.7+ | PostgreSQL, Oracle, Redis, Kafka |
| **Framework** | xUnit | 2.6+ | IClassFixture support |
| **HTTP** | HttpClient | - | Testing endpoints |
| **Assertions** | FluentAssertions | 6.12+ | Expresividad |

> El uso de tecnologías no listadas requiere aprobación de Arquitectura.

---

## 4. Requisitos Obligatorios 🔴

- [ ] WebApplicationFactory para APIs .NET
- [ ] Testcontainers para dependencias externas (PostgreSQL, Redis)
- [ ] BD real (NO in-memory DB)
- [ ] IClassFixture para compartir setup (performance)
- [ ] Cleanup después de cada test (transaction rollback o BD limpia)
- [ ] Ejecución paralela habilitada cuando sea posible
- [ ] Environment variables en `.env.test`
- [ ] Migraciones aplicadas automáticamente en setup
- [ ] Tests ejecutables localmente SIN infraestructura externa
- [ ] Integración en CI/CD (containers en GitHub Actions)
- [ ] Naming: `Feature_Scenario_ExpectedResult`
- [ ] NO datos compartidos entre tests (aislamiento)

---

## 5. Prohibiciones

- ❌ In-memory DB (SQLite) para tests de integración
- ❌ Dependencias reales en prod (usar containers)
- ❌ Tests sin cleanup (contamina siguientes tests)
- ❌ Hardcoded ports (usar dynamic ports)
- ❌ Tests interdependientes (orden de ejecución)
- ❌ Secrets en código (usar variables de entorno)
- ❌ Tests que modifican estado global

---

## 6. Configuración Mínima

### C# con WebApplicationFactory y Testcontainers
```xml
<!-- Tests.csproj -->
<ItemGroup>
  <PackageReference Include="Microsoft.AspNetCore.Mvc.Testing" Version="8.0.*" />
  <PackageReference Include="Testcontainers" Version="3.7.*" />
  <PackageReference Include="Testcontainers.PostgreSql" Version="3.7.*" />
  <PackageReference Include="xunit" Version="2.6.*" />
  <PackageReference Include="FluentAssertions" Version="6.12.*" />
</ItemGroup>
```

```csharp
// IntegrationTestFactory.cs
using DotNet.Testcontainers.Builders;
using Microsoft.AspNetCore.Mvc.Testing;
using Microsoft.EntityFrameworkCore;
using Testcontainers.PostgreSql;

public class IntegrationTestFactory : WebApplicationFactory<Program>, IAsyncLifetime
{
    private readonly PostgreSqlContainer _dbContainer;

    public IntegrationTestFactory()
    {
        _dbContainer = new PostgreSqlBuilder()
            .WithImage("postgres:16-alpine")
            .WithDatabase("test_db")
            .WithUsername("test")
            .WithPassword("test123")
            .Build();
    }

    protected override void ConfigureWebHost(IWebHostBuilder builder)
    {
        builder.ConfigureServices(services =>
        {
            // Remover DbContext original
            services.RemoveAll<DbContextOptions<AppDbContext>>();
            
            // Configurar DbContext con container
            services.AddDbContext<AppDbContext>(options =>
                options.UseNpgsql(_dbContainer.GetConnectionString()));

            // Aplicar migraciones
            var sp = services.BuildServiceProvider();
            using var scope = sp.CreateScope();
            var db = scope.ServiceProvider.GetRequiredService<AppDbContext>();
            db.Database.Migrate();
        });
    }

    public async Task InitializeAsync() => await _dbContainer.StartAsync();
    public new async Task DisposeAsync() => await _dbContainer.DisposeAsync();
}
```

```csharp
// OrdersControllerTests.cs
public class OrdersControllerTests : IClassFixture<IntegrationTestFactory>
{
    private readonly HttpClient _client;
    private readonly IntegrationTestFactory _factory;

    public OrdersControllerTests(IntegrationTestFactory factory)
    {
        _factory = factory;
        _client = factory.CreateClient();
    }

    [Fact]
    public async Task CreateOrder_ValidRequest_ReturnsCreated()
    {
        // Arrange
        var request = new CreateOrderRequest { UserId = "user-123", Items = new[] { /* items */ } };

        // Act
        var response = await _client.PostAsJsonAsync("/api/v1/orders", request);

        // Assert
        response.StatusCode.Should().Be(HttpStatusCode.Created);
        var order = await response.Content.ReadFromJsonAsync<OrderDto>();
        order.Should().NotBeNull();
        order!.OrderId.Should().NotBeEmpty();
    }

    [Fact]
    public async Task GetOrder_OrderExists_ReturnsOk()
    {
        // Arrange: Crear orden en BD
        using var scope = _factory.Services.CreateScope();
        var db = scope.ServiceProvider.GetRequiredService<AppDbContext>();
        var order = new Order { OrderId = Guid.NewGuid(), Status = "PENDING" };
        db.Orders.Add(order);
        await db.SaveChangesAsync();

        // Act
        var response = await _client.GetAsync($"/api/v1/orders/{order.OrderId}");

        // Assert
        response.StatusCode.Should().Be(HttpStatusCode.OK);
    }
}
```

---

## 7. Validación

```bash
# Ejecutar integration tests
dotnet test --filter Category=Integration

# Coverage (excluir unit tests)
dotnet test --filter Category=Integration /p:CollectCoverage=true

# CI/CD - GitHub Actions
# Testcontainers automáticamente gestiona Docker
dotnet test
```

**Métricas de cumplimiento:**

| Métrica | Target | Verificación |
|---------|--------|--------------|  
| Containers usados | 100% | NO in-memory DB |
| Cleanup después tests | 100% | Transaction rollback |
| Tests ejecutables localmente | 100% | `dotnet test` funciona |
| BD real (PostgreSQL) | 100% | Testcontainers |

Incumplimientos deben corregirse o documentarse mediante excepción aprobada.

---

## 8. Referencias

- [Unit Tests](01-unit-tests.md)
- [E2E Tests](03-e2e-tests.md)
- [Testcontainers .NET](https://dotnet.testcontainers.org/)
- [WebApplicationFactory](https://learn.microsoft.com/aspnet/core/test/integration-tests)
