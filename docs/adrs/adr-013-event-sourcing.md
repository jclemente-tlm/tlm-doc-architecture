---
id: adr-013-event-sourcing
title: "Event Sourcing"
sidebar_position: 13
---

## ✅ ESTADO

Aceptada – Agosto 2025

---

## 🗺️ CONTEXTO

Los servicios corporativos distribuidos requieren una estrategia de Event Store que soporte:

- **Event Sourcing** para auditoría completa y trazabilidad de cambios
- **Multi-tenancy** con segregación de eventos por país/tenant
- **Multi-cloud portabilidad** sin vendor lock-in
- **Escalabilidad horizontal** para alto volumen de eventos
- **Consistencia transaccional** para integridad de datos
- **Snapshots automáticos** para optimización de performance
- **Proyecciones en tiempo real** para vistas materializadas
- **Replay de eventos** para debugging y migración de datos
- **Compliance y auditoría** con retención configurable
- **Disaster recovery** con backup y replicación

La intención estratégica es **priorizar agnosticidad vs performance especializada** para Event Store empresarial.

Las alternativas evaluadas fueron:

- **PostgreSQL + Event Table** (RDBMS, JSON events, triggers)
- **EventStoreDB** (Event Store nativo, especializado)
- **Apache Kafka** (Streaming platform, event log)
- **MongoDB** (Document store, event collections)
- **AWS DynamoDB Streams** (NoSQL managed, AWS nativo)
- **Azure CosmosDB Change Feed** (Multi-model, Azure nativo)

### Comparativa Cualitativa

| Criterio | PostgreSQL | EventStoreDB | Apache Kafka | MongoDB | DynamoDB Streams | CosmosDB |
|----------|------------|--------------|--------------|---------|------------------|----------|
| **Agnosticidad** | ✅ Totalmente agnóstico | ✅ Totalmente agnóstico | ✅ Totalmente agnóstico | ✅ Totalmente agnóstico | ❌ Lock-in AWS | ❌ Lock-in Azure |
| **Event Sourcing** | 🟡 Manual con JSON | ✅ Nativo, especializado | 🟡 Log como eventos | 🟡 Collections | 🟡 Streams | 🟡 Change feed |
| **Escalabilidad** | 🟡 Vertical limitada | ✅ Horizontal | ✅ Masiva | ✅ Horizontal | ✅ Automática | ✅ Global |
| **Ecosistema .NET** | ✅ Npgsql excelente | ✅ Cliente oficial | ✅ Confluent.Kafka | ✅ MongoDB.Driver | ✅ AWS SDK | ✅ Azure SDK |
| **Snapshots** | 🟡 Manual | ✅ Nativo | 🟡 Compactación | 🟡 Manual | 🟡 Manual | 🟡 Manual |
| **Consistencia** | ✅ ACID fuerte | ✅ Fuerte | 🟡 Eventual | 🟡 Eventual | 🟡 Eventual | 🟡 Configurable |
| **Operación** | ✅ Conocimiento existente | 🟡 Especializada | 🟡 Compleja | ✅ Simple | ✅ Gestionada | ✅ Gestionada |
| **Costos** | ✅ Gratuito OSS | ✅ OSS + comercial | ✅ Gratuito OSS | ✅ Gratuito OSS | 🟡 Por uso | 🟡 Por uso |

### Matriz de Decisión

| Solución | Agnosticidad | Event Sourcing | Escalabilidad | Ecosistema .NET | Recomendación |
|----------|--------------|----------------|---------------|-----------------|---------------|
| **PostgreSQL + Event Table** | Excelente | Manual | Limitada | Excelente | ✅ **Seleccionada** |
| **EventStoreDB** | Excelente | Nativo | Buena | Excelente | 🟡 Alternativa |
| **Apache Kafka** | Excelente | Como log | Excelente | Buena | 🟡 Considerada |
| **MongoDB** | Excelente | Manual | Buena | Buena | 🟡 Considerada |
| **DynamoDB Streams** | Mala | Streams | Excelente | Buena | ❌ Descartada |
| **CosmosDB Change Feed** | Mala | Change feed | Excelente | Buena | ❌ Descartada |

### Comparativa de costos estimados (2025)

| Solución         | Costo mensual base* | Costos adicionales         | Infra propia |
|------------------|---------------------|---------------------------|--------------|
| PostgreSQL       | ~US$30/mes (VM)     | Backup, monitoreo         | Sí           |
| EventStoreDB     | ~US$50/mes (VM)     | Licencia Enterprise opc.  | Sí           |
| DynamoDB Streams | Pago por uso        | Lecturas/escrituras       | No           |
| CosmosDB         | Pago por uso        | Throughput, almacenamiento| No           |

*Precios aproximados, sujetos a variación según proveedor y volumen.

---

## ✔️ DECISIÓN

Se recomienda abstraer el Event Store mediante interfaces y patrones (Repository, EventStoreAdapter) para permitir cambiar de backend sin impacto en la lógica de dominio. Inicialmente se usará PostgreSQL por su bajo costo y portabilidad, pero la arquitectura soporta migración a EventStoreDB o servicios cloud según necesidades futuras.

## Justificación

- Permite trazabilidad completa y reconstrucción de estado a partir de eventos.
- Facilita auditoría, debugging y patrones CQRS.
- El desacoplamiento del backend permite portabilidad y evita lock-in.
- PostgreSQL es suficiente para la mayoría de escenarios, pero se puede evolucionar a soluciones especializadas si la carga o los requisitos lo demandan.

## Limitaciones

- PostgreSQL requiere lógica adicional para snapshots y proyecciones.
- Las soluciones cloud pueden implicar lock-in y costos variables.
- EventStoreDB requiere operación y monitoreo especializado.

## Alternativas descartadas

- DynamoDB Streams y CosmosDB: lock-in cloud, consistencia eventual, menos flexibilidad para despliegues híbridos.

---

## ⚠️ CONSECUENCIAS

- El código debe desacoplarse del proveedor concreto mediante interfaces.
- Se facilita la migración multi-cloud y despliegue híbrido.
- Se requiere mantener pruebas de integración para cada backend soportado.

---

## 📚 REFERENCIAS

- [EventStoreDB](https://eventstore.com/)
- [Event Sourcing en PostgreSQL](https://eventstore.org/docs/)
- [DynamoDB Streams](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Streams.html)
- [CosmosDB Change Feed](https://learn.microsoft.com/en-us/azure/cosmos-db/change-feed)
