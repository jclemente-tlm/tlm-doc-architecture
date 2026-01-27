---
id: seguridad-apis
sidebar_position: 2
title: Seguridad de APIs
description: Estándar de seguridad para APIs REST: autenticación JWT/OAuth, autorización RBAC, HTTPS/TLS, rate limiting y protección de datos
---

# Estándar: Seguridad de APIs

## 1. Propósito

Definir los estándares técnicos obligatorios de **seguridad para APIs REST** en Talma, incluyendo autenticación JWT/OAuth 2.0, autorización basada en roles, comunicación segura HTTPS/TLS, rate limiting y protección de datos sensibles.

## 2. Alcance

### Aplica a

- ✅ Todas las APIs REST (públicas, privadas, internas)
- ✅ APIs de integración con sistemas externos
- ✅ Microservicios con comunicación HTTP
- ✅ Backend-for-Frontend (BFF) APIs

### NO aplica a

- ❌ gRPC services (estándar separado de seguridad gRPC)
- ❌ Comunicación interna mesh service-to-service sin Internet exposure

## 3. Tecnologías Obligatorias

### Stack de Seguridad

| Tecnología                                      | Versión Mínima | Propósito                          |
| ----------------------------------------------- | -------------- | ---------------------------------- |
| **ASP.NET Core Authentication.JwtBearer**       | 8.0+           | Autenticación JWT                  |
| **Microsoft.Identity.Web**                      | 2.15+          | Azure AD / OAuth 2.0 / OpenID Connect |
| **AspNetCoreRateLimit**                         | 5.0+           | Rate limiting por IP/usuario       |
| **Swashbuckle.AspNetCore** (con JWT support)    | 6.5+           | Documentación segura de APIs       |

### Versiones de Protocolo

- **TLS**: 1.3 mínimo (1.2 compatible)
- **JWT**: RS256 (RSA + SHA256) obligatorio
- **OAuth 2.0**: Authorization Code Flow con PKCE
- **HTTPS**: Obligatorio en todos los entornos (incluido desarrollo local con certificado self-signed)

### Versiones de Protocolo

- **TLS**: 1.3 mínimo (1.2 compatible)
- **JWT**: RS256 (RSA + SHA256) obligatorio
- **OAuth 2.0**: Authorization Code Flow con PKCE
- **HTTPS**: Obligatorio en todos los entornos (incluido desarrollo local con certificado self-signed)

## 4. Configuración Técnica Obligatoria

### 4.1 Autenticación JWT (RS256)

```csharp
// Program.cs - Configuración JWT con RS256
using Microsoft.AspNetCore.Authentication.JwtBearer;
using Microsoft.IdentityModel.Tokens;

builder.Services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
    .AddJwtBearer(options =>
    {
        options.Authority = builder.Configuration["Jwt:Authority"]; // ✅ Azure AD, Okta, Auth0
        options.Audience = builder.Configuration["Jwt:Audience"];
        
        options.TokenValidationParameters = new TokenValidationParameters
        {
            ValidateIssuer = true,
            ValidateAudience = true,
            ValidateLifetime = true,
            ValidateIssuerSigningKey = true,
            ValidAlgorithms = new[] { SecurityAlgorithms.RsaSha256 }, // ✅ RS256 obligatorio
            ClockSkew = TimeSpan.FromMinutes(5) // Tolerancia de 5 min para skew de reloj
        };

        options.Events = new JwtBearerEvents
        {
            OnAuthenticationFailed = context =>
            {
                var logger = context.HttpContext.RequestServices
                    .GetRequiredService<ILogger<Program>>();
                
                logger.LogWarning(
                    "Autenticación fallida: {Reason}. CorrelationId: {CorrelationId}",
                    context.Exception.Message,
                    context.HttpContext.Items["CorrelationId"]
                );
                
                context.Response.Headers.Append("X-Auth-Error", "Token inválido o expirado");
                return Task.CompletedTask;
            },
            
            OnTokenValidated = context =>
            {
                var logger = context.HttpContext.RequestServices
                    .GetRequiredService<ILogger<Program>>();
                
                logger.LogInformation(
                    "Token validado para usuario: {UserId}",
                    context.Principal?.Identity?.Name
                );
                return Task.CompletedTask;
            }
        };
    });
```

