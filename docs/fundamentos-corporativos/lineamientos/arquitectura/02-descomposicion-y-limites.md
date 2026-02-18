---
id: descomposicion-y-limites
sidebar_position: 2
title: Descomposición y Límites
description: Cómo dividir sistemas en componentes con límites claros de responsabilidad
---

# Descomposición y Límites

Dividir sistemas en componentes con límites claros facilita el mantenimiento, la evolución independiente y la gobernanza efectiva. Límites mal definidos generan dependencias ocultas, god services y acoplamiento que dificulta la escalabilidad y autonomía de equipos. Una descomposición bien diseñada alinea capacidades de negocio con estructura técnica, permitiendo cambios localizados y despliegues independientes.

**Este lineamiento aplica a:** monolitos modulares, arquitecturas de microservicios, arquitecturas orientadas a eventos y sistemas legacy en evolución.

## Estándares Obligatorios

- [Identificar bounded contexts por capacidad de negocio](../../estandares/arquitectura/bounded-contexts.md)
- [Definir relaciones entre contextos con context mapping](../../estandares/arquitectura/context-mapping.md)
- [Establecer contratos explícitos en los límites](../../estandares/apis/api-contracts.md)
- [Gestionar dependencias y evitar ciclos](../../estandares/arquitectura/dependency-management.md)
- [Modelar descomposición con C4 Model](../../estandares/documentacion/c4-model.md)

## Referencias Relacionadas

- [Establecer contratos explícitos en los límites](../07-contratos-de-integracion.md)
