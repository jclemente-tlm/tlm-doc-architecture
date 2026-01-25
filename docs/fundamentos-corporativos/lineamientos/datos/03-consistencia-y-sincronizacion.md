---
id: consistencia-y-sincronizacion
sidebar_position: 3
title: Consistencia y Sincronización
description: Estrategias para mantener consistencia de datos en sistemas distribuidos
---

# Consistencia y Sincronización

## 1. Propósito

Definir cómo gestionar la consistencia de datos en arquitecturas distribuidas, aceptando consistencia eventual cuando sea apropiado y garantizando consistencia fuerte donde sea crítico.

---

## 2. Alcance

Aplica a:

- Sistemas distribuidos y microservicios
- Datos replicados entre servicios
- Eventos y mensajería asíncrona
- Integraciones entre sistemas
- Cachés y vistas materializadas

---

## 3. Lineamientos Obligatorios

- Definir explícitamente el modelo de consistencia por caso de uso
- Documentar si se acepta consistencia eventual o se requiere consistencia fuerte
- Implementar mecanismos de reconciliación para consistencia eventual
- Gestionar conflictos de datos con estrategias definidas (last-write-wins, CRDT, manual)
- Evitar transacciones distribuidas; preferir sagas o compensaciones

---

## 4. Decisiones de Diseño Esperadas

- Modelo de consistencia por dominio/caso de uso
- Estrategia de sincronización de datos (eventos, polling, CDC)
- Mecanismos de detección y resolución de conflictos
- Políticas de retry y manejo de fallos en sincronización
- SLOs de consistencia (tiempo máximo de convergencia)

---

## 5. Antipatrones y Prácticas Prohibidas

- Transacciones distribuidas (2PC) sin justificación crítica
- Asumir consistencia fuerte donde no es necesaria
- Sincronización síncrona entre todos los servicios
- Ausencia de estrategia para manejar inconsistencias
- Datos duplicados sin dueño claro (source of truth)

---

## 6. Principios Relacionados

- Consistencia según el Contexto
- Resiliencia y Tolerancia a Fallos
- Arquitectura Orientada a Eventos
- Desacoplamiento y Autonomía

---

## 7. Validación y Cumplimiento

- Documentación de modelo de consistencia en ADRs
- Pruebas de reconciliación y manejo de conflictos
- Monitoreo de lag de sincronización
- Revisión de estrategias de compensación
- Auditoría de transacciones distribuidas justificadas
