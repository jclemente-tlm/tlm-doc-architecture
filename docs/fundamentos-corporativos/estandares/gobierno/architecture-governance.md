---
id: architecture-governance
sidebar_position: 1
title: Gobierno de Arquitectura
description: Estándar consolidado para revisiones formales de arquitectura (ARB), retrospectivas periódicas y documentación completa de decisiones mediante ADRs trazables
---

# Estándar Técnico — Gobierno de Arquitectura

## 1. Propósito

Establecer un marco de gobierno arquitectónico integral que incluye revisiones formales de decisiones significativas (Architecture Review Board), retrospectivas sistemáticas para capturar lecciones aprendidas y documentación completa y trazable de todas las decisiones mediante Architecture Decision Records (ADRs).

## 2. Alcance

**Aplica a:**

- Nuevas arquitecturas de sistemas
- Cambios arquitectónicos significativos
- Selección de tecnologías no estándar
- Decisiones con impacto multi-equipo
- Migraciones de sistemas críticos
- Proyectos completados o en fase estable
- Incidentes mayores relacionados con arquitectura
- Architecture Review Board (ARB) meetings
- Architecture Decision Records (ADRs)
- Design reviews formales
- Technical RFCs
- Post-mortems arquitectónicos
- Retrospectivas de arquitectura

**No aplica a:**

- Code reviews de pull requests
- Decisiones técnicas locales a un equipo
- Refactorings internos sin cambio arquitectónico
- Bug fixes operacionales
- Configuraciones estándar
- Retrospectivas de sprint (ágil ceremonies)
- Daily standup notes
- Conversaciones informales
- Draft documents internos

## 3. Tecnologías Aprobadas

| Componente          | Tecnología   | Uso Principal                | Observaciones                |
| ------------------- | ------------ | ---------------------------- | ---------------------------- |
| **ADR Management**  | ADR Tools    | Versionado de ADRs en Git    | Formato Markdown             |
| **Documentation**   | Confluence   | Knowledge base de decisiones | Con templates estandarizados |
| **Diagrams**        | Mermaid      | Diagramas as code            | Versionado en Git            |
| **Diagrams**        | Draw.io      | Diagramas complejos          | Integrado con Confluence     |
| **Review Tracking** | Jira         | Workflow de aprobaciones ARB | Custom workflow ARB          |
| **Collaboration**   | Miro         | Retrospectivas remotas       | Templates de retros          |
| **Collaboration**   | FigJam       | Whiteboarding colaborativo   | Integrado con Figma          |
| **Meetings**        | Teams/Zoom   | Sesiones sincrónicas         | Grabaciones para auditoría   |
| **Métricas**        | Grafana      | Visualización de impacto     | Dashboards de decisiones     |
| **Survey**          | Google Forms | Feedback y pre-retros        | Recolección async            |
| **Version Control** | Git          | Historia de ADRs             | Con branch protection        |

> El uso de tecnologías no listadas requiere aprobación de Arquitectura.

## 4. Requisitos Obligatorios 🔴

### 4.1 Architecture Review Board (ARB)

#### Proceso de Review

- [ ] **ADR escrito ANTES de implementación:** Obligatorio
- [ ] **Template estándar:** Usar plantilla corporativa ADR
- [ ] **Submission deadline:** Mínimo 1 semana antes de ARB meeting
- [ ] **Pre-review:** Arquitecto líder valida completitud
- [ ] **Distribución:** ADR enviado a reviewers 3 días antes
- [ ] **Quorum:** Mínimo 5 miembros para aprobar

#### Criterios de Revisión

- [ ] **Alineación estratégica:** Con roadmap tecnológico
- [ ] **Estándares corporativos:** Cumplimiento verificado
- [ ] **Análisis de alternativas:** Mínimo 2 opciones evaluadas
- [ ] **Trade-offs documentados:** Pros/cons claros
- [ ] **Impacto operacional:** Costos, complejidad, skills
- [ ] **Riesgos identificados:** Con planes de mitigación

#### Participantes del ARB

- [ ] **Chief Architect:** Chair obligatorio
- [ ] **Domain Architects:** Según área afectada
- [ ] **Tech Leads:** De equipos impactados
- [ ] **SRE Lead:** Para decisiones de infraestructura
- [ ] **Security Lead:** Para decisiones con impacto de seguridad

#### Resultado del Review

- [ ] **Decisión formal:** Approved / Approved with Conditions / Rejected / Deferred
- [ ] **Documentación:** Minuta de reunión publicada en 24h
- [ ] **Conditions tracking:** Si approved with conditions
- [ ] **Feedback estructurado:** Para decisiones rechazadas
- [ ] **ADR actualizado:** Con outcome del review

