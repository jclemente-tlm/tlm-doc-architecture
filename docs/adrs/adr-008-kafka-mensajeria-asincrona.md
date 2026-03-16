---
title: "ADR-008: Kafka Mensajería Asíncrona"
sidebar_position: 8
---

## ✅ ESTADO

Aceptada – Agosto 2025

---

## 🗺️ CONTEXTO

Los servicios corporativos requieren una solución de mensajería asíncrona que permita:

- **Comunicación desacoplada y resiliente** entre microservicios
- **Portabilidad multi-cloud** para evitar lock-in
- **Soporte de event sourcing y patrones dirigidos por eventos**
- **Escalabilidad masiva para cargas variables**
- **Garantías de entrega y durabilidad**
- **Integración nativa con .NET**
- **Observabilidad y monitoreo centralizado**
- **Capacidad de streaming y procesamiento de eventos históricos**

Alternativas evaluadas:

- **Apache Kafka** (Open source, alta escalabilidad, agnóstico, streaming)
- **Google Cloud Pub/Sub** (Gestionado GCP, serverless, global)
- **AWS SNS + SQS** (Gestionado AWS, integración nativa, lock-in)
- **RabbitMQ** (Open source, flexible, escalabilidad limitada)
- **Azure Service Bus** (Gestionado Azure, lock-in)

---

## 🔍 COMPARATIVA DE ALTERNATIVAS

