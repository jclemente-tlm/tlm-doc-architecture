---
id: architecture-principles
sidebar_position: 5
title: Principios de Arquitectura
description: Principios KISS, YAGNI, acoplamiento bajo, gestión de dependencias, simplicidad operacional, análisis de complejidad y métricas de simplicidad.
---

# Principios de Arquitectura

## Contexto

Este estándar consolida los principios fundamentales que guían las decisiones arquitectónicas hacia simplicidad y mantenibilidad. Complementa el lineamiento [Simplicidad Intencional](../../lineamientos/arquitectura/13-simplicidad-intencional.md).

**Conceptos incluidos:**

- **KISS (Keep It Simple)** → Preferir soluciones simples
- **YAGNI (You Aren't Gonna Need It)** → No anticipar necesidades futuras
- **Loose Coupling** → Minimizar dependencias entre componentes
- **Dependency Management** → Control explícito de dependencias externas
- **Operational Simplicity** → Diseñar para facilitar operación
- **Complexity Analysis** → Medir y controlar complejidad
- **Simplicity Metrics** → Métricas objetivas de simplicidad

---

## Stack Tecnológico

| Componente                 | Tecnología | Versión | Uso                                 |
| -------------------------- | ---------- | ------- | ----------------------------------- |
| **Análisis estático**      | SonarQube  | 10.0+   | Métricas de complejidad ciclomática |
| **Gestión dependencias**   | NuGet      | 6.8+    | Control de paquetes .NET            |
| **Seguridad dependencias** | Dependabot | -       | Alertas de vulnerabilidades         |
| **Visualización**          | NDepend    | 2024+   | Análisis arquitectónico avanzado    |

---

## Conceptos Fundamentales

Este estándar cubre 7 principios para arquitecturas simples:

### Índice de Conceptos

1. **KISS**: Preferir soluciones simples sobre complejas
2. **YAGNI**: Implementar solo lo necesario ahora
3. **Loose Coupling**: Minimizar dependencias
4. **Dependency Management**: Control explícito de dependencias
5. **Operational Simplicity**: Facilitar troubleshooting
6. **Complexity Analysis**: Identificar complejidad
7. **Simplicity Metrics**: Medir simplicidad objetivamente

---

## 1. KISS (Keep It Simple, Stupid)

### ¿Qué es KISS?

Principio que prioriza soluciones simples y directas sobre soluciones complejas.

**Propósito:** Reducir complejidad cognitiva, facilitar mantenimiento.

**Beneficios:**
✅ Onboarding rápido
✅ Menos bugs
✅ Mantenimiento económico

### Ejemplo Comparativo

```csharp
// ❌ MALO: Abstracción innecesaria
public interface IRepositoryFactory
{
    IRepository<T> CreateRepository<T>() where T : class;
}
// Solo usamos un repository, factory no aporta valor

// ✅ BUENO: Solución directa
public class CustomerRepository : ICustomerRepository
{
    private readonly ApplicationDbContext _context;

    public async Task<Customer?> GetByIdAsync(Guid id)
    {
        return await _context.Customers.FindAsync(id);
    }
}
```

---

## 2. YAGNI (You Aren't Gonna Need It)

### ¿Qué es YAGNI?

Principio de no implementar funcionalidad hasta que sea realmente necesaria.

**Propósito:** Evitar código muerto, reducir superficie de mantenimiento.

**Beneficios:**
✅ Menos código que mantener
✅ Decisiones con datos reales
✅ Entrega más rápida

### Ejemplo Comparativo

```csharp
// ❌ MALO: Anticipar futuro hipotético
public class ProductService
{
    public async Task<Product> GetProduct(Guid id, ProviderType provider = ProviderType.Default)
    {
        // Solo usamos Default, el resto es código muerto
        return provider switch
        {
            ProviderType.Default => await _repo.GetAsync(id),
            ProviderType.External => await _externalRepo.GetAsync(id),
            _ => throw new NotImplementedException()
        };
    }
}

// ✅ BUENO: Solo lo necesario
public class ProductService
{
    public async Task<Product> GetProduct(Guid id)
    {
        return await _repository.GetByIdAsync(id);
    }
}
```

---

## 3. Loose Coupling

### ¿Qué es Loose Coupling?

Minimizar dependencias directas entre componentes usando abstracciones.

**Propósito:** Facilitar cambios, testing, evolución paralela.

**Beneficios:**
✅ Componentes intercambiables
✅ Testing aislado
✅ Cambios localizados

### Ejemplo Comparativo

```csharp
// ❌ MALO: Acoplamiento fuerte
public class OrderProcessor
{
    public void ProcessOrder(Order order)
    {
        var emailService = new SmtpEmailService();
        emailService.SendEmail(order.CustomerEmail, "Confirmed");
    }
}

// ✅ BUENO: Acoplamiento bajo
public class OrderProcessor
{
    private readonly IEmailService _emailService;

    public OrderProcessor(IEmailService emailService)
    {
        _emailService = emailService;
    }

    public async Task ProcessOrder(Order order)
    {
        await _emailService.SendAsync(order.CustomerEmail, "Confirmed");
    }
}
```

---

## 4. Dependency Management

### ¿Qué es Dependency Management?

Control explícito de todas las dependencias externas del proyecto.

**Propósito:** Evitar dependency hell, controlar superficie de ataque.

**Beneficios:**
✅ Builds reproducibles
✅ Actualizaciones controladas
✅ Menor riesgo de seguridad

### Ejemplo Comparativo

```xml
<!-- ❌ MALO: Sin control -->
<ItemGroup>
  <PackageReference Include="Newtonsoft.Json" Version="*" />
  <PackageReference Include="RandomPackage" Version="1.0.0" />
</ItemGroup>

<!-- ✅ BUENO: Control explícito -->
<ItemGroup>
  <PackageReference Include="System.Text.Json" Version="8.0.0" />
  <PackageReference Include="Npgsql.EntityFrameworkCore.PostgreSQL" Version="8.0.0" />
  <PackageReference Include="Serilog.AspNetCore" Version="8.0.0" />
</ItemGroup>
```

---

## 5. Operational Simplicity

### ¿Qué es Operational Simplicity?

Diseñar sistemas simples de operar y diagnosticar en producción.

**Propósito:** Reducir MTTR, facilitar troubleshooting.

**Beneficios:**
✅ Menor MTTR
✅ Troubleshooting rápido
✅ On-call menos estresante

### Ejemplo Comparativo

```csharp
// ❌ MALO: Opaco
public async Task<bool> ProcessPayment(decimal amount)
{
    try
    {
        var result = await _gateway.Charge(amount);
        return result > 0;
    }
    catch { return false; }
}

// ✅ BUENO: Observable
public async Task<Result<PaymentId>> ProcessPayment(OrderId orderId, Money amount)
{
    _logger.LogInformation("Processing payment: Order={OrderId}, Amount={Amount}",
        orderId, amount);

    try
    {
        var result = await _gateway.ChargeAsync(amount);
        _logger.LogInformation("Payment successful: PaymentId={PaymentId}",
            result.PaymentId);
        return Result.Success(result.PaymentId);
    }
    catch (PaymentException ex)
    {
        _logger.LogError(ex, "Payment failed: Order={OrderId}, Code={Code}",
            orderId, ex.ErrorCode);
        return Result.Failure<PaymentId>($"Payment failed: {ex.Reason}");
    }
}
```

---

## 6. Complexity Analysis

### ¿Qué es Complexity Analysis?

Identificación y medición sistemática de complejidad en el código.

**Métricas:**

- **Cyclomatic Complexity**: Número de caminos independientes
- **Cognitive Complexity**: Esfuerzo mental para entender
- **Lines of Code**: Tamaño del código

**Beneficios:**
✅ Identificar hotspots
✅ Objetivizar code reviews
✅ Prevenir degradación

### Umbrales Recomendados

```yaml
# SonarQube Quality Gates
complexity:
  methods:
    cyclomatic_max: 10
    critical_threshold: 15

  classes:
    cyclomatic_max: 50
    lines_max: 300

  files:
    lines_max: 500
```

---

## 7. Simplicity Metrics

### ¿Qué son Simplicity Metrics?

Métricas objetivas para medir y trackear simplicidad en el tiempo.

**Métricas clave:**

- LOC total
- Dependencias por proyecto (< 15)
- Complejidad ciclomática promedio (< 5)
- Profundidad de herencia (< 4)
- Test coverage (> 80%)

**Beneficios:**
✅ Seguimiento objetivo
✅ Detectar degradación temprano
✅ Baseline para mejoras

---

## Matriz de Decisión

| Escenario         | KISS   | YAGNI  | Loose Coupling | Dep. Mgmt | Op. Simplicity |
| ----------------- | ------ | ------ | -------------- | --------- | -------------- |
| **Nuevo feature** | ✅✅✅ | ✅✅✅ | ✅✅           | ✅        | ✅             |
| **Refactoring**   | ✅✅✅ | ✅     | ✅✅✅         | ✅        | ✅             |
| **Microservicio** | ✅✅   | ✅✅   | ✅✅✅         | ✅✅✅    | ✅✅✅         |
| **MVP**           | ✅✅✅ | ✅✅✅ | ✅             | ✅        | ✅             |

---

## Requisitos Técnicos

### MUST (Obligatorio)

- **MUST** aplicar KISS como criterio por defecto
- **MUST** justificar complejidad cuando se introduce
- **MUST** usar inyección de dependencias
- **MUST** versionar dependencias explícitamente
- **MUST** incluir logs estructurados

### SHOULD (Fuertemente recomendado)

- **SHOULD** aplicar YAGNI salvo necesidad demostrable
- **SHOULD** mantener < 15 dependencias directas por proyecto
- **SHOULD** medir complejidad ciclomática en CI/CD

### MUST NOT (Prohibido)

- **MUST NOT** introducir frameworks pesados sin justificación
- **MUST NOT** sobre-ingenierizar soluciones simples
- **MUST NOT** usar dependencias sin versionado explícito

---

## Referencias

- [YAGNI (Martin Fowler)](https://martinfowler.com/bliki/Yagni.html)
- [Coupling and Cohesion](<https://en.wikipedia.org/wiki/Coupling_(computer_programming)>)
- [SonarQube Metrics](https://docs.sonarqube.org/latest/user-guide/metric-definitions/)
