---
id: bajo-acoplamiento
sidebar_position: 3
title: Bajo Acoplamiento
description: Minimizar dependencias entre componentes para reducir impacto de cambios
---

# Bajo Acoplamiento

## 1. Declaración

Los componentes del sistema deben minimizar las dependencias entre sí, haciéndolas explícitas, estables y gestionables.

## 2. Justificación

Este principio busca reducir el impacto de cambios, fallos y decisiones locales en el sistema, permitiendo que componentes evolucionen con mínima coordinación.

El acoplamiento excesivo entre componentes provoca efectos en cascada: un cambio pequeño genera impactos amplios, aumenta el riesgo operativo y ralentiza la entrega de valor.

Cuando los componentes están fuertemente acoplados:

- Los cambios se propagan de forma impredecible
- El testing se vuelve complejo (múltiples dependencias)
- La comprensión del sistema requiere conocer todo el ecosistema
- Los fallos se extienden entre componentes relacionados

Este principio no busca eliminar toda dependencia, sino hacerlas explícitas, conscientes, estables y minimizarlas al nivel necesario.

## 3. Alcance y Contexto

Aplica a:

- Componentes y módulos dentro de sistemas
- Servicios en arquitecturas distribuidas
- Dominios y bounded contexts
- Capas arquitectónicas

El acoplamiento se evalúa en múltiples dimensiones: temporal, espacial, semántico y de datos.

## 4. Implicaciones

- Las dependencias entre componentes deben ser explícitas (contratos, interfaces).
- Las dependencias deben ser estables (no cambiar frecuentemente).
- La comunicación entre componentes debe usar abstracciones, no implementaciones concretas.
- Los cambios internos de un componente no deben afectar a sus consumidores.
- Se debe preferir acoplamiento temporal asíncrono sobre síncrono cuando sea apropiado.

**Compensaciones (Trade-offs):**

Puede incrementar el esfuerzo de diseño inicial y la necesidad de definir contratos claros, a cambio de mayor capacidad de evolución, reducción de impacto de cambios y mejor aislamiento de fallos.
