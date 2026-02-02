---
id: autonomia-de-servicios
sidebar_position: 4
title: Autonomía de Servicios
description: Servicios capaces de evolucionar, desplegarse y operar de forma independiente
---

# Autonomía de Servicios

## 1. Declaración

Los servicios deben ser autónomos, capaces de evolucionar, desplegarse y operar de forma independiente sin requerir coordinación sincronizada con otros servicios.

## 2. Justificación

Este principio busca maximizar la capacidad de evolución independiente de servicios, permitiendo que equipos entreguen valor de forma continua sin coordinaciones complejas.

La autonomía permite que cada servicio asuma responsabilidad completa sobre su comportamiento, sus datos, su evolución y su ciclo de vida, reduciendo dependencias operativas y organizacionales.

Sin autonomía:

- Los despliegues requieren coordinación entre múltiples equipos
- Los cambios quedan bloqueados por dependencias externas
- Los equipos no pueden iterar a su propio ritmo
- La escalabilidad organizacional se ve limitada

La autonomía no significa aislamiento total, sino capacidad de tomar decisiones y ejecutar cambios dentro del ámbito del servicio sin afectar a otros.

## 3. Alcance y Contexto

Aplica a:

- Servicios en arquitecturas de microservicios
- Bounded contexts en DDD
- Componentes modulares con ciclos de vida independientes
- Equipos autónomos con responsabilidad end-to-end

La autonomía se evalúa en múltiples dimensiones: despliegue, datos, decisiones técnicas y gobierno.

## 4. Implicaciones

- Cada servicio debe tener ownership completo sobre sus datos (ver [Propiedad de Datos](../../datos/01-propiedad-de-datos.md)).
- Los servicios deben poder desplegarse independientemente sin coordinar con otros.
- Los equipos deben tener autoridad para tomar decisiones técnicas dentro de su ámbito.
- La comunicación entre servicios debe ser asíncrona cuando sea posible.
- Cada servicio debe ser capaz de operar en modo degradado si sus dependencias fallan.

**Compensaciones (Trade-offs):**

Puede generar duplicación controlada de capacidades y mayor complejidad de gobierno distribuido, a cambio de mayor velocidad de entrega, escalabilidad organizacional y resiliencia operativa.
