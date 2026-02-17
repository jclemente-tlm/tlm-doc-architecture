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

- [Separar lógica de negocio de frameworks e infraestructura](../../estandares/arquitectura/bounded-contexts.md)
- [Orientar dependencias hacia el dominio, no hacia detalles técnicos](../../estandares/arquitectura/dependency-inversion.md)
- [Limitar impacto de cambios tecnológicos en el núcleo del sistema](../../estandares/arquitectura/hexagonal-architecture.md)
- [Estructurar sistema reflejando prioridades del negocio](../../estandares/arquitectura/bounded-contexts.md)
- [Documentar capas y responsabilidades arquitectónicas](../../estandares/documentacion/c4-model.md)

## Referencias Relacionadas

- [Mantenibilidad y Extensibilidad](../../principios/01-mantenibilidad-y-extensibilidad.md)
- [Modelado de Dominio](09-modelado-de-dominio.md)
- [Descomposición y Límites](02-descomposicion-y-limites.md)
