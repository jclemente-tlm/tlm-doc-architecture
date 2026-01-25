---
id: contratos-de-integracion
sidebar_position: 2
title: Contratos de Integración
description: Definición y gestión de contratos entre sistemas y servicios
---

# Contratos de Integración

## 1. Propósito

Establecer cómo definir, versionar y gestionar contratos de integración entre sistemas, garantizando compatibilidad y evolución controlada.

---

## 2. Alcance

Aplica a:

- Contratos de APIs REST y GraphQL
- Contratos de mensajes y eventos
- Contratos de servicios SOAP (legacy)
- Interfaces de integración con terceros

---

## 3. Lineamientos Obligatorios

- Definir contratos explícitos con esquemas formales (OpenAPI, AsyncAPI)
- Versionar contratos semánticamente (major.minor.patch)
- Validar requests y responses contra esquemas
- Mantener retrocompatibilidad o gestionar breaking changes
- Publicar contratos en registro centralizado

---

## 4. Decisiones de Diseño Esperadas

- Formato de contratos (OpenAPI, AsyncAPI, Protobuf)
- Estrategia de versionado y deprecación
- Schema registry o repositorio de contratos
- Proceso de aprobación de cambios de contrato
- Herramientas de validación y testing de contratos

---

## 5. Antipatrones y Prácticas Prohibidas

- Integraciones sin contrato definido
- Breaking changes sin incremento de versión mayor
- Contratos solo en documentación, no en código
- Validación solo en consumidor, no en productor
- Cambios de contrato sin comunicación

---

## 6. Principios Relacionados

- Contratos de Integración
- Contratos de Datos
- Arquitectura Evolutiva
- Desacoplamiento y Autonomía

---

## 7. Validación y Cumplimiento

- Contract testing automatizado (Pact, Spring Cloud Contract)
- Validación de breaking changes en CI/CD
- Revisión de cambios de contrato en PRs
- Monitoreo de versiones deprecadas en uso
- Auditoría de contratos publicados vs implementados
