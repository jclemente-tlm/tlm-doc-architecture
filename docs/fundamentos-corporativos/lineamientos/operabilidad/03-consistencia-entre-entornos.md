---
id: consistencia-entre-entornos
sidebar_position: 3
title: Consistencia entre Entornos
description: Paridad entre entornos para reducir "funciona en mi máquina"
---

# Consistencia entre Entornos

## 1. Propósito

Garantizar que los entornos de desarrollo, QA y producción sean lo más similares posible, reduciendo problemas de "funciona en mi máquina" y facilitando diagnóstico.

---

## 2. Alcance

Aplica a:

- Entornos locales de desarrollo
- Entornos de integración y QA
- Staging y pre-producción
- Producción
- Contenedores y orquestación

---

## 3. Lineamientos Obligatorios

- Usar mismas versiones de dependencias en todos los entornos
- Contenedorizar aplicaciones para consistencia
- Gestionar configuración externamente (variables de entorno)
- Documentar diferencias inevitables entre entornos
- Validar paridad de entornos regularmente

---

## 4. Decisiones de Diseño Esperadas

- Estrategia de contenedorización
- Gestión de configuración por entorno
- Herramientas de paridad (Docker, Dev Containers)
- Diferencias aceptables entre entornos (ej: recursos)
- Proceso de sincronización de versiones

---

## 5. Antipatrones y Prácticas Prohibidas

- Versiones diferentes de runtime entre entornos
- Configuración específica de entorno en código
- "Funciona en mi máquina" sin reproducibilidad
- Dependencias globales no documentadas
- Tests que solo pasan en un entorno específico

---

## 6. Principios Relacionados

- Consistencia entre Entornos
- Infraestructura como Código
- Automatización como Principio
- Arquitectura Cloud Native

---

## 7. Validación y Cumplimiento

- Comparación de versiones entre entornos
- Tests de humo en todos los entornos
- Documentación de configuración por entorno
- Auditoría de diferencias no justificadas
- Métricas de problemas "solo en prod"
