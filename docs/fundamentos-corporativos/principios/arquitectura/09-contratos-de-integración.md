# Contratos de Integración

## Declaración del Principio

La integración entre sistemas y servicios debe basarse en contratos explícitos, versionados y acordados, que definan claramente las expectativas entre productores y consumidores.

## Propósito

Reducir el acoplamiento entre sistemas, permitir la evolución independiente y evitar dependencias implícitas que generen fallos difíciles de detectar y corregir.

## Justificación

Cuando las integraciones se basan en supuestos no documentados o en detalles internos de otros sistemas, cualquier cambio puede provocar errores en cascada.

Los contratos de integración establecen un acuerdo claro sobre:

- Qué se expone
- Cómo se consume
- Qué se garantiza
- Qué no debe asumirse

Esto permite que los sistemas evolucionen sin romper a sus consumidores y facilita el gobierno de las integraciones.

## Alcance Conceptual

Aplica a:

- APIs (REST, SOAP, gRPC, etc.)
- Eventos y mensajería
- Integraciones síncronas y asíncronas
- Flujos batch e intercambios de datos

El principio es independiente del estilo arquitectónico o la tecnología utilizada.

## Implicaciones Arquitectónicas

- Las integraciones deben definirse mediante contratos explícitos.
- Los contratos forman parte de la arquitectura y deben ser versionados.
- Los consumidores no deben depender de estructuras internas del proveedor.
- Los cambios deben gestionarse considerando compatibilidad hacia atrás.
- La comunicación entre sistemas se diseña como una relación contractual, no como un acceso directo.

## Compensaciones (Trade-offs)

Reduce la flexibilidad inmediata para realizar cambios rápidos, a cambio de mayor estabilidad, previsibilidad y capacidad de evolución del ecosistema de sistemas.

## Relación con Decisiones Arquitectónicas (ADRs)

Este principio se refleja en ADRs relacionados con:

- Estrategias de integración
- Versionado de APIs y eventos
- Compatibilidad hacia atrás
- Gestión de cambios entre sistemas
