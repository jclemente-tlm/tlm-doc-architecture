---
id: 02-arquitectura-de-microservicios
sidebar_position: 2
# title: Arquitectura de Microservicios
---

# Arquitectura de Microservicios

## Declaración del Principio

Un sistema puede descomponerse en servicios autónomos, alineados a capacidades de negocio, que pueden evolucionar y desplegarse de forma independiente.

## Propósito

Habilitar escalabilidad técnica y organizacional, reducir el impacto de cambios y permitir que distintos equipos trabajen de forma autónoma sobre un mismo ecosistema.

## Justificación

En sistemas grandes o en crecimiento, las arquitecturas monolíticas tienden a:

- Limitar la velocidad de cambio
- Aumentar el impacto de errores
- Generar dependencias difíciles de gestionar entre equipos

La arquitectura de microservicios permite aislar responsabilidades, reducir el radio de impacto de los cambios y escalar tanto la plataforma como la organización de forma controlada.

No es una solución universal ni obligatoria, sino una respuesta arquitectónica a contextos específicos de complejidad y crecimiento.

## Alcance Conceptual

Aplica principalmente cuando existen:

- Dominios o capacidades de negocio claramente separables
- Necesidad de escalabilidad independiente
- Múltiples equipos con ownership técnico y funcional
- Evolución continua del sistema

No todos los sistemas deben adoptar microservicios; en dominios simples o equipos pequeños, otros estilos pueden ser más adecuados.

## Implicaciones Arquitectónicas

- Cada servicio representa una capacidad clara del negocio.
- Los servicios son autónomos en despliegue y evolución.
- Cada servicio es responsable de sus propios datos.
- No se permite acceso directo a datos de otros servicios.
- La comunicación entre servicios se realiza mediante contratos explícitos.
- La observabilidad y la resiliencia son preocupaciones centrales del diseño.

## Compensaciones (Trade-offs)

Introduce mayor complejidad operativa, de monitoreo y de coordinación entre equipos, a cambio de mayor autonomía, escalabilidad y capacidad de evolución del sistema a largo plazo.

## Relación con Decisiones Arquitectónicas (ADRs)

Este principio se refleja en ADRs relacionados con:

- Descomposición del sistema
- Definición de límites de servicio
- Estrategias de comunicación síncrona y asíncrona
- Gobierno de datos y contratos de integración
