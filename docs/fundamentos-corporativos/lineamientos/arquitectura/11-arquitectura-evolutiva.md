---
id: arquitectura-evolutiva
sidebar_position: 11
title: Arquitectura Evolutiva
description: Enfoque arquitectónico que diseña sistemas preparados para cambiar de forma controlada a lo largo del tiempo, usando fitness functions para guiar la evolución.
tags: [lineamiento, arquitectura, evolutionary-architecture, mantenibilidad]
---

# Arquitectura Evolutiva

## Tipo de Lineamiento

**Lineamiento de Arquitectura** - Implementa el principio de [Mantenibilidad y Extensibilidad](../../principios/01-mantenibilidad-y-extensibilidad.md)

## 1. Declaración

La arquitectura debe diseñarse para adaptarse al cambio de forma controlada, aceptando que los requisitos, el negocio y la tecnología evolucionarán con el tiempo.

## 2. Justificación

Este principio busca permitir que el sistema incorpore cambios sin necesidad de rediseños completos, reduciendo el costo y el riesgo de la evolución.

Las arquitecturas que asumen estabilidad permanente tienden a volverse rígidas, costosas de modificar y desconectadas de las necesidades reales del negocio.

Diseñar para la evolución no significa anticipar todo, sino crear estructuras que toleren cambios, errores y ajustes progresivos.

El cambio no es una excepción, es una condición normal del sistema.

## 3. Alcance y Contexto

Aplica a:

- Sistemas de larga vida
- Plataformas en crecimiento
- Arquitecturas con múltiples equipos
- Entornos tecnológicos cambiantes

No implica ausencia de decisiones, sino decisiones conscientes sobre qué debe ser estable y qué puede cambiar.

## 4. Implicaciones

- Las decisiones arquitectónicas se revisan y ajustan en el tiempo.
- Se prioriza la reversibilidad de decisiones cuando es posible.
- Los límites y contratos ayudan a contener el impacto del cambio.
- La arquitectura admite refactorización y mejora continua.

**Compensaciones (Trade-offs):**

Puede implicar mayor disciplina en el diseño y gobierno arquitectónico, a cambio de menor rigidez, menor deuda estructural y mayor alineación con el negocio.
