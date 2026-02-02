---
id: consistencia-contextual
sidebar_position: 3
title: Consistencia Contextual
description: Nivel de consistencia definido según necesidades de cada dominio
---

# Consistencia Contextual

## 1. Declaración del Principio

El nivel de consistencia de los datos debe definirse según las necesidades específicas de cada dominio o caso de uso, aceptando que diferentes partes del sistema pueden requerir modelos de consistencia distintos (fuerte, eventual, causal).

## 2. Propósito

Permitir que cada dominio adopte el modelo de consistencia que mejor se alinee con sus reglas de negocio, requisitos operativos y tolerancia al riesgo.

## 3. Justificación

Imponer consistencia fuerte en todos los escenarios introduce complejidad, acoplamiento y limitaciones innecesarias.
De la misma forma, aceptar inconsistencia donde el negocio requiere certeza puede generar errores funcionales y pérdida de confianza.

La consistencia es una decisión arquitectónica contextual, no una propiedad global del sistema.

## 4. Alcance Conceptual

Aplica principalmente a:

- Sistemas distribuidos
- Arquitecturas orientadas a eventos
- Integraciones y flujos de datos entre dominios

No existe un único modelo de consistencia válido para todos los casos ni para todos los dominios.
Las decisiones de consistencia deben considerar tanto aspectos técnicos como expectativas del negocio.

## 5. Implicaciones Arquitectónicas

- Se aceptan distintos modelos de consistencia dentro de una misma solución.
- Cada dominio define sus expectativas de consistencia y tiempos aceptables de propagación de datos.
- Las decisiones de consistencia deben ser explícitas y comprensibles para los consumidores.
- La arquitectura debe soportar estos modelos sin forzar soluciones uniformes.

## 6. Compensaciones (Trade-offs)

Introduce mayor complejidad conceptual y necesidad de alineación entre equipos, a cambio de mejor escalabilidad, resiliencia y una arquitectura alineada con las necesidades reales del negocio.

## 7. Relación con Decisiones Arquitectónicas (ADRs)

Este principio suele reflejarse en decisiones relacionadas con:

- Modelos de comunicación entre dominios
- Uso de eventos y mecanismos de sincronización
- Estrategias de consistencia y expectativas entre productores y consumidores
