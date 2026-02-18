---
id: technology-selection
sidebar_position: 10
title: Technology Selection
description: Criterios objetivos para seleccionar tecnologías y herramientas
---

# Technology Selection

## Contexto

Este estándar define criterios **objetivos** para evaluar y seleccionar tecnologías. Decisiones deben basarse en **requisitos reales**, no en hype o preferencias personales. Complementa el [lineamiento de Simplicidad Intencional](../../lineamientos/arquitectura/13-simplicidad-intencional.md) eligiendo herramientas **apropiadas al problema**.

---

## Evaluation Framework

```yaml
# ✅ Criterios para evaluar tecnologías

1. Alignment con Requisitos (Peso: 40%):
   ✅ Resuelve problema específico
   ✅ Performance adecuado (no overkill)
   ✅ Scale apropiado para volumen
   ✅ Features necesarias disponibles

   Preguntas:
     - ¿Resuelve nuestro problema específico?
     - ¿Podemos lograr objetivo con herramienta más simple?
     - ¿Features avanzadas realmente las usaremos?

2. Team Capability (Peso: 25%):
   ✅ Expertise existente en equipo
   ✅ Learning curve razonable
   ✅ Training disponible
   ✅ Hiring pool (si necesitamos contratar)

   Preguntas:
     - ¿Alguien en equipo ya lo usa?
     - ¿Cuánto tardamos en ser productivos?
     - ¿Podemos contratar si crece equipo?

3. Ecosystem & Support (Peso: 20%):
   ✅ Community activo
   ✅ Documentación completa
   ✅ Libraries/Plugins disponibles
   ✅ Long-term viability (no abandonado)

   Preguntas:
     - ¿Última release cuándo fue?
     - ¿Issues en GitHub se responden?
     - ¿Empresas grandes lo usan?

4. Operational Cost (Peso: 10%):
   ✅ Infrastructure cost
   ✅ Licensing cost
   ✅ Maintenance effort

   Preguntas:
     - ¿Costo mensual AWS?
     - ¿Licencias necesarias?
     - ¿Horas/mes mantenimiento?

5. Integration (Peso: 5%):
   ✅ Integra con stack existente
   ✅ APIs estándar (REST, gRPC)
   ✅ SDKs para .NET

   Preguntas:
     - ¿Funciona con PostgreSQL, AWS, .NET?
     - ¿Hay client library oficial?
```

## Decision Template

```yaml
# ✅ Template para documentar decisión (ADR)

Title: Selección de [Tecnología] para [Caso de Uso]

Context:
  - Problema: [Descripción del problema concreto]
  - Volumen: [Requests/día, usuarios, datos]
  - Requisitos: [Performance, reliability, features]

Options Evaluated:
  Option 1: [Nombre]
    Pros:
      - [Pro 1]
      - [Pro 2]
    Cons:
      - [Con 1]
      - [Con 2]
    Score: [0-100]

  Option 2: [Nombre]
    Pros: ...
    Cons: ...
    Score: [0-100]

Decision: [Opción elegida]

Justification:
  - [Razón 1 con datos]
  - [Razón 2 con datos]
  - Cost-benefit analysis: [Ver tabla]

Consequences:
  - [Impacto positivo 1]
  - [Trade-off aceptado]
  - [Mitigación para cons]

Reversibility:
  - Cost: [Low/Medium/High]
  - Effort: [Días/Semanas]
  - Strategy: [Cómo migrar si es necesario]

Review Trigger:
  - [Condición 1 para reevaluar]
  - [Threshold específico]
```

## Real Example: Message Broker Selection

