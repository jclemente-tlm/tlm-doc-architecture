---
sidebar_position: 9
title: Decisiones de Arquitectura
description: Decisiones arquitectónicas de la plataforma de mensajería Kafka KRaft.
---

# 9. Decisiones de Arquitectura

## Decisión Principal

| ADR     | Decisión                                             | Estado                 | Referencia                                                     |
| ------- | ---------------------------------------------------- | ---------------------- | -------------------------------------------------------------- |
| ADR-008 | Apache Kafka como plataforma de mensajería asíncrona | Aceptado (Agosto 2025) | [ADR-008](../../../adrs/adr-008-kafka-mensajeria-asincrona.md) |

Ver el ADR completo para la comparativa de alternativas (Amazon SQS/SNS, Amazon MSK, RabbitMQ, Azure Service Bus, Redpanda).

## Decisiones Locales a la Plataforma de Mensajería

### DEC-01: Modo KRaft sin ZooKeeper

- **Estado**: Aceptado
- **Contexto**: Kafka históricamente dependía de ZooKeeper para gestionar metadatos del clúster. Esto añade un componente operativo adicional con su propio ciclo de vida, monitoreo y escalado. Desde Kafka 3.3, el modo KRaft está disponible en producción y elimina esta dependencia.
- **Decisión**: Desplegar Kafka en modo KRaft con 2 controllers dedicados. ZooKeeper no forma parte de la infraestructura.
- **Consecuencias**: Menor superficie operativa (4 nodos en lugar de 4+3). Elección de líder más rápida (< 30s vs minutos con ZooKeeper). Con 2 controllers no se tolera el fallo simultáneo de ambos para operaciones de metadatos; mitigado escalando a 3 controllers en la hoja de ruta (DT-01).

### DEC-02: Docker en EC2 en lugar de ECS Fargate

- **Estado**: Aceptado
- **Contexto**: El resto de la plataforma corporativa usa ECS Fargate. Sin embargo, Kafka tiene requerimientos específicos de red y disco que ECS Fargate no cubre adecuadamente: acceso a volúmenes EBS de alto rendimiento, configuración de red de bajo nivel (`advertised.listeners` por IP privada) y control sobre la JVM (heap, GC).
- **Decisión**: Desplegar cada nodo Kafka como contenedor Docker en una instancia EC2 dedicada con volumen EBS gp3 montado.
- **Consecuencias**: Se mantiene la portabilidad de Docker sin las limitaciones de Fargate. Mayor responsabilidad operativa en el equipo de Plataforma para gestión de instancias EC2. Escalado manual (no automático como ECS Service Auto Scaling).

### DEC-03: Roles Separados — Controllers Dedicados

- **Estado**: Aceptado
- **Contexto**: Kafka KRaft soporta modo combinado donde un mismo nodo actúa como controller y broker. El modo combinado simplifica la topología pero mezcla el plano de control con el plano de datos.
- **Decisión**: Controllers y brokers son nodos dedicados con roles separados (`KAFKA_PROCESS_ROLES=controller` vs `broker`).
- **Consecuencias**: Los controllers no alojan particiones de datos, lo que evita que la carga de datos afecte la estabilidad del quórum. El clúster mínimo requiere 4 instancias EC2 en lugar de 3. Recomendado por Apache Kafka para entornos de producción.

### DEC-04: Convención de Nombrado de Topics

- **Estado**: Aceptado
- **Contexto**: Sin una convención estándar, los nombres de topics son inconsistentes, dificultando la aplicación de ACLs, el descubrimiento de topics y la trazabilidad de eventos.
- **Decisión**: Todos los topics siguen el formato `<dominio>.<servicio>.<entidad>.<evento>`. La creación de topics que no sigan esta convención es rechazada en la revisión de IaC.
- **Consecuencias**: ACLs aplicables por prefijo de dominio. Búsqueda y filtraje de topics simplificados. Requiere coordinación entre equipos al definir nuevos topics.
