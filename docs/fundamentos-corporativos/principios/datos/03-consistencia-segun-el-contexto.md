# Consistencia según el Contexto

## Declaración del Principio

El nivel de consistencia de los datos debe definirse según el contexto y las necesidades del dominio, y no imponerse de manera uniforme en toda la arquitectura.

## Propósito

Permitir que cada dominio adopte el modelo de consistencia que mejor se alinee con sus reglas de negocio, requisitos operativos y tolerancia al riesgo.

## Justificación

Imponer consistencia fuerte en todos los escenarios introduce complejidad, acoplamiento y limitaciones innecesarias.
De la misma forma, aceptar inconsistencia donde el negocio requiere certeza puede generar errores funcionales y pérdida de confianza.

La consistencia es una decisión arquitectónica contextual, no una propiedad global del sistema.

## Alcance Conceptual

Aplica principalmente a:

- Sistemas distribuidos
- Arquitecturas orientadas a eventos
- Integraciones y flujos de datos entre dominios

No existe un único modelo de consistencia válido para todos los casos ni para todos los dominios.
Las decisiones de consistencia deben considerar tanto aspectos técnicos como expectativas del negocio.

## Implicaciones Arquitectónicas

- Se aceptan distintos modelos de consistencia dentro de una misma solución.
- Cada dominio define sus expectativas de consistencia y tiempos aceptables de propagación de datos.
- Las decisiones de consistencia deben ser explícitas y comprensibles para los consumidores.
- La arquitectura debe soportar estos modelos sin forzar soluciones uniformes.

## Compensaciones (Trade-offs)

Introduce mayor complejidad conceptual y necesidad de alineación entre equipos, a cambio de mejor escalabilidad, resiliencia y una arquitectura alineada con las necesidades reales del negocio.

## Relación con Decisiones Arquitectónicas (ADRs)

Este principio suele reflejarse en decisiones relacionadas con:

- Modelos de comunicación entre dominios
- Uso de eventos y mecanismos de sincronización
- Estrategias de consistencia y expectativas entre productores y consumidores
