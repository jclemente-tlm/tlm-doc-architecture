---
id: resiliencia-y-tolerancia-a-fallos
sidebar_position: 3
title: Resiliencia y Tolerancia a Fallos
description: Sistemas diseñados para degradarse, recuperarse y operar ante fallos
---

# Resiliencia y Tolerancia a Fallos

## 1. Declaración

Los sistemas deben diseñarse asumiendo que los fallos ocurrirán y deben ser capaces de degradarse, recuperarse y continuar operando de forma controlada.

## 2. Justificación

Este principio busca reducir el impacto de fallos técnicos, errores humanos o dependencias externas, manteniendo niveles aceptables de servicio y continuidad del negocio.

En sistemas modernos, distribuidos e integrados, los fallos no son excepciones, sino eventos esperables:

- Servicios externos pueden no estar disponibles
- Componentes internos pueden fallar
- Picos de carga pueden degradar el sistema

Diseñar asumiendo disponibilidad total genera arquitecturas frágiles.
La resiliencia debe ser una **propiedad estructural del sistema**, no una reacción operativa.

## 3. Alcance y Contexto

Este principio aplica a:

- Comunicación entre componentes
- Integraciones internas y externas
- Manejo de dependencias
- Experiencia del usuario ante fallos
- Expectativas de disponibilidad del negocio

Aplica independientemente del estilo arquitectónico adoptado.

## 4. Implicaciones

- La arquitectura debe asumir fallos parciales como escenario normal.
- Los componentes deben fallar de forma controlada y predecible.
- El sistema debe evitar fallos en cascada entre dependencias.
- Se deben priorizar funcionalidades críticas frente a fallos.
- Las expectativas de disponibilidad deben estar alineadas con el diseño del sistema.

**Compensaciones (Trade-offs):**

Puede incrementar el esfuerzo de diseño y el costo inicial de implementación, a cambio de mayor estabilidad, menor impacto operativo y mejor continuidad del servicio.
