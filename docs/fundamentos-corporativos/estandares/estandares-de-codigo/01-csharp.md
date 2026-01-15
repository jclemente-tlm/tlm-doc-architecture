---
title: "C# y .NET"
description: "Lineamientos de Clean Code, estilo, buenas prácticas y seguridad para C# y .NET."
id: 01-csharp
sidebar_position: 1
---

## Introducción

Este documento resume y adapta los principios de Clean Code para C# y .NET, basado en la guía [clean-code-dotnet](https://github.com/thangchung/clean-code-dotnet), con ejemplos prácticos y recomendaciones clave.

## Objetivo

Promover un código legible, mantenible y seguro en proyectos C# y .NET, aplicando Clean Code.

## Alcance

Aplica a todos los desarrolladores que trabajen con C# y .NET en la organización.

---

## Principios clave de Clean Code en C #

### 1. Nombres claros y significativos

- Usa nombres descriptivos para variables, funciones y clases.
- Evita abreviaturas, nombres genéricos y prefijos innecesarios.

**Correcto:**

```csharp
int userAge;
string customerEmail;
class InvoiceProcessor {}
```

**Incorrecto:**

```csharp
int a;
string ce;
class IP {}
```

### 2. Funciones cortas y de una sola responsabilidad (SRP)

- Cada función debe hacer solo una cosa.
- Prefiere funciones pequeñas y reutilizables.

**Correcto:**

```csharp
void SendEmail(string to, string body) { /* ... */ }
```

**Incorrecto:**

```csharp
void ProcessOrder() {
  // ...
  // envío de email incluido aquí (mala práctica)
}
```

### 3. Evita duplicidad (DRY)

- Extrae lógica repetida en funciones o clases reutilizables.

**Correcto:**

```csharp
bool IsAdult(User user) => user.Age >= 18;
```

**Incorrecto:**

```csharp
if (user.Age < 18) { /* ... */ }
if (user.Age < 18) { /* ... */ }
```

### 4. Simplicidad (KISS)

- Prefiere soluciones simples y directas.
- Evita lógica innecesariamente compleja.

**Correcto:**

```csharp
if (user.IsActive) { /* ... */ }
```

**Incorrecto:**

```csharp
if ((user.Status == 1 || user.Status == 2) && !user.IsBanned) { /* ... */ }
```

### 5. No escribas código que no necesitas (YAGNI)

- Implementa solo lo necesario para el requerimiento actual.

**Incorrecto:**

```csharp
// Métodos y clases no usados ni requeridos
void FutureFeature() { /* ... */ }
```

### 6. Manejo adecuado de errores

- Usa excepciones específicas y mensajes claros.
- No ocultes errores ni uses catch vacíos.

**Correcto:**

```csharp
try {
  // ...
} catch (FileNotFoundException ex) {
  LogError(ex.Message);
}
```

**Incorrecto:**

```csharp
try {
  // ...
} catch { }
```

### 7. Comentarios útiles y documentación

- Comenta solo lo necesario para aclarar intenciones o casos especiales.
- Prefiere código autoexplicativo.

**Correcto:**

```csharp
// Calcula el total del pedido incluyendo impuestos
void CalculateTotal() { /* ... */ }
```

**Incorrecto:**

```csharp
// ct
void ct() { /* ... */ }
```

### 8. Organización y modularidad

- Separa responsabilidades en archivos y clases distintas.
- Usa namespaces y carpetas para organizar el código.

**Correcto:**

```csharp
namespace Talma.Orders.Services {
  public class OrderService { /* ... */ }
}
```

### 9. Colecciones y estructuras de control

- Prefiere LINQ y métodos funcionales para manipular colecciones.
- Evita bucles anidados y lógica compleja en una sola función.

**Correcto:**

```csharp
var activeUsers = users.Where(u => u.IsActive).ToList();
```

**Incorrecto:**

```csharp
List<User> activeUsers = new List<User>();
foreach (var u in users) {
  if (u.IsActive) activeUsers.Add(u);
}
```

### 10. Manejo de dependencias

- Usa inyección de dependencias para facilitar pruebas y mantenimiento.
- Evita dependencias ocultas o acoplamiento fuerte.

**Correcto:**

```csharp
public class OrderService {
  private readonly IEmailSender _emailSender;
  public OrderService(IEmailSender emailSender) {
    _emailSender = emailSender;
  }
}
```

**Incorrecto:**

```csharp
public class OrderService {
  private EmailSender _emailSender = new EmailSender();
}
```

### 11. Pruebas y refactorización

- Escribe pruebas unitarias para lógica crítica.
- Refactoriza regularmente para mantener el código limpio.
- Usa mocks y fakes para aislar dependencias en pruebas.

**Correcto:**

```csharp
[Test]
public void CalculateTotal_ReturnsCorrectValue() {
  // ...
}
```

### 12. Antipatrones comunes a evitar

- Métodos y clases demasiado grandes.
- Variables globales o estáticas innecesarias.
- Código duplicado o sin uso.
- Comentarios que explican código confuso en vez de refactorizarlo.

---

## Buenas prácticas adicionales

- Usa herramientas de análisis estático y linters.
- Aplica principios SOLID.
- Mantén el código alineado y ordenado.

## Seguridad

- Valida entradas del usuario.
- No expongas información sensible en logs.

## Referencias

- [clean-code-dotnet](https://github.com/thangchung/clean-code-dotnet)
- [Guía de estilo de C#](https://learn.microsoft.com/es-es/dotnet/csharp/fundamentals/coding-style/coding-conventions)
- [Principios SOLID](https://es.wikipedia.org/wiki/SOLID)
- [Clean Code (Robert C. Martin)](https://www.oreilly.com/library/view/clean-code/9780136083238/)

## Última revisión

- Fecha: 2025-08-08
- Responsable: Equipo de Arquitectura
