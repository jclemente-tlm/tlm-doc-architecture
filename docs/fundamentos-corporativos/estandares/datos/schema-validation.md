---
id: schema-validation
sidebar_position: 13
title: Schema Validation
description: Estándar para validación de esquemas de datos en API requests, mensajes Kafka y persistencia usando FluentValidation
---

# Estándar Técnico — Schema Validation

---

## 1. Propósito

Garantizar integridad y calidad de datos mediante validación automática de esquemas en boundaries del sistema (APIs, eventos, persistencia), rechazando datos inválidos early y proporcionando feedback claro.

---

## 2. Alcance

**Aplica a:**

- API request/response validation
- Kafka message validation
- Database constraints
- File upload validation
- External integration inputs
- Configuration validation

**No aplica a:**

- Datos internos ya validados
- Read-only queries
- Health check endpoints

---

## 3. Tecnologías Aprobadas

| Componente          | Tecnología            | Versión mínima | Observaciones                |
| ------------------- | --------------------- | -------------- | ---------------------------- |
| **API Validation**  | FluentValidation      | 11.8+          | Preferido para .NET          |
| **Data Annotation** | System.ComponentModel | .NET 8+        | Para validaciones simples    |
| **JSON Schema**     | NJsonSchema           | 11.0+          | Validación de JSON           |
| **DB Constraints**  | PostgreSQL CHECK      | 14+            | Validación en BD             |
| **Kafka**           | Avro/Protobuf         | -              | Schema validation automática |
| **OpenAPI**         | Swashbuckle           | 6.5+           | API contract validation      |

> El uso de tecnologías no listadas requiere aprobación de Arquitectura.

---

## 4. Requisitos Obligatorios 🔴

### Validation Layers

- [ ] **API Layer:** validar inputs antes de procesar
- [ ] **Application Layer:** validar business rules
- [ ] **Domain Layer:** validar invariantes del dominio
- [ ] **Database Layer:** constraints para data integrity final
- [ ] **Event Layer:** validar mensajes con schema registry

### FluentValidation Rules

- [ ] Validators registrados en DI container
- [ ] Validación automática en controllers (filter)
- [ ] Mensajes de error descriptivos
- [ ] Reglas de negocio documentadas en validators
- [ ] Tests unitarios de validators

### Error Responses

- [ ] RFC 7807 Problem Details format
- [ ] HTTP 400 Bad Request para validation errors
- [ ] Array de errores con field names
- [ ] Mensajes user-friendly (no stack traces)
- [ ] Correlation ID para debugging

### Database Constraints

- [ ] NOT NULL para campos obligatorios
- [ ] CHECK constraints para business rules
- [ ] UNIQUE constraints para unicidad
- [ ] Foreign keys para integridad referencial
- [ ] Domain types para validación de tipos

### Performance

- [ ] Validación fail-fast (stop on first error configurable)
- [ ] Async validation solo cuando necesario
- [ ] Cache de validation rules cuando sea posible
- [ ] No validar datos ya validados (trust boundaries)

---

## 5. Prohibiciones

- ❌ Aceptar inputs sin validar
- ❌ Validación solo en frontend (trust but verify)
- ❌ Stack traces en error responses a clientes
- ❌ Mensajes de error genéricos ("Invalid input")
- ❌ Ignorar database constraints
- ❌ Validación custom sin tests
- ❌ Validación sincrónica de operaciones lentas (llamadas externas)

---

## 6. Configuración Mínima

### FluentValidation Setup

```csharp
// Program.cs
using FluentValidation;
using FluentValidation.AspNetCore;

var builder = WebApplication.CreateBuilder(args);

// Registrar FluentValidation
builder.Services.AddFluentValidationAutoValidation();
builder.Services.AddFluentValidationClientsideAdapters();
builder.Services.AddValidatorsFromAssemblyContaining<Program>();

// Configurar behavior de validación
builder.Services.AddControllers()
    .ConfigureApiBehaviorOptions(options =>
    {
        options.InvalidModelStateResponseFactory = context =>
        {
            var problemDetails = new ValidationProblemDetails(context.ModelState)
            {
                Type = "https://tools.ietf.org/html/rfc7231#section-6.5.1",
                Title = "One or more validation errors occurred.",
                Status = StatusCodes.Status400BadRequest,
                Detail = "See the errors property for details.",
                Instance = context.HttpContext.Request.Path
            };

            problemDetails.Extensions["traceId"] = context.HttpContext.TraceIdentifier;

            return new BadRequestObjectResult(problemDetails)
            {
                ContentTypes = { "application/problem+json" }
            };
        };
    });

var app = builder.Build();
app.Run();
```

### Validator Example

