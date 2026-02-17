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

- [Introducir complejidad solo con beneficio claro y medible](../../estandares/arquitectura/complexity-analysis.md)
- [Documentar decisiones arquitectónicas de forma comprensible](../../estandares/documentacion/adr-template.md)
- [Preferir soluciones conocidas y estables sobre enfoques novedosos](../../estandares/arquitectura/technology-selection.md)
- [Minimizar dependencias innecesarias entre componentes](../../estandares/arquitectura/bounded-contexts.md)
- [Facilitar operación, monitoreo y evolución del sistema](../../estandares/observabilidad/observability.md)

## Referencias Relacionadas

- [Mantenibilidad y Extensibilidad](../../principios/01-mantenibilidad-y-extensibilidad.md)
- [Arquitectura Evolutiva](12-arquitectura-evolutiva.md)
- [Descomposición y Límites](02-descomposicion-y-limites.md)
