---
id: service-ownership
sidebar_position: 1
title: Service Ownership
description: Definir ownership claro de servicios con responsabilidad end-to-end
---

# Service Ownership

## Contexto

Este estándar define el modelo de **service ownership**: cada servicio tiene un equipo owner responsable de su ciclo de vida completo. Complementa el [lineamiento de Autonomía de Servicios](../../lineamientos/arquitectura/10-autonomia-de-servicios.md) asegurando **accountability y autonomía técnica**.

---

## Conceptos Fundamentales

### ¿Qué es Service Ownership?

```yaml
# ✅ Service Ownership = Responsabilidad end-to-end

Definición:
  Un equipo (o persona) es responsable total de un servicio desde
  desarrollo hasta producción, incluyendo operación y soporte.

Principio: "You build it, you run it"
  - Quien desarrolla, opera el servicio en producción
  - Quien diseña, resuelve incidentes
  - Quien agrega features, monitorea performance

Responsabilidades del Owner:
  ✅ Desarrollo y feature delivery
  ✅ Testing y calidad
  ✅ Deployment y releases
  ✅ Monitoring y observabilidad
  ✅ On-call y resolución de incidentes
  ✅ Performance y escalabilidad
  ✅ Seguridad y compliance
  ✅ Documentación técnica
  ✅ Costo de infraestructura

Beneficios:
  ✅ Accountability clara (no "no es mi problema")
  ✅ Feedback loop rápido (devs sienten dolor de operación)
  ✅ Calidad mejorada (incentivo para no romper producción)
  ✅ Autonomía (equipo decide stack, arquitectura, prioridades)
  ✅ Velocidad (sin handoffs entre dev y ops)
```

### Service Ownership Model

```yaml
# ✅ Modelo de ownership en Talma

Sales Service:
  Owner Team: Sales Engineering Team
  Tech Lead: Juan Pérez
  Members: 4 developers + 1 QA
  Responsibilities:
    - Bounded Context: Sales (orders, order lines)
    - API: /api/v1/orders, /api/v2/orders
    - Database: sales-db (PostgreSQL RDS)
    - Events Published: OrderCreated, OrderApproved, OrderCancelled
    - Events Consumed: ProductPriceChanged, CustomerBlocked
    - Infrastructure: ECS service, ALB, S3 buckets
    - On-Call: 24/7 rotation (4 devs)
    - SLO: 99.9% availability, p95 latency < 200ms
    - Budget: $2,000/mes AWS

Fulfillment Service:
  Owner Team: Fulfillment Engineering Team
  Tech Lead: María García
  Members: 3 developers + 1 QA
  Responsibilities:
    - Bounded Context: Fulfillment (shipments, packages, deliveries)
    - API: /api/v1/shipments
    - Database: fulfillment-db (PostgreSQL RDS)
    - Events Published: ShipmentCreated, PackageDelivered
    - Events Consumed: OrderApproved
    - Infrastructure: ECS service, ALB
    - On-Call: 24/7 rotation (3 devs)
    - SLO: 99.5% availability, p95 latency < 500ms
    - Budget: $1,500/mes AWS

Catalog Service:
  Owner Team: Catalog Engineering Team
  Tech Lead: Carlos López
  Members: 5 developers + 1 QA
  Responsibilities:
    - Bounded Context: Catalog (products, categories, inventory)
    - API: /api/v1/products, /api/v1/categories
    - Database: catalog-db (PostgreSQL RDS + 2 read replicas)
    - Cache: ElastiCache Redis cluster
    - Events Published: ProductCreated, ProductPriceChanged
    - Infrastructure: ECS service (4 tasks), ALB
    - On-Call: 24/7 rotation (5 devs)
    - SLO: 99.95% availability (critical), p95 latency < 100ms
    - Budget: $5,000/mes AWS (read-heavy, requiere replicas)

Platform Team (Support Role):
  Owner: Platform Engineering Team
  Responsibilities:
    - AWS account management
    - Networking (VPCs, Security Groups)
    - Shared services (API Gateway Kong, Kafka cluster)
    - CI/CD pipelines (GitHub Actions templates)
    - Monitoring infrastructure (Grafana, Prometheus, Loki)
    - Consultoría a service teams

  ❌ NO es responsable de:
    - Desarrollo de servicios de negocio
    - On-call de servicios específicos
    - Features de productos
```

