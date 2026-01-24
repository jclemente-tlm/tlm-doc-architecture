<!-- # Zero Trust

## Enunciado
Ningún componente, usuario o sistema es confiable por defecto.

## Intención
Eliminar supuestos implícitos de confianza basados en red o ubicación.

## Alcance conceptual
Aplica especialmente en sistemas distribuidos y multi-entorno.

## Implicaciones arquitectónicas
- Toda interacción requiere verificación.
- La confianza es contextual y temporal.
- Los límites de confianza son explícitos.

## Compensaciones (trade-offs)
Incrementa validaciones y controles, a cambio de mayor seguridad y trazabilidad. -->


# Zero Trust

## Declaración del Principio
Ningún componente, usuario o sistema debe considerarse confiable por defecto, independientemente de su ubicación, red o entorno de ejecución.

## Propósito
Eliminar supuestos implícitos de confianza y reducir el riesgo de accesos indebidos o propagación de incidentes dentro del sistema.

## Justificación
En arquitecturas modernas, los sistemas están compuestos por múltiples componentes, servicios e integraciones que interactúan entre sí de forma continua.

Asumir confianza implícita —por estar “dentro” de la red o del sistema— aumenta el impacto de errores, configuraciones incorrectas o accesos no autorizados.

Zero Trust establece que la confianza debe ser siempre explícita, validada y limitada al contexto de cada interacción.

## Alcance Conceptual
Este principio aplica a:
- Comunicación entre componentes y servicios
- Acceso a datos y recursos
- Integraciones internas y externas
- Sistemas distribuidos, multi-entorno y multi-tenant

## Implicaciones Arquitectónicas
- Toda interacción debe ser evaluada antes de otorgar acceso.
- La confianza no es permanente ni global.
- Los límites de confianza deben ser claros y explícitos.
- La arquitectura no debe depender de redes o zonas “confiables”.

## Compensaciones (Trade-offs)
Puede aumentar la cantidad de validaciones y controles necesarios, a cambio de una reducción significativa del impacto de fallos de seguridad y una mayor trazabilidad de accesos.

## Relación con Decisiones Arquitectónicas (ADRs)
Este principio suele reflejarse en ADRs relacionados con:
- Definición de límites de confianza
- Modelos de acceso entre componentes
- Estrategias de autenticación y autorización
