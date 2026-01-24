<!-- # Protección de Datos Sensibles

## Enunciado
Los datos sensibles deben ser protegidos durante todo su ciclo de vida.

## Intención
Reducir riesgos legales, reputacionales y operativos.

## Alcance conceptual
Aplica a datos personales, financieros, regulatorios y críticos.

## Implicaciones arquitectónicas
- El diseño considera clasificación de datos.
- La exposición es mínima y controlada.
- La protección no depende del entorno.

## Compensaciones (trade-offs)
Mayor esfuerzo de diseño y control, a cambio de menor impacto ante incidentes. -->

# Protección de Datos Sensibles

## Declaración del Principio

Los datos sensibles deben ser identificados, protegidos y expuestos de forma controlada durante todo su ciclo de vida.

## Propósito

Reducir el impacto de incidentes de seguridad y cumplir con requisitos regulatorios y de negocio.

## Justificación

No todos los datos tienen el mismo nivel de riesgo.
La arquitectura debe reconocer estas diferencias y tratarlas explícitamente, evitando exposiciones innecesarias.

## Alcance Conceptual

Aplica a:

- Datos en tránsito
- Datos en reposo
- Integraciones
- Observabilidad y logging

## Implicaciones Arquitectónicas

- La arquitectura debe clasificar los datos según su sensibilidad.
- El acceso a datos sensibles debe ser explícito y justificado.
- Se deben minimizar copias, exposiciones y propagación innecesaria.
- Los flujos de datos deben ser visibles y controlados.

## Compensaciones (Trade-offs)

Puede restringir el acceso y aumentar controles, a cambio de menor exposición y mayor cumplimiento normativo.

## Relación con Decisiones Arquitectónicas (ADRs)

Relacionado con ADRs sobre:

- Manejo y flujo de datos
- Integraciones
- Estrategias de protección y acceso





# Protección de Datos Sensibles

## Declaración del Principio

Los datos sensibles deben ser identificados, tratados y protegidos explícitamente en la arquitectura, controlando su exposición durante todo su ciclo de vida.

## Propósito

Reducir el impacto de incidentes de seguridad, proteger a la organización y a los usuarios, y facilitar el cumplimiento de requisitos regulatorios y de negocio.

## Justificación

No todos los datos presentan el mismo nivel de riesgo.
La arquitectura debe reconocer estas diferencias y tomar decisiones conscientes sobre cómo los datos son:

- creados
- transportados
- almacenados
- expuestos
- observados

La ausencia de un tratamiento diferenciado conduce a exposiciones innecesarias, mayor superficie de ataque y mayores costos ante incidentes.

## Alcance Conceptual

Este principio aplica a:

- Datos en tránsito entre componentes
- Datos en reposo
- Integraciones internas y externas
- Eventos, APIs y procesos batch
- Observabilidad, logging y trazabilidad

Aplica tanto a datos regulados como a información crítica para el negocio.

## Implicaciones Arquitectónicas

- La arquitectura debe clasificar los datos según su nivel de sensibilidad y riesgo.
- El acceso a datos sensibles debe ser intencional, explícito y justificable.
- Se deben minimizar copias, propagación y exposición innecesaria de datos.
- Los flujos de datos sensibles deben ser visibles y comprensibles a nivel arquitectónico.
- La observabilidad no debe exponer datos sensibles salvo justificación explícita.

## Compensaciones (Trade-offs)

Puede introducir restricciones de acceso y mayor esfuerzo de diseño, a cambio de reducir significativamente la exposición, el impacto de incidentes y el riesgo legal y reputacional.

## Relación con Decisiones Arquitectónicas (ADRs)

Este principio se refleja en ADRs relacionados con:

- Modelos de datos y su exposición
- Integraciones y contratos
- Estrategias de acceso y protección de información
- Manejo de datos en observabilidad y trazabilidad
