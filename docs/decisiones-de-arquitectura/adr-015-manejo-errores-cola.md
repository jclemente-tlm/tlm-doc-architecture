---
title: "ADR-015: Manejo de Errores en Mensajería"
sidebar_position: 15
---

## ✅ ESTADO

Aceptada – Agosto 2025

---

## 🗺️ CONTEXTO

Los servicios corporativos distribuidos requieren una estrategia robusta para el manejo de errores en mensajería asíncrona con Apache Kafka, considerando:

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

- **Dead Letter Topic (DLT)** en Kafka
- **Reintentos exponenciales** sin DLT
- **Circuit Breaker** complementario
- **Manual retry** con almacenamiento persistente
- **Event Store** con replay
- **Enfoque híbrido** (DLT + Circuit Breaker)

## 🔍 COMPARATIVA DE ALTERNATIVAS

### Comparativa Cualitativa

| Criterio                | DLT (Kafka)              | Reintentos         | Circuit Breaker      | Manual Retry        | Event Store         | Híbrido (DLT+CB)    |
|------------------------|--------------------------|--------------------|---------------------|---------------------|---------------------|---------------------|
| **Resiliencia**        | ✅ Completa              | 🟡 Limitada        | 🟡 Temporal          | 🟡 Parcial          | ✅ Completa         | ✅ Máxima           |
| **Observabilidad**     | ✅ Alta                  | ❌ Muy limitada    | 🟡 Básica            | 🟡 Manual           | ✅ Completa         | ✅ Total            |
| **Operación**          | ✅ Automatizada          | ✅ Simple          | 🟡 Config. compleja  | ❌ Manual           | 🟡 Compleja         | 🟡 Moderada         |
| **Agnosticidad**       | ✅ Kafka nativo          | ✅ Total           | ✅ Universal         | ✅ Total            | ✅ Total            | ✅ Alta             |
| **Prevención pérdida** | ✅ Cero pérdida          | ❌ Alta probabilidad| 🟡 Parcial           | ✅ Persistencia     | ✅ Cero pérdida     | ✅ Cero pérdida     |
| **Automatización**     | ✅ Total                 | ✅ Total           | ✅ Total             | ❌ Manual           | 🟡 Parcial          | ✅ Total            |
| **Costos**             | ✅ Incluido en Kafka     | ✅ Bajos           | ✅ Moderados         | ✅ Bajos            | 🟡 Altos            | ✅ Moderados        |

### Matriz de Decisión

| Solución                  | Resiliencia | Observabilidad | Operación | Prevención Pérdida | Recomendación         |
|--------------------------|-------------|----------------|-----------|--------------------|-----------------------|
| **Híbrido (DLT + CB)**   | Excelente   | Excelente      | Moderada  | Excelente          | ✅ **Seleccionada**    |
| **Dead Letter Topic**    | Excelente   | Excelente      | Automática| Excelente          | 🟡 Componente base     |
| **Event Store**          | Excelente   | Excelente      | Compleja  | Excelente          | 🟡 Considerada         |
| **Circuit Breaker**      | Moderada    | Básica         | Compleja  | Moderada           | 🟡 Complementaria      |
| **Manual Retry**         | Moderada    | Limitada       | Manual    | Buena              | ❌ Descartada          |
| **Reintentos sin DLT**   | Básica      | Muy limitada   | Simple    | Mala               | ❌ Descartada          |

---

## 💰 ANÁLISIS DE COSTOS (TCO 3 años)

> **Supuesto:** Uso de Apache Kafka (AWS MSK) con Dead Letter Topics, 5 topics principales, 4 países, 1 millón de mensajes/mes por topic. Costos estimados para almacenamiento, transferencias y monitoreo.

| Solución                | Licenciamiento | Infraestructura | Operación      | TCO 3 años   |
|------------------------|---------------|----------------|---------------|--------------|
| Kafka (AWS MSK) + DLT  | Incluido      | US$18,000      | US$0          | US$18,000    |
| Kafka Self-managed     | OSS           | US$12,000      | US$24,000     | US$36,000    |

---

## Consideraciones técnicas y riesgos

### Límites clave

- **Kafka DLT:** Retención configurable (7-90 días), sin límite de tamaño de mensaje (hasta 1MB default)
- **AWS MSK:** Throughput según tamaño de cluster, storage ilimitado

### Riesgos y mitigación

- **Complejidad Kafka:** mitigada con Confluent.Kafka SDK y monitoreo
- **Pérdida de mensajes:** mitigada con DLT y alertas
- **Costos storage:** mitigado con políticas de retención adecuadas

---

## ✔️ DECISIÓN

Se selecciona un **enfoque híbrido**: uso de `Dead Letter Topics (DLT)` en Apache Kafka complementado con `Circuit Breaker` para máxima resiliencia y observabilidad.

## Justificación

- Aislamiento y análisis de mensajes fallidos en topics dedicados
- Recuperación y reprocesamiento flexible desde DLT
- Observabilidad y auditoría completas con Grafana
- Integración nativa con ecosistema .NET (Confluent.Kafka)
- Reducción de riesgo de pérdida de información
- Cumplimiento de requisitos multi-tenant y multipaís
- Consistencia con decisión de mensajería (ADR-012: solo Kafka)

## Alternativas descartadas

- **Reintentos sin DLT:** alto riesgo de pérdida y baja trazabilidad
- **Manual Retry:** operación manual y poca escalabilidad
- **Queues (SQS, RabbitMQ):** no alineado con decisión de usar solo Kafka

---

## ⚠️ CONSECUENCIAS

- Todos los servicios deben implementar DLT y monitoreo de errores en Kafka
- Se deben definir políticas de reprocesamiento y alertas automáticas
- Naming convention: `{topic-name}.dlt` para dead letter topics
- El código debe usar Confluent.Kafka SDK con manejo de errores robusto

---

## 📚 REFERENCIAS

- [Kafka Dead Letter Topics Pattern](https://www.confluent.io/blog/error-handling-patterns-in-kafka/)
- [ADR-012: Mensajería Asíncrona](./adr-012-mensajeria-asincrona.md)
- [arc42: Decisiones de arquitectura](https://arc42.org/decision/)
