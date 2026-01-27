---
id: typescript
sidebar_position: 2
title: TypeScript
description: Estándares de Clean Code, principios SOLID y buenas prácticas para TypeScript y Node.js
---

# TypeScript

## 1. Propósito

Establecer los estándares técnicos de Clean Code y principios SOLID para garantizar que el código TypeScript sea legible, mantenible, type-safe y testeable.

> **Nota:** Para convenciones de nomenclatura (naming), consulta [Convenciones - Naming TypeScript](../../convenciones/codigo/02-naming-typescript.md).

## 2. Alcance

**Aplica a:**
- Proyectos Node.js con TypeScript 5.0+
- APIs REST con Express, NestJS, Fastify
- Servicios backend y microservicios
- Librerías y componentes reutilizables

**No aplica a:**
- JavaScript puro sin tipos
- Proyectos frontend (React, Angular, Vue)
- Scripts de automatización simples

## 3. Tecnologías y Herramientas Obligatorias

### Versiones Mínimas

- **TypeScript:** 5.0+
- **Node.js:** 18 LTS+ o 20 LTS+
- **ESLint:** 8.0+
- **Prettier:** 3.0+

### Herramientas de Calidad

**Análisis estático (obligatorio):**

```json
{
  "devDependencies": {
    "@typescript-eslint/parser": "^6.0.0",
    "@typescript-eslint/eslint-plugin": "^6.0.0",
    "eslint": "^8.50.0",
    "prettier": "^3.0.0",
    "eslint-config-prettier": "^9.0.0"
  }
}
```

**Instalación:**

```bash
npm install --save-dev @typescript-eslint/parser @typescript-eslint/eslint-plugin eslint prettier
```

### Configuración Estándar

**tsconfig.json:**

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "commonjs",
    "lib": ["ES2022"],
    "outDir": "./dist",
    "rootDir": "./src",
    "strict": true,
    "strictNullChecks": true,
    "strictFunctionTypes": true,
    "noImplicitAny": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noImplicitReturns": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true
  }
}
```

**.eslintrc.json:**

```json
{
  "parser": "@typescript-eslint/parser",
  "plugins": ["@typescript-eslint"],
  "extends": [
    "eslint:recommended",
    "plugin:@typescript-eslint/recommended",
    "prettier"
  ],
  "rules": {
    "@typescript-eslint/no-explicit-any": "error",
    "@typescript-eslint/explicit-function-return-type": "warn",
    "no-console": "warn"
  }
}
```

## 4. Principios de Clean Code

### Principio 1: Type Safety First

Usa el sistema de tipos de TypeScript completamente.

**✅ Correcto:**

```typescript
interface User {
  id: string;
  email: string;
  age: number;
}

function isAdult(user: User): boolean {
  return user.age >= 18;
}
```

**❌ Incorrecto:**

```typescript
function isAdult(user: any): boolean {  // ❌ any
  return user.age >= 18;
}
```

### Principio 2: Single Responsibility

Cada clase/función una responsabilidad.

**✅ Correcto:**

```typescript
class OrderService {
  constructor(
    private repository: OrderRepository,
    private validator: OrderValidator
  ) {}

  async createOrder(dto: CreateOrderDto): Promise<Order> {
    this.validator.validate(dto);
    const order = this.mapToEntity(dto);
    return await this.repository.save(order);
  }
}

class EmailService {
  async sendOrderConfirmation(order: Order): Promise<void> {
    // Solo responsabilidad de enviar emails
  }
}
```

**❌ Incorrecto:**

```typescript
class OrderService {
  async createOrder(dto: CreateOrderDto): Promise<Order> {
    // Mezcla validación, persistencia y email
    if (!dto.customerId) throw new Error('Invalid');
    const order = new Order(dto);
    await this.saveToDb(order);
    await this.sendEmail(order.customerEmail);  // ❌
    return order;
  }
}
```

## 5. Ejemplos Prácticos

### Ejemplo 1: Dependency Injection

**✅ Correcto:**

```typescript
interface Logger {
  log(message: string): void;
  error(message: string, error: Error): void;
}

class OrderProcessor {
  constructor(
    private readonly paymentGateway: PaymentGateway,
    private readonly logger: Logger
  ) {}

  async process(order: Order): Promise<PaymentResult> {
    this.logger.log(`Processing order ${order.id}`);
    try {
      return await this.paymentGateway.charge(order);
    } catch (error) {
      this.logger.error('Payment failed', error as Error);
      throw error;
    }
  }
}
```

### Ejemplo 2: Async/Await

**✅ Correcto:**

```typescript
async function getActiveOrders(): Promise<Order[]> {
  try {
    const orders = await orderRepository.findAll();
    return orders.filter(o => o.status === OrderStatus.Active);
  } catch (error) {
    logger.error('Failed to fetch orders', error);
    throw new DatabaseError('Unable to retrieve orders');
  }
}
```

**❌ Incorrecto:**

```typescript
function getActiveOrders(): Promise<Order[]> {
  return orderRepository.findAll()
    .then(orders => orders.filter(o => o.status === 'active'))  // ❌ Promise chains
    .catch(error => {
      console.log(error);  // ❌ console.log
      return [];  // ❌ Silenciar error
    });
}
```

### Ejemplo 3: Functional Programming

**✅ Correcto:**

```typescript
const activeUsers = users
  .filter(u => u.isActive && u.registrationDate > cutoffDate)
  .map(u => ({
    id: u.id,
    name: u.name,
    email: u.email
  }))
  .sort((a, b) => a.name.localeCompare(b.name));
