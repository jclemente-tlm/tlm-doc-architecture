---
id: readme-standards
sidebar_position: 1
title: README Standards
description: Estructura y contenido obligatorio para archivos README de servicios y librerías
---

# README Standards

## Contexto

Este estándar define **README Standards**: estructura y contenido mínimo requerido para archivos **README.md** de servicios y librerías. README es el **primer punto de entrada** para developers nuevos en un proyecto. README incompleto genera fricción en onboarding. Complementa el [lineamiento de Documentación Técnica](../../lineamientos/desarrollo/03-documentacion-tecnica.md) estableciendo **plantilla estándar**.

---

## Concepto Fundamental

```yaml
# README como Contrato de Documentación

Purpose:
  - Onboarding: New developer can setup project < 30 min
  - Reference: Existing developer finds info quickly
  - Discovery: External teams understand what service does

Anti-Pattern (❌):

  # My Service

  This is a service.

  To run: `npm start`

Good README (✅):

  # Sales Service

  REST API para gestión de órdenes de venta, integrado con Billing y Inventory.

  ## Stack
  - .NET 8, PostgreSQL, Kafka, Redis

  ## Setup Local
  1. Prerequisites: Docker, .NET SDK 8.0
  2. `docker compose up -d` (starts DB + Kafka)
  3. `dotnet run`
  4. Open http://localhost:5000/swagger

  ## Architecture
  - Hexagonal (Ports & Adapters)
  - CQRS (separate read/write models)
  - Event-driven (publishes OrderCreated to Kafka)

  ## API Endpoints
  - POST /api/orders - Create order
  - GET /api/orders/:id - Get order details

  ## Testing
  - Unit: `dotnet test tests/UnitTests`
  - Integration: `dotnet test tests/IntegrationTests`
  - Coverage: > 80%

  ## Deployment
  - CI/CD: GitHub Actions → ECS Fargate
  - Prod URL: https://api.talma.com/sales

  ## Team
  - Owner: Sales Team (@sales-team)
  - On-call: PagerDuty "Sales Service"

  ## Links
  - [Architecture Diagram](docs/architecture.md)
  - [ADRs](docs/adr/)
  - [Runbooks](docs/runbooks/)
```

## README Template

```markdown
# [Service Name]

> **One-line description of what this service does**

[![Build Status](https://github.com/talma/sales-service/workflows/CI/badge.svg)](https://github.com/talma/sales-service/actions)
[![Coverage](https://codecov.io/gh/talma/sales-service/branch/main/graph/badge.svg)](https://codecov.io/gh/talma/sales-service)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Stack](#stack)
- [Prerequisites](#prerequisites)
- [Local Setup](#local-setup)
- [Running](#running)
- [Testing](#testing)
- [API Documentation](#api-documentation)
- [Deployment](#deployment)
- [Monitoring](#monitoring)
- [Team](#team)
- [Contributing](#contributing)
- [License](#license)

---

## 🎯 Overview

**Business Purpose:**
[2-3 sentences explaining WHY this service exists from business perspective]

Example:

> Sales Service manages customer orders from creation to fulfillment. Validates inventory availability, calculates pricing with discounts, and triggers billing once order is approved. Core service for e-commerce flow.

**Technical Purpose:**
[2-3 sentences explaining WHAT this service does technically]

Example:

> Exposes REST API for order management. Publishes domain events (OrderCreated, OrderApproved) to Kafka for async processing by downstream services (Billing, Fulfillment, Analytics). Implements CQRS pattern with read/write separation.

**Boundaries:**
[What this service does vs does NOT do]

Example:

- ✅ Order creation, validation, status updates
- ✅ Inventory reservation (calls Inventory API)
- ✅ Order history queries
- ❌ Does NOT handle payments (Billing Service)
- ❌ Does NOT manage shipping (Fulfillment Service)
- ❌ Does NOT send notifications (Notification Service)

---

## 🏗️ Architecture

**Pattern:** Hexagonal Architecture (Ports & Adapters)
```

SalesService/
├── src/
│ ├── SalesService.Api/ # HTTP API (adapter)
│ ├── SalesService.Application/ # Use cases (business logic)
│ ├── SalesService.Domain/ # Domain models (core)
│ └── SalesService.Infrastructure/# DB, Kafka, HTTP clients (adapters)
└── tests/
├── UnitTests/
└── IntegrationTests/

