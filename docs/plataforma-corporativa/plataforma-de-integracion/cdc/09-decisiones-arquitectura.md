---
sidebar_position: 9
title: Decisiones de Arquitectura
description: Registro de decisiones arquitectónicas del servicio CDC con Debezium.
---

# 9. Decisiones de Arquitectura

## Decisión Principal

| Campo          | Valor                                                              |
| -------------- | ------------------------------------------------------------------ |
| **ADR**        | ADR-009 — Adopción de Debezium para Captura de Cambios en BD (CDC) |
| **Estado**     | Aceptado                                                           |
| **Fecha**      | Febrero 2026                                                       |
| **Referencia** | [ADR-009](../../../adrs/adr-009-debezium-cdc.md)                   |

## Registro de Decisiones de Componente

### DEC-01 — Formato JSON sin Schema Registry

| Campo             | Valor                                                                                                                                                                                                            |
| ----------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **ID**            | DEC-01                                                                                                                                                                                                           |
| **Estado**        | Aceptado                                                                                                                                                                                                         |
| **Contexto**      | Al adoptar Debezium se evaluó el uso de Avro con Schema Registry (Confluent) para validar contratos de mensajes.                                                                                                 |
| **Decisión**      | Usar formato JSON con `schemas.enable=false`, sin Schema Registry.                                                                                                                                               |
| **Consecuencias** | ✅ Sin dependencia de Confluent Platform. ✅ Menor complejidad operacional. ⚠️ Consumidores deben conocer el esquema de la tabla fuera de banda. ⚠️ Sin validación automática de contrato al cambiar el esquema. |

---

### DEC-02 — Despliegue como contenedor Docker en EC2

| Campo             | Valor                                                                                                                                                                                                                                                                               |
| ----------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **ID**            | DEC-02                                                                                                                                                                                                                                                                              |
| **Estado**        | Aceptado                                                                                                                                                                                                                                                                            |
| **Contexto**      | Debezium/Kafka Connect no requiere acceso directo a disco local como los brokers Kafka, pero se optó por mantener el mismo modelo operacional Docker-en-EC2 usado en el clúster Kafka para simplificar operaciones y troubleshooting.                                               |
| **Decisión**      | Desplegar el Kafka Connect worker como contenedor Docker en una instancia EC2 dedicada.                                                                                                                                                                                             |
| **Consecuencias** | ✅ Modelo operacional uniforme con los nodos Kafka (Docker + EC2). ✅ Reinicio automático configurado por Docker restart policy (`--restart=unless-stopped`). ✅ Acceso SSH directo para troubleshooting. ⚠️ Requiere gestión del ciclo de vida de la instancia EC2 (AMI, parches). |

---

### DEC-03 — Topic Naming por Defecto de Debezium (`<bd>.<schema>.<tabla>`)

| Campo             | Valor                                                                                                                                                                                                                    |
| ----------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **ID**            | DEC-03                                                                                                                                                                                                                   |
| **Estado**        | Aceptado                                                                                                                                                                                                                 |
| **Contexto**      | Un topic naming personalizado requeriría un SMT `RerouteByField` por cada tabla, aumentando la complejidad de configuración.                                                                                             |
| **Decisión**      | Usar el naming por defecto de Debezium: `<topic.prefix>.<schema>.<tabla>` donde `topic.prefix` es el nombre de la BD.                                                                                                    |
| **Consecuencias** | ✅ Sin configuración adicional por tabla. ✅ El nombre del topic es autodescriptivo y trazable hasta la tabla origen. ⚠️ El naming incluye el nombre del schema SQL, lo que expone detalles de la BD a los consumidores. |

---

### DEC-04 — Offsets en Kafka (no base de datos externa)

| Campo             | Valor                                                                                                                                                                                                                                                                                      |
| ----------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **ID**            | DEC-04                                                                                                                                                                                                                                                                                     |
| **Estado**        | Aceptado                                                                                                                                                                                                                                                                                   |
| **Contexto**      | Los offsets de lectura del WAL podrían almacenarse en una base de datos externa (RDS, Redis) para mayor durabilidad.                                                                                                                                                                       |
| **Decisión**      | Almacenar offsets en el topic Kafka `connect-offsets` con replication factor 3.                                                                                                                                                                                                            |
| **Consecuencias** | ✅ Sin dependencia de infraestructura adicional. ✅ Los offsets tienen la misma durabilidad que Kafka (replicación 3x). ✅ Arquitectura cohesiva: todos los datos del sistema CDC están en Kafka. ⚠️ La pérdida total del clúster Kafka implica perder los offsets (requiere re-snapshot). |
