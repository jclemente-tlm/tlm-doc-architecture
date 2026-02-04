---
id: event-topology
sidebar_position: 4
title: Topología de Eventos
description: Estándar para arquitectura de topics Kafka: naming conventions, partitioning strategy, retention policies y topic organization
---

# Estándar Técnico — Topología de Eventos

---

## 1. Propósito

Definir arquitectura de topics Kafka con naming conventions (`{domain}.{entity}.{event}`), estrategia de particionado por tenant_id o entity_id, retention policies (7 días default) y organización de topics por dominio de negocio.

---

## 2. Alcance

**Aplica a:**

- Diseño de topics Kafka
- Naming de eventos
- Partitioning strategy
- Retention y compaction
- Consumer groups

**No aplica a:**

- Queue-based systems (RabbitMQ)

---

## 3. Tecnologías Aprobadas

| Componente         | Tecnología                | Versión mínima | Observaciones    |
| ------------------ | ------------------------- | -------------- | ---------------- |
| **Message Broker** | Apache Kafka Kraft        | 3.5+           | Self-managed     |
| **Management**     | kafka-topics CLI          | -              | Admin operations |
| **Monitoring**     | Grafana + Prometheus      | -              | Lags, throughput |
| **Schema**         | JSON Schema + CloudEvents | -              | Event structure  |

> El uso de tecnologías no listadas requiere aprobación de Arquitectura.

---

## 4. Requisitos Obligatorios 🔴

### Naming Conventions

- [ ] **Pattern**: `{domain}.{entity}.{event}` (lowercase, dots)
- [ ] **Ejemplos**: `payment.transaction.created`, `customer.account.updated`
- [ ] **NO guiones**: Usar dots (.) no hyphens (-)
- [ ] **NO versiones en nombre**: Usar schema evolution

### Partitioning

- [ ] **Key**: `tenant_id` o `entity_id` (consistente por domain)
- [ ] **Particiones**: Múltiplos de 3 (3, 6, 12, 24)
- [ ] **NO single partition**: Mínimo 3 para alta disponibilidad
- [ ] **Ordenamiento**: Garantizado dentro de partición

### Retention

- [ ] **Default**: 7 días (168 horas)
- [ ] **Eventos críticos**: 30 días
- [ ] **Compaction**: Solo para state topics
- [ ] **Cleanup policy**: delete (default) o compact

### Replication

- [ ] **Replication factor**: 3 (mínimo)
- [ ] **Min in-sync replicas**: 2
- [ ] **Unclean leader election**: false

---

## 5. Naming Conventions

### Patrón Estándar

```text
{domain}.{entity}.{event}

Domains:
- payment (Pagos)
- customer (Clientes)
- inventory (Inventario)
- notification (Notificaciones)
- audit (Auditoría)

Events:
- created
- updated
- deleted
- failed
- completed
```

### Ejemplos Válidos

```bash
# ✅ CORRECTO
payment.transaction.created
payment.transaction.completed
payment.transaction.failed

customer.account.created
customer.account.updated
customer.profile.updated

inventory.product.stockchanged
inventory.warehouse.allocated

notification.email.sent
notification.sms.failed

audit.login.succeeded
audit.login.failed

# ❌ INCORRECTO
PaymentCreated              # Camel case
payment-transaction-created # Hyphens
payment_transaction_created # Underscores
payments.v1.created         # Versión en nombre
```

### Dead Letter Queue (DLQ)

```bash
{original-topic}.dlq

Ejemplos:
payment.transaction.created.dlq
customer.account.updated.dlq
```

---

## 6. Kafka - Crear Topics

### Script de Creación

```bash
#!/bin/bash
# scripts/create-kafka-topics.sh

KAFKA_BOOTSTRAP="localhost:9092"

# Payment domain topics
kafka-topics.sh --bootstrap-server $KAFKA_BOOTSTRAP --create \
  --topic payment.transaction.created \
  --partitions 12 \
  --replication-factor 3 \
  --config retention.ms=604800000 \
  --config min.insync.replicas=2 \
  --config cleanup.policy=delete

kafka-topics.sh --bootstrap-server $KAFKA_BOOTSTRAP --create \
  --topic payment.transaction.completed \
  --partitions 12 \
  --replication-factor 3 \
  --config retention.ms=604800000 \
  --config min.insync.replicas=2

kafka-topics.sh --bootstrap-server $KAFKA_BOOTSTRAP --create \
  --topic payment.transaction.failed \
  --partitions 12 \
  --replication-factor 3 \
  --config retention.ms=604800000 \
  --config min.insync.replicas=2

# DLQ
kafka-topics.sh --bootstrap-server $KAFKA_BOOTSTRAP --create \
  --topic payment.transaction.created.dlq \
  --partitions 3 \
  --replication-factor 3 \
  --config retention.ms=2592000000  # 30 días para investigación

# Customer domain topics
kafka-topics.sh --bootstrap-server $KAFKA_BOOTSTRAP --create \
  --topic customer.account.created \
  --partitions 6 \
  --replication-factor 3 \
  --config retention.ms=604800000

kafka-topics.sh --bootstrap-server $KAFKA_BOOTSTRAP --create \
  --topic customer.account.updated \
  --partitions 6 \
  --replication-factor 3 \
  --config retention.ms=604800000
```

### Terraform (Infraestructura como Código)

