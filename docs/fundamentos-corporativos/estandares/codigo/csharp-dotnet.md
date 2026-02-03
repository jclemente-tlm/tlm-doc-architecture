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

## 8. Referencias

- [Convenciones - Naming C#](../../convenciones/codigo/01-naming-csharp.md)
- [Unit Tests](../testing/01-unit-tests.md)
- [.NET Coding Conventions](https://learn.microsoft.com/dotnet/csharp/fundamentals/coding-style/coding-conventions)
- [Clean Code .NET](https://github.com/thangchung/clean-code-dotnet)
- [SOLID Principles](https://www.digitalocean.com/community/conceptual-articles/s-o-l-i-d-the-first-five-principles-of-object-oriented-design)
