---
id: secrets-management
sidebar_position: 3
title: Gestión de Secretos
description: Estándar técnico obligatorio para gestión segura de secretos con AWS Secrets Manager, rotación automática, least privilege y auditoría
---

# Gestión de Secretos

## 1. Propósito

Definir la configuración técnica obligatoria para gestionar secretos (passwords, API keys, certificados) de forma segura mediante:
- **AWS Secrets Manager** como herramienta principal con rotación automática
- **Never hardcode** - Cero secretos en código fuente, variables de entorno o logs
- **Rotación automática** cada 30-90 días con Lambda functions
- **Least privilege** - IAM policies granulares por servicio
- **Encryption** - AES-256 en reposo, TLS 1.3 en tránsito
- **Auditoría completa** - CloudTrail para todos los accesos

Garantiza cero leaks de secretos, compliance con PCI-DSS/SOC2, y recuperación ante compromiso.

## 2. Alcance

### Aplica a:

- ✅ Credenciales de bases de datos (PostgreSQL, SQL Server, Redis)
- ✅ API keys de servicios externos (Stripe, SendGrid, AWS services)
- ✅ OAuth tokens, JWT signing keys
- ✅ Certificados SSL/TLS privados
- ✅ Claves de encriptación simétricas/asimétricas
- ✅ Secretos en dev, staging, production (separados)

### NO aplica a:

- ❌ Configuraciones públicas (URLs de endpoints públicos)
- ❌ Feature flags (usar servicios específicos como LaunchDarkly)
- ❌ Valores no sensibles (timeouts, limits, nombres de recursos)
- ❌ Certificados públicos (estos son públicos por definición)

## 3. Tecnologías Obligatorias

| Categoría          | Tecnología / Configuración                | Versión   | Justificación                           |
| ------------------ | ----------------------------------------- | --------- | --------------------------------------- |
| **Secrets Store**  | AWS Secrets Manager                       | -         | Rotación automática, integración AWS    |
| **Encryption**     | AWS KMS (AES-256)                         | -         | Encryption at rest managed             |
| **SDK .NET**       | `AWSSDK.SecretsManager`                   | 3.7+      | Cliente oficial AWS                     |
| **SDK Node.js**    | `@aws-sdk/client-secrets-manager`         | 3.0+      | Cliente oficial AWS v3                  |
| **Rotation**       | AWS Lambda + RDS/Custom rotation          | -         | Rotación sin downtime                   |
| **Auditoría**      | AWS CloudTrail                            | -         | Log de todos los accesos                |
| **IAM**            | Políticas granulares por servicio         | -         | Least privilege                         |

### Tipos de Secretos

| Tipo                       | Ejemplos                            | Herramienta         | Rotación      |
| -------------------------- | ----------------------------------- | ------------------- | ------------- |
| **Credenciales BD**        | User, password, connection string   | Secrets Manager     | 30 días       |
| **API Keys**               | Stripe, SendGrid, third-party       | Secrets Manager     | 90 días       |
| **Certificados**           | SSL/TLS private keys                | ACM, Secrets Manager| 1 año         |
| **OAuth Tokens**           | Access tokens, refresh tokens       | Secrets Manager     | Por proveedor |
| **Encryption Keys**        | Symmetric/asymmetric keys           | AWS KMS             | 1 año         |

## 4. Configuración Técnica Obligatoria

### 4.1 Naming Convention para Secretos

### 4.1 Naming Convention para Secretos

```
{environment}/{service}/{secret-type}/{name}

✅ Ejemplos AWS Secrets Manager:
- prod/users-api/database/master-password
- prod/users-api/external-api/stripe-api-key
- prod/orders-api/jwt/signing-key
- staging/notifications/smtp/password
- dev/shared/redis/password
```

### 4.2 Creación de Secretos con AWS CLI

