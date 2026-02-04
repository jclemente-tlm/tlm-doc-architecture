---
id: architecture-review
sidebar_position: 2
title: Architecture Review
description: Estándar para revisiones formales de arquitectura (Architecture Review Board - ARB) y validación de ADRs antes de implementación
---

# Estándar Técnico — Architecture Review

---

## 1. Propósito

Establecer un proceso formal de revisión arquitectónica para evaluar y aprobar decisiones técnicas significativas, asegurando alineación con estrategia corporativa, estándares y mejores prácticas antes de su implementación.

---

## 2. Alcance

**Aplica a:**

- Nuevas arquitecturas de sistemas
- Cambios arquitectónicos significativos
- Selección de tecnologías no estándar
- Decisiones con impacto multi-equipo
- Migraciones de sistemas críticos
- Cambios en patrones arquitectónicos corporativos

**No aplica a:**

- Code reviews de pull requests
- Decisiones técnicas locales a un equipo
- Refactorings internos sin cambio arquitectónico
- Bug fixes operacionales
- Configuraciones estándar

---

## 3. Tecnologías Aprobadas

| Componente            | Tecnología  | Uso Principal                | Observaciones                         |
| --------------------- | ----------- | ---------------------------- | ------------------------------------- |
| **ADR Management**    | ADR Tools   | Versionado de ADRs en Git    | Formato Markdown                      |
| **Documentation**     | Confluence  | Knowledge base de decisiones | Con templates estandarizados          |
| **Diagrams**          | C4 Model    | Diagramas arquitectónicos    | Niveles Context, Container, Component |
| **Diagramming Tools** | Draw.io     | Diagramas técnicos           | Integrado con Confluence              |
| **Diagramming Tools** | Mermaid     | Diagramas as code            | Versionado en Git                     |
| **Review Tracking**   | Jira        | Workflow de aprobaciones     | Custom workflow ARB                   |
| **Collaboration**     | Teams/Zoom  | Sesiones de review           | Grabaciones para auditoría            |
| **Voting**            | Slido/Menti | Votaciones en sesiones       | Para decisiones consensuadas          |

> El uso de tecnologías no listadas requiere aprobación de Arquitectura.

---

## 4. Requisitos Obligatorios 🔴

### Proceso de Review

- [ ] **ADR escrito ANTES de implementación:** obligatorio
- [ ] **Template estándar:** usar plantilla corporativa ADR
- [ ] **Submission deadline:** mínimo 1 semana antes de ARB meeting
- [ ] **Pre-review:** arquitecto líder valida completitud
- [ ] **Distribución:** ADR enviado a reviewers 3 días antes

### Criterios de Revisión

- [ ] **Alineación estratégica:** con roadmap tecnológico
- [ ] **Estándares corporativos:** cumplimiento verificado
- [ ] **Análisis de alternativas:** mínimo 2 opciones evaluadas
- [ ] **Trade-offs documentados:** pros/cons claros
- [ ] **Impacto operacional:** costos, complejidad, skills
- [ ] **Riesgos identificados:** con planes de mitigación

### Participantes del ARB

- [ ] **Chief Architect:** chair obligatorio
- [ ] **Domain Architects:** según área afectada
- [ ] **Tech Leads:** de equipos impactados
- [ ] **SRE Lead:** para decisiones de infraestructura
- [ ] **Security Lead:** para decisiones con impacto de seguridad
- [ ] **Quorum:** mínimo 5 miembros para aprobar

### Resultado del Review

- [ ] **Decisión formal:** Approved / Approved with Conditions / Rejected / Deferred
- [ ] **Documentación:** minuta de reunión publicada en 24h
- [ ] **Conditions tracking:** si approved with conditions
- [ ] **Feedback estructurado:** para decisiones rechazadas
- [ ] **ADR actualizado:** con outcome del review

### Seguimiento Post-Review

- [ ] **Implementation tracking:** vincular ADR con work items
- [ ] **Checkpoints:** revisión en 30/60/90 días post-implementation
- [ ] **Métricas de impacto:** medir outcomes vs expectativas
- [ ] **Lessons learned:** capturar en retrospectivas

