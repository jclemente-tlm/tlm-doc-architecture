# Observabilidad desde el Diseño

## Declaración del Principio

La observabilidad debe considerarse una propiedad arquitectónica del sistema y definirse desde las primeras decisiones de diseño, no añadirse posteriormente como una preocupación operativa.

## Propósito

Permitir comprender el comportamiento del sistema, diagnosticar problemas y evaluar su estado real en producción de forma oportuna y confiable.

## Justificación

En sistemas modernos, distribuidos y dinámicos, los fallos no siempre son evidentes ni reproducibles en entornos de prueba.

Cuando la observabilidad se agrega al final, el sistema se vuelve una “caja negra”:
es difícil entender qué ocurre, por qué ocurre y dónde intervenir.

Diseñar la observabilidad desde el inicio permite:

- Detectar problemas antes de que impacten al negocio
- Reducir tiempos de diagnóstico y recuperación
- Tomar decisiones informadas sobre operación y evolución

Un sistema que no puede observarse adecuadamente no puede operarse ni evolucionar de forma segura.

## Alcance Conceptual

Aplica a:

- Componentes y servicios
- Integraciones y flujos entre sistemas
- Procesos síncronos y asíncronos
- Operación en ambientes productivos y no productivos

No prescribe herramientas específicas, sino capacidades mínimas de observación.

## Implicaciones Arquitectónicas

- Los componentes deben exponer información relevante sobre su estado y comportamiento.
- Las interacciones entre sistemas deben ser rastreables de extremo a extremo.
- Los errores y eventos relevantes deben ser visibles y comprensibles.
- La arquitectura debe permitir diferenciar comportamientos normales de anomalías.
- El diseño debe facilitar la correlación entre eventos, métricas y flujos.

## Compensaciones (Trade-offs)

Introduce esfuerzo adicional en diseño y desarrollo, a cambio de mayor confiabilidad operativa, menor tiempo de resolución de incidentes y mejor capacidad de evolución del sistema.

## Relación con Decisiones Arquitectónicas (ADRs)

Este principio se refleja en ADRs relacionados con:

- Estrategias de logging, métricas y trazabilidad
- Diseño de flujos y correlación entre componentes
- Manejo de errores y eventos
- Exposición de información operativa