```hcl
# terraform/kafka-topics.tf

# Nota: Kafka NO tiene provider oficial de Terraform
# Usar mongey/kafka o script de inicialización

resource "kafka_topic" "payment_transaction_created" {
  name               = "payment.transaction.created"
  replication_factor = 3
  partitions         = 12

  config = {
    "retention.ms"          = "604800000"  # 7 días
    "min.insync.replicas"   = "2"
    "cleanup.policy"        = "delete"
    "compression.type"      = "snappy"
  }
}

resource "kafka_topic" "payment_transaction_created_dlq" {
  name               = "payment.transaction.created.dlq"
  replication_factor = 3
  partitions         = 3

  config = {
    "retention.ms"        = "2592000000"  # 30 días
    "min.insync.replicas" = "2"
  }
}
```

---

## 7. Partitioning Strategy

### Por Tenant ID (Multi-Tenancy)

```csharp
// Uso: Todos los eventos del mismo tenant van a misma partición
// Garantiza ordenamiento de eventos por tenant

var message = new Message<string, string>
{
    Key = tenantId,  // "PE", "CO", "MX", "CL"
    Value = JsonSerializer.Serialize(paymentEvent)
};

await _producer.ProduceAsync("payment.transaction.created", message);
```

### Por Entity ID

```csharp
// Uso: Todos los eventos de misma entidad van a misma partición
// Garantiza ordenamiento de eventos por customer

var message = new Message<string, string>
{
    Key = customerId.ToString(),  // UUID del customer
    Value = JsonSerializer.Serialize(customerEvent)
};

await _producer.ProduceAsync("customer.account.updated", message);
```

### Cálculo de Particiones

```text
Partición = hash(key) % num_partitions

Ejemplo con 12 particiones:
- tenant_id="PE" → hash → partition 3
- tenant_id="CO" → hash → partition 7
- tenant_id="MX" → hash → partition 11
- tenant_id="CL" → hash → partition 2

Todos los eventos de "PE" siempre van a partition 3 (ordenamiento garantizado)
```

---

## 8. Retention Policies

### Retention por Tipo de Evento

| Tipo de Evento         | Retention | Razón                       |
| ---------------------- | --------- | --------------------------- |
| **Transaccional**      | 7 días    | Buffer para reprocesamiento |
| **Auditoría**          | 30 días   | Investigación de incidentes |
| **Estado (compacted)** | Infinito  | Snapshot de estado actual   |
| **DLQ**                | 30 días   | Análisis de fallos          |
| **Notificaciones**     | 3 días    | Fire-and-forget             |

### Configurar Retention

```bash
# Cambiar retention de topic existente
kafka-configs.sh --bootstrap-server localhost:9092 \
  --entity-type topics \
  --entity-name payment.transaction.created \
  --alter \
  --add-config retention.ms=604800000  # 7 días

# Log compaction (para state topics)
kafka-configs.sh --bootstrap-server localhost:9092 \
  --entity-type topics \
  --entity-name customer.account.snapshot \
  --alter \
  --add-config cleanup.policy=compact
```

---

## 9. Consumer Groups

### Naming Convention

```text
{service-name}-{consumer-purpose}

Ejemplos:
payment-service-processor
notification-service-email-sender
audit-service-logger
inventory-service-stock-updater
```

### Configuración

```csharp
var consumerConfig = new ConsumerConfig
{
    BootstrapServers = "localhost:9092",
    GroupId = "payment-service-processor",

    // Configuración importante
    AutoOffsetReset = AutoOffsetReset.Earliest,  // Leer desde inicio si no hay offset
    EnableAutoCommit = false,                     // Manual commit
    MaxPollIntervalMs = 300000,                   // 5 min max processing time
    SessionTimeoutMs = 45000,                     // 45s session timeout
};
```

---

## 10. Topic Organization

### Estructura Recomendada

```text
Dominio: Payment
├── payment.transaction.created      (12 partitions, 7d retention)
├── payment.transaction.completed    (12 partitions, 7d retention)
├── payment.transaction.failed       (12 partitions, 7d retention)
├── payment.transaction.created.dlq  (3 partitions, 30d retention)
└── payment.transaction.snapshot     (6 partitions, compacted)

Dominio: Customer
├── customer.account.created         (6 partitions, 7d retention)
├── customer.account.updated         (6 partitions, 7d retention)
├── customer.account.deleted         (6 partitions, 7d retention)
└── customer.account.snapshot        (3 partitions, compacted)

Dominio: Audit
├── audit.login.succeeded            (6 partitions, 30d retention)
├── audit.login.failed               (6 partitions, 30d retention)
└── audit.dataaccess.logged          (6 partitions, 30d retention)
```

---

## 11. Validación de Cumplimiento

```bash
# Listar todos los topics
kafka-topics.sh --bootstrap-server localhost:9092 --list

# Describir configuración de topic
kafka-topics.sh --bootstrap-server localhost:9092 \
  --describe --topic payment.transaction.created

# Verificar naming convention (debe tener 3 partes separadas por .)
kafka-topics.sh --bootstrap-server localhost:9092 --list | \
  awk -F'.' '{if(NF!=3) print "Invalid: " $0}'

# Verificar replication factor >= 3
kafka-topics.sh --bootstrap-server localhost:9092 --describe | \
  grep "ReplicationFactor" | grep -v "ReplicationFactor:3"
# Esperado: Sin resultados (todos tienen RF=3)

# Listar consumer groups
kafka-consumer-groups.sh --bootstrap-server localhost:9092 --list

# Describir consumer group (ver lag)
kafka-consumer-groups.sh --bootstrap-server localhost:9092 \
  --describe --group payment-service-processor
```

---

## 12. Referencias

**Kafka:**

- [Kafka Topic Configuration](https://kafka.apache.org/documentation/#topicconfigs)
- [Partitioning Strategy](https://kafka.apache.org/documentation/#intro_topics)
- [Log Compaction](https://kafka.apache.org/documentation/#compaction)

**Patterns:**

- [Event-Driven Architecture Patterns](https://martinfowler.com/articles/201701-event-driven.html)
