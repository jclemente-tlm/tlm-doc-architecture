---
id: adr-015-manejo-errores-en-cola
title: "Manejo de Errores en Cola"
sidebar_position: 15
---

## ✅ ESTADO

Aceptada – Agosto 2025

---

## 🗺️ CONTEXTO

Los servicios corporativos distribuidos requieren una estrategia robusta para el manejo de errores en colas de mensajería asíncrona, considerando:

- **Mensajes fallidos** tras múltiples reintentos
- **Poison messages** que generan errores recurrentes
- **Recuperación y reprocesamiento** manual o automatizado
- **Auditoría y trazabilidad** de fallos
- **Aislamiento de errores** para evitar bloqueos
- **Alertas proactivas** ante patrones de fallo
- **Retención configurable** según criticidad
- **Compatibilidad multi-tenant** y multipaís

La estrategia prioriza **resiliencia, observabilidad y simplicidad operativa** usando tecnologías y patrones aprobados.

Alternativas evaluadas:

- **Dead Letter Queue (DLQ)** con AWS SQS, Azure Service Bus, RabbitMQ
- **Reintentos exponenciales** sin DLQ
- **Circuit Breaker** complementario
- **Manual retry** con almacenamiento persistente
- **Event Store** con replay
- **Enfoque híbrido** (DLQ + Circuit Breaker)

## 🔍 COMPARATIVA DE ALTERNATIVAS

### Comparativa Cualitativa

| Criterio                | DLQ                      | Reintentos         | Circuit Breaker      | Manual Retry        | Event Store         | Híbrido (DLQ+CB)    |
|------------------------|--------------------------|--------------------|---------------------|---------------------|---------------------|---------------------|
| **Resiliencia**        | ✅ Completa              | 🟡 Limitada        | 🟡 Temporal          | 🟡 Parcial          | ✅ Completa         | ✅ Máxima           |
| **Observabilidad**     | ✅ Alta                  | ❌ Muy limitada    | 🟡 Básica            | 🟡 Manual           | ✅ Completa         | ✅ Total            |
| **Operación**          | ✅ Automatizada          | ✅ Simple          | 🟡 Config. compleja  | ❌ Manual           | 🟡 Compleja         | 🟡 Moderada         |
| **Agnosticidad**       | 🟡 Depende del broker    | ✅ Total           | ✅ Universal         | ✅ Total            | ✅ Total            | 🟡 Parcial          |
| **Prevención pérdida** | ✅ Cero pérdida          | ❌ Alta probabilidad| 🟡 Parcial           | ✅ Persistencia     | ✅ Cero pérdida     | ✅ Cero pérdida     |
| **Automatización**     | ✅ Total                 | ✅ Total           | ✅ Total             | ❌ Manual           | 🟡 Parcial          | ✅ Total            |
| **Costos**             | ✅ Moderados             | ✅ Bajos           | ✅ Moderados         | ✅ Bajos            | 🟡 Altos            | 🟡 Moderados-altos  |

### Matriz de Decisión

| Solución                  | Resiliencia | Observabilidad | Operación | Prevención Pérdida | Recomendación         |
|--------------------------|-------------|----------------|-----------|--------------------|-----------------------|
| **Híbrido (DLQ + CB)**   | Excelente   | Excelente      | Moderada  | Excelente          | ✅ **Seleccionada**    |
| **Dead Letter Queue**    | Excelente   | Excelente      | Automática| Excelente          | 🟡 Alternativa         |
| **Event Store**          | Excelente   | Excelente      | Compleja  | Excelente          | 🟡 Considerada         |
| **Circuit Breaker**      | Moderada    | Básica         | Compleja  | Moderada           | 🟡 Complementaria      |
| **Manual Retry**         | Moderada    | Limitada       | Manual    | Buena              | ❌ Descartada          |
| **Reintentos sin DLQ**   | Básica      | Muy limitada   | Simple    | Mala               | ❌ Descartada          |

---

## 💰 ANÁLISIS DE COSTOS (TCO 3 años)

> **Supuesto:** Uso de AWS SQS con DLQ, 5 colas principales, 4 países, 1 millón de mensajes/mes por cola. Costos estimados para almacenamiento, transferencias y monitoreo.

| Solución         | Licenciamiento | Infraestructura | Operación      | TCO 3 años   |
|------------------|---------------|----------------|---------------|--------------|
| AWS SQS + DLQ    | Pago por uso  | US$0           | US$0          | US$7,200     |
| Azure Service Bus| Pago por uso  | US$0           | US$0          | US$8,400     |
| RabbitMQ         | OSS           | US$4,800       | US$12,000     | US$50,400    |

---

## Consideraciones técnicas y riesgos

### Límites clave

- **AWS SQS/Azure Service Bus:** límites por tamaño de mensaje, retención y throughput
- **RabbitMQ:** depende de infraestructura propia, requiere operación

### Riesgos y mitigación

- **Lock-in cloud:** mitigado con interfaces desacopladas
- **Complejidad operativa RabbitMQ:** mitigada con automatización y monitoreo
- **Pérdida de mensajes:** mitigada con DLQ y alertas

---

## ✔️ DECISIÓN

Se selecciona un **enfoque híbrido**: uso de `Dead Letter Queues (DLQ)` en las colas de mensajería (AWS SQS, Azure Service Bus) complementado con `Circuit Breaker` para máxima resiliencia y observabilidad.

## Justificación

- Aislamiento y análisis de mensajes fallidos
- Recuperación y reprocesamiento flexible
- Observabilidad y auditoría completas
- Integración nativa con ecosistema .NET y herramientas de monitoreo
- Reducción de riesgo de pérdida de información
- Cumplimiento de requisitos multi-tenant y multipaís

## Alternativas descartadas

- **Reintentos sin DLQ:** alto riesgo de pérdida y baja trazabilidad
- **Manual Retry:** operación manual y poca escalabilidad
- **RabbitMQ puro:** mayor complejidad operativa

---

## ⚠️ CONSECUENCIAS

- Todos los servicios deben implementar DLQ y monitoreo de errores en colas
- Se deben definir políticas de reprocesamiento y alertas automáticas
- El código debe desacoplarse del broker mediante interfaces

---

## 📚 REFERENCIAS

- [AWS SQS DLQ](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-dead-letter-queues.html)
- [Azure Service Bus DLQ](https://learn.microsoft.com/es-es/azure/service-bus-messaging/service-bus-dead-letter-queues)
- [arc42: Decisiones de arquitectura](https://arc42.org/decision/)
