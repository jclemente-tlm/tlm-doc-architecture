---
sidebar_position: 8
title: Conceptos Transversales
description: Patrones y configuraciones aplicadas transversalmente en el servicio CDC con Debezium.
---

# 8. Conceptos Transversales

## CDC Log-Based vs. Polling

Debezium usa **log-based CDC**: lee los transaction logs de la base de datos (WAL en PostgreSQL, binlog en MySQL, CDC tables en SQL Server) en lugar de hacer consultas periódicas. Esto garantiza:

- **Sin impacto en la BD origen:** no ejecuta queries adicionales sobre las tablas.
- **Latencia baja:** el cambio se captura en milisegundos tras el commit, no en el siguiente intervalo de polling.
- **Completitud:** captura todos los cambios, incluyendo los que no sobreviven a un polling tardío (filas borradas entre dos polls).

## Formato JSON y Estructura `before`/`after`

Cada mensaje publicado en Kafka contiene el estado `before` y `after` de la fila, más metadata del cambio:

```json
{
  "before": { "id": 10, "estado": "ABIERTO" },
  "after": { "id": 10, "estado": "CERRADO" },
  "op": "u",
  "ts_ms": 1710000000000,
  "source": {
    "db": "base-ops",
    "schema": "public",
    "table": "operaciones"
  }
}
```

Con `schemas.enable=false` (configuración actual), el schema no se embebe en el mensaje. Los consumidores deben conocer la estructura de la tabla para deserializar correctamente.

> Cuando se implemente Schema Registry (DT-03 de mensajería), se evaluará migrar a Avro para validación de contratos.

## Gestión de Offsets y Garantía At-Least-Once

Los offsets de lectura (posición en el WAL/binlog) se almacenan en el topic `connect-offsets` de Kafka. Tras un reinicio del worker, Debezium reanuda la lectura desde el último offset confirmado.

- La garantía de entrega es **at-least-once**: un evento puede publicarse más de una vez si el worker falla entre la publicación y la confirmación del offset.
- Los consumidores deben ser **idempotentes** (procesar el mismo evento dos veces sin efectos adversos).
- Para identificar duplicados, usar el campo `ts_ms` + clave primaria de la fila como identificador único del evento.

## Enmascaramiento de Datos PII (SMT MaskField)

Las columnas que contienen datos de identificación personal (DNI, email, teléfono, cuenta bancaria) deben enmascararse antes de publicarse en Kafka mediante el SMT `MaskField`:

```json
"transforms": "maskPII",
"transforms.maskPII.type": "org.apache.kafka.connect.transforms.MaskField$Value",
"transforms.maskPII.fields": "dni,email,telefono",
"transforms.maskPII.replacement": "***MASKED***"
```

La lista de columnas a enmascarar por tabla es responsabilidad del equipo de Seguridad y debe revisarse antes del registro de cada conector.

## Observabilidad

### Métricas → Mimir/Grafana (JMX Exporter)

El worker Kafka Connect expone métricas JMX que el agente JMX Exporter convierte al formato Prometheus. Métricas clave:

| Métrica                                                       | Descripción                                            |
| ------------------------------------------------------------- | ------------------------------------------------------ |
| `debezium_metrics_NumberOfCommittedTransactions`              | Transacciones capturadas y confirmadas por conector    |
| `debezium_metrics_MilliSecondsBehindSource`                   | Lag en ms entre el cambio en la BD y la publicación    |
| `kafka_connect_connector_task_status`                         | Estado de cada tarea de conector (0=RUNNING, 1=FAILED) |
| `kafka_connect_source_task_metrics_source_record_poll_total`  | Total de registros leídos desde la BD                  |
| `kafka_connect_source_task_metrics_source_record_write_total` | Total de registros publicados en Kafka                 |

### Alertas Clave en Grafana

| Alerta                        | Condición                                              |
| ----------------------------- | ------------------------------------------------------ |
| Conector en estado FAILED     | `task_status != 0` por más de 2 minutos                |
| Lag CDC alto                  | `MilliSecondsBehindSource > 5000` por más de 5 minutos |
| Worker sin conectores activos | Todos los tasks en FAILED o PAUSED                     |

### Logs → Loki

El worker emite logs por `stdout`. Fluent Bit (sidecar en el contenedor Docker) los renvía a Loki. Labels indexados: `job=debezium`, `connector`, `env`.

## Replication Slot en PostgreSQL

Debezium requiere un **replication slot lógico** en PostgreSQL para leer el WAL. El slot persiste los cambios hasta que Debezium los confirma, lo que implica:

- Si el worker se detiene por mucho tiempo, el slot acumula WAL inflando el disco de la BD. **Monitorear `pg_replication_slots`.**
- El slot debe crearse con `wal_level=logical` habilitado en la BD origen (parámetro de servidor).
- Si el slot se invalida (BD reiniciada sin el slot), el conector debe recrearse con `snapshot.mode=initial`.

```sql
-- Verificar estado del replication slot
SELECT slot_name, active, restart_lsn, confirmed_flush_lsn
FROM pg_replication_slots
WHERE slot_name = 'debezium_base_ops';
```