```bash
# Crear secreto simple
aws secretsmanager create-secret \
    --name prod/orders-api/database/master-password \
    --description "PostgreSQL master password" \
    --secret-string "SuperSecretPassword123!" \
    --tags Key=Environment,Value=production Key=Service,Value=orders-api

# Crear secreto JSON
aws secretsmanager create-secret \
    --name prod/orders-api/database/connection \
    --secret-string '{
        "username": "dbadmin",
        "password": "SuperSecretPassword123!",
        "host": "db.example.com",
        "port": 5432,
        "database": "orders"
    }'
```

### Configuración de rotación automática

```bash
aws secretsmanager rotate-secret \
    --secret-id prod/orders-api/database/master-password \
    --rotation-lambda-arn arn:aws:lambda:us-east-1:123456789012:function:SecretsManagerRotation \
    --rotation-rules AutomaticallyAfterDays=30
```

## 4. Implementación en .NET

### Configuración

```csharp
// Program.cs
builder.Configuration.AddSecretsManager(
    configurator: options =>
    {
        options.SecretFilter = entry =>
            entry.Name.StartsWith($"{builder.Environment.EnvironmentName}/");
        options.KeyGenerator = (secret, name) =>
            name.Replace($"{builder.Environment.EnvironmentName}/", "")
                .Replace("/", ":");
        options.PollingInterval = TimeSpan.FromHours(1);
    });
```

### Servicio de Secrets

```csharp
public interface ISecretsService
{
    Task<string> GetSecretAsync(string secretName);
    Task<T> GetSecretAsync<T>(string secretName) where T : class;
    Task UpdateSecretAsync(string secretName, string secretValue);
}

public class AwsSecretsService : ISecretsService
{
    private readonly IAmazonSecretsManager _secretsManager;
    private readonly IMemoryCache _cache;
    private readonly ILogger<AwsSecretsService> _logger;

    public AwsSecretsService(
        IAmazonSecretsManager secretsManager,
        IMemoryCache cache,
        ILogger<AwsSecretsService> logger)
    {
        _secretsManager = secretsManager;
        _cache = cache;
        _logger = logger;
    }

    public async Task<string> GetSecretAsync(string secretName)
    {
        var cacheKey = $"secret:{secretName}";

        if (_cache.TryGetValue(cacheKey, out string cachedSecret))
        {
            return cachedSecret;
        }

        try
        {
            var request = new GetSecretValueRequest
            {
                SecretId = secretName
            };

            var response = await _secretsManager.GetSecretValueAsync(request);

            var secret = response.SecretString;

            // Cache por 5 minutos
            _cache.Set(cacheKey, secret, TimeSpan.FromMinutes(5));

            _logger.LogInformation("Secret retrieved: {SecretName}", secretName);

            return secret;
        }
        catch (ResourceNotFoundException)
        {
            _logger.LogError("Secret not found: {SecretName}", secretName);
            throw;
        }
        catch (InvalidRequestException ex)
        {
            _logger.LogError(ex, "Invalid request for secret: {SecretName}", secretName);
            throw;
        }
        catch (InvalidParameterException ex)
        {
            _logger.LogError(ex, "Invalid parameter for secret: {SecretName}", secretName);
            throw;
        }
    }

    public async Task<T> GetSecretAsync<T>(string secretName) where T : class
    {
        var secretString = await GetSecretAsync(secretName);

        try
        {
            return JsonSerializer.Deserialize<T>(secretString)
                ?? throw new InvalidOperationException($"Failed to deserialize secret {secretName}");
        }
        catch (JsonException ex)
        {
            _logger.LogError(ex, "Failed to deserialize secret {SecretName}", secretName);
            throw;
        }
    }

    public async Task UpdateSecretAsync(string secretName, string secretValue)
    {
        var request = new UpdateSecretRequest
        {
            SecretId = secretName,
            SecretString = secretValue
        };

        await _secretsManager.UpdateSecretAsync(request);

        // Invalidar cache
        _cache.Remove($"secret:{secretName}");

        _logger.LogInformation("Secret updated: {SecretName}", secretName);
    }
}
```

