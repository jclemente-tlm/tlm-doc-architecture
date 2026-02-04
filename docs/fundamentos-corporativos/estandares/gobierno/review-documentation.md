---
id: review-documentation
sidebar_position: 6
title: Review Documentation
description: Estándar para documentación completa y trazable de revisiones arquitectónicas, decisiones y outcomes del ARB
---

# Estándar Técnico — Review Documentation

---

## 1. Propósito

Establecer estándares para documentar comprehensivamente todas las revisiones arquitectónicas, capturando contexto, decisiones, justificaciones y outcomes de manera trazable y auditable para futuras referencias.

---

## 2. Alcance

**Aplica a:**

- Architecture Review Board (ARB) meetings
- Architecture Decision Records (ADRs)
- Design reviews formales
- Technical RFCs
- Post-mortems arquitectónicos
- Retrospectivas de arquitectura

**No aplica a:**

- Code reviews de PRs
- Daily standup notes
- Conversaciones informales
- Draft documents internos

---

## 3. Tecnologías Aprobadas

| Componente          | Tecnología | Uso Principal           | Observaciones            |
| ------------------- | ---------- | ----------------------- | ------------------------ |
| **ADR Management**  | ADR Tools  | ADRs versionados en Git | Markdown format          |
| **Documentation**   | Confluence | Knowledge base central  | Templates estandarizados |
| **Diagrams**        | Mermaid    | Diagramas as code       | Versionados con ADRs     |
| **Diagrams**        | Draw.io    | Diagramas complejos     | Integrado con Confluence |
| **Meeting Minutes** | Notion     | Notas colaborativas     | Con templates            |
| **Version Control** | Git        | Historia de ADRs        | Con branch protection    |

> El uso de tecnologías no listadas requiere aprobación de Arquitectura.

---

## 4. Requisitos Obligatorios 🔴

### Contenido Mínimo

- [ ] **Contexto:** problema y drivers de negocio
- [ ] **Alternativas:** mínimo 2 opciones consideradas
- [ ] **Decisión:** opción seleccionada con justificación
- [ ] **Consecuencias:** trade-offs y limitaciones
- [ ] **Stakeholders:** quién participó y aprobó
- [ ] **Estado:** DRAFT | PROPOSED | ACCEPTED | REJECTED | SUPERSEDED

### Formato y Estructura

- [ ] **Template estándar:** usar plantilla corporativa
- [ ] **Markdown:** formato portable y versionable
- [ ] **Diagrams as Code:** Mermaid para diagramas clave
- [ ] **Frontmatter:** metadata YAML (status, date, decision-makers)
- [ ] **Naming:** ADR-NNN-descriptive-title.md

### Publicación

- [ ] **Versionado:** en repositorio Git
- [ ] **Accesibilidad:** visible para equipos relevantes
- [ ] **Inmutabilidad:** ADRs son append-only (no editar decisiones pasadas)
- [ ] **Enlaces:** cross-references entre ADRs relacionados
- [ ] **Timeline:** publicar dentro de 48h post-decisión

### Trazabilidad

- [ ] **Unique ID:** ADR-YYYY-NNN auto-incrementado
- [ ] **Git history:** commits firmados con GPG
- [ ] **Audit trail:** quién aprobó, cuándo
- [ ] **Links:** vincular a issues, PRs, deployments

---

## 5. Prohibiciones

- ❌ Decisiones sin documentar
- ❌ Editar ADRs aprobados (usar SUPERSEDED)
- ❌ Documentación solo en emails/chats
- ❌ Falta de alternativas consideradas
- ❌ No indicar estado del ADR
- ❌ Diagramas sin versionar
- ❌ Documentación sin acceso público (dentro de org)

---

## 6. Configuración Mínima

### ADR Template