```csharp
// DTOs/CreateOrderRequest.cs
public record CreateOrderRequest
{
    public Guid CustomerId { get; init; }
    public List<OrderItemRequest> Items { get; init; } = new();
    public string? Notes { get; init; }
}

public record OrderItemRequest
{
    public Guid ProductId { get; init; }
    public int Quantity { get; init; }
}

// Validators/CreateOrderRequestValidator.cs
using FluentValidation;

public class CreateOrderRequestValidator : AbstractValidator<CreateOrderRequest>
{
    public CreateOrderRequestValidator()
    {
        RuleFor(x => x.CustomerId)
            .NotEmpty()
            .WithMessage("Customer ID is required");

        RuleFor(x => x.Items)
            .NotEmpty()
            .WithMessage("Order must contain at least one item")
            .Must(items => items.Count <= 100)
            .WithMessage("Order cannot contain more than 100 items");

        RuleForEach(x => x.Items)
            .SetValidator(new OrderItemRequestValidator());

        RuleFor(x => x.Notes)
            .MaximumLength(500)
            .WithMessage("Notes cannot exceed 500 characters")
            .When(x => !string.IsNullOrEmpty(x.Notes));
    }
}

public class OrderItemRequestValidator : AbstractValidator<OrderItemRequest>
{
    public OrderItemRequestValidator()
    {
        RuleFor(x => x.ProductId)
            .NotEmpty()
            .WithMessage("Product ID is required");

        RuleFor(x => x.Quantity)
            .GreaterThan(0)
            .WithMessage("Quantity must be greater than 0")
            .LessThanOrEqualTo(1000)
            .WithMessage("Quantity cannot exceed 1000 per item");
    }
}
```

### Controller with Validation

```csharp
// Controllers/OrdersController.cs
[ApiController]
[Route("api/v1/[controller]")]
public class OrdersController : ControllerBase
{
    private readonly IOrderService _orderService;
    private readonly ILogger<OrdersController> _logger;

    /// <summary>
    /// Crea una nueva orden
    /// </summary>
    /// <param name="request">Detalles de la orden</param>
    /// <returns>Orden creada</returns>
    /// <response code="201">Orden creada exitosamente</response>
    /// <response code="400">Request inválido - ver errores de validación</response>
    /// <response code="422">Business rule violation</response>
    [HttpPost]
    [ProducesResponseType(typeof(OrderDto), StatusCodes.Status201Created)]
    [ProducesResponseType(typeof(ValidationProblemDetails), StatusCodes.Status400BadRequest)]
    [ProducesResponseType(typeof(ProblemDetails), StatusCodes.Status422UnprocessableEntity)]
    public async Task<ActionResult<OrderDto>> CreateOrder(
        [FromBody] CreateOrderRequest request)
    {
        // Validación automática por FluentValidation
        // Si falla, retorna 400 con ValidationProblemDetails

        try
        {
            var command = new CreateOrderCommand
            {
                CustomerId = request.CustomerId,
                Items = request.Items.Select(i => new CreateOrderItemCommand
                {
                    ProductId = i.ProductId,
                    Quantity = i.Quantity
                }).ToList()
            };

            var order = await _orderService.CreateOrderAsync(command);
            var dto = OrderDto.FromEntity(order);

            return CreatedAtAction(
                nameof(GetOrder),
                new { id = dto.Id },
                dto);
        }
        catch (InsufficientStockException ex)
        {
            // Business rule violation (no es validation error)
            var problem = new ProblemDetails
            {
                Type = "https://api.talma.com/errors/insufficient-stock",
                Title = "Insufficient Stock",
                Status = StatusCodes.Status422UnprocessableEntity,
                Detail = ex.Message,
                Instance = HttpContext.Request.Path
            };

            problem.Extensions["productId"] = ex.ProductId.ToString();
            problem.Extensions["available"] = ex.AvailableStock;
            problem.Extensions["requested"] = ex.RequestedQuantity;

            return UnprocessableEntity(problem);
        }
    }

    [HttpGet("{id}")]
    public async Task<ActionResult<OrderDto>> GetOrder(Guid id)
    {
        var order = await _orderService.GetOrderAsync(id);

        if (order == null)
            return NotFound();

        return Ok(OrderDto.FromEntity(order));
    }
}
```

### Complex Business Validation

