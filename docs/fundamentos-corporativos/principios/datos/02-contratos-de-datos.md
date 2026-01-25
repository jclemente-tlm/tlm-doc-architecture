# Contratos de Datos

## Declaración del Principio

El intercambio de datos entre dominios debe realizarse mediante contratos de datos explícitos, versionados y acordados entre productor y consumidor.

## Propósito

Asegurar integraciones estables, comprensibles y evolutivas entre dominios, reduciendo acoplamientos innecesarios.

## Justificación

Cuando los consumidores dependen de estructuras internas de datos de otro dominio, se genera fragilidad ante cambios, pérdida de control sobre la evolución y alto riesgo de ruptura.

Los contratos de datos establecen una frontera clara de responsabilidad, definiendo qué se expone, cómo puede evolucionar y qué expectativas existen entre las partes.

## Alcance Conceptual

Aplica a todo intercambio de datos entre dominios, independientemente del mecanismo utilizado, incluyendo:

- APIs
- Eventos
- Integraciones síncronas y asíncronas
- Flujos batch y procesos de replicación

Este principio no prescribe tecnologías específicas, sino el acuerdo conceptual que gobierna el intercambio de datos.

## Implicaciones Arquitectónicas

- Los esquemas y estructuras expuestas forman parte del contrato.
- El contrato es definido y gobernado por el productor del dato.
- Los cambios deben evaluarse por su impacto en los consumidores.
- Los consumidores no asumen ni dependen de detalles internos del productor.
- El contrato define la semántica del dato, no solo su estructura.
- El versionado es un mecanismo clave para permitir evolución controlada.

## Compensaciones (Trade-offs)

Reduce la flexibilidad inmediata para modificar estructuras internas, a cambio de mayor estabilidad, gobernanza y sostenibilidad del ecosistema de sistemas.

## Relación con Decisiones Arquitectónicas (ADRs)

Este principio suele materializarse en decisiones relacionadas con:

- Versionado de esquemas y contratos
- Definición de datos públicos versus internos
- Estrategias de compatibilidad y evolución entre productores y consumidores
