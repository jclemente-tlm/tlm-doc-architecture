---
id: simplicidad-intencional
sidebar_position: 13
title: Simplicidad Intencional
description: Práctica arquitectónica que evita sobreingeniería y complejidad innecesaria, manteniendo soluciones proporcionales al problema real.
tags: [lineamiento, arquitectura, simplicidad, YAGNI, KISS, mantenibilidad]
---

# Simplicidad Intencional

La arquitectura debe priorizar soluciones simples y comprensibles, incorporando complejidad únicamente cuando exista necesidad clara y justificada. La complejidad innecesaria genera fallos difíciles de diagnosticar, costos de mantenimiento elevados, dependencia de conocimiento especializado y riesgos operativos. Una arquitectura "elegante" pero difícil de operar termina siendo más costosa que una solución simple pero robusta. La simplicidad no significa falta de diseño, sino elección consciente de lo esencial con complejidad proporcional al problema.

**Este lineamiento aplica a:** selección de estilos arquitectónicos, nivel de distribución del sistema, cantidad de componentes y dependencias, modelos de integración, mecanismos de resiliencia y escalabilidad.

## Estándares Obligatorios

- [Justificar complejidad con análisis cost-benefit](../../estandares/arquitectura/complexity-analysis.md)
- [Aplicar principio YAGNI (You Aren't Gonna Need It)](../../estandares/arquitectura/yagni-principle.md)
- [Aplicar principio KISS (Keep It Simple, Stupid)](../../estandares/arquitectura/kiss-principle.md)
- [Evaluar tecnologías con criterios objetivos](../../estandares/arquitectura/technology-selection.md)
- [Validar simplicidad en architecture reviews](../../estandares/gobierno/architecture-review.md)
- [Minimizar dependencias entre componentes](../../estandares/arquitectura/loose-coupling.md)
- [Priorizar operabilidad y mantenibilidad](../../estandares/arquitectura/operational-simplicity.md)
- [Documentar decisiones de forma clara](../../estandares/documentacion/architecture-decision-records.md)

## Referencias Relacionadas

- [Mantenibilidad y Extensibilidad](../../principios/01-mantenibilidad-y-extensibilidad.md)
- [Arquitectura Evolutiva](12-arquitectura-evolutiva.md)
- [Descomposición y Límites](02-descomposicion-y-limites.md)
