---
id: contract-testing
sidebar_position: 3
title: Contract Testing
description: Testing de contratos entre consumidores y proveedores de APIs
---

# Contract Testing

## Contexto

Este estándar define cómo implementar contract testing (consumer-driven contracts) para garantizar compatibilidad entre APIs y sus consumidores. Complementa el [lineamiento de APIs y Contratos](../../lineamientos/arquitectura/07-apis-y-contratos.md) especificando **cómo** validar contratos de manera automatizada.

---

## Stack Tecnológico

| Componente           | Tecnología   | Versión | Uso                       |
| -------------------- | ------------ | ------- | ------------------------- |
| **Framework**        | ASP.NET Core | 8.0+    | Framework base            |
| **Contract Testing** | PactNet      | 4.0+    | Consumer-driven contracts |
| **Testing**          | xUnit        | 2.6+    | Framework de testing      |
| **Broker**           | Pact Broker  | 2.107+  | Publicación de contratos  |

### Dependencias NuGet

```xml
<!-- Consumer side -->
<PackageReference Include="PactNet" Version="4.5.0" />
<PackageReference Include="xunit" Version="2.6.0" />
<PackageReference Include="Microsoft.AspNetCore.Mvc.Testing" Version="8.0.0" />

<!-- Provider side -->
<PackageReference Include="PactNet" Version="4.5.0" />
<PackageReference Include="xunit" Version="2.6.0" />
```

---

## Implementación Técnica

### Consumer Test - Definir Expectativas

