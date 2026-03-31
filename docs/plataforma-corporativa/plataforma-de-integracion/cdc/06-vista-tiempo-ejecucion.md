---
sidebar_position: 6
title: Vista de Tiempo de Ejecución
description: Flujos de captura de cambios, snapshot inicial y recuperación ante fallos del servicio CDC.
---

# 6. Vista de Tiempo de Ejecución

## Flujo 1: Snapshot Inicial y Arranque del Conector

```mermaid
sequenceDiagram
    participant OPS as Equipo Plataforma (IaC)
    participant KC as Kafka Connect Worker
    participant PG as PostgreSQL (BD origen)
    participant KB as Kafka Brokers

    OPS->>KC: POST /connectors (config JSON)
    KC->>PG: Crear replication slot (snapshot.mode=initial)
    PG-->>KC: Slot creado + LSN inicial
    KC->>PG: SELECT * FROM tabla (snapshot consistente)
    loop Por cada fila
        KC->>KB: Produce evento op=r (read) en base-ops.public.tabla
    end
    KC->>KB: Guardar LSN en connect-offsets
    Note over KC,PG: Snapshot completado — inicia streaming CDC
    loop Streaming continuo
        PG->>KC: Cambio en WAL (INSERT/UPDATE/DELETE)
        KC->>KB: Produce evento op=c/u/d en base-ops.public.tabla
        KC->>KB: Actualizar offset en connect-offsets
    end
```

> El snapshot inicial puede omitirse con `snapshot.mode=never` si la tabla ya fue cargada previamente.

## Flujo 2: Captura de Cambio (Streaming CDC)

```mermaid
sequenceDiagram
    participant APP as Aplicación
    participant PG as PostgreSQL
    participant KC as Kafka Connect\n(Debezium)
    participant KB as Kafka Brokers
    participant CONS as Servicio Consumidor

    APP->>PG: UPDATE operaciones SET estado='CERRADO' WHERE id=42
    PG->>PG: Escribe en WAL (LSN + cambio)
    PG->>KC: Envía registro WAL vía replication slot
    KC->>KC: Aplica SMT (enmascaramiento, filtros)
    KC->>KB: Produce mensaje JSON en base-ops.public.operaciones
    Note right of KC: {"before":{...}, "after":{...}, "op":"u"}
    KC->>KB: Actualiza offset en connect-offsets (LSN confirmado)
    CONS->>KB: Poll (FetchRequest)
    KB-->>CONS: Mensaje JSON con el cambio
    CONS->>CONS: Procesa evento (sincroniza, notifica, audita)
```

## Flujo 3: Recuperación tras Fallo del Worker

```mermaid
sequenceDiagram
    participant EC2 as EC2 Instance
    participant KC as Kafka Connect Worker
    participant KB as Kafka Brokers
    participant PG as PostgreSQL

    Note over KC: Worker falla o Docker reinicia el contenedor
    EC2->>KC: Nuevo contenedor arranca
    KC->>KB: Lee último offset desde connect-offsets
    KB-->>KC: LSN = 1234567 (último confirmado)
    KC->>PG: Reanuda lectura del WAL desde LSN 1234567
    PG-->>KC: Cambios desde LSN 1234567 (sin duplicar eventos ya publicados)
    KC->>KB: Reanuda publicación de eventos
    Note over KC: Recuperación sin pérdida de eventos (at-least-once)
```

> La garantía es **at-least-once**: en caso de fallo entre publicación y confirmación de offset, un evento puede publicarse dos veces. Los consumidores deben ser idempotentes.

## Manejo de Errores

| Escenario                                | Respuesta del Sistema                                                                      |
| ---------------------------------------- | ------------------------------------------------------------------------------------------ |
| BD origen no disponible                  | Conector reintenta con backoff exponencial; alerta si supera `max.retries`                 |
| Replication slot caído / invalidado      | Conector falla con `FAILED`; requiere intervención manual (recrear slot y snapshot)        |
| Kafka no disponible                      | Worker bufferiza cambios en memoria hasta `producer.max.block.ms`; luego falla y reintenta |
| Cambio de esquema en tabla origen        | Debezium detecta el cambio, registra en `connect-schema-changes` y continúa el streaming   |
| Contenedor reiniciado (OOM u otro fallo) | Worker reanuda desde el último offset confirmado en Kafka (`connect-offsets`)              |
| Columna PII publicada sin enmascarar     | Alerta de auditoría; revisión de configuración SMT del conector afectado                   |
