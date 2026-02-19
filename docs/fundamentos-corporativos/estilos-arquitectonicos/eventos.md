---
id: eventos
sidebar_position: 3
title: Arquitectura Orientada a Eventos
description: Estilo basado en comunicación asíncrona mediante eventos de dominio
---

# Arquitectura Orientada a Eventos

> **Tipo:** Estilo Arquitectónico Contextual
> **Aplicabilidad:** Sistemas con desacoplamiento temporal, múltiples consumidores y tolerancia a consistencia eventual

## Declaración del Estilo

Un sistema puede comunicarse y coordinarse mediante eventos que representan hechos relevantes del dominio, promoviendo desacoplamiento temporal y estructural entre componentes.

## Principios que Materializa

Este estilo arquitectónico implementa los siguientes principios corporativos:

- ✅ [Modularidad y Bajo Acoplamiento](../principios/01-modularidad-y-bajo-acoplamiento.md)
- ✅ [Resiliencia y Tolerancia a Fallos](../principios/03-resiliencia-y-tolerancia-a-fallos.md)
- ✅ [Arquitectura Evolutiva](../lineamientos/arquitectura/12-arquitectura-evolutiva.md)

## Propósito

Reducir el acoplamiento entre sistemas y servicios, habilitar escalabilidad y resiliencia, y permitir que múltiples consumidores reaccionen a cambios del negocio sin dependencias directas.

## Cuándo Usar este Estilo

✅ **Aplicar cuando:**

- Se requiere desacoplamiento temporal entre componentes
- Existen múltiples consumidores de la misma información
- Se tolera consistencia eventual
- El sistema debe escalar de forma distribuida
- Necesidad de reacción a hechos del dominio
- Arquitecturas de microservicios con comunicación asíncrona

❌ **NO aplicar cuando:**

- Se requiere consistencia fuerte inmediata
- Flujos síncronos críticos (ej: validación en línea)
- Sistemas simples sin necesidad de desacoplamiento temporal
- Dificultad para rastrear flujos asíncronos

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