```csharp
// OrdersConsumer.Tests/OrderApiContractTests.cs
using PactNet;
using PactNet.Matchers;

public class OrderApiContractTests : IDisposable
{
    private readonly IPactBuilderV3 _pact;
    private readonly int _mockServerPort = 9000;

    public OrderApiContractTests()
    {
        var config = new PactConfig
        {
            PactDir = Path.Combine("..", "..", "..", "pacts"),
            LogLevel = PactLogLevel.Debug
        };

        // ✅ Definir consumidor y proveedor
        _pact = Pact.V3("OrdersWebApp", "OrdersAPI", config)
            .WithHttpInteractions(_mockServerPort);
    }

    [Fact]
    public async Task GetOrder_WhenOrderExists_ReturnsOrderDetails()
    {
        // ✅ ARRANGE: Definir expectativa del consumidor
        _pact
            .UponReceiving("A GET request for an existing order")
            .Given("Order 550e8400-e29b-41d4-a716-446655440000 exists")
            .WithRequest(HttpMethod.Get, "/api/v1/orders/550e8400-e29b-41d4-a716-446655440000")
            .WithHeader("Accept", "application/json")
            .WithHeader("Authorization", Match.Regex("Bearer .*", "Bearer token123"))
            .WillRespond()
            .WithStatus(200)
            .WithHeader("Content-Type", "application/json")
            .WithJsonBody(new
            {
                id = Match.Type("550e8400-e29b-41d4-a716-446655440000"),
                orderNumber = Match.Regex("ORD-2024-001234", "^ORD-\\d{4}-\\d{6}$"),
                customerId = Match.Type("3fa85f64-5717-4562-b3fc-2c963f66afa6"),
                totalAmount = Match.Decimal(299.99),
                status = Match.Regex("Pending", "^(Pending|Confirmed|Shipped|Delivered)$"),
                createdAt = Match.DateTime("2024-01-15T10:30:00Z", "yyyy-MM-dd'T'HH:mm:ss'Z'")
            });

        // ✅ ACT: Ejecutar contra mock server
        await _pact.VerifyAsync(async ctx =>
        {
            var client = new HttpClient
            {
                BaseAddress = new Uri($"http://localhost:{_mockServerPort}")
            };
            client.DefaultRequestHeaders.Add("Authorization", "Bearer token123");

            var response = await client.GetAsync("/api/v1/orders/550e8400-e29b-41d4-a716-446655440000");

            // ✅ ASSERT: Validar respuesta
            Assert.Equal(HttpStatusCode.OK, response.StatusCode);

            var content = await response.Content.ReadAsStringAsync();
            var order = JsonSerializer.Deserialize<OrderDto>(content);

            Assert.NotNull(order);
            Assert.Equal("550e8400-e29b-41d4-a716-446655440000", order.Id.ToString());
            Assert.StartsWith("ORD-", order.OrderNumber);
        });
    }

    [Fact]
    public async Task GetOrder_WhenOrderNotFound_Returns404()
    {
        _pact
            .UponReceiving("A GET request for a non-existent order")
            .Given("Order 999e8400-e29b-41d4-a716-446655440000 does not exist")
            .WithRequest(HttpMethod.Get, "/api/v1/orders/999e8400-e29b-41d4-a716-446655440000")
            .WithHeader("Authorization", Match.Regex("Bearer .*", "Bearer token123"))
            .WillRespond()
            .WithStatus(404)
            .WithHeader("Content-Type", "application/problem+json")
            .WithJsonBody(new
            {
                type = Match.Type("https://api.talma.com/errors/not-found"),
                title = Match.Type("Order not found"),
                status = Match.Integer(404),
                detail = Match.Type("Order with ID 999e8400-e29b-41d4-a716-446655440000 does not exist"),
                instance = Match.Type("/api/v1/orders/999e8400-e29b-41d4-a716-446655440000")
            });

        await _pact.VerifyAsync(async ctx =>
        {
            var client = new HttpClient
            {
                BaseAddress = new Uri($"http://localhost:{_mockServerPort}")
            };
            client.DefaultRequestHeaders.Add("Authorization", "Bearer token123");

            var response = await client.GetAsync("/api/v1/orders/999e8400-e29b-41d4-a716-446655440000");

            Assert.Equal(HttpStatusCode.NotFound, response.StatusCode);
        });
    }

    [Fact]
    public async Task CreateOrder_WithValidRequest_ReturnsCreatedOrder()
    {
        var requestBody = new
        {
            customerId = "3fa85f64-5717-4562-b3fc-2c963f66afa6",
            items = new[]
            {
                new
                {
                    productId = "5fa85f64-5717-4562-b3fc-2c963f66afa6",
                    quantity = 2,
                    unitPrice = 99.99
                }
            },
            shippingAddress = new
            {
                street = "Av. Principal 123",
                city = "Lima",
                country = "PE",
                postalCode = "15001"
            }
        };

        _pact
            .UponReceiving("A POST request to create an order")
            .Given("Customer 3fa85f64-5717-4562-b3fc-2c963f66afa6 exists")
            .WithRequest(HttpMethod.Post, "/api/v1/orders")
            .WithHeader("Content-Type", "application/json")
            .WithHeader("Authorization", Match.Regex("Bearer .*", "Bearer token123"))
            .WithJsonBody(requestBody)
            .WillRespond()
            .WithStatus(201)
            .WithHeader("Content-Type", "application/json")
            .WithHeader("Location", Match.Regex("/api/v1/orders/.*", "/api/v1/orders/550e8400-e29b-41d4-a716-446655440000"))
            .WithJsonBody(new
            {
                id = Match.Type("550e8400-e29b-41d4-a716-446655440000"),
                orderNumber = Match.Regex("ORD-2024-001234", "^ORD-\\d{4}-\\d{6}$"),
                customerId = Match.Type("3fa85f64-5717-4562-b3fc-2c963f66afa6"),
                totalAmount = Match.Decimal(199.98),
                status = Match.Type("Pending"),
                createdAt = Match.DateTime("2024-01-15T10:30:00Z")
            });

        await _pact.VerifyAsync(async ctx =>
        {
            var client = new HttpClient
            {
                BaseAddress = new Uri($"http://localhost:{_mockServerPort}")
            };
            client.DefaultRequestHeaders.Add("Authorization", "Bearer token123");

            var content = new StringContent(
                JsonSerializer.Serialize(requestBody),
                Encoding.UTF8,
                "application/json"
            );

            var response = await client.PostAsync("/api/v1/orders", content);

            Assert.Equal(HttpStatusCode.Created, response.StatusCode);
            Assert.NotNull(response.Headers.Location);
        });
    }

    public void Dispose()
    {
        // ✅ Genera archivo pact en /pacts/OrdersWebApp-OrdersAPI.json
    }
}

// Archivo generado: pacts/OrdersWebApp-OrdersAPI.json
// {
//   "consumer": { "name": "OrdersWebApp" },
//   "provider": { "name": "OrdersAPI" },
//   "interactions": [
//     {
//       "description": "A GET request for an existing order",
//       "providerStates": [
//         { "name": "Order 550e8400-e29b-41d4-a716-446655440000 exists" }
//       ],
//       "request": {
//         "method": "GET",
//         "path": "/api/v1/orders/550e8400-e29b-41d4-a716-446655440000",
//         "headers": { "Authorization": "Bearer token123" }
//       },
//       "response": {
//         "status": 200,
//         "headers": { "Content-Type": "application/json" },
//         "body": { ... }
//       }
//     }
//   ],
//   "metadata": { "pactSpecification": { "version": "3.0.0" } }
// }
```

### Provider Test - Verificar Cumplimiento

