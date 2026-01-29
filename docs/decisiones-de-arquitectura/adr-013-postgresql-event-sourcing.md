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
- **EventStoreDB** (nativo, especializado)
- **Apache Kafka** (event log, streaming)
- **MongoDB** (collections de eventos)
- **AWS DynamoDB Streams** (NoSQL, AWS nativo)
- **Azure CosmosDB Change Feed** (Azure nativo)

## 🔍 COMPARATIVA DE ALTERNATIVAS

### Comparativa Cualitativa

| Criterio              | PostgreSQL | EventStoreDB | Apache Kafka | MongoDB | DynamoDB Streams | CosmosDB |
|----------------------|------------|--------------|--------------|---------|------------------|----------|
| **Agnosticidad**     | ✅ OSS, multi-cloud | ✅ OSS, multi-cloud | ✅ OSS, multi-cloud | ✅ OSS, multi-cloud | ❌ Lock-in AWS | ❌ Lock-in Azure |
| **Event Sourcing**   | 🟡 Manual con JSON | ✅ Nativo | 🟡 Log como eventos | 🟡 Collections | 🟡 Streams | 🟡 Change feed |
| **Escalabilidad**    | 🟡 Limitada | ✅ Horizontal | ✅ Masiva | ✅ Horizontal | ✅ Automática | ✅ Global |
| **Ecosistema .NET**  | ✅ Excelente (Npgsql) | ✅ Cliente oficial | ✅ Confluent.Kafka | ✅ MongoDB.Driver | ✅ AWS SDK | ✅ Azure SDK |
| **Snapshots**        | 🟡 Manual | ✅ Nativo | 🟡 Compactación | 🟡 Manual | 🟡 Manual | 🟡 Manual |
| **Consistencia**     | ✅ ACID fuerte | ✅ Fuerte | 🟡 Eventual | 🟡 Eventual | 🟡 Eventual | 🟡 Configurable |
| **Operación**        | ✅ Conocimiento existente | 🟡 Especializada | 🟡 Compleja | ✅ Simple | ✅ Gestionada | ✅ Gestionada |
| **Costos**           | ✅ Gratuito OSS | ✅ OSS + comercial | ✅ Gratuito OSS | ✅ Gratuito OSS | 🟡 Por uso | 🟡 Por uso |

### Matriz de Decisión

| Solución                    | Agnosticidad | Event Sourcing | Escalabilidad | Ecosistema .NET | Recomendación         |
|-----------------------------|--------------|---------------|---------------|-----------------|-----------------------|
| **PostgreSQL + Event Table**| Excelente    | Manual        | Limitada      | Excelente       | ✅ **Seleccionada**    |
| **EventStoreDB**            | Excelente    | Nativo        | Buena         | Excelente       | 🟡 Alternativa         |
| **Apache Kafka**            | Excelente    | Como log      | Excelente     | Buena           | 🟡 Considerada         |
| **MongoDB**                 | Excelente    | Manual        | Buena         | Buena           | 🟡 Considerada         |
| **DynamoDB Streams**        | Mala         | Streams       | Excelente     | Buena           | ❌ Descartada          |
| **CosmosDB Change Feed**    | Mala         | Change feed   | Excelente     | Buena           | ❌ Descartada          |

## 💰 ANÁLISIS DE COSTOS (TCO 3 años)

> **Metodología y supuestos:** Se asume un uso promedio de 1M eventos/mes, 3 instancias, multi-región. El TCO (Total Cost of Ownership) se calcula para un horizonte de 3 años, incluyendo costos directos y estimaciones de operación. Los valores pueden variar según volumen y proveedor.

| Solución         | Licenciamiento | Infraestructura | Operación      | TCO 3 años   |
|------------------|---------------|----------------|---------------|--------------|
| PostgreSQL       | OSS           | US$30/mes      | US$360/año     | US$1,080     |
| EventStoreDB     | OSS           | US$50/mes      | US$600/año     | US$1,800     |
| Kafka            | OSS           | US$60/mes      | US$720/año     | US$2,160     |
| DynamoDB Streams | Pago por uso  | US$0           | US$0           | US$1,200/año |
| CosmosDB         | Pago por uso  | US$0           | US$0           | US$1,440/año |

---

## Consideraciones técnicas y riesgos

### Límites clave

- **PostgreSQL:** requiere lógica adicional para snapshots y proyecciones
- **EventStoreDB:** operación y monitoreo especializado
- **Kafka:** tuning, monitoreo y operación compleja
- **DynamoDB/CosmosDB:** lock-in cloud, consistencia eventual

### Riesgos y mitigación

- **Lock-in cloud:** mitigado usando solo tecnologías OSS y adaptadores desacoplados
- **Complejidad operativa:** mitigada con automatización y monitoreo
- **Costos variables cloud:** monitoreo y revisión anual

---

## ✔️ DECISIÓN

Se selecciona **PostgreSQL + Event Table** como solución estándar de Event Store para todos los servicios y microservicios corporativos.

## Justificación

- Permite trazabilidad completa y reconstrucción de estado a partir de eventos
- Facilita auditoría, debugging y patrones CQRS
- Bajo costo, portabilidad y operación conocida
- Desacoplamiento del backend mediante interfaces y adaptadores
- Soporte para migración futura a EventStoreDB o Kafka si la carga lo demanda

## Alternativas descartadas

- **DynamoDB Streams:** lock-in AWS, consistencia eventual, menor portabilidad
- **CosmosDB Change Feed:** lock-in Azure, consistencia eventual, menor portabilidad

---

## ⚠️ CONSECUENCIAS

- El código debe desacoplarse del proveedor concreto mediante interfaces
- Se facilita la migración multi-cloud y despliegue híbrido
- Se requiere mantener pruebas de integración para cada backend soportado

---

## 🏗️ ARQUITECTURA DE DESPLIEGUE

- PostgreSQL: tabla de eventos por dominio, particionada por tenant
- EventStoreDB/Kafka: integración futura soportada por adaptadores
- Backups y snapshots automáticos
- Monitoreo con Prometheus y Grafana

---

## 📊 MÉTRICAS Y MONITOREO

### KPIs Clave

- **Eventos procesados**: > 99.99% registrados
- **Latencia promedio**: < 100ms
- **Throughput**: > 10K eventos/minuto
- **Errores de persistencia**: < 0.01%

### Alertas Críticas

- Eventos pendientes > umbral
- Latencia > 500ms
- Fallos de persistencia repetidos
- Errores de integración SDK

---

## 📚 REFERENCIAS

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
