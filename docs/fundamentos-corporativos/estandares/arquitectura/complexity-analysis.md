---
id: complexity-analysis
sidebar_position: 7
title: Complexity Analysis
description: Analizar costo-beneficio de agregar complejidad arquitectónica
---

# Complexity Analysis

## Contexto

Este estándar define cómo **analizar complejidad** antes de agregar: cada nivel de complejidad debe tener justificación clara basada en **costo vs beneficio**. Complementa el [lineamiento de Simplicidad Intencional](../../lineamientos/arquitectura/13-simplicidad-intencional.md) tomando **decisiones informadas**.

---

## Levels of Complexity

```yaml
# ✅ Framework para evaluar complejidad

Level 0 (Simple):
  - Monolito modular
  - CRUD directo
  - Deployment manual
  - PostgreSQL single instance

  Apropiado para:
    - MVP (< 1000 usuarios)
    - Prototipos
    - Internal tools

  Change cost: Bajo
  Operational cost: $50-200/mes

Level 1 (Moderado):
  - Monolito con bounded contexts claros
  - Repository pattern + DTOs
  - CI/CD básico (GitHub Actions)
  - PostgreSQL con read replica
  - Redis cache

  Apropiado para:
    - Producción (< 10K usuarios)
    - SLA 99.5%
    - 1-2 equipos

  Change cost: Moderado
  Operational cost: $500-1000/mes

Level 2 (Complejo):
  - Microservices (3-7 servicios)
  - Event-driven communication
  - API Gateway
  - Kafka cluster
  - PostgreSQL per service
  - Kubernetes

  Apropiado para:
    - Scale (> 10K usuarios)
    - SLA 99.9%
    - 3+ equipos independientes

  Change cost: Alto
  Operational cost: $3000-8000/mes

Level 3 (Muy complejo):
  - Microservices (> 15 servicios)
  - Service mesh (Istio)
  - CQRS + Event Sourcing
  - Multi-region active-active
  - Observability completo

  Apropiado para:
    - Hyper-scale (> 100K usuarios)
    - SLA 99.99%
    - 10+ equipos
    - Compliance estricto (audit trail completo)

  Change cost: Muy alto
  Operational cost: $20K-50K/mes
```

## Decision Matrix

```yaml
# ✅ Usar para decisiones de complejidad

# Pregunta: ¿Implementar microservices para Sales Service?

Context (Sales Service):
  - Volumen actual: 500 órdenes/día
  - Usuarios concurrentes: 20-30
  - Equipo: 3 developers
  - Uptime actual: 99.3% (monolito)
  - Costo actual: $300/mes

Análisis Level 1 (Monolito modular) vs Level 2 (Microservices):

┌─────────────────┬──────────────────────┬──────────────────────┐
│ Dimensión       │ Level 1 (Monolito)   │ Level 2 (Micro)      │
├─────────────────┼──────────────────────┼──────────────────────┤
│ Development     │ 3 devs OK            │ 3 devs thin spread   │
│ Deployment      │ 5 min (single app)   │ 30 min (orquestador) │
│ Debugging       │ Stack trace directo  │ Distributed tracing  │
│ Latency         │ In-process (<1ms)    │ Network (20-50ms)    │
│ Infrastructure  │ $300/mes             │ $3000/mes            │
│ Team capacity   │ 80% features         │ 40% features, 60% infra │
│ Onboarding      │ 1 semana             │ 1 mes                │
│ SLA actual      │ 99.3% suficiente     │ 99.9% overkill       │
└─────────────────┴──────────────────────┴──────────────────────┘

Costo-Beneficio:
  Level 1 → Level 2:
    Costo:
      - $2700/mes más (infrastructure)
      - 60% tiempo en ops (vs 20%)
      - 4x onboarding time
      - 20-50ms latency overhead

    Beneficio:
      - Independent scaling (NO necesario con volumen actual)
      - Independent deploys (NO crítico con 3 devs)
      - 99.9% uptime (NO requerido por negocio)

  Decisión: ✅ MANTENER Level 1
  Trigger para revisar: Volumen > 10K órdenes/día O equipos independientes

# Pregunta: ¿Implementar CQRS para Billing Service?

Context (Billing Service):
  - Operaciones: 90% reads, 10% writes
  - Reportes complejos: Sí (facturación mensual)
  - Volumen: 2000 facturas/día
  - Query performance: p95 400ms (aceptable)

Análisis Repository Simple vs CQRS:

┌─────────────────┬──────────────────────┬──────────────────────┐
│ Dimensión       │ Repository Simple    │ CQRS + Event Source  │
├─────────────────┼──────────────────────┼──────────────────────┤
│ Read model      │ PostgreSQL directo   │ Read DB optimizado   │
│ Write model     │ PostgreSQL directo   │ Event Store          │
│ Query perf      │ p95 400ms OK         │ p95 50ms excelente   │
│ Complexity      │ 1 database           │ 2 databases + sync   │
│ Development     │ 1 semana/feature     │ 3 semanas/feature    │
│ Team expertise  │ Alta (todos saben)   │ Baja (0 experiencia) │
│ Audit trail     │ Change tracking OK   │ Event store completo │
└─────────────────┴──────────────────────┴──────────────────────┘

Costo-Beneficio:
  Simple → CQRS:
    Costo:
      - 3x development time
      - Learning curve (3 meses)
      - Eventual consistency (bugs potenciales)
      - 2 databases (duplicar storage/backup)

    Beneficio:
      - 400ms → 50ms query (NO necesario, 400ms aceptable)
      - Audit trail completo (Change Tracking suficiente)
      - Scale reads (NO necesario con volumen actual)

  Decisión: ✅ MANTENER Repository Simple
  Trigger para revisar: Query performance problema O audit compliance requerido

# Pregunta: ¿Implementar CI/CD automatizado?

Context:
  - Deploys: Manual (SSH + bash scripts)
  - Frecuencia: 2 deploys/semana
  - Errores: 1/10 deploys falla
  - Rollback: Manual (20 min)

Análisis Manual vs CI/CD:

Costo:
  - Implementación: 1 semana
  - Mantenimiento: 4 horas/mes

Beneficio:
  - Deploy time: 30 min → 5 min (ahorro 50 min/semana = 200 min/mes)
  - Error rate: 10% → 1% (menos incidents)
  - Rollback: 20 min → 1 min (menos downtime)
  - Confidence: Tests automáticos antes de deploy

Decisión: ✅ IMPLEMENTAR CI/CD
ROI: 1 mes (beneficio supera costo rápidamente)
```

