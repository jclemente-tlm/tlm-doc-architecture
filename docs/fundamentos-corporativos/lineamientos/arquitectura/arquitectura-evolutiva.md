---
id: arquitectura-evolutiva
sidebar_position: 9
title: Arquitectura Evolutiva
description: Enfoque arquitectónico que diseña sistemas preparados para cambiar de forma controlada a lo largo del tiempo, usando fitness functions para guiar la evolución.
tags: [lineamiento, arquitectura, evolutionary-architecture, mantenibilidad]
---

# Arquitectura Evolutiva

La arquitectura debe diseñarse para adaptarse al cambio de forma controlada, aceptando que requisitos, negocio y tecnología evolucionarán. Las arquitecturas que asumen estabilidad permanente se vuelven rígidas, costosas de modificar y desconectadas del negocio. Diseñar para la evolución significa crear estructuras que toleren cambios, errores y ajustes progresivos mediante fitness functions y revisión continua. El cambio no es una excepción, es una condición normal del sistema.

**Este lineamiento aplica a:** sistemas de larga vida, plataformas en crecimiento, arquitecturas con múltiples equipos, entornos tecnológicos cambiantes.

## Prácticas Obligatorias

- [Documentar decisiones con ADRs](../../estandares/gobierno/adr-management.md)
- [Implementar fitness functions](../../estandares/arquitectura/architecture-evolution.md#1-fitness-functions)
- [Realizar architecture reviews periódicos](../../estandares/gobierno/architecture-review-process.md#architecture-review)
- [Aplicar refactoring continuo](../../estandares/desarrollo/code-quality.md#3-refactoring-practices)
- [Diseñar con bajo acoplamiento para facilitar cambio incremental](../../estandares/arquitectura/architecture-principles.md#3-loose-coupling)
- [Priorizar reversibilidad de decisiones arquitectónicas](../../estandares/arquitectura/architecture-evolution.md#2-reversibility)
- [Evaluar y seleccionar tecnologías con criterios de longevidad](../../estandares/arquitectura/architecture-evolution.md#3-technology-selection)

## Referencias Relacionadas

- [Mantenibilidad y Extensibilidad](../../principios/04-mantenibilidad-y-extensibilidad.md)
- [Descomposición y Límites](descomposicion-y-limites.md)
- [Simplicidad Intencional](simplicidad-intencional.md)
