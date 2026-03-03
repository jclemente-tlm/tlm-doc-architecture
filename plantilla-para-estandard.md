<!--
GUÍA DE USO DE LA PLANTILLA:

🎯 ADAPTA LA DENSIDAD AL TEMA:
- Temas complejos (arquitecturas, patrones): 700-800 líneas con múltiples secciones
- Temas moderados (prácticas, tecnologías): 300-500 líneas
- Temas simples (convenciones, principios básicos): 150-300 líneas

✅ INCLUYE SOLO LO NECESARIO:
- "## Stack Tecnológico": Solo para estándares de tecnologías específicas (SIEMPRE con versiones exactas)
- Secciones conceptuales con **nombres propios descriptivos** directamente como `##` (ej: `## ¿Qué es Distributed Tracing?`, `## Anatomía de un Trace`)
- Si hay múltiples secciones conceptuales, déjalas como `##` planas con nombres descriptivos propios — nunca las anijes bajo un agrupador genérico
- "### Ejemplo Comparativo": Si hay antipatrón común que mostrar
- "### Diagrama Conceptual": Solo si ayuda a entender (no por obligación)
- "## [Sección específica]": Solo si el tema lo requiere (ej: Estructura de Proyecto para arquitecturas)
- "## Implementación: X": Múltiples solo si hay varios aspectos técnicos distintos
- "## Beneficios en Práctica": Para patrones/arquitecturas con casos de uso claros
- "### MAY (Opcional)": Solo si existen opciones adicionales reales

🗂️ NOMBRES DE SECCIONES:
- Cada sección `##` debe tener nombre propio que describa su contenido específico
- Evita agrupadores genéricos como "Conceptos Fundamentales", "Contenido", "Información General" — no comunican nada
- Si un grupo natural existe, nómbralo por lo que contiene: `## Anatomía de un Trace`, `## Flujo de Autenticación`, `## Modelo de Permisos`
- Regla práctica: si no puedes nombrar el grupo sin usar una palabra genérica, déjalo como secciones `##` planas independientes
- ❌ **Nunca numeres secciones**: `## 1. Distributed Tracing`, `## 2. Correlation IDs` → el anchor cambia si reordenas y los links internos se rompen

❌ EVITA RELLENO:
- No agregues secciones "porque están en la plantilla"
- No infles ejemplos innecesariamente
- No dupliques información entre secciones
- Código conciso y directo al punto

💬 CALLOUTS DOCUSAURUS (:::tipo):
- **:::tip** → dato útil no crítico, truco de implementación
- **:::note** → referencia a otro estándar o indica responsabilidad de Plataforma
- **:::warning** → consecuencia de no cumplir o error frecuente
- **:::info** → contexto adicional que no es advertencia ni truco
- Usa callouts con moderación — máximo uno por sección, nunca como sustituto de contenido real

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
tags: [categoria, tecnología]

---

# [Título del Estándar]

## Contexto

Este estándar define [qué es brevemente]. Complementa el [lineamiento de X](../../lineamientos/categoria/nombre.md) asegurando [valor que aporta].

**Decisión arquitectónica:** [ADR-XXX: Título](../../adrs/adr-xxx.md) (si existe)

---

## Stack Tecnológico (si aplica)

> 💡 **Incluye esta sección para estándares sobre tecnologías/herramientas específicas**
>
> - Ejemplo: Estándares de Kafka, PostgreSQL, Redis, EF Core, API Gateway
> - NO incluyas para conceptos abstractos (YAGNI, SOLID, patrones arquitectónicos genéricos)
> - SIEMPRE especifica versiones exactas (mínimas con +)
>
> **Ejemplo de tabla:**
>
> | Componente        | Tecnología   | Versión | Uso                                       |
> | ----------------- | ------------ | ------- | ----------------------------------------- |
> | **Framework**     | ASP.NET Core | 8.0+    | Framework base API REST                   |
> | **Base de datos** | PostgreSQL   | 16+     | RDBMS principal con Npgsql + EF Core 8.0+ |
> | **Resilience**    | Polly        | 8.0+    | Circuit breaker, retry, timeout           |

| Componente      | Tecnología          | Versión | Uso                                 |
| --------------- | ------------------- | ------- | ----------------------------------- |
| **[Categoría]** | [Nombre tecnología] | [X.Y+]  | [Descripción concisa del propósito] |

---

## ¿Qué es [Concepto Principal]?

