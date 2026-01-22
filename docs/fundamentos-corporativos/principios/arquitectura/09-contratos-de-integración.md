<!-- ## Propósito

## Declaración del principio

## Justificación

## Implicancias arquitectónicas

## Relación con ADRs

## Ejemplos (alto nivel) -->

# Contratos de Integración

## Enunciado
Las interacciones entre sistemas deben definirse mediante contratos explícitos, estables y versionables.

## Intención
Reducir acoplamiento implícito y permitir evolución independiente entre productores y consumidores.

## Alcance conceptual
Aplica a toda integración entre sistemas, servicios o componentes externos al dominio inmediato.

## Implicaciones arquitectónicas
- Las integraciones se diseñan como acuerdos formales.
- Los cambios deben considerar compatibilidad.
- La comunicación se gobierna, no se improvisa.
- Los contratos son parte de la arquitectura.

## Compensaciones (trade-offs)
Requiere mayor disciplina y gobierno, a cambio de integraciones más estables, predecibles y escalables.
