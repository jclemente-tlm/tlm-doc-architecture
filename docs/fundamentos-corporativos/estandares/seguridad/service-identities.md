---
id: service-identities
sidebar_position: 18
title: Identidades de Servicios
description: Estándar para identidades de servicios con AWS IAM Roles for ECS, Keycloak service accounts y workload identity sin credentials hardcodeados
---

# Estándar Técnico — Identidades de Servicios

---

## 1. Propósito

Implementar identidades de servicios (service-to-service authentication) usando AWS IAM Roles for ECS Tasks, Keycloak service accounts con client_credentials grant y workload identity, eliminando credentials hardcodeados.

---

## 2. Alcance

**Aplica a:**

- Servicios backend (.NET APIs)
- Jobs/Workers
- Comunicación service-to-service
- Acceso a AWS resources (S3, Secrets Manager, RDS)
- Acceso a APIs internas

**No aplica a:**

- Usuarios humanos (usar SSO)

---

## 3. Tecnologías Aprobadas

| Componente           | Tecnología          | Versión mínima | Observaciones             |
| -------------------- | ------------------- | -------------- | ------------------------- |
| **AWS Identity**     | IAM Roles for ECS   | -              | Workload identity         |
| **Service Accounts** | Keycloak            | 23.0+          | OAuth2 client_credentials |
| **Secrets**          | AWS Secrets Manager | -              | NO env vars               |
| **SDK**              | AWS SDK for .NET    | 3.7+           | AssumeRole                |
| **HTTP Client**      | .NET HttpClient     | -              | Bearer token              |

> El uso de tecnologías no listadas requiere aprobación de Arquitectura.

---

## 4. Requisitos Obligatorios 🔴

### Service Identity

- [ ] **AWS IAM Role**: Por cada servicio ECS
- [ ] **Keycloak Service Account**: Para APIs internas
- [ ] **NO hardcoded credentials**: Ni en código ni en env vars
- [ ] **NO long-lived tokens**: Solo short-lived (15min)

### Least Privilege

- [ ] **Minimal permissions**: Solo lo necesario
- [ ] **Resource-based policies**: Limitar a recursos específicos
- [ ] **NO wildcard**: Evitar `*` en policies

### Rotation

- [ ] **Auto-rotation**: Secrets rotan automáticamente
- [ ] **Token refresh**: Refresh tokens antes de expiry

### Auditing

- [ ] **CloudTrail**: Log todas las AssumeRole
- [ ] **Token usage**: Monitorear service account tokens

---

## 5. AWS IAM Roles for ECS Tasks

### Terraform - Task Role

```hcl
# terraform/iam.tf

# IAM Role para Payment Service
resource "aws_iam_role" "payment_service_task" {
  name = "${var.environment}-payment-service-task-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = {
        Service = "ecs-tasks.amazonaws.com"
      }
      Action = "sts:AssumeRole"
    }]
  })

  tags = {
    Service     = "payment-service"
    Environment = var.environment
  }
}

# Policy: Acceso a Secrets Manager (solo secrets de payment service)
resource "aws_iam_role_policy" "payment_secrets" {
  role = aws_iam_role.payment_service_task.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue",
          "secretsmanager:DescribeSecret"
        ]
        Resource = [
          "arn:aws:secretsmanager:${var.aws_region}:${var.aws_account_id}:secret:payment-service/*"
        ]
      }
    ]
  })
}

# Policy: Acceso a S3 (solo bucket de payments)
resource "aws_iam_role_policy" "payment_s3" {
  role = aws_iam_role.payment_service_task.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject"
        ]
        Resource = [
          "arn:aws:s3:::talma-payments-${var.environment}/*"
        ]
      }
    ]
  })
}

# ECS Task Definition con Task Role
resource "aws_ecs_task_definition" "payment_service" {
  family                   = "payment-service"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = "512"
  memory                   = "1024"

  # Task Role: Permisos de la aplicación
  task_role_arn = aws_iam_role.payment_service_task.arn

  # Execution Role: Permisos de ECS para pull image, logs, etc.
  execution_role_arn = aws_iam_role.ecs_execution_role.arn

  container_definitions = jsonencode([{
    name  = "payment-api"
    image = "${var.ecr_repository}/payment-api:${var.image_tag}"
    # ...
  }])
}
```

---

## 6. .NET - AWS SDK con IAM Role

### Acceso a Secrets Manager (Sin Credentials)