```csharp
// OrdersAPI.Tests/OrderApiProviderTests.cs
using PactNet.Verifier;
using Microsoft.AspNetCore.Mvc.Testing;

public class OrderApiProviderTests : IDisposable
{
    private readonly WebApplicationFactory<Program> _factory;
    private readonly PactVerifier _verifier;

    public OrderApiProviderTests()
    {
        _factory = new WebApplicationFactory<Program>();

        var config = new PactVerifierConfig
        {
            Outputters = new List<IOutput>
            {
                new XUnitOutput(_output)
            },
            LogLevel = PactLogLevel.Debug
        };

        _verifier = new PactVerifier(config);
    }

    [Fact]
    public void EnsureProviderHonorsContractWithConsumer()
    {
        // ✅ Configurar provider states
        var stateHandlers = new Dictionary<string, Action>
        {
            ["Order 550e8400-e29b-41d4-a716-446655440000 exists"] = () =>
            {
                // Setup: Crear orden en DB de test
                using var scope = _factory.Services.CreateScope();
                var dbContext = scope.ServiceProvider.GetRequiredService<OrdersDbContext>();

                dbContext.Orders.Add(new Order
                {
                    Id = Guid.Parse("550e8400-e29b-41d4-a716-446655440000"),
                    OrderNumber = "ORD-2024-001234",
                    CustomerId = Guid.Parse("3fa85f64-5717-4562-b3fc-2c963f66afa6"),
                    TotalAmount = 299.99m,
                    Status = OrderStatus.Pending,
                    CreatedAt = DateTime.Parse("2024-01-15T10:30:00Z")
                });

                dbContext.SaveChanges();
            },

            ["Order 999e8400-e29b-41d4-a716-446655440000 does not exist"] = () =>
            {
                // Setup: Asegurar que orden no existe
                using var scope = _factory.Services.CreateScope();
                var dbContext = scope.ServiceProvider.GetRequiredService<OrdersDbContext>();

                var order = dbContext.Orders.Find(
                    Guid.Parse("999e8400-e29b-41d4-a716-446655440000")
                );

                if (order != null)
                    dbContext.Orders.Remove(order);

                dbContext.SaveChanges();
            },

            ["Customer 3fa85f64-5717-4562-b3fc-2c963f66afa6 exists"] = () =>
            {
                // Setup: Crear customer en DB de test
                using var scope = _factory.Services.CreateScope();
                var dbContext = scope.ServiceProvider.GetRequiredService<OrdersDbContext>();

                dbContext.Customers.Add(new Customer
                {
                    Id = Guid.Parse("3fa85f64-5717-4562-b3fc-2c963f66afa6"),
                    Name = "John Doe",
                    Email = "john@example.com"
                });

                dbContext.SaveChanges();
            }
        };

        // ✅ Verificar contrato desde archivo local
        _verifier
            .WithHttpEndpoint(new Uri("http://localhost:5000"))
            .WithFileSource(new FileInfo("../../../pacts/OrdersWebApp-OrdersAPI.json"))
            .WithProviderStateUrl(new Uri("http://localhost:5000/pact-provider-states"))
            .WithRequestFilter(req =>
            {
                // ✅ Agregar headers necesarios (autenticación, etc.)
                req.Headers.Add("X-Test-Mode", "true");
            })
            .Verify();
    }

    [Fact]
    public void EnsureProviderHonorsContractFromBroker()
    {
        // ✅ Verificar contrato desde Pact Broker
        _verifier
            .WithHttpEndpoint(new Uri("http://localhost:5000"))
            .WithPactBrokerSource(new Uri("https://pact-broker.talma.com"), options =>
            {
                options
                    .ConsumerVersionSelectors(
                        new ConsumerVersionSelector { MainBranch = true },
                        new ConsumerVersionSelector { DeployedOrReleased = true }
                    )
                    .ProviderVersion("1.2.3")
                    .ProviderBranch("main")
                    .PublishResults(true, "1.2.3");
            })
            .Verify();
    }

    public void Dispose()
    {
        _factory.Dispose();
    }
}

// Endpoint de provider states en API
[ApiController]
[Route("pact-provider-states")]
public class PactProviderStatesController : ControllerBase
{
    [HttpPost]
    public IActionResult SetupState([FromBody] ProviderStateRequest request)
    {
        switch (request.State)
        {
            case "Order 550e8400-e29b-41d4-a716-446655440000 exists":
                // Setup state
                return Ok();

            case "Order 999e8400-e29b-41d4-a716-446655440000 does not exist":
                // Setup state
                return Ok();

            default:
                return BadRequest($"Unknown state: {request.State}");
        }
    }
}

public record ProviderStateRequest
{
    public string State { get; init; }
    public Dictionary<string, object>? Params { get; init; }
}
```

### Pact Broker - Publicación de Contratos

