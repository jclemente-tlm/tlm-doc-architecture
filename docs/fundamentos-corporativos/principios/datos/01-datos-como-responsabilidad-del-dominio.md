<!-- ## Propósito

## Declaración del principio

## Justificación

## Implicancias arquitectónicas

## Relación con ADRs

## Ejemplos (alto nivel) -->
<!--
# Datos como Responsabilidad del Dominio

## Enunciado
Cada dominio es responsable de sus datos y de la semántica asociada a ellos.

## Intención
Evitar modelos de datos compartidos que generen acoplamiento y pérdida de significado.

## Alcance conceptual
Aplica a sistemas con múltiples dominios o contextos.
No promueve silos aislados, sino ownership claro.

## Implicaciones arquitectónicas
- El dominio define cómo se crean, interpretan y exponen los datos.
- No existen bases de datos compartidas por conveniencia.
- Los datos reflejan reglas de negocio.

## Compensaciones (trade-offs)
Puede aumentar la duplicación controlada de datos, a cambio de mayor independencia y claridad semántica. -->

# Datos como Responsabilidad del Dominio

## Declaración del Principio

Cada dominio es responsable de los datos que produce, gestiona y expone, así como del significado y las reglas asociadas a ellos.

## Propósito

Evitar acoplamientos innecesarios, pérdida de significado y dependencias implícitas entre dominios a través de modelos de datos compartidos.

## Justificación

Cuando los datos son tratados como un recurso común sin un responsable claro, se generan:

- Ambigüedad semántica
- Dependencias frágiles entre sistemas
- Dificultad para evolucionar modelos de negocio

Asignar ownership explícito a los datos permite que los sistemas evolucionen de forma más independiente y alineada al negocio.

## Alcance Conceptual

Aplica a:

- Sistemas con múltiples dominios o contextos
- Arquitecturas distribuidas
- Integraciones internas y externas
- Flujos de datos operacionales y analíticos

No promueve silos aislados, sino responsabilidad clara sobre los datos.

## Implicaciones Arquitectónicas

- Cada dominio define cómo se crean, interpretan y exponen sus datos.
- No deben existir bases de datos compartidas por conveniencia.
- Los datos reflejan reglas y lenguaje del dominio.
- El acceso a datos de otro dominio se realiza mediante contratos explícitos.

## Compensaciones (Trade-offs)

Puede generar duplicación controlada de datos, a cambio de mayor autonomía, claridad semántica y capacidad de evolución.

## Relación con Decisiones Arquitectónicas (ADRs)

Este principio se refleja en ADRs relacionados con:

- Separación de dominios
- Estrategias de integración de datos
- Ownership y límites de responsabilidad
