---
title: "Seguridad de APIs"
sidebar_position: 2
---

Esta guía establece los estándares de seguridad esenciales para APIs REST, cubriendo autenticación, autorización, comunicación segura y protección de datos.

## 🔐 Autenticación

### JWT (JSON Web Tokens)

Estándar principal para autenticación stateless en APIs REST.

```csharp
builder.Services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
    .AddJwtBearer(options =>
    {
        options.TokenValidationParameters = new TokenValidationParameters
        {
            ValidateIssuer = true,
            ValidateAudience = true,
            ValidateLifetime = true,
            ValidateIssuerSigningKey = true,
            ValidIssuer = builder.Configuration["Jwt:Issuer"],
            ValidAudience = builder.Configuration["Jwt:Audience"],
            IssuerSigningKey = new SymmetricSecurityKey(
                Encoding.UTF8.GetBytes(builder.Configuration["Jwt:Key"])),
            ClockSkew = TimeSpan.FromMinutes(5)
        };
    });
```

### OAuth 2.0 / OpenID Connect

Para integración con proveedores de identidad externos y SSO corporativo.

```csharp
// Azure AD
builder.Services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
    .AddMicrosoftIdentityWebApi(builder.Configuration.GetSection("AzureAd"));
```

### API Keys

Para servicios a servicios y integraciones específicas.

```csharp
[AttributeUsage(AttributeTargets.Class | AttributeTargets.Method)]
public class ApiKeyAttribute : Attribute, IAsyncActionFilter
{
    private const string API_KEY_HEADER = "X-API-Key";

    public async Task OnActionExecutionAsync(ActionExecutingContext context, ActionExecutionDelegate next)
    {
        if (!context.HttpContext.Request.Headers.TryGetValue(API_KEY_HEADER, out var extractedApiKey))
        {
            context.Result = new UnauthorizedObjectResult("API Key requerida");
            return;
        }

        var configuration = context.HttpContext.RequestServices.GetRequiredService<IConfiguration>();
        var validApiKey = configuration.GetValue<string>("ApiKeys:Service");

        if (!validApiKey.Equals(extractedApiKey))
        {
            context.Result = new UnauthorizedObjectResult("API Key inválida");
            return;
        }

        await next();
    }
}
```

## 🛡️ Autorización

### Políticas basadas en roles

```csharp
builder.Services.AddAuthorization(options =>
{
    options.AddPolicy("AdminOnly", policy =>
        policy.RequireRole("Admin"));

    options.AddPolicy("ManagerOrAdmin", policy =>
        policy.RequireRole("Manager", "Admin"));

    options.AddPolicy("CountryAccess", policy =>
        policy.RequireClaim("country"));
});
```

## 🔒 Comunicación segura

### TLS/HTTPS

**Requisitos obligatorios:**

- TLS 1.2 mínimo, TLS 1.3 recomendado
- Certificados válidos y actualizados
- HTTPS redirect automático
- HSTS habilitado

```csharp
if (!app.Environment.IsDevelopment())
{
    app.UseHttpsRedirection();
    app.UseHsts();
}

// Headers de seguridad
app.Use(async (context, next) =>
{
    context.Response.Headers.Add("X-Content-Type-Options", "nosniff");
    context.Response.Headers.Add("X-Frame-Options", "DENY");
    context.Response.Headers.Add("Strict-Transport-Security",
        "max-age=31536000; includeSubDomains");

    await next();
});
```

### CORS

```csharp
builder.Services.AddCors(options =>
{
    options.AddPolicy("TalmaPolicy", policy =>
    {
        policy.WithOrigins("https://app.talma.pe", "https://admin.talma.pe")
              .AllowAnyMethod()
              .AllowAnyHeader()
              .AllowCredentials();
    });
});
```

## 🔧 Protección de datos

### Validación de entrada

```csharp
public class SecureUserRequest
{
    [Required]
    [StringLength(100, MinimumLength = 2)]
    [RegularExpression(@"^[a-zA-Z0-9\s._-]+$")]
    public string Name { get; set; }

    [Required]
    [EmailAddress]
    public string Email { get; set; }
}
```

### Rate Limiting

```csharp
builder.Services.AddMemoryCache();
builder.Services.Configure<IpRateLimitOptions>(
    builder.Configuration.GetSection("IpRateLimit"));
builder.Services.AddSingleton<IIpPolicyStore, MemoryCacheIpPolicyStore>();
builder.Services.AddSingleton<IRateLimitCounterStore, MemoryCacheRateLimitCounterStore>();

app.UseIpRateLimiting();
```

## ⚙️ Configuración recomendada

### appsettings.json

```json
{
  "Jwt": {
    "Issuer": "https://api.talma.pe",
    "Audience": "https://app.talma.pe",
    "Key": "your-256-bit-secret-key-here",
    "ExpiryInHours": 24
  },
  "ApiKeys": {
    "Service": "your-service-api-key-here"
  },
  "IpRateLimit": {
    "EnableEndpointRateLimiting": true,
    "GeneralRules": [
      {
        "Endpoint": "*",
        "Period": "1m",
        "Limit": 60
      }
    ]
  }
}
```

### Variables de entorno

```bash
# Nunca hardcodear secrets en código
JWT_KEY=your-production-jwt-key-256-bits-long
API_SERVICE_KEY=your-production-api-key
AZURE_CLIENT_SECRET=your-azure-app-secret
```

## 🚨 Respuestas de seguridad

### Autenticación fallida

```json
{
  "status": "error",
  "error": {
    "code": "AUTHENTICATION_FAILED",
    "message": "Token inválido o expirado",
    "details": []
  },
  "meta": {
    "timestamp": "2025-09-22T10:30:00Z"
  },
  "trace_id": "sec_abc123-def456-789012"
}
```

### Acceso no autorizado

```json
{
  "status": "error",
  "error": {
    "code": "INSUFFICIENT_PERMISSIONS",
    "message": "No tienes permisos para acceder a este recurso",
    "details": []
  },
  "meta": {
    "timestamp": "2025-09-22T10:30:00Z"
  },
  "trace_id": "sec_def456-ghi789-012345"
}
```

## ✅ Checklist de seguridad

### Básico

- [ ] HTTPS habilitado en todos los entornos
- [ ] Headers de seguridad configurados
- [ ] Validación de entrada implementada
- [ ] Rate limiting activo

### Autenticación

- [ ] JWT configurado correctamente
- [ ] Tokens con expiración apropiada
- [ ] API Keys para servicios

### Autorización

- [ ] Políticas de autorización definidas
- [ ] Control de acceso por recursos
- [ ] Validación de permisos en endpoints

### Monitoreo

- [ ] Logging de eventos de seguridad
- [ ] Alertas para intentos no autorizados

## 📖 Referencias

### ADRs relacionados

- [ADR-004: Autenticación SSO](/docs/adrs/adr-004-autenticacion-sso)
- [ADR-003: Gestión de secretos](/docs/adrs/adr-003-gestion-secretos)
- [ADR-008: Gateway de APIs](/docs/adrs/adr-008-gateway-apis)
- [ADR-016: Logging estructurado](/docs/adrs/adr-016-logging-estructurado)

### Estándares de la industria

- [OAuth 2.0 RFC 6749](https://tools.ietf.org/html/rfc6749)
- [JWT RFC 7519](https://tools.ietf.org/html/rfc7519)
- [OWASP API Security Top 10](https://owasp.org/www-project-api-security/)
- [Microsoft Identity Platform](https://docs.microsoft.com/en-us/azure/active-directory/develop/)