### 4.2 OAuth 2.0 con Azure AD (Microsoft Identity Platform)

```csharp
using Microsoft.Identity.Web;

builder.Services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
    .AddMicrosoftIdentityWebApi(builder.Configuration.GetSection("AzureAd"));
```

**appsettings.json**:

```json
{
  "AzureAd": {
    "Instance": "https://login.microsoftonline.com/",
    "TenantId": "your-tenant-id",
    "ClientId": "your-client-id",
    "Audience": "api://your-api-client-id"
  }
}
```

### 4.3 Autorización Basada en Roles (RBAC)

```csharp
builder.Services.AddAuthorization(options =>
{
    // ✅ Políticas basadas en roles
    options.AddPolicy("AdminOnly", policy =>
        policy.RequireRole("Admin"));

    options.AddPolicy("ManagerOrAdmin", policy =>
        policy.RequireRole("Manager", "Admin"));

    // ✅ Políticas basadas en claims
    options.AddPolicy("CountryAccess", policy =>
        policy.RequireClaim("country"));

    // ✅ Políticas basadas en claims + valores específicos
    options.AddPolicy("PeAccess", policy =>
        policy.RequireClaim("country", "PE"));

    // ✅ Políticas complejas
    options.AddPolicy("SeniorManager", policy =>
        policy.RequireRole("Manager")
              .RequireClaim("seniority", "senior"));
});
```

**Uso en Controllers**:

```csharp
[ApiController]
[Route("api/v1/[controller]")]
[Authorize] // ✅ Requiere autenticación para todo el controller
public class UsersController : ControllerBase
{
    [HttpGet]
    [Authorize(Policy = "AdminOnly")] // ✅ Solo admins
    public async Task<IActionResult> GetAllUsers()
    {
        // ...
    }

    [HttpPost]
    [Authorize(Roles = "Admin,Manager")] // ✅ Admins o Managers
    public async Task<IActionResult> CreateUser(CreateUserRequest request)
    {
        // ...
    }

    [HttpGet("{id}")]
    [AllowAnonymous] // ✅ Excepción: endpoint público
    public async Task<IActionResult> GetPublicUserProfile(Guid id)
    {
        // ...
    }
}
```

### 4.4 HTTPS/TLS Obligatorio

```csharp
// Program.cs
if (!app.Environment.IsDevelopment())
{
    // ✅ Redirección HTTPS
    app.UseHttpsRedirection();
    
    // ✅ HSTS (HTTP Strict Transport Security)
    app.UseHsts(); // max-age=31536000 (1 año)
}

// ✅ Headers de seguridad
app.Use(async (context, next) =>
{
    context.Response.Headers.Append("X-Content-Type-Options", "nosniff");
    context.Response.Headers.Append("X-Frame-Options", "DENY");
    context.Response.Headers.Append("X-XSS-Protection", "1; mode=block");
    context.Response.Headers.Append("Referrer-Policy", "strict-origin-when-cross-origin");
    context.Response.Headers.Append("Permissions-Policy", "geolocation=(), microphone=(), camera=()");
    
    if (!context.Request.IsHttps && !app.Environment.IsDevelopment())
    {
        context.Response.Headers.Append("Strict-Transport-Security",
            "max-age=31536000; includeSubDomains; preload");
    }
    
    await next();
});
```

### 4.5 CORS (Cross-Origin Resource Sharing)

```csharp
builder.Services.AddCors(options =>
{
    options.AddPolicy("TalmaPolicy", policy =>
    {
        policy.WithOrigins(
            "https://portal.talma.com",
            "https://app.talma.com",
            "https://admin.talma.com"
        )
        .AllowAnyMethod()
        .AllowAnyHeader()
        .AllowCredentials() // Para cookies/auth headers
        .SetPreflightMaxAge(TimeSpan.FromHours(1)); // Cache preflight 1 hora
    });

    // ✅ Política para desarrollo (solo local)
    if (app.Environment.IsDevelopment())
    {
        options.AddPolicy("DevPolicy", policy =>
            policy.AllowAnyOrigin()
                  .AllowAnyMethod()
                  .AllowAnyHeader());
    }
});

// Aplicar CORS
app.UseCors("TalmaPolicy");
```