```yaml
# ✅ Caso real: Selección de message broker (Talma 2024)

Context:
  Problem: Comunicación asíncrona entre Sales, Fulfillment, Billing
  Volumen: 2000 mensajes/día (actual), 10K/día (proyectado 1 año)
  Requisitos:
    - At-least-once delivery
    - Message ordering por partition key
    - Retention 7 días mínimo
    - Consumer groups

Options Evaluated:

┌──────────────┬─────────────┬─────────────┬──────────────┐
│ Criterio     │ AWS SQS/SNS │ RabbitMQ    │ Kafka        │
├──────────────┼─────────────┼─────────────┼──────────────┤
│ Requisitos   │ 30/40       │ 35/40       │ 40/40 ✅     │
│ - Ordering   │ FIFO queue  │ Sí          │ Partition ✅ │
│ - Retention  │ 14 días ✅  │ Config ✅   │ Ilimitado ✅ │
│ - Groups     │ No nativo   │ Sí ✅       │ Consumer ✅  │
│ - Scale      │ 10K OK ✅   │ 10K OK ✅   │ 100K+ ✅     │
├──────────────┼─────────────┼─────────────┼──────────────┤
│ Team         │ 20/25       │ 15/25       │ 18/25        │
│ - Expertise  │ AWS (medio) │ Ninguna     │ 1 dev junior │
│ - Learning   │ 1 semana ✅ │ 2 semanas   │ 2 semanas    │
│ - Hiring     │ Común ✅    │ Común ✅    │ Medio        │
├──────────────┼─────────────┼─────────────┼──────────────┤
│ Ecosystem    │ 18/20       │ 17/20       │ 20/20 ✅     │
│ - Community  │ AWS grande  │ Activo ✅   │ Muy activo ✅│
│ - Docs       │ Completa ✅ │ Buena ✅    │ Excelente ✅ │
│ - Libraries  │ AWS SDK ✅  │ Sí ✅       │ Confluent ✅ │
│ - Viability  │ Managed ✅  │ Open ✅     │ Open ✅      │
├──────────────┼─────────────┼─────────────┼──────────────┤
│ Cost         │ 9/10        │ 6/10        │ 7/10         │
│ - Infra      │ $50/mes ✅  │ $150/mes EC2│ $120/mes MSK │
│ - License    │ Free ✅     │ Free ✅     │ Free ✅      │
│ - Maintenance│ 0 (AWS) ✅  │ 8h/mes      │ 4h/mes       │
├──────────────┼─────────────┼─────────────┼──────────────┤
│ Integration  │ 5/5         │ 4/5         │ 5/5 ✅       │
│ - .NET SDK   │ AWSSDK ✅   │ Client ✅   │ Confluent ✅ │
│ - AWS        │ Native ✅   │ EC2 needed  │ MSK ✅       │
├──────────────┼─────────────┼─────────────┼──────────────┤
│ TOTAL        │ 82/100      │ 77/100      │ 90/100 ✅    │
└──────────────┴─────────────┴─────────────┴──────────────┘

Decision: ✅ Kafka (AWS MSK)

Justification:
  1. Cumple 100% requisitos (ordering, retention, consumer groups)
  2. Scale para crecimiento proyectado (10K → 100K mensajes)
  3. Expertise inicial (1 dev) + learning curve aceptable (2 semanas)
  4. Ecosystem maduro (Confluent libraries, community grande)
  5. Costo razonable ($120/mes vs $50 SQS, pero mejor features)
  6. Managed service (MSK) reduce operational burden

Trade-offs aceptados:
  - $70/mes más caro que SQS
  - Learning curve (2 semanas vs 1 semana SQS)
  - Complejidad operational mayor

Mitigations:
  - MSK managed (reduce operational overhead)
  - Training plan (2 semanas dedicated)
  - Start simple (3 topics, 2 partitions cada uno)

Reversibility:
  - Cost: Medium (2-3 semanas)
  - Strategy: Interfaces IEventPublisher/IEventConsumer
              permiten swap implementation
  - Abstractions en Application layer

Review Triggers:
  - Volumen > 100K mensajes/día (considerar Kafka self-managed)
  - Costo > $500/mes (optimizar o evaluar alternativas)
  - Operational burden > 20 horas/mes (re-evaluar managed vs self)

ADR: adr-012-kafka-mensajeria-asincrona.md
```

## Anti-Patterns

