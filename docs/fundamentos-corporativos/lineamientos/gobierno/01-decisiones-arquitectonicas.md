---
id: decisiones-arquitectonicas
sidebar_position: 1
title: Decisiones Arquitectónicas
description: Documentación y gobernanza de decisiones arquitectónicas mediante ADRs
---

# Decisiones Arquitectónicas

## 1. Propósito

Establecer cómo documentar, comunicar y gobernar las decisiones arquitectónicas significativas mediante Architecture Decision Records (ADRs).

---

## 2. Alcance

Aplica a:

- Decisiones arquitectónicas significativas
- Selección de tecnologías core
- Cambios en estilos arquitectónicos
- Definición de estándares técnicos
- Decisiones con impacto de largo plazo

---

## 3. Lineamientos Obligatorios

- Documentar decisiones arquitectónicas significativas en ADRs
- Versionar ADRs en repositorio junto al código
- Incluir contexto, alternativas evaluadas, decisión y consecuencias
- Revisar ADRs en architecture reviews antes de implementación
- Mantener ADRs actualizados cuando se superseden o modifiquen

---

## 4. Decisiones de Diseño Esperadas

- Formato de ADRs (MADR, Y-statement, custom)
- Ubicación de ADRs en repositorio
- Proceso de revisión y aprobación
- Criterios para determinar qué requiere ADR
- Herramientas de gestión de ADRs

---

## 5. Antipatrones y Prácticas Prohibidas

- Decisiones arquitectónicas significativas sin documentación
- ADRs sin contexto o justificación
- Documentación de decisiones solo en wikis externos
- ADRs sin fecha ni autores
- Modificar ADRs históricos (en lugar de crear nuevos)

---

## 6. Principios Relacionados

- Arquitectura Evolutiva
- Simplicidad Intencional
- Todos los principios (los ADRs los referencian)

---

## 7. Validación y Cumplimiento

- Revisión de ADRs en architecture reviews
- Auditoría de decisiones documentadas vs implementadas
- Verificación de presencia de ADRs en repositorios
- Análisis de trazabilidad entre ADRs y código
- Métricas de decisiones documentadas
