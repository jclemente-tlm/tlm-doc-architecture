# Estándar Técnico — Mensajería con Kafka

## 1. Propósito

Estándares para mensajería asíncrona con Apache Kafka: modelado de eventos, topología, idempotencia, DLQ y monitoreo.

## 2. Alcance

**Aplica a:**

- Microservicios con comunicación asíncrona
- Event sourcing y procesamiento en tiempo real
- Integración de bounded contexts
- Notificaciones y auditoría

**No aplica a:**

- Comunicación síncrona (usar APIs REST)
- Transferencia de archivos (usar S3 + eventos)

## 3. Tecnologías Aprobadas

| Componente    | Tecnología                | Versión mínima | Observaciones                |
| ------------- | ------------------------- | -------------- | ---------------------------- |
| Broker        | Apache Kafka (KRaft)      | 3.6+           | No Confluent Platform        |
| Cliente .NET  | Confluent.Kafka           | 2.3+           | Producer/Consumer .NET       |
| Schema        | JSON Schema + CloudEvents | Draft 2020-12  | Sin Avro, sin SchemaRegistry |
| Serialización | System.Text.Json          | 8.0+           | JSON puro                    |
| Deduplication | PostgreSQL, Redis         | 14+, 7.2+      | processed_events, TTL        |
| Monitoring    | Grafana, Kafka Exporter   | 10.0+          | Métricas y alertas           |

## 4. Requisitos Obligatorios 🔴

### Modelado de Eventos y Naming

- Eventos inmutables, versionados, con metadata (eventId, timestamp, correlationId)
- Naming: `{domain}.{entity}.{event-type}` (ej: `order.payment.created`)
- Envelope CloudEvents para todos los eventos
- Lenguaje de dominio, tiempo pasado (`OrderCreatedEvent`)
- Documentar schema y versionado en Git

### Topología y Particionado

- Topics replicados (factor ≥ 3), mínimo 3 particiones
- Partition key: aggregateId, tenantId o entityId
- Retention: 7 días (eventos), 30 días (event sourcing)
- Cleanup policy: delete (eventos), compact (snapshots)
- Consumer groups: `{service}.{topic}`

### Garantías de Entrega

- At-least-once por defecto, exactly-once para operaciones críticas
- Idempotent producer (`enable.idempotence=true`), acks=all
- Manual commit en consumer, deduplication por CloudEvents.id
- Dead Letter Queue (DLQ) `{topic}.dlq` tras 3 reintentos
- Backoff exponencial en reintentos

### Idempotencia y Deduplicación

- processed_events en PostgreSQL para deduplication
- Business key (OrderId, TransactionId) para reintentos
- TTL de registros: 7-30 días
- Métricas de duplicados y alertas si >5%

### Esquemas y Validación

- JSON Schema + CloudEvents para todos los eventos
- Validación en producer obligatoria, en consumer opcional
- Versionado semántico, backward compatible por defecto
- Tests unitarios de schemas

### Monitoreo y Alertas

- Kafka Exporter + Grafana para lag, throughput, DLQ
- Métricas: replication_lag, event_propagation_duration, duplicados
- Alertas: lag >5s, DLQ >10 mensajes/hora, duplicados >5%

## 5. Prohibiciones ❌

- Topics sin replicación o con una sola partición
- Eventos sin eventId/timestamp/correlationId
- Payloads >1MB (usar S3)
- Consumidores no idempotentes
- Uso de Avro, Schema Registry, Confluent Platform
- JOIN cross-service en consumers
- Falta de DLQ o sin monitoreo

## 6. Configuración / Implementación

### Ejemplo: Envelope CloudEvents

```json
{
  "id": "b1f6...",
  "source": "order-service",
  "type": "OrderCreatedEvent",
  "time": "2026-02-04T12:34:56Z",
  "correlationId": "...",
  "data": { ... }
}
```

### Ejemplo: Deduplicación en PostgreSQL

```sql
CREATE TABLE processed_events (
  event_id uuid PRIMARY KEY,
  processed_at timestamptz NOT NULL DEFAULT now()
);
```

### Ejemplo: Configuración de Producer

```csharp
var config = new ProducerConfig {
    BootstrapServers = "kafka:9092",
    EnableIdempotence = true,
    Acks = Acks.All,
    MessageSendMaxRetries = int.MaxValue
};
```

### Ejemplo: DLQ y reintentos

```yaml
kafka-topics:
  - name: order.payment.created
    partitions: 6
    replication: 3
  - name: order.payment.created.dlq
    partitions: 3
    replication: 3
```

## 7. Validación

- Validar naming y versionado de topics y eventos
- Verificar idempotencia y deduplicación en consumers
- Validar configuración de DLQ y monitoreo
- Auditar schemas y compatibilidad
- Monitorear métricas de lag, duplicados y DLQ

## 8. Referencias

- [Kafka Docs](https://kafka.apache.org/documentation/)
- [CloudEvents Spec](https://cloudevents.io/)
- [JSON Schema](https://json-schema.org/)
- [Confluent.Kafka .NET](https://docs.confluent.io/clients-confluent-kafka-dotnet/current/overview.html)
- [Kafka Exporter](https://github.com/danielqsj/kafka_exporter)
- [Grafana](https://grafana.com/)
