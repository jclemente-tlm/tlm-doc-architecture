# 2. Restricciones de la arquitectura

## 2.1 Restricciones técnicas

| Categoría | Restricción | Justificación |
|------------|---------------|---------------|
| **Runtime** | .NET 8 | Estándar corporativo |
| **Base de datos** | PostgreSQL | Robustez y ACID |
| **Arquitectura** | CQRS + Event Sourcing | Trazabilidad inmutable |
| **APIs** | REST + GraphQL | Flexibilidad consultas |
| **Contenedores** | Docker | Portabilidad |

## 2.2 Restricciones de rendimiento

| Métrica | Objetivo | Razón |
|---------|----------|-------|
| **Capacidad** | 50,000+ eventos/hora | Volumen operacional |
| **Latencia ingesta** | < 100ms | Tiempo real |
| **Latencia consulta** | < 200ms | Experiencia usuario |
| **Disponibilidad** | 99.9% | SLA empresarial |

## 2.3 Restricciones de seguridad

| Aspecto | Requerimiento | Estándar |
|---------|---------------|----------|
| **Inmutabilidad** | Event sourcing | Auditoría |
| **Cifrado** | TLS 1.3 | Mejores prácticas |
| **Autenticación** | JWT obligatorio | Zero trust |
| **Trazabilidad** | Auditoría completa | Compliance |

## 2.4 Restricciones organizacionales

| Área | Restricción | Impacto |
|------|---------------|--------|
| **Multi-tenancy** | Aislamiento por país | Regulaciones locales |
| **Operaciones** | DevOps 24/7 | Continuidad negocio |
| **Documentación** | ARC42 actualizada | Mantenibilidad |

El **Sistema de Track & Trace** debe operar bajo restricciones técnicas, operacionales y de compliance específicas para el seguimiento en tiempo real de eventos operacionales. Estas restricciones definen las decisiones arquitectónicas críticas del sistema.

## 2.1 Restricciones técnicas

### Arquitectura CQRS Obligatoria

| Restricción | Descripción | Justificación | Implementación |
|-------------|-------------|---------------|----------------|
| **CQRS Pattern** | Separación Command/Query obligatoria | Optimización lectura vs escritura, escalabilidad | Comandos para ingestión, queries para consulta |
| **Event Sourcing** | Almacenamiento basado en eventos | Auditabilidad completa, reconstrucción de estado | Event store como fuente de verdad |
| **Message Queue** | Event Bus para event streaming | Alta capacidad de procesamiento, durabilidad, replay capability | Event topics por tipo de evento |
| **Read Models** | Vistas materializadas para consultas | Rendimiento de consultas complejas | PostgreSQL para read models |

### Stack Tecnológico Mandatorio

| Componente | Tecnología Requerida | Versión Mínima | Justificación |
|------------|---------------------|----------------|---------------|
| **Runtime** | .NET 8 LTS | 8.0+ | Standardización corporativa, rendimiento |
| **Event Store** | PostgreSQL/SNS+SQS/RabbitMQ | 15+/Latest | Event streaming, alta disponibilidad |
| **Read Database** | PostgreSQL | 15+ | Consultas complejas, soporte JSON, analítica |
| **Cache Layer** | Redis | 7.0+ | Rendimiento de consultas, dashboards en tiempo real |
| **Base de Datos de Series Temporales** | InfluxDB | 2.7+ | Almacenamiento de métricas, analítica basada en tiempo |
| **Motor de Búsqueda** | Elasticsearch | 8.0+ | Búsqueda de texto completo, agregación de registros |

### Rendimiento y Capacidad

| Métrica | Restricción | Justificación | Arquitectura Requerida |
|---------|-------------|---------------|------------------------|
| **Event Ingestion** | 50,000 eventos/segundo | Peak operational loads | Event partitioning, async processing |
| **Query Response** | p95 < 200ms | Real-time dashboard requirements | Materialized views, caching |
| **Data Retention** | 7 años eventos, 2 años métricas | Cumplimiento, análisis operacional | Tiered storage, archival strategy |
| **Real-time Updates** | < 5 segundos latencia | Operational decision making | Event streaming, WebSocket notifications |