### 4.6 Rate Limiting por IP y Usuario

```csharp
using AspNetCoreRateLimit;

// Program.cs - Configuración
builder.Services.AddMemoryCache();

builder.Services.Configure<IpRateLimitOptions>(options =>
{
    options.EnableEndpointRateLimiting = true;
    options.StackBlockedRequests = false;
    options.HttpStatusCode = 429; // Too Many Requests
    options.RealIpHeader = "X-Real-IP";
    options.ClientIdHeader = "X-ClientId";
    
    options.GeneralRules = new List<RateLimitRule>
    {
        new RateLimitRule
        {
            Endpoint = "*",
            Period = "1m",
            Limit = 100 // 100 requests por minuto
        },
        new RateLimitRule
        {
            Endpoint = "POST:/api/v1/auth/login",
            Period = "5m",
            Limit = 5 // 5 intentos de login en 5 minutos
        },
        new RateLimitRule
        {
            Endpoint = "POST:/api/v1/*",
            Period = "1m",
            Limit = 30 // 30 POSTs por minuto
        }
    };
});

builder.Services.AddSingleton<IIpPolicyStore, MemoryCacheIpPolicyStore>();
builder.Services.AddSingleton<IRateLimitCounterStore, MemoryCacheRateLimitCounterStore>();
builder.Services.AddSingleton<IRateLimitConfiguration, RateLimitConfiguration>();
builder.Services.AddSingleton<IProcessingStrategy, AsyncKeyLockProcessingStrategy>();

// Middleware
app.UseIpRateLimiting();
```

**appsettings.json**:

```json
{
  "IpRateLimiting": {
    "EnableEndpointRateLimiting": true,
    "StackBlockedRequests": false,
    "RealIpHeader": "X-Real-IP",
    "ClientIdHeader": "X-ClientId",
    "HttpStatusCode": 429,
    "GeneralRules": [
      {
        "Endpoint": "*",
        "Period": "1m",
        "Limit": 100
      }
    ]
  }
}
```

```

## 5. Ejemplos de Implementación

### 5.1 API Key para Service-to-Service

```csharp
// Middleware personalizado para API Key
[AttributeUsage(AttributeTargets.Class | AttributeTargets.Method)]
public class ApiKeyAttribute : Attribute, IAsyncActionFilter
{
    private const string API_KEY_HEADER = "X-API-Key";

    public async Task OnActionExecutionAsync(ActionExecutingContext context, ActionExecutionDelegate next)
    {
        if (!context.HttpContext.Request.Headers.TryGetValue(API_KEY_HEADER, out var extractedApiKey))
        {
            context.Result = new UnauthorizedObjectResult(new ProblemDetails
            {
                Status = StatusCodes.Status401Unauthorized,
                Title = "API Key requerida",
                Detail = $"Header '{API_KEY_HEADER}' no encontrado"
            });
            return;
        }

        var configuration = context.HttpContext.RequestServices.GetRequiredService<IConfiguration>();
        var validApiKeys = configuration.GetSection("ApiKeys:Services").Get<Dictionary<string, string>>();

        if (!validApiKeys.Values.Contains(extractedApiKey.ToString()))
        {
            var logger = context.HttpContext.RequestServices.GetRequiredService<ILogger<ApiKeyAttribute>>();
            logger.LogWarning("Intento de acceso con API Key inválida desde IP: {IP}", 
                context.HttpContext.Connection.RemoteIpAddress);
            
            context.Result = new UnauthorizedObjectResult(new ProblemDetails
            {
                Status = StatusCodes.Status401Unauthorized,
                Title = "API Key inválida"
            });
            return;
        }

        await next();
    }
}

// Uso en Controller
[ApiController]
[Route("api/v1/internal/[controller]")]
[ApiKey] // ✅ Requiere API Key
public class WebhooksController : ControllerBase
{
    [HttpPost("process")]
    public async Task<IActionResult> ProcessWebhook([FromBody] WebhookPayload payload)
    {
        // Procesamiento seguro
        return Ok();
    }
}
```

### 5.2 Validación de Claims en Authorization Handler

```csharp
public class TenantAuthorizationHandler : AuthorizationHandler<TenantRequirement>
{
    protected override Task HandleRequirementAsync(
        AuthorizationHandlerContext context,
        TenantRequirement requirement)
    {
        var tenantClaim = context.User.FindFirst("tenant_id");
        
        if (tenantClaim == null)
        {
            context.Fail();
            return Task.CompletedTask;
        }

        if (requirement.AllowedTenants.Contains(tenantClaim.Value))
        {
            context.Succeed(requirement);
        }
        else
        {
            context.Fail();
        }

        return Task.CompletedTask;
    }
}