#### Seguimiento Post-Review

- [ ] **Implementation tracking:** Vincular ADR con work items
- [ ] **Checkpoints:** Revisión en 30/60/90 días post-implementation
- [ ] **Métricas de impacto:** Medir outcomes vs expectativas
- [ ] **Lessons learned:** Capturar en retrospectivas

### 4.2 Architecture Retrospectives

#### Frecuencia y Timing

- [ ] **Retrospectivas trimestrales:** Mínimo cada 3 meses
- [ ] **Post-proyecto:** Dentro de 2 semanas de go-live
- [ ] **Post-incidente mayor:** Dentro de 1 semana
- [ ] **Migración completada:** Retrospectiva obligatoria
- [ ] **Calendario publicado:** Con 2 semanas de anticipación

#### Participantes

- [ ] **Arquitecto líder:** Facilitador obligatorio
- [ ] **Equipo de desarrollo:** Mínimo 3 desarrolladores
- [ ] **Product Owner:** Si afecta roadmap
- [ ] **SRE/Ops:** Si involucra operaciones
- [ ] **Stakeholders clave:** Según decisiones revisadas

#### Preparación

- [ ] **ADRs a revisar:** Lista enviada con 1 semana de anticipación
- [ ] **Métricas recolectadas:** Performance, incidents, costs
- [ ] **Timeline preparado:** Hitos de implementación
- [ ] **Feedback previo:** Encuesta anónima pre-retro
- [ ] **Agenda compartida:** Objetivos claros

#### Ejecución

- [ ] **Duración:** 90-120 minutos máximo
- [ ] **Facilitador neutral:** Sin defensiveness
- [ ] **Timeboxing:** Cada sección con tiempo fijo
- [ ] **Toma de notas:** Designar note-taker
- [ ] **Grabación:** Con consentimiento del equipo

#### Documentación de Retrospectivas

- [ ] **Template estándar:** Usar plantilla corporativa
- [ ] **Secciones obligatorias:** What went well, What didn't, Learnings, Actions
- [ ] **Action items:** Con owner y fecha límite
- [ ] **Publicación:** Máximo 3 días post-retro
- [ ] **Accesibilidad:** Visible para toda ingeniería

#### Seguimiento de Retrospectivas

- [ ] **Action items tracking:** En herramienta de proyecto
- [ ] **Review en próxima retro:** Verificar closure
- [ ] **Actualización de ADRs:** Si decisiones cambian
- [ ] **Métricas de mejora:** Medir impacto de acciones
- [ ] **Cierre formal:** Validar con stakeholders

### 4.3 Review Documentation

#### Contenido Mínimo de ADRs

- [ ] **Contexto:** Problema y drivers de negocio
- [ ] **Alternativas:** Mínimo 2 opciones consideradas
- [ ] **Decisión:** Opción seleccionada con justificación
- [ ] **Consecuencias:** Trade-offs y limitaciones
- [ ] **Stakeholders:** Quién participó y aprobó
- [ ] **Estado:** DRAFT | PROPOSED | ACCEPTED | REJECTED | SUPERSEDED

#### Formato y Estructura

- [ ] **Template estándar:** Usar plantilla corporativa
- [ ] **Markdown:** Formato portable y versionable
- [ ] **Diagrams as Code:** Mermaid para diagramas clave
- [ ] **Frontmatter:** Metadata YAML (status, date, decision-makers)
- [ ] **Naming:** ADR-NNN-descriptive-title.md

#### Publicación

- [ ] **Versionado:** En repositorio Git
- [ ] **Accesibilidad:** Visible para equipos relevantes
- [ ] **Inmutabilidad:** ADRs son append-only (no editar decisiones pasadas)
- [ ] **Enlaces:** Cross-references entre ADRs relacionados
- [ ] **Timeline:** Publicar dentro de 48h post-decisión

#### Trazabilidad

- [ ] **Unique ID:** ADR-YYYY-NNN auto-incrementado
- [ ] **Git history:** Commits firmados con GPG
- [ ] **Audit trail:** Quién aprobó, cuándo
- [ ] **Links:** Vincular a issues, PRs, deployments

## 5. Prohibiciones

**ARB Reviews:**

- ❌ Implementar antes de aprobación del ARB
- ❌ Reviews sin ADR documentado
- ❌ Decisiones sin análisis de alternativas
- ❌ Aprobaciones sin quorum
- ❌ Falta de documentación del outcome
- ❌ Ignorar feedback del ARB
- ❌ Reviews de decisiones ya implementadas (rubber stamping)

