---
id: observabilidad-desde-el-diseno
sidebar_position: 5
title: Observabilidad desde el Diseño
description: Observabilidad como propiedad arquitectónica desde las primeras decisiones
---

# Observabilidad desde el Diseño

## 1. Declaración

La observabilidad debe considerarse una propiedad arquitectónica del sistema y definirse desde las primeras decisiones de diseño, no añadirse posteriormente como una preocupación operativa.

## 2. Justificación

Este principio busca permitir comprender el comportamiento del sistema, diagnosticar problemas y evaluar su estado real en producción de forma oportuna y confiable.

En sistemas modernos, distribuidos y dinámicos, los fallos no siempre son evidentes ni reproducibles en entornos de prueba.

Cuando la observabilidad se agrega al final, el sistema se vuelve una “caja negra”:
es difícil entender qué ocurre, por qué ocurre y dónde intervenir.

Diseñar la observabilidad desde el inicio permite:

- Detectar problemas antes de que impacten al negocio
- Reducir tiempos de diagnóstico y recuperación
- Tomar decisiones informadas sobre operación y evolución

Un sistema que no puede observarse adecuadamente no puede operarse ni evolucionar de forma segura.

## 3. Alcance y Contexto

Aplica a:

- Componentes y servicios
- Integraciones y flujos entre sistemas
- Procesos síncronos y asíncronos
- Operación en ambientes productivos y no productivos

No prescribe herramientas específicas, sino capacidades mínimas de observación.

## 4. Implicaciones

- Los componentes deben exponer información relevante sobre su estado y comportamiento.
- Las interacciones entre sistemas deben ser rastreables de extremo a extremo.
- Los errores y eventos relevantes deben ser visibles y comprensibles.
- La arquitectura debe permitir diferenciar comportamientos normales de anomalías.
- El diseño debe facilitar la correlación entre eventos, métricas y flujos.

**Compensaciones (Trade-offs):**

Introduce esfuerzo adicional en diseño y desarrollo, a cambio de mayor confiabilidad operativa, menor tiempo de resolución de incidentes y mejor capacidad de evolución del sistema.
