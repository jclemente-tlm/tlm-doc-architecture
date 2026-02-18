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

- [Seguir convenciones RESTful en diseño de APIs](../../estandares/apis/api-rest-standards.md)
- [Implementar versionado explícito de APIs](../../estandares/apis/api-versioning.md)
- [Documentar APIs REST con OpenAPI 3.0+](../../estandares/apis/openapi-specification.md)
- [Estandarizar manejo de errores en APIs](../../estandares/apis/api-error-handling.md)
- [Aplicar paginación en colecciones](../../estandares/apis/api-pagination.md)
- [Mantener retrocompatibilidad en evolución](../../estandares/apis/api-backward-compatibility.md)
- [Implementar contract testing automatizado](../../estandares/testing/contract-testing.md)

## Referencias Relacionadas

- [Comunicación Asíncrona y Eventos](./07-comunicacion-asincrona-y-eventos.md)
- [Arquitectura de Microservicios](../../estilos-arquitectonicos/microservicios.md)
