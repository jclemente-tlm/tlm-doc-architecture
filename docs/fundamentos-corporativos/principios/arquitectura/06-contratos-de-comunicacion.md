---
id: contratos-de-comunicacion
sidebar_position: 6
title: Contratos de Comunicación
description: Interfaces basadas en contratos explícitos, versionados y acordados
---

# Contratos de Comunicación

## 1. Declaración del Principio

La comunicación entre sistemas y servicios debe basarse en contratos explícitos, versionados y acordados, que definan claramente las expectativas de las interfaces de integración (APIs, mensajería, eventos).

## 2. Propósito

Reducir el acoplamiento entre sistemas, permitir la evolución independiente y evitar dependencias implícitas en las interfaces de comunicación (APIs, mensajería).

> **Nota:** Este principio se enfoca en **contratos de comunicación** (APIs REST, GraphQL, gRPC, mensajería). Para esquemas de datos de dominio (BD, modelos) ver [Esquemas de Dominio](../../datos/02-esquemas-de-dominio.md).

## 3. Justificación

Cuando las integraciones se basan en supuestos no documentados o en detalles internos de otros sistemas, cualquier cambio puede provocar errores en cascada.

Los contratos de comunicación establecen un acuerdo claro sobre:

- Qué se expone
- Cómo se consume
- Qué se garantiza
- Qué no debe asumirse

Esto permite que los sistemas evolucionen sin romper a sus consumidores y facilita el gobierno de las integraciones.

## 4. Alcance Conceptual

Aplica específicamente a:

- APIs y protocolos de comunicación síncrona
- Mensajería y eventos (colas, topics, streaming)
- Contratos de servicios síncronos y asíncronos
- Webhooks y callbacks

No aplica a:

- Esquemas de bases de datos (ver Esquemas de Dominio)
- Modelos de dominio internos

El principio es independiente del estilo arquitectónico o la tecnología utilizada.

## 5. Implicaciones Arquitectónicas

- Las integraciones deben definirse mediante contratos explícitos.
- Los contratos forman parte de la arquitectura y deben ser versionados.
- Los consumidores no deben depender de estructuras internas del proveedor.
- Los cambios deben gestionarse considerando compatibilidad hacia atrás.
- La comunicación entre sistemas se diseña como una relación contractual, no como un acceso directo.

## 6. Compensaciones (Trade-offs)

Reduce la flexibilidad inmediata para realizar cambios rápidos, a cambio de mayor estabilidad, previsibilidad y capacidad de evolución del ecosistema de sistemas.

## 7. Relación con Decisiones Arquitectónicas (ADRs)

Este principio se refleja en ADRs relacionados con:

- Estrategias de integración
- Versionado de APIs y eventos
- Compatibilidad hacia atrás
- Gestión de cambios entre sistemas
