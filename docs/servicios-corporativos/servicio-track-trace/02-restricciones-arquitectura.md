# 2. Restricciones de la arquitectura

## 2.1 Restricciones técnicas

| Categoría | Restricción | Justificación |
|-----------|-------------|---------------|
| **Runtime** | `.NET 8` | Estándar corporativo |
| **Base de datos** | `PostgreSQL` | Robustez y ACID |
| **Arquitectura** | `CQRS` + `Event Sourcing` | Trazabilidad inmutable |
| **APIs** | `REST` + `GraphQL` | Flexibilidad consultas |
| **Contenedores** | `Docker` | Portabilidad |

## 2.2 Restricciones de rendimiento

| Métrica | Objetivo | Razón |
|---------|----------|-------|
| **Capacidad** | `50,000+ eventos/hora` | Volumen operacional |
| **Latencia ingesta** | `< 100ms` | Tiempo real |
| **Latencia consulta** | `< 200ms` | Experiencia usuario |
| **Disponibilidad** | `99.9%` | SLA empresarial |

## 2.3 Restricciones de seguridad

| Aspecto | Requerimiento | Estándar |
|---------|--------------|----------|
| **Inmutabilidad** | `Event sourcing` | Auditoría |
| **Cifrado** | `TLS 1.3` | Mejores prácticas |
| **Autenticación** | JWT obligatorio | Zero trust |
| **Trazabilidad** | Auditoría completa | Compliance |

## 2.4 Restricciones organizacionales

| Área | Restricción | Impacto |
|------|-------------|---------|
| **Multi-tenancy** | Aislamiento por país | Regulaciones locales |
| **Operaciones** | DevOps 24/7 | Continuidad negocio |
| **Documentación** | ARC42 actualizada | Mantenibilidad |

El **Sistema de Track & Trace** opera bajo restricciones técnicas, operacionales y de compliance específicas para el seguimiento en tiempo real de eventos operacionales. Estas restricciones definen las decisiones arquitectónicas críticas del sistema.

### Arquitectura CQRS Obligatoria

| Restricción | Descripción | Justificación | Implementación |
|-------------|-------------|---------------|----------------|
| **CQRS Pattern** | Separación Command/Query obligatoria | Optimización lectura vs escritura, escalabilidad | Comandos para ingestión, queries para consulta |
| **Event Sourcing** | Almacenamiento basado en eventos | Auditabilidad completa, reconstrucción de estado | Event store como fuente de verdad |
| **Message Queue** | Event Bus para event streaming | Alta capacidad de procesamiento, durabilidad, replay capability | Event topics por tipo de evento |
| **Read Models** | Vistas materializadas para consultas | Rendimiento de consultas complejas | `PostgreSQL` para read models |

### Stack Tecnológico Mandatorio

| Componente | Tecnología Requerida | Versión Mínima | Justificación |
|------------|---------------------|---------------|---------------|
| **Runtime** | `.NET 8 LTS` | 8.0+ | Standardización corporativa, rendimiento |
| **Event Store** | `PostgreSQL`/SNS+SQS/RabbitMQ | 15+/Latest | Event streaming, alta disponibilidad |
| **Read Database** | `PostgreSQL` | 15+ | Consultas complejas, soporte JSON, analítica |
| **Cache Layer** | `Redis` | 7.0+ | Rendimiento de consultas, dashboards en tiempo real |
| **Base de Datos de Series Temporales** | `InfluxDB` | 2.7+ | Almacenamiento de métricas, analítica basada en tiempo |
| **Motor de Búsqueda** | `Elasticsearch` | 8.0+ | Búsqueda de texto completo, agregación de registros |

### Rendimiento y Capacidad

| Métrica | Restricción | Justificación | Arquitectura Requerida |
|---------|------------|---------------|-----------------------|
| **Event Ingestion** | `50,000 eventos/segundo` | Peak operational loads | Event partitioning, async processing |
| **Query Response** | `p95 < 200ms` | Real-time dashboard requirements | Materialized views, caching |
| **Data Retention** | `7 años eventos`, `2 años métricas` | Cumplimiento, análisis operacional | Tiered storage, archival strategy |
| **Real-time Updates** | `< 5 segundos latencia` | Operational decision making | Event streaming, WebSocket notifications |

