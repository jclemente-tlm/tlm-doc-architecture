---
id: externalizar-configuracion-12factor
sidebar_position: 5
title: Externalizar Configuración (12-Factor App)
description: Estándar para externalizar configuración en variables de entorno según 12-Factor App Factor III, garantizando separación config/código.
---

# Estándar Técnico — Externalizar Configuración (12-Factor App)

---

## 1. Propósito

Externalizar toda configuración en variables de entorno según **12-Factor App Factor III**, garantizando portabilidad, seguridad y separación estricta código/config para entornos multi-cloud.

---

## 2. Alcance

**Aplica a:**

- Microservicios, aplicaciones serverless, APIs
- Configuración de BD, endpoints externos, secrets
- Despliegues en AWS, AWS, AWS ECS Fargate
- Entornos dev, staging, producción

**No aplica a:**

- Constantes de dominio (en código)
- Configuración de build (nuget.config)
- Opciones de IDE/tooling

---

## 3. Tecnologías Aprobadas

| Componente             | Tecnología              | Versión mínima | Observaciones           |
| ---------------------- | ----------------------- | -------------- | ----------------------- |
| **Secrets Management** | AWS Secrets Manager     | N/A            | Para secrets sensibles  |
| **Secrets Management** | AWS SSM Parameter Store | N/A            | Para config no sensible |
| **App Config**         | .NET IConfiguration     | .NET 6+        | Con providers AWS       |
| **Container Env Vars** | Docker/ECS/AWS ECS Fargate          | N/A            | Inyección en runtime    |
| **Local Development**  | dotnet user-secrets     | .NET 6+        | Desarrollo local        |

> Prohibido hardcodear secrets o config específica de entorno en código.

---

## 4. Requisitos Obligatorios 🔴

- [ ] **CERO** configuración hardcodeada en código fuente
- [ ] Variables de entorno para toda config específica de entorno
- [ ] Secrets en AWS Secrets Manager (NO en código/repos)
- [ ] Configuración no sensible en SSM Parameter Store
- [ ] Nombres estandarizados: `APP_NAME__SECTION__KEY` (doble guion bajo)
- [ ] Variables obligatorias documentadas en README.md
- [ ] Validación al inicio: aplicación falla si falta config crítica
- [ ] .NET: usar `IConfiguration` con providers AWS
- [ ] Separación clara: secrets vs config vs constantes de dominio
- [ ] NO commits de `.env`, `appsettings.Production.json` con secrets
- [ ] Local dev: `dotnet user-secrets` o `.env.local` (gitignored)
- [ ] Despliegue: env vars inyectadas por ECS/AWS ECS Fargate/Lambda

---

## 5. Prohibiciones

- ❌ Secrets en appsettings.json committed en git
- ❌ Connection strings hardcodeadas
- ❌ API keys o tokens en código
- ❌ Config específica de prod en código
- ❌ Diferentes mecanismos de config por entorno (usar uno solo)
- ❌ Variables de entorno sin documentar
- ❌ Aplicación que inicia sin validar config crítica

---

## 6. Configuración Mínima

### .NET con IConfiguration y AWS

```csharp
// Program.cs
var builder = WebApplication.CreateBuilder(args);

// Orden de precedencia: env vars > AWS Systems Manager > appsettings.json
builder.Configuration
    .AddJsonFile("appsettings.json", optional: false)
    .AddJsonFile($"appsettings.{builder.Environment.EnvironmentName}.json", optional: true)
    .AddSystemsManager($"/talma/{builder.Environment.EnvironmentName}/")
    .AddEnvironmentVariables(); // Mayor precedencia

// Validación de config crítica
var dbConnection = builder.Configuration["Database__ConnectionString"];
if (string.IsNullOrEmpty(dbConnection))
    throw new InvalidOperationException("Database__ConnectionString es obligatoria");

var app = builder.Build();
```

### Docker/ECS task definition

```json
{
  "containerDefinitions": [
    {
      "name": "api-orders",
      "environment": [
        { "name": "ASPNETCORE_ENVIRONMENT", "value": "Production" },
        { "name": "APP_NAME", "value": "orders-api" }
      ],
      "secrets": [
        {
          "name": "Database__ConnectionString",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:123456789012:secret:rds/prod/orders-abc123"
        },
        {
          "name": "Auth__JwtSecret",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:123456789012:secret:jwt/prod-xyz789"
        }
      ]
    }
  ]
}
```

### Naming convention

```bash
# Estándar: APP_NAME__SECTION__KEY (doble guion bajo)
DATABASE__CONNECTIONSTRING=...
AUTH__JWTSECRET=...
REDIS__ENDPOINT=...
AWS__REGION=us-east-1
LOGGING__LOGLEVEL__DEFAULT=Information
```

### README.md obligatorio

```markdown
## Variables de Entorno Requeridas

| Variable                     | Descripción                  | Ejemplo                                   | Obligatoria           |
| ---------------------------- | ---------------------------- | ----------------------------------------- | --------------------- |
| `Database__ConnectionString` | Connection string PostgreSQL | `Host=...`                                | ✅                    |
| `Auth__JwtSecret`            | Secret para JWT              | (desde Secrets Manager)                   | ✅                    |
| `Redis__Endpoint`            | Endpoint ElastiCache         | `redis.prod.xxx.cache.amazonaws.com:6379` | ✅                    |
| `AWS__Region`                | AWS region                   | `us-east-1`                               | ✅                    |
| `Logging__LogLevel__Default` | Nivel de logs                | `Information`                             | ❌ (default: Warning) |
```

---

## 7. Validación

**Checklist de cumplimiento:**

- [ ] `git log -p | grep -i "password\|secret\|key"` → **sin resultados**
- [ ] README.md documenta todas las env vars obligatorias
- [ ] `.env`, `*.Production.json` en `.gitignore`
- [ ] Secrets en AWS Secrets Manager (verificar ARNs en task definition)
- [ ] Aplicación valida config crítica al inicio (fail fast)
- [ ] Config local usa `dotnet user-secrets` (NO `.env` committeado)

**Métricas de cumplimiento:**

| Métrica                    | Target         | Verificación                   |
| -------------------------- | -------------- | ------------------------------ |
| Secrets en código          | 0              | `git-secrets` scan + SonarQube |
| Variables documentadas     | 100%           | README.md review               |
| Validación al inicio       | 100% servicios | Code review                    |
| Uso de AWS Secrets Manager | 100% secrets   | Task definitions audit         |

Incumplimientos bloquean deployment a producción.

---

## 8. Referencias

- [12-Factor App — Config (Factor III)](https://12factor.net/config)
- [AWS Secrets Manager](https://docs.aws.amazon.com/secretsmanager/)
- [.NET Configuration](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/configuration/)
- [ADR-005: Gestión de Configuraciones](../../../decisiones-de-arquitectura/adr-005-gestion-configuraciones.md)