## Responsabilidades del Owner

### 1. Development

```yaml
# ✅ Owner desarrolla y evoluciona servicio

Responsabilidades:
  - Diseño de arquitectura del servicio
  - Implementación de features
  - Code reviews
  - Testing (unit, integration, e2e)
  - Refactoring y reducción de deuda técnica
  - Actualización de dependencias (NuGet packages, base images)
  - Documentación técnica (README, ADRs, runbooks)

Autonomía Técnica:
  ✅ Elegir stack tecnológico (PostgreSQL vs MongoDB)
  ✅ Elegir patterns (CQRS, Event Sourcing, etc)
  ✅ Elegir herramientas (ORM, librerías)
  ✅ Decidir refactorings internos

  ⚠️ Restricciones:
    - Debe seguir lineamientos corporativos
    - Debe usar stack aprobado (dentro de opciones)
    - Debe cumplir NFRs (security, performance, observabilidad)

Ejemplo - Sales Team Autonomy:
  ✅ Puede: Implementar CQRS en Sales Service
  ✅ Puede: Agregar Redis cache para queries read-heavy
  ✅ Puede: Refactorizar Order aggregate sin avisar a otros equipos
  ❌ No puede: Usar base de datos no aprobada (MySQL, Cassandra)
  ❌ No puede: Ignorar lineamientos de seguridad
```

### 2. Operations

```yaml
# ✅ Owner opera servicio en producción

Responsabilidades:
  - Deployment a producción
  - Monitoring de health y performance
  - On-call rotation (24/7)
  - Respuesta a incidentes
  - Post-mortem analysis
  - Capacity planning
  - Performance optimization
  - Cost optimization

On-Call Rotation:
  - 1 semana on-call por dev (rotación)
  - PagerDuty notifications
  - SLA response time: 15 minutos
  - Escalation to Tech Lead si >1 hora sin resolver

Ejemplo - Sales Service Incident:

  10:35 AM: PagerDuty alert → "Sales API p95 latency > 2s"
  10:36 AM: Dev on-call revisa Grafana dashboards
  10:40 AM: Identifica query lento en DB (missing index)
  10:45 AM: Crea index en Sales DB
  10:50 AM: Latency vuelve a normal (< 200ms)
  11:00 AM: Post-mortem: Agregar index a migration, alerta preventiva

  ✅ Resuelto por Sales Team (owner)
  ✅ Sin handoff a "ops team"
  ✅ Fast resolution (15 minutos)
```

### 3. SLOs y Métricas

```csharp
// ✅ Owner define SLOs y monitorea cumplimiento

// SLO Definition (Sales Service)
public class SalesServiceSLO
{
    // ✅ Availability SLO: 99.9% (43 min downtime/mes permitido)
    public static readonly SLO Availability = new SLO
    {
        Name = "Availability",
        Target = 99.9m,
        Measurement = "Success rate of /health endpoint",
        ErrorBudget = 0.1m  // 0.1% = 43 min/mes
    };

    // ✅ Latency SLO: p95 < 200ms
    public static readonly SLO Latency = new SLO
    {
        Name = "API Latency",
        Target = 200,  // milliseconds
        Percentile = 95,
        Measurement = "p95 of API response time"
    };

    // ✅ Error Rate SLO: < 1%
    public static readonly SLO ErrorRate = new SLO
    {
        Name = "Error Rate",
        Target = 1.0m,  // 1%
        Measurement = "% of API requests with 5xx errors"
    };
}

// Grafana Dashboard (Sales Service)
{
  "dashboard": {
    "title": "Sales Service - SLOs",
    "panels": [
      {
        "title": "Availability (Target: 99.9%)",
        "targets": [
          {
            "expr": "sum(rate(http_requests_total{service=\"sales\",status!~\"5..\"}[5m])) / sum(rate(http_requests_total{service=\"sales\"}[5m])) * 100"
          }
        ]
      },
      {
        "title": "Latency p95 (Target: < 200ms)",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket{service=\"sales\"}[5m])) * 1000"
          }
        ]
      },
      {
        "title": "Error Budget Remaining",
        "targets": [
          {
            "expr": "(1 - (1 - 0.999) / (1 - availability_actual)) * 100"
          }
        ]
      }
    ]
  }
}

// ✅ Owner revisa SLOs semanalmente
// ✅ Si error budget se agota, freeze de features (focus en stability)
```

