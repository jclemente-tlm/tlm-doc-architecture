---
sidebar_position: 6
title: Vista de Tiempo de Ejecución
description: Flujos de publicación, consumo y resiliencia de la plataforma de mensajería Kafka KRaft.
---

# 6. Vista de Tiempo de Ejecución

## Flujo 1: Publicación de Mensaje (Producer)

```mermaid
sequenceDiagram
    participant P as Productor
    participant B1 as Broker-1 (líder)
    participant B2 as Broker-2 (réplica)
    participant C1 as Controller-1

    P->>B1: Metadata request (¿quién es líder del topic?)
    B1->>C1: Consulta metadata
    C1-->>B1: Metadata actualizada
    B1-->>P: Leader = Broker-1, partición 0
    P->>B1: ProduceRequest (acks=1, mensaje)
    B1->>B2: Replicación asíncrona
    B1-->>P: Ack (offset asignado)
    alt acks=all configurado
        B1->>B2: Replicación síncrona
        B2-->>B1: Confirmación de réplica
        B1-->>P: Ack (offset confirmado en todas las ISR)
    end
```

> `acks=1` es el valor por defecto. Para eventos críticos (pagos, auditoría) usar `acks=all` + `min.insync.replicas=2`.

## Flujo 2: Consumo de Mensajes (Consumer Group)

```mermaid
sequenceDiagram
    participant C1 as Consumer A (instancia 1)
    participant C2 as Consumer A (instancia 2)
    participant B1 as Broker-1
    participant B2 as Broker-2
    participant CG as Group Coordinator

    C1->>CG: JoinGroup request
    C2->>CG: JoinGroup request
    CG-->>C1: Asignación: partición 0, 1
    CG-->>C2: Asignación: partición 2, 3
    loop Polling continuo
        C1->>B1: FetchRequest (partición 0, offset N)
        B1-->>C1: Mensajes [N..N+k]
        C1->>CG: CommitOffset (partición 0, offset N+k)
        C2->>B2: FetchRequest (partición 2, offset M)
        B2-->>C2: Mensajes [M..M+j]
        C2->>CG: CommitOffset (partición 2, offset M+j)
    end
```

> Cada consumer group mantiene su propio offset por partición. Múltiples grupos pueden consumir el mismo topic de forma independiente.

## Flujo 3: Elección de Líder KRaft (Failover de Controller)

```mermaid
sequenceDiagram
    participant C1 as Controller-1 (líder activo)
    participant C2 as Controller-2
    participant B1 as Broker-1
    participant B2 as Broker-2

    Note over C1: Fallo o reinicio de Controller-1
    C2->>C2: Detecta timeout de heartbeat (election.timeout.ms)
    C2->>C2: Incrementa epoch, inicia elección Raft
    C2-->>B1: Notifica nuevo líder del quórum
    C2-->>B2: Notifica nuevo líder del quórum
    B1->>C2: Confirma registro al nuevo controller activo
    B2->>C2: Confirma registro al nuevo controller activo
    Note over C2: Controller-2 asume como líder del quórum
    Note over B1,B2: Tráfico de producers/consumers no interrumpido
```

> La elección KRaft ocurre en el plano de control (metadatos). El tráfico de datos (produce/consume) continúa sin interrupción mientras haya al menos un broker disponible.

## Manejo de Errores por Flujo

| Escenario                         | Respuesta del Sistema                                                                   |
| --------------------------------- | --------------------------------------------------------------------------------------- |
| Broker-1 cae (partición líder)    | Controller promueve réplica en Broker-2 como líder; reconexión automática del productor |
| Fallo en replicación inter-broker | Réplica sale de ISR; broker degradado no recibe escrituras hasta resincronización       |
| Consumer falla sin commit         | Al reiniciar, retoma desde el último offset confirmado (at-least-once delivery)         |
| Quórum KRaft sin mayoría          | Clúster rechaza escrituras de metadatos; datos existentes siguen siendo legibles        |
| Disco lleno en broker             | Broker rechaza nuevas escrituras; alerta en Grafana por métrica `kafka_log_size`        |