---

## 5. Prohibiciones

- ❌ Implementar antes de aprobación del ARB
- ❌ Reviews sin ADR documentado
- ❌ Decisiones sin análisis de alternativas
- ❌ Aprobaciones sin quorum
- ❌ Falta de documentación del outcome
- ❌ Ignorar feedback del ARB
- ❌ Reviews de decisiones ya implementadas (rubber stamping)

---

## 6. Configuración Mínima

### ADR Template para Review

```markdown
---
status: DRAFT | IN_REVIEW | APPROVED | REJECTED | SUPERSEDED
date: YYYY-MM-DD
decision-makers: [List of ARB attendees]
consulted: [Stakeholders consulted]
informed: [Teams to be informed]
---

# ADR-XXX: [Decision Title]

## Contexto y Problema

### Contexto del Negocio

[Business context, why this matters]

### Problema Técnico

[Technical problem statement]

### Drivers

- Driver 1: [Business/technical driver]
- Driver 2: [Another driver]

### Restricciones

- Constraint 1: [e.g., budget limit]
- Constraint 2: [e.g., timeline]
- Constraint 3: [e.g., technology compatibility]

---

## Opciones Consideradas

### Opción 1: [Option Name]

**Descripción:**
[Detailed description]

**Pros ✅:**

- Pro 1
- Pro 2

**Cons ❌:**

- Con 1
- Con 2

**Costo Estimado:** $X/mes
**Complejidad:** Low/Medium/High
**Impacto Operacional:** [Description]

---

### Opción 2: [Option Name]

[Same structure as Option 1]

---

### Opción 3: [Option Name]

[Same structure as Option 1]

---

## Decision Matrix

| Criterio               | Peso | Opción 1 | Opción 2 | Opción 3 |
| ---------------------- | ---- | -------- | -------- | -------- |
| Performance            | 25%  | 8/10     | 6/10     | 9/10     |
| Cost                   | 20%  | 5/10     | 9/10     | 7/10     |
| Developer Experience   | 15%  | 7/10     | 5/10     | 8/10     |
| Operational Complexity | 15%  | 6/10     | 8/10     | 5/10     |
| Scalability            | 15%  | 9/10     | 6/10     | 8/10     |
| Time to Market         | 10%  | 7/10     | 8/10     | 6/10     |
| **TOTAL WEIGHTED**     |      | **7.2**  | **6.9**  | **7.5**  |

---

## Decisión Propuesta

**Opción Seleccionada:** Opción 3 - [Name]

**Justificación:**
[Why this option was chosen, referencing decision matrix and trade-offs]

**Implementation Plan:**

1. Phase 1: [Description] — Timeline: [X weeks]
2. Phase 2: [Description] — Timeline: [X weeks]
3. Phase 3: [Description] — Timeline: [X weeks]

**Success Criteria:**

- Metric 1: [e.g., API latency < 200ms p95]
- Metric 2: [e.g., Deploy frequency > 5x/week]
- Metric 3: [e.g., Zero downtime migration]

---

## Riesgos y Mitigaciones

| Riesgo                  | Probabilidad | Impacto | Mitigación                       |
| ----------------------- | ------------ | ------- | -------------------------------- |
| Vendor lock-in          | Medium       | High    | Usar abstraction layer           |
| Skills gap en equipo    | High         | Medium  | Training plan + external support |
| Performance degradation | Low          | High    | Load testing en staging          |
| Cost overrun            | Medium       | Medium  | Budget alerts + monthly reviews  |

---

## Preguntas para el ARB

1. [Question for the Architecture Review Board]
2. [Another question]
3. [Another question]

---

## Referencias

- [Link to related ADRs]
- [Proof of Concept results]
- [Vendor documentation]
- [Performance benchmarks]

---

## ARB Review Outcome

**Fecha de Review:** [YYYY-MM-DD]
**Decisión:** [APPROVED | APPROVED WITH CONDITIONS | REJECTED | DEFERRED]
**Votación:** [X Approve, Y Reject, Z Abstain]

**Conditions (si aplica):**

1. Condition 1 — Owner: [Name] — Deadline: [Date]
2. Condition 2 — Owner: [Name] — Deadline: [Date]

**Feedback:**
[Summary of ARB discussion and feedback]

**Next Steps:**

- [ ] Action 1
- [ ] Action 2
- [ ] Follow-up review scheduled for: [Date]
```