public class TenantRequirement : IAuthorizationRequirement
{
    public string[] AllowedTenants { get; }

    public TenantRequirement(params string[] allowedTenants)
    {
        AllowedTenants = allowedTenants;
    }
}

// Registro
builder.Services.AddAuthorization(options =>
{
    options.AddPolicy("PeOnly", policy =>
        policy.Requirements.Add(new TenantRequirement("talma-pe")));
});

builder.Services.AddSingleton<IAuthorizationHandler, TenantAuthorizationHandler>();
```

### 5.3 Respuestas de Error de Seguridad

```csharp
// Middleware global de excepciones
app.UseExceptionHandler(errorApp =>
{
    errorApp.Run(async context =>
    {
        var exceptionHandlerPathFeature = context.Features.Get<IExceptionHandlerPathFeature>();
        var exception = exceptionHandlerPathFeature?.Error;
        
        var problemDetails = exception switch
        {
            UnauthorizedAccessException => new ProblemDetails
            {
                Status = StatusCodes.Status401Unauthorized,
                Title = "No autenticado",
                Detail = "Token inválido, expirado o ausente",
                Instance = context.Request.Path
            },
            ForbiddenAccessException => new ProblemDetails
            {
                Status = StatusCodes.Status403Forbidden,
                Title = "Acceso denegado",
                Detail = "No tienes permisos para acceder a este recurso",
                Instance = context.Request.Path
            },
            _ => new ProblemDetails
            {
                Status = StatusCodes.Status500InternalServerError,
                Title = "Error interno del servidor"
            }
        };

        problemDetails.Extensions["traceId"] = context.TraceIdentifier;
        problemDetails.Extensions["timestamp"] = DateTime.UtcNow;

        context.Response.StatusCode = problemDetails.Status.Value;
        context.Response.ContentType = "application/problem+json";
        await context.Response.WriteAsJsonAsync(problemDetails);
    });
});
```

## 6. Mejores Prácticas

### 6.1 Gestión de Secretos

```csharp
// ✅ BIEN - Usar Azure Key Vault / AWS Secrets Manager
builder.Configuration.AddAzureKeyVault(
    new Uri($"https://{builder.Configuration["KeyVault:Name"]}.vault.azure.net/"),
    new DefaultAzureCredential()
);

// ✅ Acceder a secretos
var jwtKey = builder.Configuration["Jwt:SecretKey"]; // Obtenido de Key Vault
```

### 6.2 Logging de Eventos de Seguridad

```csharp
public class SecurityAuditMiddleware
{
    private readonly RequestDelegate _next;
    private readonly ILogger<SecurityAuditMiddleware> _logger;

    public SecurityAuditMiddleware(RequestDelegate next, ILogger<SecurityAuditMiddleware> logger)
    {
        _next = next;
        _logger = logger;
    }

    public async Task InvokeAsync(HttpContext context)
    {
        var isAuthenticated = context.User.Identity?.IsAuthenticated ?? false;
        var userId = context.User.FindFirst(ClaimTypes.NameIdentifier)?.Value ?? "anonymous";
        var endpoint = context.Request.Path;
        var method = context.Request.Method;

        await _next(context);

        var statusCode = context.Response.StatusCode;

        // ✅ Log eventos de seguridad
        if (statusCode == 401 || statusCode == 403)
        {
            _logger.LogWarning(
                "Acceso denegado: {UserId} intentó {Method} {Endpoint}. StatusCode: {StatusCode}. IP: {IP}",
                userId, method, endpoint, statusCode, context.Connection.RemoteIpAddress
            );
        }

        if (isAuthenticated && statusCode >= 200 && statusCode < 300)
        {
            _logger.LogInformation(
                "Acceso autorizado: {UserId} ejecutó {Method} {Endpoint}",
                userId, method, endpoint
            );
        }
    }
}
```

### 6.3 Rotación de Tokens

```csharp
// ✅ Tokens con expiración corta (1 hora) + Refresh Token (7 días)
var accessToken = GenerateAccessToken(user, expiryMinutes: 60);
var refreshToken = GenerateRefreshToken(user, expiryDays: 7);

