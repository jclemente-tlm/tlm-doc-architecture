# Lineamientos para desarrollo de APIs

Esta sección contiene las mejores prácticas y estándares para el desarrollo de APIs REST en Talma.

## 📚 Contenido

### [01. Diseño y arquitectura](./01-diseno-y-arquitectura.md)

Principios fundamentales de diseño RESTful, convenciones de naming, estructura de recursos y códigos de estado HTTP.

**Temas cubiertos:**

- Principios RESTful
- Naming conventions
- Estructura de recursos y jerarquías
- Estándares de respuesta JSON
- Códigos de estado HTTP
- Implementación con ASP.NET Core

### [02. Seguridad en APIs](./02-seguridad.md)

Lineamientos de seguridad específicos para APIs REST, incluyendo autenticación, autorización y protección contra vulnerabilidades.

**Temas cubiertos:**

- Autenticación JWT Bearer
- Autorización granular con políticas
- Validación y sanitización de entrada
- Protección contra vulnerabilidades (SQL injection, CSRF)
- Manejo seguro de datos sensibles
- Monitoreo de seguridad

### [03. Validación y manejo de errores](./03-validacion-y-errores.md)

Estrategias para validación robusta de entrada y manejo consistente de errores siguiendo RFC 7807.

**Temas cubiertos:**

- Validación con Data Annotations
- Validación personalizada
- Middleware de manejo global de errores
- Estructura estándar de errores (RFC 7807)
- Logging de errores

### [04. Versionado y documentación](./04-versionado-y-documentacion.md)

Políticas de versionado, compatibilidad hacia atrás y documentación automática con OpenAPI/Swagger.

**Temas cubiertos:**

- Estrategias de versionado
- Semantic Versioning para APIs
- Compatibilidad hacia atrás
- Documentación con OpenAPI/Swagger
- Changelogs y guías de migración

### [05. Performance y monitoreo](./05-performance-y-monitoreo.md)

Optimización de performance, métricas, logging estructurado y monitoreo de salud de APIs.

**Temas cubiertos:**

- Paginación eficiente
- Caching estratégico
- Compresión de respuestas
- Métricas de performance
- Health checks
- Distributed tracing
- Rate limiting

## 🔗 Referencias cruzadas

### ADRs relacionados

- [ADR-002: Estándar para APIs REST](/docs/adrs/adr-002-estandard-apis-rest)
- [ADR-003: Gestión de Secretos](/docs/adrs/adr-003-gestion-secretos)
- [ADR-004: Autenticación SSO](/docs/adrs/adr-004-autenticacion-sso)
- [ADR-008: Gateway de APIs](/docs/adrs/adr-008-gateway-apis)
- [ADR-011: Cache distribuido](/docs/adrs/adr-011-cache-distribuido)
- [ADR-016: Logging estructurado](/docs/adrs/adr-016-logging-estructurado)
- [ADR-017: Versionado de APIs](/docs/adrs/adr-017-versionado-apis)

### Otros lineamientos

- [Lineamientos de seguridad](/docs/lineamientos/lineamientos-de-seguridad/) - Para aspectos de seguridad en APIs
- [Estándares de código C#](/docs/lineamientos/estandares-de-codigo/01-csharp) - Para código backend
- [Principios de arquitectura](/docs/lineamientos/principios-de-arquitectura/) - Para diseño de sistemas

## 🚀 Quick Start

### 1. Nuevo proyecto de API

```bash
dotnet new webapi -n MiApi.Talma
cd MiApi.Talma
dotnet add package Microsoft.AspNetCore.Mvc.Versioning
dotnet add package Swashbuckle.AspNetCore
```

### 2. Configuración básica

```csharp
// Program.cs
builder.Services.AddApiVersioning();
builder.Services.AddSwaggerGen();
builder.Services.AddResponseCompression();

var app = builder.Build();
app.UseResponseCompression();
app.UseSwagger();
app.UseSwaggerUI();
```

### 3. Controller template

```csharp
[ApiController]
[Route("api/v{version:apiVersion}/[controller]")]
[ApiVersion("1.0")]
public class UsersController : ControllerBase
{
    [HttpGet]
    [ProducesResponseType(typeof(PagedResponse<UserDto>), 200)]
    public async Task<ActionResult<PagedResponse<UserDto>>> GetUsers()
    {
        // Implementación...
    }
}
```

## ✅ Checklist de implementación

### Diseño y arquitectura

- [ ] Seguir principios RESTful en diseño de endpoints
- [ ] Usar naming conventions consistentes
- [ ] Implementar códigos de estado HTTP apropiados
- [ ] Estructurar respuestas JSON estándar

### Seguridad

- [ ] Configurar autenticación JWT Bearer
- [ ] Implementar autorización granular con políticas
- [ ] Validar y sanitizar toda entrada de usuario
- [ ] Proteger contra inyección SQL con consultas parametrizadas
- [ ] Implementar protección CSRF para operaciones de modificación
- [ ] Configurar rate limiting específico por endpoint
- [ ] Cifrar datos sensibles en tránsito y reposo
- [ ] Implementar logging seguro sin exponer datos sensibles

### Validación y errores

- [ ] Implementar validación robusta de entrada
- [ ] Configurar manejo global de errores RFC 7807
- [ ] Estructurar respuestas de error consistentes

### Versionado y documentación

- [ ] Establecer política de versionado clara
- [ ] Generar documentación automática con Swagger/OpenAPI
- [ ] Mantener changelogs y guías de migración

### Performance y monitoreo

- [ ] Implementar paginación en listados
- [ ] Configurar caching apropiado
- [ ] Agregar métricas y health checks
- [ ] Implementar distributed tracing
- [ ] Asegurar logging estructurado
