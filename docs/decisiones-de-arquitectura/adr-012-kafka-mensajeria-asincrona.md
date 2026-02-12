---
title: "ADR-012: Kafka Mensajería Asíncrona"
sidebar_position: 12
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

- **Apache Kafka (AWS MSK)** (open source, alta escalabilidad, agnóstico, streaming)
- **Apache Pulsar** (open source, multi-tenancy nativo, competidor moderno de Kafka)
- **Google Cloud Pub/Sub** (gestionado GCP, serverless, global)
- **NATS** (open source, cloud-native, ligero, CNCF)
- **AWS SNS + SQS** (gestionado, integración nativa AWS, lock-in)
- **RabbitMQ** (open source, flexible, limitada escalabilidad)
- **Azure Service Bus** (gestionado, lock-in Azure)

## 🔍 COMPARATIVA DE ALTERNATIVAS

### Comparativa Cualitativa

| Criterio            | Kafka (MSK)                   | Apache Pulsar           | Google Pub/Sub           | NATS                    | SNS+SQS              | RabbitMQ            | Azure SB               |
| ------------------- | ----------------------------- | ----------------------- | ------------------------ | ----------------------- | -------------------- | ------------------- | ---------------------- |
| **Agnosticidad**    | ✅ OSS, multi-cloud           | ✅ OSS, multi-cloud     | ❌ Lock-in GCP           | ✅ OSS, multi-cloud     | ❌ Lock-in AWS       | ✅ OSS, multi-cloud | ❌ Lock-in Azure       |
| **Escalabilidad**   | ✅ Masiva                     | ✅ Masiva, auto-scaling | ✅ Serverless ilimitada  | ✅ Muy alta             | ✅ Automática        | ⚠️ Limitada         | ✅ Muy buena           |
| **Operación**       | ⚠️ Gestionada (MSK)           | ⚠️ Compleja operación   | ✅ Totalmente gestionado | ⚠️ Self-hosted          | ✅ Gestionada        | ⚠️ Compleja         | ✅ Gestionada          |
| **Rendimiento**     | ✅ Máximo                     | ✅ Muy alto             | ✅ Muy alto              | ✅ Sub-ms latencia      | ✅ Muy alto          | ⚠️ Moderado         | ✅ Muy alto            |
| **Ecosistema .NET** | ✅ Confluent.Kafka            | ✅ Apache.Pulsar.Client | ✅ Google.Cloud.PubSub   | ✅ NATS.Client          | ✅ AWS SDK           | ✅ RabbitMQ.Client  | ✅ Azure SDK           |
| **Persistencia**    | ✅ Log distribuido inmutable  | ✅ Tiered storage       | ✅ 7+ días default       | ✅ JetStream            | ✅ Persistente       | ✅ Durable queues   | ✅ Persistencia nativa |
| **Streaming**       | ✅ Nativo (replay, windowing) | ✅ Functions, SQL       | ⚠️ Dataflow requerido    | ✅ JetStream            | ❌ No soportado      | ❌ No soportado     | ❌ Limitado            |
| **Event Sourcing**  | ✅ Ideal (log inmutable)      | ✅ Excellent            | ⚠️ Parcial               | ✅ JetStream            | ⚠️ Parcial           | ❌ No recomendado   | ⚠️ Parcial             |
| **Multi-tenancy**   | ⚠️ Por topics                 | ✅ Nativo (namespaces)  | ✅ Por proyectos         | ✅ Accounts/Users       | ⚠️ Por topics        | ⚠️ Por vhosts       | ⚠️ Por namespaces      |
| **Costos**          | ⚠️ Infraestructura managed    | ⚠️ Infraestructura      | ⚠️ Pago por mensaje      | ✅ Solo infraestructura | ✅ Pago por uso bajo | ✅ OSS              | ⚠️ Pago por uso        |

**Leyenda:** ✅ Cumple completamente | ⚠️ Cumple parcialmente | ❌ No cumple

## ✔️ DECISIÓN

Se selecciona **Apache Kafka (AWS MSK)** como solución estándar de mensajería asíncrona y event streaming para todos los servicios corporativos.

## Justificación

- Portabilidad multi-cloud (OSS estándar de la industria)
- Escalabilidad masiva y alto throughput
- Soporte nativo de event sourcing y streaming (replay, windowing)
- Log distribuido inmutable ideal para auditoría
- Integración nativa con .NET mediante Confluent.Kafka
- Operación gestionada con AWS MSK (sin administrar brokers)
- Flexibilidad para migrar entre clouds manteniendo mismo stack
- Ecosistema maduro con tooling de monitoreo y observabilidad

## Alternativas descartadas

- **Apache Pulsar:** alternativa moderna excelente pero menor adopción en industria vs Kafka, complejidad operativa similar, ecosistema .NET menos maduro, equipo aún familiarizándose con Kafka
- **Google Cloud Pub/Sub:** lock-in GCP, infraestructura AWS ya establecida, costos por mensaje (US$40/TB vs US$0.10/GB Kafka), no soporta replay nativo, requiere Dataflow para streaming
- **NATS:** excelente para mensajería ligera pero no diseñado para event sourcing y almacenamiento largo plazo, JetStream aún inmaduro comparado con Kafka, menor adopción enterprise
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

- **Complejidad operativa:** mitigada con AWS MSK managed y automatización Terraform
- **Curva de aprendizaje:** mitigada con capacitación y documentación corporativa
- **Costos infraestructura:** optimizados con políticas retención y dimensionamiento adecuado

---

## 📚 REFERENCIAS

- [Apache Kafka](https://kafka.apache.org/)
- [AWS MSK](https://aws.amazon.com/msk/)
- [Confluent.Kafka .NET Client](https://docs.confluent.io/kafka-clients/dotnet/current/overview.html)
- [Event Sourcing with Kafka](https://www.confluent.io/blog/event-sourcing-cqrs-stream-processing-apache-kafka-whats-connection/)
- [Dead Letter Queue Pattern](https://docs.confluent.io/platform/current/streams/developer-guide/dsl-api.html#dead-letter-queue)

---

**Decisión tomada por:** Equipo de Arquitectura
**Fecha:** Agosto 2025
**Próxima revisión:** Agosto 2026
