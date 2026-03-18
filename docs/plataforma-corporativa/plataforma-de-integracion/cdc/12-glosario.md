---
sidebar_position: 12
title: Glosario
description: Términos y acrónimos del servicio CDC con Debezium sobre Kafka Connect.
---

# 12. Glosario

## Términos del Dominio

| Término                    | Definición                                                                                                                                   |
| -------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| **CDC**                    | Change Data Capture. Patrón que captura cada modificación (INSERT/UPDATE/DELETE) en una base de datos y la publica como evento.              |
| **WAL**                    | Write-Ahead Log. Registro de transacciones de PostgreSQL del que Debezium lee los cambios mediante replicación lógica.                       |
| **Binlog**                 | Binary Log de MySQL/MariaDB. Equivalente al WAL; registro ordenado de todos los cambios con que Debezium implementa CDC en MySQL.            |
| **Replication Slot**       | Mecanismo de PostgreSQL que retiene el WAL hasta que el consumidor (Debezium) lo haya procesado, evitando pérdida de cambios.                |
| **Snapshot**               | Fotografía consistente del estado actual de una tabla, tomada por Debezium al registrar un nuevo conector antes de iniciar el streaming.     |
| **Streaming CDC**          | Fase continua tras el snapshot donde Debezium lee y publica cambios en tiempo real desde el WAL/binlog.                                      |
| **Conector**               | Unidad de configuración de Kafka Connect que define qué BD/tablas monitorear, cómo conectarse y cómo transformar los mensajes.               |
| **Worker**                 | Proceso Kafka Connect que ejecuta uno o más conectores. En esta implementación, un único worker como contenedor Docker en una instancia EC2. |
| **Task**                   | Subunidad de un conector que realiza la lectura efectiva. Un conector puede tener una o varias tasks para paralelismo.                       |
| **Offset**                 | Posición de lectura del conector en el log de transacciones (LSN en PostgreSQL, GTID en MySQL). Persistido en `connect-offsets`.             |
| **LSN**                    | Log Sequence Number. Identificador único de una posición en el WAL de PostgreSQL.                                                            |
| **GTID**                   | Global Transaction ID. Identificador único de transacción en MySQL, usado por Debezium para rastrear la posición de lectura.                 |
| **before / after**         | Campos del mensaje JSON de Debezium que contienen el estado de la fila antes y después del cambio, respectivamente.                          |
| **op**                     | Campo del mensaje JSON que indica el tipo de operación: `c` (create/INSERT), `u` (update/UPDATE), `d` (delete/DELETE), `r` (read/snapshot).  |
| **ts_ms**                  | Timestamp en milisegundos del momento en que ocurrió el cambio en la BD, incluido en el mensaje JSON de Debezium.                            |
| **SMT**                    | Single Message Transform. Plugins de Kafka Connect que transforman mensajes en vuelo: enmascaramiento, filtrado, routing, renombrado.        |
| **Topic Prefix**           | Valor de configuración `topic.prefix` del conector; primera parte del nombre del topic resultante (`<prefix>.<schema>.<tabla>`).             |
| **Enmascaramiento PII**    | Aplicación del SMT `MaskField` para sustituir datos de identificación personal por un valor opaco antes de publicar en Kafka.                |
| **connect-offsets**        | Topic Kafka interno que almacena la posición de lectura de cada conector (durabilidad igual a la del clúster Kafka).                         |
| **connect-schema-changes** | Topic Kafka interno que registra el historial de cambios de esquema de las tablas monitoreadas.                                              |
| **connect-status**         | Topic Kafka interno con el estado actual de conectores y tasks (RUNNING, PAUSED, FAILED).                                                    |

## Acrónimos

| Acrónimo | Significado                         |
| -------- | ----------------------------------- |
| **CDC**  | Change Data Capture                 |
| **WAL**  | Write-Ahead Log                     |
| **LSN**  | Log Sequence Number                 |
| **GTID** | Global Transaction ID               |
| **SMT**  | Single Message Transform            |
| **ECS**  | Elastic Container Service (AWS)     |
| **PII**  | Personally Identifiable Information |
| **RTO**  | Recovery Time Objective             |
| **RPO**  | Recovery Point Objective            |
| **IaC**  | Infrastructure as Code              |
| **REST** | Representational State Transfer     |
| **JSON** | JavaScript Object Notation          |
