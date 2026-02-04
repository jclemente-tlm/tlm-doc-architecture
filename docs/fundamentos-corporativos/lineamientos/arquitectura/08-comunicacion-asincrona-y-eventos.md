---
id: comunicacion-asincrona-y-eventos
sidebar_position: 8
title: Comunicación Asíncrona y Eventos
description: Lineamientos para mensajería asíncrona y arquitectura orientada a eventos
---

# Comunicación Asíncrona y Eventos

Comunicación asíncrona desacopla sistemas en tiempo y espacio, permitiendo resiliencia ante indisponibilidades temporales y escalabilidad independiente. Eventos mal diseñados (imperativos, sin esquema, sin idempotencia) generan acoplamiento oculto y procesamiento duplicado. Adoptar AsyncAPI, eventos inmutables e idempotencia garantiza consistencia eventual y evolución controlada de integraciones.

**Este lineamiento aplica a:** mensajería entre servicios, arquitectura orientada a eventos, event sourcing, CQRS e integraciones asíncronas.

## Estándares Obligatorios

- [Implementar mensajería con Apache Kafka](../../estandares/mensajeria/kafka-messaging.md)
- [Definir esquemas de eventos con AsyncAPI o Avro](../../estandares/mensajeria/kafka-messaging.md)
- [Usar eventos para comunicar hechos del dominio, no comandos](../../estandares/mensajeria/kafka-messaging.md)
- [Implementar idempotencia en consumidores](../../estandares/mensajeria/kafka-messaging.md)
- [Garantizar entrega at-least-once o exactly-once](../../estandares/mensajeria/kafka-messaging.md)
- [Configurar Dead Letter Queue para mensajes fallidos](../../estandares/mensajeria/kafka-messaging.md)
- [Documentar topología de eventos y consumidores](../../estandares/mensajeria/kafka-messaging.md)
