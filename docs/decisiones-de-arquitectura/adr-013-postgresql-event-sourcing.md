---
title: "ADR-013: PostgreSQL Event Sourcing"
sidebar_position: 13
---

## ✅ ESTADO

Aceptada – Agosto 2025

---

## 🗺️ CONTEXTO

Los servicios corporativos requieren una solución de Event Store que permita:

- **Event Sourcing** para trazabilidad y auditoría completa
- **Multi-tenancy** con segregación de eventos por país/tenant
- **Portabilidad multi-cloud** sin lock-in
- **Escalabilidad horizontal** para alto volumen de eventos
- **Consistencia transaccional** para integridad de datos
- **Snapshots automáticos** para optimización de performance
- **Proyecciones en tiempo real** para vistas materializadas
- **Replay de eventos** para debugging y migración
- **Retención configurable y compliance**
- **Disaster recovery** con backup y replicación

Alternativas evaluadas:

- **PostgreSQL + Event Table** (RDBMS, JSON events, triggers)
- **Marten** (biblioteca .NET para Event Sourcing sobre PostgreSQL)
- **EventStoreDB** (nativo, especializado)
- **Apache Kafka** (event log, streaming)
- **MongoDB** (collections de eventos)
- **AWS DynamoDB Streams** (NoSQL, AWS nativo)
- **Azure CosmosDB Change Feed** (Azure nativo)

## 🔍 COMPARATIVA DE ALTERNATIVAS

### Comparativa Cualitativa

| Criterio            | PostgreSQL                | Marten                     | EventStoreDB        | Apache Kafka        | MongoDB             | DynamoDB Streams | CosmosDB         |
| ------------------- | ------------------------- | -------------------------- | ------------------- | ------------------- | ------------------- | ---------------- | ---------------- |
| **Agnosticidad**    | ✅ OSS, multi-cloud       | ✅ OSS, PostgreSQL-based   | ✅ OSS, multi-cloud | ✅ OSS, multi-cloud | ✅ OSS, multi-cloud | ❌ Lock-in AWS   | ❌ Lock-in Azure |
| **Event Sourcing**  | ⚠️ Manual con JSON        | ✅ Nativo .NET             | ✅ Nativo           | ⚠️ Log como eventos | ⚠️ Collections      | ⚠️ Streams       | ⚠️ Change feed   |
| **Escalabilidad**   | ⚠️ Limitada               | ⚠️ Depende PostgreSQL      | ✅ Horizontal       | ✅ Masiva           | ✅ Horizontal       | ✅ Automática    | ✅ Global        |
| **Ecosistema .NET** | ✅ Excelente (Npgsql)     | ✅ Diseñado para .NET      | ✅ Cliente oficial  | ✅ Confluent.Kafka  | ✅ MongoDB.Driver   | ✅ AWS SDK       | ✅ Azure SDK     |
| **Snapshots**       | ⚠️ Manual                 | ✅ Automático              | ✅ Nativo           | ⚠️ Compactación     | ⚠️ Manual           | ⚠️ Manual        | ⚠️ Manual        |
| **Consistencia**    | ✅ ACID fuerte            | ✅ ACID PostgreSQL         | ✅ Fuerte           | ⚠️ Eventual         | ⚠️ Eventual         | ⚠️ Eventual      | ⚠️ Configurable  |
| **Operación**       | ✅ Conocimiento existente | ✅ .NET libraries familiar | ⚠️ Especializada    | ⚠️ Compleja         | ✅ Simple           | ✅ Gestionada    | ✅ Gestionada    |
| **Costos**          | ✅ Gratuito OSS           | ✅ Gratuito OSS            | ✅ OSS + comercial  | ✅ Gratuito OSS     | ✅ Gratuito OSS     | ⚠️ Por uso       | ⚠️ Por uso       |

**Leyenda:** ✅ Cumple completamente | ⚠️ Cumple parcialmente | ❌ No cumple

## ✔️ DECISIÓN

Se selecciona **PostgreSQL + Event Table** como solución estándar de Event Store para todos los servicios y microservicios corporativos.

## Justificación

- Permite trazabilidad completa y reconstrucción de estado a partir de eventos
- Facilita auditoría, debugging y patrones CQRS
- Bajo costo, portabilidad y operación conocida
- Desacoplamiento del backend mediante interfaces y adaptadores
- Soporte para migración futura a EventStoreDB o Kafka si la carga lo demanda

## Alternativas descartadas

- **Marten:** excelente para .NET pero menor madurez vs PostgreSQL manual (2015 vs tradición), comunidad más pequeña, abstracción adicional innecesaria con conocimiento PostgreSQL existente
- **EventStoreDB:** especializado pero requiere infraestructura adicional, complejidad operativa mayor, costo licencias comerciales, sobrede-dimensionado para necesidades actuales
- **Apache Kafka:** diseñado para streaming no event sourcing puro, complejidad operativa alta, costos infraestructura, overhead innecesario para event store
- **MongoDB:** consistencia eventual, modelo documento no ideal para event log append-only, menor garantías ACID vs PostgreSQL
- **DynamoDB Streams:** lock-in AWS, consistencia eventual, modelo streams no event store completo, menor portabilidad
- **CosmosDB Change Feed:** lock-in Azure, consistencia eventual configurable pero compleja, infraestructura AWS ya establecida

---

## ⚠️ CONSECUENCIAS

### Positivas

- Trazabilidad completa y reconstitución de estado a partir de eventos
- Auditoría y debugging facilitados
- Soporte CQRS con proyecciones desde eventos
- Bajo costo y operación conocida (PostgreSQL existente)
- Portabilidad multi-cloud sin lock-in

### Negativas (Riesgos y Mitigaciones)

- **Snapshots manuales:** requiere lógica adicional para optimizar lecturas - mitigado con patrones documentados
- **Escalabilidad limitada:** vs EventStoreDB/Kafka - mitigado con particionamiento y migración futura soportada
- **Proyecciones custom:** requiere desarrollo manual - mitigado con interfaces desacopladas

---

## 📚 REFERENCIAS

- [PostgreSQL Event Sourcing](https://www.postgresql.org/docs/current/indexes.html)
- [Marten Event Store](https://martendb.io/)
- [EventStoreDB](https://eventstore.com/)
- [Event Sourcing en PostgreSQL](https://eventstore.org/docs/)
- [Apache Kafka](https://kafka.apache.org/)
- [MongoDB Change Streams](https://www.mongodb.com/docs/manual/changeStreams/)
- [DynamoDB Streams](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Streams.html)
- [CosmosDB Change Feed](https://learn.microsoft.com/en-us/azure/cosmos-db/change-feed)

---

**Decisión tomada por:** Equipo de Arquitectura
**Fecha:** Agosto 2025
**Próxima revisión:** Agosto 2026