```csharp
// Validators/UpdateOrderStatusRequestValidator.cs
public class UpdateOrderStatusRequestValidator : AbstractValidator<UpdateOrderStatusRequest>
{
    private readonly IOrderRepository _orderRepository;

    public UpdateOrderStatusRequestValidator(IOrderRepository orderRepository)
    {
        _orderRepository = orderRepository;

        RuleFor(x => x.OrderId)
            .NotEmpty();

        RuleFor(x => x.NewStatus)
            .NotEmpty()
            .IsEnumName(typeof(OrderStatus), caseSensitive: false)
            .WithMessage("Invalid status value");

        // Business rule: solo ciertos transitions permitidos
        RuleFor(x => x)
            .MustAsync(async (request, cancellation) =>
            {
                var order = await _orderRepository.GetByIdAsync(request.OrderId);
                if (order == null)
                    return false;

                return IsValidStatusTransition(order.Status, request.NewStatus);
            })
            .WithMessage("Invalid status transition")
            .When(x => x.OrderId != Guid.Empty);

        // Async validation - verificar payment si status = PAID
        RuleFor(x => x.PaymentId)
            .NotEmpty()
            .When(x => x.NewStatus == OrderStatus.PAID)
            .WithMessage("Payment ID required when marking order as PAID");

        RuleFor(x => x.PaymentId)
            .MustAsync(async (paymentId, cancellation) =>
            {
                // Validar que payment existe y es válido
                // (ejemplo simplificado)
                return paymentId.HasValue;
            })
            .When(x => x.NewStatus == OrderStatus.PAID && x.PaymentId.HasValue)
            .WithMessage("Payment ID not found or invalid");
    }

    private bool IsValidStatusTransition(OrderStatus current, OrderStatus requested)
    {
        return (current, requested) switch
        {
            (OrderStatus.PENDING, OrderStatus.PAID) => true,
            (OrderStatus.PAID, OrderStatus.PROCESSING) => true,
            (OrderStatus.PROCESSING, OrderStatus.SHIPPED) => true,
            (OrderStatus.SHIPPED, OrderStatus.DELIVERED) => true,
            (_, OrderStatus.CANCELLED) => true,  // Cualquier estado puede cancelarse
            _ => false
        };
    }
}
```

### Database Constraints

```sql
-- Validación en BD (última línea de defensa)
CREATE TABLE orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id UUID NOT NULL,  -- NOT NULL constraint
    order_number VARCHAR(20) NOT NULL UNIQUE,  -- UNIQUE constraint
    total_amount DECIMAL(10,2) NOT NULL,
    status VARCHAR(20) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),

    -- CHECK constraints para business rules
    CONSTRAINT check_total_positive CHECK (total_amount >= 0),
    CONSTRAINT check_status_valid CHECK (
        status IN ('PENDING', 'PAID', 'PROCESSING', 'SHIPPED', 'DELIVERED', 'CANCELLED')
    )
);

-- Domain types para reutilizar validaciones
CREATE DOMAIN email AS VARCHAR(255)
CHECK (VALUE ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$');

CREATE DOMAIN phone AS VARCHAR(20)
CHECK (VALUE ~* '^\+[1-9]\d{1,14}$');  -- E.164 format

CREATE TABLE customers (
    id UUID PRIMARY KEY,
    email email NOT NULL,  -- Usando domain type
    phone phone NULL
);
```

### JSON Schema Validation

```csharp
// Para validar JSON dinámico (ej: configuraciones, metadata)
using NJsonSchema;
using NJsonSchema.Validation;

public class JsonSchemaValidator
{
    public async Task<ValidationResult> ValidateJsonAsync(string json, string schemaJson)
    {
        var schema = await JsonSchema.FromJsonAsync(schemaJson);
        var validator = new JsonSchemaValidator();

        var errors = schema.Validate(json);

        return new ValidationResult
        {
            IsValid = !errors.Any(),
            Errors = errors.Select(e => new ValidationError
            {
                Path = e.Path,
                Message = e.ToString()
            }).ToList()
        };
    }
}

// Ejemplo de uso
public class OrderMetadataValidator
{
    private readonly JsonSchemaValidator _schemaValidator;
    private const string MetadataSchema = @"
    {
      ""type"": ""object"",
      ""properties"": {
        ""source"": { ""type"": ""string"", ""enum"": [""web"", ""mobile"", ""api""] },
        ""campaign_id"": { ""type"": ""string"", ""pattern"": ""^[A-Z0-9-]+$"" },
        ""user_agent"": { ""type"": ""string"", ""maxLength"": 500 }
      },
      ""required"": [""source""],
      ""additionalProperties"": false
    }";

    public async Task<bool> ValidateMetadataAsync(string metadataJson)
    {
        var result = await _schemaValidator.ValidateJsonAsync(metadataJson, MetadataSchema);
        return result.IsValid;
    }
}
```

---

## 7. Ejemplos

### Custom Validator with External Service

```csharp
public class CreateCustomerRequestValidator : AbstractValidator<CreateCustomerRequest>
{
    private readonly ICustomerRepository _repository;

    public CreateCustomerRequestValidator(ICustomerRepository repository)
    {
        _repository = repository;

        RuleFor(x => x.Email)
            .NotEmpty()
            .EmailAddress()
            .MaximumLength(255)
            .MustAsync(async (email, cancellation) =>
            {
                var exists = await _repository.EmailExistsAsync(email);
                return !exists;
            })
            .WithMessage("Email already registered");

        RuleFor(x => x.TaxId)
            .NotEmpty()
            .Matches(@"^\d{11}$")
            .WithMessage("Tax ID must be 11 digits")
            .MustAsync(async (taxId, cancellation) =>
            {
                var exists = await _repository.TaxIdExistsAsync(taxId);
                return !exists;
            })
            .WithMessage("Tax ID already registered");
    }
}
```

