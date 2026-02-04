---
id: api-deprecation
sidebar_position: 9
title: Deprecación de APIs
description: Política de deprecación de APIs con RFC 8594 Sunset header, versionado semántico y comunicación a consumidores
---

# Estándar Técnico — Deprecación de APIs

---

## 1. Propósito

Establecer un proceso formal de deprecación de APIs que garantice transiciones suaves para consumidores, usando RFC 8594 Sunset header, versionado semántico, periodos de gracia mínimos y comunicación proactiva.

---

## 2. Alcance

**Aplica a:**

- APIs REST públicas y privadas en deprecación
- Endpoints específicos deprecados
- Versiones completas de API deprecadas
- Breaking changes que requieren migración

**No aplica a:**

- APIs internas experimentales (sin SLA)
- Endpoints nunca publicados en producción
- Cambios compatibles hacia atrás (non-breaking)

---

## 3. Tecnologías Aprobadas

| Componente          | Tecnología           | Versión mínima | Observaciones                     |
| ------------------- | -------------------- | -------------- | --------------------------------- |
| **Header estándar** | RFC 8594 Sunset      | -              | Header HTTP `Sunset`              |
| **Middleware**      | ASP.NET Core         | 8.0+           | Middleware custom para headers    |
| **Documentación**   | OpenAPI 3.1+         | -              | Campo `deprecated: true`          |
| **Versionado**      | URI-based versioning | -              | `/api/v1`, `/api/v2`              |
| **Monitoreo**       | Application Insights | -              | Telemetría de uso APIs deprecadas |

> El uso de tecnologías no listadas requiere aprobación de Arquitectura.

---

## 4. Requisitos Obligatorios 🔴

### Política de Deprecación

- [ ] Periodo mínimo de gracia: **6 meses** para APIs públicas
- [ ] Periodo mínimo de gracia: **3 meses** para APIs privadas
- [ ] Header `Sunset` con fecha ISO 8601 de desactivación
- [ ] Header `Deprecation: true` (draft RFC)
- [ ] Header `Link` a documentación de migración
- [ ] OpenAPI spec con `deprecated: true` en endpoints
- [ ] Status code 299 (Miscellaneous Warning) en deprecation headers

### Comunicación

- [ ] Anuncio formal 30 días antes del inicio de deprecación
- [ ] Emails a equipos consumidores conocidos
- [ ] Changelog público actualizado
- [ ] Documentación de migración publicada
- [ ] Notificación 30 días antes del sunset
- [ ] Notificación 7 días antes del sunset

### Monitoreo

- [ ] Métricas de uso de endpoints deprecados
- [ ] Alertas cuando endpoints deprecados reciben tráfico
- [ ] Dashboard de adopción de nuevas versiones
- [ ] Logs de consumidores usando APIs deprecadas

### Proceso de Sunset

- [ ] Día 0: Publicar nueva versión
- [ ] Día 0: Marcar versión antigua como deprecada
- [ ] Día 30: Notificación formal
- [ ] Cada mes: Recordatorio a consumidores activos
- [ ] Día -30: Última notificación
- [ ] Día D: Desactivar API deprecada (retornar 410 Gone)

---

## 5. Prohibiciones

- ❌ Deprecar sin periodo de gracia mínimo
- ❌ Desactivar API sin avisos previos
- ❌ Deprecar sin alternativa documentada
- ❌ Omitir headers estándar de deprecación
- ❌ No monitorear uso de endpoints deprecados
- ❌ Eliminar documentación de versiones deprecadas antes del sunset

---

## 6. Configuración Mínima

```csharp
// DeprecationMiddleware.cs
public class DeprecationMiddleware
{
    private readonly RequestDelegate _next;

    public DeprecationMiddleware(RequestDelegate next)
    {
        _next = next;
    }

    public async Task InvokeAsync(HttpContext context)
    {
        var endpoint = context.GetEndpoint();
        var deprecation = endpoint?.Metadata.GetMetadata<DeprecatedAttribute>();

        if (deprecation != null)
        {
            context.Response.Headers["Deprecation"] = "true";
            context.Response.Headers["Sunset"] = deprecation.SunsetDate.ToString("r"); // RFC 1123
            context.Response.Headers["Link"] = $"<{deprecation.MigrationGuideUrl}>; rel=\"deprecation\"";

            // Log usage
            var logger = context.RequestServices.GetRequiredService<ILogger<DeprecationMiddleware>>();
            logger.LogWarning(
                "Deprecated endpoint accessed: {Path} by {Client}. Sunset: {Sunset}",
                context.Request.Path,
                context.Request.Headers["User-Agent"],
                deprecation.SunsetDate
            );
        }

        await _next(context);
    }
}

// DeprecatedAttribute.cs
[AttributeUsage(AttributeTargets.Class | AttributeTargets.Method)]
public class DeprecatedAttribute : Attribute
{
    public DateTime SunsetDate { get; }
    public string MigrationGuideUrl { get; }

    public DeprecatedAttribute(string sunsetDate, string migrationGuideUrl)
    {
        SunsetDate = DateTime.Parse(sunsetDate);
        MigrationGuideUrl = migrationGuideUrl;
    }
}
```

