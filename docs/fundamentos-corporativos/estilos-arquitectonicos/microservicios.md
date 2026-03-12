---
id: microservicios
sidebar_position: 2
title: Arquitectura de Microservicios
description: Estilo de servicios independientes con dominios acotados y escalabilidad diferenciada
---

# Arquitectura de Microservicios

> **Tipo:** Estilo Arquitectónico Contextual
> **Aplicabilidad:** Sistemas con dominios independientes, múltiples equipos y necesidad de escalabilidad diferenciada

## Declaración del Estilo

Un sistema puede descomponerse en servicios autónomos, alineados a capacidades de negocio, que pueden evolucionar y desplegarse de forma independiente.

## Principios que Materializa

Este estilo arquitectónico implementa los siguientes principios corporativos:

- ✅ [Autonomía de Servicios](../../fundamentos-corporativos/lineamientos/arquitectura/autonomia-de-servicios.md)
- ✅ [Arquitectura Evolutiva](../../fundamentos-corporativos/lineamientos/arquitectura/arquitectura-evolutiva.md)
- ✅ [Diseño Orientado al Dominio](../../fundamentos-corporativos/lineamientos/arquitectura/modelado-de-dominio.md)

## Propósito

Habilitar escalabilidad técnica y organizacional, reducir el impacto de cambios y permitir que distintos equipos trabajen de forma autónoma sobre un mismo ecosistema.

## Cuándo Usar este Estilo

✅ **Aplicar cuando:**

- Existen dominios o capacidades de negocio claramente separables
- Se requiere escalabilidad independiente por servicio
- Múltiples equipos con ownership técnico y funcional
- Evolución continua del sistema
- Alto volumen de cambios frecuentes

❌ **NO aplicar cuando:**

- Dominios simples o equipos pequeños (< 10 personas)
- Baja frecuencia de cambios
- Infraestructura o capacidades DevOps inmaduras
- Complejidad no justificada por el valor de negocio

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

## Características del Estilo

- Cada servicio representa una capacidad clara del negocio
- Los servicios son autónomos en despliegue y evolución
- Cada servicio es responsable de sus propios datos (no compartir BD)
- No se permite acceso directo a datos de otros servicios
- La comunicación entre servicios se realiza mediante contratos explícitos
- La observabilidad y la resiliencia son preocupaciones centrales del diseño
- Cada servicio puede evolucionar tecnológicamente de forma independiente

## Compensaciones (Trade-offs)

Introduce mayor complejidad operativa, de monitoreo y de coordinación entre equipos, a cambio de mayor autonomía, escalabilidad y capacidad de evolución del sistema a largo plazo.

## Relación con Decisiones Arquitectónicas (ADRs)

Este principio se refleja en ADRs relacionados con:

- Descomposición del sistema
- Definición de límites de servicio
- Estrategias de comunicación síncrona y asíncrona
- Gobierno de datos y contratos de integración
