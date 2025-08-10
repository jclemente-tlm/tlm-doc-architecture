---
title: "Manejo de Errores en Cola"
sidebar_position: 15
---

## ✅ ESTADO

Aceptada – Agosto 2025

---

## 🗺️ CONTEXTO

Los servicios corporativos distribuidos con mensajería asíncrona requieren una estrategia robusta para manejar:

- **Mensajes fallidos** que no pueden procesarse después de múltiples reintentos
- **Poison messages** que causan errores recurrentes en consumidores
- **Recuperación de mensajes** para reprocesamiento manual o automatizado
- **Auditoría de fallos** para análisis de patrones y mejora continua
- **Aislamiento de errores** para evitar que mensajes problemáticos bloqueen colas
- **Alertas proactivas** cuando se detectan patrones de fallo
- **Retención configurable** según criticidad del mensaje
- **Compatibilidad multi-tenant** con segregación por país

La intención estratégica es **balancear resiliencia vs complejidad operacional** para sistemas de mensajería empresarial.

Las alternativas evaluadas fueron:

- **Dead Letter Queue (DLQ)** con Apache Kafka, AWS SQS, Azure Service Bus
- **Reintentos exponenciales** sin DLQ
- **Circuit Breaker** con bypass temporal
- **Manual retry** con almacenamiento persistente
- **Event Store** con replay capability
- **Hybrid approach** (DLQ + Circuit Breaker)

### COMPARATIVA DE ALTERNATIVAS

### Comparativa Cualitativa

| Criterio | DLQ | Reintentos | Circuit Breaker | Manual Retry | Event Store | Hybrid |
|----------|-----|------------|-----------------|--------------|-------------|--------|
| **Resiliencia** | ✅ Recuperación completa | 🟡 Básica, puede perder | 🟡 Protección temporal | 🟡 Depende intervención | ✅ Replay completo | ✅ Máxima protección |
| **Observabilidad** | ✅ Mensajes visibles | ❌ Muy limitada | 🟡 Métricas básicas | 🟡 Logs manuales | ✅ Historial completo | ✅ Visibilidad total |
| **Operación** | ✅ Automatizada | ✅ Muy simple | 🟡 Configuración compleja | ❌ Intervención manual | 🟡 Compleja gestión | 🟡 Moderadamente compleja |
| **Agnosticidad** | 🟡 Depende del broker | ✅ Totalmente agnóstico | ✅ Patrón universal | ✅ Totalmente agnóstico | ✅ Agnóstico | 🟡 Depende componentes |
| **Prevención Pérdida** | ✅ Cero pérdida | ❌ Alta probabilidad | 🟡 Puede perder durante corte | ✅ Persistencia manual | ✅ Cero pérdida | ✅ Cero pérdida |
| **Automatización** | ✅ Totalmente automática | ✅ Automática | ✅ Automática | ❌ Requiere intervención | 🟡 Semi-automática | ✅ Automática |
| **Costos** | ✅ Moderados | ✅ Mínimos | ✅ Moderados | ✅ Bajos | 🟡 Altos | 🟡 Moderados-altos |

### Matriz de Decisión

| Solución | Resiliencia | Observabilidad | Operación | Prevención Pérdida | Recomendación |
|----------|-------------|----------------|-----------|---------------------|---------------|
| **Hybrid (DLQ + Circuit Breaker)** | Excelente | Excelente | Moderada | Excelente | ✅ **Seleccionada** |
| **Dead Letter Queue** | Excelente | Excelente | Automática | Excelente | 🟡 Alternativa |
| **Event Store** | Excelente | Excelente | Compleja | Excelente | 🟡 Considerada |
| **Circuit Breaker** | Moderada | Básica | Compleja | Moderada | 🟡 Complementaria |
| **Manual Retry** | Moderada | Limitada | Manual | Buena | ❌ Descartada |
| **Reintentos sin DLQ** | Básica | Muy limitada | Simple | Mala | ❌ Descartada |

---

## DECISIÓN

Se implementarán `Dead Letter Queues (DLQ)` en las `colas SQS` utilizadas por los `microservicios` y sistemas que requieran resiliencia en el procesamiento de mensajes.

## Justificación

- Permite aislar y analizar mensajes que no pudieron procesarse.
- Facilita la recuperación y reprocesamiento manual o automatizado.
- Mejora la trazabilidad y auditoría de errores.
- Integración nativa con `AWS SQS` y `CloudWatch`.
- Reduce el riesgo de pérdida de información.

## Alternativas descartadas

- **Reintentos sin DLQ**: Mayor riesgo de pérdida de mensajes y menor trazabilidad.

---

## ⚠️ CONSECUENCIAS

- Los mensajes fallidos se almacenan en DLQ para análisis y recuperación.
- Se deben definir políticas de reprocesamiento y monitoreo.

---

## 📚 REFERENCIAS

- [AWS SQS DLQ](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-dead-letter-queues.html)
- [Arc42: Decisiones de arquitectura](https://arc42.org/decision/)
