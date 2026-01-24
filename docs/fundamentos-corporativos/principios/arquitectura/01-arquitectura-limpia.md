---
id: 01-clean-architecture
sidebar_position: 1
title: Clean Architecture
---

<!-- ## Principios

- Separación clara de responsabilidades (capas: dominio, aplicación, infraestructura, presentación).
- Las dependencias siempre apuntan hacia el dominio.
- Entidades y lógica de negocio independientes de frameworks.

## Buenas prácticas

- Usa interfaces para desacoplar dependencias.
- Mantén el dominio libre de detalles técnicos.
- Aplica inyección de dependencias.
- Escribe pruebas unitarias para el dominio. -->

# Arquitectura Limpia

## Enunciado
La arquitectura debe proteger el núcleo del negocio de dependencias técnicas, organizando el sistema alrededor del dominio y no de frameworks o tecnologías.

## Intención
Evitar que decisiones técnicas tempranas limiten la evolución del negocio y reducir el costo de cambio ante nuevas necesidades funcionales o tecnológicas.

## Alcance conceptual
Aplica a todo sistema que represente reglas de negocio relevantes, independientemente de su tamaño o estilo arquitectónico.

No busca eliminar el uso de frameworks, sino evitar que estos definan la estructura del sistema.

## Implicaciones arquitectónicas
- El dominio se convierte en el centro del diseño.
- Las dependencias conceptuales se orientan hacia el negocio.
- Las decisiones técnicas se consideran reemplazables en el tiempo.
- La arquitectura se evalúa por su capacidad de absorber cambios.

## Compensaciones (trade-offs)
Incrementa el esfuerzo de diseño inicial y requiere mayor disciplina del equipo, a cambio de mayor mantenibilidad, testabilidad y vida útil del sistema.