```csharp
// Services/SecretsService.cs
using Amazon.SecretsManager;
using Amazon.SecretsManager.Model;

public class SecretsService
{
    private readonly IAmazonSecretsManager _secretsManager;

    public SecretsService()
    {
        // ✅ SDK usa automáticamente IAM Role del ECS Task
        // NO requiere access key / secret key
        _secretsManager = new AmazonSecretsManagerClient();
    }

    public async Task<string> GetSecretAsync(string secretName)
    {
        var request = new GetSecretValueRequest
        {
            SecretId = secretName
        };

        var response = await _secretsManager.GetSecretValueAsync(request);
        return response.SecretString;
    }
}

// Program.cs
builder.Services.AddSingleton<SecretsService>();

// Uso
var dbPassword = await secretsService.GetSecretAsync("payment-service/db-password");
```

### Acceso a S3 (Sin Credentials)

```csharp
// Services/S3Service.cs
using Amazon.S3;
using Amazon.S3.Model;

public class S3Service
{
    private readonly IAmazonS3 _s3Client;
    private readonly string _bucketName;

    public S3Service(IConfiguration configuration)
    {
        // ✅ SDK usa automáticamente IAM Role del ECS Task
        _s3Client = new AmazonS3Client();
        _bucketName = configuration["AWS:S3:BucketName"];
    }

    public async Task<string> UploadFileAsync(string key, Stream fileStream)
    {
        var request = new PutObjectRequest
        {
            BucketName = _bucketName,
            Key = key,
            InputStream = fileStream,
            ServerSideEncryptionMethod = ServerSideEncryptionMethod.AWSKMS
        };

        var response = await _s3Client.PutObjectAsync(request);
        return $"s3://{_bucketName}/{key}";
    }
}
```

---

## 7. Keycloak - Service Accounts

### Crear Service Account

```bash
# Keycloak Admin CLI
kcadm.sh create clients -r talma-internal \
  -s clientId=payment-service \
  -s name="Payment Service" \
  -s serviceAccountsEnabled=true \
  -s directAccessGrantsEnabled=false \
  -s standardFlowEnabled=false \
  -s publicClient=false

# Obtener client secret
kcadm.sh get clients/{client-id}/client-secret -r talma-internal
# Output: {"value": "abc123-secret-xyz"}
```

### Configurar Roles

```bash
# Crear role para service account
kcadm.sh create roles -r talma-internal \
  -s name=payment-service-role \
  -s description="Payment service permissions"

# Asignar role a service account
kcadm.sh add-roles -r talma-internal \
  --uusername service-account-payment-service \
  --rolename payment-service-role
```

---

## 8. .NET - Obtener Token Service Account

### Service Account Token Service

```csharp
// Services/ServiceAccountTokenService.cs
public class ServiceAccountTokenService
{
    private readonly IHttpClientFactory _httpClientFactory;
    private readonly IConfiguration _configuration;
    private string? _cachedToken;
    private DateTime _tokenExpiry;

    public async Task<string> GetTokenAsync()
    {
        // Reusar token si no ha expirado
        if (!string.IsNullOrEmpty(_cachedToken) && DateTime.UtcNow < _tokenExpiry)
        {
            return _cachedToken;
        }

        // Obtener nuevo token
        var client = _httpClientFactory.CreateClient();
        var tokenEndpoint = $"{_configuration["Keycloak:Authority"]}/protocol/openid-connect/token";

        // Client credentials desde AWS Secrets Manager (NO env vars)
        var secretsService = new SecretsService();
        var clientSecret = await secretsService.GetSecretAsync("payment-service/keycloak-client-secret");

        var request = new HttpRequestMessage(HttpMethod.Post, tokenEndpoint);
        request.Content = new FormUrlEncodedContent(new Dictionary<string, string>
        {
            ["grant_type"] = "client_credentials",
            ["client_id"] = _configuration["Keycloak:ClientId"],
            ["client_secret"] = clientSecret,
            ["scope"] = "openid"
        });

        var response = await client.SendAsync(request);
        response.EnsureSuccessStatusCode();

        var tokenResponse = await response.Content.ReadFromJsonAsync<TokenResponse>();

        _cachedToken = tokenResponse.AccessToken;
        _tokenExpiry = DateTime.UtcNow.AddSeconds(tokenResponse.ExpiresIn - 60); // 1min buffer

        return _cachedToken;
    }
}

public record TokenResponse(
    [property: JsonPropertyName("access_token")] string AccessToken,
    [property: JsonPropertyName("expires_in")] int ExpiresIn,
    [property: JsonPropertyName("token_type")] string TokenType
);
```

