---
id: 03-orientada-a-eventos
sidebar_position: 3
title: Arquitectura orientada a eventos
---

## Principios

- Desacopla productores y consumidores mediante eventos.
- Usa mensajes inmutables y bien definidos.
- Garantiza la entrega y el orden de los eventos según necesidad.

## Buenas prácticas

- Documenta el esquema de los eventos.
- Implementa idempotencia en consumidores.
- Monitorea colas y flujos de eventos.
- Usa mecanismos de retry y DLQ (Dead Letter Queue).