### 4. Costos

```yaml
# ✅ Owner es responsable de costos de infraestructura

Sales Service - Monthly AWS Bill:
  ECS Fargate (4 tasks, 1 vCPU, 2GB): $120
  RDS PostgreSQL (db.t3.medium, 100GB): $150
  ALB (Application Load Balancer): $25
  S3 (logs, backups): $10
  CloudWatch (metrics, logs): $15
  Secrets Manager: $2
  Total: $322/month

  ✅ Under budget ($2,000/mes)
  ✅ Sales Team revisa AWS Cost Explorer mensualmente
  ✅ Sales Team optimiza costos (right-sizing, Spot instances)

Catalog Service - Monthly AWS Bill:
  ECS Fargate (8 tasks, 1 vCPU, 2GB): $240
  RDS PostgreSQL (db.t3.large, 200GB): $300
  RDS Read Replicas (2x db.t3.medium): $300
  ElastiCache Redis (cache.t3.medium): $50
  ALB: $25
  CloudWatch: $30
  Total: $945/month

  ✅ Under budget ($5,000/mes)
  ✅ Catalog Team justifica read replicas (read-heavy workload)
  ✅ Catalog Team monitorea cache hit rate (80%+)

Cost Optimization Examples:
  - Sales Team: Migró a Fargate Spot (70% savings en non-prod)
  - Fulfillment Team: Right-sized tasks (512MB → 256MB, suficiente)
  - Billing Team: S3 Intelligent-Tiering (logs migran a Glacier después de 90 días)
```

## Documentación del Ownership

### Service Registry

```yaml
# ✅ Service Registry (Confluence o GitHub)

services:
  - name: Sales Service
    owner:
      team: Sales Engineering Team
      tech_lead: Juan Pérez
      slack: #sales-engineering
      email: sales-team@talma.com
      pagerduty: sales-oncall

    bounded_context: Sales
    description: Manejo de ordenes de venta desde creación hasta aprobación

    technical:
      repository: https://github.com/talma/sales-service
      api_docs: https://api.talma.com/sales/docs
      grafana_dashboard: https://grafana.talma.com/d/sales
      runbook: https://wiki.talma.com/runbooks/sales

    infrastructure:
      database: sales-db.cluster-xyz.us-east-1.rds.amazonaws.com
      ecs_cluster: talma-production
      ecs_service: sales-service
      alb: sales-api-prod.talma.com

    contracts:
      apis:
        - version: v1
          url: https://api.talma.com/v1/orders
          swagger: https://api.talma.com/v1/orders/swagger.json
        - version: v2
          url: https://api.talma.com/v2/orders

      events_published:
        - OrderCreated
        - OrderApproved
        - OrderCancelled
        - OrderShipped

      events_consumed:
        - ProductPriceChanged (from Catalog)
        - CustomerBlocked (from Customer)

    slos:
      availability: 99.9%
      latency_p95: 200ms
      error_rate: 1%

    on_call:
      schedule: Weekly rotation
      escalation: Tech Lead → Engineering Manager → CTO
      response_sla: 15 minutes

    dependencies:
      - Catalog Service (HTTP API)
      - Customer Service (HTTP API)
      - Kafka (events)
      - PostgreSQL RDS

    budget:
      monthly: $2,000
      actual: $322

  - name: Fulfillment Service
    owner:
      team: Fulfillment Engineering Team
      tech_lead: María García
      slack: #fulfillment-engineering
    # ... similar structure
```

### RACI Matrix

```yaml
# ✅ RACI Matrix para clarificar responsabilidades

Activity: Deploy Sales Service to Production
  Sales Team: Responsible & Accountable ✅
  Platform Team: Consulted (provee pipeline template)
  Other Teams: Informed (post en #deployments)

Activity: Fix Sales Service Outage
  Sales Team: Responsible & Accountable ✅
  Platform Team: Consulted (si es problema de infra compartida)
  On-Call Manager: Informed

Activity: Change Sales Service Database Schema
  Sales Team: Responsible & Accountable ✅
  DBA: Consulted (best practices)  [opcional, no requerido]
  Other Teams: Informed (si publica eventos que cambian)

Activity: Optimize Sales Service AWS Costs
  Sales Team: Responsible & Accountable ✅
  FinOps: Consulted (provee recommendations)
  Engineering Manager: Informed (reportes mensuales)

Activity: Upgrade PostgreSQL Version (Sales DB)
  Sales Team: Responsible & Accountable ✅
  Platform Team: Consulted (soporte técnico)

Activity: Design New Sales Feature
  Sales Team: Responsible & Accountable ✅
  Product Manager: Consulted (requisitos)
  Architecture Team: Consulted (review de decisiones significativas)
```

