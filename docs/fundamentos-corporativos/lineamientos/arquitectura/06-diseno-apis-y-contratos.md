---
id: diseno-apis-y-contratos
sidebar_position: 6
title: Diseño de APIs y Contratos de Integración
description: Principios para diseñar APIs REST coherentes, contratos explícitos y evolución controlada
---

# Diseño de APIs y Contratos de Integración

APIs inconsistentes, contratos mal definidos o documentación desactualizada generan fricción en consumidores, incompatibilidades entre equipos y errores en producción. Especificaciones explícitas (OpenAPI, AsyncAPI) actúan como fuente de verdad que permite validación automática, facilita adopción y reduce malentendidos. Seguir convenciones RESTful, versionado semántico y contratos retrocompatibles garantiza evolución sin romper clientes existentes, reduce coupling temporal y permite despliegues independientes con confianza.

**Este lineamiento aplica a:** APIs REST públicas e internas, APIs de microservicios, mensajes asíncronos, servicios GraphQL, integraciones con terceros y Backends for Frontend (BFF).

## Estándares Obligatorios

### Diseño de APIs REST

- [Seguir convenciones RESTful para recursos y verbos HTTP](../../estandares/apis/api-rest-standards.md)
- [Implementar versionado explícito en URL o header](../../estandares/apis/api-rest-standards.md#6-versionado-de-apis)
- [Aplicar rate limiting y paginación en colecciones](../../estandares/apis/api-rest-standards.md#8-paginación)
- [Estandarizar manejo de errores con estructura consistente](../../estandares/apis/api-rest-standards.md#9-manejo-de-errores)

### Contratos y Especificaciones

- [Definir contratos con especificaciones estándar OpenAPI 3.0+](../../estandares/apis/api-rest-standards.md#11-documentación-openapiswagger)
- [Documentar APIs asíncronas con AsyncAPI](../../estandares/mensajeria/kafka-messaging.md)
- [Validar requests/responses contra contratos en runtime](../../estandares/apis/api-rest-standards.md)
- [Mantener retrocompatibilidad durante deprecación](../../estandares/apis/api-rest-standards.md#6-versionado-de-apis)
- [Implementar contract testing automatizado (Pact)](../../estandares/testing/testing-standards.md#contract-tests)

## Referencias Relacionadas

- [Comunicación Asíncrona y Eventos](./07-comunicacion-asincrona-y-eventos.md)
- [Arquitectura de Microservicios](../../estilos-arquitectonicos/microservicios.md)
