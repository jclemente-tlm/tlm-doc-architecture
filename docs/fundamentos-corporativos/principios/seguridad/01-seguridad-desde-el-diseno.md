---
id: seguridad-desde-el-diseno
sidebar_position: 1
title: Seguridad desde el Diseño
description: Seguridad como consideración explícita desde decisiones iniciales
---

# Seguridad desde el Diseño

## 1. Declaración

La seguridad debe ser una consideración explícita desde las decisiones arquitectónicas iniciales del sistema y no incorporarse posteriormente como controles aislados o correctivos.

## 2. Justificación

Este principio busca reducir riesgos previsibles desde la estructura del sistema, evitando arquitecturas que dependan exclusivamente de configuraciones tardías o medidas reactivas.

Las decisiones arquitectónicas definen aspectos fundamentales del sistema, como:

- Qué componentes existen y cómo se relacionan
- Qué capacidades se exponen y a quién
- Cómo circulan los datos dentro y fuera del sistema
- Dónde se establecen los límites de confianza

Si estos elementos se diseñan sin considerar seguridad, los controles añadidos posteriormente solo mitigan síntomas y no las causas del riesgo, generando soluciones frágiles, costosas de mantener y difíciles de corregir.

## 3. Alcance y Contexto

Aplica a decisiones relacionadas con:

- Definición de componentes, responsabilidades y dependencias
- Exposición de servicios, APIs, eventos e integraciones
- Flujo, persistencia y acceso a datos
- Identificación de activos críticos y puntos de entrada al sistema

Este principio no reemplaza controles técnicos específicos, sino que establece el marco arquitectónico que permite que dichos controles sean coherentes, efectivos y sostenibles.

## 4. Implicaciones

- Los componentes y datos críticos deben identificarse desde el diseño.
- Los límites y relaciones de confianza deben definirse de forma explícita.
- La exposición de capacidades debe ser intencional y mínima.
- La arquitectura debe reducir la superficie de ataque por diseño.
- Deben considerarse escenarios de uso indebido y abuso desde la etapa de definición arquitectónica.

**Compensaciones (Trade-offs):**

Requiere mayor análisis y alineación en etapas tempranas del diseño, a cambio de una reducción significativa del riesgo, menor deuda técnica en seguridad y menores costos de corrección en fases posteriores.