### Uso en aplicación

```csharp
public class DatabaseConnectionFactory
{
    private readonly ISecretsService _secretsService;

    public DatabaseConnectionFactory(ISecretsService secretsService)
    {
        _secretsService = secretsService;
    }

    public async Task<NpgsqlConnection> CreateConnectionAsync()
    {
        var dbCredentials = await _secretsService
            .GetSecretAsync<DatabaseCredentials>(
                "prod/orders-api/database/connection");

        var connectionString = $"Host={dbCredentials.Host};" +
                              $"Port={dbCredentials.Port};" +
                              $"Database={dbCredentials.Database};" +
                              $"Username={dbCredentials.Username};" +
                              $"Password={dbCredentials.Password};" +
                              "SSL Mode=Require;";

        return new NpgsqlConnection(connectionString);
    }
}

public class DatabaseCredentials
{
    public string Host { get; set; }
    public int Port { get; set; }
    public string Database { get; set; }
    public string Username { get; set; }
    public string Password { get; set; }
}
```

## 5. Azure Key Vault

### Naming Conventions

```
{environment}-{service}-{secret-type}-{name}

Ejemplos:
- prod-orders-api-db-password
- prod-orders-api-stripe-key
- staging-notifications-smtp-password
```

### Configuración en .NET

```csharp
// Program.cs
var keyVaultEndpoint = new Uri(builder.Configuration["AzureKeyVault:VaultUri"]);

builder.Configuration.AddAzureKeyVault(
    keyVaultEndpoint,
    new DefaultAzureCredential());
```

### Servicio para Azure Key Vault

```csharp
public class AzureKeyVaultSecretsService : ISecretsService
{
    private readonly SecretClient _secretClient;
    private readonly IMemoryCache _cache;
    private readonly ILogger<AzureKeyVaultSecretsService> _logger;

    public AzureKeyVaultSecretsService(
        SecretClient secretClient,
        IMemoryCache cache,
        ILogger<AzureKeyVaultSecretsService> logger)
    {
        _secretClient = secretClient;
        _cache = cache;
        _logger = logger;
    }

    public async Task<string> GetSecretAsync(string secretName)
    {
        var cacheKey = $"secret:{secretName}";

        if (_cache.TryGetValue(cacheKey, out string cachedSecret))
        {
            return cachedSecret;
        }

        try
        {
            KeyVaultSecret secret = await _secretClient.GetSecretAsync(secretName);

            // Cache por 5 minutos
            _cache.Set(cacheKey, secret.Value, TimeSpan.FromMinutes(5));

            _logger.LogInformation("Secret retrieved from Key Vault: {SecretName}", secretName);

            return secret.Value;
        }
        catch (RequestFailedException ex) when (ex.Status == 404)
        {
            _logger.LogError("Secret not found in Key Vault: {SecretName}", secretName);
            throw;
        }
    }

    public async Task<T> GetSecretAsync<T>(string secretName) where T : class
    {
        var secretString = await GetSecretAsync(secretName);
        return JsonSerializer.Deserialize<T>(secretString)
            ?? throw new InvalidOperationException($"Failed to deserialize secret {secretName}");
    }

    public async Task UpdateSecretAsync(string secretName, string secretValue)
    {
        await _secretClient.SetSecretAsync(secretName, secretValue);

        // Invalidar cache
        _cache.Remove($"secret:{secretName}");

        _logger.LogInformation("Secret updated in Key Vault: {SecretName}", secretName);
    }
}
```

## 6. Gestión en Terraform/IaC

### AWS Secrets Manager

