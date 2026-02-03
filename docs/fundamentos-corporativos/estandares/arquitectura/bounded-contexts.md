# Bounded Contexts

## Contexto

Un bounded context es un límite explícito donde un modelo de dominio específico es aplicable. Sistemas monolíticos sin límites claros generan modelos de datos gigantes, acoplamiento global y equipos bloqueados. Bounded contexts permiten modelos diferentes para el mismo concepto según el contexto.

## Decisión

Identificar límites de contextos por capacidades de negocio (no por tecnología), donde cada contexto tiene su propio modelo de dominio, lenguaje ubicuo y equipo responsable.

## Estándares Obligatorios

### 1. Identificación por Capacidad de Negocio

**Criterios de delimitación:**

- Capacidad de negocio cohesiva (e.g., Billing, Inventory, Shipping)
- Lenguaje ubicuo diferente entre contextos
- Tasa de cambio independiente
- Autonomía de equipo

**Evitar delimitar por:**

- ❌ Tecnología (frontend/backend)
- ❌ Capas técnicas (presentation/business/data)
- ❌ Tipo de datos (maestros/transaccionales)

### 2. Context Mapping

**Patrones de relación:**

- **Shared Kernel:** Modelo compartido pequeño entre 2 contextos
- **Customer/Supplier:** Downstream depende de upstream
- **Conformist:** Downstream acepta modelo de upstream
- **Anticorruption Layer:** Traducción entre modelos
- **Open Host Service:** API pública estándar
- **Published Language:** Formato de intercambio estándar

### 3. Modelo por Contexto

Cada bounded context tiene:

- Propio modelo de dominio (entidades, value objects, agregados)
- Base de datos independiente
- Deployment independiente
- Equipo dueño

## Alineación con Industria

- **Domain-Driven Design (Eric Evans)** - Bounded Context pattern
- **Implementing Domain-Driven Design (Vaughn Vernon)**
- **Microsoft Cloud Design Patterns** - Domain Model pattern

## Validación de Cumplimiento

- ¿Los límites reflejan capacidades de negocio?
- ¿Cada contexto tiene lenguaje ubicuo documentado?
- ¿Los modelos son independientes entre contextos?
- ¿Hay context map documentado?

## Referencias

- [Domain-Driven Design, Eric Evans](https://www.domainlanguage.com/ddd/)
- [Bounded Context, Martin Fowler](https://martinfowler.com/bliki/BoundedContext.html)
- [Strategic Design with Context Mapping](https://www.infoq.com/articles/ddd-contextmapping/)
