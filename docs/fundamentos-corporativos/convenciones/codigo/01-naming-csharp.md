---
id: naming-csharp
sidebar_position: 1
title: Naming - C#
description: Convenciones de nomenclatura para C# y .NET
---

## 1. Principio

Seguir las convenciones de Microsoft para C# garantiza código legible, consistente y profesional que otros desarrolladores .NET puedan entender fácilmente.

## 2. Reglas

### Regla 1: Clases, Structs, Enums, Interfaces

- **Formato**: `PascalCase`
- **Interfaces**: Prefijo `I`
- **Ejemplo correcto**: `UserService`, `OrderDto`, `IRepository`, `PaymentStatus`
- **Ejemplo incorrecto**: `userService`, `order_dto`, `Repository`, `payment_status`
- **Justificación**: Estándar de Microsoft, legibilidad

```csharp
// ✅ Correcto
public class UserService { }
public interface IUserRepository { }
public struct Point { }
public enum OrderStatus { Pending, Approved, Rejected }

// ❌ Incorrecto
public class userService { }
public interface UserRepository { }  // Falta prefijo I
public enum order_status { }
```

### Regla 2: Métodos y Propiedades

- **Formato**: `PascalCase`
- **Ejemplo correcto**: `GetUserById()`, `IsActive`, `CreatedAt`
- **Ejemplo incorrecto**: `getUserById()`, `isActive`, `created_at`

```csharp
// ✅ Correcto
public class User
{
    public string FirstName { get; set; }
    public DateTime CreatedAt { get; set; }

    public User GetUserById(int id) { }
    public bool IsActive() { }
}

// ❌ Incorrecto
public class User
{
    public string firstName { get; set; }  // camelCase
    public DateTime created_at { get; set; }  // snake_case

    public User getUserById(int id) { }  // camelCase
}
```

### Regla 3: Variables Locales y Parámetros

- **Formato**: `camelCase`
- **Ejemplo correcto**: `userId`, `orderTotal`, `isValid`
- **Ejemplo incorrecto**: `UserId`, `order_total`, `is_valid`

```csharp
// ✅ Correcto
public void ProcessOrder(int orderId, decimal orderTotal)
{
    var userId = GetCurrentUserId();
    bool isValid = ValidateOrder(orderId);
}

// ❌ Incorrecto
public void ProcessOrder(int OrderId, decimal order_total)
{
    var UserId = GetCurrentUserId();
    bool is_valid = ValidateOrder(OrderId);
}
```

### Regla 4: Campos Privados

- **Formato**: `_camelCase` (con underscore)
- **Ejemplo correcto**: `_userRepository`, `_logger`
- **Ejemplo incorrecto**: `userRepository`, `m_logger`, `_UserRepository`

```csharp
// ✅ Correcto
public class OrderService
{
    private readonly IOrderRepository _orderRepository;
    private readonly ILogger<OrderService> _logger;

    public OrderService(IOrderRepository orderRepository, ILogger<OrderService> logger)
    {
        _orderRepository = orderRepository;
        _logger = logger;
    }
}

// ❌ Incorrecto
public class OrderService
{
    private readonly IOrderRepository orderRepository;  // Falta _
    private readonly ILogger<OrderService> m_logger;     // Prefijo húngaro
}
```

### Regla 5: Constantes

