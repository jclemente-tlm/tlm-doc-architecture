---
id: modularidad-y-bajo-acoplamiento
sidebar_position: 1
title: Modularidad y Bajo Acoplamiento
description: Dividir sistemas en componentes independientes con dependencias mínimas y explícitas
---

# Modularidad y Bajo Acoplamiento

## Declaración del Principio

Los sistemas deben dividirse en componentes modulares e independientes, minimizando las dependencias entre ellos y haciéndolas explícitas, estables y gestionables.

## Justificación

En sistemas modernos, especialmente distribuidos, el acoplamiento excesivo entre componentes provoca efectos en cascada donde un cambio pequeño genera impactos amplios, aumenta el riesgo operativo y ralentiza la entrega de valor.

Cuando los componentes están fuertemente acoplados, los cambios se propagan de forma impredecible, el testing se vuelve complejo, la comprensión del sistema requiere conocer todo el ecosistema y los fallos se extienden entre componentes relacionados.

Este principio busca permitir la evolución independiente de componentes minimizando el impacto de cambios locales en el sistema global. Se logra haciendo las dependencias explícitas mediante contratos estables, usando abstracciones en lugar de implementaciones concretas, y minimizando el acoplamiento temporal, espacial, semántico y de datos. Se aplica a componentes y módulos internos, servicios en arquitecturas distribuidas, dominios y bounded contexts, y capas arquitectónicas.

## Implicaciones

- Las dependencias entre componentes deben ser explícitas mediante contratos e interfaces estables
- La comunicación debe usar abstracciones, no implementaciones concretas
- Los cambios internos de un componente no deben afectar a sus consumidores
- Preferir acoplamiento asíncrono sobre síncrono cuando sea apropiado
- Balancear independencia con necesidades de integración
- Requiere mayor esfuerzo de diseño inicial a cambio de mejor capacidad de evolución

## Referencias

**Lineamientos relacionados:**

- [Modelado de Dominio](../lineamientos/arquitectura/modelado-de-dominio.md)
- [Autonomía de Servicios](../lineamientos/arquitectura/autonomia-de-servicios.md)
- [Arquitectura Limpia](../lineamientos/arquitectura/arquitectura-limpia.md)

**ADRs relacionados:**

- [ADR-008: Kafka para Mensajería Asíncrona](/docs/adrs/adr-008-kafka-mensajeria-asincrona)
- [ADR-010: Kong como API Gateway](/docs/adrs/adr-010-kong-api-gateway)

**Frameworks de referencia:**

- [AWS Well-Architected Framework](https://aws.amazon.com/architecture/well-architected/)
- [Azure Well-Architected Framework](https://learn.microsoft.com/azure/well-architected/)
