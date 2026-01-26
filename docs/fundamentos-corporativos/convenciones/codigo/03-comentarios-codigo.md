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

### Regla 2: Documentar APIs Públicas (TypeScript - JSDoc)

- **Formato**: JSDoc con `/** */`
- **Obligatorio**: Funciones exportadas, clases e interfaces públicas
- **Ejemplo correcto**:

````typescript
/**
 * Valida que un correo electrónico cumpla con el formato corporativo.
 *
 * @param email - Dirección de correo a validar
 * @returns true si el email es válido y pertenece al dominio @talma.com
 * @throws {ValidationError} Si el formato del email es inválido
 *
 * @example
 * ```typescript
 * const isValid = validateCorporateEmail('user@talma.com'); // true
 * const isValid = validateCorporateEmail('user@gmail.com'); // false
 * ```
 */
export function validateCorporateEmail(email: string): boolean {
  // Implementation...
}
````

### Regla 3: NO Comentar Código Obvio

```typescript
❌ Evitar comentarios redundantes:

// Obtener usuario por ID
const user = await getUserById(userId);

// Incrementar contador
counter++;

// Retornar true
return true;
```

### Regla 4: Explicar Decisiones de Negocio o Complejidad

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

### Regla 5: Marcar TODOs y FIXMEs con Contexto

- **Formato**: `// TODO(autor): descripción [JIRA-123]`
- **Ejemplo correcto**:

```typescript
// TODO(jperez): Migrar a Redis cuando el caché supere 10GB [ARCH-456]
const cache = new InMemoryCache();

// FIXME(mrodriguez): Este endpoint falla con >1000 items [BUG-789]
async function fetchAllUsers() {}

// DEPRECATED: Usar getUserV2() en su lugar - Remover en v3.0
function getUserV1() {}
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

### Regla 7: Secciones de Código con Regions (C# - Usar con Moderación)

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

### TypeScript JSDoc Completo

````typescript
/**
 * Sincroniza inventario con sistema externo SAP.
 *
 * @param productIds - Lista de IDs de productos a sincronizar
 * @param options - Configuración de la sincronización
 * @param options.batchSize - Cantidad de productos por lote (default: 100)
 * @param options.retryAttempts - Reintentos ante falla (default: 3)
 *
 * @returns Resultado con productos sincronizados y fallidos
 *
 * @throws {SapConnectionError} Si no se puede conectar a SAP
 * @throws {ValidationError} Si algún productId es inválido
 *
 * @see {@link https://wiki.talma.com/sap-integration} para detalles
 *
 * @example
 * ```typescript
 * const result = await syncInventory([1, 2, 3], {
 *   batchSize: 50,
 *   retryAttempts: 5
 * });
 * console.log(`Sincronizados: ${result.success.length}`);
 * ```
 */
export async function syncInventory(
  productIds: number[],
  options: SyncOptions = {},
): Promise<SyncResult> {
  // Implementation...
}
````

## 4. Comentarios que DEBEN Evitarse

```typescript
❌ Comentarios malos:

// Esta función hace cosas
function doStuff() { }

// Loop
for (let i = 0; i < items.length; i++) { }

// Código comentado (usar control de versiones)
// const oldImplementation = () => { ... };
// return oldImplementation();

// Comentario desactualizado
// Retorna el usuario (MENTIRA: ahora retorna null si no existe)
function getUser() { return null; }
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

### TSDoc (TypeScript)

```json
// tsdoc.json
{
  "extends": ["@microsoft/tsdoc/tsdoc.json"],
  "noStandardTags": false,
  "tagDefinitions": [
    {
      "tagName": "@internal",
      "syntaxKind": "modifier"
    }
  ]
}
```

### ESLint

```json
{
  "plugins": ["jsdoc"],
  "rules": {
    "jsdoc/require-jsdoc": [
      "warn",
      {
        "require": {
          "FunctionDeclaration": true,
          "ClassDeclaration": true,
          "MethodDefinition": true
        }
      }
    ],
    "jsdoc/require-param": "warn",
    "jsdoc/require-returns": "warn",
    "jsdoc/check-types": "warn"
  }
}
```

## 6. Tabla de Referencia Rápida

| Escenario        | C#                                      | TypeScript                   |
| ---------------- | --------------------------------------- | ---------------------------- |
| Clase pública    | `/// <summary>`                         | `/** */`                     |
| Método público   | `/// <summary>`, `<param>`, `<returns>` | `@param`, `@returns`         |
| Excepción        | `/// <exception>`                       | `@throws`                    |
| Ejemplo          | `/// <example>`                         | `@example`                   |
| Enlace externo   | `/// <see cref>`                        | `@see`                       |
| Deprecado        | `[Obsolete("mensaje")]` + `///`         | `@deprecated`                |
| TODO             | `// TODO(autor): [JIRA-123]`            | `// TODO(autor): [JIRA-123]` |
| Decisión negocio | `// Razón: ...`                         | `// Razón: ...`              |
| Workaround       | `// WORKAROUND: ...`                    | `// WORKAROUND: ...`         |

## 7. Niveles de Documentación

| Visibilidad                 | Documentación Requerida                | Ejemplo                             |
| --------------------------- | -------------------------------------- | ----------------------------------- |
| `public` / `export`         | ✅ Obligatoria (XMLDoc/JSDoc completo) | APIs consumidas externamente        |
| `internal` / interno módulo | ⚠️ Recomendada (al menos summary)      | Helpers compartidos entre servicios |
| `private`                   | ❌ Opcional (solo si complejo)         | Métodos internos de clase           |

## 📖 Referencias

### Estándares relacionados

- [C# y .NET](/docs/fundamentos-corporativos/estandares/codigo/csharp-dotnet)
- [TypeScript](/docs/fundamentos-corporativos/estandares/codigo/typescript)

### Convenciones relacionadas

- [Naming C#](./01-naming-csharp.md)
- [Naming TypeScript](./02-naming-typescript.md)

### Recursos externos

- [C# XML Documentation Comments](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/xmldoc/)
- [TSDoc](https://tsdoc.org/)
- [JSDoc](https://jsdoc.app/)

---

**Última revisión**: 26 de enero 2026
**Responsable**: Equipo de Arquitectura