**Retrospectives:**

- ❌ Buscar culpables o blame individual
- ❌ Retrospectivas sin preparación previa
- ❌ Ignorar feedback de desarrolladores
- ❌ Action items sin owner asignado
- ❌ No documentar resultados
- ❌ Retrospectivas solo cuando hay problemas
- ❌ Participación no diversa (solo seniors)

**Documentation:**

- ❌ Decisiones sin documentar
- ❌ Editar ADRs aprobados (usar SUPERSEDED)
- ❌ Documentación solo en emails/chats
- ❌ Falta de alternativas consideradas
- ❌ No indicar estado del ADR
- ❌ Diagramas sin versionar
- ❌ Documentación sin acceso público (dentro de org)

## 6. Templates y Configuración

### 6.1 ADR Template Completo

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

**Descripción:** [Detailed description]

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

---

## Lessons Learned (Post-Implementation)

**Fecha de Revisión:** [YYYY-MM-DD]

**What Went Well:**

- [Success 1]
- [Success 2]

**What Didn't Go Well:**

- [Challenge 1]
- [Challenge 2]

**Métricas Reales vs Esperadas:**
| Métrica | Esperado | Real | Delta |
|---------|----------|------|-------|
| Latency p95 | <200ms | 180ms | ✅ -10% |
| Cost | $5k/mes | $6.5k/mes | ⚠️ +30% |

**Recomendaciones para Futuros ADRs:**

1. [Lesson learned 1]
2. [Lesson learned 2]
```

### 6.2 Jira Workflow — ARB Review

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

### 6.3 Architecture Retrospective Template

```markdown
# Architecture Retrospective — {Project Name}

**Fecha:** {Date}
**Facilitador:** {Architect Name}
**Participantes:** {List of attendees}
**ADRs Revisadas:** {Links to ADRs}

---

## 1. Contexto

**Proyecto:** {Brief description}
**Periodo Revisado:** {Start date - End date}
**Decisiones Arquitectónicas Principales:**

- [ADR-001: Decision Title](link)
- [ADR-005: Another Decision](link)

---

## 2. Métricas de Impacto

| Métrica                 | Antes     | Después   | Delta    |
| ----------------------- | --------- | --------- | -------- |
| Tiempo de build         | 15 min    | 8 min     | -47% ✅  |
| Deploy frequency        | 1x/semana | 5x/semana | +400% ✅ |
| Incidents (P1/P2)       | 12/mes    | 3/mes     | -75% ✅  |
| API response time (p95) | 800ms     | 200ms     | -75% ✅  |
| Infrastructure cost     | $5k/mes   | $8k/mes   | +60% ⚠️  |
| Developer satisfaction  | 6/10      | 8/10      | +33% ✅  |

---

## 3. What Went Well ✅

### Decisiones Acertadas

**ADR-007: Migración a Microservicios**

- Escalabilidad mejoró significativamente
- Teams autónomos redujeron dependencies
- Deploy independiente redujo riesgo

**ADR-012: Implementación de API Gateway (Kong)**

- Centralización de autenticación simplificó seguridad
- Rate limiting previno 3 incidentes potenciales
- Observabilidad mejoró troubleshooting

### Prácticas que Funcionaron

- Code reviews arquitectónicos semanales
- Proof of concepts antes de decisiones grandes
- Documentación temprana en ADRs

---

## 4. What Didn't Go Well ⚠️

### Decisiones Sub-óptimas

**ADR-015: Event Sourcing para todos los módulos**

- ❌ Complejidad operacional subestimada
- ❌ Curva de aprendizaje impactó delivery
- ❌ Debugging de issues tomó 3x más tiempo
- ❌ Costos de storage aumentaron 60%

**Recomendación:** Limitar Event Sourcing solo a dominios que realmente lo requieren (audit, compliance)

**ADR-018: Multi-region desde día 1**

- ❌ Over-engineering para tráfico actual
- ❌ Costo no justificado vs beneficio
- ❌ Complejidad de testing aumentó

**Recomendación:** Single region inicial, multi-region cuando tráfico lo justifique

### Gaps de Proceso

- Falta de performance testing antes de producción
- ADRs escritos después de implementación
- Poca participación de Ops en decisiones

---

## 5. Lecciones Aprendidas 📚

