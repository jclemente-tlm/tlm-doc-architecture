---
id: descomposicion-y-limites
sidebar_position: 2
title: Descomposición y Límites
description: Cómo dividir sistemas en componentes con límites claros de responsabilidad
---

# Descomposición y Límites

## 1. Propósito

Establecer cómo dividir sistemas en componentes con límites claros de responsabilidad, facilitando mantenimiento, evolución independiente y gobernanza efectiva.

---

## 2. Alcance

Aplica a:

- Monolitos modulares
- Arquitecturas de microservicios
- Arquitecturas orientadas a eventos
- Sistemas legacy en evolución

---

## 3. Lineamientos Obligatorios

- Identificar límites por capacidad de negocio, no por tecnología
- Cada componente debe tener responsabilidad única y bien definida
- Evitar dependencias cíclicas entre componentes
- Documentar propiedad clara de cada componente (equipo responsable)
- Definir contratos explícitos en los límites

**Criterios de descomposición:**

- **Por dominio:** Agrupar por capacidad de negocio cohesiva
- **Por volatilidad:** Separar lo que cambia frecuentemente
- **Por escalabilidad:** Independizar lo que requiere escalar diferente
- **Por equipo:** Alinear a estructuras de equipos autónomos

---

## 4. Decisiones de Diseño Esperadas

- Mapa de componentes/servicios con límites claros
- Matriz de responsabilidades (RACI) por componente
- Diagrama de dependencias entre componentes
- Estrategia de comunicación entre límites (API, eventos, etc.)
- Plan de gestión de transacciones entre límites

---

## 5. Antipatrones y Prácticas Prohibidas

- Componentes sin propósito claro ("God service")
- Límites basados solo en capas técnicas
- Dependencias ocultas entre componentes
- Acceso directo a datos de otros componentes
- Componentes sin dueño claro

---

## 6. Principios Relacionados

- Diseño Orientado al Dominio
- Arquitectura de Microservicios
- Desacoplamiento y Autonomía
- Simplicidad Intencional
- Contratos de Integración

---

## 7. Validación y Cumplimiento

- Architecture review validando límites propuestos
- Verificación de matriz de dependencias
- Auditoría de propiedad documentada
- Análisis de acoplamiento entre componentes
- Documentación en ADR de decisiones de descomposición
