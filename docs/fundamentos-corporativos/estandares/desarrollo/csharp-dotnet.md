---
id: csharp-dotnet
sidebar_position: 1
title: C# y .NET
description: Estándares de Clean Code, principios SOLID y buenas prácticas para C# y .NET
---

# Estándar Técnico — C# y .NET

---

## 1. Propósito

Garantizar código C# legible, mantenible y testeable mediante Clean Code, SOLID, async/await, inyección de dependencias, StyleCop/SonarAnalyzer y nullable reference types habilitados.

---

## 2. Alcance

**Aplica a:**

- Proyectos .NET 8.0+ (backend, APIs, servicios)
- Librerías y componentes reutilizables
- Microservicios cloud-native

**No aplica a:**

- Proyectos legacy .NET Framework `<4.8` sin planes de migración
- Scripts de automatización simples

---

## 3. Tecnologías Aprobadas

| Componente    | Tecnología           | Versión mínima | Observaciones                   |
| ------------- | -------------------- | -------------- | ------------------------------- |
| **Framework** | .NET                 | 8.0+           | LTS recomendado                 |
| **Lenguaje**  | C#                   | 12+            | Nullable reference types        |
| **Mapeo**     | Mapster              | 7.4+           | Object mapping (NO AutoMapper)  |
| **Análisis**  | StyleCop.Analyzers   | 1.2+           | Reglas de estilo                |
| **Análisis**  | SonarAnalyzer.CSharp | 9.16+          | Detección bugs/vulnerabilidades |
| **Análisis**  | SonarQube            | 10.0+          | Análisis continuo código        |
| **Testing**   | xUnit                | 2.6+           | Framework de pruebas            |
| **Mocking**   | Moq                  | 4.20+          | Mocks para tests                |

> El uso de tecnologías no listadas requiere aprobación de Arquitectura.

---

## 4. Requisitos Obligatorios 🔴

- [ ] .NET 8.0+ y C# 12+ en todos los proyectos nuevos
- [ ] Nullable reference types habilitado (`<Nullable>enable</Nullable>`)
- [ ] StyleCop.Analyzers configurado en todos los proyectos
- [ ] SonarAnalyzer.CSharp habilitado
- [ ] Inyección de dependencias (NO `new` en lógica de negocio)
- [ ] Async/await para operaciones I/O (NO síncronas)
- [ ] SOLID principles aplicados (SRP, OCP, LSP, ISP, DIP)
- [ ] Métodos con responsabilidad única (`<20` líneas)
- [ ] Clases cohesivas (`<300` líneas, `<10` métodos)
- [ ] Excepciones específicas (NO `catch (Exception)`)
- [ ] ConfigureAwait(false) en librerías
- [ ] Interfaces para abstracciones (NO clases concretas en constructores)

---

## 5. Prohibiciones

- ❌ `new` directo en lógica de negocio (usar DI)
- ❌ Operaciones I/O síncronas (usar async/await)
- ❌ `catch (Exception ex)` sin rethrow
- ❌ Métodos con >3 parámetros (usar objetos de configuración)
- ❌ Magic numbers/strings (usar constantes/enums)
- ❌ Clases con >10 dependencias (God Object)
- ❌ Código comentado (eliminar, usar Git)

---

## 6. Configuración Mínima

```xml
<!-- .csproj -->
<PropertyGroup>
  <TargetFramework>net8.0</TargetFramework>
  <LangVersion>12</LangVersion>
  <Nullable>enable</Nullable>
  <TreatWarningsAsErrors>true</TreatWarningsAsErrors>
</PropertyGroup>

<ItemGroup>
  <PackageReference Include="StyleCop.Analyzers" Version="1.2.0-beta.556" />
  <PackageReference Include="SonarAnalyzer.CSharp" Version="9.16.0" />
  <PackageReference Include="Microsoft.CodeAnalysis.NetAnalyzers" Version="8.0.0" />
</ItemGroup>
```

```ini
# .editorconfig
[*.cs]
indent_style = space
indent_size = 4

# Nullable
dotnet_diagnostic.CS8600.severity = error
dotnet_diagnostic.CS8602.severity = error

# Code quality
dotnet_diagnostic.CA1062.severity = warning  # Validate arguments
dotnet_diagnostic.CA1031.severity = warning  # Do not catch general exceptions
dotnet_diagnostic.CA2007.severity = warning  # ConfigureAwait
```

```csharp
// Program.cs - Inyección de dependencias
var builder = WebApplication.CreateBuilder(args);

builder.Services.AddScoped<IOrderService, OrderService>();
builder.Services.AddSingleton<ICacheService, RedisCacheService>();
builder.Services.AddTransient<IEmailSender, SendGridEmailSender>();

var app = builder.Build();
```

