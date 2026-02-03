---
id: contratos-de-integracion
sidebar_position: 7
title: Contratos de Integración
description: Definición y gestión de contratos de comunicación entre sistemas y servicios
---

# Contratos de Integración

Contratos mal definidos o desactualizados generan incompatibilidades, errores en producción y desconfianza entre equipos. Especificaciones explícitas (OpenAPI, AsyncAPI) actúan como fuente de verdad, permiten validación automática y facilitan evolución sin romper clientes existentes. Contratos versionados y retrocompatibles reducen coupling temporal y permiten despliegues independientes.

**Este lineamiento aplica a:** APIs REST/GraphQL, mensajes asíncronos, servicios gRPC, SOAP legacy e interfaces con terceros.

## Estándares Obligatorios

- [Definir contratos con especificaciones estándar OpenAPI/AsyncAPI](../../estandares/apis/openapi-swagger.md)
- [Versionar contratos semánticamente en URL o header](../../estandares/apis/versionado.md)
- [Validar requests/responses contra contratos en runtime](../../estandares/apis/contract-validation.md)
- [Mantener retrocompatibilidad durante deprecación](../../estandares/apis/deprecacion-apis.md)
- [Publicar contratos en API Portal accesible](../../estandares/apis/api-portal.md)
- [Implementar contract testing automatizado](../../estandares/testing/contract-testing.md)
