---
id: contract-validation
sidebar_position: 7
title: Validación de Contratos API
description: Validación de contratos API con OpenAPI spec, JSON Schema, tests de contrato con Pact y validación automatizada en CI/CD
---

# Estándar Técnico — Validación de Contratos API

---

## 1. Propósito

Garantizar compatibilidad entre productor y consumidor mediante validación automatizada de contratos API con OpenAPI 3.1+, JSON Schema Draft 2020-12, tests de contrato con Pact, y validación en CI/CD para prevenir breaking changes.

---

## 2. Alcance

**Aplica a:**

- Contratos entre microservicios (producer-consumer)
- APIs REST públicas y privadas
- Validación request/response contra schema
- Tests de compatibilidad backward/forward
- Detección de breaking changes en CI/CD

**No aplica a:**

- APIs internas experimentales (sin contrato formal)
- Protocolos no HTTP (gRPC usa protobuf validation)
- Validación de lógica de negocio (no estructura)

---

## 3. Tecnologías Aprobadas

| Componente             | Tecnología                     | Versión mínima | Observaciones                 |
| ---------------------- | ------------------------------ | -------------- | ----------------------------- |
| **Especificación**     | OpenAPI                        | 3.1+           | Contrato formal de API        |
| **Validación Schema**  | JSON Schema                    | Draft 2020-12  | Validación estructura JSON    |
| **Contract Testing**   | Pact                           | 9.0+           | Tests consumer-driven         |
| **Validación Runtime** | Swashbuckle.AspNetCore.Filters | 7.0+           | Validación automática         |
| **Breaking Changes**   | Optic                          | -              | Detección de breaking changes |
| **CI/CD Validation**   | oasdiff                        | -              | Comparación de specs          |

> El uso de tecnologías no listadas requiere aprobación de Arquitectura.

---

## 4. Requisitos Obligatorios 🔴

### OpenAPI Contract

- [ ] Spec OpenAPI 3.1+ versionado en Git
- [ ] Schemas para todos los DTOs con validaciones
- [ ] Tipos de datos explícitos: `type`, `format`, `pattern`
- [ ] Restricciones: `minLength`, `maxLength`, `minimum`, `maximum`
- [ ] Campos obligatorios: `required` array
- [ ] Enumeraciones: `enum` para valores fijos
- [ ] Ejemplos válidos en todos los schemas
- [ ] Versionado semántico de contrato (1.0.0, 1.1.0, 2.0.0)

### Validación Runtime

- [ ] Validación automática de request contra schema
- [ ] Validación automática de response contra schema (en dev/staging)
- [ ] Retornar 400 Bad Request con detalles de validación
- [ ] Status code 422 Unprocessable Entity para errores semánticos
- [ ] Validación de Content-Type: `application/json`
- [ ] Validación de Accept header

### Contract Testing

- [ ] Tests Pact para cada consumer
- [ ] Publicar contratos Pact a Pact Broker
- [ ] Verificación del productor contra contratos
- [ ] Tests ejecutados en CI/CD
- [ ] Bloqueo de deploy si tests fallan

### Detección Breaking Changes

- [ ] Validación de backward compatibility en CI/CD
- [ ] Bloqueo de PR con breaking changes no versionados
- [ ] Changelog automático de cambios en contrato
- [ ] Incremento de versión major para breaking changes
- [ ] Incremento de versión minor para nuevos endpoints/fields

### Documentación de Contrato

- [ ] README con guía de uso del contrato
- [ ] Ejemplos de request/response válidos
- [ ] Documentación de breaking changes en releases

---

## 5. Prohibiciones

- ❌ Modificar contrato sin validación automatizada
- ❌ Breaking changes sin incremento de versión major
- ❌ Schemas sin validaciones (`type: object` genérico)
- ❌ Ejemplos inválidos en schema
- ❌ Deploy sin verificar compatibilidad backward
- ❌ Omitir tests de contrato en CI/CD

---

## 6. Configuración Mínima

### OpenAPI Schema con validaciones

```yaml
openapi: 3.1.0
info:
  title: Users API
  version: 1.2.0
components:
  schemas:
    CreateUserRequest:
      type: object
      required:
        - email
        - firstName
        - lastName
      properties:
        email:
          type: string
          format: email
          pattern: '^[a-zA-Z0-9._%+-]+@talma\.com$'
          maxLength: 100
          example: juan.perez@talma.com
        firstName:
          type: string
          minLength: 2
          maxLength: 50
          pattern: '^[a-zA-Z\s]+$'
          example: Juan
        lastName:
          type: string
          minLength: 2
          maxLength: 50
          pattern: '^[a-zA-Z\s]+$'
          example: Pérez
        age:
          type: integer
          minimum: 18
          maximum: 120
          example: 30
        role:
          type: string
          enum: [Developer, Manager, Admin]
          example: Developer
      additionalProperties: false
```

