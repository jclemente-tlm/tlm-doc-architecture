---
id: adr-012-mensajeria-asincrona
title: "Mensajería Asíncrona Empresarial"
sidebar_position: 12
---

## ✅ ESTADO

Aceptada – Agosto 2025

---

## 🗺️ CONTEXTO

Los servicios corporativos requieren una solución de mensajería asíncrona que permita:

- **Comunicación desacoplada y resiliente** entre microservicios
- **Despliegue multi-cloud y on-premises** para evitar lock-in
- **Soporte de event sourcing y patrones dirigidos por eventos**
- **Escalabilidad automática para cargas variables**
- **Garantías de entrega y durabilidad**
- **Integración nativa con .NET y ecosistema cloud**
- **Observabilidad y monitoreo centralizado**
- **Costos controlados y operación gestionada**

Alternativas evaluadas:

- **AWS SNS + SQS** (gestionado, integración nativa, escalabilidad, lock-in AWS)
- **Apache Kafka** (open source, alta escalabilidad, agnóstico)
- **RabbitMQ** (open source, flexible, fácil operación)
- **Azure Service Bus** (gestionado, lock-in Azure)
- **Google Pub/Sub** (gestionado, lock-in GCP)

## 🔍 COMPARATIVA DE ALTERNATIVAS

### Comparativa Cualitativa

| Criterio              | SNS+SQS | Kafka | RabbitMQ | Azure SB | Google PS |
|----------------------|---------|-------|----------|----------|-----------|
| **Agnosticidad**     | ❌ Lock-in AWS | ✅ OSS, multi-cloud | ✅ OSS, multi-cloud | ❌ Lock-in Azure | ❌ Lock-in GCP |
| **Escalabilidad**    | ✅ Automática | ✅ Masiva | 🟡 Limitada | ✅ Muy buena | ✅ Muy buena |
| **Operación**        | ✅ Gestionada | 🟡 Compleja | ✅ Simple | ✅ Gestionada | ✅ Gestionada |
| **Rendimiento**      | ✅ Muy alto | ✅ Máximo | 🟡 Moderado | ✅ Muy alto | ✅ Muy alto |
| **Ecosistema .NET**  | ✅ AWS SDK | ✅ Confluent.Kafka | ✅ RabbitMQ.Client | ✅ Azure SDK | 🟡 Google SDK |
| **Persistencia**     | ✅ SQS persistente | ✅ Log distribuido | ✅ Durable queues | ✅ Persistencia nativa | ✅ Persistencia nativa |
| **Patrones**         | ✅ Pub/sub + queues | ✅ Streaming + messaging | ✅ Messaging tradicional | ✅ Messaging completo | ✅ Pub/sub puro |
| **Costos**           | 🟡 Pago por uso | ✅ OSS | ✅ OSS | 🟡 Pago por uso | 🟡 Pago por uso |

### Matriz de Decisión

| Solución         | Agnosticidad | Escalabilidad | Operación | Rendimiento | Recomendación         |
|------------------|--------------|--------------|-----------|-------------|-----------------------|
| **AWS SNS + SQS**| Mala         | Excelente    | Excelente | Excelente   | ✅ **Seleccionada**    |
| **Apache Kafka** | Excelente    | Excelente    | Compleja  | Excelente   | 🟡 Alternativa         |
| **RabbitMQ**     | Excelente    | Limitada     | Simple    | Moderado    | 🟡 Considerada         |
| **Azure SB**     | Mala         | Muy buena    | Gestionada| Muy alto    | ❌ Descartada          |
| **Google PS**    | Mala         | Muy buena    | Gestionada| Muy alto    | ❌ Descartada          |

## 💰 ANÁLISIS DE COSTOS (TCO 3 años)

> **Metodología y supuestos:** Se asume un uso promedio de 1M mensajes/mes, 3 instancias, multi-región. El TCO (Total Cost of Ownership) se calcula para un horizonte de 3 años, incluyendo costos directos y estimaciones de operación. Los valores pueden variar según volumen y proveedor.

| Solución         | Licenciamiento | Infraestructura | Operación      | TCO 3 años   |
|------------------|---------------|----------------|---------------|--------------|
| SNS+SQS          | Pago por uso  | US$0           | US$0          | US$1,080/año |
| Kafka            | OSS           | US$2,160/año   | US$36,000/año | US$114,480   |
| RabbitMQ         | OSS           | US$1,800/año   | US$24,000/año | US$77,400    |
| Azure SB         | Pago por uso  | US$0           | US$0          | US$1,440/año |
| Google PS        | Pago por uso  | US$0           | US$0          | US$1,200/año |

---

## Consideraciones técnicas y riesgos

### Límites clave

- **SNS+SQS:** escalabilidad automática, sin límite práctico de colas o tópicos
- **Kafka:** requiere gestión de particiones, tuning y monitoreo
- **RabbitMQ:** escalabilidad limitada, requiere clustering manual
- **Azure SB/Google PS:** límites por suscripción y throughput

### Riesgos y mitigación

- **Lock-in AWS:** mitigado con interfaces y adaptadores desacoplados
- **Complejidad operativa Kafka/RabbitMQ:** mitigada con automatización y monitoreo
- **Costos variables cloud:** monitoreo y revisión anual

---

## ✔️ DECISIÓN

Se selecciona **AWS SNS + SQS** como solución estándar de mensajería asíncrona para todos los servicios y microservicios corporativos.

## Justificación

- Operación gestionada, sin infraestructura propia
- Escalabilidad automática y alta disponibilidad
- Integración nativa con AWS y .NET
- Costos bajos y pago por uso
- Garantías de entrega y durabilidad
- Observabilidad y monitoreo integrados

## Alternativas descartadas

- **Apache Kafka:** mayor complejidad operativa y costos
- **RabbitMQ:** escalabilidad limitada y operación manual
- **Azure Service Bus:** lock-in Azure, menor portabilidad
- **Google Pub/Sub:** lock-in GCP, menor portabilidad

---

## ⚠️ CONSECUENCIAS

- Todos los servicios nuevos deben usar SNS+SQS salvo justificación técnica documentada
- Se debe estandarizar la gestión de colas, tópicos y monitoreo
- El equipo debe mantener adaptadores desacoplados para facilitar migración futura

---

## 🏗️ ARQUITECTURA DE DESPLIEGUE

- SNS: tópicos por dominio de eventos
- SQS: colas por microservicio consumidor
- Integración con AWS SDK y librerías .NET
- Monitoreo con CloudWatch y Prometheus

---

## 📊 MÉTRICAS Y MONITOREO

### KPIs Clave

- **Mensajes procesados**: > 99.99% entregados
- **Latencia promedio**: < 100ms
- **Throughput**: > 10K mensajes/minuto
- **Errores de entrega**: < 0.01%

### Alertas Críticas

- Mensajes en cola > umbral
- Latencia > 500ms
- Fallos de entrega repetidos
- Errores de integración SDK

---

## 📚 REFERENCIAS

- [AWS SNS](https://aws.amazon.com/sns/)
- [AWS SQS](https://aws.amazon.com/sqs/)
- [Apache Kafka](https://kafka.apache.org/)
- [RabbitMQ](https://www.rabbitmq.com/)
- [Azure Service Bus](https://azure.microsoft.com/en-us/services/service-bus/)
- [Google Pub/Sub](https://cloud.google.com/pubsub/)

---

**Decisión tomada por:** Equipo de Arquitectura
**Fecha:** Agosto 2025
**Próxima revisión:** Agosto 2026
