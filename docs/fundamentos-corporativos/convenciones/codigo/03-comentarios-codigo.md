---
id: comentarios-codigo
sidebar_position: 3
title: Comentarios en Código
description: Convención para documentar código con comentarios efectivos
---

## 1. Principio

Los comentarios deben explicar el **por qué**, no el **qué**. El código debe ser autoexplicativo en su estructura y nombres; los comentarios agregan contexto, razones de negocio o advertencias.

## 2. Reglas

### Regla 1: Documentar APIs Públicas (C# - XMLDoc)

- **Formato**: XML comments con `///`
- **Obligatorio**: Clases, métodos y propiedades públicas
- **Ejemplo correcto**:

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

- **Ejemplo incorrecto**:

```csharp
// Este método calcula el precio total
public async Task<Money> CalculateTotalPriceAsync(int orderId, bool applyDiscount)
{
    // Implementation...
}
```

### Regla 2: NO Comentar Código Obvio

```csharp
❌ Evitar comentarios redundantes:

// Obtener usuario por ID
var user = await GetUserByIdAsync(userId);

// Incrementar contador
counter++;

// Retornar true
return true;
```

### Regla 3: Explicar Decisiones de Negocio o Complejidad

```csharp
✅ Comentarios útiles:

// Aplicamos 15% de descuento solo a clientes VIP con más de 10 órdenes
// según política comercial definida en JIRA-1234
if (customer.IsVIP && customer.OrderCount > 10)
{
    discount = price * 0.15m;
}

// Usamos Dictionary en lugar de List para O(1) lookup
// dado que este método se llama 10,000+ veces por request
var userCache = new Dictionary<int, User>();
```
## 3. Documentación XML Completa
### Regla 5: Marcar TODOs y FIXMEs con Contexto

- **Formato**: `// TODO(autor): descripción [JIRA-123]`
- **Ejemplo correcto**:

```csharp
// TODO(jperez): Migrar a Redis cuando el caché supere 10GB [ARCH-456]
var cache = new InMemoryCache();

// FIXME(mrodriguez): Este endpoint falla con >1000 items [BUG-789]
public async Task<List<User>> FetchAllUsersAsync() { }

// DEPRECATED: Usar GetUserV2Async() en su lugar - Remover en v3.0
public User GetUserV1(int id) { }
```

### Regla 6: Comentar Workarounds Temporales

```csharp
// WORKAROUND: AWS SDK bug con credenciales rotadas cada hora
// Issue: https://github.com/aws/aws-sdk-net/issues/1234
// Remover cuando se libere v3.7.200
if (DateTime.UtcNow.Hour == 0)
{
    await RefreshCredentialsAsync();
}
```

### Regla 4: Secciones de Código con Regions (C# - Usar con Moderación)

```csharp
✅ Correcto (agrupa lógica relacionada):

#region Database Operations

private async Task<User> GetUserFromDbAsync(int userId) { }
private async Task SaveUserToDbAsync(User user) { }

#endregion

❌ Evitar (sobre-uso que oculta complejidad):

#region Properties (100 propiedades)
#region Constructors (10 constructores)
#region Private Methods (50 métodos)
```

## 3. Plantillas de Documentación

### C# XMLDoc Completo

```csharp
/// <summary>
/// Procesa un pago mediante gateway configurado para el país del cliente.
/// </summary>
/// <param name="paymentRequest">Datos del pago a procesar</param>
/// <param name="cancellationToken">Token para cancelar la operación</param>
/// <returns>
/// Confirmación del pago con ID de transacción del gateway
/// </returns>
/// <exception cref="PaymentGatewayException">
/// Si el gateway rechaza la transacción
/// </exception>
/// <exception cref="InsufficientFundsException">
/// Si la cuenta no tiene fondos suficientes
/// </exception>
/// <remarks>
/// Este método es idempotente usando el paymentRequest.IdempotencyKey.
/// El timeout por defecto es 30 segundos configurado en appsettings.
/// </remarks>
/// <seealso cref="RefundPaymentAsync"/>
public async Task<PaymentConfirmation> ProcessPaymentAsync(
    PaymentRequest paymentRequest,
    CancellationToken cancellationToken = default)
{
    // Implementation...
}
```

