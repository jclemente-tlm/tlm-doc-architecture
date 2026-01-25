---
id: observabilidad
sidebar_position: 6
title: Observabilidad
description: Observabilidad como requisito arquitectónico desde el diseño
---

# Observabilidad

## 1. Propósito

Definir la observabilidad como un requisito arquitectónico obligatorio desde el diseño, no como una preocupación operativa posterior.

---

## 2. Alcance

Aplica a:

- Todos los servicios y aplicaciones
- Flujos de integración end-to-end
- Procesos batch y asíncronos
- Infraestructura y plataforma

---

## 3. Lineamientos Obligatorios

- Generar logs estructurados con contexto relevante
- Emitir métricas de negocio y técnicas
- Implementar trazas distribuidas (distributed tracing)
- Usar identificadores de correlación en todas las interacciones
- Configurar health checks y readiness probes

---

## 4. Decisiones de Diseño Esperadas

- Estrategia de logging (niveles, formato, destino)
- Métricas clave por servicio (latencia, errores, tráfico, saturación)
- Implementación de tracing distribuido
- Esquema de correlación de requests
- Dashboards y alertas definidos

---

## 5. Antipatrones y Prácticas Prohibidas

- Logs sin estructura ni contexto
- Ausencia de métricas de negocio
- Trazas incompletas o sin correlación
- Health checks que no reflejan el estado real
- Observabilidad como añadido posterior

---

## 6. Principios Relacionados

- Observabilidad desde el Diseño
- Calidad desde el Diseño
- Resiliencia y Tolerancia a Fallos
- Automatización como Principio

---

## 7. Validación y Cumplimiento

- Verificación de logs estructurados en code reviews
- Validación de métricas y dashboards antes de producción
- Pruebas de correlación end-to-end
- Auditoría de alertas configuradas
- Documentación de estrategia en ADRs
