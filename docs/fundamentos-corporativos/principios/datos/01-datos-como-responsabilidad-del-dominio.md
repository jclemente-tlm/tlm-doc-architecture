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
Cada dominio es responsable de sus datos y de la semántica asociada a ellos.

## Propósito
Establecer ownership claro sobre los datos, alineando su significado y uso con el dominio que los genera.

## Justificación
Cuando los datos se comparten sin responsabilidad clara, se pierde semántica, se incrementa el acoplamiento y se dificulta la evolución independiente de los sistemas.

## Alcance Conceptual
Aplica a sistemas con múltiples dominios o contextos.
No promueve silos aislados, sino responsabilidad explícita sobre los datos.

## Implicaciones Arquitectónicas
- El dominio define cómo se crean, interpretan y exponen los datos.
- No existen bases de datos compartidas por conveniencia.
- Los datos reflejan reglas y lenguaje del negocio.

## Compensaciones (Trade-offs)
Puede aumentar la duplicación controlada de datos, a cambio de mayor independencia, claridad semántica y evolución autónoma.

## Relación con Decisiones Arquitectónicas (ADRs)
Este principio suele reflejarse en decisiones relacionadas con separación de bases de datos, contratos de datos y mecanismos de integración entre dominios.