```csharp
// Program.cs
app.UseMiddleware<DeprecationMiddleware>();
```

---

## 7. Ejemplos

### Controller con endpoint deprecado

```csharp
[ApiController]
[Route("api/v1/users")]
[Deprecated("2024-12-31", "https://docs.talma.com/migration/v1-to-v2")]
public class UsersV1Controller : ControllerBase
{
    [HttpGet]
    public async Task<IActionResult> GetUsers()
    {
        // Lógica legacy
        return Ok(users);
    }
}

// Nueva versión
[ApiController]
[Route("api/v2/users")]
public class UsersV2Controller : ControllerBase
{
    [HttpGet]
    public async Task<IActionResult> GetUsers()
    {
        // Nueva lógica mejorada
        return Ok(users);
    }
}
```

### Response con headers de deprecación

```http
HTTP/1.1 200 OK
Content-Type: application/json
Deprecation: true
Sunset: Tue, 31 Dec 2024 23:59:59 GMT
Link: <https://docs.talma.com/migration/v1-to-v2>; rel="deprecation"

{
  "users": [...]
}
```

### OpenAPI spec con deprecación

```yaml
openapi: 3.1.0
paths:
  /api/v1/users:
    get:
      summary: Obtener usuarios (DEPRECADO)
      deprecated: true
      description: |
        ⚠️ Este endpoint está deprecado y será removido el 31/12/2024.
        Migrar a /api/v2/users.
        Guía: https://docs.talma.com/migration/v1-to-v2
      responses:
        "200":
          description: Lista de usuarios
          headers:
            Deprecation:
              schema:
                type: string
                example: "true"
            Sunset:
              schema:
                type: string
                example: "Tue, 31 Dec 2024 23:59:59 GMT"
```

### API desactivada retornando 410 Gone

```csharp
[ApiController]
[Route("api/v1/legacy")]
public class LegacyController : ControllerBase
{
    [HttpGet]
    public IActionResult GetLegacy()
    {
        return StatusCode(410, new
        {
            error = "Gone",
            message = "This API version was sunset on 2024-12-31",
            migrationGuide = "https://docs.talma.com/migration/v1-to-v2",
            newEndpoint = "/api/v2/users"
        });
    }
}
```

---

## 8. Validación y Auditoría

```bash
# Verificar headers de deprecación
curl -I https://api.talma.com/api/v1/users

# Monitorear uso de APIs deprecadas (Application Insights)
az monitor app-insights metrics show \
  --app talma-api \
  --metrics "requests/count" \
  --filter "url contains 'v1'"

# Verificar OpenAPI spec
curl https://api.talma.com/swagger/v1/swagger.json | jq '.paths | to_entries | map(select(.value.get.deprecated == true))'
```

**Métricas de cumplimiento:**

| Métrica                  | Umbral                               | Verificación                    |
| ------------------------ | ------------------------------------ | ------------------------------- |
| Periodo de gracia mínimo | 6 meses (public) / 3 meses (private) | Revisar timeline de deprecación |
| Notificaciones enviadas  | 100% consumidores                    | Logs de email/Slack             |
| Headers presente         | 100% endpoints deprecados            | Tests automatizados             |
| Adopción nueva versión   | >90% antes de sunset                 | Métricas de tráfico             |
| Documentación migración  | 100% casos                           | Revisar docs publicados         |

---

## 9. Referencias

- [RFC 8594 - Sunset HTTP Header](https://datatracker.ietf.org/doc/html/rfc8594)
- [OpenAPI Deprecation](https://spec.openapis.org/oas/v3.1.0#fixed-fields-8)
- [Microsoft API Deprecation Guidelines](https://github.com/microsoft/api-guidelines/blob/vNext/Guidelines.md#172-deprecating-existing-apis)
- [Google API Design Guide - Breaking Changes](https://cloud.google.com/apis/design/compatibility)
- [Stripe API Versioning](https://stripe.com/docs/api/versioning)
- [Twilio API Lifecycle](https://www.twilio.com/docs/glossary/what-is-api-lifecycle-management)
