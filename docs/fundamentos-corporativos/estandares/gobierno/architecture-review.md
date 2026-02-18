---
id: architecture-review
sidebar_position: 1
title: Architecture Review Process
description: Proceso formal de revisión de decisiones arquitectónicas significativas
---

# Architecture Review Process

## Contexto

Este estándar define el proceso de revisión arquitectónica para validar decisiones significativas antes de su implementación. Complementa el [lineamiento de Estilo y Enfoque Arquitectónico](../../lineamientos/arquitectura/01-estilo-y-enfoque-arquitectonico.md) asegurando **rigor, alineación y calidad** en decisiones de arquitectura.

---

## Conceptos Fundamentales

### ¿Qué es una Architecture Review?

```yaml
# ✅ Architecture Review = Evaluación formal de decisión arquitectónica

Definición: Proceso colaborativo donde arquitectos y stakeholders evalúan
  una propuesta arquitectónica significativa antes de su implementación.

Objetivos:
  - Validar alineación con lineamientos y principios
  - Identificar riesgos y trade-offs
  - Compartir conocimiento entre equipos
  - Asegurar consistencia arquitectónica
  - Prevenir deuda técnica

No es: ❌ Code review (eso es otro proceso)
  ❌ Aprobación burocrática
  ❌ Gatekeeping sin justificación
  ❌ Reunión de status

Cuándo requieren review: ✅ Selección de nuevo estilo arquitectónico
  ✅ Introducción de nueva tecnología al stack
  ✅ Cambios en patrones de integración
  ✅ Decisiones que afectan múltiples equipos
  ✅ Trade-offs significativos (costo, complejidad, performance)
  ✅ Cambios en seguridad o compliance
```

### Niveles de Review

```yaml
# ✅ 3 niveles según magnitud del impacto

Nivel 1 - Lightweight Review:
  Impacto: Un solo bounded context
  Duración: 30 minutos
  Participantes: Team Lead + Tech Lead + 1 Arquitecto
  Entregable: RFC (Request for Comments) + Decisión verbal
  Ejemplos:
    - Adoptar nueva librería interna al servicio
    - Cambio de patrón de persistencia en un servicio
    - Refactoring significativo interno

Nivel 2 - Standard Review:
  Impacto: Múltiples bounded contexts o equipo
  Duración: 1 hora
  Participantes: Arquitectos + Tech Leads afectados + Product Owner
  Entregable: ADR (Architecture Decision Record)
  Ejemplos:
    - Nueva integración entre servicios
    - Cambio en contrato de API público
    - Introducción de nueva base de datos
    - Adopción de nuevo patrón (circuit breaker, saga)

Nivel 3 - Strategic Review:
  Impacto: Toda la organización o plataforma
  Duración: 2 horas
  Participantes: Architecture Board + Engineering Leadership + Product Leadership
  Entregable: ADR + Presentation + Roadmap
  Ejemplos:
    - Migración de monolito a microservicios
    - Adopción de nuevo cloud provider
    - Cambio de strategy de comunicación (REST → Event-driven)
    - Nueva plataforma compartida
```

### Architecture Review Board

```yaml
# ✅ Composición del Architecture Board

Core Members (permanentes):
  - Principal Architect (chair)
  - Lead Backend Architect
  - Lead Frontend Architect
  - Lead Data Architect
  - Infrastructure Lead

Rotating Members (por caso):
  - Tech Lead del equipo proponente
  - Product Owner (si tiene impacto de producto)
  - Security Engineer (si tiene impacto de seguridad)
  - DevOps Engineer (si tiene impacto de infra)

Invitees (opcionales):
  - Domain experts
  - Stakeholders afectados
  - Vendors (si es evaluación de tool)

Roles:
  - Chair: Facilita meeting, asegura cobertura de topics
  - Proponente: Presenta propuesta y contesta preguntas
  - Reviewers: Hacen preguntas, identifican riesgos, sugieren alternatives
  - Scribe: Documenta decisión en ADR
```

## Proceso de Review

### Fase 1: Preparación (1-2 días antes)

```yaml
# ✅ Proponente prepara y distribuye documentación

Artefactos requeridos:
  1. RFC o ADR Draft:
    - Context y problema
    - Propuesta con diagrama C4
    - Alternativas consideradas
    - Trade-offs identificados
    - Plan de implementación
    - Riesgos y mitigaciones

  2. Diagrama de arquitectura (C4 Model):
    - Context diagram
    - Container diagram (si aplica)
    - Component diagram (si aplica)

  3. Análisis de impacto:
    - Servicios afectados
    - Equipos afectados
    - Timeline de implementación
    - Costos estimados (infra + desarrollo)

Distribución:
  - Enviar 2 días hábiles antes de review
  - Via Confluence page + email
  - Incluir link a Slack channel para Q&A async
```

### Fase 2: Review Meeting

