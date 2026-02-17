---
id: arquitectura-limpia
sidebar_position: 11
title: Arquitectura Limpia
description: Patrón arquitectónico que separa las decisiones de negocio de los detalles técnicos, manteniendo el dominio independiente de frameworks e infraestructura.
tags: [lineamiento, arquitectura, clean-architecture, mantenibilidad]
---

# Arquitectura Limpia

## Tipo de Lineamiento

**Lineamiento de Arquitectura** - Implementa el principio de [Mantenibilidad y Extensibilidad](../../principios/01-mantenibilidad-y-extensibilidad.md)

## 1. Declaración

La arquitectura de un sistema debe separar claramente las decisiones de negocio de los detalles técnicos, permitiendo que el dominio evolucione de forma independiente a frameworks, infraestructura o tecnologías específicas.

## 2. Justificación

Este principio busca preservar la claridad del dominio, reducir el acoplamiento técnico y facilitar la evolución del sistema a lo largo del tiempo.

Cuando las decisiones técnicas dominan la estructura del sistema, los cambios tecnológicos impactan directamente en la lógica de negocio, incrementando el costo de mantenimiento y la rigidez del sistema.

La Arquitectura Limpia propone que el negocio sea el eje central del diseño, y que los detalles técnicos se adapten a él, no al revés.

Este principio no busca imponer una estructura rígida, sino establecer una dirección clara sobre qué decisiones deben ser más estables y cuáles pueden cambiar con mayor facilidad.

## 3. Alcance y Contexto

Aplica a:

- Sistemas con lógica de negocio relevante
- Soluciones con expectativa de evolución en el tiempo
- Arquitecturas donde se desea reducir dependencia tecnológica

No requiere una implementación literal de capas o patrones específicos, ni es exclusiva de un estilo arquitectónico particular.

## 4. Implicaciones

- La lógica de negocio no depende de frameworks, bases de datos o mecanismos de entrega.
- Las dependencias se orientan hacia el dominio, no hacia los detalles técnicos.
- Los cambios tecnológicos deben tener impacto limitado en el núcleo del sistema.
- La estructura del sistema refleja prioridades del negocio antes que decisiones técnicas.

**Compensaciones (Trade-offs):**

Puede introducir mayor esfuerzo inicial de diseño y disciplina en la estructura del sistema, a cambio de mayor mantenibilidad, claridad y capacidad de evolución a largo plazo.
