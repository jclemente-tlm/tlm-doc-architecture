---
id: diseno-orientado-al-dominio
sidebar_position: 2
title: Diseño Orientado al Dominio (DDD)
description: Arquitectura estructurada en torno al dominio del negocio
---

# Diseño Orientado al Dominio (DDD)

## 1. Declaración del Principio

La arquitectura debe estructurarse en torno al dominio del negocio, reflejando sus conceptos, reglas y límites, y no únicamente consideraciones técnicas.

## 2. Propósito

Alinear el diseño del sistema con el negocio, facilitando la comprensión, evolución y sostenibilidad de la solución en el tiempo.

## 3. Justificación

Cuando la arquitectura se define principalmente desde lo técnico, el sistema pierde significado para el negocio, se vuelve difícil de mantener y costoso de cambiar.

El Diseño Orientado al Dominio promueve que el software modele explícitamente las reglas, procesos y conceptos relevantes del negocio, reduciendo malentendidos entre equipos técnicos y no técnicos.

El dominio es la fuente principal de decisiones arquitectónicas, no una consecuencia de ellas.

## 4. Alcance Conceptual

Aplica a:

- Sistemas con lógica de negocio relevante o compleja
- Soluciones que evolucionan con el negocio
- Arquitecturas con múltiples equipos o dominios
- Plataformas donde el conocimiento del negocio es crítico

No implica el uso obligatorio de patrones o tácticas específicas de DDD, sino una orientación conceptual al dominio.

## 5. Implicaciones Arquitectónicas

- Los límites del sistema reflejan contextos del dominio.
- El lenguaje utilizado en el diseño y la comunicación es consistente con el negocio.
- Las responsabilidades se asignan según capacidades del dominio.
- La arquitectura evita mezclar lógicas de dominios distintos.

## 6. Compensaciones (Trade-offs)

Requiere mayor esfuerzo inicial de análisis y colaboración con el negocio, a cambio de mayor claridad, menor deuda conceptual y una arquitectura más adaptable al cambio.

## 7. Relación con Decisiones Arquitectónicas (ADRs)

Este principio se refleja en ADRs relacionados con:

- Identificación de dominios y contextos
- Definición de límites entre componentes o servicios
- Asignación de responsabilidades
- Estrategias de integración entre dominios