```hcl
resource "aws_secretsmanager_secret" "database_password" {
  name        = "prod/orders-api/database/master-password"
  description = "PostgreSQL master password for orders API"

  tags = {
    Environment = "production"
    Service     = "orders-api"
    ManagedBy   = "Terraform"
  }
}

resource "aws_secretsmanager_secret_version" "database_password" {
  secret_id     = aws_secretsmanager_secret.database_password.id
  secret_string = var.database_password # Pasar como variable, no hardcodear
}

# Rotación automática
resource "aws_secretsmanager_secret_rotation" "database_password" {
  secret_id           = aws_secretsmanager_secret.database_password.id
  rotation_lambda_arn = aws_lambda_function.rotate_secret.arn

  rotation_rules {
    automatically_after_days = 30
  }
}
```

### Azure Key Vault

```hcl
resource "azurerm_key_vault" "main" {
  name                = "talma-prod-kv"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  tenant_id           = data.azurerm_client_config.current.tenant_id
  sku_name            = "standard"

  purge_protection_enabled   = true
  soft_delete_retention_days = 90

  network_acls {
    bypass         = "AzureServices"
    default_action = "Deny"
    ip_rules       = var.allowed_ips
  }
}

resource "azurerm_key_vault_secret" "database_password" {
  name         = "prod-orders-api-db-password"
  value        = var.database_password
  key_vault_id = azurerm_key_vault.main.id

  tags = {
    Environment = "production"
    Service     = "orders-api"
  }
}
```

## 7. Buenas Prácticas

### En desarrollo local

```bash
# .env.local (NO COMMITEAR)
AWS_SECRETS_MANAGER_SECRET_NAME=dev/orders-api/database/connection
AWS_REGION=us-east-1

# Para desarrollo, usar AWS_PROFILE
AWS_PROFILE=talma-dev
```

### En CI/CD

```yaml
# GitHub Actions
env:
  AWS_REGION: us-east-1

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v1
        with:
          role-to-assume: arn:aws:iam::123456789012:role/GitHubActionsRole
          aws-region: ${{ env.AWS_REGION }}

      - name: Deploy
        run: |
          # Secretos se obtienen automáticamente via IAM role
          dotnet publish -c Release
```

## 5. Buenas Prácticas

### 5.1 Separación por Entorno

```bash
# ✅ Secretos separados por entorno
/talma/dev/db/postgres/credentials
/talma/staging/db/postgres/credentials
/talma/prod/db/postgres/credentials
```

### 5.2 Cache de Secretos con TTL

```csharp
public class CachedSecretsProvider
{
    private readonly IMemoryCache _cache;
    private readonly IAmazonSecretsManager _client;
    private readonly TimeSpan _cacheDuration = TimeSpan.FromMinutes(5);

    public async Task<string> GetSecretAsync(string secretName)
    {
        return await _cache.GetOrCreateAsync(secretName, async entry =>
        {
            entry.AbsoluteExpirationRelativeToNow = _cacheDuration;
            var response = await _client.GetSecretValueAsync(new GetSecretValueRequest
            {
                SecretId = secretName
            });
            return response.SecretString;
        });
    }
}
```

### 5.3 Rotación Automática

```bash
# Configurar rotación automática cada 30 días
aws secretsmanager rotate-secret \
    --secret-id /talma/prod/db/postgres/credentials \
    --rotation-lambda-arn arn:aws:lambda:us-east-1:123456789012:function:SecretsManagerRotation \
    --rotation-rules AutomaticallyAfterDays=30
```

## 6. Antipatrones

### 6.1 ❌ Secretos Hardcodeados

**Problema**:
```csharp
// ❌ NUNCA hacer esto
public class DatabaseConfig
{
    public string ConnectionString = "Server=db.talma.com;User=admin;Password=P@ssw0rd123";
}
```

**Solución**:
```csharp
// ✅ Obtener de Secrets Manager
public class DatabaseConfig
{
    private readonly ISecretsProvider _secrets;

    public async Task<string> GetConnectionStringAsync()
    {
        var secret = await _secrets.GetSecretAsync("/talma/prod/db/postgres/credentials");
        var credentials = JsonSerializer.Deserialize<DbCredentials>(secret);
        return $"Server={credentials.Host};User={credentials.Username};Password={credentials.Password}";
    }
}
```

