# 9. Decisiones de Arquitectura

## 9.1 Decisiones Principales

| ADR        | Decisión                        | Estado    | Justificación           |
|------------|----------------------------------|-----------|-------------------------|
| `ADR-001`  | CQRS + Event Sourcing            | Aceptado  | Trazabilidad inmutable  |
| `ADR-002`  | PostgreSQL event store           | Aceptado  | Simplicidad inicial     |
| `ADR-003`  | Deduplicación por tenant (realm) | Aceptado  | Prevención duplicados   |
| `ADR-004`  | Event-driven propagación         | Aceptado  | Integración SITA        |
| `ADR-006`  | Multi-tenant schema separation   | Aceptado  | Aislamiento de datos    |
| `ADR-007`  | Observabilidad OpenTelemetry     | Aceptado  | Trazas y métricas       |

## 9.2 Alternativas Evaluadas

| Componente      | Alternativas                        | Selección      | Razón         |
|-----------------|-------------------------------------|----------------|---------------|
| `Event Store`   | EventStore, PostgreSQL, SNS+SQS     | PostgreSQL     | Simplicidad   |
| `API`           | REST, GraphQL, gRPC                 | REST           | Flexibilidad  |
| `Deduplicación` | Global, Por tenant (realm)          | Por tenant     | Aislamiento   |
| `Propagación`   | Síncrona, Asíncrona                 | Asíncrona      | Desacoplamiento |

## 9.3 ADR-001: Event Sourcing como Patrón Principal

**Estado**: Aceptado
**Fecha**: 2024-01-15
**Decidido por**: Equipo de Arquitectura

**Contexto**: Requisito de trazabilidad completa y auditoría robusta.

**Decisión**: Se adopta `Event Sourcing` como patrón arquitectónico principal.

**Justificación**:

- Auditabilidad total
- Análisis temporal
- Escalabilidad de lectura
- Debugging avanzado
- Analytics nativo

**Consecuencias**:

- Positivas: Auditabilidad, escalabilidad, flexibilidad
- Negativas: Complejidad inicial, eventual consistency

---

## 9.4 ADR-002: PostgreSQL como Event Store

**Estado**: Aceptado
**Fecha**: 2024-01-20
**Decidido por**: Equipo de Arquitectura

**Contexto**: Almacén confiable y performante para eventos con soporte ACID.

**Decisión**: Se utiliza `PostgreSQL` como event store.

**Justificación**:

- ACID compliance
- Soporte `JSONB`
- Performance y experiencia del equipo
- Ecosistema maduro

**Consecuencias**:

- Positivas: Confiabilidad, performance
- Negativas: Complejidad para sharding futuro

---

## 9.5 ADR-003: CQRS con Read Models Especializados

**Estado**: Aceptado
**Fecha**: 2024-01-25
**Decidido por**: Equipo de Arquitectura

**Contexto**: Optimización de consultas y vistas especializadas.

**Decisión**: Se implementa `CQRS` con read models especializados en `PostgreSQL`.

**Justificación**:

- Performance y flexibilidad
- Escalabilidad
- Analytics y reporting

**Consecuencias**:

- Positivas: Performance, flexibilidad
- Negativas: Complejidad adicional

---

## 9.6 ADR-006: Multi-tenant Schema Separation

**Estado**: Aceptado
**Fecha**: 2024-02-10
**Decidido por**: Equipo de Arquitectura + Security

**Contexto**: Aislamiento completo de datos entre tenants (realms).

**Decisión**: Separación de esquemas por tenant (realm) en `PostgreSQL`.

**Justificación**:

- Aislamiento físico
- Performance
- Compliance

**Consecuencias**:

- Positivas: Aislamiento total, performance
- Negativas: Gestión compleja de schemas

---

## 9.7 ADR-007: Observabilidad con OpenTelemetry

**Estado**: Aceptado
**Fecha**: 2024-02-15
**Decidido por**: Equipo de Arquitectura + SRE

**Contexto**: Observabilidad completa y trazabilidad distribuida.

**Decisión**: Se adopta `OpenTelemetry` con `Jaeger` y `Prometheus`.

**Justificación**:

- Estándar abierto
- Unificación de logs, métricas y trazas
- Correlación distribuida

**Consecuencias**:

- Positivas: Observabilidad completa
- Negativas: Overhead de instrumentación

---

## 9.8 Decisiones Pendientes

- Estrategia de sharding para escalamiento horizontal
- Políticas de archivado de eventos
- Estrategia de evolución de esquemas de eventos
