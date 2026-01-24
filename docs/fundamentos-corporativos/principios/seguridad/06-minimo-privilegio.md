<!-- # Mínimo Privilegio

## Enunciado
Todo acceso debe otorgarse con el menor privilegio necesario para cumplir su función.

## Intención
Reducir el impacto de accesos indebidos o comprometidos.

## Alcance conceptual
Aplica a usuarios, servicios y procesos automatizados.

## Implicaciones arquitectónicas
- Los permisos son explícitos y limitados.
- El acceso se revisa y ajusta.
- No existen privilegios implícitos.

## Compensaciones (trade-offs)
Incrementa esfuerzo de gestión de accesos, a cambio de mayor seguridad y control. -->

# Mínimo Privilegio

## Declaración del Principio

Todo actor del sistema debe operar con el nivel mínimo de permisos necesarios para cumplir su función.

## Propósito

Limitar el impacto de errores, accesos indebidos o compromisos de seguridad.

## Justificación

Los permisos excesivos amplifican el daño potencial de incidentes y dificultan la auditoría y el control.

El acceso debe concederse por necesidad, no por conveniencia.

## Alcance Conceptual

Aplica a:

- Usuarios
- Servicios
- Integraciones
- Procesos automatizados

## Implicaciones Arquitectónicas

- Los permisos deben ser explícitos y revisables.
- No se permiten accesos globales sin justificación arquitectónica.
- La arquitectura debe facilitar la segregación de responsabilidades.

## Compensaciones (Trade-offs)

Puede incrementar la gestión de permisos y revisiones, a cambio de mayor control y reducción significativa del riesgo.

## Relación con Decisiones Arquitectónicas (ADRs)

Este principio suele reflejarse en ADRs sobre:

- Autorización
- Segmentación
- Modelos de acceso

# Mínimo Privilegio

## Declaración del Principio

Todo actor del sistema debe operar únicamente con los permisos estrictamente necesarios para cumplir su función.

## Propósito

Reducir el impacto de errores, accesos indebidos o compromisos de seguridad, limitando el alcance de las acciones que cada actor puede realizar.

## Justificación

Los permisos excesivos incrementan el riesgo y amplifican las consecuencias de incidentes de seguridad, errores humanos o fallas técnicas.

El acceso debe otorgarse por necesidad funcional y de forma deliberada, no por conveniencia ni por defecto.

## Alcance Conceptual

Este principio aplica a:

- Usuarios finales y administrativos
- Servicios y microservicios
- Integraciones entre sistemas
- Procesos automatizados y jobs
- Infraestructura y componentes de plataforma

## Implicaciones Arquitectónicas

- Los permisos deben ser explícitos, definidos y documentados.
- No deben existir accesos implícitos ni privilegios heredados sin justificación.
- La arquitectura debe permitir la segregación de responsabilidades.
- Los accesos deben poder revisarse, auditarse y ajustarse de forma controlada.

## Compensaciones

La aplicación estricta de este principio puede aumentar el esfuerzo de gestión y revisión de accesos, a cambio de un mayor nivel de control, trazabilidad y reducción significativa del riesgo.

## Relación con Decisiones Arquitectónicas (ADRs)

Este principio suele materializarse en ADRs relacionados con:

- Modelos de autorización
- Gestión de identidades y accesos
- Segmentación de responsabilidades
- Diseño de permisos en servicios e integraciones