```yaml
# ❌ Malas razones para elegir tecnología

1. "Es trending en Hacker News"
   Problema: Hype ≠ Apropiado para tu contexto
   Ejemplo: Adoptar Rust porque "es rápido"
            (pero team solo sabe C#, no hay material benefit)

2. "Otra empresa lo usa"
   Problema: Su contexto ≠ Tu contexto
   Ejemplo: "Netflix usa microservices, nosotros también"
            (Netflix: 200M usuarios, tú: 1000 usuarios)

3. "Quiero aprenderlo"
   Problema: Learning personal ≠ Decisión técnica
   Ejemplo: "Usar Elixir porque quiero aprenderlo"
            (pero equipo no sabe Elixir, hiring difícil)

4. "Es más moderno"
   Problema: Nuevo ≠ Mejor
   Ejemplo: "Reescribir en GraphQL porque REST es viejo"
            (pero REST funciona bien, clientes felices)

5. "Resuelve problema hipotético"
   Problema: YAGNI violation
   Ejemplo: "Kubernetes porque quizás necesitemos scale"
            (10 requests/día actualmente)

# ✅ Buenas razones

1. "Resuelve problema medido"
   Ejemplo: "PostgreSQL read replica porque query latency p95 = 800ms"
            (target: <200ms, medimos impacto)

2. "Reduce costo operacional"
   Ejemplo: "Keycloak SSO vs implementar propio"
            (ahorra 3 meses dev + security risk)

3. "Team expertise existente"
   Ejemplo: ".NET 8 porque team tiene 5 años experiencia"
            (productividad inmediata)

4. "Scale requirement claro"
   Ejemplo: "Redis cache porque 50K requests/día, DB bottleneck medido"
            (profiling muestra problema real)
```

## Technology Radar

```yaml
# ✅ Categorías de adopción (inspirado en ThoughtWorks Radar)

ADOPT (Usar en producción):
  - .NET 8
  - PostgreSQL
  - AWS ECS Fargate
  - Kafka (MSK)
  - Terraform
  - GitHub Actions

  Criterio: Probado, team expertise, production-ready

TRIAL (Experimentar en no-crítico):
  - Dapr (service mesh light)
  - Testcontainers
  - FluentAssertions

  Criterio: Promising, low risk, evaluar en proyectos pequeños

ASSESS (Investigar, no usar todavía):
  - .NET Aspire
  - OpenTelemetry
  - gRPC

  Criterio: Interesante, necesitamos más info, no urgente

HOLD (No usar en nuevos proyectos):
  - .NET Framework 4.x (legacy, usar .NET 8)
  - MongoDB (sin caso de uso claro, preferir PostgreSQL)
  - Jenkins (usar GitHub Actions)

  Criterio: Superado por alternativas mejores

Actualización: Cada 6 meses
Owner: Architecture Team
```

---

## Requisitos Técnicos

### MUST (Obligatorio)

- **MUST** documentar selección de tecnología en ADR
- **MUST** evaluar al menos 3 opciones antes de decidir
- **MUST** usar criterios objetivos (no preferencias personales)
- **MUST** incluir análisis de costo operacional real
- **MUST** definir triggers para reevaluar decisión

### SHOULD (Fuertemente recomendado)

- **SHOULD** hacer POC para tecnologías nuevas (no producción directamente)
- **SHOULD** considerar team expertise como factor importante
- **SHOULD** preferir tecnologías con long-term support

### MUST NOT (Prohibido)

- **MUST NOT** elegir por hype o trending
- **MUST NOT** ignorar costo de learning curve
- **MUST NOT** decidir sin evaluar alternativas
- **MUST NOT** adoptar tecnología sin caso de uso claro

---

## Referencias

- [Lineamiento: Simplicidad Intencional](../../lineamientos/arquitectura/13-simplicidad-intencional.md)
- [ADR-012: Kafka Mensajería](../../../decisiones-de-arquitectura/adr-012-kafka-mensajeria-asincrona.md)
- [ADR-004: Keycloak SSO](../../../decisiones-de-arquitectura/adr-004-keycloak-sso-autenticacion.md)
- [Complexity Analysis](./complexity-analysis.md)
