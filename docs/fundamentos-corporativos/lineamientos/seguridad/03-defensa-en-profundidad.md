---
id: defensa-en-profundidad
sidebar_position: 3
title: Defensa en Profundidad
description: Múltiples capas de protección independientes en la arquitectura
---

# Defensa en Profundidad

## 1. Declaración

La arquitectura debe diseñarse incorporando múltiples capas de protección independientes, de modo que la falla o evasión de un control no comprometa la seguridad del sistema en su conjunto.

## 2. Justificación

Este principio busca reducir el impacto de fallos, errores humanos o accesos indebidos, evitando que un único punto de falla exponga activos críticos o comprometa todo el sistema.

Ningún control de seguridad es infalible.
Las configuraciones pueden fallar, los accesos pueden ser mal otorgados y los mecanismos de protección pueden ser evadidos.

La defensa en profundidad asume esta realidad y establece que la seguridad no depende de un único control, sino de la combinación coherente de múltiples barreras que limitan el alcance y la propagación de un incidente.

## 3. Alcance y Contexto

Este principio aplica a:

- Componentes y servicios
- Acceso a datos y recursos críticos
- Integraciones internas y externas
- Flujos de información dentro de la arquitectura

No implica duplicar controles sin criterio, sino diseñar capas complementarias y con responsabilidades claras.

## 4. Implicaciones

- No debe existir un único punto cuya falla comprometa activos críticos.
- Las capas de seguridad deben ser independientes y complementarias.
- El acceso y las capacidades deben limitarse progresivamente.
- La arquitectura debe facilitar la detección, contención y aislamiento de incidentes.
- Los controles deben distribuirse en distintos niveles de la arquitectura.

**Compensaciones (Trade-offs):**

Introduce mayor complejidad en diseño, operación y gobierno de la seguridad, a cambio de una reducción significativa del impacto de incidentes y una mayor resiliencia ante fallos inevitables.
