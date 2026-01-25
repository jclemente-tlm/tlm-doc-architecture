---
id: 04-arquitectura-cloud-native
sidebar_position: 4
# title: Arquitectura Cloud-Native
---

# Arquitectura Cloud-Native

## Declaración del Principio

Un sistema puede diseñarse siguiendo principios cloud-native cuando se espera que opere en entornos dinámicos, escalables y automatizados, aprovechando las capacidades propias de plataformas cloud.

## Propósito

Permitir que los sistemas se adapten al cambio, escalen bajo demanda y se operen de forma confiable en entornos distribuidos y automatizados.

## Justificación

Diseñar sistemas únicamente para entornos estáticos o infraestructuras predecibles limita su capacidad de escalar, recuperarse ante fallos y evolucionar de forma eficiente.

La arquitectura cloud-native asume que:

- la infraestructura es dinámica,
- los recursos no son permanentes,
- los fallos son esperables,
- y la automatización es una condición básica de operación.

No todo sistema requiere un enfoque cloud-native, pero cuando se adopta la nube como plataforma principal, el diseño debe alinearse a estas realidades.

## Alcance Conceptual

Aplica principalmente a:

- Sistemas desplegados en plataformas cloud
- Arquitecturas distribuidas
- Servicios que requieren escalabilidad y elasticidad
- Entornos con despliegues frecuentes y automatizados

No implica migrar sistemas existentes sin evaluación ni utilizar servicios cloud por defecto.

## Implicaciones Arquitectónicas

- Los sistemas deben tolerar fallos y reemplazo de componentes.
- El estado debe gestionarse de forma explícita y preferentemente externa.
- La configuración debe separarse del código.
- El escalado y la recuperación no dependen de intervención manual.
- La observabilidad y automatización son requisitos arquitectónicos, no operativos.

## Compensaciones (Trade-offs)

Introduce mayor complejidad inicial en diseño y operación, a cambio de mayor elasticidad, resiliencia y capacidad de adaptación al cambio.

## Relación con Decisiones Arquitectónicas (ADRs)

Este principio se refleja en ADRs relacionados con:

- Estrategias de despliegue
- Manejo de estado y configuración
- Automatización y operación del sistema
- Uso de capacidades gestionadas de la plataforma
