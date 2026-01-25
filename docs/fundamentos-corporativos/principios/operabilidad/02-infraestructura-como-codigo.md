# Infraestructura como Código

## Declaración del Principio

La infraestructura debe definirse, versionarse y gestionarse como parte del sistema, utilizando mecanismos declarativos y reproducibles.

## Propósito

Garantizar consistencia, trazabilidad y control sobre los entornos donde operan los sistemas.

## Justificación

La infraestructura configurada manualmente es difícil de auditar, reproducir y mantener.
Esto genera diferencias entre entornos, errores difíciles de diagnosticar y dependencia de conocimiento no documentado.

Tratar la infraestructura como código permite aplicar los mismos principios de calidad, revisión y control que al software.

## Alcance Conceptual

Aplica a:

- Entornos de desarrollo, prueba y producción
- Configuración de recursos
- Dependencias de infraestructura
- Políticas y controles asociados al entorno

No se limita a una tecnología específica, sino a una forma de gestionar la infraestructura.

## Implicaciones Arquitectónicas

- Los entornos deben poder recrearse de forma consistente.
- Los cambios en infraestructura deben ser explícitos y versionados.
- La arquitectura debe evitar configuraciones manuales no controladas.
- La infraestructura forma parte del ciclo de vida del sistema.

## Compensaciones (Trade-offs)

Puede aumentar la complejidad inicial de adopción, a cambio de mayor control, auditabilidad y reducción de errores operativos.

## Relación con Decisiones Arquitectónicas (ADRs)

Relacionado con ADRs sobre:

- Estrategias de provisión de entornos
- Gestión de configuración
- Separación de responsabilidades entre equipos
