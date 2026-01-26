---
id: headers-http
sidebar_position: 2
title: Headers HTTP
description: Convención para headers HTTP estándar y personalizados
---

## 1. Principio

Los headers HTTP deben seguir estándares de la industria y usar nombres consistentes para facilitar la integración, trazabilidad y debugging.

## 2. Reglas

### Regla 1: Headers Personalizados con Prefijo X-

- **Formato**: `X-{Nombre-Header}` (Pascal-Kebab-Case)
- **Ejemplo correcto**: `X-Correlation-ID`, `X-Request-ID`, `X-Tenant-ID`
- **Ejemplo incorrecto**: `correlationId`, `x-correlation-id`, `X_Correlation_ID`
- **Justificación**: Distingue headers custom de estándar

### Regla 2: Headers Obligatorios de Trazabilidad

| Header             | Propósito                               | Formato | Generado por          |
| ------------------ | --------------------------------------- | ------- | --------------------- |
| `X-Correlation-ID` | Tracking end-to-end de request          | UUID v4 | API Gateway o Cliente |
| `X-Request-ID`     | ID único del request individual         | UUID v4 | API Gateway           |
| `X-Tenant-ID`      | Identificador de tenant (multi-tenancy) | String  | Cliente autenticado   |

```http
GET /api/v1/users HTTP/1.1
Host: api.talma.com
X-Correlation-ID: 550e8400-e29b-41d4-a716-446655440000
X-Request-ID: 7f3d6b2a-8c1e-4d5f-9a2b-3c4d5e6f7890
X-Tenant-ID: tlm-pe
Authorization: Bearer eyJhbGc...
```

### Regla 3: Headers de Autenticación

- **Formato**: `Authorization: Bearer {token}`
- **Ejemplo correcto**: `Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5...`
- **Ejemplo incorrecto**: `Authorization: eyJhbGc...`, `Auth-Token: xyz`, `X-API-Key: abc`

```http
✅ Correcto:
Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5...

❌ Incorrecto:
Authorization: eyJhbGciOiJSUzI1NiIsInR5...  # Falta "Bearer"
X-Auth-Token: xyz                            # No estándar
Api-Key: abc123                              # No estándar
```

### Regla 4: Headers de Content Negotiation

| Header            | Uso                        | Valores                               |
| ----------------- | -------------------------- | ------------------------------------- |
| `Content-Type`    | Tipo de contenido enviado  | `application/json`, `application/xml` |
| `Accept`          | Tipo de contenido esperado | `application/json`, `application/xml` |
| `Accept-Language` | Idioma preferido           | `es-ES`, `en-US`                      |
| `Accept-Encoding` | Compresión aceptada        | `gzip`, `deflate`, `br`               |

```http
POST /api/v1/users HTTP/1.1
Content-Type: application/json
Accept: application/json
Accept-Language: es-ES
Accept-Encoding: gzip
```

### Regla 5: Headers de Caching

| Header          | Propósito              | Ejemplo                                      |
| --------------- | ---------------------- | -------------------------------------------- |
| `Cache-Control` | Directivas de cache    | `no-cache`, `max-age=3600`, `private`        |
| `ETag`          | Versión del recurso    | `"33a64df551425fcc55e4d42a148795d9f25f89d4"` |
| `If-None-Match` | Validación condicional | `"33a64df551425fcc55e4d42a148795d9f25f89d4"` |

```http
# Response
HTTP/1.1 200 OK
Cache-Control: max-age=3600, private
ETag: "v1.0.0-abc123"

# Subsequent request
GET /api/v1/users/123
If-None-Match: "v1.0.0-abc123"

# Response if not modified
HTTP/1.1 304 Not Modified
```

### Regla 6: Headers de Rate Limiting

| Header                  | Propósito                | Ejemplo      |
| ----------------------- | ------------------------ | ------------ |
| `X-RateLimit-Limit`     | Límite total de requests | `1000`       |
| `X-RateLimit-Remaining` | Requests restantes       | `243`        |
| `X-RateLimit-Reset`     | Timestamp de reset       | `1672531200` |
| `Retry-After`           | Segundos para reintentar | `3600`       |

```http
HTTP/1.1 200 OK
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 243
X-RateLimit-Reset: 1672531200
```

## 3. Headers Estándar HTTP (NO personalizar)

Usar estos headers **SIN** prefijo X-:

| Header          | Uso                       | NO Usar               |
| --------------- | ------------------------- | --------------------- |
| `Authorization` | Autenticación             | ~~`X-Authorization`~~ |
| `Content-Type`  | Tipo de contenido         | ~~`X-Content-Type`~~  |
| `User-Agent`    | Cliente que hace request  | ~~`X-User-Agent`~~    |
| `Origin`        | Origen del request (CORS) | ~~`X-Origin`~~        |

## 4. Headers de Seguridad

| Header                      | Propósito              | Valor                                 |
| --------------------------- | ---------------------- | ------------------------------------- |
| `Strict-Transport-Security` | HSTS                   | `max-age=31536000; includeSubDomains` |
| `X-Content-Type-Options`    | Prevenir MIME sniffing | `nosniff`                             |
| `X-Frame-Options`           | Prevenir clickjacking  | `DENY` o `SAMEORIGIN`                 |
| `Content-Security-Policy`   | CSP                    | `default-src 'self'`                  |
| `X-XSS-Protection`          | XSS protection         | `1; mode=block`                       |

```http
HTTP/1.1 200 OK
Strict-Transport-Security: max-age=31536000; includeSubDomains
X-Content-Type-Options: nosniff
X-Frame-Options: SAMEORIGIN
X-XSS-Protection: 1; mode=block
```

## 5. Headers de Contexto

Headers que mantienen contexto entre llamadas:

- `X-Correlation-ID` - ID de tracking transaccional
- `X-Tenant-ID` - Identificador de tenant
- `Authorization` - Token de autenticación
- `Accept-Language` - Preferencia de idioma

Headers generados por cada servicio:

- `X-Request-ID` - ID único por request
- `Host` - Específico del endpoint
- `User-Agent` - Identificación del cliente

## 6. Tabla de Referencia Rápida

| Header             | Tipo     | Requerido      | Valor Ejemplo               |
| ------------------ | -------- | -------------- | --------------------------- |
| `X-Correlation-ID` | Custom   | ✅ Sí          | UUID v4                     |
| `X-Request-ID`     | Custom   | ✅ Sí          | UUID v4                     |
| `X-Tenant-ID`      | Custom   | Multi-tenant   | `tlm-pe`                    |
| `Authorization`    | Estándar | Auth endpoints | `Bearer {token}`            |
| `Content-Type`     | Estándar | POST/PUT       | `application/json`          |
| `Accept`           | Estándar | Recomendado    | `application/json`          |
| `X-RateLimit-*`    | Custom   | Rate limit     | `1000`, `243`, `1672531200` |

## 7. Herramientas de Validación

### Middleware .NET

```csharp
public class TraceabilityHeadersMiddleware
{
    public async Task InvokeAsync(HttpContext context)
    {
        // Generar X-Request-ID si no existe
        if (!context.Request.Headers.ContainsKey("X-Request-ID"))
        {
            context.Request.Headers.Add("X-Request-ID", Guid.NewGuid().ToString());
        }

        // Validar X-Correlation-ID
        if (!context.Request.Headers.ContainsKey("X-Correlation-ID"))
        {
            context.Response.StatusCode = 400;
            await context.Response.WriteAsJsonAsync(new
            {
                error = "X-Correlation-ID header is required"
            });
            return;
        }

        await _next(context);
    }
}
```

### Middleware TypeScript (Express)

```typescript
export const traceabilityHeaders: RequestHandler = (req, res, next) => {
  // Generar X-Request-ID
  req.headers["x-request-id"] = req.headers["x-request-id"] || uuidv4();

  // Validar X-Correlation-ID
  if (!req.headers["x-correlation-id"]) {
    return res.status(400).json({
      error: "X-Correlation-ID header is required",
    });
  }

  next();
};
```

## 📖 Referencias

### Estándares relacionados

- [Seguridad de APIs](/docs/fundamentos-corporativos/estandares/apis/seguridad-apis)
- [Logging Estructurado](/docs/fundamentos-corporativos/estandares/observabilidad/logging)

### Convenciones relacionadas

- [Correlation IDs](/docs/fundamentos-corporativos/convenciones/logs/correlation-ids)

### Recursos externos

- [HTTP Headers - MDN](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers)
- [OWASP Secure Headers](https://owasp.org/www-project-secure-headers/)

---

**Última revisión**: 26 de enero 2026
**Responsable**: Equipo de Arquitectura