return new AuthResponse
{
    AccessToken = accessToken,
    RefreshToken = refreshToken,
    ExpiresIn = 3600 // 1 hora en segundos
};
```

## 7. Antipatrones (NO Hacer)

### ❌ Antipatrón 1: Usar HS256 en lugar de RS256

```csharp
// ❌ MAL - HS256 (simétrico) = secret compartido entre API y clientes
options.TokenValidationParameters = new TokenValidationParameters
{
    ValidAlgorithms = new[] { SecurityAlgorithms.HmacSha256 }, // ❌ HS256
    IssuerSigningKey = new SymmetricSecurityKey(Encoding.UTF8.GetBytes("my-secret-key"))
};

// ✅ BIEN - RS256 (asimétrico) = private key en Identity Provider, public key en API
options.TokenValidationParameters = new TokenValidationParameters
{
    ValidAlgorithms = new[] { SecurityAlgorithms.RsaSha256 }, // ✅ RS256
    ValidateIssuerSigningKey = true
};
options.Authority = "https://login.microsoftonline.com/tenant-id"; // ✅ Azure AD valida con clave pública
```

**Problema**: HS256 requiere compartir secret con clientes (inseguro si se compromete).  
**Solución**: Usar RS256 con Identity Provider centralizado (Azure AD, Okta, Auth0).

### ❌ Antipatrón 2: Hardcodear Secretos en Código

```csharp
// ❌ MAL - Secretos en código/appsettings.json committed a Git
var jwtKey = "my-super-secret-jwt-key-12345"; // ❌ Hardcodeado
var apiKey = configuration["ApiKeys:Service"]; // ❌ En appsettings.json (committed)

// ✅ BIEN - Secretos en Azure Key Vault / AWS Secrets Manager
builder.Configuration.AddAzureKeyVault(
    new Uri($"https://talma-keyvault.vault.azure.net/"),
    new DefaultAzureCredential()
);

var jwtKey = builder.Configuration["Jwt:SecretKey"]; // ✅ Obtenido de Key Vault
```

**Problema**: Secretos en Git = accesibles a todos, riesgo de leak.  
**Solución**: Azure Key Vault (Azure), Secrets Manager (AWS), variables de entorno en CI/CD.

### ❌ Antipatrón 3: No Validar Claims en Autorización

```csharp
// ❌ MAL - Solo verificar autenticación, no autorización
[Authorize] // Solo verifica que el token sea válido
public async Task<IActionResult> DeleteUser(Guid id)
{
    await _userService.DeleteAsync(id); // ❌ Cualquier usuario autenticado puede borrar
    return NoContent();
}

// ✅ BIEN - Verificar roles y claims específicos
[Authorize(Policy = "AdminOnly")] // ✅ Solo Admins
public async Task<IActionResult> DeleteUser(Guid id)
{
    // Verificación adicional
    var tenantClaim = User.FindFirst("tenant_id")?.Value;
    if (tenantClaim != "talma-pe")
    {
        return Forbid();
    }

    await _userService.DeleteAsync(id);
    return NoContent();
}
```

**Problema**: Usuarios autenticados sin privilegios pueden ejecutar acciones sensibles.  
**Solución**: Siempre usar políticas de autorización con roles/claims específicos.

### ❌ Antipatrón 4: No Implementar Rate Limiting

```csharp
// ❌ MAL - Endpoint de login sin rate limiting
[HttpPost("login")]
[AllowAnonymous]
public async Task<IActionResult> Login(LoginRequest request)
{
    var result = await _authService.LoginAsync(request.Email, request.Password);
    return Ok(result); // ❌ Vulnerable a brute-force
}

