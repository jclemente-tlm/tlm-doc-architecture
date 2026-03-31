---
sidebar_position: 1
title: Introducción y Objetivos
description: Objetivos, requisitos y partes interesadas de la plataforma de mensajería basada en Apache Kafka KRaft.
---

# 1. Introducción y Objetivos

La **plataforma de mensajería corporativa** provee comunicación asíncrona, desacoplada y persistente entre servicios. Está implementada con **Apache Kafka en modo KRaft** (sin ZooKeeper), desplegado como contenedores Docker sobre instancias EC2 en AWS.

La topología de producción consta de **2 Controllers** y **2 Brokers**, cada uno ejecutándose como contenedor Docker en una instancia EC2 dedicada.

## Capacidades Clave

| Capacidad                    | Descripción                                                                               |
| ---------------------------- | ----------------------------------------------------------------------------------------- |
| Mensajería asíncrona         | Publicación y consumo de mensajes con semántica at-least-once y exactly-once configurable |
| Desacoplamiento de servicios | Productores y consumidores operan de forma independiente sin conocerse entre sí           |
| Event streaming              | Flujo continuo de eventos con retención configurable para replay y auditoría              |
| Tolerancia a fallos          | Replicación de particiones entre brokers; sin punto único de falla                        |
| Multi-tenant por topic       | Aislamiento lógico mediante convención de nombrado de topics por dominio/servicio         |
| KRaft (sin ZooKeeper)        | Metadatos del clúster gestionados mediante consenso Raft nativo; menor operatividad       |
| Observabilidad               | Métricas JMX exportadas a Prometheus, logs estructurados a Loki, trazas a Tempo           |

## Requisitos de Calidad

| Atributo              | Objetivo                   | Crítico                |
| --------------------- | -------------------------- | ---------------------- |
| Throughput producer   | `> 50,000 msg/s` por topic | `> 20,000 msg/s`       |
| Latencia end-to-end   | `< 20ms p95`               | `< 50ms`               |
| Disponibilidad        | `99.9%`                    | `99.5%`                |
| Durabilidad           | `replication.factor=2`     | Sin pérdida de datos   |
| Retención de mensajes | `7 días` por defecto       | Configurable por topic |

## Partes Interesadas

| Rol                    | Interés                                                             |
| ---------------------- | ------------------------------------------------------------------- |
| Equipo de Plataforma   | Operación, escalado y monitoreo del clúster Kafka                   |
| Equipo de Arquitectura | Estándares de topics, particionado y convenciones de nombrado       |
| Equipos de Desarrollo  | Publicación y consumo de mensajes; configuración de consumer groups |
| Equipo de Seguridad    | Autenticación SASL, cifrado TLS y políticas de ACL                  |
| Equipo de Datos        | Retención, compactación y acceso a eventos para analítica e ingesta |

## Decisión de Tecnología

Apache Kafka con modo KRaft fue seleccionado como plataforma de mensajería corporativa en [ADR-008](../../../adrs/adr-008-kafka-mensajeria-asincrona.md).
