---
sidebar_position: 1
title: Introducción y Objetivos
description: Objetivos, requisitos y partes interesadas del servicio de Change Data Capture basado en Debezium.
---

# 1. Introducción y Objetivos

El **servicio de Change Data Capture (CDC)** captura en tiempo real los cambios en bases de datos corporativas y los publica como eventos en la plataforma de mensajería Kafka. Está implementado con **Debezium** sobre **Kafka Connect**, desplegado como contenedor Docker en AWS EC2 (ADR-009).

Debezium lee directamente los **transaction logs** de las bases de datos origen (sin consultas adicionales), garantizando baja latencia y sin impacto en el rendimiento de la base de datos.

## Capacidades Clave

| Capacidad                    | Descripción                                                                                          |
| ---------------------------- | ---------------------------------------------------------------------------------------------------- |
| Captura de cambios log-based | Lee transaction logs de la BD; sin polling, sin triggers, sin impacto en la BD origen                |
| Publicación en Kafka         | Cada cambio (INSERT, UPDATE, DELETE) se publica como evento JSON en un topic Kafka dedicado          |
| Snapshot inicial             | Al arrancar el conector, Debezium toma un snapshot consistente de la tabla antes de iniciar el CDC   |
| Transformaciones SMT         | Single Message Transforms para filtrar columnas, renombrar campos o enriquecer mensajes en tránsito  |
| Multi-base de datos          | Soporte para PostgreSQL, MySQL, SQL Server, MongoDB, Oracle mediante conectores oficiales            |
| Formato JSON                 | Mensajes publicados en formato JSON con estructura `before`/`after`/`op` estándar de Debezium        |
| Gestión de offsets           | Los offsets de lectura se almacenan en Kafka (`connect-offsets`) para garantizar exactamente-una-vez |
| Observabilidad               | Métricas JMX exportadas a Prometheus; logs estructurados a Loki                                      |

## Requisitos de Calidad

| Atributo             | Objetivo                             | Crítico             |
| -------------------- | ------------------------------------ | ------------------- |
| Latencia de captura  | `< 100ms p95`                        | `< 500ms`           |
| Throughput           | `> 10,000 eventos/s`                 | `> 5,000 eventos/s` |
| Disponibilidad       | `99.9%`                              | `99.5%`             |
| Pérdida de eventos   | Cero                                 | Cero                |
| Tiempo de reconexión | `< 30s` tras reinicio del contenedor | `< 60s`             |

## Partes Interesadas

| Rol                    | Interés                                                                           |
| ---------------------- | --------------------------------------------------------------------------------- |
| Equipo de Plataforma   | Operación, despliegue y monitoreo de conectores Debezium                          |
| Equipo de Arquitectura | Estándares de conectores, formato de mensajes y naming de topics CDC              |
| Equipos de Desarrollo  | Consumo de eventos CDC desde Kafka para sincronización o event-driven logic       |
| Equipo de Datos        | Ingesta de eventos CDC en data lake o data warehouse para analítica               |
| Equipo de Seguridad    | Permisos de replicación en BD, credenciales de conexión y datos sensibles en logs |
| DBA / Base de Datos    | Configuración de replicación lógica (slot, WAL level) en bases de datos origen    |

## Decisión de Tecnología

Debezium fue seleccionado como solución estándar de CDC en [ADR-009](../../../adrs/adr-009-debezium-cdc.md).