### Conditional Validation

```csharp
public class PaymentRequestValidator : AbstractValidator<PaymentRequest>
{
    public PaymentRequestValidator()
    {
        RuleFor(x => x.PaymentMethod)
            .NotEmpty()
            .IsEnumName(typeof(PaymentMethod));

        // Credit card validations solo si payment method es credit card
        When(x => x.PaymentMethod == PaymentMethod.CreditCard, () =>
        {
            RuleFor(x => x.CardNumber)
                .NotEmpty()
                .CreditCard()
                .WithMessage("Invalid credit card number");

            RuleFor(x => x.CardHolderName)
                .NotEmpty()
                .MaximumLength(100);

            RuleFor(x => x.ExpiryMonth)
                .InclusiveBetween(1, 12);

            RuleFor(x => x.ExpiryYear)
                .GreaterThanOrEqualTo(DateTime.Now.Year);

            RuleFor(x => x.CVV)
                .NotEmpty()
                .Matches(@"^\d{3,4}$");
        });

        // Bank transfer validations
        When(x => x.PaymentMethod == PaymentMethod.BankTransfer, () =>
        {
            RuleFor(x => x.BankAccount)
                .NotEmpty()
                .Matches(@"^\d{10,20}$");
        });
    }
}
```

---

## 8. Validación y Auditoría

### Checklist

- [ ] FluentValidation configurado en API layer
- [ ] Validators registrados en DI
- [ ] Database constraints implementados
- [ ] Error responses en formato RFC 7807
- [ ] Tests unitarios de validators
- [ ] Schema validation en Kafka messages
- [ ] Async validations solo cuando necesario

### Métricas

```promql
# Validation errors por endpoint
rate(http_requests_total{status="400"}[5m])

# Top validation errors
topk(10, sum by (field) (validation_errors_total))
```

### Tests Unitarios

```csharp
// Tests/Validators/CreateOrderRequestValidatorTests.cs
public class CreateOrderRequestValidatorTests
{
    private readonly CreateOrderRequestValidator _validator;

    public CreateOrderRequestValidatorTests()
    {
        _validator = new CreateOrderRequestValidator();
    }

    [Fact]
    public async Task Validate_WhenCustomerIdEmpty_ShouldHaveError()
    {
        var request = new CreateOrderRequest
        {
            CustomerId = Guid.Empty,
            Items = new List<OrderItemRequest>
            {
                new() { ProductId = Guid.NewGuid(), Quantity = 1 }
            }
        };

        var result = await _validator.ValidateAsync(request);

        result.IsValid.Should().BeFalse();
        result.Errors.Should().Contain(e => e.PropertyName == "CustomerId");
    }

    [Fact]
    public async Task Validate_WhenItemsEmpty_ShouldHaveError()
    {
        var request = new CreateOrderRequest
        {
            CustomerId = Guid.NewGuid(),
            Items = new List<OrderItemRequest>()
        };

        var result = await _validator.ValidateAsync(request);

        result.IsValid.Should().BeFalse();
        result.Errors.Should().Contain(e =>
            e.PropertyName == "Items" &&
            e.ErrorMessage.Contains("at least one item"));
    }

    [Theory]
    [InlineData(0)]
    [InlineData(-1)]
    [InlineData(1001)]
    public async Task Validate_WhenQuantityInvalid_ShouldHaveError(int quantity)
    {
        var request = new CreateOrderRequest
        {
            CustomerId = Guid.NewGuid(),
            Items = new List<OrderItemRequest>
            {
                new() { ProductId = Guid.NewGuid(), Quantity = quantity }
            }
        };

        var result = await _validator.ValidateAsync(request);

        result.IsValid.Should().BeFalse();
        result.Errors.Should().Contain(e => e.PropertyName.Contains("Quantity"));
    }
}
```

---

## 9. Referencias

**Documentación:**

- [FluentValidation Documentation](https://docs.fluentvalidation.net/)
- [RFC 7807 - Problem Details](https://www.rfc-editor.org/rfc/rfc7807)
- [JSON Schema Specification](https://json-schema.org/)

**Buenas prácticas:**

- "Domain-Driven Design" - Eric Evans
- [ASP.NET Core Model Validation](https://learn.microsoft.com/en-us/aspnet/core/mvc/models/validation)
- [PostgreSQL Constraints](https://www.postgresql.org/docs/current/ddl-constraints.html)
