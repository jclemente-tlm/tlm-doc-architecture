---
id: simplicidad-intencional
sidebar_position: 10
title: Simplicidad Intencional
description: Práctica arquitectónica que evita sobreingeniería y complejidad innecesaria, manteniendo soluciones proporcionales al problema real.
tags: [lineamiento, arquitectura, simplicidad, YAGNI, KISS, mantenibilidad]
---

# Simplicidad Intencional

La arquitectura debe priorizar soluciones simples y comprensibles, incorporando complejidad únicamente cuando exista necesidad clara y justificada. La complejidad innecesaria genera fallos difíciles de diagnosticar, costos de mantenimiento elevados, dependencia de conocimiento especializado y riesgos operativos. Una arquitectura "elegante" pero difícil de operar termina siendo más costosa que una solución simple pero robusta. La simplicidad no significa falta de diseño, sino elección consciente de lo esencial con complejidad proporcional al problema.

**Este lineamiento aplica a:** selección de estilos arquitectónicos, nivel de distribución del sistema, cantidad de componentes y dependencias, modelos de integración, mecanismos de resiliencia y escalabilidad.

**No aplica a:** estructura interna de capas o separación de responsabilidades dentro de un servicio — ver [Arquitectura Limpia](./08-arquitectura-limpia.md).

## Estándares Obligatorios

- [Justificar complejidad con análisis cost-benefit](../../estandares/arquitectura/architecture-principles.md#6-complexity-analysis)
- [Aplicar principio YAGNI (You Aren't Gonna Need It)](../../estandares/arquitectura/architecture-principles.md#2-yagni-you-arent-gonna-need-it)
- [Aplicar principio KISS (Keep It Simple, Stupid)](../../estandares/arquitectura/architecture-principles.md#1-kiss-keep-it-simple-stupid)
- [Evaluar tecnologías con criterios objetivos](../../estandares/arquitectura/architecture-evolution.md#3-technology-selection)
- [Priorizar operabilidad y mantenibilidad](../../estandares/arquitectura/architecture-principles.md#5-operational-simplicity)
- [Medir simplicidad con métricas objetivas](../../estandares/arquitectura/architecture-principles.md#7-simplicity-metrics)

## Referencias Relacionadas

- [Mantenibilidad y Extensibilidad](../../principios/04-mantenibilidad-y-extensibilidad.md)
- [Arquitectura Evolutiva](09-arquitectura-evolutiva.md)
- [Descomposición y Límites](02-descomposicion-y-limites.md)
