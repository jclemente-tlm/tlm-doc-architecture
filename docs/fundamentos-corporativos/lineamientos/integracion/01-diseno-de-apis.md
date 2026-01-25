---
id: diseno-de-apis
sidebar_position: 1
title: Diseño de APIs
description: Principios y lineamientos para diseñar APIs REST coherentes y mantenibles
---

# Diseño de APIs

## 1. Propósito

Establecer lineamientos para diseñar APIs REST coherentes, intuitivas y alineadas a estándares de la industria.

---

## 2. Alcance

Aplica a:

- APIs REST públicas e internas
- APIs de microservicios
- APIs de integración con terceros
- Backends for Frontend (BFF)

---

## 3. Lineamientos Obligatorios

- Seguir convenciones RESTful (recursos, verbos HTTP, códigos de estado)
- Usar sustantivos en plural para recursos (`/users`, `/orders`)
- Implementar versionado de APIs (URL, header)
- Documentar APIs con OpenAPI/Swagger
- Aplicar rate limiting y paginación en colecciones

---

## 4. Decisiones de Diseño Esperadas

- Estrategia de versionado (URL path, header, query)
- Convenciones de nomenclatura (camelCase, snake_case)
- Formato de respuestas de error estandarizado
- Estrategia de paginación (offset, cursor)
- Mecanismos de filtrado y búsqueda

---

## 5. Antipatrones y Prácticas Prohibidas

- Verbos en URLs (`/getUser`, `/createOrder`)
- Inconsistencia en nomenclatura entre endpoints
- APIs sin versionado
- Respuestas de error sin estructura estándar
- Colecciones sin paginación

---

## 6. Principios Relacionados

- Contratos de Integración
- Simplicidad Intencional
- Arquitectura de Microservicios

---

## 7. Validación y Cumplimiento

- Revisión de especificaciones OpenAPI
- Validación de convenciones con linters (Spectral)
- Code reviews verificando estándares
- Pruebas de contratos de API
- Documentación publicada y actualizada
