---
id: architecture-evolution
sidebar_position: 8
title: Evolución de Arquitectura
description: Patrones para evolución arquitectónica incluyendo reversibilidad y selección tecnológica.
tags: [arquitectura, evolucion, tecnologias]
---

# Evolución de Arquitectura

## Contexto

Este estándar consolida prácticas para evolucionar arquitecturas de forma controlada. Complementa el lineamiento [Decisiones Arquitectónicas](../../lineamientos/gobierno/decisiones-arquitectonicas.md).

**Conceptos incluidos:**

- **Reversibility** → Decisiones reversibles vs irreversibles
- **Technology Selection** → Criterios para selección de tecnologías

---

## Stack Tecnológico

| Componente          | Tecnología       | Versión | Uso                           |
| ------------------- | ---------------- | ------- | ----------------------------- |
| **ADR**             | Markdown + Git   | -       | Architecture Decision Records |
| **Evaluación tech** | Technology Radar | -       | Trackeo de tecnologías        |

---

## Reversibilidad

### ¿Qué es Reversibilidad?

Capacidad de revertir decisiones arquitectónicas sin costo prohibitivo.

**Propósito:** Reducir riesgo, permitir experimentación.

**Decisiones reversibles vs irreversibles:**

- **Reversible**: UI framework, ORM, cache provider
- **Irreversible**: Modelo de datos, contratos públicos, compliance

**Beneficios:**
✅ Experimentación segura
✅ Menor riesgo de decisiones
✅ Adaptación al cambio

### Estrategias

```csharp
// Abstracciones para reversibilidad
public interface IEmailService // Decisión reversible: proveedor
{
    Task SendAsync(string to, string subject, string body);
}

// Implementación 1: SendGrid
public class SendGridEmailService : IEmailService { }

// Implementación 2: AWS SES (cambio reversible)
public class AwsSesEmailService : IEmailService { }

// Configuración permite cambio sin tocar código
builder.Services.AddScoped<IEmailService, AwsSesEmailService>();
```

---

## Selección Tecnológica

### ¿Qué es Selección Tecnológica?

Proceso sistemático para seleccionar tecnologías usando criterios objetivos.

**Criterios:**

- Madurez y adopción
- Soporte y comunidad
- Licenciamiento
- Performance
- Curva de aprendizaje
- Costos (licencias + operación)

**Beneficios:**
✅ Decisiones documentadas
✅ Evaluación objetiva
✅ Reducción de riesgo técnico

### Plantilla de Evaluación

```yaml
# Technology Evaluation Template
technology: Redis
version: 7.2+
purpose: Cache distribuido

evaluation:
  maturity:
    score: 9/10
    notes: Probado en producción por años

  performance:
    score: 10/10
    notes: Sub-millisecond latency

  cost:
    score: 8/10
    license: BSD (open source)
    operational: AWS ElastiCache ~$50/mes

  learning_curve:
    score: 7/10
    team_experience: 3/5 developers
    training_needed: false

  support:
    score: 9/10
    community: Muy activa
    enterprise_support: Disponible

alternatives_considered:
  - Memcached
  - Hazelcast

decision: ADOPT
rationale: Performance superior, equipo con experiencia, bajo costo
decision_date: 2026-02-18
review_date: 2026-08-18
```

---

## Matriz de Decisión

| Escenario         | Reversibility | Tech Selection |
| ----------------- | ------------- | -------------- |
| **Nueva app**     | ✅✅✅        | ✅✅✅         |
| **Refactoring**   | ✅✅          | ✅             |
| **Microservicio** | ✅✅          | ✅✅           |

---

## Requisitos Técnicos

### MUST (Obligatorio)

**Reversibility:**

- **MUST** evaluar reversibilidad antes de decisiones mayores

**Technology Selection:**

- **MUST** documentar evaluación para tecnologías nuevas
- **MUST** usar ADR para decisiones arquitectónicas

### SHOULD (Fuertemente recomendado)

- **SHOULD** revisar ADRs trimestralmente
- **SHOULD** mantener technology radar actualizado
- **SHOULD** hacer apps disposable (fast startup)

### MUST NOT (Prohibido)

- **MUST NOT** hardcodear configuración
- **MUST NOT** adoptar tecnologías sin evaluación

---

## Referencias

- [Lineamiento Decisiones Arquitectónicas](../../lineamientos/gobierno/decisiones-arquitectonicas.md) — lineamiento que origina este estándar
- [Building Evolutionary Architectures (ThoughtWorks)](https://evolutionaryarchitecture.com/)
- [The Twelve-Factor App](https://12factor.net/)
- [Architecture Decision Records](https://adr.github.io/)
