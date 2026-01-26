---
id: esquemas-de-datos
sidebar_position: 2
title: Esquemas de Datos
description: Definición explícita de esquemas de datos de dominio versionados y documentados
---

# Esquemas de Datos

## 1. Propósito

Garantizar que los datos del dominio (bases de datos, eventos de negocio, modelos) tengan esquemas explícitos, versionados y documentados que faciliten evolución y compatibilidad.

> **Nota:** Para contratos de APIs REST/GraphQL ver [Contratos de Integración](../integracion/02-contratos-de-integracion.md).

---

## 2. Alcance

Aplica a:

- Esquemas de bases de datos (tablas, columnas, tipos)
- Eventos de dominio (estructura de eventos de negocio)
- Modelos de dominio persistidos
- Mensajes de dominio asíncronos
- Archivos de intercambio de datos (CSV, JSON, XML)

No aplica a:

- Contratos de APIs REST/GraphQL (ver Integración/02)
- DTOs o payloads de API (ver Integración/02)

---

## 3. Lineamientos Obligatorios

- Definir esquemas explícitos para estructuras de datos de dominio
- Versionar esquemas de BD mediante migraciones versionadas (Flyway, Liquibase)
- Documentar esquemas de eventos con formato estándar (JSON Schema, Avro)
- Validar datos contra esquemas antes de persistir o publicar
- Gestionar cambios de esquema mediante estrategias de evolución (expand-contract)

---

## 4. Decisiones de Diseño Esperadas

- Herramientas de migración de BD (Flyway, Liquibase, EF Migrations)
- Formato de esquemas de eventos (JSON Schema, Avro, Protobuf)
- Estrategia de evolución de esquemas (expand-contract, parallel change)
- Política de cambios breaking en modelos de dominio
- Registro de esquemas de eventos (Schema Registry, Event Catalog)
- Documentación de modelos de dominio (ERD, DDD aggregates)

---

## 5. Antipatrones y Prácticas Prohibidas

- Cambios de esquema de BD sin migraciones versionadas
- Eventos de dominio sin esquema definido
- Modificaciones de BD directas (no mediante migraciones)
- Esquemas de eventos no documentados
- Breaking changes en modelos sin estrategia de compatibilidad
- Uso de SELECT \* en lugar de columnas explícitas

---

## 6. Principios Relacionados

- Contratos de Datos
- Datos como Responsabilidad del Dominio
- Arquitectura Evolutiva
- Diseño Orientado al Dominio

---

## 7. Validación y Cumplimiento

- Revisión de migraciones de BD en PRs
- Validación automática de migraciones en CI/CD
- Pruebas de backward compatibility de eventos
- Documentación de esquemas en repositorio de código
- Auditoría de cambios de esquema sin migración
- Verificación de validación de eventos contra esquemas
