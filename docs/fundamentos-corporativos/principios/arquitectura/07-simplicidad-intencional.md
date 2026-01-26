---
id: simplicidad-intencional
sidebar_position: 7
title: Simplicidad Intencional
description: Priorizar soluciones simples y comprensibles evitando sobreingeniería
---

# Simplicidad Intencional

## Declaración del Principio

La arquitectura debe priorizar soluciones simples y comprensibles, incorporando complejidad únicamente cuando exista una necesidad clara y justificada.

## Propósito

Evitar la sobreingeniería y construir sistemas sostenibles, mantenibles y entendibles a lo largo del tiempo, alineados con las capacidades reales del equipo y del negocio.

## Justificación

La complejidad innecesaria es una de las principales fuentes de:

- Fallos difíciles de diagnosticar
- Costos de mantenimiento elevados
- Dependencia excesiva de conocimiento especializado
- Riesgos operativos y de continuidad

Una arquitectura “elegante” pero difícil de operar o evolucionar termina siendo más costosa que una solución más simple pero robusta.

La simplicidad no significa falta de diseño, sino **elección consciente de lo esencial**.

## Alcance Conceptual

Este principio aplica a decisiones como:

- Selección de estilos arquitectónicos
- Nivel de distribución del sistema
- Cantidad de componentes y dependencias
- Modelos de integración
- Mecanismos de resiliencia y escalabilidad

No promueve soluciones simplistas, sino **complejidad proporcional al problema**.

## Implicaciones Arquitectónicas

- La complejidad debe introducirse solo cuando exista un beneficio claro y medible.
- Las decisiones arquitectónicas deben poder explicarse de forma comprensible a distintos roles.
- Se deben preferir soluciones conocidas, estables y bien entendidas antes que enfoques novedosos sin necesidad real.
- La arquitectura debe minimizar dependencias innecesarias entre componentes.
- El diseño debe facilitar la operación, el monitoreo y la evolución del sistema.

## Compensaciones (Trade-offs)

Puede limitar soluciones altamente sofisticadas o “óptimas” desde un punto de vista técnico, a cambio de mayor claridad, menor riesgo operativo y mayor sostenibilidad a largo plazo.

## Relación con Decisiones Arquitectónicas (ADRs)

Este principio suele reflejarse en ADRs relacionados con:

- Elección de estilos arquitectónicos
- Nivel de distribución del sistema
- Introducción (o no) de nuevas tecnologías
- Decisiones de escalabilidad y resiliencia