```csharp
// Ejemplo de servicio con DI y async/await
public class OrderService : IOrderService
{
    private readonly IOrderRepository _repository;
    private readonly ILogger<OrderService> _logger;

    public OrderService(IOrderRepository repository, ILogger<OrderService> logger)
    {
        _repository = repository ?? throw new ArgumentNullException(nameof(repository));
        _logger = logger ?? throw new ArgumentNullException(nameof(logger));
    }

    public async Task<Order?> GetOrderAsync(Guid orderId, CancellationToken cancellationToken)
    {
        _logger.LogInformation("Retrieving order {OrderId}", orderId);

        var order = await _repository.GetByIdAsync(orderId, cancellationToken).ConfigureAwait(false);

        if (order == null)
        {
            _logger.LogWarning("Order {OrderId} not found", orderId);
        }

        return order;
    }
}
```

---

## 7. Validación

```bash
# Build con análisis estático
dotnet build --configuration Release /warnaserror

# Ejecutar analyzers
dotnet build /p:EnforceCodeStyleInBuild=true

# Tests
dotnet test --configuration Release

# Verificar nullable warnings
dotnet build | grep -i "CS8"  # Debe retornar 0

# Code coverage
dotnet test /p:CollectCoverage=true /p:CoverletOutputFormat=opencover
```

**Métricas de cumplimiento:**

| Métrica               | Target | Verificación                 |
| --------------------- | ------ | ---------------------------- |
| Nullable habilitado   | 100%   | `grep Nullable *.csproj`     |
| Warnings como errores | 100%   | `TreatWarningsAsErrors=true` |
| Métodos `<20` líneas  | >90%   | SonarQube analysis           |
| Code coverage         | >80%   | Coverlet report              |

Incumplimientos deben corregirse o documentarse mediante excepción aprobada.

---

## 8. Convenciones de Nomenclatura

### 8.1. Clases, Structs, Enums, Interfaces

- **Formato**: `PascalCase`
- **Interfaces**: Prefijo `I`
- **Ejemplo**: `UserService`, `OrderDto`, `IRepository`, `PaymentStatus`

```csharp
// ✅ Correcto
public class UserService { }
public interface IUserRepository { }
public struct Point { }
public enum OrderStatus { Pending, Approved, Rejected }
```

### 8.2. Métodos y Propiedades

- **Formato**: `PascalCase`
- **Async methods**: Sufijo `Async`
- **Ejemplo**: `GetUserById()`, `IsActive`, `CreatedAt`, `GetUserAsync()`

```csharp
public class User
{
    public string FirstName { get; set; }
    public DateTime CreatedAt { get; set; }

    public async Task<User> GetUserAsync(int id) { }
}
```

### 8.3. Variables Locales y Parámetros

- **Formato**: `camelCase`
- **Ejemplo**: `userId`, `orderTotal`, `isValid`

```csharp
public void ProcessOrder(int orderId, decimal orderTotal)
{
    var userId = GetCurrentUserId();
    bool isValid = ValidateOrder(orderId);
}
```

### 8.4. Campos Privados

- **Formato**: `_camelCase` (con underscore)
- **Ejemplo**: `_userRepository`, `_logger`

```csharp
public class OrderService
{
    private readonly IOrderRepository _orderRepository;
    private readonly ILogger<OrderService> _logger;
}
```

### 8.5. Constantes