> 💡 **Nombre propio descriptivo** — reemplaza este `##` por el nombre real del concepto (ej: `## ¿Qué es Distributed Tracing?`, `## Tipos de Métricas`).
> Si el estándar tiene múltiples secciones conceptuales, déjalas como `##` planas independientes — no las anijes bajo un agrupador genérico.

[Definición directa en 2-3 oraciones. Qué es, para qué sirve, qué problema resuelve.]

**Componentes principales:**

- **[Componente 1]** — [descripción concisa]
- **[Componente 2]** — [descripción concisa]

**Beneficios:**

- ✅ [Beneficio 1 medible o observable]
- ✅ [Beneficio 2]
- ✅ [Beneficio 3]

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

> 💡 **Incluye secciones adicionales solo si el tema las requiere.** Patrones de nombre más usados:
>
> | Patrón de nombre                | Cuándo usarlo                                                            |
> | ------------------------------- | ------------------------------------------------------------------------ |
> | `## Configuración [Tecnología]` | Configuración de herramientas/librerías (ej: `## Configuración Serilog`) |
> | `## Uso en [Componente]`        | Uso en contexto real (ej: `## Uso en Controllers`)                       |
> | `## Estructura de Proyecto`     | Arquitecturas / patrones complejos                                       |
> | `## Principios de [Tema]`       | Si hay múltiples principios a detallar                                   |
> | `## Code Smells y Soluciones`   | Prácticas de desarrollo; antipatrones con corrección                     |
>
> **Para configuración gestionada por Plataforma** (Alloy, agentes, service mesh, pipelines):
> no documentes la config en el estándar de desarrollo — añade solo un callout:
>
> ```markdown
> :::note Configurado por Plataforma
> La configuración de [herramienta] es responsabilidad del equipo de Plataforma.
> Ver [nombre de la sección](../../../plataforma-corporativa/[categoria]/[nombre-archivo].md).
> :::
> ```
>
> **NO agregues secciones "por completar" — solo las que aporten valor real**

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

---

<!-- OPCIONAL: elimina esta sección si solo hay un aspecto de implementación -->

## Implementación: [Aspecto 2]

> 💡 **Incluye solo si hay aspectos técnicos sustancialmente diferentes del Aspecto 1**

[Implementación concisa del segundo aspecto]

---

## Beneficios en Práctica

> 💡 **Incluye esta sección para patrones/arquitecturas con casos de uso claros**
>
> - Escenarios de cambio (migración de DB, agregar protocolo, etc.)
> - Comparación de esfuerzo con/sin el patrón
> - OMITE si los beneficios son obvios o ya están en la sección conceptual anterior

**Para patrones de aislamiento** (Hexagonal, Clean Architecture, CQRS):

```yaml
# ✅ Casos de uso reales en Talma (2-3 casos concretos máximo)

Caso 1: [Escenario — ej: migrar de PostgreSQL a Cosmos DB]
  Cambio necesario: [Qué se toca — ej: solo el repositorio de infraestructura]
  Sin cambios:
    ✅ [Qué permanece intacto — ej: lógica de dominio, casos de uso, tests]
  Tiempo: [Estimación — ej: 2-3 días]
```

**Para estándares de tecnología o práctica** (Observabilidad, Seguridad, APIs):

```yaml
# ✅ Comparativa de impacto

Antes (sin el estándar):
  Problema:
    [Situación observable — ej: logs no estructurados, sin correlation ID]
  Consecuencia: [Impacto real — ej: 45 min para rastrear un error en producción]

Después (con el estándar):
  Estado: [Situación mejorada — ej: logs indexables, traces completos]
  Resultado: [Mejora medible — ej: diagnóstico en < 5 min con Loki + Tempo]
```

---

## Requisitos Técnicos

<!-- Guía de cantidad: 3–5 MUST, 2–4 SHOULD, 1–3 MAY, 1–3 MUST NOT.
     Menos es mejor — si tienes 8+ MUST, revisa si algunos son SHOULD en realidad.
     Omite secciones vacías (especialmente MAY si no hay opciones reales). -->

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

<!-- Formato: [Nombre](ruta) — descripción breve de por qué es relevante -->

- [Lineamiento de [Categoría]](../../lineamientos/[categoria]/[nombre].md) — lineamiento que origina este estándar
- [ADR-XXX: Título](../../adrs/adr-xxx.md) — decisión arquitectónica asociada (si existe)
- [Estándar relacionado](./nombre-estandar.md) — complementa este estándar en [aspecto]
- [Documentación oficial — Nombre Tecnología](https://...) — referencia externa
