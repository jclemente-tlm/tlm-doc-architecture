---
id: api-contracts
sidebar_position: 2
title: Contratos de APIs
description: Definición y documentación de contratos de APIs usando OpenAPI 3.0, DTOs y FluentValidation.
tags: [apis, rest, openapi, swagger, fluent-validation, dtos]
---

# Contratos de APIs

## Contexto

Este estándar define cómo especificar formalmente endpoints, requests y responses usando OpenAPI (Swagger) con DTOs y validación. Complementa el lineamiento [APIs y Contratos](../../lineamientos/arquitectura/07-apis-y-contratos.md).

**Cuándo aplicar:** Toda API expuesta externamente o a otros equipos. Obligatorio para APIs públicas.

---

## Stack Tecnológico

| Componente        | Tecnología             | Versión | Uso                     |
| ----------------- | ---------------------- | ------- | ----------------------- |
| **Documentación** | Swashbuckle.AspNetCore | 6.5+    | OpenAPI/Swagger         |
| **Validación**    | FluentValidation       | 11.0+   | Validación de contratos |
| **Framework**     | ASP.NET Core           | 8.0+    | Construcción de APIs    |

---

## DTOs y Contratos

Los DTOs separan el modelo de dominio del contrato público de la API.

```csharp
// Request: anotaciones XML para documentación automática en Swagger
public record CreateCustomerRequest
{
    /// <summary>Nombre del cliente (2-100 caracteres)</summary>
    /// <example>Acme Corporation</example>
    public required string Name { get; init; }

    /// <summary>Email del cliente (formato válido)</summary>
    /// <example>contact@acme.com</example>
    public required string Email { get; init; }

    /// <summary>Teléfono (opcional, formato E.164)</summary>
    /// <example>+51987654321</example>
    public string? Phone { get; init; }

    /// <summary>Documento de identidad</summary>
    public required DocumentDto Document { get; init; }
}

public record DocumentDto
{
    /// <summary>Tipo de documento (DNI, RUC, CE)</summary>
    public required DocumentType Type { get; init; }

    /// <summary>Número de documento</summary>
    /// <example>20123456789</example>
    public required string Number { get; init; }
}

public enum DocumentType
{
    /// <summary>Documento Nacional de Identidad</summary>
    DNI,
    /// <summary>Registro Único de Contribuyentes</summary>
    RUC,
    /// <summary>Carnet de Extranjería</summary>
    CE
}

// Response: incluye campos generados por el servidor
public record CustomerDto
{
    public Guid Id { get; init; }
    public string Name { get; init; } = default!;
    public string Email { get; init; } = default!;
    public string? Phone { get; init; }
    public DocumentDto Document { get; init; } = default!;
    public DateTime CreatedAt { get; init; }
    public DateTime? UpdatedAt { get; init; }
}
```

:::tip DTOs separados por dirección
Usar DTOs distintos para request y response. Nunca exponer la entidad de dominio directamente en el contrato.
:::

---

## Validación con FluentValidation

```csharp
public class CreateCustomerRequestValidator : AbstractValidator<CreateCustomerRequest>
{
    public CreateCustomerRequestValidator()
    {
        RuleFor(x => x.Name)
            .NotEmpty().WithMessage("El nombre es requerido")
            .Length(2, 100).WithMessage("El nombre debe tener entre 2 y 100 caracteres")
            .Matches(@"^[a-zA-Z0-9\s\.,-]+$").WithMessage("El nombre contiene caracteres inválidos");

        RuleFor(x => x.Email)
            .NotEmpty().WithMessage("El email es requerido")
            .EmailAddress().WithMessage("Formato de email inválido")
            .MaximumLength(254);

        RuleFor(x => x.Phone)
            .Matches(@"^\+\d{10,15}$")
            .When(x => !string.IsNullOrEmpty(x.Phone))
            .WithMessage("Teléfono debe estar en formato E.164 (+51987654321)");

        RuleFor(x => x.Document)
            .NotNull().WithMessage("El documento es requerido")
            .SetValidator(new DocumentDtoValidator());
    }
}

public class DocumentDtoValidator : AbstractValidator<DocumentDto>
{
    public DocumentDtoValidator()
    {
        RuleFor(x => x.Type)
            .IsInEnum().WithMessage("Tipo de documento inválido");

        RuleFor(x => x.Number)
            .NotEmpty().WithMessage("Número de documento requerido")
            .Must((doc, number) => ValidateDocumentNumber(doc.Type, number))
            .WithMessage("Número de documento inválido para el tipo especificado");
    }

    private bool ValidateDocumentNumber(DocumentType type, string number)
    {
        return type switch
        {
            DocumentType.DNI => number.Length == 8 && number.All(char.IsDigit),
            DocumentType.RUC => number.Length == 11 && number.All(char.IsDigit),
            DocumentType.CE  => number.Length is >= 9 and <= 12,
            _                => false
        };
    }
}

// Program.cs
builder.Services.AddValidatorsFromAssemblyContaining<CreateCustomerRequestValidator>();
builder.Services.AddFluentValidationAutoValidation();
```

