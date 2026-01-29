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
- **AWS SNS + SQS** (gestionado, integración nativa AWS, lock-in)
- **RabbitMQ** (open source, flexible, limitada escalabilidad)
- **Azure Service Bus** (gestionado, lock-in Azure)

## 🔍 COMPARATIVA DE ALTERNATIVAS

### Comparativa Cualitativa

| Criterio              | Kafka (MSK) | SNS+SQS | RabbitMQ | Azure SB |
|----------------------|-------------|---------|----------|----------|
| **Agnosticidad**     | ✅ OSS, multi-cloud | ❌ Lock-in AWS | ✅ OSS, multi-cloud | ❌ Lock-in Azure |
| **Escalabilidad**    | ✅ Masiva | ✅ Automática | 🟡 Limitada | ✅ Muy buena |
| **Operación**        | 🟡 Gestionada (MSK) | ✅ Gestionada | 🟡 Compleja | ✅ Gestionada |
| **Rendimiento**      | ✅ Máximo | ✅ Muy alto | 🟡 Moderado | ✅ Muy alto |
| **Ecosistema .NET**  | ✅ Confluent.Kafka | ✅ AWS SDK | ✅ RabbitMQ.Client | ✅ Azure SDK |
| **Persistencia**     | ✅ Log distribuido inmutable | ✅ Persistente | ✅ Durable queues | ✅ Persistencia nativa |
| **Streaming**        | ✅ Nativo (replay, windowing) | ❌ No soportado | ❌ No soportado | ❌ Limitado |
| **Event Sourcing**   | ✅ Ideal (log inmutable) | 🟡 Parcial | ❌ No recomendado | 🟡 Parcial |
| **Costos**           | 🟡 Infraestructura managed | ✅ Pago por uso bajo | ✅ OSS | 🟡 Pago por uso |

### Matriz de Decisión

| Solución            | Agnosticidad | Escalabilidad | Streaming | Event Sourcing | Recomendación         |
|--------------------|--------------|--------------|-----------|----------------|-----------------------|
| **Apache Kafka (MSK)** | Excelente    | Excelente    | Excelente | Excelente      | ✅ **Seleccionada**    |
| **AWS SNS + SQS**  | Mala         | Excelente    | No        | Parcial        | ❌ Descartada          |
| **RabbitMQ**       | Excelente    | Limitada     | No        | No recomendado | ❌ Descartada          |
| **Azure SB**       | Mala         | Muy buena    | Limitado  | Parcial        | ❌ Descartada          |

## 💰 ANÁLISIS DE COSTOS (TCO 3 años)

> **Metodología y supuestos:** Se asume AWS MSK con 3 brokers t3.small, 5 topics, 1M mensajes/mes, retención 7 días. TCO incluye infraestructura managed y transferencia de datos.

| Solución         | Licenciamiento | Infraestructura | Operación      | TCO 3 años   |
|------------------|---------------|----------------|---------------|--------------|
| Kafka (AWS MSK)  | Incluido      | US$18,000      | US$0          | US$18,000    |
| SNS+SQS          | Pago por uso  | US$0           | US$0          | US$1,080     |
| RabbitMQ         | OSS           | US$1,800/año   | US$24,000/año | US$77,400    |
| Azure SB         | Pago por uso  | US$0           | US$0          | US$1,440     |

---

## Consideraciones técnicas y riesgos

### Límites clave

- **Kafka (MSK):** Retención configurable (7-90 días), throughput según tamaño de cluster
- **SNS+SQS:** Retención máxima 14 días, no soporta replay de eventos
- **RabbitMQ:** Escalabilidad limitada, requiere clustering manual complejo
- **Azure SB:** Lock-in Azure, límites por suscripción

### Riesgos y mitigación

- **Complejidad operativa Kafka:** mitigada con AWS MSK managed, monitoreo con Prometheus
- **Costos infraestructura:** optimizado con autoescalado y políticas de retención
- **Curva de aprendizaje:** mitigada con Confluent.Kafka SDK y capacitación del equipo

---

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

- **AWS SNS+SQS:** lock-in AWS, no soporta replay de eventos ni event sourcing robusto
- **RabbitMQ:** escalabilidad limitada, no diseñado para streaming de eventos
- **Azure Service Bus:** lock-in Azure, menor portabilidad

---

## ⚠️ CONSECUENCIAS

- Todos los servicios nuevos deben usar Kafka (AWS MSK) para mensajería asíncrona
- Se debe usar Confluent.Kafka SDK para integración con .NET
- Topics deben seguir naming convention: `{domain}.{entity}.{event}` (ej: `orders.order.created`)
- Dead Letter Topics (DLT) obligatorios para manejo de errores: `{topic-name}.dlt`
- Retención de topics: 7 días default, configurable según requisitos de auditoría
- Particionamiento por tenant (país) para aislamiento multi-tenant

---

## 🏗️ ARQUITECTURA DE DESPLIEGUE

- AWS MSK cluster: 3 brokers mínimo, multi-AZ
- Topics por dominio de eventos: `orders`, `notifications`, `payments`, etc.
- Particionamiento por clave de tenant (país)
- Replicación: factor 3 para alta disponibilidad
- Integración con Confluent.Kafka SDK y librerías .NET
- Monitoreo con Prometheus + Grafana + AWS CloudWatch

---

## 📊 MÉTRICAS Y MONITOREO

### KPIs Clave

- **Mensajes procesados**: > 99.99% entregados
- **Latencia promedio**: < 50ms
- **Throughput**: > 100K mensajes/minuto
- **Consumer lag**: < 1000 mensajes
- **Disponibilidad brokers**: > 99.9%

### Alertas Críticas

- Consumer lag > 10,000 mensajes
- Latencia > 200ms
- Errores de producción > 1%
- Broker offline
- Disco > 80% en brokers

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
