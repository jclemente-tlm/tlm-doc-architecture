---
title: "TypeScript"
description: "Lineamientos de Clean Code, estilo, buenas prácticas y seguridad para TypeScript."
id: 02-typescript
sidebar_position: 2
---

## Introducción

Este documento adapta los principios de Clean Code para TypeScript, basado en la guía [clean-code-typescript](https://github.com/labs42io/clean-code-typescript), con ejemplos prácticos y recomendaciones clave.

## Objetivo

Promover un código legible, mantenible y seguro en proyectos TypeScript, aplicando Clean Code.

## Alcance

Aplica a todos los desarrolladores que trabajen con TypeScript en la organización.

---

## Principios clave de Clean Code en TypeScript

### 1. Nombres claros y significativos

- Usa nombres descriptivos para variables, funciones y clases.
- Evita abreviaturas, nombres genéricos y prefijos innecesarios.

**Correcto:**

```typescript
let userAge: number;
const customerEmail: string = '';
class InvoiceProcessor {}
```

**Incorrecto:**

```typescript
let a: number;
const ce = '';
class IP {}
```

### 2. Funciones cortas y de una sola responsabilidad (SRP)

- Cada función debe hacer solo una cosa.
- Prefiere funciones pequeñas y reutilizables.

**Correcto:**

```typescript
function sendEmail(to: string, body: string): void { /* ... */ }
```

**Incorrecto:**

```typescript
function processOrder() {
  // ...
  // envío de email incluido aquí (mala práctica)
}
```

### 3. Evita duplicidad (DRY)

- Extrae lógica repetida en funciones o utilidades reutilizables.

**Correcto:**

```typescript
function isAdult(user: User): boolean {
  return user.age >= 18;
}
```

**Incorrecto:**

```typescript
if (user.age < 18) { /* ... */ }
if (user.age < 18) { /* ... */ }
```

### 4. Simplicidad (KISS)

- Prefiere soluciones simples y directas.
- Evita lógica innecesariamente compleja.

**Correcto:**

```typescript
if (user.isActive) { /* ... */ }
```

**Incorrecto:**

```typescript
if ((user.status === 1 || user.status === 2) && !user.isBanned) { /* ... */ }
```

### 5. No escribas código que no necesitas (YAGNI)

- Implementa solo lo necesario para el requerimiento actual.

**Incorrecto:**

```typescript
// Métodos y clases no usados ni requeridos
function futureFeature() { /* ... */ }
```

### 6. Manejo adecuado de errores

- Usa excepciones específicas y mensajes claros.
- No ocultes errores ni uses catch vacíos.

**Correcto:**

```typescript
try {
  // ...
} catch (error) {
  console.error(error.message);
}
```

**Incorrecto:**

```typescript
try {
  // ...
} catch {}
```

### 7. Comentarios útiles y documentación

- Comenta solo lo necesario para aclarar intenciones o casos especiales.
- Prefiere código autoexplicativo.

**Correcto:**

```typescript
// Calcula el total del pedido incluyendo impuestos
function calculateTotal() { /* ... */ }
```

**Incorrecto:**

```typescript
// ct
function ct() { /* ... */ }
```

### 8. Organización y modularidad

- Separa responsabilidades en archivos y módulos distintos.
- Usa carpetas y namespaces para organizar el código.

**Correcto:**

```typescript
// src/orders/services/OrderService.ts
export class OrderService { /* ... */ }
```

**Incorrecto:**

```typescript
// Todo en un solo archivo grande
```

### 9. Colecciones y estructuras de control

- Prefiere métodos funcionales (`map`, `filter`, `reduce`) para manipular colecciones.
- Evita bucles anidados y lógica compleja en una sola función.

**Correcto:**

```typescript
const activeUsers = users.filter(u => u.isActive);
```

**Incorrecto:**

```typescript
const activeUsers: User[] = [];
for (const u of users) {
  if (u.isActive) activeUsers.push(u);
}
```

### 10. Manejo de dependencias

- Usa inyección de dependencias para facilitar pruebas y mantenimiento.
- Evita dependencias ocultas o acoplamiento fuerte.

**Correcto:**

```typescript
class OrderService {
  constructor(private emailSender: EmailSender) {}
}
```

**Incorrecto:**

```typescript
class OrderService {
  private emailSender = new EmailSender();
}
```

### 11. Pruebas y refactorización

- Escribe pruebas unitarias para lógica crítica.
- Refactoriza regularmente para mantener el código limpio.
- Usa mocks y fakes para aislar dependencias en pruebas.

**Correcto:**

```typescript
test('calculateTotal retorna el valor correcto', () => {
  // ...
});
```

### 12. Antipatrones comunes a evitar

- Métodos y clases demasiado grandes.
- Variables globales o estáticas innecesarias.
- Código duplicado o sin uso.
- Comentarios que explican código confuso en vez de refactorizarlo.

---

## Buenas prácticas adicionales

- Usa linters (ESLint) y formateadores (Prettier).
- Aplica principios SOLID.
- Mantén el código alineado y ordenado.
- Prefiere `const` y `let`, evita `var`.
- Usa tipado estricto siempre que sea posible.
- Prefiere arrow functions para callbacks.

## Seguridad

- Valida y escapa entradas del usuario.
- No expongas información sensible en el código ni en logs.

## Referencias

- [clean-code-typescript](https://github.com/labs42io/clean-code-typescript)
- [Guía oficial de TypeScript](https://www.typescriptlang.org/docs/)
- [ESLint](https://eslint.org/docs/latest/)
- [Prettier](https://prettier.io/docs/en/index.html)
- [Principios SOLID](https://es.wikipedia.org/wiki/SOLID)
- [Clean Code (Robert C. Martin)](https://www.oreilly.com/library/view/clean-code/9780136083238/)

## Última revisión

- Fecha: 2025-08-08
- Responsable: Equipo de Arquitectura
