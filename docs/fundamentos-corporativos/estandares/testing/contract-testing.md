---
id: contract-testing
sidebar_position: 3
title: Contract Testing
description: Estándar para pruebas de contrato con Pact.io, validando integración entre microservicios sin comunicación real
---

# Estándar Técnico — Contract Testing

---

## 1. Propósito

Garantizar compatibilidad entre microservicios (consumer-provider) mediante Pact.io, generando contratos en tests de consumer, validándolos en provider, y detectando breaking changes antes de deployment.

---

## 2. Alcance

**Aplica a:**

- Integración entre microservicios REST
- APIs REST consumidas por otros equipos
- Servicios con múltiples consumers
- Evoluciones de API con versionado

**No aplica a:**

- APIs externas de terceros (usar mocks)
- Integración con UI (usar E2E tests)
- Mensajería asíncrona Kafka (usar schema validation separado)

---

## 3. Tecnologías Aprobadas

| Componente      | Tecnología       | Versión mínima | Observaciones            |
| --------------- | ---------------- | -------------- | ------------------------ |
| **Framework**   | PactNet          | 5.0+           | Pact para .NET           |
| **Broker**      | Pact Broker      | 2.100+         | Repositorio de contratos |
| **CI/CD**       | GitHub Actions   | -              | Validación automática    |
| **Assertions**  | FluentAssertions | 6.12+          | Validaciones expresivas  |
| **HTTP Client** | HttpClient       | .NET 8+        | Consumer tests           |

> El uso de tecnologías no listadas requiere aprobación de Arquitectura.

---

## 4. Requisitos Obligatorios 🔴

### Consumer Side

- [ ] **Tests de consumer** generan contratos Pact
- [ ] **Contratos publicados** en Pact Broker
- [ ] **Versionado** con tags (branch, version)
- [ ] **CI/CD** ejecuta tests de consumer antes de merge

### Provider Side

- [ ] **Verificación de contratos** contra API real
- [ ] **Provider states** implementados para diferentes escenarios
- [ ] **Validación en CI/CD** antes de deployment
- [ ] **Can-I-Deploy** obligatorio antes de prod

### Workflow

- [ ] **Consumer**: Genera contrato en test → Publica a Broker
- [ ] **Provider**: Descarga contratos → Verifica contra API → Publica resultado
- [ ] **Deployment**: Can-I-Deploy check antes de prod

---

## 5. Consumer Tests - Generar Contrato

### .NET - PactNet (Consumer)

```csharp
// Tests/PaymentServiceConsumerTests.cs
using PactNet;
using PactNet.Matchers;
using Xunit;

public class PaymentServiceConsumerTests : IDisposable
{
    private readonly IPactBuilderV4 _pactBuilder;
    private readonly string _providerName = "payment-api";
    private readonly string _consumerName = "order-api";

    public PaymentServiceConsumerTests()
    {
        var pactConfig = new PactConfig
        {
            PactDir = "../../../pacts",  // Directorio de contratos
            DefaultJsonSettings = new JsonSerializerSettings
            {
                ContractResolver = new CamelCasePropertyNamesContractResolver()
            }
        };

        _pactBuilder = Pact.V4(_consumerName, _providerName, pactConfig).WithHttpInteractions();
    }

    [Fact]
    public async Task CreatePayment_ShouldReturnPaymentId()
    {
        // Arrange: Definir contrato esperado
        _pactBuilder
            .UponReceiving("a request to create payment")
                .WithRequest(HttpMethod.Post, "/api/payments")
                .WithHeader("Content-Type", "application/json")
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

        // Act: Ejecutar request contra mock
        await _pactBuilder.VerifyAsync(async ctx =>
        {
            var client = new HttpClient { BaseAddress = ctx.MockServerUri };
            var request = new
            {
                orderId = "ord-123",
                amount = 100.50m,
                currency = "USD"
            };

            var response = await client.PostAsJsonAsync("/api/payments", request);

            // Assert
            response.StatusCode.Should().Be(HttpStatusCode.Created);
            var payment = await response.Content.ReadFromJsonAsync<PaymentResponse>();
            payment.PaymentId.Should().NotBeNullOrEmpty();
            payment.Status.Should().BeOneOf("pending", "completed", "failed");
        });

        // Contrato generado automáticamente en pacts/order-api-payment-api.json
    }

    [Fact]
    public async Task GetPayment_ShouldReturnPaymentDetails()
    {
        _pactBuilder
            .UponReceiving("a request to get payment by ID")
                .WithRequest(HttpMethod.Get, "/api/payments/pay-456")
                .WithHeader("Authorization", Match.Regex("Bearer token123", "^Bearer .+$"))
            .WillRespond()
                .WithStatus(200)
                .WithJsonBody(new
                {
                    paymentId = "pay-456",
                    amount = 100.50m,
                    status = "completed"
                });

        await _pactBuilder.VerifyAsync(async ctx =>
        {
            var client = new HttpClient { BaseAddress = ctx.MockServerUri };
            client.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", "token123");

            var response = await client.GetAsync("/api/payments/pay-456");

            response.StatusCode.Should().Be(HttpStatusCode.OK);
        });
    }

    public void Dispose()
    {
        // Pact file generado en Dispose
    }
}
```

