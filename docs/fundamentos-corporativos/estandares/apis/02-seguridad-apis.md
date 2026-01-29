---
id: seguridad-apis
sidebar_position: 2
title: Seguridad de APIs
description: Estándar de seguridad para APIs REST; autenticación JWT/OAuth, autorización RBAC, HTTPS/TLS, rate limiting y protección de datos
---

# Estándar Técnico — Seguridad de APIs

---

## 1. Propósito
Garantizar seguridad mediante autenticación JWT/OAuth 2.0 con RS256, autorización RBAC, HTTPS/TLS 1.3, rate limiting, CORS restringido y protección de datos sensibles sin exposición en logs.

---

## 2. Alcance

**Aplica a:**
- Todas las APIs REST (públicas, privadas, internas)
- APIs de integración con sistemas externos
- Microservicios con comunicación HTTP

**No aplica a:**
- gRPC services (estándar separado)
- Comunicación interna mesh service-to-service sin Internet exposure

---

## 3. Tecnologías Aprobadas

| Componente | Tecnología | Versión mínima | Observaciones |
|-----------|------------|----------------|---------------|
| **Autenticación** | AspNetCore.Authentication.JwtBearer | 8.0+ | JWT Bearer con RS256 |
| **OAuth/OIDC** | Microsoft.Identity.Web | 2.15+ | Azure AD / OAuth 2.0 / OpenID |
| **Rate Limiting** | AspNetCoreRateLimit | 5.0+ | Límites por IP/usuario |
| **CORS** | AspNetCore.Cors | 8.0+ | Configuración explícita de orígenes |
| **TLS** | TLS 1.3 (1.2 compatible) | - | Encryption en tránsito |
| **JWT Algorithm** | RS256 (RSA + SHA256) | - | Asimétrico obligatorio |

> El uso de tecnologías no listadas requiere aprobación de Arquitectura.

---

## 4. Requisitos Obligatorios 🔴

- [ ] HTTPS/TLS 1.3 en todos los entornos (incluido desarrollo)
- [ ] Autenticación JWT con algoritmo RS256 (único permitido)
- [ ] Tokens JWT firmados con certificados RSA (NO secrets compartidos)
- [ ] Validación: Issuer, Audience, Lifetime, SigningKey
- [ ] Autorización RBAC con claims/roles en JWT
- [ ] CORS con orígenes explícitos (NO `AllowAnyOrigin` en prod)
- [ ] Rate limiting: 100 req/min por IP, 1000 req/min por usuario autenticado
- [ ] Headers de seguridad: X-Content-Type-Options, X-Frame-Options, CSP
- [ ] Secrets NUNCA en logs (enmascarar passwords, tokens, API keys)
- [ ] API keys en headers (NO query strings)
- [ ] Rotación de certificados JWT cada 90 días
- [ ] Logging de intentos de autenticación fallidos

---

## 5. Prohibiciones

- ❌ Algoritmos simétricos JWT (HS256, HS384, HS512)
- ❌ CORS `AllowAnyOrigin()` en producción
- ❌ HTTP sin TLS (incluido desarrollo local)
- ❌ Tokens en URLs o query strings
- ❌ Secrets en código fuente o logs
- ❌ Autenticación Basic sin HTTPS

---

## 6. Configuración Mínima

```csharp
// Program.cs
using Microsoft.AspNetCore.Authentication.JwtBearer;

builder.Services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
    .AddJwtBearer(options =>
    {
        options.Authority = builder.Configuration["Jwt:Authority"];
        options.Audience = builder.Configuration["Jwt:Audience"];
        
        options.TokenValidationParameters = new()
        {
            ValidateIssuer = true,
            ValidateAudience = true,
            ValidateLifetime = true,
            ValidateIssuerSigningKey = true,
            ValidAlgorithms = new[] { SecurityAlgorithms.RsaSha256 }, // RS256 obligatorio
            ClockSkew = TimeSpan.FromMinutes(5)
        };
    });

// CORS restringido
builder.Services.AddCors(options =>
{
    options.AddPolicy("AllowedOrigins", policy =>
    {
        policy.WithOrigins("https://app.talma.com", "https://admin.talma.com")
              .AllowAnyMethod()
              .AllowAnyHeader()
              .AllowCredentials();
    });
});

// Rate limiting
builder.Services.AddMemoryCache();
builder.Services.AddInMemoryRateLimiting();
builder.Services.Configure<IpRateLimitOptions>(options =>
{
    options.GeneralRules = new List<RateLimitRule>
    {
        new() { Endpoint = "*", Period = "1m", Limit = 100 }
    };
});

var app = builder.Build();

app.UseHttpsRedirection();
app.UseCors("AllowedOrigins");
app.UseIpRateLimiting();
app.UseAuthentication();
app.UseAuthorization();
app.MapControllers();
```

---

## 7. Validación

```bash
# Verificar TLS 1.3
openssl s_client -connect api.talma.com:443 -tls1_3

# Verificar autenticación JWT
curl -H "Authorization: Bearer <token>" https://api.talma.com/api/v1/users

# Verificar rate limiting
for i in {1..150}; do curl https://api.talma.com/api/v1/users; done

# Verificar CORS
curl -H "Origin: https://malicious.com" -I https://api.talma.com/api/v1/users

# Tests de seguridad
dotnet test --filter Category=Security
```

**Métricas de cumplimiento:**

| Métrica | Target | Verificación |
|---------|--------|--------------|  
| HTTPS habilitado | 100% | `curl -I` retorna 308 redirect |
| JWT con RS256 | 100% | Verificar header `alg` en token |
| Rate limiting activo | 100% | Request 151 retorna 429 |
| CORS restringido | 100% | Orígenes no permitidos retornan 403 |

Incumplimientos deben corregirse o documentarse mediante excepción aprobada.

---

## 8. Referencias

- [ADR-004: Autenticación SSO](../../../decisiones-de-arquitectura/adr-004-autenticacion-sso.md)
- [ADR-008: Gateway de APIs](../../../decisiones-de-arquitectura/adr-008-gateway-apis.md)
- [Diseño REST](./01-diseno-rest.md)
- [Gestión de Secretos](../infraestructura/03-secrets-management.md)
- [OWASP API Security Top 10](https://owasp.org/www-project-api-security/)
- [JWT Best Practices](https://auth0.com/blog/a-look-at-the-latest-draft-for-jwt-bcp/)
