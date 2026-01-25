---
id: calidad-y-operacion
sidebar_position: 4
title: Calidad y Operación
description: Calidad integrada en el ciclo de desarrollo y operación continua
---

# Calidad y Operación

## 1. Propósito

Establecer que la calidad y operabilidad deben integrarse desde el diseño y desarrollo, no como actividades posteriores o separadas.

---

## 2. Alcance

Aplica a:

- Pruebas automatizadas
- Análisis estático de código
- Monitoreo y alertas
- Gestión de incidentes
- Mejora continua

---

## 3. Lineamientos Obligatorios

- Definir métricas de calidad y SLOs desde el diseño
- Implementar pruebas automatizadas (unitarias, integración, e2e)
- Configurar monitoreo y alertas antes de producción
- Establecer procesos de respuesta a incidentes
- Realizar análisis de causa raíz (RCA) post-incidentes

---

## 4. Decisiones de Diseño Esperadas

- Estrategia de testing (pirámide de tests)
- Cobertura mínima de código
- SLOs y SLIs del servicio
- Herramientas de monitoreo y alerting
- Procesos de on-call y escalación

---

## 5. Antipatrones y Prácticas Prohibidas

- Testing solo manual sin automatización
- Monitoreo agregado después de incidentes
- Ausencia de SLOs definidos
- Código sin code review
- Incidentes sin análisis de causa raíz

---

## 6. Principios Relacionados

- Calidad desde el Diseño
- Observabilidad desde el Diseño
- Automatización como Principio
- Resiliencia y Tolerancia a Fallos

---

## 7. Validación y Cumplimiento

- Revisión de cobertura de pruebas
- Auditoría de configuración de monitoreo
- Verificación de SLOs documentados
- Análisis de métricas de calidad (bugs, incidentes)
- Documentación de procesos operativos