```yaml
# ✅ Agenda estructurada de review meeting

1. Introduction (5 min):
  - Chair introduce propuesta y participantes
  - Confirmar que todos leyeron documentación previa

2. Presentation (15-20 min):
  - Proponente presenta propuesta
  - Focus en decisiones clave y trade-offs
  - Mostrar diagramas C4
  - Explicar alternativas descartadas y por qué

3. Q&A (20-30 min):
  - Reviewers hacen preguntas
  - Identificar gaps en análisis
  - Discutir riesgos no identificados
  - Sugerir alternativas

4. Discussion (15-20 min):
  - Debate de trade-offs
  - Evaluación de alternativas
  - Identificación de dependencias
  - Definir action items

5. Decision (10 min):
  - Approved (proceder con implementación)
  - Approved with Conditions (lista de requisitos adicionales)
  - Needs More Information (iterar documentación)
  - Rejected (explicar razones, sugerir alternativas)

6. Next Steps (5 min):
  - Asignar responsables de action items
  - Definir timeline de follow-up
  - Confirmar quién documenta decisión en ADR
```

### Fase 3: Documentación

```yaml
# ✅ Documentar decisión en ADR

Responsable:
  - Scribe del review (o Tech Lead proponente)

Contenido ADR:
  - Decision outcome (Approved/Rejected)
  - Key points discutidos
  - Concerns identificados
  - Action items con responsables
  - Follow-up date (si aplica)
  - Participantes del review

Timeline:
  - Publicar ADR máximo 2 días después de review
  - Notificar stakeholders via email/Slack
```

### Fase 4: Follow-up

```yaml
# ✅ Tracking de implementación

Si Approved:
  - Crear epics/stories en Jira
  - Incluir link a ADR en tickets
  - Track progress en Architecture Roadmap
  - Schedule follow-up review (si es Strategic Review)

Si Approved with Conditions:
  - Track completion de requisitos
  - Re-review cuando se cumplen conditions

Si Needs More Information:
  - Definir qué información falta
  - Timeline para iterar y re-presentar

Si Rejected:
  - Documentar razones en ADR
  - Sugerir alternativas viables
  - Opción de appeal si hay desacuerdo
```

## Checklist de Evaluación

```yaml
# ✅ Criterios de evaluación en review

1. Alineación: □ ¿Sigue lineamientos y principios de arquitectura?
  □ ¿Consistente con decisiones previas (ADRs)?
  □ ¿Alineado con tech strategy y roadmap?

2. Análisis de Alternativas: □ ¿Se evaluaron al menos 3 alternativas?
  □ ¿Se documentaron trade-offs de cada una?
  □ ¿Se justifica por qué la propuesta es la mejor opción?

3. Riesgos: □ ¿Se identificaron riesgos técnicos?
  □ ¿Se identificaron riesgos de negocio?
  □ ¿Hay plan de mitigación para riesgos críticos?
  □ ¿Se evaluó impacto de failure?

4. Escalabilidad y Performance: □ ¿Se modeló carga esperada?
  □ ¿Se identificaron bottlenecks potenciales?
  □ ¿Hay plan de capacity planning?
  □ ¿Se evaluó costo de escalar?

5. Seguridad y Compliance: □ ¿Se revisó con Security team si aplica?
  □ ¿Cumple políticas de seguridad?
  □ ¿Cumple compliance requirements?
  □ ¿Se documentó threat model?

6. Operabilidad: □ ¿Cómo se monitorea?
  □ ¿Cómo se hace troubleshooting?
  □ ¿Impacto en SLOs/SLAs?
  □ ¿Se evaluó costo operativo?

7. Implementación: □ ¿Timeline realista?
  □ ¿Se identificaron dependencias?
  □ ¿Se evaluó impacto en equipos?
  □ ¿Hay plan de rollout/rollback?

8. Testing: □ ¿Cómo se test end-to-end?
  □ ¿Performance testing plan?
  □ ¿Chaos engineering si aplica?

9. Documentación: □ ¿Diagramas C4 claros?
  □ ¿ADR bien escrito?
  □ ¿Plan de comunicación a equipos?

10. Reversibilidad: □ ¿Decisión es reversible?
  □ ¿Si no, se justifica por qué?
  □ ¿Cuál es el costo de revertir?
```

## Template: RFC (Request for Comments)

````markdown
# RFC-XXX: [Título de la Propuesta]

**Status:** Draft | In Review | Approved | Rejected
**Author:** [Nombre]
**Reviewers:** [Lista de reviewers]
**Review Date:** YYYY-MM-DD
**Type:** Lightweight | Standard | Strategic

---

## Context

**Problema:**
[Descripción del problema o necesidad que motiva esta propuesta]

**Goal:**
[Objetivo específico que se busca lograr]

**Non-Goals:**
[Explícitamente qué NO se busca resolver]

---

## Proposed Solution

**Descripción:**
[Descripción técnica de la solución propuesta]

**Diagrama:**

```mermaid
graph TB
    [Diagrama C4 de la solución]
```
````

