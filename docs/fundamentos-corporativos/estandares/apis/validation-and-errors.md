---
id: validacion-y-errores
sidebar_position: 3
title: Validación y Manejo de Errores
description: Estándar para validación de entrada con FluentValidation, manejo de errores con RFC 7807 Problem Details y middleware global de excepciones
---

# Estándar Técnico — Validación y Manejo de Errores

---

## 1. Propósito
Garantizar validación consistente con FluentValidation 11+ y manejo de errores con RFC 7807 Problem Details, middleware global de excepciones y logging estructurado sin exponer detalles internos.

---

## 2. Alcance

**Aplica a:**
- Validación de DTOs de entrada (requests)
- Validación de lógica de negocio
- Manejo de excepciones globales
- Respuestas de error consistentes (RFC 7807)

**No aplica a:**
- Validación en frontend (responsabilidad del cliente)
- Validación de entidades de dominio (use domain validation patterns)

---

## 3. Tecnologías Aprobadas

| Componente | Tecnología | Versión mínima | Observaciones |
|-----------|------------|----------------|---------------|
| **Validación** | FluentValidation | 11.0+ | Validación de DTOs declarativa |
| **Integración** | FluentValidation.AspNetCore | 11.0+ | Auto-validación en controllers |
| **Errores** | Hellang.Middleware.ProblemDetails | 6.5+ | RFC 7807 middleware |
| **Logging** | Serilog.AspNetCore | 8.0+ | Logging estructurado de errores |
| **Estándar** | RFC 7807 Problem Details | - | Formato error HTTP APIs |

> El uso de tecnologías no listadas requiere aprobación de Arquitectura.

---

## 4. Requisitos Obligatorios 🔴

- [ ] FluentValidation para todos los DTOs de entrada
- [ ] Validación automática en controllers (auto-validation)
- [ ] Respuestas de error con RFC 7807 Problem Details
- [ ] Middleware global de excepciones
- [ ] Status codes HTTP semánticos: 400 (validación), 404 (not found), 409 (conflict), 500 (server error)
- [ ] NO exponer stack traces en producción
- [ ] Logging de excepciones con correlation IDs
- [ ] Mensajes de error localizados y user-friendly
- [ ] Validación de campos anidados (nested objects)
- [ ] Custom validators para lógica de negocio compleja
- [ ] Errores con campo `type` (URI de documentación del error)
- [ ] Errores con campo `traceId` para correlación

---

## 5. Prohibiciones

- ❌ Exponer stack traces en producción
- ❌ Validación manual con `if` (usar FluentValidation)
- ❌ Errores genéricos sin contexto ("Bad Request")
- ❌ Status code 200 con errores en body
- ❌ Mezclar validación de negocio con validación de entrada
- ❌ Mensajes de error técnicos al usuario ("NullReferenceException")

---

## 6. Configuración Mínima

```csharp
// Program.cs
using FluentValidation;
using Hellang.Middleware.ProblemDetails;

// FluentValidation
builder.Services.AddValidatorsFromAssemblyContaining<Program>();
builder.Services.AddFluentValidationAutoValidation();

// Problem Details middleware
builder.Services.AddProblemDetails(options =>
{
    options.IncludeExceptionDetails = (ctx, ex) => builder.Environment.IsDevelopment();
    
    options.Map<ValidationException>(ex => new StatusCodeProblemDetails(400)
    {
        Title = "Validation Error",
        Detail = ex.Message,
        Type = "https://docs.talma.com/errors/validation"
    });
    
    options.Map<NotFoundException>(ex => new StatusCodeProblemDetails(404)
    {
        Title = "Not Found",
        Detail = ex.Message,
        Type = "https://docs.talma.com/errors/not-found"
    });
});

var app = builder.Build();
app.UseProblemDetails();
```

```csharp
// Validator ejemplo
public class CreateUserRequestValidator : AbstractValidator<CreateUserRequest>
{
    public CreateUserRequestValidator()
    {
        RuleFor(x => x.Name)
            .NotEmpty().WithMessage("El nombre es obligatorio")
            .Length(2, 100).WithMessage("El nombre debe tener entre 2 y 100 caracteres");

        RuleFor(x => x.Email)
            .NotEmpty()
            .EmailAddress().WithMessage("El formato del email no es válido")
            .Must(HaveValidDomain).WithMessage("Solo emails @talma.com permitidos");

        RuleFor(x => x.Age)
            .InclusiveBetween(18, 120).When(x => x.Age.HasValue);
    }
    
    private bool HaveValidDomain(string email) => email?.EndsWith("@talma.com") ?? false;
}
```

---

## 7. Validación

```bash
# Error de validación (400)
curl -X POST https://api.talma.com/api/v1/users \
  -H "Content-Type: application/json" \
  -d '{"name":"","email":"invalid"}'

# Error not found (404)
curl https://api.talma.com/api/v1/users/99999

# Verificar Problem Details format
curl -i https://api.talma.com/api/v1/users/99999 | grep -i "content-type: application/problem+json"

# Tests de validación
dotnet test --filter Category=Validation
```

**Métricas de cumplimiento:**

| Métrica | Target | Verificación |
|---------|--------|--------------|  
| DTOs con FluentValidation | 100% | `grep AbstractValidator` |
| Errores con RFC 7807 | 100% | Header `application/problem+json` |
| Stack traces en prod | 0 | Verificar logs de error |
| Errores con traceId | 100% | `jq .traceId` en responses |

Incumplimientos deben corregirse o documentarse mediante excepción aprobada.

---

## 8. Referencias

- [Diseño REST](./01-diseno-rest.md)
- [RFC 7807: Problem Details for HTTP APIs](https://datatracker.ietf.org/doc/html/rfc7807)
- [FluentValidation Documentation](https://docs.fluentvalidation.net/)
- [ASP.NET Core Error Handling](https://learn.microsoft.com/aspnet/core/web-api/handle-errors)
