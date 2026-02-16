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

- **Apache Kafka** (open source, alta escalabilidad, agnóstico, streaming)
- **Google Cloud Pub/Sub** (gestionado GCP, serverless, global)
- **AWS SNS + SQS** (gestionado, integración nativa AWS, lock-in)
- **RabbitMQ** (open source, flexible, limitada escalabilidad)
- **Azure Service Bus** (gestionado, lock-in Azure)

## 🔍 COMPARATIVA DE ALTERNATIVAS

| Criterio                  | Apache Kafka              | Google Cloud Pub/Sub    | AWS SNS+SQS          | RabbitMQ            | Azure Service Bus       |
| ------------------------- | ------------------------- | ----------------------- | -------------------- | ------------------- | ----------------------- |
| **Agnosticidad**          | ✅ OSS, multi-cloud       | ❌ Lock-in GCP          | ❌ Lock-in AWS       | ✅ OSS, multi-cloud | ❌ Lock-in Azure        |
| **Modelo de gestión**     | ⚠️ Self-hosted            | ✅ Gestionado (GCP)     | ✅ Gestionado (AWS)  | ⚠️ Self-hosted      | ✅ Gestionado (Azure)   |
| **Complejidad operativa** | ⚠️ Media (automatización) | ❌ Alta (vendor GCP)    | ✅ Baja (infra AWS)  | ⚠️ Media (setup)    | ⚠️ Media (vendor nuevo) |
| **Escalabilidad**         | ✅ Masiva                 | ✅ Serverless ilimitada | ✅ Automática        | ⚠️ Limitada         | ✅ Muy buena            |
| **Performance**           | ✅ 1M+ msg/seg, <10ms p99 | ✅ 100K+ msg/seg        | ✅ 100K+ msg/seg     | ⚠️ 50K msg/seg      | ✅ 100K+ msg/seg        |
| **Integración .NET**      | ✅ Confluent.Kafka        | ✅ Google.Cloud.PubSub  | ✅ AWS SDK           | ✅ RabbitMQ.Client  | ✅ Azure SDK            |
| **Persistencia**          | ✅ Log distribuido        | ✅ 7+ días default      | ✅ Persistente       | ✅ Durable queues   | ✅ Persistencia nativa  |
| **Streaming**             | ✅ Nativo (replay)        | ⚠️ Dataflow requerido   | ❌ No soportado      | ❌ No soportado     | ❌ Limitado             |
| **Event Sourcing**        | ✅ Ideal (log inmutable)  | ⚠️ Parcial              | ⚠️ Parcial           | ❌ No recomendado   | ⚠️ Parcial              |
| **Multi-tenancy**         | ⚠️ Por topics             | ✅ Por proyectos        | ⚠️ Por topics        | ⚠️ Por vhosts       | ⚠️ Por namespaces       |
| **Alta disponibilidad**   | ✅ Replicación, Multi-AZ  | ✅ Multi-region         | ✅ Multi-AZ          | ⚠️ Clustering       | ✅ Geo-replicación      |
| **Costos**                | ⚠️ Infraestructura        | ⚠️ Pago por mensaje     | ✅ Pago por uso bajo | ✅ OSS              | ⚠️ Pago por uso         |

**Leyenda:** ✅ Cumple completamente | ⚠️ Cumple parcialmente | ❌ No cumple

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

- **Google Cloud Pub/Sub:** lock-in GCP, **vendor adicional sin infraestructura GCP existente** (requiere cuenta/proyecto/billing activo), **SDK .NET adicional** (Google.Cloud.PubSub) a mantener, **complejidad multi-vendor** (AWS + Azure + GCP) sin beneficio diferencial, **overhead operativo** (tercera consola cloud, tercera facturación, tercer soporte), costos por mensaje (US$40/TB vs US$0.10/GB Kafka), no soporta replay nativo, requiere Dataflow para streaming
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

- **Complejidad operativa:** mitigada con automatización Terraform, monitoreo proactivo, y expertise DevOps
- **Curva de aprendizaje:** mitigada con capacitación y documentación corporativa
- **Costos infraestructura:** optimizados con políticas retención y dimensionamiento adecuado
- **Atomicidad con BD:** para garantizar consistencia con PostgreSQL (ADR-010), usar patrones como Transactional Outbox (ver guías de arquitectura)

---

## 📚 REFERENCIAS

- [Apache Kafka](https://kafka.apache.org/)
- [Confluent.Kafka .NET Client](https://docs.confluent.io/kafka-clients/dotnet/current/overview.html)
- [Event Sourcing with Kafka](https://www.confluent.io/blog/event-sourcing-cqrs-stream-processing-apache-kafka-whats-connection/)
- [Kafka Documentation](https://kafka.apache.org/documentation/)

---

**Decisión tomada por:** Equipo de Arquitectura
**Fecha:** Agosto 2025
**Próxima revisión:** Agosto 2026