```yaml
# docker-compose.yml - Pact Broker local
version: "3.8"

services:
  pact-broker:
    image: pactfoundation/pact-broker:2.107.1
    ports:
      - "9292:9292"
    environment:
      PACT_BROKER_DATABASE_URL: postgresql://postgres:password@postgres/pact_broker
      PACT_BROKER_BASIC_AUTH_USERNAME: pact_broker
      PACT_BROKER_BASIC_AUTH_PASSWORD: pact_broker
      PACT_BROKER_ALLOW_PUBLIC_READ: "true"
    depends_on:
      - postgres

  postgres:
    image: postgres:14
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
      POSTGRES_DB: pact_broker
    volumes:
      - pact-broker-db:/var/lib/postgresql/data

volumes:
  pact-broker-db:
```

### CI/CD - Publicar Contratos

```yaml
# .github/workflows/contract-tests.yml
name: Contract Tests

on:
  push:
    branches: [main, develop]
  pull_request:

jobs:
  consumer-tests:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Setup .NET
        uses: actions/setup-dotnet@v4
        with:
          dotnet-version: "8.0.x"

      - name: Run consumer tests
        run: dotnet test OrdersConsumer.Tests/OrdersConsumer.Tests.csproj

      - name: Publish pacts to broker
        run: |
          dotnet tool install --global pact-cli
          pact publish \
            OrdersConsumer.Tests/pacts \
            --consumer-app-version ${{ github.sha }} \
            --branch ${{ github.ref_name }} \
            --broker-base-url https://pact-broker.talma.com \
            --broker-username ${{ secrets.PACT_BROKER_USERNAME }} \
            --broker-password ${{ secrets.PACT_BROKER_PASSWORD }}

  provider-tests:
    runs-on: ubuntu-latest
    needs: consumer-tests

    steps:
      - uses: actions/checkout@v4

      - name: Setup .NET
        uses: actions/setup-dotnet@v4
        with:
          dotnet-version: "8.0.x"

      - name: Run provider tests
        run: dotnet test OrdersAPI.Tests/OrdersAPI.Tests.csproj
        env:
          PACT_BROKER_BASE_URL: https://pact-broker.talma.com
          PACT_BROKER_USERNAME: ${{ secrets.PACT_BROKER_USERNAME }}
          PACT_BROKER_PASSWORD: ${{ secrets.PACT_BROKER_PASSWORD }}

      - name: Can I deploy?
        run: |
          pact can-i-deploy \
            --pacticipant OrdersAPI \
            --version ${{ github.sha }} \
            --to-environment production \
            --broker-base-url https://pact-broker.talma.com
```

---

## Requisitos Técnicos

### MUST (Obligatorio)

- **MUST** escribir contract tests en el lado del consumidor
- **MUST** verificar contratos en el lado del proveedor
- **MUST** publicar contratos a Pact Broker centralizado
- **MUST** ejecutar contract tests en CI/CD antes de deploy
- **MUST** usar matchers de Pact (Type, Regex, DateTime) en vez de valores exactos
- **MUST** definir provider states para setup de datos de test
- **MUST** verificar todos los códigos de estado (200, 404, 400, etc.)
- **MUST** validar estructura de response bodies (RFC 7807 para errores)
- **MUST** bloquear deploy si contract tests fallan

### SHOULD (Fuertemente recomendado)

- **SHOULD** usar PactNet para proyectos .NET
- **SHOULD** publicar contratos en cada commit a main
- **SHOULD** verificar contratos contra versiones deployed del proveedor
- **SHOULD** usar `can-i-deploy` antes de deployar a producción
- **SHOULD** versionado semántico para contratos
- **SHOULD** documentar provider states requeridos
- **SHOULD** ejecutar consumer tests contra mock server local

### MAY (Opcional)

- **MAY** usar Pact Broker Webhooks para notificaciones
- **MAY** integrar con Slack para notificaciones de breaking changes
- **MAY** generar documentación de APIs desde contratos Pact

### MUST NOT (Prohibido)

- **MUST NOT** deployar breaking changes sin verificar impacto en consumidores
- **MUST NOT** hardcodear valores específicos en expectations (usar matchers)
- **MUST NOT** compartir estado entre tests de contrato
- **MUST NOT** verificar contratos solo manualmente

---

## Referencias

- [Lineamiento: APIs y Contratos](../../lineamientos/arquitectura/07-apis-y-contratos.md)
- Estándares relacionados:
  - [Estándares REST](../apis/api-rest-standards.md)
  - [Versionado de APIs](../apis/api-versioning.md)
  - [Retrocompatibilidad](../apis/api-backward-compatibility.md)
- Especificaciones:
  - [Pact Specification](https://github.com/pact-foundation/pact-specification)
  - [PactNet Documentation](https://github.com/pact-foundation/pact-net)
  - [Consumer-Driven Contracts](https://martinfowler.com/articles/consumerDrivenContracts.html)
