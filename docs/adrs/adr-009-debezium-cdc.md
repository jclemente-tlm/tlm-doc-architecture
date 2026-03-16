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

---

## 🔍 COMPARATIVA DE ALTERNATIVAS

| Criterio                      | Debezium                                                          | Oracle GoldenGate                             | IBM InfoSphere                       | AWS DMS                             | Azure Data Factory                  |
| ----------------------------- | ----------------------------------------------------------------- | --------------------------------------------- | ------------------------------------ | ----------------------------------- | ----------------------------------- |
| **Agnosticidad**              | ✅ Totalmente agnóstico                                           | ⚠️ Mejor con Oracle                           | ⚠️ Mejor con IBM DB2                 | ❌ Lock-in AWS                      | ❌ Lock-in Azure                    |
| **Madurez**                   | ✅ Alta (2016, Red Hat/IBM)                                       | ✅ Muy alta (1992, líder mercado)             | ✅ Muy alta (1994, enterprise)       | ✅ Alta (2016, AWS standard)        | ✅ Alta (2015, Azure std)           |
| **Adopción**                  | ✅ Muy alta (líder OSS CDC, comunidad activa)                     | ✅ Muy alta (enterprise líder)                | ⚠️ Media (mainframe legacy)          | ✅ Alta (AWS ecosystem)             | ✅ Alta (Azure ecosystem)           |
| **Modelo de gestión**         | ⚠️ Self-hosted (Kafka Connect)                                    | ⚠️ Self-hosted/Cloud                          | ⚠️ Self-hosted                       | ✅ Fully managed                    | ✅ Fully managed                    |
| **Complejidad operativa**     | ⚠️ Media (0.5 FTE, 5-10h/sem)                                     | ❌ Muy alta (2+ FTE, 20-40h/sem)              | ❌ Muy alta (2+ FTE, 20-40h/sem)     | ✅ Baja (0.25 FTE, `<5h/sem)`       | ✅ Baja (0.25 FTE, `<5h/sem)`       |
| **Integración Kafka**         | ✅ Nativa (Kafka Connect)                                         | ⚠️ Requiere adaptadores                       | ⚠️ Integración manual                     | ⚠️ Kinesis preferred                | ⚠️ Event Hubs preferred             |
| **Bases de datos soportadas** | ✅ PostgreSQL, MySQL, MongoDB, SQL Server, Oracle, DB2, Cassandra | ✅ Oracle, SQL Server, MySQL, PostgreSQL, DB2 | ✅ DB2, Oracle, SQL Server, Informix | ✅ 20+ engines (RDS, Aurora, etc.)  | ✅ 20+ engines (SQL, NoSQL)         |
| **CDC Method**                | ✅ Log-based (transaction logs)                                   | ✅ Log-based + trigger-based                  | ✅ Log-based                         | ✅ Log-based + trigger-based        | ⚠️ Polling + trigger-based          |
| **Latencia**                  | ✅ `<100ms `(real-time streaming)                                 | ✅ `<50ms `(enterprise tuned)                 | ✅ `<100ms `                         | ⚠️ ~1-10s (near real-time)          | ⚠️ ~5-30s (configurable)            |
| **Rendimiento**               | ✅ 10K+ events/seg                                                | ✅ 50K+ events/seg                            | ✅ 20K+ events/seg                   | ⚠️ 5K-10K events/seg                | ⚠️ Variable (batch oriented)        |
| **Escalabilidad**             | ✅ Horizontal (Kafka partitions)                                  | ✅ Horizontal + vertical                      | ⚠️ Principalmente vertical           | ⚠️ Auto-scaling limitado            | ✅ Auto-scaling                     |
| **Schema Evolution**          | ✅ Avro, JSON, Protobuf (Schema Registry)                         | ⚠️ Limitado                                   | ⚠️ Configuración manual                   | ❌ No soportado                     | ⚠️ Básico                           |
| **Transformaciones**          | ✅ Single Message Transforms (SMT)                                | ✅ Transformaciones de datos                  | ✅ Transformaciones de mapeo             | ⚠️ Básicas                          | ✅ Data flows completos             |
| **Filtrado**                  | ✅ Table filtering, column filtering                              | ✅ Advanced filtering                         | ✅ Table/column filtering            | ✅ Selection rules                  | ✅ Filter activities                |
| **Initial Snapshot**          | ✅ Consistent snapshot                                            | ✅ Snapshot empresarial                       | ✅ Carga inicial                         | ✅ Carga completa + CDC                  | ✅ Copia completa + incremental          |
| **Monitoring**                | ✅ JMX metrics + Kafka metrics                                    | ✅ Monitoreo empresarial                      | ✅ Herramientas de monitoreo IBM         | ✅ CloudWatch integration           | ✅ Azure Monitor                    |
| **Comunidad/Soporte**         | ✅ Red Hat support + comunidad activa                             | ✅ Oracle support enterprise                  | ⚠️ Soporte IBM (en declive)            | ✅ AWS support                      | ✅ Microsoft support                |
| **Licencia**                  | ✅ Apache 2.0 (OSS)                                               | ❌ Propietaria (costosa)                      | ❌ Propietaria (muy costosa)         | ⚠️ AWS service (pay-per-use)        | ⚠️ Azure service (pay-per-use)      |
| **Costos**                    | ✅ $0 licencia + ~$300-600/mes infra                              | ❌ $50K-500K/año licencia + infra             | ❌ $100K-1M+/año licencia            | ⚠️ $0.50-1.50/h/task (~$360-1K/mes) | ⚠️ $1-5/h/pipeline (~$700-3.5K/mes) |

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

---

## ⚠️ CONSECUENCIAS

### Positivas

- Agnosticidad tecnológica total - portable entre clouds y bases de datos
- Integración nativa con infraestructura Kafka existente
- CDC real-time (`<100ms`) sin impacto en base de datos origen
- Costos optimizados ($0 licencia + infraestructura compartida)
- Schema evolution con Schema Registry (Avro, Protobuf)
- Escalabilidad horizontal probada en producción
- Comunidad activa + soporte Red Hat enterprise disponible
- Open source con visibilidad completa del código

### Negativas (Riesgos y Mitigaciones)

- **Curva de aprendizaje Kafka/Debezium:** mitigado con capacitación del equipo
- **Complejidad operativa:** mitigado con monitoreo proactivo (JMX + Kafka metrics)
- **Configuración específica por base de datos:** mitigado con automatización Terraform/IaC y documentación interna
- **Snapshot inicial lento:** mitigado con planificación en ventanas de bajo tráfico y configuración de SMT

---

## 📚 REFERENCIAS

- [Debezium](https://debezium.io/)
- [Debezium GitHub](https://github.com/debezium/debezium)
- [Debezium Connectors](https://debezium.io/documentation/reference/stable/connectors/index.html)
- [Kafka Connect](https://kafka.apache.org/documentation/#connect)
- [Oracle GoldenGate](https://www.oracle.com/integration/goldengate/)
- [AWS DMS](https://aws.amazon.com/dms/)
- [Azure Data Factory](https://azure.microsoft.com/en-us/services/data-factory/)
- [Change Data Capture Patterns](https://www.confluent.io/blog/cdc-change-data-capture-patterns/)
- [Debezium vs Alternatives](https://debezium.io/documentation/faq/#how-does-debezium-compare)