// ✅ BIEN - Rate limiting en login
// appsettings.json
{
  "IpRateLimiting": {
    "GeneralRules": [
      {
        "Endpoint": "POST:/api/v1/auth/login",
        "Period": "5m",
        "Limit": 5 // ✅ Máximo 5 intentos en 5 minutos
      }
    ]
  }
}
```

**Problema**: Endpoint de login vulnerable a ataques de fuerza bruta.  
**Solución**: Rate limiting agresivo en endpoints de autenticación (5 intentos / 5 min).

## 8. Validación y Cumplimiento

### 8.1 Checklist de Implementación

- [ ] **JWT con RS256** configurado (no HS256)
- [ ] **OAuth 2.0 / Azure AD** integrado para SSO
- [ ] **HTTPS/TLS 1.3** obligatorio en todos los entornos
- [ ] **HSTS** habilitado con max-age 1 año
- [ ] **CORS** configurado solo para orígenes permitidos
- [ ] **Rate Limiting** habilitado (100 req/min general, 5 req/5min login)
- [ ] **Headers de seguridad** (X-Content-Type-Options, X-Frame-Options, CSP)
- [ ] **Autorización RBAC** con políticas definidas
- [ ] **Secretos en Key Vault** (no hardcodeados)
- [ ] **Logging de eventos de seguridad** (401, 403, intentos fallidos)
- [ ] **API Keys** para service-to-service (si aplica)
- [ ] **Swagger con JWT** support configurado

### 8.2 Métricas de Cumplimiento

| Métrica                            | Target | Verificación                                |
| ---------------------------------- | ------ | ------------------------------------------- |
| Endpoints con `[Authorize]`        | 95%+   | Grep search, code review                    |
| Uso de RS256 (no HS256)            | 100%   | Configuración de JWT                        |
| HTTPS en producción                | 100%   | Certificados SSL activos                    |
| Rate limiting habilitado           | 100%   | Configuración de AspNetCoreRateLimit        |
| Secretos en Key Vault              | 100%   | No secretos en appsettings.json/Git         |
| Headers de seguridad               | 100%   | Validación con SecurityHeaders.com          |
| Eventos de seguridad loggeados     | 100%   | Logs de 401/403 en Application Insights     |

## 9. Referencias

### Estándares Relacionados

- [Diseño REST](./01-diseno-rest.md) - Implementación técnica de APIs
- [Validación y Errores](./03-validacion-y-errores.md) - Validación de entrada
- [Performance](./05-performance.md) - Rate limiting y caching

### Convenciones Relacionadas

- [Headers HTTP](../../convenciones/apis/02-headers-http.md) - Headers de autenticación y seguridad
- [Formato Respuestas](../../convenciones/apis/03-formato-respuestas.md) - Estructura de errores

### Lineamientos Relacionados

- [Seguridad desde el Diseño](../../lineamientos/seguridad/01-seguridad-desde-el-diseno.md) - Lineamientos de seguridad
- [Protección de Datos](../../lineamientos/seguridad/02-proteccion-de-datos.md) - Gestión de datos sensibles

### Principios Relacionados

- [Seguridad desde el Diseño](../../principios/seguridad/01-seguridad-desde-el-diseno.md) - Fundamento de seguridad

### ADRs Relacionados

- [ADR-003: Gestión de Secretos](../../../decisiones-de-arquitectura/adr-003-gestion-secretos.md) - Azure Key Vault
- [ADR-004: Autenticación SSO](../../../decisiones-de-arquitectura/adr-004-autenticacion-sso.md) - Azure AD
- [ADR-008: Gateway de APIs](../../../decisiones-de-arquitectura/adr-008-gateway-apis.md) - API Gateway
- [ADR-016: Logging Estructurado](../../../decisiones-de-arquitectura/adr-016-logging-estructurado.md) - Audit logs

### Documentación Externa

- [OAuth 2.0 RFC 6749](https://tools.ietf.org/html/rfc6749) - Estándar OAuth 2.0
- [JWT RFC 7519](https://tools.ietf.org/html/rfc7519) - Estándar JWT
- [OWASP API Security Top 10](https://owasp.org/www-project-api-security/) - Amenazas de seguridad
- [Microsoft Identity Platform](https://docs.microsoft.com/en-us/azure/active-directory/develop/) - Azure AD
- [ASP.NET Core Security](https://learn.microsoft.com/en-us/aspnet/core/security/) - Microsoft Docs

---

**Última actualización**: 27 de enero 2026  
**Responsable**: Equipo de Arquitectura