### Jira Workflow - ARB Review

```yaml
# ARB Review Workflow States
statuses:
  - DRAFT:
      description: "ADR being written"
      transitions: [SUBMIT_FOR_REVIEW]

  - PRE_REVIEW:
      description: "Pre-review by lead architect"
      transitions: [READY_FOR_ARB, RETURN_TO_DRAFT]

  - READY_FOR_ARB:
      description: "Scheduled for next ARB meeting"
      transitions: [IN_REVIEW]

  - IN_REVIEW:
      description: "Being discussed in ARB meeting"
      transitions: [APPROVED, APPROVED_WITH_CONDITIONS, REJECTED, DEFERRED]

  - APPROVED:
      description: "Approved for implementation"
      transitions: [IN_IMPLEMENTATION]

  - APPROVED_WITH_CONDITIONS:
      description: "Approved pending conditions"
      transitions: [APPROVED, REJECTED]

  - REJECTED:
      description: "Not approved"
      transitions: [DRAFT] # Can be revised and resubmitted

  - DEFERRED:
      description: "Needs more information"
      transitions: [DRAFT]

  - IN_IMPLEMENTATION:
      description: "Being implemented"
      transitions: [IMPLEMENTED]

  - IMPLEMENTED:
      description: "Implementation complete"
      final: true

# Custom fields
fields:
  - arb_submission_date: date
  - arb_review_date: date
  - arb_decision: select [APPROVED, APPROVED_WITH_CONDITIONS, REJECTED, DEFERRED]
  - arb_conditions: textarea
  - implementation_deadline: date
  - follow_up_review_date: date
```

---

## 7. Ejemplos

### ARB Meeting Agenda

```markdown
# Architecture Review Board — Meeting Agenda

**Fecha:** 2024-02-15 10:00-12:00
**Facilitador:** Sarah Chen (Chief Architect)
**Attendees:** Domain Architects, Tech Leads, SRE Lead, Security Lead

---

## 1. Previous Actions Follow-up (15 min)

- [ ] ADR-045 conditions verified (John)
- [ ] ADR-048 implementation checkpoint (Maria)

---

## 2. New Submissions for Review (90 min)

### 2.1 ADR-052: Migration to Event-Driven Architecture (30 min)

- **Presenter:** Pedro González
- **Domain:** Order Management
- **Impact:** High (affects 3 teams)
- **Pre-read:** [Link to ADR]

**Questions to Address:**

- Operational complexity increase
- Skills gap mitigation plan
- Rollback strategy

**Expected Outcome:** Decision with conditions

---

### 2.2 ADR-053: Add Redis Cache for User Profiles (30 min)

- **Presenter:** Ana Martínez
- **Domain:** User Management
- **Impact:** Medium (1 team)
- **Pre-read:** [Link to ADR]

**Questions to Address:**

- Cache invalidation strategy
- Cost-benefit analysis validation
- Query pattern changes impact

**Expected Outcome:** Deferred (need PoC results)

---

### 2.3 ADR-054: Adopt Rust for Performance-Critical Microservices (30 min)

- **Presenter:** Carlos López
- **Domain:** Payment Processing
- **Impact:** High (new language in stack)
- **Pre-read:** [Link to ADR]

**Questions to Address:**

- Team readiness and training plan
- Hiring implications
- Integration with existing .NET services

**Expected Outcome:** Discussion, likely deferred

---

## 3. Announcements (15 min)

- New AWS services approved for use
- Upcoming architecture retrospective (Q1)
- Updated ADR template v2.0

---

## 4. Next Meeting

**Date:** 2024-03-01
**Submission Deadline:** 2024-02-23
```