### Validación Runtime con Swashbuckle

```csharp
// Program.cs
using Microsoft.AspNetCore.Mvc;

builder.Services.AddControllers()
    .AddJsonOptions(options =>
    {
        options.JsonSerializerOptions.PropertyNamingPolicy = JsonNamingPolicy.CamelCase;
    });

builder.Services.Configure<ApiBehaviorOptions>(options =>
{
    options.InvalidModelStateResponseFactory = context =>
    {
        var errors = context.ModelState
            .Where(e => e.Value.Errors.Count > 0)
            .Select(e => new
            {
                field = e.Key,
                errors = e.Value.Errors.Select(x => x.ErrorMessage).ToArray()
            });

        return new BadRequestObjectResult(new
        {
            type = "https://docs.talma.com/errors/validation",
            title = "Validation Error",
            status = 400,
            errors = errors
        });
    };
});
```

### Contract Testing con Pact

```csharp
// Consumer test (servicio consumidor)
using PactNet;
using PactNet.Infrastructure.Outputters;
using Xunit;

public class UsersApiConsumerTests : IClassFixture<PactFixture>
{
    private readonly IPactBuilderV3 _pact;

    public UsersApiConsumerTests(PactFixture fixture)
    {
        _pact = Pact.V3("UserService", "UsersApi", new PactConfig())
            .WithHttpInteractions();
    }

    [Fact]
    public async Task GetUser_WhenUserExists_ReturnsUser()
    {
        // Arrange
        _pact
            .UponReceiving("A request to get user by ID")
            .Given("User 123 exists")
            .WithRequest(HttpMethod.Get, "/api/v1/users/123")
            .WithHeader("Accept", "application/json")
            .WillRespond()
            .WithStatus(200)
            .WithHeader("Content-Type", "application/json")
            .WithJsonBody(new
            {
                id = "123",
                email = "juan.perez@talma.com",
                firstName = "Juan",
                lastName = "Pérez"
            });

        await _pact.VerifyAsync(async ctx =>
        {
            var client = new HttpClient { BaseAddress = ctx.MockServerUri };
            var response = await client.GetAsync("/api/v1/users/123");

            Assert.Equal(HttpStatusCode.OK, response.StatusCode);
            var user = await response.Content.ReadFromJsonAsync<UserDto>();
            Assert.Equal("juan.perez@talma.com", user.Email);
        });
    }
}
```

```csharp
// Provider verification (servicio productor)
using PactNet.Infrastructure.Outputters;
using PactNet.Verifier;
using Xunit;

public class UsersApiProviderTests
{
    [Fact]
    public void EnsureProviderHonorsConsumerContracts()
    {
        var config = new PactVerifierConfig
        {
            Outputters = new[] { new XUnitOutput(_output) }
        };

        new PactVerifier(config)
            .WithHttpEndpoint(new Uri("http://localhost:5000"))
            .WithPactBrokerSource(new Uri("https://pact-broker.talma.com"), options =>
            {
                options.TokenAuthentication("YOUR_PACT_BROKER_TOKEN");
            })
            .WithProviderStateUrl(new Uri("http://localhost:5000/provider-states"))
            .Verify();
    }
}
```

### Detección Breaking Changes en CI/CD

```yaml
# .github/workflows/contract-validation.yml
name: Contract Validation

on:
  pull_request:
    paths:
      - "swagger.json"
      - "src/**/*.cs"

jobs:
  validate-contract:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0

      - name: Get base spec
        run: |
          git show origin/main:swagger.json > base-swagger.json

      - name: Generate current spec
        run: |
          dotnet build
          dotnet run --urls http://localhost:5000 &
          sleep 5
          curl http://localhost:5000/swagger/v1/swagger.json > current-swagger.json

      - name: Check breaking changes
        run: |
          docker run --rm -v ${PWD}:/specs openapitools/openapi-diff \
            /specs/base-swagger.json /specs/current-swagger.json \
            --fail-on-incompatible

      - name: Run Pact tests
        run: |
          dotnet test --filter Category=ContractTest

      - name: Publish to Pact Broker
        if: success()
        run: |
          docker run --rm \
            -e PACT_BROKER_BASE_URL=https://pact-broker.talma.com \
            -e PACT_BROKER_TOKEN=${{ secrets.PACT_BROKER_TOKEN }} \
            -v ${PWD}/pacts:/pacts \
            pactfoundation/pact-cli publish /pacts \
            --consumer-app-version ${{ github.sha }}
```