````

**Key Patterns:**
- CQRS: Separate read (queries) and write (commands) models
- Event Sourcing: Order state changes published as events
- Repository: Abstract data access
- Dependency Injection: .NET built-in DI

**Diagrams:**
- [C4 Context Diagram](docs/architecture/c4-context.md)
- [Sequence Diagrams](docs/architecture/sequences.md)

---

## 🛠️ Stack

| Component | Technology | Version |
|-----------|------------|---------|
| Language | C# | .NET 8.0 |
| Framework | ASP.NET Core | 8.0 |
| Database | PostgreSQL | 15.4 |
| Message Broker | Apache Kafka | 3.6 |
| Cache | Redis | 7.2 |
| Container | Docker | 24.x |
| Orchestration | AWS ECS Fargate | - |

**Key Libraries:**
- `MediatR` - CQRS command/query handling
- `FluentValidation` - Input validation
- `Dapper` - Micro-ORM for queries
- `Confluent.Kafka` - Kafka client
- `Polly` - Resilience (retry, circuit breaker)

---

## ✅ Prerequisites

Before running locally, install:

- [.NET SDK 8.0](https://dotnet.microsoft.com/download) or later
- [Docker Desktop](https://www.docker.com/products/docker-desktop) (for database + Kafka)
- [Git](https://git-scm.com/)

Optional (recommended):
- [Visual Studio 2022](https://visualstudio.microsoft.com/) or [Rider](https://www.jetbrains.com/rider/)
- [Postman](https://www.postman.com/) or [Insomnia](https://insomnia.rest/) for API testing

---

## 🚀 Local Setup

### 1. Clone Repository

```bash
git clone https://github.com/talma/sales-service.git
cd sales-service
````

### 2. Start Dependencies

```bash
# Start PostgreSQL, Kafka, Redis
docker compose up -d

# Wait for services to be healthy (30 seconds)
docker compose ps
```

### 3. Configure Environment

```bash
# Copy environment template
cp appsettings.Development.json.example appsettings.Development.json

# Edit connection strings (if needed)
# Default values work with docker-compose
```

### 4. Run Database Migrations

```bash
dotnet ef database update --project src/SalesService.Infrastructure
```

### 5. Restore Dependencies

```bash
dotnet restore
```

---

## ▶️ Running

### Development Mode

```bash
# Run with hot-reload
dotnet watch run --project src/SalesService.Api

# Service available at:
# - HTTP: http://localhost:5000
# - HTTPS: https://localhost:5001
# - Swagger: http://localhost:5000/swagger
```

### Docker

```bash
# Build image
docker build -t sales-service:latest .

# Run container
docker run -p 5000:8080 \
  -e ConnectionStrings__Database="Host=host.docker.internal;Port=5432;Database=sales;Username=postgres;Password=postgres" \
  sales-service:latest
```

### Production-like (with docker-compose)

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml up
```

---

## 🧪 Testing

### Unit Tests

```bash
# Run all unit tests
dotnet test tests/SalesService.UnitTests

# With coverage
dotnet test tests/SalesService.UnitTests --collect:"XPlat Code Coverage"
```

**Coverage Target:** > 80% line coverage

### Integration Tests

```bash
# Run integration tests (requires Docker dependencies running)
dotnet test tests/SalesService.IntegrationTests
```

**What's tested:**

- Database interactions (real PostgreSQL via Testcontainers)
- Kafka message publishing
- HTTP API endpoints (WebApplicationFactory)
- External service integrations (mocked)

### Load Testing

```bash
# Run k6 load tests
k6 run tests/load/create-order.js

# Expected: 100 RPS, p95 < 500ms
```

---

## 📚 API Documentation

### Swagger UI

**Local:** http://localhost:5000/swagger

**Production:** https://api.talma.com/sales/swagger (requires auth)

### Key Endpoints

#### Create Order

```http
POST /api/orders
Authorization: Bearer <JWT>
Content-Type: application/json

{
  "customerId": "cust-123",
  "items": [
    {
      "productId": "prod-001",
      "quantity": 2,
      "price": 50.00
    }
  ]
}

Response: 201 Created
{
  "orderId": "ord-abc-123",
  "status": "PENDING",
  "total": 100.00
}
```

#### Get Order

```http
GET /api/orders/{orderId}
Authorization: Bearer <JWT>

Response: 200 OK
{
  "orderId": "ord-abc-123",
  "customerId": "cust-123",
  "status": "CONFIRMED",
  "total": 100.00,
  "items": [...]
}
```

### Events Published

| Event            | Topic              | Schema                                     |
| ---------------- | ------------------ | ------------------------------------------ |
| `OrderCreated`   | `orders.created`   | [schema](docs/events/order-created.json)   |
| `OrderApproved`  | `orders.approved`  | [schema](docs/events/order-approved.json)  |
| `OrderCancelled` | `orders.cancelled` | [schema](docs/events/order-cancelled.json) |

---

## 🚢 Deployment

### CI/CD Pipeline

- **Tool:** GitHub Actions
- **Workflow:** [`.github/workflows/deploy.yml`](.github/workflows/deploy.yml)
- **Trigger:** Push to `main` branch

**Pipeline Steps:**

1. Build & Test (unit + integration)
2. SonarQube analysis (quality gate)
3. Security scan (Snyk, Trivy)
4. Docker build & push to GHCR
5. Deploy to ECS Fargate (dev → auto, prod → manual approval)

### Environments

| Environment | URL                             | Deployment                    |
| ----------- | ------------------------------- | ----------------------------- |
| Dev         | https://dev-api.talma.com/sales | Automatic (on push to `main`) |
| QA          | https://qa-api.talma.com/sales  | Automatic (on push to `main`) |
| Prod        | https://api.talma.com/sales     | Manual approval required      |

### Infrastructure

- **Platform:** AWS ECS Fargate
- **Region:** us-east-1
- **Cluster:** production-cluster
- **Service:** sales-service
- **Tasks:** 4 (multi-AZ)
- **Load Balancer:** ALB (Application Load Balancer)
- **Database:** RDS PostgreSQL (Multi-AZ, encrypted)

**IaC:** Terraform configurations in [`terraform/`](terraform/)

---

## 📊 Monitoring

### Dashboards

- **Grafana:** [Sales Service Dashboard](https://grafana.talma.com/d/sales-service)
- **Metrics:** Prometheus (Latency, Error Rate, Throughput)

### Key Metrics

| Metric              | Target     | Alert Threshold |
| ------------------- | ---------- | --------------- |
| Response Time (p95) | < 500ms    | > 1000ms        |
| Error Rate          | < 0.1%     | > 1%            |
| Throughput          | 50-200 RPS | -               |
| CPU Utilization     | < 70%      | > 85%           |
| Memory Usage        | < 1.5GB    | > 1.8GB         |

### Logs

- **CloudWatch Logs:** `/aws/ecs/sales-service`
- **Structured Logging:** JSON format (Serilog)
- **Trace ID:** Included in all logs (`X-Request-ID`)

### Alerts

- **On-Call:** PagerDuty "Sales Service" rotation
- **Incidents:** [Incident Response Runbook](docs/runbooks/incident-response.md)

---

## 👥 Team

**Owner:** Sales Engineering Team

**Members:**

- Tech Lead: @juan-perez
- Backend Developers: @maria-garcia, @carlos-lopez
- DevOps: @platform-team

**Communication:**

- **Slack:** #sales-service
- **Email:** sales-team@talma.com
- **Meetings:** Tuesdays 10am (Sprint Planning), Fridays 3pm (Retrospective)

**On-Call Rotation:** [PagerDuty Schedule](https://talma.pagerduty.com/schedules#ABC123)

---

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for:

- Code style guide
- Branch naming conventions
- PR review process
- Testing requirements

**Before submitting PR:**

1. ✅ All tests pass (`dotnet test`)
2. ✅ Code coverage > 80%
3. ✅ SonarQube quality gate pass
4. ✅ No security vulnerabilities (Snyk)
5. ✅ README updated (if API changes)

---

## 📄 License

Copyright © 2024 Talma. All rights reserved.

Internal use only. See [LICENSE](LICENSE) for details.

---

## 📖 Additional Documentation

- [Architecture Decision Records (ADRs)](docs/adr/)
- [Runbooks](docs/runbooks/)
- [Database Schema](docs/database-schema.md)
- [Event Catalog](docs/events/)
- [Troubleshooting Guide](docs/troubleshooting.md)

---

**Last Updated:** 2024-01-15 | **Version:** 2.3.0

````

---

## Mandatory Sections

```yaml
# ✅ MUST have these sections

1. Overview (MUST):
   - What the service does (1-2 sentences)
   - Why it exists (business purpose)
   - Boundaries (what it does NOT do)

2. Stack (MUST):
   - Language, framework, version
   - Database, message broker
   - Key dependencies

3. Prerequisites (MUST):
   - What to install before running
   - Links to download pages

4. Local Setup (MUST):
   - Step-by-step instructions
   - From git clone to running service
   - Should work in < 30 minutes

5. Running (MUST):
   - How to start service locally
   - Expected output (URL, port)
   - How to verify it's working

6. Testing (MUST):
   - How to run unit tests
   - How to run integration tests
   - Coverage target

7. Team (MUST):
   - Who owns this service
   - How to contact (Slack, email)
   - On-call rotation link

8. Contributing (MUST):
   - Link to CONTRIBUTING.md
   - OR inline guide if simple

# ✅ SHOULD have these sections

9. Architecture (SHOULD):
   - High-level diagram
   - Key patterns used
   - Folder structure

10. API Documentation (SHOULD):
    - Link to Swagger
    - Key endpoints examples
    - Authentication requirements

11. Deployment (SHOULD):
    - CI/CD pipeline description
    - Environments (dev/qa/prod)
    - Manual deployment steps (if needed)

12. Monitoring (SHOULD):
    - Dashboard links
    - Key metrics
    - Alert contacts

# Optional sections

13. Troubleshooting (nice to have)
14. Performance Tuning (nice to have)
15. FAQ (nice to have)
````

## Anti-Patterns

```yaml
# ❌ Common README mistakes

1. No Setup Instructions:

   ❌ "To run: npm start"

   Problem: Assumes knowledge (DB setup? Migrations?)

2. Outdated Information:

   ❌ "Run on Node 12" (actual: Node 20)

   Solution: Version badge, CI validates

3. No Prerequisites:

   ❌ Jumps directly to "git clone"

   Problem: Fails if Docker not installed

4. Vague Descriptions:

   ❌ "This is a microservice for orders"

   Better: "REST API for order management, publishes events to Kafka, used by Billing and Fulfillment"

5. No Team Contact:

   ❌ No mention of who owns service

   Problem: Who to ask for help?

6. Copy-Paste Template:

   ❌ "Lorem ipsum dolor sit amet..."

   Problem: Left placeholder text
```

## Validation

```yaml
# ✅ README Quality Checklist

Automated Checks (CI):

  - [ ] README.md exists in root
  - [ ] Has "Overview" section (grep)
  - [ ] Has "Setup" section (grep)
  - [ ] Has "Team" section (grep)
  - [ ] Links are not broken (markdown-link-check)
  - [ ] No TODOs or placeholders (grep "TODO")

Manual Review (PR):

  - [ ] New developer can setup in < 30 min
  - [ ] All commands work (tested locally)
  - [ ] Diagrams up-to-date
  - [ ] Contact info correct
```

---

## Requisitos Técnicos

### MUST (Obligatorio)

- **MUST** tener README.md en root de repositorio
- **MUST** incluir secciones: Overview, Stack, Prerequisites, Setup, Running, Testing, Team
- **MUST** funcionar paso a paso (new developer can execute)
- **MUST** actualizar cuando cambia (ej: migra a .NET 8)
- **MUST** validarse en CI (link checker)

### SHOULD (Fuertemente recomendado)

- **SHOULD** incluir diagrama de arquitectura
- **SHOULD** tener badges (build status, coverage)
- **SHOULD** documentar API endpoints clave
- **SHOULD** enlazar a docs adicionales (ADRs, runbooks)

### MUST NOT (Prohibido)

- **MUST NOT** omitir team/contact info
- **MUST NOT** dejar placeholders (TODO, Lorem Ipsum)
- **MUST NOT** tener información obsoleta (validar quarterly)
- **MUST NOT** asumir conocimiento previo (explicar desde cero)

---

## Referencias

- [Lineamiento: Documentación Técnica](../../lineamientos/desarrollo/03-documentacion-tecnica.md)
- [Contributing Guide Standards](./contributing-guide.md)
- [Architecture Decision Records](./architecture-decision-records.md)
- [Onboarding Guide](./onboarding-guide.md)