## Transición de Ownership

```yaml
# ✅ Proceso para transferir ownership de servicio

Escenario: Order Management Service split en Sales + Fulfillment

Fase 1: Definir Nuevo Ownership (Week 1)
  - Identificar bounded contexts: Sales, Fulfillment
  - Asignar teams: Sales Team, Fulfillment Team
  - Definir límites: Orders (Sales), Shipments (Fulfillment)

Fase 2: Knowledge Transfer (Weeks 2-4)
  - Sales Team revisa código de Orders module (2 semanas)
  - Fulfillment Team revisa código de Shipments module (2 semanas)
  - Pairing sessions con equipo original
  - Documentar runbooks específicos

Fase 3: Shadow On-Call (Weeks 5-6)
  - Sales Team en shadow on-call para Orders
  - Fulfillment Team en shadow on-call para Shipments
  - Equipo original sigue siendo primary on-call

Fase 4: Split Infrastructure (Weeks 7-8)
  - Crear sales-db (split data de orders)
  - Crear fulfillment-db (split data de shipments)
  - Crear ECS services separados

Fase 5: Go-Live (Week 9)
  - Sales Team asume ownership completo de Sales Service
  - Fulfillment Team asume ownership completo de Fulfillment Service
  - Actualizar Service Registry
  - Comunicar a organización

Fase 6: Post-Go-Live Support (Weeks 10-12)
  - Equipo original disponible para consultas
  - Weekly sync entre equipos
  - Gradual handoff completo
```

---

## Requisitos Técnicos

### MUST (Obligatorio)

- **MUST** asignar owner team a cada servicio
- **MUST** owner es responsable de development + operations
- **MUST** owner participa en on-call rotation 24/7
- **MUST** documentar ownership en Service Registry
- **MUST** owner define y monitorea SLOs
- **MUST** owner es responsable de costos de infraestructura
- **MUST** owner escribe runbooks y documentación técnica
- **MUST** owner responde a incidentes (SLA: 15 minutos)

### SHOULD (Fuertemente recomendado)

- **SHOULD** owner team tener autonomía técnica (stack, patterns)
- **SHOULD** owner revisar métricas semanalmente
- **SHOULD** owner optimizar costos mensualmente
- **SHOULD** documentar RACI matrix para actividades críticas
- **SHOULD** hacer knowledge transfer al cambiar ownership (4-6 semanas)
- **SHOULD** mantener service registry actualizado

### MAY (Opcional)

- **MAY** Platform Team proveer consultoría a service teams
- **MAY** crear FinOps team para optimización de costos cross-service
- **MAY** rotar devs entre teams para knowledge sharing

### MUST NOT (Prohibido)

- **MUST NOT** transferir responsabilidad a "ops team" separado
- **MUST NOT** owner ignorar incidentes ("no es mi problema")
- **MUST NOT** "throw over the wall" a producción sin ownership
- **MUST NOT** compartir ownership de un servicio entre múltiples teams
- **MUST NOT** desplegar sin runbook documentado
- **MUST NOT** exceder budget sin justificación y aprobación

---

## Referencias

- [Lineamiento: Autonomía de Servicios](../../lineamientos/arquitectura/10-autonomia-de-servicios.md)
- Estándares relacionados:
  - [Database per Service](../datos/database-per-service.md)
  - [Independent Deployment](./independent-deployment.md)
  - [Service Level Objectives](../observabilidad/slo-monitoring.md)
- Libros:
  - [Team Topologies (Matthew Skelton)](https://teamtopologies.com/)
  - [Accelerate (Nicole Forsgren)](https://www.amazon.com/Accelerate-Software-Performing-Technology-Organizations/dp/1942788339)
- Artículos:
  - [You Build It, You Run It (Werner Vogels, Amazon CTO)](https://queue.acm.org/detail.cfm?id=1142065)
