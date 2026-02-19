---
id: estilo-y-enfoque-arquitectonico
sidebar_position: 1
title: Estilo y Enfoque Arquitectónico
description: Estilos arquitectónicos permitidos y criterios de selección
---

# Estilo y Enfoque Arquitectónico

La selección del estilo arquitectónico es una decisión estructural que impacta directamente la escalabilidad, mantenibilidad y agilidad del sistema. Elegir por moda tecnológica o sin análisis de contexto genera complejidad innecesaria y costos operativos evitables. Un estilo bien seleccionado y explícitamente documentado facilita la coherencia en decisiones técnicas y la evolución sostenible del sistema.

**Este lineamiento aplica a:** nuevas aplicaciones, evolución de sistemas existentes, integraciones entre sistemas y plataformas compartidas.

## Estándares Obligatorios

- [Documentar decisión de estilo en ADR](../../estandares/documentacion/architecture-documentation.md#3-architecture-decision-records-adrs)
- [Validar selección mediante architecture review](../../estandares/gobierno/architecture-governance.md#1-architecture-review)
- [Identificar bounded contexts si es arquitectura modular o distribuida](../../estandares/arquitectura/domain-modeling.md#4-bounded-contexts)
- [Modelar estructura arquitectónica con C4 Model](../../estandares/documentacion/architecture-documentation.md#2-c4-model)

## Referencias Relacionadas

- [Seleccionar estilo basado en contexto de negocio](../../estilos-arquitectonicos/)
- [Diseñar monolitos modulares para dominios acotados](../../estilos-arquitectonicos/monolito-modular.md)
- [Adoptar microservicios para dominios independientes](../../estilos-arquitectonicos/microservicios.md)
- [Implementar arquitectura orientada a eventos para desacoplamiento temporal](../../estilos-arquitectonicos/eventos.md)
