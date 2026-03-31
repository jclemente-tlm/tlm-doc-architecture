---
sidebar_position: 5
title: Vista de Bloques de Construcción
description: Descomposición estática de la plataforma de mensajería Kafka KRaft.
---

# 5. Vista de Bloques de Construcción

## Nivel 1: Sistema en Contexto

```mermaid
graph TD
    PROD[Servicios Productores] -->|produce| MB[Mensajería\nKafka KRaft]
    MB -->|consume| CONS[Servicios Consumidores]
    ADMIN[Equipo de Plataforma\nAdmin CLI] -->|gestión| MB
    MB -->|métricas / logs| OBS[Observabilidad]
```

## Nivel 2: Componentes Internos del Clúster

| Componente       | Tecnología / Imagen                   | Responsabilidad                                                                   |
| ---------------- | ------------------------------------- | --------------------------------------------------------------------------------- |
| **Controller-1** | `apache/kafka:3.7` — rol `controller` | Participa en quórum KRaft; gestiona metadata log y elección de líder de partición |
| **Controller-2** | `apache/kafka:3.7` — rol `controller` | Réplica del quórum KRaft; garantiza disponibilidad de metadatos ante fallo        |
| **Broker-1**     | `apache/kafka:3.7` — rol `broker`     | Almacena particiones; atiende producers y consumers; replica hacia Broker-2       |
| **Broker-2**     | `apache/kafka:3.7` — rol `broker`     | Réplica de particiones de Broker-1; asume liderazgo ante fallo del otro broker    |
| **JMX Exporter** | `bitnami/jmx-exporter` (sidecar)      | Exporta métricas JMX de Kafka en formato Prometheus por cada instancia EC2        |
| **Fluent Bit**   | `fluent/fluent-bit` (agente en EC2)   | Recolecta stdout de contenedores Kafka y los envía a Loki                         |

## Relación Controller ↔ Broker

```mermaid
graph LR
    subgraph Quórum KRaft
        C1[Controller-1\nEC2-ctrl-1]
        C2[Controller-2\nEC2-ctrl-2]
        C1 <-->|Raft consensus| C2
    end

    subgraph Capa de datos
        B1[Broker-1\nEC2-broker-1]
        B2[Broker-2\nEC2-broker-2]
        B1 <-->|replicación| B2
    end

    C1 -->|metadata fetch| B1
    C1 -->|metadata fetch| B2
    C2 -->|metadata fetch| B1
    C2 -->|metadata fetch| B2
```

## Estructura de Topics

| Elemento              | Configuración        | Descripción                                                          |
| --------------------- | -------------------- | -------------------------------------------------------------------- |
| `partitions`          | `≥ 4` por topic      | Paralelismo de consumo; ajustable según throughput esperado          |
| `replication.factor`  | `2`                  | Una réplica por broker; sin pérdida de datos ante fallo de un broker |
| `min.insync.replicas` | `1`                  | Mínimo de réplicas en sincronía para aceptar escrituras              |
| `retention.ms`        | `604800000` (7 días) | Retención por defecto; configurable por topic                        |
| `cleanup.policy`      | `delete`             | Limpieza por tiempo/tamaño; `compact` para topics de estado          |