**Key Decisions:**

- [Decisión 1 y justificación]
- [Decisión 2 y justificación]

**Trade-offs:**
| Aspecto | Pro | Con |
|---------|-----|-----|
| Performance | ... | ... |
| Complexity | ... | ... |
| Cost | ... | ... |

---

## Alternatives Considered

### Alternative 1: [Nombre]

**Description:** [Descripción breve]
**Pros:**

- [Pro 1]
  **Cons:**
- [Con 1]
  **Why not:** [Razón por la que no se eligió]

### Alternative 2: [Nombre]

[...]

---

## Impact Analysis

**Services Affected:**

- [Servicio 1]: [Tipo de cambio]

**Teams Affected:**

- [Equipo 1]: [Cómo les impacta]

**Dependencies:**

- [Dependencia externa 1]

**Timeline:**

- Phase 1 (Weeks 1-2): [...]
- Phase 2 (Weeks 3-4): [...]

**Cost Estimate:**

- Development: [X person-weeks]
- Infrastructure: $[Y]/month

---

## Risks & Mitigations

| Risk       | Probability     | Impact          | Mitigation           |
| ---------- | --------------- | --------------- | -------------------- |
| [Riesgo 1] | High/Medium/Low | High/Medium/Low | [Plan de mitigación] |

---

## Open Questions

1. [Pregunta pendiente 1]
2. [Pregunta pendiente 2]

---

## Success Criteria

**Definition of Done:**

- [ ] [Criterio 1]
- [ ] [Criterio 2]

**Metrics:**

- [Métrica 1]: [Valor objetivo]
- [Métrica 2]: [Valor objetivo]

---

## References

- [ADR-XXX: Related Decision]
- [Lineamiento: XYZ]
- [External Doc: Link]

````

## Template: Review Decision

```markdown
# Architecture Review Decision: RFC-XXX

**Date:** YYYY-MM-DD
**Decision:** Approved | Approved with Conditions | Needs More Information | Rejected
**Participants:**
- [Nombre 1] (Role)
- [Nombre 2] (Role)

---

## Summary

[Breve resumen de la propuesta y decisión]

---

## Key Discussion Points

- [Punto 1 discutido y outcome]
- [Punto 2 discutido y outcome]

---

## Concerns Raised

1. **[Concern 1]**
   - Raised by: [Nombre]
   - Resolution: [Cómo se resolvió o mitiga]

---

## Conditions (si Approved with Conditions)

1. [ ] [Condición 1] - Owner: [Nombre] - Due: [Fecha]
2. [ ] [Condición 2] - Owner: [Nombre] - Due: [Fecha]

---

## Action Items

- [ ] [Action 1] - Owner: [Nombre] - Due: [Fecha]
- [ ] [Action 2] - Owner: [Nombre] - Due: [Fecha]

---

## Follow-up

**Next Review:** [Fecha] (si aplica)
**Progress Tracking:** [Link a Jira epic]
````

---

## Requisitos Técnicos

### MUST (Obligatorio)

- **MUST** someter decisiones significativas a Architecture Review
- **MUST** preparar RFC o ADR draft antes del review
- **MUST** incluir diagramas C4 en propuesta
- **MUST** evaluar al menos 2 alternativas
- **MUST** documentar decisión en ADR después de review
- **MUST** identificar riesgos y mitigaciones
- **MUST** notificar stakeholders afectados

### SHOULD (Fuertemente recomendado)

- **SHOULD** distribuir documentación 2 días antes de review
- **SHOULD** limitar review meeting a 1 hora (Standard Review)
- **SHOULD** incluir Security Engineer si hay impacto de seguridad
- **SHOULD** track action items hasta completion
- **SHOULD** schedule follow-up para Strategic Reviews
- **SHOULD** mantener Architecture Review log

### MAY (Opcional)

- **MAY** hacer pre-review informal con 1-2 arquitectos
- **MAY** grabar review meeting para referencia
- **MAY** crear POC antes de review para validar viabilidad

### MUST NOT (Prohibido)

- **MUST NOT** implementar sin review si es decisión significativa
- **MUST NOT** usar review como gatekeeping sin justificación
- **MUST NOT** proceder si hay concerns críticos sin resolver
- **MUST NOT** omitir documentación por "urgencia"
- **MUST NOT** ignorar outcome de review
- **MUST NOT** hacer review sin preparación previa

---

## Referencias

- [Lineamiento: Estilo y Enfoque Arquitectónico](../../lineamientos/arquitectura/01-estilo-y-enfoque-arquitectonico.md)
- Estándares relacionados:
  - [Architecture Decision Records](../documentacion/architecture-decision-records.md)
  - [C4 Model](../documentacion/c4-model.md)
- Especificaciones:
  - [Architecture Review Process (ThoughtWorks)](https://www.thoughtworks.com/insights/blog/architecture/architecture-review-process)
  - [Technology Radar](https://www.thoughtworks.com/radar)
