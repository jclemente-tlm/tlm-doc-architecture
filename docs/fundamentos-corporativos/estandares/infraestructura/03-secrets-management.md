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

## 8. Rotación de Secretos

### Lambda de rotación (ejemplo)

```python
import boto3
import json

def lambda_handler(event, context):
    service_client = boto3.client('secretsmanager')

    # Obtener token de rotación
    token = event['Token']
    secret_arn = event['SecretId']
    step = event['Step']

    if step == "createSecret":
        # Generar nueva contraseña
        new_password = generate_password()

        # Guardar como AWSPENDING
        service_client.put_secret_value(
            SecretId=secret_arn,
            ClientRequestToken=token,
            SecretString=json.dumps({"password": new_password}),
            VersionStages=['AWSPENDING']
        )

    elif step == "setSecret":
        # Actualizar contraseña en la base de datos
        update_database_password(new_password)

    elif step == "testSecret":
        # Probar nueva contraseña
        test_database_connection(new_password)

    elif step == "finishSecret":
        # Marcar como AWSCURRENT
        service_client.update_secret_version_stage(
            SecretId=secret_arn,
            VersionStage='AWSCURRENT',
            MoveToVersionId=token
        )
```

## 9. Checklist de Secrets Management

- [ ] **No hardcoding**: Sin secretos en código, configuración o variables de entorno commiteadas
- [ ] **Secrets Manager configurado**: AWS Secrets Manager o Azure Key Vault en uso
- [ ] **Naming convention**: Nomenclatura consistente para secretos
- [ ] **Separation por entorno**: Secretos diferentes para dev/staging/prod
- [ ] **IAM/RBAC**: Permisos de acceso configurados con least privilege
- [ ] **Rotación automática**: Secretos críticos rotan automáticamente
- [ ] **Auditoría**: Logs de acceso a secretos habilitados
- [ ] **Encriptación**: KMS keys configuradas apropiadamente
- [ ] **Cache**: Implementado con TTL corto para reducir llamadas
- [ ] **Terraform**: Secretos gestionados como IaC (sin valores hardcodeados)

## 📖 Referencias

### Lineamientos relacionados

- [Protección de Datos](/docs/fundamentos-corporativos/lineamientos/seguridad/proteccion-de-datos)
- [Infraestructura como Código](/docs/fundamentos-corporativos/lineamientos/operabilidad/infraestructura-como-codigo)

### ADRs relacionados

- [ADR-003: Gestión de Secretos](/docs/decisiones-de-arquitectura/adr-003-gestion-secretos)

### Recursos externos

- [AWS Secrets Manager Best Practices](https://docs.aws.amazon.com/secretsmanager/latest/userguide/best-practices.html)
- [Azure Key Vault Best Practices](https://docs.microsoft.com/en-us/azure/key-vault/general/best-practices)
- [OWASP Secrets Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)
