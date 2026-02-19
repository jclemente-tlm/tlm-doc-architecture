<!--
GUÍA DE USO DE LA PLANTILLA:

🎯 ADAPTA LA DENSIDAD AL TEMA:
- Temas complejos (arquitecturas, patrones): 700-800 líneas con múltiples secciones
- Temas moderados (prácticas, tecnologías): 300-500 líneas
- Temas simples (convenciones, principios básicos): 150-300 líneas

✅ INCLUYE SOLO LO NECESARIO:
- "## Stack Tecnológico": Solo para estándares de tecnologías específicas (SIEMPRE con versiones exactas)
- "Conceptos Fundamentales": SIEMPRE (pero adapta subsecciones según complejidad)
- "### Ejemplo Comparativo": Si hay antipatrón común que mostrar
- "### Diagrama Conceptual": Solo si ayuda a entender (no por obligación)
- "## [Sección específica]": Solo si el tema lo requiere (ej: Estructura de Proyecto para arquitecturas)
- "## Implementación: X": Múltiples solo si hay varios aspectos técnicos distintos
- "## Beneficios en Práctica": Para patrones/arquitecturas con casos de uso claros
- "### MAY (Opcional)": Solo si existen opciones adicionales reales

❌ EVITA RELLENO:
- No agregues secciones "porque están en la plantilla"
- No infles ejemplos innecesariamente
- No dupliques información entre secciones
- Código conciso y directo al punto

