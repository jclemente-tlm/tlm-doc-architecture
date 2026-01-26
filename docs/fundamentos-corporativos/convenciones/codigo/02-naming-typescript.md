---
id: naming-typescript
sidebar_position: 2
title: Naming - TypeScript
description: Convenciones de nomenclatura para TypeScript y JavaScript
---

## 1. Principio

Seguir las convenciones de la comunidad TypeScript/JavaScript garantiza código consistente, legible y compatible con las herramientas del ecosistema.

## 2. Reglas

### Regla 1: Clases, Tipos e Interfaces

- **Formato**: `PascalCase`
- **Interfaces**: Prefijo `I` opcional (no recomendado en TS moderno)
- **Types**: Prefijo `T` opcional
- **Ejemplo correcto**: `UserService`, `OrderDto`, `User`, `PaymentStatus`
- **Ejemplo incorrecto**: `userService`, `order_dto`, `payment_status`

```typescript
// ✅ Correcto
export class UserService {}
export interface User {}
export type OrderStatus = "pending" | "approved" | "rejected";
export enum PaymentMethod {
  CreditCard,
  DebitCard,
  PayPal,
}

// ❌ Incorrecto
export class userService {}
export interface user {}
export type order_status = "pending" | "approved";
```

### Regla 2: Funciones y Métodos

- **Formato**: `camelCase`
- **Ejemplo correcto**: `getUserById()`, `isActive()`, `processPayment()`
- **Ejemplo incorrecto**: `GetUserById()`, `IsActive()`, `process_payment()`

```typescript
// ✅ Correcto
export function getUserById(id: number): User {}
export const processPayment = async (orderId: string): Promise<void> => {};

// ❌ Incorrecto
export function GetUserById(id: number): User {}
export const process_payment = async (orderId: string): Promise<void> => {};
```

### Regla 3: Variables y Constantes

- **Variables**: `camelCase`
- **Constantes**: `UPPER_SNAKE_CASE` o `camelCase` (según contexto)
- **Ejemplo correcto**: `userId`, `orderTotal`, `MAX_RETRIES`, `API_BASE_URL`

```typescript
// ✅ Correcto
const userId = getCurrentUserId();
let orderTotal = 0;
const MAX_RETRIES = 3;
const API_BASE_URL = "https://api.talma.com";

// ❌ Incorrecto
const UserId = getCurrentUserId();
let OrderTotal = 0;
const max_retries = 3;
```

### Regla 4: Propiedades de Objetos/Interfaces

- **Formato**: `camelCase`
- **Ejemplo correcto**: `firstName`, `createdAt`, `isActive`
- **Ejemplo incorrecto**: `FirstName`, `created_at`

```typescript
// ✅ Correcto
interface User {
  id: number;
  firstName: string;
  lastName: string;
  createdAt: Date;
  isActive: boolean;
}

// ❌ Incorrecto
interface User {
  Id: number; // PascalCase
  first_name: string; // snake_case
  created_at: Date;
}
```

### Regla 5: Archivos

- **Componentes React**: `PascalCase.tsx` → `UserProfile.tsx`
- **Otros archivos**: `kebab-case.ts` → `user-service.ts`
- **Tests**: `{nombre}.spec.ts` o `{nombre}.test.ts`

```
// ✅ Correcto
user-service.ts
order-repository.ts
UserProfile.tsx
Button.tsx
user-service.spec.ts

// ❌ Incorrecto
UserService.ts  // Debería ser kebab-case
user_service.ts  // snake_case
UserProfile.ts  // Componente debe ser .tsx
```

### Regla 6: Carpetas

- **Formato**: `kebab-case`
- **Ejemplo**: `user-management/`, `payment-gateway/`, `api-client/`

```
src/
├── user-management/
├── payment-gateway/
├── shared/
│   ├── components/
│   ├── utils/
│   └── types/
```

## 3. Tabla de Referencia Rápida

| Elemento         | Convención  | Ejemplo           | Incorrecto        |
| ---------------- | ----------- | ----------------- | ----------------- |
| Clase            | PascalCase  | `UserService`     | `userService`     |
| Interfaz         | PascalCase  | `User` o `IUser`  | `user`            |
| Type             | PascalCase  | `OrderStatus`     | `order_status`    |
| Función          | camelCase   | `getUserById()`   | `GetUserById()`   |
| Variable         | camelCase   | `userId`          | `UserId`          |
| Constante        | UPPER_SNAKE | `MAX_RETRIES`     | `maxRetries`      |
| Propiedad        | camelCase   | `firstName`       | `FirstName`       |
| Enum             | PascalCase  | `PaymentMethod`   | `payment_method`  |
| Enum value       | PascalCase  | `CreditCard`      | `CREDIT_CARD`     |
| Archivo          | kebab-case  | `user-service.ts` | `UserService.ts`  |
| Componente React | PascalCase  | `UserProfile.tsx` | `userProfile.tsx` |

## 4. Casos Especiales

### React Components

```typescript
// ✅ Correcto
export const UserProfile: React.FC<Props> = ({ userId }) => {
  return <div>{userId}</div>;
};

// Archivo: UserProfile.tsx
```

### Async Functions

```typescript
// ✅ Correcto (no requiere sufijo Async)
export async function getUser(id: number): Promise<User> {
  return await api.get(`/users/${id}`);
}
```

### Boolean Variables/Functions

```typescript
// ✅ Correcto - Prefijos is/has/can
const isActive = true;
const hasPermission = user.role === "admin";
const canEdit = () => isActive && hasPermission;

// ❌ Incorrecto
const active = true; // No es claro que es boolean
const permission = user.role === "admin";
```

### Private Members (con #)

```typescript
class UserService {
  // ✅ Correcto - usar # para privados
  #apiKey: string;

  constructor(apiKey: string) {
    this.#apiKey = apiKey;
  }
}
```

## 5. Herramientas de Validación

### ESLint

```json
// .eslintrc.json
{
  "extends": ["@typescript-eslint/recommended"],
  "rules": {
    "@typescript-eslint/naming-convention": [
      "error",
      {
        "selector": "class",
        "format": ["PascalCase"]
      },
      {
        "selector": "interface",
        "format": ["PascalCase"]
      },
      {
        "selector": "variable",
        "format": ["camelCase", "UPPER_CASE"]
      },
      {
        "selector": "function",
        "format": ["camelCase"]
      }
    ]
  }
}
```

## 6. Excepciones

- **Variables de loop**: `i`, `j`, `k` aceptables
- **Destructuring**: Mantener nombres originales de APIs externas
- **React props**: Pueden usar PascalCase si es estándar del componente
- **Enums**: Valores pueden ser UPPER_CASE si representa constantes

## 📖 Referencias

### Estándares relacionados

- [TypeScript Clean Code](/docs/fundamentos-corporativos/estandares/codigo/typescript)

### Recursos externos

- [TypeScript Coding Guidelines](https://github.com/microsoft/TypeScript/wiki/Coding-guidelines)
- [Airbnb JavaScript Style Guide](https://github.com/airbnb/javascript)
- [Google TypeScript Style Guide](https://google.github.io/styleguide/tsguide.html)

---

**Última revisión**: 26 de enero 2026
**Responsable**: Equipo de Arquitectura
