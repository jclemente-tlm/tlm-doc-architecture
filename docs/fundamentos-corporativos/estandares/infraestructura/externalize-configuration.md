---
id: externalize-configuration
sidebar_position: 5
title: Externalización de Configuración
description: Estándares para separar la configuración del código, inyección vía variables de entorno y jerarquía de fuentes de configuración en .NET 8.
tags: [infraestructura, configuracion, dotnet, environment-variables, 12factor]
---

# Externalización de Configuración

## Contexto

Toda configuración environment-specific (connection strings, feature flags, timeouts, API keys) debe vivir fuera del código fuente. Este estándar define cómo externalizar configuración siguiendo el principio [XII-Factor Config](https://12factor.net/config) e inyectarla vía variables de entorno en runtime. Complementa el lineamiento [Infraestructura como Código](../../lineamientos/operabilidad/02-infraestructura-como-codigo.md).

**Conceptos incluidos:**

- **Externalize Configuration** → Separar config del código fuente
- **Environment Variables** → Inyección de config vía variables de entorno en .NET 8

---

## Stack Tecnológico

| Componente                | Tecnología                         | Versión | Uso                                  |
| ------------------------- | ---------------------------------- | ------- | ------------------------------------ |
| **Configuration Format**  | JSON, YAML                         | -       | Formato de archivos de configuración |
| **Config Library (.NET)** | Microsoft.Extensions.Configuration | .NET 8  | Configuración en ASP.NET Core        |
| **Runtime Injection**     | Environment Variables              | -       | Inyección en tiempo de ejecución     |
| **IaC**                   | Terraform                          | 1.7+    | Inyección en ECS Task Definition     |

---

## Externalize Configuration

Práctica de separar toda la configuración (connection strings, API keys, feature flags, etc.) del código fuente, permitiendo cambios sin recompilar o redesplegar.

**Propósito:** Independencia entre código y configuración, facilitando despliegues en múltiples ambientes y cambios dinámicos.

**¿Qué debe externalizarse?**

- ✅ Connection strings (bases de datos, Redis, Kafka)
- ✅ API keys y tokens
- ✅ URLs de servicios externos
- ✅ Feature flags
- ✅ Límites y umbrales (timeouts, retry attempts, rate limits)
- ✅ Secrets (passwords, private keys, certificates)
- ✅ Environment-specific values (log level, batch size)

**¿Qué NO debe externalizarse?**

- ❌ Valores constantes que nunca cambian (ej. `MaxNameLength = 100`)
- ❌ Lógica de negocio
- ❌ Defaults razonables que aplican a todos los ambientes

### Ejemplo Comparativo

```csharp
// ❌ MALO: Hardcoded Configuration
public class CustomerService
{
    private readonly string _connectionString =
        "Host=prod-db.talma.com;Database=customers;User=admin;Password=P@ssw0rd123";

    private readonly int _retryAttempts = 3;
    private readonly int _timeoutSeconds = 30;
}

// Problemas:
// 1. Password expuesto en código
// 2. Imposible cambiar timeout sin recompilar
// 3. No se puede usar diferentes configs para dev/prod
// 4. Password en repositorio Git (security risk)
```

```csharp
// ✅ BUENO: Externalized Configuration
public class CustomerService
{
    private readonly IConfiguration _configuration;

    public CustomerService(IConfiguration configuration)
    {
        _configuration = configuration;
    }

    public async Task<Customer> GetCustomerAsync(Guid id)
    {
        var connectionString = _configuration.GetConnectionString("CustomerDb");
        var retryAttempts = _configuration.GetValue<int>("Resilience:RetryAttempts");
        var timeoutSeconds = _configuration.GetValue<int>("Resilience:TimeoutSeconds");

        using var connection = new NpgsqlConnection(connectionString);
        // ...
    }
}
```

### Jerarquía de Fuentes de Configuración (.NET 8)

ASP.NET Core carga configuración en este orden (último gana):

```csharp
// Program.cs — jerarquía implícita
// 1. appsettings.json            → defaults razonables
// 2. appsettings.{Env}.json      → overrides por ambiente
// 3. User Secrets                → solo Development
// 4. Environment Variables       → runtime (mayor prioridad)
// 5. Command-line arguments      → runtime
```

| Fuente                   | Uso                        | Contenido                                 |
| ------------------------ | -------------------------- | ----------------------------------------- |
| `appsettings.json`       | Defaults razonables        | Timeouts, retry attempts, log level DEBUG |
| `appsettings.{Env}.json` | Overrides por ambiente     | URLs, feature flags                       |
| AWS Parameter Store      | Config no sensible runtime | URLs de APIs, límites                     |
| AWS Secrets Manager      | Secrets                    | Connection strings, API keys              |
| Environment Variables    | Inyección final            | Todo lo anterior inyectado por ECS        |

### Setup en .NET 8

```csharp
// Program.cs
var builder = WebApplication.CreateBuilder(args);

builder.Configuration
    .AddJsonFile("appsettings.json", optional: false, reloadOnChange: true)
    .AddJsonFile($"appsettings.{builder.Environment.EnvironmentName}.json", optional: true)
    .AddEnvironmentVariables();

if (builder.Environment.IsDevelopment())
{
    builder.Configuration.AddUserSecrets<Program>();
}

// Strongly-typed settings
builder.Services.Configure<ResilienceSettings>(
    builder.Configuration.GetSection("Resilience"));
builder.Services.Configure<FeatureSettings>(
    builder.Configuration.GetSection("Features"));

var app = builder.Build();
app.Run();
```

### Ejemplo appsettings.json vs Production

```json
// appsettings.json (defaults)
{
  "Logging": {
    "LogLevel": {
      "Default": "Information",
      "Microsoft.AspNetCore": "Warning"
    }
  },
  "ConnectionStrings": {
    "CustomerDb": "Host=localhost;Database=customers_dev;Username=dev;Password=dev"
  },
  "Resilience": {
    "RetryAttempts": 3,
    "TimeoutSeconds": 30,
    "CircuitBreakerThreshold": 5
  },
  "Features": {
    "EnableAdvancedSearch": false
  }
}
```

```json
// appsettings.Production.json (overrides mínimos)
{
  "Logging": {
    "LogLevel": {
      "Default": "Warning"
    }
  },
  "Features": {
    "EnableAdvancedSearch": true
  }
  // NOTE: NO incluye ConnectionStrings (viene de Secrets Manager)
}
```

---

## Environment Variables

Variables del sistema operativo inyectadas al proceso en tiempo de ejecución. Mecanismo estándar para 12-Factor App y contenedores.

**Formato en .NET:**

```bash
# Estructura jerárquica con doble guión bajo (__)
ConnectionStrings__CustomerDb="Host=prod-db;..."
Resilience__RetryAttempts=3
Features__EnableAdvancedSearch=true
```

ASP.NET Core mapea automáticamente `__` → `:`, por lo que `Resilience__RetryAttempts` equivale a `Configuration["Resilience:RetryAttempts"]`.

### Docker Compose (Development)

```yaml
# docker-compose.yml — inyección de config en desarrollo
services:
  customer-api:
    image: customer-service:latest
    ports:
      - "8080:80"
    environment:
      - ASPNETCORE_ENVIRONMENT=Development
      - ConnectionStrings__CustomerDb=Host=postgres;Database=customers_dev;Username=dev;Password=dev
      - Resilience__RetryAttempts=3
      - Resilience__TimeoutSeconds=30
      - Features__EnableAdvancedSearch=false
      - Logging__LogLevel__Default=Debug
    depends_on:
      - postgres
      - redis
```

### ECS Task Definition (Production)

```hcl
# terraform/modules/ecs/task-definition.tf
resource "aws_ecs_task_definition" "customer_service" {
  container_definitions = jsonencode([{
    name  = "customer-api"
    image = "${var.ecr_repository_url}:${var.image_tag}"

    # Environment variables (non-sensitive)
    environment = [
      { name = "ASPNETCORE_ENVIRONMENT", value = title(var.environment) },
      { name = "Resilience__RetryAttempts", value = "3" },
      { name = "Resilience__TimeoutSeconds", value = "30" },
      { name = "Features__EnableAdvancedSearch", value = "true" },
      { name = "Features__EnableCache", value = "true" }
    ]

    # Secrets desde Secrets Manager (inyectados como env vars de forma segura)
    secrets = [
      {
        name      = "ConnectionStrings__CustomerDb"
        valueFrom = "${aws_secretsmanager_secret.customer_db.arn}:connectionString::"
      },
      {
        name      = "ExternalApi__ApiKey"
        valueFrom = aws_secretsmanager_secret.external_api_key.arn
      }
    ]
  }])
}
```

---

## Requisitos Técnicos

### MUST (Obligatorio)

- **MUST** externalizar toda configuración environment-specific (URLs, connection strings, feature flags)
- **MUST** nunca incluir secrets en código fuente o repositorio Git
- **MUST** usar `appsettings.json` solo para defaults razonables
- **MUST** soportar override vía environment variables
- **MUST** inyectar configuración vía environment variables en runtime
- **MUST** usar naming convention jerárquico (`Section__SubSection__Key`)
- **MUST** documentar todas las environment variables requeridas en README del servicio

### SHOULD (Fuertemente recomendado)

- **SHOULD** usar strongly-typed configuration classes en .NET (`IOptions<T>`)
- **SHOULD** validar configuración al startup con `ValidateOnStart()` (fail fast si config inválida)
- **SHOULD** implementar reload de configuración sin restart donde sea posible
- **SHOULD** usar feature flags para habilitar/deshabilitar funcionalidad en runtime

### MUST NOT (Prohibido)

- **MUST NOT** incluir secrets en `appsettings.json` o archivos de configuración versionados
- **MUST NOT** hardcodear URLs, passwords, API keys en código
- **MUST NOT** usar archivos de configuración environment-specific versionados en Git con secrets

---

## Referencias

- [XII-Factor — III. Config](https://12factor.net/config) — principio de externalización de configuración
- [Configuration in ASP.NET Core](https://docs.microsoft.com/en-us/aspnet/core/fundamentals/configuration/) — sistema de configuración en .NET 8
- [Options pattern](https://docs.microsoft.com/en-us/aspnet/core/fundamentals/configuration/options) — tipado fuerte de configuración en .NET
- [Configuración Centralizada](./centralized-configuration.md) — AWS Parameter Store y Secrets Manager para config en runtime
- [Paridad de Ambientes](./environment-parity.md) — consistencia de configuración entre dev/staging/prod
- [Containerización](./containerization.md) — inyección de configuración en contenedores ECS
- [Infrastructure as Code — Implementación](./iac-implementation.md) — provisioning de configuración con Terraform