## Real Examples (Talma)

```yaml
# ✅ Decisiones reales de complejidad

# Caso 1: Sales Service (2024)

Decisión: Monolito modular vs Microservices
Análisis:
  - Volumen: 800 órdenes/día
  - Team: 4 developers
  - Bounded contexts: 3 (Sales, Catalog, Billing)

  Opción A (Microservices):
    Costo: $4000/mes, 50% tiempo en ops

  Opción B (Monolito modular):
    Costo: $400/mes, 10% tiempo en ops

Resultado: ✅ Monolito modular
Justificación: Volumen NO justifica microservices cost
ADR: adr-025-monolito-modular-sales.md

# Caso 2: Authentication (2024)

Decisión: Implementar SSO propio vs Keycloak
Análisis:
  - Usuarios: 500 internos, 2000 externos (creciendo)
  - Compliance: OWASP, OAuth 2.0, OIDC

  Opción A (Implementar SSO):
    Costo: 3 meses dev, 40 horas/mes mantenimiento
    Riesgo: Security vulnerabilities

  Opción B (Keycloak):
    Costo: 2 semanas integración, 4 horas/mes mantenimiento
    Beneficio: Battle-tested, compliance built-in

Resultado: ✅ Keycloak
Justificación: Security > NIH, costo-beneficio claro
ADR: adr-004-keycloak-sso-autenticacion.md

# Caso 3: Infrastructure as Code (2024)

Decisión: CloudFormation vs Terraform
Análisis:
  - Multi-cloud: NO (solo AWS)
  - Team expertise: CloudFormation 0%, Terraform 20%

  Opción A (CloudFormation):
    - AWS native
    - Learning curve: 1 mes

  Opción B (Terraform):
    - Multi-cloud (NO necesario)
    - Learning curve: 2 semanas (hay expertise)
    - Community modules

Resultado: ✅ Terraform
Justificación: Team expertise existente, community support
ADR: adr-006-terraform-iac.md
```

## Complexity Debt

```yaml
# ✅ Medir deuda de complejidad (como tech debt)

Complejidad innecesaria = Deuda:
  - Código que NO aporta valor
  - Abstracciones sin uso concreto
  - Infraestructura over-provisioned
  - Patterns sofisticados sin justificación

Ejemplo (Sales Service):

  # ❌ Complejidad sin valor
  - Strategy pattern con 1 sola implementación (5 días trabajo, 0 valor)
  - Cache distribuido con 10 requests/día (1 semana setup, 0 beneficio)
  - API Gateway para 1 solo servicio (2 días config, overhead latencia)

  Deuda total: 12 días trabajo desperdiciados
  Interés: 2 horas/mes mantenimiento innecesario

Refactoring:
  - Eliminar Strategy, usar clase directa (-50 líneas, +claridad)
  - Eliminar cache distribuido, usar in-memory (-3 dependencies)
  - Eliminar API Gateway, llamadas directas (-200ms latency)

  Resultado: -8 horas/mes mantenimiento, +performance, +claridad
```

---

## Requisitos Técnicos

### MUST (Obligatorio)

- **MUST** justificar complejidad con análisis costo-beneficio (ADR)
- **MUST** usar matriz de decisión para cambios significativos
- **MUST** documentar triggers para reevaluar decisión
- **MUST** empezar en nivel más simple que cumpla requisitos

### SHOULD (Fuertemente recomendado)

- **SHOULD** revisar complejidad cada 6 meses (¿sigue justificada?)
- **SHOULD** refactorizar cuando complejidad ya no aporta valor
- **SHOULD** medir costo operacional real vs estimado

### MUST NOT (Prohibido)

- **MUST NOT** agregar complejidad sin análisis previo
- **MUST NOT** usar "best practices" como justificación única
- **MUST NOT** ignorar costos de mantenimiento
- **MUST NOT** sobre-estimar beneficios hipotéticos

---

## Referencias

- [Lineamiento: Simplicidad Intencional](../../lineamientos/arquitectura/13-simplicidad-intencional.md)
- [ADR-004: Keycloak SSO](../../../decisiones-de-arquitectura/adr-004-keycloak-sso-autenticacion.md)
- [ADR-006: Terraform IaC](../../../decisiones-de-arquitectura/adr-006-terraform-iac.md)
- [YAGNI Principle](./yagni-principle.md)
- [KISS Principle](./kiss-principle.md)
