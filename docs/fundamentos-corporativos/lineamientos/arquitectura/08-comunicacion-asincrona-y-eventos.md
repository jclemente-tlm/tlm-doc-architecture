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

- [Usar mensajería asíncrona](../../estandares/mensajeria/event-driven-architecture.md#1-async-messaging)
- [Documentar contratos de eventos](../../estandares/apis/event-contracts.md)
- [Diseñar eventos como hechos del dominio](../../estandares/mensajeria/event-driven-architecture.md#2-event-design)
- [Implementar consumidores idempotentes](../../estandares/mensajeria/event-driven-architecture.md#4-idempotency)
- [Configurar garantías de entrega](../../estandares/mensajeria/message-reliability.md#1-message-delivery-guarantees)
- [Implementar Dead Letter Queue](../../estandares/mensajeria/message-reliability.md#2-dead-letter-queue)
- [Mantener catálogo de eventos](../../estandares/mensajeria/event-driven-architecture.md#3-event-catalog)