### ARB Decision Email Template

```markdown
Subject: [ARB DECISION] ADR-052: Migration to Event-Driven Architecture — APPROVED WITH CONDITIONS

Hi Team,

The Architecture Review Board reviewed ADR-052 on 2024-02-15.

**Decision:** ✅ APPROVED WITH CONDITIONS

**Voting Results:**

- Approve: 6
- Reject: 0
- Abstain: 1

**Summary:**
The ARB recognizes the benefits of event-driven architecture for the Order Management domain, particularly for improved scalability and system decoupling. The decision is approved with the following conditions:

**Conditions (must be completed before implementation):**

1. **PoC Validation** (Owner: Pedro González, Deadline: 2024-03-01)
   - Demonstrate end-to-end flow with Kafka
   - Performance benchmarks: p95 latency < 500ms
   - Failure scenarios tested (broker down, consumer lag)

2. **Operational Runbook** (Owner: SRE Team, Deadline: 2024-03-10)
   - Monitoring playbook for Kafka
   - Consumer lag alerting strategy
   - Incident response procedures

3. **Training Plan** (Owner: Pedro González, Deadline: 2024-02-28)
   - 2-day workshop for dev team
   - External Kafka expert engagement confirmed
   - Documentation of patterns and anti-patterns

**Key Feedback from ARB:**

- **Concern:** Operational complexity increase. Ensure SRE team is involved from day 1.
- **Suggestion:** Start with 1 bounded context, expand gradually.
- **Risk:** Consumer lag monitoring is critical. Invest in observability early.
- **Approval:** Architecture aligns with long-term strategy.

**Next Steps:**

1. Pedro to update ADR-052 with ARB outcome
2. Conditions tracking in Jira: ARB-052-C1, ARB-052-C2, ARB-052-C3
3. Follow-up review scheduled for: 2024-03-15 (validate conditions met)
4. Implementation can start after conditions verified

**Full Meeting Minutes:** [Link to Confluence]

Questions? Reply to this email or reach out to Sarah Chen.

Best,
ARB Team
```

---

## 8. Validación y Auditoría

### Checklist

- [ ] ADR escrito antes de implementación
- [ ] Análisis de alternativas documentado
- [ ] ARB review realizado con quorum
- [ ] Decisión formal documentada
- [ ] Conditions tracked y verificadas
- [ ] Implementation vinculada a ADR
- [ ] Follow-up reviews realizados

### Métricas

```promql
# ADRs reviewed per month
count(adr_review{status="completed"}) by (month)

# Approval rate
count(adr_review{decision="approved"}) / count(adr_review) * 100

# Time to decision (submission → outcome)
histogram_quantile(0.95, adr_review_duration_days)

# Conditions compliance rate
count(adr_conditions{status="met"}) / count(adr_conditions) * 100
```

### Dashboard SLIs

| Métrica                 | SLI       | Alertar si    |
| ----------------------- | --------- | ------------- |
| ARB meetings/mes        | >= 2      | < 2           |
| Time to decision        | < 14 días | > 21 días     |
| Approval rate           | 60-80%    | < 50% o > 90% |
| Conditions met on time  | > 85%     | < 70%         |
| ADRs without ARB review | 0%        | > 5%          |

---

## 9. Referencias

**Frameworks:**

- [Architecture Decision Records (ADR) - Michael Nygard](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions)
- [TOGAF ADM - Architecture Governance](https://pubs.opengroup.org/architecture/togaf9-doc/arch/)
- [AWS Well-Architected Framework Reviews](https://aws.amazon.com/architecture/well-architected/)

**Templates:**

- [ADR GitHub Organization](https://adr.github.io/)
- [Markdown ADR Tools](https://github.com/npryce/adr-tools)
- [C4 Model for Architecture Diagrams](https://c4model.com/)

**Buenas Prácticas:**

- ThoughtWorks Technology Radar - Decision-making process
- "Architecture Governance" - TOGAF Standard
- Google Design Docs - Collaborative decision-making