### Usar Token en HTTP Requests

```csharp
// Services/CustomerApiClient.cs
public class CustomerApiClient
{
    private readonly IHttpClientFactory _httpClientFactory;
    private readonly ServiceAccountTokenService _tokenService;

    public async Task<Customer> GetCustomerAsync(Guid customerId)
    {
        var client = _httpClientFactory.CreateClient("CustomerAPI");

        // Obtener token service account
        var token = await _tokenService.GetTokenAsync();

        var request = new HttpRequestMessage(HttpMethod.Get, $"/api/customers/{customerId}");
        request.Headers.Authorization = new AuthenticationHeaderValue("Bearer", token);

        var response = await client.SendAsync(request);
        response.EnsureSuccessStatusCode();

        return await response.Content.ReadFromJsonAsync<Customer>();
    }
}
```

---

## 9. Secrets Storage - NO Hardcoded

### AWS Secrets Manager

```bash
# Crear secret para service account
aws secretsmanager create-secret \
  --name payment-service/keycloak-client-secret \
  --description "Keycloak client secret for payment service" \
  --secret-string "abc123-secret-xyz" \
  --tags Key=Service,Value=payment-service Key=Environment,Value=production

# Habilitar auto-rotation (30 días)
aws secretsmanager rotate-secret \
  --secret-id payment-service/keycloak-client-secret \
  --rotation-lambda-arn arn:aws:lambda:us-east-1:123456789012:function:SecretsManagerRotation \
  --rotation-rules AutomaticallyAfterDays=30
```

### ❌ NUNCA Hacer Esto

```csharp
// ❌ MAL: Hardcoded credentials
public class BadExample
{
    private const string ClientSecret = "abc123-secret-xyz";  // ❌ NO!

    // ❌ MAL: Credentials en appsettings.json
    // {
    //   "Keycloak": {
    //     "ClientSecret": "abc123-secret-xyz"  // ❌ NO!
    //   }
    // }

    // ❌ MAL: Credentials en environment variables
    // Environment.GetEnvironmentVariable("CLIENT_SECRET")  // ❌ NO!
}
```

---

## 10. Monitoring - Service Identity Usage

### CloudTrail - AssumeRole Events

```json
{
  "eventName": "AssumeRole",
  "eventSource": "sts.amazonaws.com",
  "userIdentity": {
    "type": "AssumedRole",
    "principalId": "AROAI...:payment-service-task",
    "arn": "arn:aws:sts::123456789012:assumed-role/production-payment-service-task-role/payment-service-task"
  },
  "requestParameters": {
    "roleArn": "arn:aws:iam::123456789012:role/production-payment-service-task-role"
  }
}
```

### Prometheus - Token Metrics

```promql
# Service account token refreshes
sum(rate(keycloak_token_requests_total{grant_type="client_credentials"}[5m])) by (client_id)

# Token refresh failures
sum(rate(keycloak_token_requests_failed_total[5m])) by (client_id, error)
```

---

## 11. Validación de Cumplimiento

```bash
# Verificar IAM Role existe
aws iam get-role --role-name production-payment-service-task-role

# Verificar policies attached
aws iam list-attached-role-policies --role-name production-payment-service-task-role

# Test: Obtener token service account
curl -X POST https://auth.talma.com/realms/talma-internal/protocol/openid-connect/token \
  -d "grant_type=client_credentials" \
  -d "client_id=payment-service" \
  -d "client_secret=$(aws secretsmanager get-secret-value --secret-id payment-service/keycloak-client-secret --query SecretString --output text)"

# Verificar CloudTrail logs de AssumeRole
aws cloudtrail lookup-events \
  --lookup-attributes AttributeKey=EventName,AttributeValue=AssumeRole \
  --max-results 10
```

---

## 12. Referencias

**AWS:**

- [IAM Roles for ECS Tasks](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/task-iam-roles.html)
- [AWS Secrets Manager](https://docs.aws.amazon.com/secretsmanager/latest/userguide/intro.html)

**Keycloak:**

- [Service Accounts](https://www.keycloak.org/docs/latest/server_admin/#_service_accounts)
- [Client Credentials Grant](https://oauth.net/2/grant-types/client-credentials/)
