---
id: diseno-de-apis
sidebar_position: 6
title: Diseño de APIs
description: Principios y lineamientos para diseñar APIs REST coherentes y mantenibles
---

# Diseño de APIs

APIs inconsistentes o mal documentadas generan fricción en consumidores, errores de integración y costos de soporte elevados. Seguir convenciones RESTful, versionado explícito y documentación OpenAPI mejora la experiencia de desarrolladores, facilita adopción y reduce malentendidos. APIs bien diseñadas son contratos claros que evolucionan sin romper clientes existentes.

**Este lineamiento aplica a:** APIs REST públicas e internas, APIs de microservicios, integraciones con terceros y Backends for Frontend (BFF).

## Estándares Obligatorios

- [Seguir convenciones RESTful para recursos y verbos HTTP](../../estandares/apis/rest-conventions.md)
- [Implementar versionado explícito de APIs](../../estandares/apis/versionado.md)
- [Documentar APIs con especificación OpenAPI](../../estandares/apis/openapi-swagger.md)
- [Aplicar rate limiting y paginación en colecciones](../../estandares/apis/rate-limiting-paginacion.md)
- [Estandarizar manejo de errores con estructura consistente](../../estandares/apis/error-handling.md)

## Referencias Relacionadas

- [Arquitectura de Microservicios](../../estilos-arquitectonicos/microservicios.md)