---

## 7. Ejemplos

### Schema con validaciones complejas

```yaml
components:
  schemas:
    OrderRequest:
      type: object
      required:
        - customerId
        - items
        - shippingAddress
      properties:
        customerId:
          type: string
          format: uuid
          example: 550e8400-e29b-41d4-a716-446655440000
        items:
          type: array
          minItems: 1
          maxItems: 50
          items:
            $ref: "#/components/schemas/OrderItem"
        shippingAddress:
          $ref: "#/components/schemas/Address"
        specialInstructions:
          type: string
          maxLength: 500
          nullable: true

    OrderItem:
      type: object
      required:
        - productId
        - quantity
      properties:
        productId:
          type: string
          format: uuid
        quantity:
          type: integer
          minimum: 1
          maximum: 999
        unitPrice:
          type: number
          format: double
          minimum: 0.01
          multipleOf: 0.01

    Address:
      type: object
      required:
        - street
        - city
        - country
        - postalCode
      properties:
        street:
          type: string
          minLength: 5
          maxLength: 100
        city:
          type: string
          minLength: 2
          maxLength: 50
        country:
          type: string
          enum: [PE, CL, CO, MX]
        postalCode:
          type: string
          pattern: '^\d{5}$'
```

### Validación personalizada

```csharp
// Custom validator
public class CreateOrderRequestValidator : AbstractValidator<CreateOrderRequest>
{
    public CreateOrderRequestValidator()
    {
        RuleFor(x => x.CustomerId)
            .NotEmpty()
            .Must(BeValidGuid).WithMessage("CustomerId debe ser un GUID válido");

        RuleFor(x => x.Items)
            .NotEmpty().WithMessage("Debe incluir al menos un item")
            .Must(items => items.Count <= 50).WithMessage("Máximo 50 items por orden");

        RuleForEach(x => x.Items).SetValidator(new OrderItemValidator());

        RuleFor(x => x.ShippingAddress).SetValidator(new AddressValidator());
    }

    private bool BeValidGuid(string guid) => Guid.TryParse(guid, out _);
}
```

---

## 8. Validación y Auditoría

```bash
# Validar spec OpenAPI
docker run --rm -v ${PWD}:/local openapitools/openapi-generator-cli validate \
  -i /local/swagger.json

# Comparar specs para breaking changes
docker run --rm -v ${PWD}:/specs openapitools/openapi-diff \
  /specs/v1.0.0-swagger.json /specs/v1.1.0-swagger.json

# Ejecutar tests de contrato
dotnet test --filter Category=ContractTest

# Verificar provider contra Pact Broker
pact-provider-verifier \
  --provider-base-url http://localhost:5000 \
  --pact-broker-url https://pact-broker.talma.com \
  --provider UsersApi
```

**Métricas de cumplimiento:**

| Métrica                     | Umbral           | Verificación                               |
| --------------------------- | ---------------- | ------------------------------------------ |
| Schemas con validaciones    | 100%             | Verificar `required`, `pattern`, `min/max` |
| Tests de contrato passing   | 100%             | CI/CD status                               |
| Breaking changes bloqueados | 0 en minor/patch | oasdiff en CI                              |
| Coverage de contratos       | >90% endpoints   | Pact Broker metrics                        |
| Tiempo validación CI        | <5 min           | Pipeline duration                          |

---

## 9. Referencias

- [OpenAPI 3.1 Schema Object](https://spec.openapis.org/oas/v3.1.0#schema-object)
- [JSON Schema 2020-12](https://json-schema.org/draft/2020-12/json-schema-validation.html)
- [Pact Documentation](https://docs.pact.io/)
- [Consumer-Driven Contracts](https://martinfowler.com/articles/consumerDrivenContracts.html)
- [OpenAPI Diff](https://github.com/OpenAPITools/openapi-diff)
- [Optic - API Change Management](https://www.useoptic.com/)
- [Azure API Breaking Change Detection](https://azure.github.io/azure-api-style-guide/)
