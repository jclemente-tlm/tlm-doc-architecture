---
id: resiliencia-y-disponibilidad
sidebar_position: 4
title: Resiliencia y Disponibilidad
description: Lineamientos para diseñar sistemas tolerantes a fallos y altamente disponibles
---

# Resiliencia y Disponibilidad

## 1. Propósito

Definir cómo diseñar sistemas que mantengan su funcionamiento ante fallos, degradaciones o picos de carga, garantizando disponibilidad y recuperación oportuna.

---

## 2. Alcance

Aplica a:

- Servicios críticos de negocio
- APIs públicas y privadas
- Sistemas distribuidos y cloud native
- Integraciones con terceros

---

## 3. Lineamientos Obligatorios

- Implementar circuit breakers y timeouts en llamadas externas
- Diseñar para degradación graceful ante fallos de dependencias
- Aplicar retry con backoff exponencial cuando corresponda
- Documentar estrategias de failover y recuperación
- Definir SLOs (Service Level Objectives) claros

---

## 4. Decisiones de Diseño Esperadas

- Estrategia de manejo de fallos de dependencias
- Definición de SLOs y SLAs del servicio
- Mecanismos de retry, timeout y circuit breaking
- Plan de contingencia y recuperación ante desastres
- Estrategia de health checks y readiness probes

---

## 5. Antipatrones y Prácticas Prohibidas

- Llamadas sin timeout a servicios externos
- Dependencias críticas sin circuit breaker
- Retry infinito sin backoff
- Fallos silenciosos sin alertas
- Ausencia de degradación graceful

---

## 6. Principios Relacionados

- Resiliencia y Tolerancia a Fallos
- Arquitectura Cloud Native
- Observabilidad desde el Diseño
- Desacoplamiento y Autonomía

---

## 7. Validación y Cumplimiento

- Pruebas de caos (chaos engineering) en entornos no productivos
- Simulación de fallos de dependencias
- Monitoreo de SLOs y alertas configuradas
- Documentación de estrategias en ADRs
- Revisión de resiliencia en architecture reviews
