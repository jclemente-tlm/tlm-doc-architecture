<!-- # Defensa en Profundidad

## Enunciado
La seguridad debe implementarse en múltiples capas complementarias.

## Intención
Reducir el impacto de fallos individuales de seguridad.

## Alcance conceptual
Aplica a arquitectura, infraestructura y aplicaciones.

## Implicaciones arquitectónicas
- Los controles no son únicos ni aislados.
- El fallo de una capa no compromete todo el sistema.
- La seguridad es redundante por diseño.

## Compensaciones (trade-offs)
Mayor complejidad y costos operativos, a cambio de mayor robustez ante ataques. -->


# Defensa en Profundidad

## Declaración del Principio

La seguridad debe implementarse mediante múltiples capas complementarias, evitando dependencias en un único mecanismo de control.

## Propósito

Aumentar la resiliencia ante fallos de seguridad, errores humanos o vulnerabilidades no detectadas.

## Justificación

Ningún control es infalible.
Confiar en una sola barrera de protección expone al sistema a fallos catastróficos cuando dicho control es superado.

La arquitectura debe asumir que los controles pueden fallar.

## Alcance Conceptual

Aplica a:

- Accesos
- Comunicación
- Manejo de datos
- Exposición de servicios

No implica redundancia innecesaria, sino capas con responsabilidades claras.

## Implicaciones Arquitectónicas

- Los controles de seguridad se distribuyen en diferentes niveles.
- El fallo de un control no debe comprometer todo el sistema.
- Las capas deben ser independientes y complementarias.
- La arquitectura debe evitar puntos únicos de fallo en seguridad.

## Compensaciones (Trade-offs)

Incrementa la complejidad del diseño y la coordinación entre capas, a cambio de una reducción significativa del riesgo sistémico.

## Relación con Decisiones Arquitectónicas (ADRs)

Relacionado con ADRs sobre:

- Segmentación de componentes
- Controles de acceso
- Manejo de errores y validaciones


# Defensa en Profundidad

## Declaración del Principio
La seguridad debe diseñarse mediante múltiples capas complementarias, de modo que la falla de un único control no comprometa todo el sistema.

## Propósito
Reducir el impacto de vulnerabilidades, errores humanos o fallos de configuración, evitando dependencias críticas en un solo mecanismo de seguridad.

## Justificación
Ningún control de seguridad es infalible.
Las arquitecturas que dependen de una única barrera de protección presentan un alto riesgo sistémico cuando dicha barrera es superada.

La defensa en profundidad asume que los controles pueden fallar y diseña la arquitectura para contener y limitar el impacto de esos fallos.

## Alcance Conceptual
Este principio aplica a decisiones arquitectónicas relacionadas con:
- Acceso a sistemas y recursos
- Comunicación entre componentes
- Manejo y exposición de datos
- Publicación de capacidades y servicios

No implica duplicación innecesaria de controles, sino la definición consciente de capas con responsabilidades diferenciadas.

## Implicaciones Arquitectónicas
- Los controles de seguridad deben distribuirse en distintos niveles de la arquitectura.
- El fallo de una capa no debe permitir el compromiso total del sistema.
- Las capas deben ser independientes y complementarias.
- La arquitectura debe evitar puntos únicos de fallo relacionados con seguridad.

## Compensaciones (Trade-offs)
Introduce mayor complejidad en el diseño y coordinación de controles, a cambio de una reducción significativa del riesgo y una mayor capacidad de contención ante incidentes.

## Relación con Decisiones Arquitectónicas (ADRs)
Este principio suele reflejarse en ADRs relacionados con:
- Segmentación de sistemas y componentes
- Estrategias de control de acceso
- Definición de límites y validaciones entre capas
