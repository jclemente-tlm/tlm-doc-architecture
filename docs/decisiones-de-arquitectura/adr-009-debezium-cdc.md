---
title: "ADR-009: Debezium CDC"
sidebar_position: 9
---

## ✅ ESTADO

Aceptada – Febrero 2026

---

## 🗺️ CONTEXTO

Los servicios corporativos requieren una solución robusta de **Change Data Capture (CDC)** para:

- **Sincronización en tiempo real** de datos entre bases de datos y sistemas downstream
- **Event-driven architecture** capturando cambios de base de datos como eventos
- **Integración con Kafka** para streaming de cambios de datos
- **Replicación de datos** para análisis, reporting y data lakes
- **Auditoría y trazabilidad** de cambios en datos críticos
- **Desacoplamiento de sistemas** legacy mediante captura de cambios
- **Microservicios data synchronization** sin acoplamiento directo

La intención estratégica es **maximizar agnosticidad tecnológica**, adoptar estándares open source y garantizar capacidades enterprise con bajo overhead operativo.

Alternativas evaluadas:

- **Debezium** (Open source, Kafka-based CDC, múltiples conectores)
- **Oracle GoldenGate** (Enterprise, multi-database, líder mercado)
- **IBM InfoSphere Data Replication** (Enterprise, mainframe legacy)
- **AWS Database Migration Service (DMS)** (Gestionado AWS, CDC + migración)
- **Azure Data Factory** (Gestionado Azure, ETL + CDC)
- **Google Cloud Dataflow** (Gestionado GCP, streaming + batch)

## 🔍 COMPARATIVA DE ALTERNATIVAS

