---
id: arquitectura-limpia
sidebar_position: 11
title: Arquitectura Limpia
description: Patrón arquitectónico que separa las decisiones de negocio de los detalles técnicos, manteniendo el dominio independiente de frameworks e infraestructura.
tags: [lineamiento, arquitectura, clean-architecture, mantenibilidad]
---

# Arquitectura Limpia

La arquitectura debe separar claramente las decisiones de negocio de los detalles técnicos, permitiendo que el dominio evolucione independientemente de frameworks, infraestructura o tecnologías. Cuando las decisiones técnicas dominan la estructura, los cambios tecnológicos impactan directamente la lógica de negocio, incrementando costos y rigidez. La Arquitectura Limpia establece que el negocio es el eje central del diseño, y los detalles técnicos se adaptan a él, no al revés, preservando claridad del dominio y facilitando evolución a largo plazo.

**Este lineamiento aplica a:** sistemas con lógica de negocio relevante, soluciones con expectativa de evolución en el tiempo, arquitecturas donde se desea reducir dependencia tecnológica.

## Estándares Obligatorios

- [Aplicar arquitectura hexagonal (Ports & Adapters)](../../estandares/arquitectura/clean-architecture.md#1-hexagonal-architecture-ports-adapters)
- [Implementar dependency inversion principle](../../estandares/arquitectura/clean-architecture.md#2-dependency-inversion-principle-dip)
- [Separar capas de dominio, aplicación e infraestructura](../../estandares/arquitectura/clean-architecture.md#3-layered-architecture)
- [Mantener dominio libre de frameworks](../../estandares/arquitectura/clean-architecture.md#4-framework-independence)
- [Diseñar modelo de dominio rico](../../estandares/arquitectura/domain-modeling.md#1-domain-model)
- [Testear dominio de forma aislada](../../estandares/testing/unit-integration-testing.md#1-unit-testing)
- [Documentar estructura de capas con C4](../../estandares/documentacion/architecture-documentation.md#2-c4-model)

## Referencias Relacionadas

- [Mantenibilidad y Extensibilidad](../../principios/01-mantenibilidad-y-extensibilidad.md)
- [Modelado de Dominio](09-modelado-de-dominio.md)
- [Descomposición y Límites](02-descomposicion-y-limites.md)