- **Formato**: `PascalCase` (no UPPER_CASE en C#)
- **Ejemplo**: `MaxRetries`, `DefaultTimeout`

```csharp
public class Configuration
{
    public const int MaxRetries = 3;
    public const string DefaultCulture = "es-ES";
}
```

### 8.6. Namespaces

- **Formato**: `PascalCase.PascalCase`
- **Patrón**: `{Company}.{Product}.{Feature}[.SubFeature]`
- **Ejemplo**: `Talma.Orders.Domain`, `Talma.Payments.Infrastructure`

```csharp
namespace Talma.Orders.Domain.Entities;
namespace Talma.Payments.Infrastructure.Repositories;
```

### 8.7. Tabla de Referencia Rápida

| Elemento       | Convención  | Ejemplo           | Incorrecto       |
| -------------- | ----------- | ----------------- | ---------------- |
| Clase          | PascalCase  | `UserService`     | `userService`    |
| Interfaz       | IPascalCase | `IUserRepository` | `UserRepository` |
| Método         | PascalCase  | `GetUser()`       | `getUser()`      |
| Propiedad      | PascalCase  | `FirstName`       | `firstName`      |
| Variable local | camelCase   | `userId`          | `UserId`         |
| Parámetro      | camelCase   | `orderId`         | `OrderId`        |
| Campo privado  | \_camelCase | `_logger`         | `logger`         |
| Constante      | PascalCase  | `MaxRetries`      | `MAX_RETRIES`    |

---

## 9. Convenciones de Comentarios

### 9.1. Documentar APIs Públicas (XMLDoc)

```csharp
/// <summary>
/// Calcula el precio total de una orden incluyendo impuestos y descuentos.
/// </summary>
/// <param name="orderId">Identificador único de la orden</param>
/// <param name="applyDiscount">Indica si se debe aplicar el descuento del cliente</param>
/// <returns>Precio total con impuestos en la moneda de la orden</returns>
/// <exception cref="OrderNotFoundException">Si la orden no existe</exception>
public async Task<Money> CalculateTotalPriceAsync(int orderId, bool applyDiscount)
{
    // Implementation...
}
```

### 9.2. Explicar Decisiones de Negocio o Complejidad

```csharp
// Aplicamos 15% de descuento solo a clientes VIP con más de 10 órdenes
// según política comercial definida en JIRA-1234
if (customer.IsVIP && customer.OrderCount > 10)
{
    discount = price * 0.15m;
}
```

### 9.3. Marcar TODOs y FIXMEs

```csharp
// TODO(jperez): Migrar a Redis cuando el caché supere 10GB [ARCH-456]
var cache = new InMemoryCache();

// DEPRECATED: Usar GetUserV2Async() en su lugar - Remover en v3.0
public User GetUserV1(int id) { }
```

### 9.4. Evitar Comentarios Obvios

```csharp
❌ Evitar:
// Obtener usuario por ID
var user = await GetUserByIdAsync(userId);

// Incrementar contador
counter++;
```

---

## 10. Estructura de Proyectos

### 10.1. Estructura por Capas (.NET)

```
src/
├── TalmaApp.Api/                      # Capa de presentación (Web API)
│   ├── Controllers/
│   ├── Filters/
│   ├── Middleware/
│   ├── Models/                        # DTOs de request/response
│   ├── Program.cs
│   └── appsettings.json
├── TalmaApp.Application/              # Casos de uso / Lógica de aplicación
│   ├── UseCases/
│   │   ├── Users/
│   │   │   ├── CreateUser/
│   │   │   │   ├── CreateUserCommand.cs
│   │   │   │   ├── CreateUserHandler.cs
│   │   │   │   └── CreateUserValidator.cs
│   │   │   └── GetUser/
│   │   └── Orders/
│   ├── Common/
│   │   ├── Behaviors/                 # MediatR behaviors
│   │   ├── Interfaces/
│   │   └── Mappings/
│   └── DependencyInjection.cs
├── TalmaApp.Domain/                   # Entidades de dominio
│   ├── Entities/
│   ├── ValueObjects/
│   ├── Enums/
│   ├── Events/
│   └── Exceptions/
├── TalmaApp.Infrastructure/           # Implementaciones concretas
│   ├── Persistence/
│   │   ├── ApplicationDbContext.cs
│   │   ├── Configurations/
│   │   └── Repositories/
│   ├── Services/
│   ├── ExternalApis/
│   └── DependencyInjection.cs
└── TalmaApp.Shared/                   # Compartido entre capas
    ├── Constants/
    ├── Extensions/
    └── Helpers/

tests/
├── TalmaApp.UnitTests/
├── TalmaApp.IntegrationTests/
└── TalmaApp.ArchitectureTests/
```

### 10.2. Patrones de Archivos

```
User.cs                    # Entidad
UserDto.cs                 # DTO
IUserRepository.cs         # Interfaz
UserRepository.cs          # Implementación
UserService.cs             # Servicio
CreateUserCommand.cs       # Comando CQRS
UserProfile.cs             # Mapster profile
```

### 10.3. Un Concepto, Una Carpeta

```
✅ Correcto:
src/users/
├── user.service.ts
├── user.repository.ts
├── user.entity.ts

❌ Incorrecto (mezclado):
src/services/
├── user.service.ts
├── order.service.ts
```

### 10.4. Nomenclatura de Carpetas

- **kebab-case**: `user-management/`, `order-processing/`
- **Plural para colecciones**: `users/`, `orders/`, `components/`
- **Singular para conceptos**: `config/`, `shared/`, `infrastructure/`
- **Máximo 7 archivos por carpeta**: Subdividir si excede

---

## 11. Referencias

- [Unit Tests](../testing/unit-tests.md)
- [APIs REST](../apis/api-rest.md) - DTOs y APIs
- [.NET Coding Conventions](https://learn.microsoft.com/dotnet/csharp/fundamentals/coding-style/coding-conventions)
- [Clean Code .NET](https://github.com/thangchung/clean-code-dotnet)
- [SOLID Principles](https://www.digitalocean.com/community/conceptual-articles/s-o-l-i-d-the-first-five-principles-of-object-oriented-design)
- [Microsoft C# Coding Conventions](https://learn.microsoft.com/en-us/dotnet/csharp/fundamentals/coding-style/coding-conventions)
- [.NET Runtime Coding Style](https://github.com/dotnet/runtime/blob/main/docs/coding-guidelines/coding-style.md)