## 4. Comentarios que DEBEN Evitarse

```csharp
❌ Comentarios malos:

// Esta función hace cosas
public void DoStuff() { }

// Loop
for (int i = 0; i < items.Length; i++) { }

// Código comentado (usar control de versiones)
// var oldImplementation = OldMethod();
// return oldImplementation;

// Comentario desactualizado
// Retorna el usuario (MENTIRA: ahora retorna null si no existe)
public User GetUser() { return null; }
```

## 5. Herramientas de Validación

### StyleCop (C#)

```xml
<!-- .editorconfig -->
[*.cs]

# SA1600: Elements should be documented
dotnet_diagnostic.SA1600.severity = warning

# SA1633: File should have header
dotnet_diagnostic.SA1633.severity = none

# SA1652: Enable XML documentation output
dotnet_diagnostic.SA1652.severity = warning
```

### SonarQube

```xml
<!-- Análisis de calidad de comentarios -->
<RuleSet Name="Documentation Rules">
  <Rule Id="S1135" Action="Warning" /> <!-- TODO sin asignar
  <Rule Id="S1186" Action="Warning" /> <!-- Métodos vacíos sin doc
  <Rule Id="S1133" Action="Info" />    <!-- Deprecated sin doc
</RuleSet>
```

## 6. Tabla de Referencia Rápida

| Escenario        | C# XMLDoc                               | Ejemplo                                           |
| ---------------- | --------------------------------------- | ------------------------------------------------- |
| Clase pública    | `/// <summary>`                         | `/// <summary>Gestiona usuarios</summary>`        |
| Método público   | `/// <summary>`, `<param>`, `<returns>` | `/// <returns>Usuario encontrado</returns>`       |
| Excepción        | `/// <exception>`                       | `/// <exception cref="NotFoundException">`        |
| Ejemplo          | `/// <example>`                         | `/// <example><code>var x = 1;</code></example>` |
| Enlace externo   | `/// <see cref>`                        | `/// <see cref="IUserRepository"/>`              |
| Deprecado        | `[Obsolete("mensaje")]` + `///`         | `[Obsolete("Usar GetUserV2")]`                    |
| TODO             | `// TODO(autor): [JIRA-123]`            | `// TODO(jperez): [JIRA-456] Optimizar`           |
| Decisión negocio | `// Razón: política comercial`          | `// Razón: JIRA-789 - descuento VIP`              |
| Workaround       | `// WORKAROUND: bug .NET 8`             | `// WORKAROUND: EF Core issue #12345`             |

## 7. Niveles de Documentación

| Visibilidad                 | Documentación Requerida                | Ejemplo                             |
| --------------------------- | -------------------------------------- | ----------------------------------- |
| `public` / `export`         | ✅ Obligatoria (XMLDoc/JSDoc completo) | APIs consumidas externamente        |
| `internal` / interno módulo | ⚠️ Recomendada (al menos summary)      | Helpers compartidos entre servicios |
| `private`                   | ❌ Opcional (solo si complejo)         | Métodos internos de clase           |

## 📖 Referencias

### Estándares relacionados

- [C# y .NET](/docs/fundamentos-corporativos/estandares/codigo/csharp-dotnet)
- [Código Limpio](/docs/fundamentos-corporativos/lineamientos/desarrollo/01-codigo-limpio)

### Convenciones relacionadas

- [Naming C#](./01-naming-csharp.md)
- [Estructura de Proyectos](./04-estructura-proyectos.md)

### Recursos externos

- [C# XML Documentation Comments](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/xmldoc/)
- [StyleCop Documentation Rules](https://github.com/DotNetAnalyzers/StyleCopAnalyzers/blob/master/documentation/DocumentationRules.md)
- [SonarQube C# Rules](https://rules.sonarsource.com/csharp/)

---

**Última revisión**: 26 de enero 2026
**Responsable**: Equipo de Arquitectura