1. **Start Simple, Scale Later:** Multi-region prematura fue costly sin beneficio
2. **PoC > Debate:** Las pruebas de concepto resolvieron más que meetings
3. **Developer Experience Matters:** Complejidad de Event Sourcing afectó moral
4. **Cost Visibility:** Necesitamos dashboards de costo por decisión arquitectónica
5. **Early Performance Testing:** Load testing en staging habría detectado issues
6. **ADRs como Living Docs:** Actualizar ADRs con learnings post-implementation

---

## 6. Action Items 🎯

| #   | Acción                                            | Owner      | Deadline   | Status         |
| --- | ------------------------------------------------- | ---------- | ---------- | -------------- |
| 1   | Refactor Event Sourcing a solo módulos críticos   | @john-dev  | 2024-03-15 | 🟡 In Progress |
| 2   | Implementar cost dashboard por servicio           | @maria-sre | 2024-02-28 | ✅ Done        |
| 3   | Crear template de performance testing             | @pedro-qa  | 2024-03-01 | 🔴 Blocked     |
| 4   | ADR review process: escribir antes de implementar | @sara-arch | 2024-02-20 | ✅ Done        |
| 5   | Incluir SRE en todas architecture reviews         | @sara-arch | Ongoing    | 🟢 Ongoing     |
| 6   | Downgrade multi-region a single-region + DR       | @john-dev  | 2024-04-01 | 🟡 In Progress |

---

## 7. Actualizaciones a ADRs

- **ADR-015:** Actualizar con "Lessons Learned" section
- **ADR-018:** Marcar como SUPERSEDED, crear ADR-025 (Single Region Strategy)
- **ADR-007:** Añadir "Success Metrics" section con datos reales

---

## 8. Métricas de Retrospectiva

- **Preparación:** ✅ 95% de participantes completaron pre-survey
- **Participación:** 12/15 stakeholders asistieron
- **Action Items:** 6 actions, 2 completadas en 2 semanas
- **Satisfacción:** 9/10 en post-retro survey
- **Follow-up:** Próxima retro programada para 2024-06-15

---

## 9. Anexos

- [Pre-Retro Survey Results](link)
- [Metrics Dashboard](link)
- [Grabación de Sesión](link) (acceso restringido)
```

### 6.4 ARB Meeting Agenda Template

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

- Q1 Architecture Strategy Review
- New standard: Observability with Grafana Stack
- Upcoming training: AWS ECS best practices
```

### 6.5 Pre-Retro Survey (Google Forms)

```
Architecture Retrospective — Pre-Survey

1. ¿Qué decisión arquitectónica tuvo el MAYOR impacto positivo?
   [Texto libre]

2. ¿Qué decisión te generó más fricciones en desarrollo?
   [Texto libre]

3. En escala 1-10, ¿qué tan satisfecho estás con las decisiones arquitectónicas?
   [1] [2] [3] [4] [5] [6] [7] [8] [9] [10]

4. ¿Qué métricas crees que mejoraron?
   [ ] Performance
   [ ] Reliability
   [ ] Developer Experience
   [ ] Time to Market
   [ ] Costs
   [ ] Security
   [ ] Observability

5. ¿Qué cambiarías si pudieras volver atrás?
   [Texto libre]

6. ¿Qué tema quieres que discutamos en la retro?
   [Texto libre]
```

## 7. Git Repository Structure

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
├── retrospectives/
│   ├── 2024-Q1-retrospective.md
│   ├── 2024-Q2-retrospective.md
│   └── post-migration-payment-system.md
├── arb-minutes/
│   ├── 2024-01-15-arb-meeting.md
│   ├── 2024-02-15-arb-meeting.md
│   └── 2024-03-15-arb-meeting.md
└── diagrams/
    ├── current-architecture.mmd
    └── target-architecture.mmd