```markdown
---
status: PROPOSED
date: 2024-02-15
decision-makers: [Sarah Chen, John Developer]
consulted: [SRE Team, Security Team]
informed: [All Engineering]
---

# ADR-052: Migration to Event-Driven Architecture

## Context and Problem Statement

[Describe the problem and why this decision is needed]

## Decision Drivers

- Driver 1: [e.g., Need for real-time data synchronization]
- Driver 2: [e.g., Reduce coupling between services]
- Driver 3: [e.g., Improve scalability]

## Considered Options

### Option 1: REST APIs with Polling

**Pros:** Simple, well-understood
**Cons:** High latency, polling overhead
**Cost:** $500/month

### Option 2: Event-Driven with Kafka

**Pros:** Real-time, decoupled, scalable
**Cons:** Operational complexity
**Cost:** $2k/month

### Option 3: Hybrid (Events + APIs)

**Pros:** Flexibility
**Cons:** Increased complexity
**Cost:** $1.5k/month

## Decision Outcome

**Chosen option:** Option 2 - Event-Driven with Kafka

**Justification:** Real-time requirements and scalability benefits outweigh operational complexity. Team has Kafka expertise.

## Consequences

**Positive:**

- Real-time data sync across services
- Reduced API coupling
- Better scalability

**Negative:**

- Increased operational complexity
- Need for monitoring and alerting
- Higher infrastructure costs

**Risks:**

- Skills gap in team → Mitigation: Training
- Message ordering issues → Mitigation: Partition keys

## Implementation Plan

1. Phase 1: PoC with 1 bounded context (2 weeks)
2. Phase 2: Production pilot (4 weeks)
3. Phase 3: Gradual rollout (8 weeks)

## Validation

**Success Criteria:**

- Event processing latency < 500ms p95
- Zero message loss
- Consumer lag < 1000 messages

**Review Date:** 2024-05-15

## References

- [Kafka Documentation](link)
- [PoC Results](link)
- [Related ADR-045: Service Decomposition](link)
```

### Confluence Template - ARB Minutes

```markdown
# ARB Meeting Minutes — 2024-02-15

**Attendees:** Sarah Chen (Chair), Pedro González, Ana Martínez, SRE Team
**Absent:** Carlos López (approved)
**Duration:** 10:00-12:00

---

## Agenda

1. Previous actions follow-up
2. ADR-052 review
3. ADR-053 review
4. Announcements

---

## 1. Previous Actions Follow-up

| Action                      | Owner | Status         | Notes              |
| --------------------------- | ----- | -------------- | ------------------ |
| ADR-045 conditions verified | John  | ✅ Done        | All conditions met |
| PoC results for ADR-048     | Maria | 🟡 In Progress | Delayed 1 week     |

---

## 2. ADR-052: Event-Driven Architecture

**Presenter:** Pedro González
**Decision:** ✅ APPROVED WITH CONDITIONS

**Discussion Highlights:**

- Concern: Operational complexity
- Suggestion: Start small, expand gradually
- Risk: Consumer lag monitoring critical

**Conditions:**

1. PoC validation (Owner: Pedro, Deadline: 2024-03-01)
2. Operational runbook (Owner: SRE, Deadline: 2024-03-10)
3. Training plan (Owner: Pedro, Deadline: 2024-02-28)

**Voting:** 6 Approve, 0 Reject, 1 Abstain

---

## 3. Next Meeting

**Date:** 2024-03-01
**Submission Deadline:** 2024-02-23
```

---

## 7. Ejemplos

### Git Repository Structure

```
docs/
├── adr/
│   ├── README.md
│   ├── template.md
│   ├── 2024/
│   │   ├── ADR-052-event-driven-architecture.md
│   │   ├── ADR-053-redis-cache-strategy.md
│   │   └── ADR-054-performance-optimization.md
│   └── superseded/
│       └── ADR-018-multi-region-day-one.md
├── rfcs/
│   └── RFC-001-api-versioning-strategy.md
└── diagrams/
    ├── current-architecture.mmd
    └── target-architecture.mmd
```

---

## 8. Validación y Auditoría

### Checklist

- [ ] Todos los ADRs con template completo
- [ ] Versionados en Git con historia inmutable
- [ ] Estado actualizado (DRAFT → ACCEPTED)
- [ ] Publicados en < 48h de decisión
- [ ] Cross-references a ADRs relacionados
- [ ] Diagramas versionados

### Métricas

```promql
# ADRs por mes
count(adr_created) by (month)

# Time to publication
histogram_quantile(0.95, adr_publication_delay_hours)

# ADR status distribution
count(adr) by (status)
```

### Dashboard SLIs

| Métrica                | SLI   | Alertar si |
| ---------------------- | ----- | ---------- |
| Time to publication    | < 48h | > 72h      |
| ADRs sin revisar       | < 5   | > 10       |
| Documentación completa | 100%  | < 95%      |

---

## 9. Referencias

**Frameworks:**

- [Architecture Decision Records - Michael Nygard](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions)
- [ADR GitHub Organization](https://adr.github.io/)
- [ISO 42010 - Architecture Description](https://www.iso.org/standard/50508.html)

**Herramientas:**

- [adr-tools](https://github.com/npryce/adr-tools)
- [Mermaid Documentation](https://mermaid.js.org/)

**Buenas Prácticas:**

- ThoughtWorks Technology Radar
- Google Design Docs