- **Formato**: `PascalCase` (no UPPER_CASE en C#)
- **Ejemplo correcto**: `MaxRetries`, `DefaultTimeout`
- **Ejemplo incorrecto**: `MAX_RETRIES`, `default_timeout`

```csharp
// ✅ Correcto
public class Configuration
{
    public const int MaxRetries = 3;
    public const string DefaultCulture = "es-ES";
}

// ❌ Incorrecto
public class Configuration
{
    public const int MAX_RETRIES = 3;  // UPPER_CASE
}
```

### Regla 6: Namespaces

- **Formato**: `PascalCase.PascalCase`
- **Patrón**: `{Company}.{Product}.{Feature}[.SubFeature]`
- **Ejemplo correcto**: `Talma.Orders.Domain`, `Talma.Payments.Infrastructure`
- **Ejemplo incorrecto**: `talma.orders`, `Talma_Orders_Domain`

```csharp
// ✅ Correcto
namespace Talma.Orders.Domain.Entities;
namespace Talma.Payments.Infrastructure.Repositories;

// ❌ Incorrecto
namespace talma.orders.domain;
namespace Talma_Orders_Domain;
```

## 3. Tabla de Referencia Rápida

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
| Enum           | PascalCase  | `OrderStatus`     | `order_status`   |
| Enum value     | PascalCase  | `Pending`         | `PENDING`        |
| Namespace      | PascalCase  | `Talma.Orders`    | `talma.orders`   |

## 4. Casos Especiales

### Async Methods

- **Sufijo**: `Async`
- **Ejemplo**: `GetUserAsync()`, `SaveOrderAsync()`

```csharp
public async Task<User> GetUserAsync(int id)
{
    return await _repository.FindAsync(id);
}
```

### Event Handlers

- **Sufijo**: `Handler` o `EventHandler`
- **Ejemplo**: `OnOrderCreatedHandler`, `UserRegisteredEventHandler`

### DTOs (Data Transfer Objects)

- **Sufijo**: `Dto` o `Request`/`Response`
- **Ejemplo**: `UserDto`, `CreateOrderRequest`, `OrderResponse`

```csharp
public class CreateUserRequest { }
public class UserResponse { }
public class OrderDto { }
```

## 5. Herramientas de Validación

### StyleCop Analyzers

```xml
<!-- .csproj -->
<ItemGroup>
  <PackageReference Include="StyleCop.Analyzers" Version="1.2.0-beta.556" />
</ItemGroup>
```

### .editorconfig

```ini
# .editorconfig
[*.cs]

# Naming conventions
dotnet_naming_rule.interface_should_be_begins_with_i.severity = warning
dotnet_naming_rule.interface_should_be_begins_with_i.symbols = interface
dotnet_naming_rule.interface_should_be_begins_with_i.style = begins_with_i

dotnet_naming_rule.private_fields_should_be_camel_case_with_underscore.severity = warning
dotnet_naming_rule.private_fields_should_be_camel_case_with_underscore.symbols = private_field
dotnet_naming_rule.private_fields_should_be_camel_case_with_underscore.style = camel_case_with_underscore

# Styles
dotnet_naming_style.begins_with_i.capitalization = pascal_case
dotnet_naming_style.begins_with_i.required_prefix = I

dotnet_naming_style.camel_case_with_underscore.capitalization = camel_case
dotnet_naming_style.camel_case_with_underscore.required_prefix = _
```

## 6. Excepciones

- **Variables de loop**: `i`, `j`, `k` son aceptables en loops simples
- **Lambdas cortas**: `x`, `y` son aceptables: `users.Where(x => x.IsActive)`
- **Framework/Library**: Seguir convenciones del framework si difieren

## 📖 Referencias

### Estándares relacionados

## 6. Referencias

### Estándares Relacionados

- [C# y .NET](../../estandares/codigo/01-csharp-dotnet.md) - Estándares de Clean Code y SOLID

### Lineamientos Relacionados

- [Testing y Calidad](../../lineamientos/operabilidad/04-testing-y-calidad.md) - Lineamientos de calidad de código

### Principios Relacionados

- [Calidad desde el Diseño](../../principios/operabilidad/03-calidad-desde-el-diseno.md) - Fundamento de código limpio

### Otras Convenciones

- [Comentarios de Código](./03-comentarios-codigo.md) - Documentación en código
- [Estructura de Proyectos](./04-estructura-proyectos.md) - Organización de soluciones

### Documentación Externa

- [Microsoft C# Coding Conventions](https://learn.microsoft.com/en-us/dotnet/csharp/fundamentals/coding-style/coding-conventions) - Guía oficial
- [.NET Runtime Coding Style](https://github.com/dotnet/runtime/blob/main/docs/coding-guidelines/coding-style.md) - Estilo del runtime
- [StyleCop Rules](https://github.com/DotNetAnalyzers/StyleCopAnalyzers) - Reglas de análisis estático
