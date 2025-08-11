---
id: adr-002-estandar-apis-rest
title: "Estándar para APIs REST"
sidebar_position: 2
---

## ✅ ESTADO

Aceptada – Agosto 2025

---

## 🗺️ CONTEXTO

Los servicios corporativos requieren estándares consistentes de diseño de APIs para:

- **Consistencia** en la experiencia de desarrollo entre servicios
- **Interoperabilidad** fluida entre microservicios
- **Documentación estandarizada** con OpenAPI/Swagger
- **Versionado coherente** para evolución sin ruptura
- **Manejo de errores uniforme** para debugging simplificado
- **Seguridad consistente** con patrones de autenticación estándar

La intención es establecer **estándares agnósticos** que funcionen en cualquier plataforma.

Las alternativas de estándares evaluadas fueron:

- **REST + OpenAPI 3.0** (Estándar web, maduro)
- **GraphQL** (Flexible, single endpoint)
- **gRPC** (Alto rendimiento, tipado fuerte)
- **SOAP** (Legado, declinando)

## 🔍 COMPARATIVA DE ALTERNATIVAS

### Comparativa Cualitativa

| Criterio | OpenAPI 3.0 | GraphQL | gRPC | SOAP |
|----------|-------------|---------|------|------|
| **Adopción** | ✅ Estándar de facto REST | ✅ Muy popular, creciente | 🟡 Nicho, microservicios | ❌ Legado, declinando |
| **Integración** | ✅ Universal, fácil | 🟡 Requiere cliente especial | 🟡 Compleja, protobuf | ❌ Muy compleja |
| **Documentación** | ✅ Automática y visual | 🟡 Introspectiva | 🟡 Generada desde proto | 🟡 WSDL complejo |
| **Herramientas** | ✅ Ecosistema enorme | ✅ Buenas herramientas | 🟡 Herramientas limitadas | 🟡 Herramientas legado |
| **Flexibilidad** | ✅ Muy flexible | ✅ Máxima flexibilidad | 🟡 Rígido, tipado | ❌ Muy rígido |
| **Rendimiento** | 🟡 HTTP/JSON estándar | 🟡 HTTP/JSON optimizable | ✅ Binario, muy rápido | ❌ XML pesado |
| **Aprendizaje** | ✅ Muy fácil | 🟡 Curva moderada | 🟡 Curva pronunciada | ❌ Muy complejo |

### Matriz de Decisión

| Estándar | Adopción | Integración | Documentación | Herramientas | Recomendación |
|----------|-----------|-------------|---------------|--------------|---------------|
| **OpenAPI 3.0** | Excelente | Excelente | Excelente | Excelente | ✅ **Seleccionada** |
| **GraphQL** | Muy buena | Moderada | Buena | Buena | 🟡 Considerada |
| **gRPC** | Moderada | Compleja | Buena | Limitadas | 🟡 Nicho específico |
| **SOAP** | Mala | Muy compleja | Compleja | Legado | ❌ Descartada |

## ⚖️ DECISIÓN

**Seleccionamos REST + OpenAPI 3.0** como estándar principal por:

### Ventajas Clave

- **Adopción universal**: Estándar de facto en la industria
- **Tooling maduro**: Generación de código, testing, documentación
- **Interoperabilidad máxima**: Compatible con cualquier cliente HTTP
- **Documentación automática**: Swagger UI out-of-the-box
- **Ecosistema .NET excelente**: Swashbuckle, NSwag, etc.

## 📋 ESTÁNDARES DEFINIDOS

### 1. Estructura de URLs

```http
Patrón Base: https://api.{dominio}/{servicio}/v{version}/{recurso}

Ejemplos:
GET    /api/notifications/v1/templates
POST   /api/notifications/v1/templates
GET    /api/notifications/v1/templates/{id}
PUT    /api/notifications/v1/templates/{id}
DELETE /api/notifications/v1/templates/{id}

Colecciones anidadas:
GET    /api/notifications/v1/templates/{id}/versions
POST   /api/notifications/v1/templates/{id}/versions
```

### 2. Métodos HTTP Estándar

```yaml
GET:    Obtener recursos (idempotente)
POST:   Crear recursos nuevos
PUT:    Actualizar recurso completo (idempotente)
PATCH:  Actualizar recurso parcial
DELETE: Eliminar recurso (idempotente)
HEAD:   Obtener headers sin body
OPTIONS: Obtener métodos permitidos
```

### 3. Códigos de Estado HTTP

```yaml
Éxito:
  200: OK - Operación exitosa con contenido
  201: Created - Recurso creado exitosamente
  204: No Content - Operación exitosa sin contenido

Redirección:
  301: Moved Permanently - Recurso movido permanentemente
  304: Not Modified - Recurso no modificado (cache)

Error Cliente:
  400: Bad Request - Solicitud malformada
  401: Unauthorized - No autenticado
  403: Forbidden - No autorizado
  404: Not Found - Recurso no encontrado
  409: Conflict - Conflicto de estado
  422: Unprocessable Entity - Validación fallida
  429: Too Many Requests - Rate limit excedido

Error Servidor:
  500: Internal Server Error - Error interno del servidor
  502: Bad Gateway - Gateway inválido
  503: Service Unavailable - Servicio no disponible
  504: Gateway Timeout - Timeout del gateway
```

### 4. Formato de Respuestas

