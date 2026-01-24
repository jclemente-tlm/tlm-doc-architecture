---
id: 02-microservicios
sidebar_position: 2
title: Microservicios
---

<!-- ## Principios

- Cada microservicio es autónomo y responsable de un único dominio.
- Comunicación preferente vía APIs bien definidas.
- Despliegue y escalado independientes.

## Buenas prácticas

- Usa contratos claros (OpenAPI, gRPC).
- Implementa observabilidad (logs, métricas, trazas).
- Maneja errores y timeouts de forma robusta.
- Automatiza pruebas y despliegues.
- Minimiza dependencias entre servicios. -->

# Arquitectura de Microservicios

## Enunciado

Un sistema puede descomponerse en servicios autónomos alineados a capacidades de negocio, capaces de evolucionar y desplegarse de forma independiente.

## Intención

Permitir escalabilidad técnica y organizacional en contextos donde el dominio y los equipos crecen de forma sostenida.

## Alcance conceptual

Aplica cuando existen dominios claramente separables y equipos con capacidad de asumir ownership técnico y funcional.

No es un principio obligatorio para todo sistema.

## Implicaciones arquitectónicas

- Los límites del sistema reflejan capacidades del negocio.
- Cada servicio asume responsabilidad completa sobre su evolución.
- La comunicación entre servicios se vuelve una preocupación arquitectónica central.
- El sistema se concibe como un ecosistema distribuido.

## Compensaciones (trade-offs)

Introduce mayor complejidad operativa y de coordinación a cambio de mayor autonomía, escalabilidad y velocidad de cambio.