### 6.2 ❌ Secretos en Variables de Entorno Commiteadas

**Problema**:
```bash
# ❌ .env versionado en Git
DB_PASSWORD=mysecretpassword123
API_KEY=sk_live_abc123def456
```

**Solución**:
```bash
# ✅ .env solo con referencias, valores en Secrets Manager
SECRET_NAME=/talma/prod/db/postgres/credentials
AWS_REGION=us-east-1

# .gitignore
.env.local
.env.*.local
```

### 6.3 ❌ Sin Rotación de Secretos

**Problema**:
```bash
# ❌ Secreto creado hace 2 años sin rotación
aws secretsmanager create-secret --name db-password --secret-string "OldPassword2022"
# Nunca se actualizó
```

**Solución**:
```bash
# ✅ Configurar rotación automática
aws secretsmanager rotate-secret \
    --secret-id db-password \
    --rotation-lambda-arn arn:aws:lambda:us-east-1:123:function:RotateSecret \
    --rotation-rules AutomaticallyAfterDays=90
```

### 6.4 ❌ Permisos IAM Demasiado Amplios

**Problema**:
```json
{
  "Effect": "Allow",
  "Action": "secretsmanager:*",
  "Resource": "*"
}
```

**Solución**:
```json
{
  "Effect": "Allow",
  "Action": [
    "secretsmanager:GetSecretValue"
  ],
  "Resource": "arn:aws:secretsmanager:us-east-1:123456789012:secret:/talma/prod/api/*"
}
```

## 7. Validación y Testing

### 7.1 Tests de Recuperación de Secretos

```csharp
public class SecretsProviderTests
{
    [Fact]
    public async Task GetSecret_ValidSecretName_ReturnsSecret()
    {
        // Arrange
        var mockClient = new Mock<IAmazonSecretsManager>();
        mockClient.Setup(c => c.GetSecretValueAsync(It.IsAny<GetSecretValueRequest>(), default))
            .ReturnsAsync(new GetSecretValueResponse
            {
                SecretString = "{\"password\":\"test123\"}"
            });

        var provider = new SecretsProvider(mockClient.Object);

        // Act
        var secret = await provider.GetSecretAsync("/test/secret");

        // Assert
        secret.Should().Contain("password");
    }
}
```

### 7.2 Validación de Rotación

```bash
# Script para verificar rotación automática configurada
#!/bin/bash
SECRETS=$(aws secretsmanager list-secrets --query 'SecretList[?RotationEnabled==`false`].Name' --output text)

if [ -n "$SECRETS" ]; then
    echo "⚠️ Secretos sin rotación automática:"
    echo "$SECRETS"
    exit 1
else
    echo "✅ Todos los secretos tienen rotación configurada"
fi
```

## 8. Referencias

### Lineamientos Relacionados
- [Seguridad desde el Diseño](/docs/fundamentos-corporativos/lineamientos/seguridad/seguridad-desde-el-diseno)
- [Protección de Datos](/docs/fundamentos-corporativos/lineamientos/seguridad/proteccion-de-datos)

### Estándares Relacionados
- [Infraestructura como Código](./02-infraestructura-como-codigo.md)
- [Seguridad de APIs](../apis/02-seguridad-apis.md)

### ADRs Relacionados
- [ADR-003: Gestión de Secretos](/docs/decisiones-de-arquitectura/adr-003-gestion-secretos)
- [ADR-006: Infraestructura IaC](/docs/decisiones-de-arquitectura/adr-006-infraestructura-iac)

### Recursos Externos
- [AWS Secrets Manager Best Practices](https://docs.aws.amazon.com/secretsmanager/latest/userguide/best-practices.html)
- [OWASP Secrets Management](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)

## 9. Changelog

| Versión | Fecha | Autor | Cambios |
|---------|-------|-------|---------|  
| 1.0 | 2025-08-08 | Equipo de Arquitectura | Versión inicial con template de 9 secciones |