---

## Configuración OpenAPI/Swagger

```csharp
// Program.cs
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen(options =>
{
    options.SwaggerDoc("v1", new OpenApiInfo
    {
        Title = "Customer API",
        Version = "v1",
        Description = "API para gestión de clientes",
        Contact = new OpenApiContact
        {
            Name = "Equipo de Arquitectura",
            Email = "arquitectura@talma.com"
        }
    });

    // Incluir comentarios XML (habilitar en .csproj: <GenerateDocumentationFile>true</GenerateDocumentationFile>)
    var xmlFile = $"{Assembly.GetExecutingAssembly().GetName().Name}.xml";
    var xmlPath = Path.Combine(AppContext.BaseDirectory, xmlFile);
    options.IncludeXmlComments(xmlPath);

    // Seguridad JWT
    options.AddSecurityDefinition("Bearer", new OpenApiSecurityScheme
    {
        Description = "JWT Authorization: 'Bearer {token}'",
        Name = "Authorization",
        In = ParameterLocation.Header,
        Type = SecuritySchemeType.ApiKey,
        Scheme = "Bearer"
    });

    options.AddSecurityRequirement(new OpenApiSecurityRequirement
    {
        {
            new OpenApiSecurityScheme
            {
                Reference = new OpenApiReference { Type = ReferenceType.SecurityScheme, Id = "Bearer" }
            },
            Array.Empty<string>()
        }
    });

    options.EnableAnnotations();
});

var app = builder.Build();

app.UseSwagger();
app.UseSwaggerUI(options =>
{
    options.SwaggerEndpoint("/swagger/v1/swagger.json", "Customer API v1");
    options.RoutePrefix = "api-docs";
    options.DisplayRequestDuration();
});
```

---

## Beneficios en Práctica

| Sin contratos formales                                | Con contratos OpenAPI                   |
| ----------------------------------------------------- | --------------------------------------- |
| Integración por documentación manual o prueba y error | Documentación interactiva automática    |
| Bugs de deserialización en producción                 | Validación automática antes del handler |
| Acoplamiento implícito cliente/servidor               | Contrato versionado y explícito         |

---

## Requisitos Técnicos

### MUST (Obligatorio)

- **MUST** documentar toda API con OpenAPI 3.0
- **MUST** validar requests con FluentValidation o DataAnnotations antes de procesar
- **MUST** usar DTOs separados para requests y responses (no exponer entidades de dominio)
- **MUST** versionar contratos OpenAPI al hacer cambios incompatibles
- **MUST** incluir `ProducesResponseType` en cada action para todos los status codes posibles
- **MUST** envolver toda respuesta en `ApiResponse<T>` (ver [Estructura de Respuesta](./api-rest-standards.md#estructura-de-respuesta))

### SHOULD (Fuertemente recomendado)

- **SHOULD** incluir ejemplos (`<example>`) en las anotaciones XML de los DTOs
- **SHOULD** usar `record` inmutable para DTOs
- **SHOULD** habilitar `GenerateDocumentationFile` en el `.csproj`
- **SHOULD** exponer Swagger UI en todos los ambientes (con control de acceso en producción)

### MUST NOT (Prohibido)

- **MUST NOT** exponer entidades de dominio directamente como response
- **MUST NOT** retornar stack traces en producción
- **MUST NOT** omitir validación de tipos de documentos, enums o rangos numéricos

---

## Referencias

- [OpenAPI Specification](https://swagger.io/specification/) — Especificación OpenAPI 3.0
- [Swashbuckle.AspNetCore](https://github.com/domaindrivendev/Swashbuckle.AspNetCore) — Integración Swagger
- [FluentValidation](https://docs.fluentvalidation.net/) — Validación de requests
- [ASP.NET Core Web APIs](https://learn.microsoft.com/aspnet/core/web-api/) — Documentación oficial
- [Estándares REST](./api-rest-standards.md) — Base HTTP
- [Versionamiento de APIs](./api-versioning.md) — Estándar relacionado
- [Manejo de Errores en APIs](./api-error-handling.md) — Respuestas de error