```

## 8. Validación y Auditoría

### 8.1 Checklist de Cumplimiento

**ARB Reviews:**

- [ ] ADR escrito antes de implementación
- [ ] Mínimo 2 alternativas consideradas
- [ ] Quorum ARB (5+ miembros) para aprobar
- [ ] Minuta publicada en <24h
- [ ] Conditions tracking si aplica
- [ ] Follow-up review programado (30/60/90 días)

**Retrospectives:**

- [ ] Retrospectiva realizada cada trimestre
- [ ] Participación multidisciplinaria (dev, arch, ops, product)
- [ ] Documentación publicada en <3 días
- [ ] Action items con owners y deadlines
- [ ] Follow-up de actions de retro anterior
- [ ] ADRs actualizados con learnings

**Documentation:**

- [ ] Todos los ADRs con template completo
- [ ] Versionados en Git con historia inmutable
- [ ] Estado actualizado (DRAFT → ACCEPTED)
- [ ] Publicados en <48h de decisión
- [ ] Cross-references a ADRs relacionados
- [ ] Diagramas versionados

### 8.2 Métricas de Cumplimiento

| Métrica                                | Target         | Verificación                |
| -------------------------------------- | -------------- | --------------------------- |
| **ADRs publicados pre-implementation** | 100%           | Git history + Jira workflow |
| **Time to ADR publication**            | <48h           | Git commit timestamps       |
| **ARB quorum alcanzado**               | 100%           | Meeting minutes             |
| **Retrospectivas trimestrales**        | 100%           | Calendar + docs             |
| **Action items completados (retros)**  | >80%           | Jira/GitHub issues          |
| **ADRs con lessons learned**           | >50%           | Post-implementation updates |
| **Participación en retros**            | >70% invitados | Attendance logs             |
| **Tiempo primera review de ADR**       | <1 semana      | Jira workflow metrics       |

### 8.3 Comandos de Validación

```bash
# Verificar ADRs sin estado definido
grep -r "status:" docs/adr/**/*.md | grep -v "DRAFT\|APPROVED\|REJECTED\|SUPERSEDED"

# Verificar ADRs aprobados sin fecha de review
grep -r "status: APPROVED" docs/adr/**/*.md -A5 | grep -L "Fecha de Review"

# Listar retrospectivas pendientes (últimas por trimestre)
ls -ltr docs/retrospectives/ | tail -1

# Verificar action items abiertos de retrospectivas
gh issue list --label "architecture-retro" --state open

# Verificar branch protection en docs/adr
gh api repos/:owner/:repo/branches/main/protection | jq '.required_pull_request_reviews'

# Métricas de ARB
echo "ADRs aprobados último mes:"
find docs/adr -name "*.md" -mtime -30 -exec grep -l "status: APPROVED" {} \; | wc -l

echo "ADRs rechazados último mes:"
find docs/adr -name "*.md" -mtime -30 -exec grep -l "status: REJECTED" {} \; | wc -l
```

## 9. Facilitación de Retrospectivas

### 9.1 Facilitation Script (120 min)

#### 0. Setup (5 min)

- ✅ Verificar que todos pueden ver Miro/whiteboard
- ✅ Explicar reglas: no blame, respeto, timeboxing
- ✅ Designar note-taker
- ✅ Iniciar grabación (con consentimiento)

#### 1. Contexto (10 min)

- Revisar ADRs del periodo
- Mostrar métricas clave (antes/después)
- Alinear expectativas

#### 2. What Went Well (20 min)

- Silent writing (5 min): cada uno escribe en stickies
- Clustering (5 min): agrupar temas similares
- Discusión (10 min): top 3-5 items

#### 3. What Didn't Go Well (20 min)

- Silent writing (5 min)
- Clustering (5 min)
- Discusión (10 min): root cause analysis

#### 4. Learnings (15 min)

- Extraer patrones de What Went Well + Didn't Go Well
- Discusión: ¿qué haríamos diferente?

#### 5. Action Items (30 min)

- Brainstorming de soluciones
- Priorización (dot voting)
- Definir: WHO, WHAT, WHEN para top 5-7 actions
- Asignar owners

#### 6. Wrap-up (10 min)

- Revisar action items
- Próximos pasos
- Meta-retro: ¿qué tal estuvo la sesión?

#### 7. Post-Retro (10 min)

- Enviar summary a todos
- Crear tickets para action items
- Actualizar ADRs si aplica

## 10. Referencias

**Architecture Decision Records:**

- [Architecture Decision Records - Michael Nygard](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions)
- [ADR GitHub Organization](https://adr.github.io/)
- [adr-tools](https://github.com/npryce/adr-tools)

**Architecture Governance:**

- [ISO 42010 - Architecture Description](https://www.iso.org/standard/50508.html)
- [ThoughtWorks Technology Radar](https://www.thoughtworks.com/radar)
- [Software Architecture in Practice, Bass et al.](https://www.oreilly.com/library/view/software-architecture-in/9780136885979/)

**Retrospectives:**

- [Agile Retrospectives, Derby & Larsen](https://pragprog.com/titles/dlret/agile-retrospectives/)
- [Retrospective Wiki](https://retrospectivewiki.org/)

**Collaboration Tools:**

- [Mermaid Documentation](https://mermaid.js.org/)
- [Miro Templates](https://miro.com/templates/)
- [Confluence Best Practices](https://www.atlassian.com/software/confluence/guides)
