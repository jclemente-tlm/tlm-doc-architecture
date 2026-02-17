---
id: modelado-de-dominio
sidebar_position: 9
title: Modelado de Dominio
description: Arquitectura estructurada en torno al dominio del negocio
---

# Modelado de Dominio

La arquitectura debe estructurarse en torno al dominio del negocio, reflejando sus conceptos, reglas y límites. Cuando se define principalmente desde lo técnico, el sistema pierde significado para el negocio, se vuelve difícil de mantener y costoso de cambiar. Orientar la arquitectura al dominio modela explícitamente reglas, procesos y conceptos del negocio, reduciendo malentendidos entre equipos y facilitando evolución sostenible. El dominio es la fuente principal de decisiones arquitectónicas, no una consecuencia de ellas.

**Este lineamiento aplica a:** sistemas con lógica de negocio relevante o compleja, soluciones que evolucionan con el negocio, arquitecturas con múltiples equipos o dominios, plataformas donde el conocimiento del negocio es crítico.

## Estándares Obligatorios

- [Identificar bounded contexts por capacidades de negocio](../../estandares/arquitectura/bounded-contexts.md)
- [Definir lenguaje ubicuo compartido con el negocio](../../estandares/arquitectura/bounded-contexts.md#lenguaje-ubicuo)
- [Asignar responsabilidades según capacidades del dominio](../../estandares/arquitectura/bounded-contexts.md)
- [Documentar modelo de dominio en diagramas de contexto](../../estandares/documentacion/c4-model.md)
- [Evitar mezclar lógicas de dominios distintos](../../estandares/arquitectura/bounded-contexts.md#9-single-responsibility-principle)

## Referencias Relacionadas

- [Descomposición y Límites](02-descomposicion-y-limites.md)
- [Autonomía de Servicios](10-autonomia-de-servicios.md)
- [APIs y Contratos](07-apis-y-contratos.md)
