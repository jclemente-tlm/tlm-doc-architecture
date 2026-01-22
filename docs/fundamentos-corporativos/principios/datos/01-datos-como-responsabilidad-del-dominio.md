<!-- ## Propósito

## Declaración del principio

## Justificación

## Implicancias arquitectónicas

## Relación con ADRs

## Ejemplos (alto nivel) -->

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
Puede aumentar la duplicación controlada de datos, a cambio de mayor independencia y claridad semántica.