### Integración y Conectividad

| Sistema | Protocolo | Restricción | Implementación |
|---------|-----------|-------------|----------------|
| **SITA Messaging** | Event Bus | Real-time event consumption | Event-driven integration |
| **Notification System** | Event Bus | Event-based notifications | Publish events to notification topics |
| **Identity System** | OAuth2/OIDC | Secure API access | JWT token validation |
| **External APIs** | REST/GraphQL | Standard protocols | RESTful APIs, GraphQL para consultas complejas |
| **Dashboard Systems** | WebSocket + REST | Real-time updates | SignalR hubs, REST APIs |

## 2.5 Restricciones operacionales

### Disponibilidad y Confiabilidad

| Aspecto | Restricción | Justificación | Implementación |
|---------|------------|---------------|----------------|
| **Uptime Target** | `99.95%` disponibilidad | Visibilidad operativa crítica | Active-active clustering |
| **Data Durability** | `99.999999999%` (11 9's) | Event data cannot be lost | Event replication, backup strategies |
| **Disaster Recovery** | RTO: 1 hour, RPO: 5 minutes | Continuidad empresarial | Cross-region replication |
| **Event Replay** | Soporte para replay histórico | Data recovery, debugging | Event retention, offset management |

### Escalabilidad y Rendimiento

| Aspecto | Requerimiento | Implementación | Monitoreo |
|---------|--------------|----------------|-----------|
| **Horizontal Scaling** | Escalado lineal con carga | Servicios stateless, datos particionados | Métricas de rendimiento, auto-scaling |
| **Data Partitioning** | Partición por tenant/tiempo | Rendimiento óptimo de consultas | Partition monitoring |
| **Query Optimization** | Respuestas sub-segundo | Read models indexados, caching | Seguimiento de rendimiento de consultas |
| **Storage Scaling** | Expansión automática | Almacenamiento elástico, ciclo de vida | Storage utilization monitoring |

### Data Management

| Aspecto | Restricción | Justificación | Implementación |
|---------|------------|---------------|----------------|
| **Data Consistency** | Eventual consistency aceptable | Trade-off CQRS, performance | Event-driven consistency |
| **Schema Evolution** | Cambios retrocompatibles | Evolución, integración | Avro schema registry |
| **Data Lineage** | Trazabilidad completa de eventos | Auditoría, debugging, compliance | Event correlation IDs |
| **Archive Strategy** | Archivado automático | Optimización de costos, compliance | Tiered storage, compresión |

## 2.6 Restricciones regulatorias y compliance

### Retención de Datos

| Tipo de Dato | Período Retención | Justificación | Implementación |
|--------------|------------------|---------------|----------------|
| **Eventos Operacionales** | `7 años` | Auditoría, investigaciones | Archive storage, retrieval capability |
| **Eventos de Seguridad** | `10 años` | Compliance, forense | Immutable storage, encryption |
| **Métricas de Performance** | `2 años` | Análisis operacional | Time-series compression |
| **Logs de Sistema** | `1 año` | Resolución de problemas, debugging | Log rotation, archival |

### Auditoría y Compliance

| Restricción | Descripción | Implementación | Validación |
|-------------|------------|----------------|-----------|
| **Audit Trail** | Historial completo de eventos | Immutable event log | Audit compliance checks |
| **Data Privacy** | Cumplimiento GDPR, LGPD | Anonimización, eliminación | Privacy impact assessments |
| **Access Control** | RBAC granular | Integración de identidad | Access reviews, monitoring |
| **Change Tracking** | Registro de modificaciones | Event sourcing pattern | Change audit reports |

### Requerimientos Jurisdiccionales

| Jurisdicción | Requerimiento | Implementación | Verificación |
|--------------|--------------|----------------|--------------|
| **European Union** | Protección de datos GDPR | Data residency, encryption | Privacy compliance audits |
| **United States** | Controles SOX | Access controls, trazas de auditoría | Financial cumplimiento de auditoría |
| **Latin America** | Leyes locales de protección de datos | Configuración por país | Regional compliance reviews |
| **Aviation Authorities** | Retención de datos operacionales | Requisitos sectoriales | Aviation compliance audits |

## 2.7 Restricciones de seguridad

### Autenticación y Autorización

| Aspecto | Requerimiento | Implementación | Validación |
|---------|--------------|----------------|-----------|
| **API Authentication** | OAuth2/OIDC obligatorio | Integración con Keycloak | Token validation testing |
| **Service-to-Service** | mTLS para comunicación interna | Certificados | Certificate validation |
| **Data Access** | Permisos RBAC | Autorización granular | Permission testing |
| **Sensitive Data** | Cifrado a nivel de campo | Column encryption, key management | Encryption compliance |

### Seguridad de Datos

| Control | Propósito | Implementación | Monitoreo |
|---------|----------|----------------|-----------|
| **Encryption at Rest** | Protección de datos | AES-256 database encryption | Encryption status monitoring |
| **Encryption in Transit** | Seguridad de comunicación | TLS 1.3 | Certificate monitoring |
| **Event Integrity** | Detección de alteraciones | Firmas digitales, checksums | Integrity validation |
| **Access Logging** | Auditoría de accesos | Access logs estructurados | Security event monitoring |

### Seguridad de Red

| Aspecto | Requerimiento | Implementación | Validación |
|---------|--------------|----------------|-----------|
| **Network Segmentation** | Zonas de red aisladas | VPC, subnets, security groups | Network topology review |
| **Firewall Rules** | Acceso mínimo necesario | Exposición mínima de puertos | Security rule audits |
| **DDoS Protection** | Mitigación de ataques | Rate limiting, traffic analysis | DDoS testing |
| **Intrusion Detection** | Monitoreo de seguridad | IDS/IPS deployment | Security alert validation |

## 2.8 Restricciones específicas CQRS

### Command Side (Write)

| Aspecto | Restricción | Implementación | Validación |
|---------|------------|----------------|-----------|
| **Event Schema** | Estructura inmutable | Avro schema evolution | Schema compatibility testing |
| **Command Validation** | Validación de reglas de negocio | Domain validation | Business rule testing |
| **Event Ordering** | Orden cronológico | Event partitioning strategy | Ordering verification |
| **Idempotency** | Manejo de duplicados | Idempotency keys | Duplicate detection testing |

### Query Side (Read)

| Aspecto | Restricción | Implementación | Validación |
|---------|------------|----------------|-----------|
| **View Materialization** | Optimización para lectura | Read models desnormalizados | Query performance testing |
| **Cache Strategy** | Caché multinivel | Redis + application cache | Cache hit rate monitoring |
| **Search Capabilities** | Búsqueda full-text y facetada | Integración con Elasticsearch | Search relevance testing |
| **Real-time Updates** | Actualizaciones en vivo | Event-driven view updates | Update latency monitoring |

### Event Store

| Aspecto | Restricción | Implementación | Validación |
|---------|------------|----------------|-----------|
| **Event Versioning** | Soporte a evolución de esquema | Version fields, migration scripts | Compatibility testing |
| **Snapshot Strategy** | Optimización de performance | Snapshots periódicos | Snapshot validation |
| **Replay Capability** | Procesamiento histórico | Offset management | Replay testing |
| **Storage Optimization** | Almacenamiento eficiente | Compresión, tiered storage | Storage efficiency monitoring |

## 2.9 Restricciones de integración

### Integración Basada en Eventos

| Sistema | Tipos de Eventos | Restricciones | Implementación |
|---------|-----------------|---------------|----------------|
| **SITA Messaging** | `Flight events`, `message status` | Consumo en tiempo real | Event consumer groups |
| **Notification System** | `Alert triggers`, `status updates` | Publicación de baja latencia | Async event publishing |
| **Dashboard Systems** | `Real-time metrics`, `alerts` | Actualizaciones sub-segundo | WebSocket streaming |
| **External Analytics** | `Data export`, `reporting` | Batch y streaming | Data pipeline integration |

### Integración de API

| Tipo de Integración | Protocolo | Restricciones | Implementación |
|---------------------|-----------|---------------|----------------|
| **Internal APIs** | `REST` + `GraphQL` | Patrones estándar | OpenAPI specs, GraphQL schema |
| **External Partners** | `REST APIs` | Rate limiting, seguridad | API gateway, authentication |
| **Real-time Feeds** | `WebSocket` + `Server-Sent Events` | Gestión de conexiones | SignalR, connection pooling |
| **Batch Exports** | File-based (`CSV`, `JSON`, `Parquet`) | Manejo de grandes volúmenes | Streaming exports, compression |

## 2.10 Restricciones de monitoreo

### Observabilidad Obligatoria

| Componente | Herramienta | Propósito | Configuración |
|------------|------------|-----------|--------------|
| **Metrics** | Prometheus + Grafana | Monitoreo de performance | Custom metrics, dashboards |
| **Logging** | ELK Stack | Logging centralizado | Structured JSON logs |
| **Tracing** | OpenTelemetry + Jaeger | Trazas distribuidas | Request correlation |
| **Health Checks** | ASP.NET Core Health Checks | Disponibilidad de servicio | Health endpoints |

### Métricas Empresariales

| Métrica | Propósito | Implementación | Alertas |
|---------|----------|----------------|--------|
| **Event Ingestion Rate** | Monitoreo operacional | Counter metrics | Rate anomaly detection |
| **Query Response Time** | Seguimiento de performance | Histogram metrics | SLA breach alerts |
| **Data Freshness** | Capacidad en tiempo real | Timestamp tracking | Stale data alerts |
| **Error Rates** | Salud del sistema | Error counters | Error spike detection |

## 2.11 Impacto en el diseño

### Decisiones Arquitectónicas Derivadas

| Restricción | Decisión de Diseño | Compromiso | Mitigación |
|-------------|-------------------|------------|------------|
| **CQRS Requirement** | Modelos de lectura/escritura separados | Eventual consistency | Event-driven synchronization |
| **Alta capacidad de procesamiento** | Arquitectura event streaming | Complejidad | Managed Event service |
| **Requerimientos tiempo real** | Caching en memoria | Overhead de memoria | Cache optimization |
| **Retención a largo plazo** | Tiered storage strategy | Costos de almacenamiento | Automated lifecycle policies |

### Implicaciones de la Pila Tecnológica

| Capa | Elección Tecnológica | Factor de Restricción | Alternativa Considerada |
|------|---------------------|----------------------|------------------------|
| **Event Store** | `PostgreSQL`/SNS+SQS/RabbitMQ | Capacidad, durabilidad | EventStore (complejidad), AWS Kinesis (vendor lock) |
| **Read Database** | `PostgreSQL` | Complejidad de consulta, JSON | MongoDB (consistencia), ClickHouse (complejidad operativa) |
| **Time Series** | `InfluxDB` | Analítica temporal | Prometheus (query language), TimescaleDB (licencias) |
| **Search** | `Elasticsearch` | Búsqueda full-text, analítica | Solr (mantenimiento), Amazon OpenSearch (vendor dependency) |

### Consideraciones Operacionales

| Aspecto | Implicación | Estrategia de Mitigación |
|---------|------------|-------------------------|
| **Data Volume** | Requerimientos de almacenamiento | Compresión, archivado, tiered storage |
| **Query Complexity** | Optimización de performance | Materialized views, indexing, caching |
| **Real-time Processing** | Uso intensivo de recursos | Escalado horizontal, algoritmos eficientes |
| **Data Consistency** | Desafíos de consistencia eventual | Monitoreo, resolución de conflictos |

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