| Criterio                      | Debezium                                                          | Oracle GoldenGate                             | IBM InfoSphere                       | AWS DMS                             | Azure Data Factory                  | Google Cloud Dataflow            |
| ----------------------------- | ----------------------------------------------------------------- | --------------------------------------------- | ------------------------------------ | ----------------------------------- | ----------------------------------- | -------------------------------- |
| **Agnosticidad**              | ✅ Totalmente agnóstico                                           | ⚠️ Mejor con Oracle                           | ⚠️ Mejor con IBM DB2                 | ❌ Lock-in AWS                      | ❌ Lock-in Azure                    | ❌ Lock-in GCP                   |
| **Madurez**                   | ✅ Alta (2016, Red Hat/IBM)                                       | ✅ Muy alta (1992, líder mercado)             | ✅ Muy alta (1994, enterprise)       | ✅ Alta (2016, AWS standard)        | ✅ Alta (2015, Azure std)           | ✅ Alta (2014, Apache Beam)      |
| **Adopción**                  | ✅ Muy alta (8K⭐, líder OSS CDC)                                 | ✅ Muy alta (enterprise líder)                | ⚠️ Media (mainframe legacy)          | ✅ Alta (AWS ecosystem)             | ✅ Alta (Azure ecosystem)           | ⚠️ Media (GCP adoption)          |
| **Modelo de gestión**         | ⚠️ Self-hosted (Kafka Connect)                                    | ⚠️ Self-hosted/Cloud                          | ⚠️ Self-hosted                       | ✅ Fully managed                    | ✅ Fully managed                    | ✅ Fully managed                 |
| **Complejidad operativa**     | ⚠️ Media (0.5 FTE, 5-10h/sem)                                     | ❌ Muy alta (2+ FTE, 20-40h/sem)              | ❌ Muy alta (2+ FTE, 20-40h/sem)     | ✅ Baja (0.25 FTE, `<5h/sem)`         | ✅ Baja (0.25 FTE, `<5h/sem)`         | ⚠️ Media (0.5 FTE, 5-10h/sem)    |
| **Integración Kafka**         | ✅ Nativa (Kafka Connect)                                         | ⚠️ Requiere adaptadores                       | ⚠️ Manual integration                | ⚠️ Kinesis preferred                | ⚠️ Event Hubs preferred             | ⚠️ Pub/Sub preferred             |
| **Bases de datos soportadas** | ✅ PostgreSQL, MySQL, MongoDB, SQL Server, Oracle, DB2, Cassandra | ✅ Oracle, SQL Server, MySQL, PostgreSQL, DB2 | ✅ DB2, Oracle, SQL Server, Informix | ✅ 20+ engines (RDS, Aurora, etc.)  | ✅ 20+ engines (SQL, NoSQL)         | ⚠️ BigQuery, Spanner, Cloud SQL  |
| **CDC Method**                | ✅ Log-based (transaction logs)                                   | ✅ Log-based + trigger-based                  | ✅ Log-based                         | ✅ Log-based + trigger-based        | ⚠️ Polling + trigger-based          | ⚠️ Batch + streaming             |
| **Latencia**                  | ✅ `<100ms `(real-time streaming)                                   | ✅ `<50ms `(enterprise tuned)                   | ✅ `<100ms `                           | ⚠️ ~1-10s (near real-time)          | ⚠️ ~5-30s (configurable)            | ⚠️ ~10s-5min (depending mode)    |
| **Rendimiento**               | ✅ 10K+ events/seg                                                | ✅ 50K+ events/seg                            | ✅ 20K+ events/seg                   | ⚠️ 5K-10K events/seg                | ⚠️ Variable (batch oriented)        | ✅ 100K+ events/seg (streaming)  |
| **Escalabilidad**             | ✅ Horizontal (Kafka partitions)                                  | ✅ Horizontal + vertical                      | ⚠️ Principalmente vertical           | ⚠️ Auto-scaling limitado            | ✅ Auto-scaling                     | ✅ Auto-scaling                  |
| **Schema Evolution**          | ✅ Avro, JSON, Protobuf (Schema Registry)                         | ⚠️ Limitado                                   | ⚠️ Manual config                     | ❌ No soportado                     | ⚠️ Básico                           | ⚠️ Manual schemas                |
| **Transformaciones**          | ✅ Single Message Transforms (SMT)                                | ✅ Data transformations                       | ✅ Mapping transformations           | ⚠️ Básicas                          | ✅ Data flows completos             | ✅ Apache Beam transforms        |
| **Filtrado**                  | ✅ Table filtering, column filtering                              | ✅ Advanced filtering                         | ✅ Table/column filtering            | ✅ Selection rules                  | ✅ Filter activities                | ✅ Beam filters                  |
| **Initial Snapshot**          | ✅ Consistent snapshot                                            | ✅ Enterprise snapshot                        | ✅ Initial load                      | ✅ Full load + CDC                  | ✅ Full copy + incremental          | ⚠️ Manual initial load           |
| **Monitoring**                | ✅ JMX metrics + Kafka metrics                                    | ✅ Enterprise monitoring                      | ✅ IBM monitoring tools              | ✅ CloudWatch integration           | ✅ Azure Monitor                    | ✅ Cloud Monitoring              |
| **Comunidad/Soporte**         | ✅ Red Hat support + comunidad activa                             | ✅ Oracle support enterprise                  | ⚠️ IBM support (declining)           | ✅ AWS support                      | ✅ Microsoft support                | ✅ Google support                |
| **Licencia**                  | ✅ Apache 2.0 (OSS)                                               | ❌ Propietaria (costosa)                      | ❌ Propietaria (muy costosa)         | ⚠️ AWS service (pay-per-use)        | ⚠️ Azure service (pay-per-use)      | ⚠️ GCP service (pay-per-use)     |
| **Costos**                    | ✅ $0 licencia + ~$300-600/mes infra                              | ❌ $50K-500K/año licencia + infra             | ❌ $100K-1M+/año licencia            | ⚠️ $0.50-1.50/h/task (~$360-1K/mes) | ⚠️ $1-5/h/pipeline (~$700-3.5K/mes) | ⚠️ $0.056/vCPU-hr (~$400-2K/mes) |

**Leyenda:** ✅ Cumple completamente | ⚠️ Cumple parcialmente | ❌ No cumple

---

## ✔️ DECISIÓN

Se selecciona **Debezium** como solución estándar de Change Data Capture (CDC) para todos los servicios corporativos, desplegado sobre Kafka Connect en AWS ECS Fargate, priorizando **agnosticidad tecnológica**, **integración nativa con Kafka**, **bajo costo** y **flexibilidad**.

### Justificación

- **Agnosticidad total:** no depende de cloud provider específico, soporta múltiples bases de datos (PostgreSQL, MySQL, MongoDB, SQL Server, Oracle)
- **Integración nativa con Kafka:** desplegado como Kafka Connect, aprovecha infraestructura existente (ADR-012)
- **Log-based CDC real-time:** latencia `<100ms `capturando cambios directamente de transaction logs sin impacto en base de datos
- **Open source Apache 2.0:** sin costos de licencia, comunidad activa, soporte Red Hat enterprise disponible
- **Schema evolution:** soporte completo para Avro, JSON, Protobuf con Schema Registry
- **Costos optimizados:** $0 licencia + infraestructura compartida con Kafka (~$300-600/mes incremental)
- **Escalabilidad horizontal:** escala con Kafka partitions, probado en producción enterprise
- **Flexible transformations:** Single Message Transforms (SMT) para filtrado, enriquecimiento, routing

### Alternativas descartadas

- **Oracle GoldenGate:** costos prohibitivos ($50K-500K/año), lock-in Oracle, complejidad operativa muy alta (2+ FTE), sobrede-dimensionado para necesidades actuales
- **IBM InfoSphere:** costos extremadamente altos ($100K-1M+/año), foco mainframe legacy, comunidad en declive, lock-in IBM, no justificado sin infraestructura IBM
- **AWS DMS:** lock-in AWS, latencia mayor (~1-10s vs `<100ms)`, transformaciones limitadas, costos escalables ($360-1K/mes base), preferencia Kinesis sobre Kafka reduce integración
- **Azure Data Factory:** lock-in Azure, orientado a ETL batch más que CDC real-time, latencia ~5-30s, infraestructura AWS ya establecida (ADR-003, ADR-007)
- **Google Cloud Dataflow:** lock-in GCP, **vendor adicional sin infraestructura GCP existente** (requiere cuenta/proyecto/billing GCP activo), **complejidad multi-vendor** (AWS + Azure + GCP) sin beneficio diferencial, **overhead operativo** (tercera consola cloud, tercera facturación, tercer soporte), menor adopción CDC específico

---

## ⚠️ CONSECUENCIAS

### Positivas

- ✅ Agnosticidad tecnológica total - portable entre clouds y bases de datos
- ✅ Integración nativa con infraestructura Kafka existente
- ✅ CDC real-time (`<100ms)` sin impacto en base de datos origen
- ✅ Costos optimizados ($0 licencia + infraestructura compartida)
- ✅ Schema evolution con Schema Registry (Avro, Protobuf)
- ✅ Escalabilidad horizontal probada en producción
- ✅ Comunidad activa + soporte Red Hat enterprise disponible
- ✅ Open source con visibilidad completa del código

### Negativas

- ⚠️ Requiere aprendizaje de Kafka Connect y Debezium connectors
- ⚠️ Complejidad operativa media (monitoring, connector management)
- ⚠️ Requiere configuración específica por base de datos (transaction logs, permisos)
- ⚠️ Snapshot inicial puede ser lento en bases de datos muy grandes

### Mitigaciones

- Capacitación del equipo en Debezium y Kafka Connect
- Automatización completa con Terraform/IaC para deployment
- Documentación interna de patterns y troubleshooting
- Monitoreo proactivo con JMX metrics + Kafka metrics
- Planificación de snapshots iniciales en ventanas de bajo tráfico
- Configuración de SMT (Single Message Transforms) para casos comunes

---

## 📚 REFERENCIAS

- [Debezium](https://debezium.io/)
- [Debezium GitHub](https://github.com/debezium/debezium)
- [Debezium Connectors](https://debezium.io/documentation/reference/stable/connectors/index.html)
- [Kafka Connect](https://kafka.apache.org/documentation/#connect)
- [Oracle GoldenGate](https://www.oracle.com/integration/goldengate/)
- [AWS DMS](https://aws.amazon.com/dms/)
- [Azure Data Factory](https://azure.microsoft.com/en-us/services/data-factory/)
- [Google Cloud Dataflow](https://cloud.google.com/dataflow)
- [Change Data Capture Patterns](https://www.confluent.io/blog/cdc-change-data-capture-patterns/)
- [Debezium vs Alternatives](https://debezium.io/documentation/faq/#how-does-debezium-compare)
