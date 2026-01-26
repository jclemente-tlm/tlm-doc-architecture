---
id: contratos-de-integracion
sidebar_position: 7
title: Contratos de Integración
description: Definición y gestión de contratos de comunicación entre sistemas y servicios
---

# Contratos de Integración

## 1. Propósito

Establecer cómo definir, versionar y gestionar contratos de comunicación (APIs, mensajes) entre sistemas, garantizando compatibilidad y evolución controlada.

> **Nota:** Para esquemas de datos de dominio (BD, eventos) ver [Esquemas de Datos](../datos/02-contratos-y-esquemas.md).

---

## 2. Alcance

Aplica a:

- Contratos de APIs REST y GraphQL (OpenAPI, GraphQL Schema)
- Contratos de mensajes asíncronos (AsyncAPI)
- Contratos gRPC (Protobuf)
- Contratos de servicios SOAP (legacy, WSDL)
- Interfaces de integración con terceros

No aplica a:

- Esquemas de bases de datos (ver Datos/02)
- Modelos de dominio internos (ver Datos/02)

---

## 3. Lineamientos Obligatorios

- Definir contratos de API con especificaciones estándar (OpenAPI 3.x, AsyncAPI 2.x+)
- Versionar contratos semánticamente en URL o header (v1, v2)
- Validar requests y responses contra contratos en runtime
- Mantener retrocompatibilidad durante deprecación (mínimo 6 meses)
- Publicar contratos en repositorio accesible (API Portal, Git)

---

## 4. Decisiones de Diseño Esperadas

- Formato de contratos por tipo (OpenAPI para REST, AsyncAPI para eventos, Protobuf para gRPC)
- Estrategia de versionado de APIs (URL path /v1, header, query param)
- Proceso de deprecación de versiones (timeline, comunicación)
- API Portal o repositorio de contratos (Swagger UI, Postman, Backstage)
- Herramientas de contract testing (Pact, Spring Cloud Contract, Dredd)
- Políticas de breaking changes (cuándo incrementar major)

---

## 5. Antipatrones y Prácticas Prohibidas

- APIs sin especificación OpenAPI/AsyncAPI
- Breaking changes sin nueva versión de API
- Especificaciones desactualizadas (no reflejan implementación)
- Validación solo en consumidor (client-side)
- Cambios de contrato sin deprecation period
- Contratos no publicados o inaccesibles
- Versionado solo en código, no en URL/header

---

## 6. Principios Relacionados

- Contratos de Integración
- Contratos de Datos
- Arquitectura Evolutiva
- Desacoplamiento y Autonomía

---

## 7. Validación y Cumplimiento

- Contract testing automatizado en CI/CD (Pact, Spring Cloud Contract, Dredd)
- Validación de especificación OpenAPI con linters (Spectral, Redocly)
- Revisión de cambios de contrato en PRs
- Monitoreo de versiones de API en uso (métricas por versión)
- Auditoría de drift entre especificación y código
- Verificación de contratos publicados en API Portal
- Alertas de uso de endpoints deprecados