```

**❌ Incorrecto:**

```typescript
const activeUsers: UserDto[] = [];
for (const u of users) {
  if (u.isActive && u.registrationDate > cutoffDate) {
    activeUsers.push({ id: u.id, name: u.name, email: u.email });
  }
}
activeUsers.sort((a, b) => a.name.localeCompare(b.name));
```

### Ejemplo 4: Error Handling

**✅ Correcto:**

```typescript
class OrderNotFoundError extends Error {
  constructor(orderId: string) {
    super(`Order ${orderId} not found`);
    this.name = 'OrderNotFoundError';
  }
}

async function getOrder(id: string): Promise<Order> {
  const order = await repository.findById(id);
  if (!order) {
    throw new OrderNotFoundError(id);
  }
  return order;
}
```

## 6. Mejores Prácticas

### Type Safety

✅ **Usar strict mode:** `"strict": true` en tsconfig  
✅ **Evitar any:** Preferir `unknown` o tipos específicos  
✅ **Usar type guards:** Para narrowing seguro  
✅ **Interfaces sobre types:** Para objetos (mejor extensibilidad)

### Async/Await

✅ **Siempre async/await:** Evitar Promise chains  
✅ **Manejo de errores:** try/catch en funciones async  
✅ **Promise.all:** Para operaciones paralelas  
✅ **No bloquear:** Evitar operaciones síncronas pesadas

### Inmutabilidad

✅ **Usar const:** Por defecto, let solo si necesario  
✅ **Readonly properties:** En interfaces y clases  
✅ **Spread operator:** Para copiar objetos/arrays  
✅ **Evitar mutación:** Preferir métodos funcionales

## 7. NO Hacer (Antipatrones)

### Antipatrón 1: Uso de `any`

❌ **NO** usar `any` para evadir el sistema de tipos

```typescript
function processData(data: any): any {  // ❌
  return data.map(item => item.value);
}
```

**Razón:** Pierde type safety, errores en runtime

**Alternativa:**

```typescript
interface DataItem {
  value: number;
}

function processData(data: DataItem[]): number[] {
  return data.map(item => item.value);
}
```

### Antipatrón 2: Callbacks en lugar de Promises

❌ **NO** usar callbacks anidados

```typescript
fs.readFile('file.txt', (err, data) => {
  if (err) throw err;
  processData(data, (err, result) => {  // ❌ Callback hell
    if (err) throw err;
    saveResult(result, (err) => {
      // ...
    });
  });
});
```

**Alternativa:**

```typescript
async function processFile(path: string): Promise<void> {
  const data = await fs.promises.readFile(path);
  const result = await processData(data);
  await saveResult(result);
}
```

### Antipatrón 3: Ignorar Errores

❌ **NO** usar catch vacío

```typescript
try {
  await riskyOperation();
} catch {  // ❌ Silenciar error
  // Nada
}
```

**Alternativa:**

```typescript
try {
  await riskyOperation();
} catch (error) {
  logger.error('Operation failed', error as Error);
  throw new OperationError('Failed to execute', { cause: error });
}
```

### Antipatrón 4: Mutación de Parámetros

❌ **NO** mutar parámetros de entrada

```typescript
function addUser(users: User[], newUser: User): void {
  users.push(newUser);  // ❌ Mutación
}
```

**Alternativa:**

```typescript
function addUser(users: readonly User[], newUser: User): User[] {
  return [...users, newUser];  // ✅ Inmutabilidad
}
```

## 8. Validación y Cumplimiento

**Criterios verificables:**

- [ ] Todos los proyectos usan TypeScript 5.0+
- [ ] `strict: true` habilitado en tsconfig
- [ ] ESLint configurado sin errores
- [ ] Prettier configurado
- [ ] No se usa `any` sin justificación
- [ ] Cobertura de pruebas >80%
- [ ] No se usan callbacks (solo async/await)
- [ ] Todas las funciones públicas tienen tipos de retorno

**Herramientas de validación:**

- **ESLint** - Análisis estático
- **TypeScript Compiler** - Validación de tipos
- **Prettier** - Formato de código
- **CI/CD** - Build falla si hay errores de tipos

## 9. Referencias

### Lineamientos Relacionados

- [Testing y Calidad](../../lineamientos/operabilidad/04-testing-y-calidad.md) - Estándares de calidad

### Principios Relacionados

- [Calidad desde el Diseño](../../principios/operabilidad/03-calidad-desde-el-diseno.md) - Fundamento de código limpio

### Convenciones Relacionadas

- [Naming - TypeScript](../../convenciones/codigo/02-naming-typescript.md) - Convenciones de nomenclatura
- [Comentarios de Código](../../convenciones/codigo/03-comentarios-codigo.md) - Documentación en código
- [Estructura de Proyectos](../../convenciones/codigo/04-estructura-proyectos.md) - Organización

### Otros Estándares

- [Testing Unitario](../testing/01-unit-tests.md) - Jest y pruebas
- [APIs REST](../apis/01-diseno-rest.md) - Diseño de APIs con TypeScript

### Documentación Externa

- [clean-code-typescript](https://github.com/labs42io/clean-code-typescript) - Guía adaptada
- [TypeScript Handbook](https://www.typescriptlang.org/docs/handbook/intro.html) - Documentación oficial
- [ESLint TypeScript](https://typescript-eslint.io/) - Plugin oficial
- [Clean Code (Robert C. Martin)](https://www.oreilly.com/library/view/clean-code/9780136083238/) - Libro fundamental
