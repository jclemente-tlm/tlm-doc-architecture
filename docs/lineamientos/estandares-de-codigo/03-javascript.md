---
title: "JavaScript"
description: "Lineamientos de Clean Code, estilo, buenas prácticas y seguridad para JavaScript."
id: 03-javascript
sidebar_position: 3
---

## Introducción

Este documento adapta los principios de Clean Code para JavaScript, basado en la guía [clean-code-javascript](https://github.com/ryanmcdermott/clean-code-javascript), con ejemplos prácticos y recomendaciones clave.

## Objetivo

Promover un código legible, mantenible y seguro en proyectos JavaScript, aplicando Clean Code.

## Alcance

Aplica a todos los desarrolladores que trabajen con JavaScript en la organización.

---

## Principios clave de Clean Code en JavaScript

### 1. Nombres claros y significativos

- Usa nombres descriptivos para variables, funciones y clases.
- Evita abreviaturas, nombres genéricos y prefijos innecesarios.

**Correcto:**

```javascript
let userAge;
const customerEmail = '';
class InvoiceProcessor {}
```

**Incorrecto:**

```javascript
let a;
const ce = '';
class IP {}
```

### 2. Funciones cortas y de una sola responsabilidad (SRP)

- Cada función debe hacer solo una cosa.
- Prefiere funciones pequeñas y reutilizables.

**Correcto:**

```javascript
function sendEmail(to, body) { /* ... */ }
```

**Incorrecto:**

```javascript
function processOrder() {
  // ...
  // envío de email incluido aquí (mala práctica)
}
```

### 3. Evita duplicidad (DRY)

- Extrae lógica repetida en funciones o utilidades reutilizables.

**Correcto:**

```javascript
function isAdult(user) {
  return user.age >= 18;
}
```

**Incorrecto:**

```javascript
if (user.age < 18) { /* ... */ }
if (user.age < 18) { /* ... */ }
```

### 4. Simplicidad (KISS)

- Prefiere soluciones simples y directas.
- Evita lógica innecesariamente compleja.

**Correcto:**

```javascript
if (user.isActive) { /* ... */ }
```

**Incorrecto:**

```javascript
if ((user.status === 1 || user.status === 2) && !user.isBanned) { /* ... */ }
```

### 5. No escribas código que no necesitas (YAGNI)

- Implementa solo lo necesario para el requerimiento actual.

**Incorrecto:**

```javascript
// Métodos y clases no usados ni requeridos
function futureFeature() { /* ... */ }
```

### 6. Manejo adecuado de errores

- Usa excepciones específicas y mensajes claros.
- No ocultes errores ni uses catch vacíos.

**Correcto:**

```javascript
try {
  // ...
} catch (error) {
  console.error(error.message);
}
```

**Incorrecto:**

```javascript
try {
  // ...
} catch {}
```

### 7. Comentarios útiles y documentación

- Comenta solo lo necesario para aclarar intenciones o casos especiales.
- Prefiere código autoexplicativo.

**Correcto:**

```javascript
// Calcula el total del pedido incluyendo impuestos
function calculateTotal() { /* ... */ }
```

**Incorrecto:**

```javascript
// ct
function ct() { /* ... */ }
```

### 8. Organización y modularidad

- Separa responsabilidades en archivos y módulos distintos.
- Usa carpetas para organizar el código.

**Correcto:**

```javascript
// src/orders/services/orderService.js
export class OrderService { /* ... */ }
```

**Incorrecto:**

```javascript
// Todo en un solo archivo grande
```

### 9. Colecciones y estructuras de control

- Prefiere métodos funcionales (`map`, `filter`, `reduce`) para manipular colecciones.
- Evita bucles anidados y lógica compleja en una sola función.

**Correcto:**

```javascript
const activeUsers = users.filter(u => u.isActive);
```

**Incorrecto:**

```javascript
const activeUsers = [];
for (const u of users) {
  if (u.isActive) activeUsers.push(u);
}
```

### 10. Manejo de dependencias

- Usa inyección de dependencias (cuando sea posible) para facilitar pruebas y mantenimiento.
- Evita dependencias ocultas o acoplamiento fuerte.

**Correcto:**

```javascript
class OrderService {
  constructor(emailSender) {
    this.emailSender = emailSender;
  }
}
```

**Incorrecto:**

```javascript
class OrderService {
  constructor() {
    this.emailSender = new EmailSender();
  }
}
```

### 11. Pruebas y refactorización

- Escribe pruebas unitarias para lógica crítica.
- Refactoriza regularmente para mantener el código limpio.
- Usa mocks y fakes para aislar dependencias en pruebas.

**Correcto:**

```javascript
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
- Prefiere arrow functions para callbacks.

## Seguridad

- Valida y escapa entradas del usuario.
- No expongas información sensible en el código ni en logs.

## Referencias

- [clean-code-javascript](https://github.com/ryanmcdermott/clean-code-javascript)
- [Guía de estilo de JavaScript](https://github.com/airbnb/javascript)
- [ESLint](https://eslint.org/docs/latest/)
- [Prettier](https://prettier.io/docs/en/index.html)
- [Principios SOLID](https://es.wikipedia.org/wiki/SOLID)
- [Clean Code (Robert C. Martin)](https://www.oreilly.com/library/view/clean-code/9780136083238/)

## Última revisión

- Fecha: 2025-08-08
- Responsable: Equipo de Arquitectura
