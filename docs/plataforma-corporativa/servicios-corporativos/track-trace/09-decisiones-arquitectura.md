# 9. Decisiones de arquitectura

## 9.1 Decisiones principales

| ADR        | Decisión                        | Estado    | Justificación           |
|------------|----------------------------------|-----------|-------------------------|
| ADR-001    | Persistencia de eventos en PostgreSQL | Aceptado  | Simplicidad, robustez   |
| ADR-002    | Multi-tenant por esquema         | Aceptado  | Aislamiento de datos    |
| ADR-003    | Procesamiento asíncrono con SQS  | Aceptado  | Escalabilidad, desacople|
| ADR-004    | Integración con SITA Messaging   | Aceptado  | Interoperabilidad       |
| ADR-005    | Observabilidad con OpenTelemetry y Prometheus | Aceptado | Trazabilidad y métricas |

## 9.2 Alternativas evaluadas

| Componente      | Alternativas                        | Selección      | Razón         |
|-----------------|-------------------------------------|----------------|---------------|
| Persistencia    | EventStoreDB, PostgreSQL, DynamoDB  | PostgreSQL     | Experiencia, ACID, soporte JSONB |
| API             | REST, GraphQL, gRPC                 | REST           | Simplicidad, interoperabilidad  |
| Multi-tenancy   | Esquema por tenant, columna por tenant | Esquema por tenant | Aislamiento, compliance |
| Mensajería      | SQS, Kafka, RabbitMQ                | SQS            | Integración nativa AWS, simplicidad |

## 9.3 Decisiones clave

### ADR-001: Persistencia de eventos en PostgreSQL

- **Contexto**: Se requiere almacenamiento confiable, performante y flexible para eventos.
- **Decisión**: Uso de PostgreSQL (AWS RDS) como base de datos principal.
- **Consecuencias**: Simplicidad operativa, soporte ACID, flexibilidad con JSONB.

### ADR-002: Multi-tenant por esquema

- **Contexto**: Aislamiento de datos y cumplimiento normativo.
- **Decisión**: Separación de datos por esquema en PostgreSQL.
- **Consecuencias**: Aislamiento fuerte, gestión de recursos por tenant.

### ADR-003: Procesamiento asíncrono con SQS

- **Contexto**: Desacoplar la ingesta y el procesamiento de eventos.
- **Decisión**: Uso de AWS SQS como cola de eventos.
- **Consecuencias**: Escalabilidad, tolerancia a fallos, desacople.

### ADR-004: Integración con SITA Messaging

- **Contexto**: Necesidad de interoperar con sistemas externos.
- **Decisión**: Publicación de eventos relevantes a SITA Messaging.
- **Consecuencias**: Integración flexible, propagación de eventos.

### ADR-005: Observabilidad con OpenTelemetry y Prometheus

- **Contexto**: Requerimiento de monitoreo y trazabilidad.
- **Decisión**: Uso de OpenTelemetry para trazas y Prometheus para métricas.
- **Consecuencias**: Observabilidad unificada, monitoreo proactivo.

## 9.4 Decisiones pendientes

- Estrategia de sharding para escalamiento horizontal.
- Políticas de archivado y retención de eventos.
- Estrategia de evolución de esquemas de eventos.
