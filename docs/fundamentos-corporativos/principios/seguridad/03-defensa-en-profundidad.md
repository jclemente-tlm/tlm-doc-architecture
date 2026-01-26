---
sidebar_position: 3
---

# Defensa en Profundidad

## Declaración del Principio

La arquitectura debe diseñarse incorporando múltiples capas de protección independientes, de modo que la falla o evasión de un control no comprometa la seguridad del sistema en su conjunto.

## Propósito

Reducir el impacto de fallos, errores humanos o accesos indebidos, evitando que un único punto de falla exponga activos críticos o comprometa todo el sistema.

## Justificación

Ningún control de seguridad es infalible.
Las configuraciones pueden fallar, los accesos pueden ser mal otorgados y los mecanismos de protección pueden ser evadidos.

La defensa en profundidad asume esta realidad y establece que la seguridad no depende de un único control, sino de la combinación coherente de múltiples barreras que limitan el alcance y la propagación de un incidente.

## Alcance Conceptual

Este principio aplica a:

- Componentes y servicios
- Acceso a datos y recursos críticos
- Integraciones internas y externas
- Flujos de información dentro de la arquitectura

No implica duplicar controles sin criterio, sino diseñar capas complementarias y con responsabilidades claras.

## Implicaciones Arquitectónicas

- No debe existir un único punto cuya falla comprometa activos críticos.
- Las capas de seguridad deben ser independientes y complementarias.
- El acceso y las capacidades deben limitarse progresivamente.
- La arquitectura debe facilitar la detección, contención y aislamiento de incidentes.
- Los controles deben distribuirse en distintos niveles de la arquitectura.

## Compensaciones (Trade-offs)

Introduce mayor complejidad en diseño, operación y gobierno de la seguridad, a cambio de una reducción significativa del impacto de incidentes y una mayor resiliencia ante fallos inevitables.

## Relación con Decisiones Arquitectónicas (ADRs)

Este principio suele reflejarse en ADRs relacionados con:

- Segmentación de componentes y dominios
- Estrategias de protección de datos y servicios
- Diseño de capas de acceso y control
- Mecanismos de aislamiento y contención
