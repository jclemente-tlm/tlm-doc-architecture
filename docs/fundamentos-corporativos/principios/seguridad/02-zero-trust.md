---
sidebar_position: 2
---

# Zero Trust

## Declaración del Principio

Ningún componente, usuario o sistema es confiable por defecto; toda interacción debe evaluarse explícitamente, independientemente de su origen o ubicación.

## Propósito

Eliminar supuestos implícitos de confianza y reducir el riesgo de accesos indebidos, movimientos laterales y propagación de incidentes dentro de la arquitectura.

## Justificación

Las arquitecturas modernas están compuestas por múltiples servicios, componentes, usuarios e integraciones que interactúan de forma continua y distribuida.

Asumir confianza implícita —por pertenecer a una red, entorno o sistema— amplifica el impacto de errores, configuraciones incorrectas o compromisos de seguridad.

El enfoque Zero Trust establece que la confianza no se presume: se define, se valida y se limita según el contexto de cada interacción.

## Alcance Conceptual

Este principio aplica a:

- Interacciones entre componentes y servicios
- Acceso de usuarios y sistemas a recursos
- Integraciones internas y externas
- Arquitecturas distribuidas, multi-entorno y multi-tenant

Zero Trust no depende de un mecanismo específico, sino de un modelo coherente de control y verificación.

## Implicaciones Arquitectónicas

- Toda interacción debe estar sujeta a verificación explícita.
- La confianza es contextual, limitada y no permanente.
- Los límites de confianza deben definirse de forma clara en la arquitectura.
- La arquitectura no debe basarse en redes, zonas o entornos considerados implícitamente confiables.
- El acceso debe evaluarse según identidad, contexto y propósito.

## Compensaciones (Trade-offs)

Incrementa la necesidad de controles, validaciones y diseño explícito de accesos, a cambio de una reducción significativa del impacto de incidentes y una mayor trazabilidad y control.

## Relación con Decisiones Arquitectónicas (ADRs)

Este principio se refleja comúnmente en ADRs relacionados con:

- Definición de límites de confianza
- Modelos de autenticación y autorización
- Estrategias de acceso entre servicios y dominios
- Segmentación lógica y control de identidades
