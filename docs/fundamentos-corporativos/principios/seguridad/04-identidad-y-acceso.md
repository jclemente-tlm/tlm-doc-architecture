# Identidad y Acceso Explícitos

## Declaración del Principio

La arquitectura debe definir explícitamente qué identidades existen (usuarios, servicios, sistemas) y qué accesos tienen a recursos, asegurando que toda interacción sea autenticada, autorizada y trazable.

## Propósito

Controlar explícitamente quién (humano o no-humano) puede acceder a qué recursos, bajo qué condiciones y durante cuánto tiempo, reduciendo el riesgo de accesos indebidos y facilitando la auditoría.

> **Relación:** Este principio materializa [Zero Trust](02-zero-trust.md) mediante control explícito de identidades y [Mínimo Privilegio](06-minimo-privilegio.md) mediante restricción de accesos.

## Justificación

En arquitecturas modernas, no solo los usuarios humanos acceden a los sistemas.
Servicios, aplicaciones, procesos automatizados e integraciones externas también requieren identidad y permisos.

Sin definición explícita de identidades y accesos:

- Los permisos tienden a crecer sin control
- Se generan accesos implícitos difíciles de auditar
- Los incidentes se vuelven complejos de investigar y contener

La gestión de identidades y accesos establece una base estructural para aplicar seguridad de forma consistente y gobernable.

## Alcance Conceptual

Este principio aplica a:

- Usuarios humanos
- Servicios y componentes internos
- Integraciones y sistemas externos
- Procesos automatizados y cuentas técnicas

Incluye tanto accesos a servicios como a datos, APIs, eventos y recursos críticos.

## Implicaciones Arquitectónicas

- Toda entidad que interactúa con el sistema debe tener una identidad definida.
- Los accesos deben otorgarse explícitamente y de forma controlada.
- La autenticación y autorización deben considerarse capacidades arquitectónicas.
- Los permisos deben ser trazables, revisables y revocables.
- La arquitectura debe evitar accesos implícitos o compartidos.

## Compensaciones (Trade-offs)

Requiere mayor esfuerzo inicial de diseño y gobierno, a cambio de mayor control, auditabilidad, reducción de riesgo y capacidad de respuesta ante incidentes de seguridad.

## Relación con Decisiones Arquitectónicas (ADRs)

Este principio se materializa en ADRs relacionados con:

- Modelos de identidad y autenticación
- Estrategias de autorización y control de acceso
- Manejo de identidades no humanas
- Integración con sistemas de identidad corporativos
