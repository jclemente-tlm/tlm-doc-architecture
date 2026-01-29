---
id: typescript
sidebar_position: 2
title: TypeScript
description: Estándares de Clean Code, principios SOLID y buenas prácticas para TypeScript y Node.js
---

# Estándar Técnico — TypeScript

---

## 1. Propósito
Garantizar código TypeScript type-safe, legible y mantenible mediante strict mode, ESLint/Prettier, async/await, inyección de dependencias y principios SOLID.

---

## 2. Alcance

**Aplica a:**
- Proyectos Node.js con TypeScript 5.0+
- APIs REST con Express, NestJS, Fastify
- Servicios backend y microservicios
- Librerías reutilizables

**No aplica a:**
- JavaScript puro sin tipos
- Proyectos frontend (React, Angular, Vue)
- Scripts de automatización simples

---

## 3. Tecnologías Aprobadas

| Componente | Tecnología | Versión mínima | Observaciones |
|-----------|------------|----------------|---------------|
| **Lenguaje** | TypeScript | 5.0+ | Strict mode habilitado |
| **Runtime** | Node.js | 18 LTS+ / 20 LTS+ | LTS recomendado |
| **Linter** | ESLint | 8.0+ | Reglas TypeScript |
| **Formatter** | Prettier | 3.0+ | Formato automático |
| **Parser** | @typescript-eslint/parser | 6.0+ | Parser ESLint para TS |
| **Plugin** | @typescript-eslint/eslint-plugin | 6.0+ | Reglas TS específicas |
| **Testing** | Jest / Vitest | 29+ / 1.0+ | Framework de pruebas |

> El uso de tecnologías no listadas requiere aprobación de Arquitectura.

---

## 4. Requisitos Obligatorios 🔴

- [ ] TypeScript 5.0+ con strict mode habilitado
- [ ] ESLint + Prettier configurados
- [ ] `noImplicitAny`, `strictNullChecks` habilitados
- [ ] Tipos explícitos en funciones públicas
- [ ] Async/await (NO callbacks ni promesas sin await)
- [ ] Inyección de dependencias (NO `new` en lógica)
- [ ] Interfaces para contratos (NO `any`)
- [ ] Funciones con responsabilidad única (<20 líneas)
- [ ] Clases cohesivas (<300 líneas)
- [ ] Error handling con tipos específicos
- [ ] Imports organizados (libs externas → internas → relativas)
- [ ] NO `console.log` en producción (usar logger estructurado)

---

## 5. Prohibiciones

- ❌ Tipo `any` (usar `unknown` si es necesario)
- ❌ Operaciones I/O síncronas (usar async/await)
- ❌ Callbacks anidados (callback hell)
- ❌ `console.log` en código de producción
- ❌ Funciones con >3 parámetros (usar objetos de configuración)
- ❌ Type assertions (`as`) sin justificación
- ❌ Código comentado (eliminar, usar Git)

---

## 6. Configuración Mínima

```json
// tsconfig.json
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
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist"]
}
```

```json
// .eslintrc.json
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

```typescript
// Ejemplo de servicio con DI y async/await
export interface IOrderRepository {
  findById(orderId: string): Promise<Order | null>;
}

export class OrderService {
  constructor(private readonly orderRepository: IOrderRepository) {}
  
  async getOrder(orderId: string): Promise<Order> {
    if (!orderId) {
      throw new Error('Order ID is required');
    }
    
    const order = await this.orderRepository.findById(orderId);
    
    if (!order) {
      throw new Error(`Order ${orderId} not found`);
    }
    
    return order;
  }
}
```

---

## 7. Validación

```bash
# Type checking
npx tsc --noEmit

# Linting
npx eslint src/**/*.ts

# Formatting
npx prettier --check "src/**/*.ts"

# Tests
npm test

# Build
npm run build

# Verificar no hay 'any'
grep -r "any" src/ --include="*.ts" | grep -v "node_modules"
```

**Métricas de cumplimiento:**

| Métrica | Target | Verificación |
|---------|--------|--------------|  
| Strict mode habilitado | 100% | `"strict": true` en tsconfig.json |
| Tipo `any` | 0 | ESLint `no-explicit-any` error |
| Funciones <20 líneas | >90% | ESLint `max-lines-per-function` |
| Code coverage | >80% | Jest coverage report |

Incumplimientos deben corregirse o documentarse mediante excepción aprobada.

---

## 8. Referencias

- [Convenciones - Naming TypeScript](../../convenciones/codigo/02-naming-typescript.md)
- [Unit Tests](../testing/01-unit-tests.md)
- [TypeScript Documentation](https://www.typescriptlang.org/docs/)
- [Clean Code TypeScript](https://github.com/labs42io/clean-code-typescript)
- [Node.js Best Practices](https://github.com/goldbergyoni/nodebestpractices)