---

## 6. Provider Verification - Validar Contrato

### .NET - PactNet (Provider)

```csharp
// Tests/PaymentApiProviderTests.cs
using PactNet.Verifier;
using Xunit;

public class PaymentApiProviderTests
{
    [Fact]
    public void EnsurePaymentApiHonoursPactWithOrderApi()
    {
        // Arrange: Configurar provider
        var config = new PactVerifierConfig
        {
            Outputters = new List<IOutput>
            {
                new XUnitOutput(_output)
            }
        };

        var pactVerifier = new PactVerifier(config);

        // Act: Verificar contratos desde Pact Broker
        pactVerifier
            .ServiceProvider("payment-api", new Uri("http://localhost:5000"))  // API real
            .WithPactBrokerSource(new Uri("https://pact-broker.company.com"), options =>
            {
                options.ConsumerVersionSelectors(new ConsumerVersionSelector
                {
                    Branch = "main",
                    Latest = true
                });
                options.ProviderVersionBranch("main");
                options.ProviderVersion("1.2.3");
                options.PublishResults = true;  // Publicar resultados a broker
            })
            .WithProviderStateUrl(new Uri("http://localhost:5000/provider-states"))  // Setup states
            .Verify();
    }
}

// Controllers/ProviderStatesController.cs
[ApiController]
[Route("provider-states")]
public class ProviderStatesController : ControllerBase
{
    private readonly PaymentDbContext _dbContext;

    [HttpPost]
    public IActionResult SetupProviderState([FromBody] ProviderState state)
    {
        // Setup state para tests
        switch (state.State)
        {
            case "payment pay-456 exists":
                _dbContext.Payments.Add(new Payment
                {
                    Id = "pay-456",
                    Amount = 100.50m,
                    Status = "completed"
                });
                _dbContext.SaveChanges();
                break;

            case "no payments exist":
                _dbContext.Payments.RemoveRange(_dbContext.Payments);
                _dbContext.SaveChanges();
                break;

            default:
                return BadRequest($"Unknown state: {state.State}");
        }

        return Ok();
    }
}
```

---

## 7. Pact Broker - Repositorio de Contratos

### Docker Compose - Pact Broker Local

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

### Publicar Contrato al Broker

```bash
# Publicar contrato generado
docker run --rm -v $(pwd)/pacts:/pacts \
  pactfoundation/pact-cli:latest \
  publish /pacts \
  --consumer-app-version=1.0.0 \
  --broker-base-url=https://pact-broker.company.com \
  --broker-username=pact \
  --broker-password=pact123 \
  --branch=main \
  --tag=dev
```

---

## 8. CI/CD Integration

### GitHub Actions - Consumer

```yaml
# .github/workflows/contract-tests.yml
name: Contract Tests (Consumer)

on:
  pull_request:
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
            --branch=${{ github.head_ref }}
```

### GitHub Actions - Provider

```yaml
# .github/workflows/provider-verification.yml
name: Provider Verification

on:
  push:
    branches: [main]

jobs:
  verify-contracts:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Start API
        run: |
          dotnet run --project PaymentApi &
          sleep 10  # Esperar inicio

      - name: Verify Pacts
        run: dotnet test Tests/ProviderTests.csproj
        env:
          PACT_BROKER_URL: ${{ secrets.PACT_BROKER_URL }}
          PACT_BROKER_TOKEN: ${{ secrets.PACT_BROKER_TOKEN }}
```

---

## 9. Can-I-Deploy

```bash
# Verificar si es seguro deployar
docker run --rm pactfoundation/pact-cli:latest \
  can-i-deploy \
  --pacticipant payment-api \
  --version 1.2.3 \
  --to-environment production \
  --broker-base-url https://pact-broker.company.com \
  --broker-token $PACT_BROKER_TOKEN

# Output:
# Computer says yes \o/
#
# CONSUMER       | C.VERSION | PROVIDER    | P.VERSION | SUCCESS?
# -------------- | --------- | ----------- | --------- | --------
# order-api      | 2.1.0     | payment-api | 1.2.3     | true
```

---

## 10. Validación de Cumplimiento

```bash
# Verificar contratos publicados
curl -u pact:pact123 https://pact-broker.company.com/pacts/provider/payment-api/consumer/order-api/latest

# Verificar verification results
curl -u pact:pact123 https://pact-broker.company.com/pacts/provider/payment-api/latest/verification-results

# Listar todos los contratos
curl -u pact:pact123 https://pact-broker.company.com/pacticipants
```

---

## 11. Referencias

**Pact:**

- [Pact.io Documentation](https://docs.pact.io/)
- [PactNet GitHub](https://github.com/pact-foundation/pact-net)

**Contract Testing:**

- [Consumer-Driven Contracts](https://martinfowler.com/articles/consumerDrivenContracts.html)
- [Testing Microservices (Martin Fowler)](https://martinfowler.com/articles/microservice-testing/)
