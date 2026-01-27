---
id: 03-orientada-a-eventos
sidebar_position: 3
title: Arquitectura orientada a eventos
---

<!-- ## Principios

- Desacopla productores y consumidores mediante eventos.
- Usa mensajes inmutables y bien definidos.
- Garantiza la entrega y el orden de los eventos según necesidad.

## Buenas prácticas

- Documenta el esquema de los eventos.
- Implementa idempotencia en consumidores.
- Monitorea colas y flujos de eventos.
- Usa mecanismos de retry y DLQ (Dead Letter Queue). -->


# Arquitectura Orientada a Eventos

## Enunciado
Los sistemas deben comunicar hechos relevantes del dominio mediante eventos explícitos, permitiendo reacciones desacopladas y asincrónicas.

## Intención
Reducir dependencias directas entre sistemas y facilitar la evolución independiente de productores y consumidores.

## Alcance conceptual
Aplica en escenarios donde el desacoplamiento temporal, la escalabilidad y la resiliencia son prioritarios.

No sustituye completamente a la comunicación síncrona.

## Implicaciones arquitectónicas
- El dominio se expresa mediante hechos observables.
- Los consumidores reaccionan sin conocimiento directo del productor.
- La consistencia puede ser eventual.
- El flujo de control se distribuye.

## Compensaciones (trade-offs)
Se pierde simplicidad en el flujo secuencial a cambio de mayor flexibilidad, escalabilidad y tolerancia a fallos.
