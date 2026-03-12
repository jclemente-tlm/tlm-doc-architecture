---
id: modelado-de-dominio
sidebar_position: 6
title: Modelado de Dominio
description: Arquitectura estructurada en torno al dominio del negocio
---

# Modelado de Dominio

La arquitectura debe estructurarse en torno al dominio del negocio, reflejando sus conceptos, reglas y límites. Cuando se define principalmente desde lo técnico, el sistema pierde significado para el negocio, se vuelve difícil de mantener y costoso de cambiar. Orientar la arquitectura al dominio modela explícitamente reglas, procesos y conceptos del negocio, reduciendo malentendidos entre equipos y facilitando evolución sostenible. El dominio es la fuente principal de decisiones arquitectónicas, no una consecuencia de ellas.

**Este lineamiento aplica a:** sistemas con lógica de negocio relevante o compleja, soluciones que evolucionan con el negocio, arquitecturas con múltiples equipos o dominios, plataformas donde el conocimiento del negocio es crítico.

## Prácticas Obligatorias

- [Identificar bounded contexts por capacidades de negocio](../../estandares/arquitectura/domain-modeling.md#4-bounded-contexts)
- [Establecer lenguaje ubicuo por contexto](../../estandares/arquitectura/domain-modeling.md#6-ubiquitous-language)
- [Diseñar modelo de dominio rico](../../estandares/arquitectura/domain-modeling.md#1-domain-model)
- [Definir agregados y límites transaccionales](../../estandares/arquitectura/domain-modeling.md#2-aggregates)
- [Distinguir entidades y value objects](../../estandares/arquitectura/domain-modeling.md#3-entities-value-objects)
- [Implementar domain events](../../estandares/arquitectura/domain-modeling.md#7-domain-events)

## Referencias Relacionadas

- [Descomposición y Límites](descomposicion-y-limites.md)
- [Autonomía de Servicios](autonomia-de-servicios.md)
- [APIs y Contratos](../integracion/apis-y-contratos.md)
