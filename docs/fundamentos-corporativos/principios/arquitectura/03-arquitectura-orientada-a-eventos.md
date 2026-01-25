---
id: 03-arquitectura-orientada-a-eventos
sidebar_position: 3
# title: Arquitectura orientada a eventos
---

# Arquitectura Orientada a Eventos

## Declaración del Principio

Un sistema puede comunicarse y coordinarse mediante eventos que representan hechos relevantes del dominio, promoviendo desacoplamiento temporal y estructural entre componentes.

## Propósito

Reducir el acoplamiento entre sistemas y servicios, habilitar escalabilidad y resiliencia, y permitir que múltiples consumidores reaccionen a cambios del negocio sin dependencias directas.

## Justificación

En arquitecturas síncronas y fuertemente acopladas, los sistemas dependen de la disponibilidad inmediata de otros componentes, lo que incrementa:

- La fragilidad ante fallos
- La dificultad de escalar
- El impacto de cambios en cascada

La arquitectura orientada a eventos permite que los sistemas reaccionen a hechos ocurridos sin requerir conocimiento directo de quién consume esa información, favoreciendo evolución independiente y tolerancia a fallos.

No sustituye a las APIs ni elimina la comunicación síncrona, sino que las complementa donde el contexto lo requiere.

## Alcance Conceptual

Aplica especialmente cuando:

- Se requiere desacoplamiento temporal entre componentes
- Existen múltiples consumidores de información
- Se tolera consistencia eventual
- El sistema debe escalar de forma distribuida

No todos los flujos deben modelarse como eventos; su uso debe responder a necesidades reales del dominio.

## Implicaciones Arquitectónicas

- Los eventos representan **hechos del dominio**, no comandos ni instrucciones.
- Los productores de eventos no conocen a sus consumidores.
- Los consumidores reaccionan a eventos de forma independiente.
- La consistencia eventual es un modelo aceptado y explícito.
- El diseño debe considerar idempotencia y manejo de duplicados.
- La observabilidad del flujo de eventos es una preocupación central.

## Compensaciones (Trade-offs)

Introduce mayor complejidad conceptual y operativa, así como desafíos en trazabilidad y consistencia, a cambio de mayor desacoplamiento, escalabilidad y resiliencia del sistema.

## Relación con Decisiones Arquitectónicas (ADRs)

Este principio se refleja en ADRs relacionados con:

- Uso de mensajería o streaming de eventos
- Definición de eventos de dominio
- Estrategias de integración entre sistemas
- Manejo de consistencia y asincronía
