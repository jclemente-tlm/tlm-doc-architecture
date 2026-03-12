---
id: configuration-management
sidebar_position: 5
title: Gestión de Configuración
description: Estándares para externalizar configuración del código e inyectarla en runtime con variables de entorno, AWS Parameter Store y Secrets Manager.
tags:
  [infraestructura, configuracion, dotnet, aws, parametros, secretos, 12factor]
---

# Gestión de Configuración

## Contexto

Toda configuración environment-specific (connection strings, feature flags, timeouts, API keys) debe vivir fuera del código fuente. Este estándar define cómo externalizar la configuración siguiendo el principio [XII-Factor Config](https://12factor.net/config) e inyectarla en runtime usando variables de entorno, AWS Parameter Store y Secrets Manager. Complementa el lineamiento [Infraestructura como Código](../../lineamientos/operabilidad/infraestructura-como-codigo.md).

**Conceptos incluidos:**

- **Externalización** → Separar toda config environment-specific del código fuente
- **Variables de Entorno** → Inyección de configuración en runtime
- **Parameter Store** → Configuración no sensible centralizada en AWS
- **Secrets Manager** → Secrets con cifrado KMS y rotación automática

---

## Stack Tecnológico

| Componente                | Tecnología                         | Versión | Uso                                  |
| ------------------------- | ---------------------------------- | ------- | ------------------------------------ |
| **Config Library (.NET)** | Microsoft.Extensions.Configuration | .NET 8  | Configuración en ASP.NET Core        |
| **Runtime Injection**     | Environment Variables              | -       | Inyección en tiempo de ejecución     |
| **Centralized Config**    | AWS Parameter Store                | -       | Configuración no sensible            |
| **Secrets Management**    | AWS Secrets Manager                | -       | Configuración sensible (credentials) |
| **Encryption**            | AWS KMS                            | -       | Cifrado de secrets                   |
| **IaC**                   | Terraform                          | 1.7+    | Provisioning de parámetros y secrets |

---

## Externalización de Configuración

Toda configuración environment-specific debe separarse del código, permitiendo cambios sin recompilar ni redesplegar.

**¿Qué debe externalizarse?**

- ✅ Connection strings, API keys, tokens
- ✅ URLs de servicios externos y feature flags
- ✅ Límites y umbrales (timeouts, retry attempts, rate limits)

**¿Qué NO debe externalizarse?**

- ❌ Constantes que nunca cambian (`MaxNameLength = 100`)
- ❌ Lógica de negocio
- ❌ Defaults razonables que aplican a todos los ambientes

```csharp
// ❌ MALO: Configuración hardcoded
public class CustomerService
{
    private readonly string _connectionString =
        "Host=prod-db.talma.com;Database=customers;User=admin;Password=P@ssw0rd123";
}

// ✅ BUENO: Configuración externalizada
public class CustomerService
{
    private readonly IConfiguration _configuration;

    public CustomerService(IConfiguration configuration)
        => _configuration = configuration;

    public async Task<Customer> GetCustomerAsync(Guid id)
    {
        var connectionString = _configuration.GetConnectionString("CustomerDb");
        var retryAttempts = _configuration.GetValue<int>("Resilience:RetryAttempts");
        // ...
    }
}
```

### Jerarquía de Fuentes en .NET 8

ASP.NET Core carga configuración en este orden (último gana):

| Fuente                   | Uso                        | Contenido                              |
| ------------------------ | -------------------------- | -------------------------------------- |
| `appsettings.json`       | Defaults razonables        | Timeouts, log level, feature flags off |
| `appsettings.{Env}.json` | Overrides por ambiente     | URLs, feature flags por ambiente       |
| AWS Parameter Store      | Config no sensible runtime | URLs de APIs, límites                  |
| AWS Secrets Manager      | Secrets                    | Connection strings, API keys           |
| Environment Variables    | Inyección final (ECS)      | Todo lo anterior inyectado             |

```csharp
// Program.cs
var builder = WebApplication.CreateBuilder(args);

builder.Configuration
    .AddJsonFile("appsettings.json", optional: false, reloadOnChange: true)
    .AddJsonFile($"appsettings.{builder.Environment.EnvironmentName}.json", optional: true)
    .AddEnvironmentVariables();

if (builder.Environment.IsDevelopment())
    builder.Configuration.AddUserSecrets<Program>();

// Strongly-typed settings
builder.Services.Configure<ResilienceSettings>(
    builder.Configuration.GetSection("Resilience"));

var app = builder.Build();
app.Run();
```

---

## Parameter Store vs Secrets Manager

| Característica    | Parameter Store        | Secrets Manager                    |
| ----------------- | ---------------------- | ---------------------------------- |
| **Uso**           | Config no sensible     | Secrets (passwords, keys)          |
| **Costo**         | Gratis (Standard tier) | $0.40/secret/mes + $0.05/10K calls |
| **Auto-rotation** | No                     | Sí (para RDS, etc.)                |
| **Encryption**    | Opcional (KMS)         | Obligatorio (KMS)                  |

**Regla simple:**

- **Secrets Manager**: Passwords, API keys, tokens, certificates
- **Parameter Store**: Todo lo demás (URLs, timeouts, feature flags)

### Naming Convention

```
/{service-name}/{environment}/{category}/{parameter-name}

Ejemplos:
/customer-service/production/database/host
/customer-service/production/resilience/retry-attempts
/customer-service/production/features/enable-advanced-search
```

### Provisioning con Terraform

```hcl
# terraform/modules/parameter-store/main.tf

resource "aws_ssm_parameter" "database_host" {
  name  = "/${var.service_name}/${var.environment}/database/host"
  type  = "String"
  value = var.database_host
  tags  = { Service = var.service_name, Environment = var.environment, ManagedBy = "Terraform" }
}

resource "aws_ssm_parameter" "database_password" {
  name   = "/${var.service_name}/${var.environment}/database/password"
  type   = "SecureString"
  value  = random_password.db_password.result
  key_id = aws_kms_key.parameter_store.id
  tags   = { Service = var.service_name, Environment = var.environment, ManagedBy = "Terraform" }
}

resource "aws_secretsmanager_secret" "customer_db" {
  name = "${var.service_name}/${var.environment}/database/credentials"
  tags = { Service = var.service_name, Environment = var.environment, ManagedBy = "Terraform" }
}

resource "aws_secretsmanager_secret_version" "customer_db" {
  secret_id = aws_secretsmanager_secret.customer_db.id
  secret_string = jsonencode({
    username         = "customer_svc"
    password         = random_password.db_password.result
    host             = aws_db_instance.customer_db.address
    connectionString = "Host=${aws_db_instance.customer_db.address};..."
  })
}
```

### IAM Policy para ECS Task

```hcl
# terraform/modules/ecs/iam.tf

resource "aws_iam_role_policy" "parameter_store_read" {
  role = aws_iam_role.ecs_task_role.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = ["ssm:GetParameter", "ssm:GetParameters", "ssm:GetParametersByPath"]
      Resource = "arn:aws:ssm:${var.aws_region}:${var.aws_account_id}:parameter/${var.service_name}/${var.environment}/*"
    }]
  })
}

resource "aws_iam_role_policy" "secrets_manager_read" {
  role = aws_iam_role.ecs_task_role.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = ["secretsmanager:GetSecretValue"]
      Resource = "arn:aws:secretsmanager:${var.aws_region}:${var.aws_account_id}:secret:${var.service_name}/${var.environment}/*"
    }]
  })
}
```

### Leer desde .NET 8

```csharp
// Program.cs — integración con AWS Systems Manager
builder.Configuration.AddSystemsManager(configureSource =>
{
    configureSource.Path = $"/customer-service/{builder.Environment.EnvironmentName}";
    configureSource.ReloadAfter = TimeSpan.FromMinutes(5);
});
```

---

## Variables de Entorno

**Formato en .NET** — ASP.NET Core mapea `__` → `:`:

```bash
ConnectionStrings__CustomerDb="Host=prod-db;..."
Resilience__RetryAttempts=3
Features__EnableAdvancedSearch=true
```

### Docker Compose (Development)

```yaml
services:
  customer-api:
    image: customer-service:latest
    environment:
      - ASPNETCORE_ENVIRONMENT=Development
      - ConnectionStrings__CustomerDb=Host=postgres;Database=customers_dev;Username=dev;Password=dev
      - Resilience__RetryAttempts=3
      - Features__EnableAdvancedSearch=false
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

    environment = [
      { name = "ASPNETCORE_ENVIRONMENT", value = title(var.environment) },
      { name = "Resilience__RetryAttempts", value = "3" },
      { name = "Features__EnableAdvancedSearch", value = "true" }
    ]

    secrets = [
      {
        name      = "ConnectionStrings__CustomerDb"
        valueFrom = "${aws_secretsmanager_secret.customer_db.arn}:connectionString::"
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
- **MUST** usar AWS Parameter Store para configuración non-sensitive en runtime
- **MUST** usar AWS Secrets Manager para secrets (passwords, API keys, tokens)
- **MUST** provisionar configuración vía Terraform (no manual en consola)
- **MUST** usar naming convention `/{service-name}/{environment}/{category}/{param}` en Parameter Store
- **MUST** usar IAM policies con least privilege para acceso a configuración
- **MUST** documentar todas las environment variables requeridas en README del servicio

### SHOULD (Fuertemente recomendado)

- **SHOULD** usar strongly-typed configuration classes en .NET (`IOptions<T>`)
- **SHOULD** validar configuración al startup con `ValidateOnStart()` (fail fast)
- **SHOULD** usar mismo mecanismo de secrets en dev/staging/prod (Secrets Manager)
- **SHOULD** habilitar rotación automática de secrets de RDS en Secrets Manager

### MUST NOT (Prohibido)

- **MUST NOT** hardcodear URLs, passwords, API keys en código
- **MUST NOT** incluir secrets en `appsettings.json` o archivos versionados en Git
- **MUST NOT** crear parámetros o secrets manualmente en consola AWS (usar Terraform)

---

## Referencias

- [XII-Factor — III. Config](https://12factor.net/config) — principio de externalización de configuración
- [Configuration in ASP.NET Core](https://docs.microsoft.com/en-us/aspnet/core/fundamentals/configuration/) — sistema de configuración en .NET 8
- [AWS Parameter Store](https://docs.aws.amazon.com/systems-manager/latest/userguide/systems-manager-parameter-store.html) — configuración centralizada
- [AWS Secrets Manager](https://docs.aws.amazon.com/secretsmanager/latest/userguide/) — gestión de secrets con rotación automática
- [ECS Task Definition Secrets](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/specifying-sensitive-data-secrets.html) — inyección de secrets en contenedores
- [Paridad de Ambientes](./environment-parity.md) — consistencia de configuración entre dev/staging/prod
- [Contenerización](./containerization.md) — inyección de configuración en contenedores ECS
- [IaC — Estándares Terraform](./iac-standards.md) — provisioning de configuración con Terraform
- [Secrets Management](../seguridad/secrets-key-management.md) — gestión de secrets y rotación de claves
