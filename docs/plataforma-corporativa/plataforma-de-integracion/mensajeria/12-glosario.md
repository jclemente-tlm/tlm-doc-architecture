---
sidebar_position: 12
title: Glosario
description: Términos y acrónimos de la plataforma de mensajería corporativa basada en Apache Kafka KRaft.
---

# 12. Glosario

## Términos del Dominio

| Término             | Definición                                                                                                                                                                                      |
| ------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Kafka**           | Plataforma de mensajería distribuida y event streaming. Almacena mensajes en logs particionados y replicados.                                                                                   |
| **KRaft**           | Modo de consenso nativo de Kafka basado en el algoritmo Raft. Reemplaza ZooKeeper para gestionar metadatos del clúster desde Kafka 3.3.                                                         |
| **Controller**      | Nodo Kafka con rol de control: gestiona el metadata log, coordina elecciones de líderes de partición y mantiene el quórum Raft. No almacena datos de particiones.                               |
| **Broker**          | Nodo Kafka con rol de datos: almacena particiones, atiende a producers y consumers, y replica mensajes entre brokers.                                                                           |
| **Topic**           | Canal lógico de mensajes en Kafka, identificado por nombre. Organizado en particiones. Equivalente a una "cola" persistente y múltiple.                                                         |
| **Partición**       | Subdivisión de un topic. Unidad de paralelismo y replicación. Cada partición tiene un broker líder y cero o más réplicas en otros brokers.                                                      |
| **Producer**        | Servicio o componente que publica mensajes en un topic de Kafka.                                                                                                                                |
| **Consumer**        | Servicio o componente que lee mensajes de uno o más topics de Kafka.                                                                                                                            |
| **Consumer Group**  | Conjunto de instancias de un mismo consumidor que se reparten las particiones de un topic para consumo paralelo. Kafka garantiza que cada partición es leída por una única instancia del grupo. |
| **Offset**          | Posición numérica de un mensaje dentro de una partición. El consumer group gestiona su propio offset por partición para reanudar el consumo tras reinicios.                                     |
| **ISR**             | In-Sync Replicas. Conjunto de réplicas que están al día con el líder de una partición. Solo réplicas en ISR pueden convertirse en líderes.                                                      |
| **Leader**          | Réplica principal de una partición. Atiende todas las lecturas y escrituras. Elegida por el controller cuando el líder actual falla.                                                            |
| **Replica**         | Copia de una partición en un broker distinto al líder. Garantiza durabilidad ante fallos de nodos.                                                                                              |
| **Quórum Raft**     | Mayoría de nodos necesaria para que el clúster de controllers acepte cambios de metadatos. Con 2 controllers, el quórum requiere 2/2 nodos activos.                                             |
| **Metadata Log**    | Log interno de Kafka KRaft (`__cluster_metadata`) donde se persisten todos los cambios de metadatos del clúster (topics, particiones, miembros).                                                |
| **Consumer Lag**    | Diferencia entre el offset más reciente de una partición y el offset confirmado por un consumer group. Indica cuántos mensajes están pendientes de procesar.                                    |
| **Retention**       | Tiempo o tamaño máximo de retención de mensajes en un topic. Transcurrido el tiempo o alcanzado el tamaño, los mensajes más antiguos se eliminan.                                               |
| **Compaction**      | Política de limpieza alternativa a `delete`. Kafka conserva solo el mensaje más reciente por clave, permitiendo usar el topic como almacén de estado.                                           |
| **SASL/SCRAM**      | Mecanismo de autenticación estándar para Kafka. SCRAM-SHA-512 usa un intercambio de desafío-respuesta sin transmitir la contraseña en claro.                                                    |
| **ACL**             | Access Control List. Regla que otorga o deniega operaciones (produce, consume, describe) sobre un topic o prefijo de topic a un usuario o grupo.                                                |
| **Schema Registry** | Servicio externo (no implementado aún — DT-03) que almacena y valida los esquemas (Avro, Protobuf, JSON Schema) de los mensajes Kafka.                                                          |
| **Event streaming** | Patrón de arquitectura donde los eventos son el principal mecanismo de comunicación entre servicios. Kafka es la infraestructura central de este patrón.                                        |

## Acrónimos

| Acrónimo | Significado                                        |
| -------- | -------------------------------------------------- |
| `KRaft`  | Kafka Raft metadata mode                           |
| `ISR`    | In-Sync Replicas                                   |
| `ACL`    | Access Control List                                |
| `SASL`   | Simple Authentication and Security Layer           |
| `SCRAM`  | Salted Challenge Response Authentication Mechanism |
| `JMX`    | Java Management Extensions                         |
| `EBS`    | Elastic Block Store (AWS)                          |
| `EC2`    | Elastic Compute Cloud (AWS)                        |
| `AZ`     | Availability Zone (AWS)                            |
| `VPC`    | Virtual Private Cloud (AWS)                        |
| `CDC`    | Change Data Capture                                |
| `SLA`    | Service Level Agreement                            |
| `RTO`    | Recovery Time Objective                            |
