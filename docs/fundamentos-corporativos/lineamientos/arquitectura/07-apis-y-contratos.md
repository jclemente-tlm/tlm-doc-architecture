---
id: apis-y-contratos
sidebar_position: 7
title: APIs y Contratos de Integración
description: Principios para diseñar APIs REST coherentes, contratos explícitos y evolución controlada
---

# APIs y Contratos de Integración

APIs inconsistentes, contratos mal definidos o documentación desactualizada generan fricción en consumidores, incompatibilidades entre equipos y errores en producción. Especificaciones explícitas (OpenAPI, AsyncAPI) actúan como fuente de verdad que permite validación automática, facilita adopción y reduce malentendidos. Seguir convenciones RESTful, versionado semántico y contratos retrocompatibles garantiza evolución sin romper clientes existentes, reduce coupling temporal y permite despliegues independientes con confianza.

**Este lineamiento aplica a:** APIs REST públicas e internas, APIs de microservicios, mensajes asíncronos, servicios GraphQL, integraciones con terceros y Backends for Frontend (BFF).

## Estándares Obligatorios

- [Seguir convenciones RESTful en diseño de APIs](../../estandares/apis/rest-api-design.md#1-rest-standards)
- [Implementar versionado explícito de APIs](../../estandares/apis/rest-api-design.md#3-api-versioning)
- [Documentar APIs REST con OpenAPI 3.0+](../../estandares/apis/event-api-contracts.md#2-asyncapi-specification)
- [Estandarizar manejo de errores en APIs](../../estandares/apis/api-error-handling.md)
- [Aplicar paginación en colecciones](../../estandares/apis/rest-api-design.md#4-api-pagination)
- [Mantener retrocompatibilidad en evolución](../../estandares/apis/rest-api-design.md#5-backward-compatibility)
- [Implementar contract testing automatizado](../../estandares/testing/contract-e2e-testing.md#1-contract-testing)

## Referencias Relacionadas

- [Comunicación Asíncrona y Eventos](./07-comunicacion-asincrona-y-eventos.md)
- [Arquitectura de Microservicios](../../estilos-arquitectonicos/microservicios.md)
