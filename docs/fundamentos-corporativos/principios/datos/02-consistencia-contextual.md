---
id: consistencia-contextual
sidebar_position: 2
title: Consistencia Contextual
description: Nivel de consistencia definido según necesidades de cada dominio
---

# Consistencia Contextual

## 1. Declaración

El nivel de consistencia de los datos debe definirse según las necesidades específicas de cada dominio o caso de uso, aceptando que diferentes partes del sistema pueden requerir modelos de consistencia distintos (fuerte, eventual, causal).

## 2. Justificación

Este principio busca permitir que cada dominio adopte el modelo de consistencia que mejor se alinee con sus reglas de negocio, requisitos operativos y tolerancia al riesgo.

Imponer consistencia fuerte en todos los escenarios introduce complejidad, acoplamiento y limitaciones innecesarias.
De la misma forma, aceptar inconsistencia donde el negocio requiere certeza puede generar errores funcionales y pérdida de confianza.

La consistencia es una decisión arquitectónica contextual, no una propiedad global del sistema.

## 3. Alcance y Contexto

Aplica principalmente a:

- Sistemas distribuidos
- Arquitecturas orientadas a eventos
- Integraciones y flujos de datos entre dominios

No existe un único modelo de consistencia válido para todos los casos ni para todos los dominios.
Las decisiones de consistencia deben considerar tanto aspectos técnicos como expectativas del negocio.

## 4. Implicaciones

- Se aceptan distintos modelos de consistencia dentro de una misma solución.
- Cada dominio define sus expectativas de consistencia y tiempos aceptables de propagación de datos.
- Las decisiones de consistencia deben ser explícitas y comprensibles para los consumidores.
- La arquitectura debe soportar estos modelos sin forzar soluciones uniformes.

**Compensaciones (Trade-offs):**

Introduce mayor complejidad conceptual y necesidad de alineación entre equipos, a cambio de mejor escalabilidad, resiliencia y una arquitectura alineada con las necesidades reales del negocio.