🌐 IDIOMA Y TERMINOLOGÍA:
- **Contenido en ESPAÑOL**: Toda la documentación, explicaciones y texto descriptivo
- **Inglés solo para**:
  - Nombres de tecnologías CON VERSIÓN (PostgreSQL 16, .NET 8+, Kafka 3.6, Redis 7.2)
  - Términos técnicos establecidos sin traducción natural (refactoring, mocking, deployment)
  - Nombres de patrones reconocidos (Hexagonal Architecture, CQRS, Event Sourcing)
  - Código fuente (C#, YAML, SQL)
- **Traduce cuando sea posible**: "pruebas unitarias" en vez de "unit testing", "implementación" en vez de "implementation"
- **Evita spanglish**: "deployear", "commitear", "pushear" → usar "desplegar", "confirmar", "subir"
- **SIEMPRE especifica versiones**: "PostgreSQL 16.1", no solo "PostgreSQL"; ".NET 8+", no solo ".NET"

📏 REFERENCIA DE DENSIDAD:
- hexagonal-architecture.md: 783 líneas (justificado: patrón complejo)
- yagni-principle.md: 263 líneas (justificado: principio simple)
-->

---

id: [nombre-estandar]
sidebar_position: [número]
title: [Título del Estándar]
description: [Descripción breve técnica]

---

# [Título del Estándar]

## Contexto

Este estándar define [qué es brevemente]. Complementa el [lineamiento de X](../../lineamientos/categoria/nombre.md) asegurando [valor que aporta].

**Decisión arquitectónica:** [ADR-XXX: Título](../../decisiones-de-arquitectura/adr-xxx.md) (si existe)

---

## Stack Tecnológico (si aplica)

> 💡 **Incluye esta sección para estándares sobre tecnologías/herramientas específicas**
>
> - Ejemplo: Estándares de Kafka, PostgreSQL, Redis, EF Core, API Gateway
> - NO incluyas para conceptos abstractos (YAGNI, SOLID, patrones arquitectónicos genéricos)
> - SIEMPRE especifica versiones exactas (mínimas con +)

| Componente      | Tecnología          | Versión | Uso                                 |
| --------------- | ------------------- | ------- | ----------------------------------- |
| **[Categoría]** | [Nombre tecnología] | [X.Y+]  | [Descripción concisa del propósito] |

**Ejemplo:**

| Componente        | Tecnología   | Versión | Uso                                       |
| ----------------- | ------------ | ------- | ----------------------------------------- |
| **Framework**     | ASP.NET Core | 8.0+    | Framework base API REST                   |
| **Base de datos** | PostgreSQL   | 16+     | RDBMS principal con Npgsql + EF Core 8.0+ |
| **Resilience**    | Polly        | 8.0+    | Circuit breaker, retry, timeout           |

---

## Conceptos Fundamentales

### ¿Qué es [Concepto Principal]?

```yaml
# ✅ Explicación clara del concepto
# Objetivo: Definición breve, componentes clave, beneficios principales
# Extensión: 20-40 líneas para temas simples, 50-100 para temas complejos

Concepto Central: [Definición breve y directa]

Componentes:
  1. [Componente 1]: [Descripción]
  2. [Componente 2]: [Descripción]

Beneficios: ✅ [Beneficio 1]
  ✅ [Beneficio 2]
  ✅ [Beneficio 3]
```

### Ejemplo Comparativo (si aplica)

> 💡 **Incluye solo si existe un antipatrón común que los desarrolladores cometen**

```csharp
// ❌ MALO: [Antipatrón o forma incorrecta]

[Código de ejemplo incorrecto conciso]

// ✅ BUENO: [Forma correcta]

[Código de ejemplo correcto conciso]
```

### Diagrama Conceptual (si aplica)

> 💡 **Incluye solo si ayuda a visualizar flujos/estructuras complejas**

```mermaid
graph TB
    [Diagrama que explica el concepto visualmente]
```

---

## [Sección específica del tema]

> 💡 **Incluye secciones adicionales solo si el tema las requiere:**
>
> - "Estructura de Proyecto" → para arquitecturas/patrones complejos
> - "Principios de [Tema]" → si hay múltiples principios a detallar
> - "Code Smells y Soluciones" → para prácticas de desarrollo
> - "Componentes Principales" → para frameworks/librerías
> - "Configuración" → para herramientas/infraestructura
>
> **NO agregues secciones "por completar" - solo las que aporten valor real**

[Contenido específico con ejemplos concisos del stack real]

---

## Implementación: [Aspecto 1]

> 💡 **Usa "## Implementación: X" cuando hay múltiples aspectos técnicos distintos**
>
> - Ejemplos: Domain Layer, Application Layer, Infrastructure Layer
> - Si es un solo aspecto, usa nombre directo: "## Configuración" o "## Uso"

```csharp
// ✅ Código del stack real (.NET 8+, PostgreSQL, etc.)
// Configuraciones concretas
// Ejemplos prácticos directos
// Sin relleno ni código genérico
```

## Implementación: [Aspecto 2]

> 💡 **Incluye solo si hay aspectos técnicos sustancialmente diferentes**

[Implementación concisa del segundo aspecto]

---

## Beneficios en Práctica

> 💡 **Incluye esta sección para patrones/arquitecturas con casos de uso claros**
>
> - Escenarios de cambio (migración de DB, agregar protocolo, etc.)
> - Comparación de esfuerzo con/sin el patrón
> - OMITE si los beneficios son obvios o ya están en Conceptos Fundamentales

```yaml
# ✅ Casos de uso reales en Talma (2-3 casos concretos máximo)

Caso 1: [Escenario específico]
  Cambio necesario: [Qué se debe cambiar]
  Cambios NO necesarios:
    ✅ [Qué permanece sin cambios]

  Tiempo: [Estimación realista]
```

---

## Requisitos Técnicos

### MUST (Obligatorio)

- **MUST** [requisito crítico mínimo]
- **MUST** [otro requisito obligatorio]

### SHOULD (Fuertemente recomendado)

- **SHOULD** [mejor práctica recomendada]
- **SHOULD** [otra recomendación]

### MAY (Opcional)

- **MAY** [opción adicional útil]
- **MAY** [otra característica opcional]

### MUST NOT (Prohibido)

- **MUST NOT** [antipatrón a evitar]
- **MUST NOT** [práctica prohibida]

---

## Referencias

[Links relevantes]