| Criterio                       | Apache Kafka                                        | Google Cloud Pub/Sub                            | AWS SNS+SQS                                   | RabbitMQ                                    | Azure Service Bus                             |
| ------------------------------ | --------------------------------------------------- | ----------------------------------------------- | --------------------------------------------- | ------------------------------------------- | --------------------------------------------- |
| **Agnosticidad**               | ✅ OSS, multi-cloud                                 | ❌ Lock-in GCP                                  | ❌ Lock-in AWS                                | ✅ OSS, multi-cloud                         | ❌ Lock-in Azure                              |
| **Madurez**                    | ✅ Muy alta (2011, streaming std)                   | ✅ Alta (2016, GCP serverless)                  | ✅ Muy alta (SNS 2010 + SQS 2006)             | ✅ Muy alta (2007, AMQP std)                | ✅ Alta (2012, Azure enterprise)              |
| **Adopción**                   | ✅ Muy alta (líder streaming, comunidad masiva)     | ✅ Alta (GCP native adoption)                   | ✅ Muy alta (AWS standard)                    | ✅ Muy alta (líder AMQP, comunidad activa)  | ✅ Alta (Azure ecosystem)                     |
| **Modelo de gestión**          | ⚠️ Self-hosted                                      | ✅ Gestionado (GCP)                             | ✅ Gestionado (AWS)                           | ⚠️ Self-hosted                              | ✅ Gestionado (Azure)                         |
| **Complejidad operativa**      | ⚠️ Alta (1 FTE, 10-20h/sem)                         | ✅ Baja (0.25 FTE, `<5h/sem)`                   | ✅ Baja (0.25 FTE, `<5h/sem)`                 | ⚠️ Alta (1 FTE, 10-20h/sem)                 | ⚠️ Media (0.5 FTE, 5-10h/sem)                 |
| **Integración .NET**           | ✅ `Confluent.Kafka` (.NET 6+, async)                 | ✅ `Google.Cloud.PubSub` (.NET 6+)                | ✅ `AWSSDK.SQS` + `SNS` (.NET 6+)                 | ✅ `RabbitMQ.Client` (.NET 6+)                 | ✅ `Azure.Messaging.ServiceBus` (.NET 6+)       |
| **Multi-tenancy**              | ⚠️ Por topics                                       | ✅ Por proyectos                                | ⚠️ Por topics                                 | ⚠️ Por vhosts                               | ⚠️ Por namespaces                             |
| **Latencia**                   | ✅ p99 `<10ms `                                     | ✅ `<50ms `delivery                             | ✅ `<100ms `delivery                          | ⚠️ `<100ms `variable                        | ✅ `<50ms `delivery                           |
| **Rendimiento**                | ✅ 100K+ msg/seg                                    | ✅ 100K+ msg/seg                                | ✅ 100K+ msg/seg                              | ⚠️ 10-20K msg/seg                           | ✅ 100K+ msg/seg                              |
| **Escalabilidad**              | ✅ Hasta trillones msg/día, 1M+ msg/seg (LinkedIn)  | ✅ Hasta 500K+ msg/seg máx (Google serverless)  | ✅ Hasta 300K+ msg/seg máx (AWS SNS/SQS)      | ⚠️ `<50K `msg/seg máx (límite arquitectura) | ✅ Hasta 100K+ msg/seg máx (Azure)            |
| **Alta disponibilidad**        | ✅ 99.95% estimado (replicación multi-broker)       | ✅ 99.95% SLA Multi-region                      | ✅ 99.9% SLA Multi-AZ                         | ⚠️ 99.5% estimado (clustering manual)       | ✅ 99.9% SLA Geo-replicación                  |
| **Persistencia**               | ✅ Log distribuido                                  | ✅ 7+ días default                              | ✅ Persistente                                | ✅ Durable queues                           | ✅ Persistencia nativa                        |
| **Streaming**                  | ✅ Nativo (replay)                                  | ⚠️ Dataflow requerido                           | ❌ No soportado                               | ❌ No soportado                             | ❌ Limitado                                   |
| **Event Sourcing**             | ✅ Ideal (log inmutable)                            | ⚠️ Parcial                                      | ⚠️ Parcial                                    | ❌ No recomendado                           | ⚠️ Parcial                                    |
| **Schema Registry**            | ✅ Confluent Schema Registry (Avro, JSON, Protobuf) | ⚠️ Manual (no nativo)                           | ⚠️ Manual implementation                      | ❌ No soportado                             | ⚠️ Custom schema validation                   |
| **Procesamiento de streams**   | ✅ Kafka Streams nativo                             | ✅ Dataflow integration                         | ⚠️ Kinesis Analytics (limitado)               | ❌ No nativo                                | ⚠️ External Stream Analytics                  |
| **Ecosistema de conectores**   | ✅ 200+ Kafka Connect connectors                    | ⚠️ Manual Pub/Sub connectors                    | ⚠️ AWS EventBridge (limitado)                 | ⚠️ Custom plugins                           | ✅ 100+ Azure connectors                      |
| **Exactly-Once Semantics**     | ✅ Idempotent producers + transactions              | ⚠️ At-least-once default                        | ⚠️ At-least-once (SQS FIFO exactly-once)      | ⚠️ At-least-once                            | ⚠️ At-least-once default                      |
| **Rebalanceo de consumidores** | ✅ Incremental cooperative rebalancing              | ⚠️ No consumer groups (push model)              | ⚠️ SQS FIFO limited                           | ⚠️ Manual consumer group management         | ⚠️ Basic consumer groups                      |
| **Costos**                     | ⚠️ $0 licencia + ~$300-800/mes infra                | ❌ $40/TB ingress + $120/TB egress (~$500+/mes) | ✅ $0.50/millón msg + $0.09/GB (~$50-150/mes) | ✅ $0 licencia + ~$150-300/mes infra        | ⚠️ $0.05/millón ops + storage (~$100-300/mes) |

**Leyenda:** ✅ Cumple completamente | ⚠️ Cumple parcialmente | ❌ No cumple

---

## ✔️ DECISIÓN

Se selecciona **Apache Kafka** como solución estándar de mensajería asíncrona y event streaming para todos los servicios corporativos.

### Justificación

- **Portabilidad multi-cloud:** OSS estándar de la industria, portable entre clouds
- **Escalabilidad masiva:** soporte de millones de mensajes por segundo
- **Event sourcing nativo:** log distribuido inmutable ideal para auditoría y replay
- **Streaming completo:** replay de eventos, windowing, procesamiento temporal
- **Ecosistema maduro:** tooling extenso, integración .NET (Confluent.Kafka), monitoreo
- **Flexibilidad deployment:** self-hosted, Confluent Cloud, AWS MSK, Azure HDInsight, etc.

### Alternativas descartadas

- **Google Cloud Pub/Sub:** lock-in GCP, sin infraestructura GCP existente, costos por mensaje elevados (US$40/TB ingress + US$120/TB egress), no soporta replay nativo, requiere Dataflow para streaming, at-least-once default
- **AWS SNS+SQS:** lock-in AWS, no soporta replay de eventos ni event sourcing robusto, no diseñado para streaming, limitado a patrones pub/sub y queue básicos
- **RabbitMQ:** escalabilidad limitada (< 50K msg/seg), no diseñado para streaming de eventos ni event sourcing, modelo broker tradicional vs log distribuido
- **Azure Service Bus:** lock-in Azure, infraestructura AWS ya establecida, menor portabilidad, no soporta streaming nativo

---

## ⚠️ CONSECUENCIAS

### Positivas

- Log distribuido inmutable ideal para event sourcing y auditoría
- Replay de eventos para reconstrucción de estado
- Escalabilidad masiva y alto throughput (millones msg/seg)
- Portabilidad multi-cloud (OSS estándar)
- Integración nativa .NET con Confluent.Kafka SDK

### Negativas (Riesgos y Mitigaciones)

- **Complejidad operativa:** mitigado con automatización Terraform, monitoreo proactivo y expertise DevOps
- **Curva de aprendizaje:** mitigado con capacitación y documentación corporativa
- **Costos infraestructura:** mitigado con políticas retención y dimensionamiento adecuado
- **Atomicidad con BD:** mitigado con patrón Transactional Outbox (ver guías de arquitectura)

---

## 📚 REFERENCIAS

- [Apache Kafka](https://kafka.apache.org/)
- [Confluent.Kafka .NET Client](https://docs.confluent.io/kafka-clients/dotnet/current/overview.html)
- [Event Sourcing with Kafka](https://www.confluent.io/blog/event-sourcing-cqrs-stream-processing-apache-kafka-whats-connection/)
- [Kafka Documentation](https://kafka.apache.org/documentation/)
