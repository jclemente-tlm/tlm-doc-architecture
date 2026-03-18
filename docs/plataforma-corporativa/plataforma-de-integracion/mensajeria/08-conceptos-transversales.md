---
sidebar_position: 8
title: Conceptos Transversales
description: Patrones y configuraciones aplicadas transversalmente en la plataforma de mensajería Kafka KRaft.
---

# 8. Conceptos Transversales

## KRaft: Consenso sin ZooKeeper

Kafka KRaft reemplaza ZooKeeper con un log de metadatos interno gestionado mediante el algoritmo Raft. El quórum de controllers elige un líder activo que gestiona todas las operaciones de metadatos (creación de topics, elección de líderes de partición, registro de brokers).

- El **metadata log** es un topic interno especial (`__cluster_metadata`) replicado en todos los controllers.
- Con 2 controllers, el quórum necesita los 2 nodos activos para aceptar cambios de metadatos. Para tolerar 1 fallo, escalar a 3 controllers (ver DT-01).
- Los brokers obtienen metadatos del controller activo mediante el protocolo `MetadataFetch`.

## Autenticación SASL/SCRAM

Todos los productores y consumidores deben autenticarse con SASL/SCRAM-SHA-512. Las credenciales se gestionan en el broker mediante el almacén interno de Kafka (`kafka-configs.sh`) y se inyectan en los servicios como secretos de AWS Secrets Manager.

| Aspecto             | Configuración                                 |
| ------------------- | --------------------------------------------- |
| Mecanismo           | `SASL_PLAINTEXT` dentro de VPC                |
| Algoritmo           | `SCRAM-SHA-512`                               |
| Gestión de usuarios | `kafka-configs.sh --alter --add-config SCRAM` |
| Secretos            | AWS Secrets Manager → variable de entorno     |
| ACLs                | Por prefijo de topic (`<dominio>.*`)          |

## Multi-tenancy por Convención de Nombrado

El clúster es único y compartido. El aislamiento lógico entre dominios y países se logra mediante la convención de naming de topics y ACLs por prefijo:

```
logistica.*          → solo servicios de logística (producer + consumer)
notificaciones.*     → solo servicio de notificaciones
cdc.*                → solo CDC Service (Debezium) como producer
```

Esta estrategia evita la complejidad operativa de múltiples clústeres mientras mantiene aislamiento de acceso configurable.

## Observabilidad

### Métricas → Mimir/Grafana (JMX Exporter)

Un contenedor `jmx-exporter` como sidecar en cada instancia EC2 expone las métricas JMX de Kafka en formato Prometheus. Prometheus las recolecta y las almacena en Mimir como backend a largo plazo.

Métricas clave monitoreadas:

| Métrica                                  | Descripción                                 |
| ---------------------------------------- | ------------------------------------------- |
| `kafka_server_brokertopicmetrics_*`      | Throughput de mensajes por topic y broker   |
| `kafka_controller_activecontrollercount` | Número de controllers activos (debe ser 1)  |
| `kafka_log_logendoffset`                 | Offset más reciente por partición           |
| `kafka_consumer_lag`                     | Lag de cada consumer group por partición    |
| `kafka_log_size`                         | Tamaño del log en disco por topic/partición |

### Logs → Loki

Cada contenedor Kafka emite logs por `stdout`. Un agente **Fluent Bit** instalado en cada instancia EC2 los recolecta y los envía a Loki. Labels indexados: `job=kafka`, `role` (`controller`/`broker`), `node_id`, `env`.

### Alertas Clave en Grafana

| Alerta                     | Condición                                          |
| -------------------------- | -------------------------------------------------- |
| Controller inactivo        | `activecontrollercount != 1` por más de 30s        |
| Consumer lag alto          | `kafka_consumer_lag > 10000` por más de 5 min      |
| Disco al 80%               | `kafka_log_size / ebs_size > 0.8`                  |
| Broker sin réplicas en ISR | `under_replicated_partitions > 0` por más de 2 min |

## Garantías de Entrega

| Configuración del Productor          | Garantía                                                                |
| ------------------------------------ | ----------------------------------------------------------------------- |
| `acks=0`                             | Fire-and-forget; sin garantía (no usar en producción)                   |
| `acks=1`                             | At-least-once; acepta pérdida si el broker cae post-ack                 |
| `acks=all` + `min.insync.replicas=2` | At-least-once con durabilidad máxima; recomendado para eventos críticos |

Para semántica **exactly-once** entre producer y consumer: usar Kafka Transactions (`enable.idempotence=true` + `transactional.id`). Requiere evaluación caso a caso.
