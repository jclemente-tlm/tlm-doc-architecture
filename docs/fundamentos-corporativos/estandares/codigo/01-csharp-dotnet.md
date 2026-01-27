---
id: csharp-dotnet
sidebar_position: 1
title: C# y .NET
description: Estándares de Clean Code, principios SOLID y buenas prácticas para C# y .NET
---

# C# y .NET

## 1. Propósito

Establecer los estándares técnicos de Clean Code y principios SOLID para garantizar que el código C# y .NET sea legible, mantenible, testeable y seguro.

> **Nota:** Para convenciones de nomenclatura (naming), consulta [Convenciones - Naming C#](../../convenciones/codigo/01-naming-csharp.md).

## 2. Alcance

**Aplica a:**
- Proyectos .NET 8.0+ (backend, APIs, servicios)
- Librerías y componentes reutilizables en C#
- Aplicaciones web con ASP.NET Core
- Microservicios y servicios cloud-native

**No aplica a:**
- Proyectos legacy en .NET Framework <4.8 sin planes de migración
- Scripts de automatización simples

## 3. Tecnologías y Herramientas Obligatorias

### Versiones Mínimas

- **.NET:** 8.0+
- **C#:** 12+
- **ASP.NET Core:** 8.0+ (para APIs y web)

### Herramientas de Calidad

**Análisis estático (obligatorio):**

```xml
<ItemGroup>
  <PackageReference Include="StyleCop.Analyzers" Version="1.2.0-beta.556" />
  <PackageReference Include="SonarAnalyzer.CSharp" Version="9.16.0.82469" />
  <PackageReference Include="Microsoft.CodeAnalysis.NetAnalyzers" Version="8.0.0" />
</ItemGroup>
```

**Configuración `.editorconfig`:**

```ini
[*.cs]
indent_style = space
indent_size = 4

# Code quality rules
dotnet_diagnostic.CA1062.severity = warning  # Validate arguments
dotnet_diagnostic.CA1031.severity = warning  # Do not catch general exceptions
dotnet_diagnostic.CA2007.severity = warning  # ConfigureAwait
```

## 4. Configuración Estándar

### Inyección de Dependencias

**Program.cs (ASP.NET Core 8+):**

```csharp
var builder = WebApplication.CreateBuilder(args);

// Servicios con tiempo de vida apropiado
builder.Services.AddScoped<IOrderService, OrderService>();
builder.Services.AddSingleton<ICacheService, RedisCacheService>();
builder.Services.AddTransient<IEmailSender, SendGridEmailSender>();
```

### Manejo de Errores Global

```csharp
app.UseExceptionHandler(errorApp =>
{
    errorApp.Run(async context =>
    {
        var exceptionHandlerPathFeature = 
            context.Features.Get<IExceptionHandlerPathFeature>();
        
        var exception = exceptionHandlerPathFeature?.Error;
        
        await Results.Problem(
            title: "An error occurred",
            statusCode: StatusCodes.Status500InternalServerError
        ).ExecuteAsync(context);
    });
});
```

## 5. Ejemplos Prácticos

### Ejemplo 1: Single Responsibility Principle (SRP)

**✅ Correcto:**

```csharp
public class OrderService
{
    private readonly IOrderRepository _repository;
    private readonly IOrderValidator _validator;
    
    public OrderService(IOrderRepository repository, IOrderValidator validator)
    {
        _repository = repository;
        _validator = validator;
    }
    
    public async Task<Order> CreateOrderAsync(CreateOrderDto dto)
    {
        // Solo responsabilidad de crear órdenes
        _validator.Validate(dto);
        var order = dto.ToEntity();
        return await _repository.AddAsync(order);
    }
}
```

**❌ Incorrecto:**

```csharp
public class OrderService
{
    public async Task<Order> CreateOrderAsync(CreateOrderDto dto)
    {
        // Mezcla validación, persistencia, notificación (múltiples responsabilidades)
        if (string.IsNullOrEmpty(dto.CustomerId)) throw new Exception("Invalid");
        var order = new Order { /* ... */ };
        SaveToDatabase(order);
        SendEmail(order.CustomerEmail, "Order created");
        return order;
    }
}
```

### Ejemplo 2: Dependency Injection

**✅ Correcto:**

```csharp
public class PaymentProcessor
{
    private readonly IPaymentGateway _gateway;
    private readonly ILogger<PaymentProcessor> _logger;
    
    public PaymentProcessor(IPaymentGateway gateway, ILogger<PaymentProcessor> logger)
    {
        _gateway = gateway ?? throw new ArgumentNullException(nameof(gateway));
        _logger = logger ?? throw new ArgumentNullException(nameof(logger));
    }
    
    public async Task<PaymentResult> ProcessAsync(Payment payment)
    {
        _logger.LogInformation("Processing payment {PaymentId}", payment.Id);
        return await _gateway.ChargeAsync(payment);
    }
}
```

### Ejemplo 3: Async/Await Correcto

**✅ Correcto:**

```csharp
public async Task<List<Order>> GetActiveOrdersAsync()
{
    return await _dbContext.Orders
        .Where(o => o.Status == OrderStatus.Active)
        .ToListAsync();
}
```

**❌ Incorrecto:**

```csharp
// NO usar .Result o .Wait() - bloquea thread
public List<Order> GetActiveOrders()
{
    return _dbContext.Orders
        .Where(o => o.Status == OrderStatus.Active)
        .ToListAsync().Result;  // ❌ Deadlock risk
}
```

### Ejemplo 4: LINQ en lugar de bucles

**✅ Correcto:**

```csharp
var activeUsers = users
    .Where(u => u.IsActive && u.RegistrationDate > cutoffDate)
    .OrderBy(u => u.Name)
    .Select(u => new UserDto 
    { 
        Id = u.Id, 
        Name = u.Name 
    })
    .ToList();
```

**❌ Incorrecto:**

```csharp
var activeUsers = new List<UserDto>();
foreach (var u in users)
{
    if (u.IsActive && u.RegistrationDate > cutoffDate)
    {
        activeUsers.Add(new UserDto { Id = u.Id, Name = u.Name });
    }
}
activeUsers.Sort((a, b) => a.Name.CompareTo(b.Name));
```

## 6. Mejores Prácticas

### Principios SOLID

✅ **Single Responsibility:** Una clase, una responsabilidad  
✅ **Open/Closed:** Abierto a extensión, cerrado a modificación  
✅ **Liskov Substitution:** Subtipos deben ser sustituibles  
✅ **Interface Segregation:** Interfaces pequeñas y específicas  
✅ **Dependency Inversion:** Depender de abstracciones

### Manejo de Errores

✅ **Usar excepciones específicas:** `FileNotFoundException`, `ArgumentNullException`  
✅ **Validar argumentos:** Null checks en constructores y métodos públicos  
✅ **Logging estructurado:** Usar Serilog o ILogger con contexto  
✅ **Global exception handler:** Middleware para APIs

### Async/Await

✅ **Siempre async hasta el final:** No mezclar sync/async  
✅ **ConfigureAwait(false):** En librerías (no en ASP.NET Core)  
✅ **Evitar async void:** Solo en event handlers  
✅ **CancellationToken:** En operaciones largas

## 7. NO Hacer (Antipatrones)

### Antipatrón 1: God Classes

❌ **NO** crear clases que hacen demasiado

```csharp
// ❌ Clase con 50+ métodos y múltiples responsabilidades
public class OrderManager
{
    public void CreateOrder() { }
    public void SendEmail() { }
    public void ProcessPayment() { }
    public void GenerateInvoice() { }
    public void UpdateInventory() { }
    // ... 45 métodos más
}
```

**Razón:** Viola SRP, difícil de mantener y testear

**Alternativa:** Separar en `OrderService`, `EmailService`, `PaymentService`, etc.

### Antipatrón 2: Catch Genérico Vacío

❌ **NO** ocultar errores

```csharp
try
{
    await ProcessOrderAsync(order);
}
catch  // ❌ Catch sin tipo y sin manejo
{
    // Silenciosamente ignora el error
}
```

**Razón:** Pérdida de información crítica, bugs ocultos

**Alternativa:**

```csharp
try
{
    await ProcessOrderAsync(order);
}
catch (ValidationException ex)
{
    _logger.LogWarning(ex, "Order validation failed");
    throw;
}
```

### Antipatrón 3: Strings Mágicos

❌ **NO** usar valores hardcodeados

```csharp
if (user.Role == "admin")  // ❌ String mágico
{
    // ...
}
```

**Alternativa:**

```csharp
public static class Roles
{
    public const string Admin = "admin";
    public const string User = "user";
}

if (user.Role == Roles.Admin)  // ✅
{
    // ...
}
```

### Antipatrón 4: Uso de .Result o .Wait()

❌ **NO** bloquear código asíncrono

```csharp
var result = GetDataAsync().Result;  // ❌ Riesgo de deadlock
```

**Razón:** Bloquea thread, puede causar deadlocks

**Alternativa:** Usar `await` correctamente

## 8. Validación y Cumplimiento

**Criterios verificables:**

- [ ] Todos los proyectos usan .NET 8.0+
- [ ] StyleCop.Analyzers configurado sin errores
- [ ] SonarQube muestra 0 bugs críticos
- [ ] Cobertura de código >80% en servicios core
- [ ] Dependency Injection en todos los servicios
- [ ] No existen `async void` (excepto event handlers)
- [ ] No se usan `.Result` ni `.Wait()`
- [ ] Global exception handler configurado

**Herramientas de validación:**

- **SonarQube** - Análisis de código continuo
- **EditorConfig** - Validación en IDE
- **CI/CD** - Build falla si hay violaciones críticas

## 9. Referencias

### Lineamientos Relacionados

- [Testing y Calidad](../../lineamientos/operabilidad/04-testing-y-calidad.md) - Estándares de calidad en desarrollo

### Principios Relacionados

- [Calidad desde el Diseño](../../principios/operabilidad/03-calidad-desde-el-diseno.md) - Fundamento de estos estándares

### Convenciones Relacionadas

- [Naming - C#](../../convenciones/codigo/01-naming-csharp.md) - Convenciones de nomenclatura
- [Comentarios de Código](../../convenciones/codigo/03-comentarios-codigo.md) - Guía de documentación
- [Estructura de Proyectos](../../convenciones/codigo/04-estructura-proyectos.md) - Organización de soluciones

### Otros Estándares

- [Testing Unitario](../testing/01-unit-tests.md) - xUnit y pruebas
- [Testing de Integración](../testing/02-integration-tests.md) - Pruebas con dependencias

### Documentación Externa

- [clean-code-dotnet](https://github.com/thangchung/clean-code-dotnet) - Guía adaptada para .NET
- [Microsoft C# Coding Conventions](https://learn.microsoft.com/es-es/dotnet/csharp/fundamentals/coding-style/coding-conventions) - Guía oficial
- [Clean Code (Robert C. Martin)](https://www.oreilly.com/library/view/clean-code/9780136083238/) - Libro fundamental
- [Principios SOLID](https://learn.microsoft.com/es-es/dotnet/architecture/modern-web-apps-azure/architectural-principles#solid) - Arquitectura .NET
