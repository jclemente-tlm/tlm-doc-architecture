---
sidebar_position: 8
---

# Resiliencia y Tolerancia a Fallos

## Declaración del Principio

Los sistemas deben diseñarse asumiendo que los fallos ocurrirán y deben ser capaces de degradarse, recuperarse y continuar operando de forma controlada.

## Propósito

Reducir el impacto de fallos técnicos, errores humanos o dependencias externas, manteniendo niveles aceptables de servicio y continuidad del negocio.

## Justificación

En sistemas modernos, distribuidos e integrados, los fallos no son excepciones, sino eventos esperables:

- Servicios externos pueden no estar disponibles
- Componentes internos pueden fallar
- Picos de carga pueden degradar el sistema

Diseñar asumiendo disponibilidad total genera arquitecturas frágiles.
La resiliencia debe ser una **propiedad estructural del sistema**, no una reacción operativa.

## Alcance Conceptual

Este principio aplica a:

- Comunicación entre componentes
- Integraciones internas y externas
- Manejo de dependencias
- Experiencia del usuario ante fallos
- Expectativas de disponibilidad del negocio

Aplica independientemente del estilo arquitectónico adoptado.

## Implicaciones Arquitectónicas

- La arquitectura debe asumir fallos parciales como escenario normal.
- Los componentes deben fallar de forma controlada y predecible.
- El sistema debe evitar fallos en cascada entre dependencias.
- Se deben priorizar funcionalidades críticas frente a fallos.
- Las expectativas de disponibilidad deben estar alineadas con el diseño del sistema.

## Compensaciones (Trade-offs)

Puede incrementar el esfuerzo de diseño y el costo inicial de implementación, a cambio de mayor estabilidad, menor impacto operativo y mejor continuidad del servicio.

## Relación con Decisiones Arquitectónicas (ADRs)

Este principio se refleja en ADRs relacionados con:

- Manejo de dependencias entre componentes
- Estrategias de degradación funcional
- Definición de expectativas de disponibilidad
- Decisiones de recuperación y continuidad
