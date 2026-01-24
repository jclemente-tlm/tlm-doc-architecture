<!-- # Consistencia según el Contexto

## Enunciado
El nivel de consistencia de los datos debe definirse según el contexto y necesidades del dominio.

## Intención
Evitar imponer consistencia fuerte donde no es necesaria, o inconsistencia donde es crítica.

## Alcance conceptual
Aplica a sistemas distribuidos y orientados a eventos.
No existe un único modelo válido para todos los casos.

## Implicaciones arquitectónicas
- Se aceptan distintos modelos de consistencia.
- La consistencia es una decisión de diseño.
- El dominio define tolerancias y expectativas.

## Compensaciones (trade-offs)
Mayor complejidad conceptual a cambio de mejor escalabilidad y alineación con el negocio. -->

# Consistencia según el Contexto

## Declaración del Principio

El nivel de consistencia de los datos debe definirse según el contexto y las necesidades del dominio, y no imponerse de forma uniforme en toda la arquitectura.

## Propósito

Permitir que cada dominio adopte el modelo de consistencia que mejor se alinee con sus reglas de negocio, requisitos operativos y tolerancia al riesgo.

## Justificación

Imponer consistencia fuerte en todos los escenarios introduce complejidad, acoplamiento y limitaciones innecesarias.
De igual forma, aceptar inconsistencia donde el negocio requiere certeza puede generar errores funcionales y pérdida de confianza.

La consistencia es una decisión arquitectónica contextual, no una propiedad global del sistema.

## Alcance Conceptual

Aplica principalmente a:

- Sistemas distribuidos
- Arquitecturas orientadas a eventos
- Integraciones entre dominios

No existe un único modelo de consistencia válido para todos los casos ni para todos los dominios.

## Implicaciones Arquitectónicas

- Se aceptan distintos modelos de consistencia dentro de una misma solución.
- El dominio define sus expectativas de consistencia y tolerancia a la latencia.
- Las decisiones de consistencia deben ser explícitas y comprendidas por los consumidores.
- La arquitectura debe soportar estos modelos sin forzar soluciones uniformes.

## Compensaciones (Trade-offs)

Introduce mayor complejidad conceptual y necesidad de alineación entre equipos, a cambio de mejor escalabilidad, resiliencia y alineación con las necesidades reales del negocio.

## Relación con Decisiones Arquitectónicas (ADRs)

Este principio suele reflejarse en decisiones relacionadas con modelos de comunicación, manejo de eventos, sincronización de datos y definición de expectativas entre productores y consumidores.
