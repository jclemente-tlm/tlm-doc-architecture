---
title: "Mensajería Asíncrona"
sidebar_position: 12
---

## ✅ ESTADO

Aceptada – Agosto 2025

---

## 🗺️ CONTEXTO

La arquitectura de servicios corporativos requiere una solución de mensajería desacoplada, escalable y portable que soporte:

- **Comunicación asíncrona** entre microservicios
- **Despliegues multi-cloud y on-premises** para evitar lock-in
- **Event sourcing** y patrones dirigidos por eventos
- **Escalabilidad** para manejar cargas variables
- **Resiliencia** con garantías de entrega

La intención estratégica es **mantenerse lo más agnóstico posible** para facilitar portabilidad y migración entre proveedores.

Las alternativas evaluadas fueron:

- **Apache Kafka** (Open source, alta escalabilidad, agnóstico)
- **RabbitMQ** (Open source, flexible, fácil operación)
- **SNS + SQS (AWS)** (Gestionado, integración nativa, lock-in AWS)
- **Azure Service Bus** (Gestionado, lock-in Azure)
- **Google Pub/Sub** (Gestionado, lock-in GCP)

## 🔍 COMPARATIVA DE ALTERNATIVAS

### Comparativa Cualitativa

| Criterio | Kafka | RabbitMQ | SNS+SQS | Azure SB | Google PS |
|----------|-------|----------|---------|----------|-----------|
| **Agnosticidad** | ✅ Totalmente agnóstico | ✅ Totalmente agnóstico | ❌ Lock-in AWS | ❌ Lock-in Azure | ❌ Lock-in GCP |
| **Escalabilidad** | ✅ Masiva, particiones | 🟡 Vertical limitada | ✅ Automática ilimitada | ✅ Muy buena | ✅ Muy buena |
| **Operación** | 🟡 Compleja, requiere expertise | ✅ Relativamente simple | ✅ Totalmente gestionado | ✅ Totalmente gestionado | ✅ Totalmente gestionado |
| **Rendimiento** | ✅ Máximo throughput | 🟡 Moderado | ✅ Muy alto | ✅ Muy alto | ✅ Muy alto |
| **Ecosistema .NET** | ✅ Confluent.Kafka | ✅ RabbitMQ.Client | ✅ AWS SDK nativo | ✅ Azure SDK | 🟡 Google SDK |
| **Persistencia** | ✅ Log distribuido | ✅ Durable queues | ✅ SQS persistente | ✅ Persistencia nativa | ✅ Persistencia nativa |
| **Patrones** | ✅ Streaming + messaging | ✅ Messaging tradicional | ✅ Pub/sub + queues | ✅ Messaging completo | ✅ Pub/sub puro |

### Matriz de Decisión

| Solución | Agnosticidad | Escalabilidad | Operación | Rendimiento | Recomendación |
|----------|--------------|---------------|-----------|-------------|---------------|
| **AWS SNS + SQS** | Mala | Excelente | Gestionada | Muy alto | ✅ **Seleccionada** |
| **Apache Kafka** | Excelente | Excelente | Compleja | Excelente | 🟡 Alternativa |
| **RabbitMQ** | Excelente | Limitada | Simple | Moderado | 🟡 Considerada |
| **Azure Service Bus** | Mala | Muy buena | Gestionada | Muy alto | ❌ Descartada |
| **Google Pub/Sub** | Mala | Muy buena | Gestionada | Muy alto | ❌ Descartada |

## 💰 ANÁLISIS DE COSTOS (TCO 3 años)

### Escenario Base: 1M mensajes/mes, 3 instancias, multi-región

| Solución | Licenciamiento | Infraestructura | Operación | TCO 3 años |
|----------|----------------|-----------------|-----------|------------|
| **Kafka** | US$0 (OSS) | US$2,160/año | US$36,000/año | **US$114,480** |
| **RabbitMQ** | US$0 (OSS) | US$1,800/año | US$24,000/año | **US$77,400** |
| **SNS+SQS** | Pago por uso | US$0 | US$0 | **US$1,080/año** |
| **Azure SB** | Pago por uso | US$0 | US$0 | **US$1,440/año** |
| **Google PS** | Pago por uso | US$0 | US$0 | **US$1,200/año** |

### Escenario Alto Volumen: 100M mensajes/mes

| Solución | TCO 3 años | Escalabilidad |
|----------|------------|---------------|
| **Kafka** | **US$180,000** | Lineal |
| **RabbitMQ** | **US$240,000** | Limitada |
| **SNS+SQS** | **US$108,000** | Automática |
| **Azure SB** | **US$144,000** | Automática |
| **Google PS** | **US$120,000** | Automática |

## ⚖️ DECISIÓN

**Seleccionamos AWS SNS + SQS** como solución de mensajería principal por:

### Ventajas Clave

- **Operación gestionada**: Sin necesidad de administrar infraestructura propia
- **Escalabilidad automática**: Maneja millones de mensajes sin intervención manual
- **Integración nativa con AWS**: Facilita despliegues y automatización
- **Costos bajos para cargas típicas**: Pago por uso, sin costos fijos de operación
- **Alta disponibilidad y durabilidad**: Garantías de entrega y persistencia

### Mitigación de Desventajas

- **Lock-in AWS**: Se mitiga con desacoplamiento vía interfaces y adaptadores
- **Menor portabilidad**: Se documenta la arquitectura para facilitar migración futura si es necesario
- **Limitaciones en patrones avanzados**: Para casos de event sourcing puro, se evaluará Kafka o RabbitMQ como alternativa

### Estrategia Híbrida

Para escenarios donde se requiera portabilidad o patrones avanzados:

- **Event sourcing avanzado**: Kafka como alternativa para cargas críticas
- **Desarrollo/Testing**: RabbitMQ para entornos simples y portables

## 🔄 CONSECUENCIAS

### Positivas

- ✅ **Portabilidad completa** entre clouds y on-premises
- ✅ **Escalabilidad ilimitada** para crecimiento futuro
- ✅ **Event sourcing robusto** para auditoría y trazabilidad
- ✅ **Ecosistema rico** de herramientas y conectores
- ✅ **Control total** sobre configuración y optimización

### Negativas

- ❌ **Mayor complejidad operacional** requiere expertise especializado
- ❌ **Costos iniciales más altos** en infraestructura y operación
- ❌ **Curva de aprendizaje** para el equipo de desarrollo

### Neutras

- 🔄 **Inversión en capacitación** necesaria pero reutilizable
- 🔄 **Herramientas de monitoreo** específicas requeridas

## 📚 REFERENCIAS

- [Apache Kafka Documentation](https://kafka.apache.org/documentation/)
- [Kafka vs RabbitMQ Comparison](https://kafka.apache.org/documentation/#design_comparison)
- [Event Sourcing Patterns](https://microservices.io/patterns/data/event-sourcing.html)
- [Multi-Cloud Messaging Strategies](https://cloud.google.com/architecture/hybrid-and-multi-cloud-messaging-patterns)

---

**Decisión tomada por:** Equipo de Arquitectura
**Fecha:** Agosto 2025
**Próxima revisión:** Agosto 2026
