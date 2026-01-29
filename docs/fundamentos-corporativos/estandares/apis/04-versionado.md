---
id: versionado
sidebar_position: 4
title: Versionado de APIs
description: Estándar de versionado de APIs REST con URL versioning, semantic versioning, estrategias de deprecación y compatibilidad hacia atrás
---

# Estándar Técnico — Versionado de APIs

---

## 1. Propósito
Garantizar evolución controlada mediante URL versioning (`/api/v1/users`), semantic versioning adaptado, políticas de deprecación (6 meses mínimo) y compatibilidad hacia atrás sin romper clientes.

---

## 2. Alcance

**Aplica a:**
- Todas las APIs REST públicas
- APIs de integración con sistemas externos
- Microservicios con contratos públicos

**No aplica a:**
- APIs internas temporales (POCs)
- Endpoints administrativos internos sin SLA

---

## 3. Tecnologías Aprobadas

| Componente | Tecnología | Versión mínima | Observaciones |
|-----------|------------|----------------|---------------|
| **Versionado** | AspNetCore.Mvc.Versioning | 5.0+ | URL segment versioning |
| **Explorer** | Asp.Versioning.Mvc.ApiExplorer | 6.0+ | Multi-version Swagger |
| **Documentación** | Swashbuckle.AspNetCore | 6.5+ | Docs por versión |
| **Estrategia** | URL Segment (recomendado) | - | `/api/v1/users` |

> El uso de tecnologías no listadas requiere aprobación de Arquitectura.

---

## 4. Requisitos Obligatorios 🔴

- [ ] URL versioning: `/api/v1/resource`, `/api/v2/resource`
- [ ] Semantic versioning: MAJOR.MINOR (ejemplo: v1.0, v2.1)
- [ ] Header `api-supported-versions` en todas las responses
- [ ] Header `api-deprecated-versions` cuando aplique
- [ ] Periodo de deprecación mínimo: 6 meses
- [ ] Documentación Swagger por versión (v1, v2)
- [ ] Breaking changes requieren nueva versión MAJOR
- [ ] Non-breaking changes pueden ir en versión actual
- [ ] Cambios compatibles hacia atrás: nuevos campos opcionales OK
- [ ] Versionado en controllers con `[ApiVersion("1.0")]`
- [ ] Default version configurada (v1.0)
- [ ] Notificación a clientes 3 meses antes de deprecación

---

## 5. Prohibiciones

- ❌ Query string versioning (`?version=1`)
- ❌ Header versioning (`X-API-Version: 1`)
- ❌ Media type versioning (`application/vnd.api.v1+json`)
- ❌ Breaking changes sin incrementar MAJOR
- ❌ Deprecar versiones sin periodo de gracia (mínimo 6 meses)
- ❌ Eliminar campos existentes en versión actual

---

## 6. Configuración Mínima

```csharp
// Program.cs
using Microsoft.AspNetCore.Mvc;

builder.Services.AddApiVersioning(options =>
{
    options.DefaultApiVersion = new ApiVersion(1, 0);
    options.AssumeDefaultVersionWhenUnspecified = true;
    options.ReportApiVersions = true; // Headers: api-supported-versions
    options.ApiVersionReader = new UrlSegmentApiVersionReader();
});

builder.Services.AddVersionedApiExplorer(options =>
{
    options.GroupNameFormat = "'v'VVV"; // v1, v2
    options.SubstituteApiVersionInUrl = true;
});
```

```csharp
// Controller v1
[ApiController]
[ApiVersion("1.0")]
[Route("api/v{version:apiVersion}/users")]
public class UsersV1Controller : ControllerBase
{
    [HttpGet]
    public IActionResult GetUsers() => Ok(new { version = "v1" });
}

// Controller v2
[ApiController]
[ApiVersion("2.0")]
[Route("api/v{version:apiVersion}/users")]
public class UsersV2Controller : ControllerBase
{
    [HttpGet]
    public IActionResult GetUsers() => Ok(new { version = "v2", newField = "added" });
}

// Controller con múltiples versiones
[ApiController]
[ApiVersion("1.0")]
[ApiVersion("2.0")]
[Route("api/v{version:apiVersion}/orders")]
public class OrdersController : ControllerBase
{
    [HttpGet]
    [MapToApiVersion("1.0")]
    public IActionResult GetOrdersV1() => Ok(new { version = "v1" });
    
    [HttpGet]
    [MapToApiVersion("2.0")]
    public IActionResult GetOrdersV2() => Ok(new { version = "v2" });
}
```

---

## 7. Validación

```bash
# Verificar versiones soportadas
curl -I https://api.talma.com/api/v1/users
# Header: api-supported-versions: 1.0, 2.0

# Acceder a v1
curl https://api.talma.com/api/v1/users

# Acceder a v2
curl https://api.talma.com/api/v2/users

# Verificar Swagger por versión
curl https://api.talma.com/swagger/v1/swagger.json
curl https://api.talma.com/swagger/v2/swagger.json

# Tests de versionado
dotnet test --filter Category=Versioning
```

**Métricas de cumplimiento:**

| Métrica | Target | Verificación |
|---------|--------|--------------|  
| URL versioning | 100% | `/api/v1/` en todas las rutas |
| Header `api-supported-versions` | 100% | `curl -I` muestra header |
| Swagger por versión | 100% | `/swagger/v1`, `/swagger/v2` |
| Periodo deprecación | ≥ 6 meses | Verificar changelog |

Incumplimientos deben corregirse o documentarse mediante excepción aprobada.

---

## 8. Referencias

- [ADR-017: Versionado de APIs](../../../decisiones-de-arquitectura/adr-017-versionado-apis.md)
- [Diseño REST](./01-diseno-rest.md)
- [ASP.NET Core API Versioning](https://github.com/dotnet/aspnet-api-versioning)
- [Semantic Versioning](https://semver.org/)