```json
// Respuesta exitosa con datos
{
  "data": {
    "id": "123",
    "type": "template",
    "attributes": {
      "name": "Bienvenida",
      "subject": "¡Bienvenido a Talma!",
      "created_at": "2025-08-06T17:55:20Z"
    }
  },
  "meta": {
    "timestamp": "2025-08-06T17:55:20Z",
    "version": "1.0.0"
  }
}

// Respuesta con colección paginada
{
  "data": [
    {
      "id": "123",
      "type": "template",
      "attributes": {...}
    }
  ],
  "meta": {
    "pagination": {
      "page": 1,
      "per_page": 10,
      "total": 25,
      "total_pages": 3
    }
  },
  "links": {
    "self": "/api/notifications/v1/templates?page=1",
    "next": "/api/notifications/v1/templates?page=2",
    "last": "/api/notifications/v1/templates?page=3"
  }
}
```

### 5. Formato de Errores

```json
// Error de validación
{
  "error": {
    "code": "VALIDATION_FAILED",
    "message": "Los datos proporcionados no son válidos",
    "details": [
      {
        "field": "email",
        "code": "INVALID_FORMAT",
        "message": "El formato del email no es válido"
      }
    ]
  },
  "meta": {
    "timestamp": "2025-08-06T17:55:20Z",
    "trace_id": "abc123def456"
  }
}

// Error de recurso no encontrado
{
  "error": {
    "code": "TEMPLATE_NOT_FOUND",
    "message": "La plantilla solicitada no existe",
    "details": {
      "template_id": "123",
      "tenant": "peru"
    }
  },
  "meta": {
    "timestamp": "2025-08-06T17:55:20Z",
    "trace_id": "abc123def456"
  }
}
```

### 6. Paginación Estándar

```text
Query Parameters:
  page: Número de página (default: 1)
  per_page: Items por página (default: 10, max: 100)
  sort: Campo de ordenamiento (default: id)
  order: Dirección (asc|desc, default: asc)

Ejemplo:
GET /api/notifications/v1/templates?page=2&per_page=20&sort=created_at&order=desc
```

### 7. Filtrado y Búsqueda

```text
Query Parameters:
  filter[campo]: Filtro exacto
  search: Búsqueda de texto libre
  include: Recursos relacionados a incluir

Ejemplos:
GET /api/notifications/v1/templates?filter[type]=email&filter[active]=true
GET /api/notifications/v1/templates?search=bienvenida
GET /api/notifications/v1/templates?include=versions,statistics
```

### 8. Versionado de APIs

```yaml
Estrategia: URL Path Versioning
Formato: /v{major}
Ejemplos: /v1, /v2, /v3

Compatibilidad:
  - Cambios compatibles: Misma versión mayor
  - Cambios incompatibles: Nueva versión mayor
  - Deprecación: Mínimo 12 meses de soporte
```

### 9. Headers Estándar

```http
Request Headers:
  Authorization: Bearer {jwt_token}
  Content-Type: application/json
  Accept: application/json
  X-Tenant-ID: {tenant_id}
  X-Trace-ID: {trace_id}
  X-Request-ID: {request_id}

Response Headers:
  Content-Type: application/json
  X-Rate-Limit-Remaining: {count}
  X-Rate-Limit-Reset: {timestamp}
  X-Trace-ID: {trace_id}
  X-Request-ID: {request_id}
```

## 🔒 SEGURIDAD ESTÁNDAR

### Autenticación y Autorización

```yaml
Autenticación:
  - JWT Bearer tokens (OAuth2/OIDC)
  - Validación de firma y expiración
  - Refresh token rotation

Autorización:
  - Claims-based authorization
  - Role-based access control (RBAC)
  - Resource-based permissions
```

### Rate Limiting

```yaml
Límites por Endpoint:
  GET: 1000 requests/hour
  POST/PUT/PATCH: 100 requests/hour
  DELETE: 50 requests/hour

Headers de Respuesta:
  X-Rate-Limit-Limit: 1000
  X-Rate-Limit-Remaining: 999
  X-Rate-Limit-Reset: 1691341200
```

## 📊 DOCUMENTACIÓN OPENAPI

### Estructura Estándar

```yaml
openapi: 3.0.3
info:
  title: Servicio de Notificaciones
  description: API para gestión de notificaciones corporativas
  version: 1.0.0
  contact:
    name: Equipo de Arquitectura
    email: arquitectura@talma.com
servers:
  - url: https://api.talma.com/notifications/v1
    description: Producción
  - url: https://api-staging.talma.com/notifications/v1
    description: Staging
```

### Componentes Reutilizables

```yaml
components:
  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT

  schemas:
    Error:
      type: object
      properties:
        error:
          $ref: '#/components/schemas/ErrorDetail'
        meta:
          $ref: '#/components/schemas/Meta'
```

## 🔄 CONSECUENCIAS

### Positivas

- ✅ **Consistencia total** entre todos los servicios
- ✅ **Documentación automática** con Swagger/OpenAPI
- ✅ **Interoperabilidad máxima** con cualquier cliente
- ✅ **Debugging simplificado** con formatos estándar
- ✅ **Onboarding rápido** para nuevos desarrolladores
- ✅ **Testing automatizado** con contratos OpenAPI

### Negativas

- ❌ **Rigidez inicial** puede limitar casos especiales
- ❌ **Overhead de documentación** para mantener specs actualizadas
- ❌ **Migración necesaria** para APIs existentes no conformes

### Neutras

- 🔄 **Tooling de validación** requerido para enforcement
- 🔄 **Capacitación del equipo** en estándares definidos

## 📚 REFERENCIAS

- [OpenAPI 3.0 Specification](https://swagger.io/specification/)
- [REST API Design Best Practices](https://restfulapi.net/)
- [HTTP Status Codes](https://httpstatuses.com/)
- [JSON:API Specification](https://jsonapi.org/)

---

**Decisión tomada por:** Equipo de Arquitectura + Desarrollo
**Fecha:** Agosto 2025
**Próxima revisión:** Febrero 2026