### Integración y Conectividad

| Sistema | Protocolo | Restricción | Implementación |
|---------|-----------|-------------|----------------|
| **SITA Messaging** | Event Bus | Real-time event consumption | Event-driven integration |
| **Notification System** | Event Bus | Event-based notifications | Publish events to notification topics |
| **Identity System** | OAuth2/OIDC | Secure API access | JWT token validation |
| **External APIs** | REST/GraphQL | Standard protocols | RESTful APIs, GraphQL for complex queries |
| **Dashboard Systems** | WebSocket + REST | Real-time updates | SignalR hubs, REST APIs |

## 2.2 Restricciones operacionales

### Disponibilidad y Confiabilidad

| Aspecto | Restricción | Justificación | Implementación |
|---------|-------------|---------------|----------------|
| **Uptime Target** | 99.95% disponibilidad | Critical operational visibility | Active-active clustering |
| **Data Durability** | 99.999999999% (11 9's) | Event data cannot be lost | Event replication, backup strategies |
| **Disaster Recovery** | RTO: 1 hour, RPO: 5 minutes | Continuidad empresarial | Cross-region replication |
| **Event Replay** | Support for historical replay | Data recovery, debugging | Event retention, offset management |

### Escalabilidad y Rendimiento

| Aspecto | Requirement | Implementation | Monitoring |
|---------|-------------|----------------|------------|
| **Horizontal Scaling** | Linear scaling with load | Stateless services, partitioned data | Métricas de rendimiento, auto-scaling |
| **Data Partitioning** | Partition by tenant/time | Rendimiento óptimo de consultas | Partition monitoring |
| **Query Optimization** | Sub-second response times | Indexed read models, caching | Seguimiento de rendimiento de consultas |
| **Storage Scaling** | Automatic storage expansion | Elastic storage, data lifecycle | Storage utilization monitoring |

### Data Management

| Aspecto | Restricción | Justificación | Implementación |
|---------|-------------|---------------|----------------|
| **Data Consistency** | Eventual consistency acceptable | CQRS trade-off, performance | Event-driven consistency |
| **Schema Evolution** | Backward-compatible changes | System evolution, integration | Avro schema registry |
| **Data Lineage** | Complete event traceability | Audit, debugging, compliance | Event correlation IDs |
| **Archive Strategy** | Automated data archiving | Cost optimization, compliance | Tiered storage, compression |

## 2.3 Restricciones regulatorias y compliance

### Retención de Datos

| Tipo de Dato | Período Retención | Justificación | Implementación |
|--------------|-------------------|---------------|----------------|
| **Eventos Operacionales** | 7 años | Auditoría, investigaciones | Archive storage, retrieval capability |
| **Eventos de Seguridad** | 10 años | Compliance, forense | Immutable storage, encryption |
| **Métricas de Performance** | 2 años | Análisis operacional | Time-series compression |
| **Logs de Sistema** | 1 año | Resolución de problemas, debugging | Log rotation, archival |

### Auditoría y Compliance

### Auditoría y Cumplimiento

| Restricción | Descripción | Implementación | Validación |
|-------------|-------------|----------------|------------|
| **Audit Trail** | Complete event history | Immutable event log | Audit compliance checks |
| **Data Privacy** | GDPR, LGPD compliance | Data anonymization, deletion | Privacy impact assessments |
| **Access Control** | RBAC with fine-grained permissions | Identity integration | Access reviews, monitoring |
| **Change Tracking** | All modifications logged | Event sourcing pattern | Change audit reports |

### Requerimientos Jurisdiccionales

| Jurisdicción | Requerimiento | Implementación | Verificación de Cumplimiento |
|-------------|-------------|----------------|------------------|
| **European Union** | GDPR data protection | Data residency, encryption | Privacy compliance audits |
| **United States** | SOX financial controls | Access controls, trazas de auditoría | Financial cumplimiento de auditoría |
| **Latin America** | Local data protection laws | Country-specific configurations | Regional compliance reviews |
| **Aviation Authorities** | Operational data retention | Industry-specific requirements | Aviation compliance audits |

## 2.4 Restricciones de seguridad

### Autenticación y Autorización

| Aspecto | Requerimiento | Implementación | Validación |
|---------|-------------|----------------|------------|
| **API Authentication** | OAuth2/OIDC mandatory | Keycloak integration | Token validation testing |
| **Service-to-Service** | mTLS for internal communication | Certificate-based authentication | Certificate validation |
| **Data Access** | Role-based permissions | Fine-grained authorization | Permission testing |
| **Sensitive Data** | Field-level encryption | Column encryption, key management | Encryption compliance |

### Seguridad de Datos

| Control | Propósito | Implementación | Monitoreo |
|---------|---------|----------------|------------|
| **Encryption at Rest** | Data protection | AES-256 database encryption | Encryption status monitoring |
| **Encryption in Transit** | Communication security | TLS 1.3 for all communications | Certificate monitoring |
| **Event Integrity** | Tamper detection | Digital signatures, checksums | Integrity validation |
| **Access Logging** | Security auditing | Comprehensive access logs | Security event monitoring |

### Seguridad de Red

| Aspecto | Requerimiento | Implementación | Validación |
|--------|-------------|----------------|------------|
| **Network Segmentation** | Isolated network zones | VPC, subnets, security groups | Network topology review |
| **Firewall Rules** | Least privilege access | Minimal port exposure | Security rule audits |
| **DDoS Protection** | Attack mitigation | Rate limiting, traffic analysis | DDoS testing |
| **Intrusion Detection** | Security monitoring | IDS/IPS deployment | Security alert validation |

## 2.5 Restricciones específicas CQRS

### Command Side (Write)

| Aspecto | Restricción | Implementación | Validación |
|--------|------------|----------------|------------|
| **Event Schema** | Immutable event structure | Avro schema evolution | Schema compatibility testing |
| **Command Validation** | Business rule enforcement | Domain validation | Business rule testing |
| **Event Ordering** | Chronological ordering | Event partitioning strategy | Ordering verification |
| **Idempotency** | Duplicate event handling | Idempotency keys | Duplicate detection testing |

### Query Side (Read)

| Aspecto | Restricción | Implementación | Validación |
|--------|------------|----------------|------------|
| **View Materialization** | Optimized for read patterns | Denormalized read models | Query performance testing |
| **Cache Strategy** | Multi-level caching | Redis + application cache | Cache hit rate monitoring |
| **Search Capabilities** | Full-text and faceted search | Elasticsearch integration | Search relevance testing |
| **Real-time Updates** | Live dashboard updates | Event-driven view updates | Update latency monitoring |

### Event Store

| Aspecto | Restricción | Implementación | Validación |
|--------|------------|----------------|------------|
| **Event Versioning** | Schema evolution support | Version fields, migration scripts | Compatibility testing |
| **Snapshot Strategy** | Performance optimization | Periodic snapshots | Snapshot validation |
| **Replay Capability** | Historical event processing | Offset management | Replay testing |
| **Storage Optimization** | Cost-effective storage | Compression, tiered storage | Storage efficiency monitoring |

## 2.6 Restricciones de integración

### Integración Basada en Eventos

| Sistema | Tipos de Eventos | Restricciones | Implementación |
|--------|-------------|-------------|----------------|
| **SITA Messaging** | Flight events, message status | Real-time consumption | Event consumer groups |
| **Notification System** | Alert triggers, status updates | Low latency publishing | Async event publishing |
| **Dashboard Systems** | Real-time metrics, alerts | Sub-second updates | WebSocket streaming |
| **External Analytics** | Data export, reporting | Batch and streaming | Data pipeline integration |

### Integración de API

| Tipo de Integración | Protocolo | Restricciones | Implementación |
|------------------|----------|-------------|----------------|
| **Internal APIs** | REST + GraphQL | Standard patterns | OpenAPI specs, GraphQL schema |
| **External Partners** | REST APIs | Rate limiting, security | API gateway, authentication |
| **Real-time Feeds** | WebSocket + Server-Sent Events | Connection management | SignalR, connection pooling |
| **Batch Exports** | File-based (CSV, JSON, Parquet) | Large dataset handling | Streaming exports, compression |

## 2.7 Restricciones de monitoreo

### Observabilidad Obligatoria

| Componente | Herramienta | Propósito | Configuración |
|-----------|------|---------|---------------|
| **Metrics** | Prometheus + Grafana | Performance monitoring | Custom metrics, dashboards |
| **Logging** | ELK Stack | Centralized logging | Structured JSON logs |
| **Tracing** | OpenTelemetry + Jaeger | Distributed tracing | Request correlation |
| **Health Checks** | ASP.NET Core Health Checks | Service disponibilidad | Health endpoints |

### Métricas Empresariales

| Métrica | Propósito | Implementación | Alertas |
|--------|---------|----------------|----------|
| **Event Ingestion Rate** | Operational monitoring | Counter metrics | Rate anomaly detection |
| **Query Response Time** | Performance tracking | Histogram metrics | SLA breach alerts |
| **Data Freshness** | Real-time capability | Timestamp tracking | Stale data alerts |
| **Error Rates** | System health | Error counters | Error spike detection |

## 2.8 Impacto en el diseño

### Decisiones Arquitectónicas Derivadas

| Restricción | Decisión de Diseño | Compromiso | Mitigación |
|------------|----------------|-----------|------------|
| **CQRS Requirement** | Separate read/write models | Eventual consistency | Event-driven synchronization |
| **High Capacidad de procesamiento** | Event streaming architecture | Complexity increase | Managed Event service |
| **Real-time Requirements** | In-memory caching | Memory overhead | Cache optimization |
| **Long-term Retention** | Tiered storage strategy | Storage costs | Automated lifecycle policies |

### Implicaciones de la Pila Tecnológica

| Capa | Elección Tecnológica | Factor de Restricción | Alternativa Considerada |
|-------|-------------------|-------------------|----------------------|
| **Event Store** | PostgreSQL/SNS+SQS/RabbitMQ | Capacidad de procesamiento, durability | EventStore (complexity), AWS Kinesis (vendor lock) |
| **Read Database** | PostgreSQL | Query complexity, JSON support | MongoDB (consistency), ClickHouse (operational complexity) |
| **Time Series** | InfluxDB | Time-based analytics | Prometheus (query language), TimescaleDB (licensing) |
| **Search** | Elasticsearch | Full-text search, analytics | Solr (maintenance), Amazon OpenSearch (vendor dependency) |

### Consideraciones Operacionales

| Aspecto | Implicación | Estrategia de Mitigación |
|--------|-------------|-------------------|
| **Data Volume** | Large storage requirements | Compression, archival, tiered storage |
| **Query Complexity** | Performance optimization needed | Materialized views, indexing, caching |
| **Real-time Processing** | Resource intensive | Horizontal scaling, efficient algorithms |
| **Data Consistency** | Eventual consistency challenges | Monitoring, conflict resolution strategies |

## Referencias

### Architectural Patterns

- [CQRS Pattern](https://docs.microsoft.com/en-us/azure/architecture/patterns/cqrs)
- [Event Sourcing Pattern](https://docs.microsoft.com/en-us/azure/architecture/patterns/event-sourcing)
- [Saga Pattern](https://microservices.io/patterns/data/saga.html)

### Technologies

- [Event-Driven Architecture](https://martinfowler.com/articles/201701-event-driven.html)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [InfluxDB Documentation](https://docs.influxdata.com/)
- [Elasticsearch Documentation](https://www.elastic.co/guide/)

### Compliance and Standards

- [GDPR Regulation](https://gdpr-info.eu/)
- [SOX Compliance](https://www.sox-online.com/)
- [ISO 27001](https://www.iso.org/isoiec-27001-information-security.html)
