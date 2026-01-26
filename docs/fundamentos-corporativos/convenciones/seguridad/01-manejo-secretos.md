---
id: manejo-secretos
sidebar_position: 1
title: Manejo de Secretos
description: Convención para gestión segura de secretos y credenciales
---

## 1. Principio

Los secretos (contraseñas, API keys, tokens, certificados) **NUNCA** deben ser committeados en repositorios. Deben gestionarse mediante herramientas especializadas y seguir el principio de mínimo privilegio.

## 2. Reglas

### Regla 1: NUNCA Commitear Secretos

```bash
❌ PROHIBIDO:

# .env
TLM_DB_PASSWORD=MyP@ssw0rd123
TLM_API_KEY=sk_live_1234567890abcdef
TLM_JWT_SECRET=super-secret-key-here

# appsettings.json
{
  "ConnectionStrings": {
    "DefaultConnection": "Server=db;User=admin;Password=Admin123"
  }
}

# hardcoded
const API_KEY = "sk_live_1234567890abcdef";
```

```bash
✅ CORRECTO:

# .env.example (template sin valores reales)
TLM_DB_PASSWORD=<FROM_VAULT>
TLM_API_KEY=<FROM_VAULT>
TLM_JWT_SECRET=<FROM_VAULT>

# appsettings.json (sin secretos)
{
  "ConnectionStrings": {
    "DefaultConnection": "Server=db;User=app_user"
    // Password cargado desde secrets manager
  }
}
```

### Regla 2: .gitignore Obligatorio

Siempre incluir en `.gitignore`:

```bash
# .gitignore

# Environment files
.env
.env.local
.env.*.local

# IDE
.vscode/
.idea/

# Secrets
secrets/
*.pem
*.key
*.crt
*.pfx
*.p12

# Configuration with secrets
appsettings.Development.json
appsettings.Local.json
```

### Regla 3: Variables de Entorno vs Secrets Manager

| Tipo de Dato                  | Método                      | Ejemplo             |
| ----------------------------- | --------------------------- | ------------------- |
| **Configuración NO sensible** | Variables de entorno        | `TLM_APP_PORT=8080` |
| **Secretos**                  | AWS Secrets Manager / Vault | `TLM_DB_PASSWORD`   |
| **Certificados**              | AWS Certificate Manager     | SSL/TLS certs       |
| **API Keys de terceros**      | Secrets Manager             | Stripe, SendGrid    |

### Regla 4: Formato de Secretos en Secrets Manager

Estructura JSON por servicio:

```json
// AWS Secrets Manager: tlm/prod/users-api
{
  "dbPassword": "MySecureP@ssw0rd123",
  "jwtSecret": "ultra-secret-jwt-key-256-bits",
  "stripeApiKey": "sk_live_1234567890abcdef",
  "awsAccessKeyId": "AKIAIOSFODNN7EXAMPLE",
  "awsSecretAccessKey": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
}
```

### Regla 5: Rotación de Secretos

| Tipo de Secreto      | Frecuencia de Rotación | Automatización                             |
| -------------------- | ---------------------- | ------------------------------------------ |
| DB Passwords         | Cada 90 días           | ✅ AWS Secrets Manager auto-rotation       |
| API Keys             | Cada 180 días          | ⚠️ Manual (coordinar con proveedor)        |
| JWT Secrets          | Cada año               | ✅ Automatizado con backward compatibility |
| Certificados SSL     | Antes de expiración    | ✅ AWS Certificate Manager auto-renewal    |
| Service Account Keys | Cada 90 días           | ✅ Terraform + CI/CD                       |

## 3. Implementación por Tecnología

### .NET - AWS Secrets Manager

```csharp
// Program.cs
builder.Configuration.AddSecretsManager(
    region: RegionEndpoint.USEast1,
    configurator: options =>
    {
        options.SecretFilter = secret =>
            secret.Name.StartsWith($"tlm/{builder.Environment.EnvironmentName}/");
        options.PollingInterval = TimeSpan.FromMinutes(5);
    });

// Uso
var connectionString = builder.Configuration["ConnectionStrings:DefaultConnection"];
var jwtSecret = builder.Configuration["JwtSecret"];
```

### TypeScript/Node.js - AWS Secrets Manager

```typescript
import {
  SecretsManagerClient,
  GetSecretValueCommand,
} from "@aws-sdk/client-secrets-manager";

export interface AppSecrets {
  dbPassword: string;
  jwtSecret: string;
  stripeApiKey: string;
}

export async function loadSecrets(): Promise<AppSecrets> {
  const client = new SecretsManagerClient({ region: "us-east-1" });

  const secretName = `tlm/${process.env.NODE_ENV}/users-api`;

  try {
    const response = await client.send(
      new GetSecretValueCommand({ SecretId: secretName }),
    );

    if (!response.SecretString) {
      throw new Error("Secret is empty");
    }

    return JSON.parse(response.SecretString) as AppSecrets;
  } catch (error) {
    console.error("Failed to load secrets:", error);
    throw error;
  }
}

// En main.ts
const secrets = await loadSecrets();

// Inyectar en process.env o config
process.env.DB_PASSWORD = secrets.dbPassword;
process.env.JWT_SECRET = secrets.jwtSecret;
```

### Kubernetes - External Secrets Operator

```yaml
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: users-api-secrets
spec:
  secretStoreRef:
    name: aws-secrets-manager
    kind: SecretStore
  target:
    name: users-api-secrets
    creationPolicy: Owner
  data:
    - secretKey: DB_PASSWORD
      remoteRef:
        key: tlm/prod/users-api
        property: dbPassword
    - secretKey: JWT_SECRET
      remoteRef:
        key: tlm/prod/users-api
        property: jwtSecret
```

### Docker Compose - Secrets

```yaml
version: "3.8"

services:
  api:
    image: users-api:latest
    secrets:
      - db_password
      - jwt_secret
    environment:
      DB_PASSWORD_FILE: /run/secrets/db_password
      JWT_SECRET_FILE: /run/secrets/jwt_secret

secrets:
  db_password:
    file: ./secrets/db_password.txt
  jwt_secret:
    file: ./secrets/jwt_secret.txt
```

## 4. Validación Pre-commit

### Git Hooks

```bash
#!/bin/bash
# .git/hooks/pre-commit

echo "🔍 Scanning for secrets..."

# Detectar patrones sospechosos
if git diff --cached | grep -E "(password|secret|key|token)\s*=\s*['\"]?[A-Za-z0-9]{8,}"; then
  echo "❌ Posible secreto detectado en commit"
  echo "   Usar variables de entorno o secrets manager"
  exit 1
fi

# Detectar archivos que no deberían committearse
if git diff --cached --name-only | grep -E "\.env$|secrets/|\.pem$|\.key$"; then
  echo "❌ Archivos de secretos detectados:"
  git diff --cached --name-only | grep -E "\.env$|secrets/|\.pem$|\.key$"
  exit 1
fi

echo "✅ No se detectaron secretos"
```

### Gitleaks (Automated Secret Scanning)

```yaml
# .gitleaks.toml
title = "Gitleaks Configuration"

[extend]
useDefault = true

[[rules]]
id = "aws-access-key"
description = "AWS Access Key"
regex = '''AKIA[0-9A-Z]{16}'''

[[rules]]
id = "generic-api-key"
description = "Generic API Key"
regex = '''(?i)(api[_-]?key|apikey)['\"]?\s*[:=]\s*['\"0-9a-zA-Z]{16,}'''

[[rules]]
id = "generic-secret"
description = "Generic Secret"
regex = '''(?i)(secret|password|passwd)['\"]?\s*[:=]\s*['\"0-9a-zA-Z]{8,}'''
```

```bash
# Ejecutar gitleaks
gitleaks detect --source . --verbose

# Pre-commit hook
gitleaks protect --staged
```

## 5. Terraform - Gestión de Secrets

```hcl
# Crear secreto en AWS Secrets Manager
resource "aws_secretsmanager_secret" "users_api" {
  name                    = "tlm/${var.environment}/users-api"
  description             = "Secrets for Users API"
  recovery_window_in_days = 7
}

resource "aws_secretsmanager_secret_version" "users_api" {
  secret_id = aws_secretsmanager_secret.users_api.id
  secret_string = jsonencode({
    dbPassword      = random_password.db_password.result
    jwtSecret       = random_password.jwt_secret.result
    stripeApiKey    = var.stripe_api_key  # Desde Terraform variable
  })
}

# Password aleatorio
resource "random_password" "db_password" {
  length  = 32
  special = true
}

# Auto-rotation
resource "aws_secretsmanager_secret_rotation" "users_api_db" {
  secret_id           = aws_secretsmanager_secret.users_api.id
  rotation_lambda_arn = aws_lambda_function.rotate_secret.arn

  rotation_rules {
    automatically_after_days = 90
  }
}
```

## 6. CI/CD - Inyección de Secretos

### GitHub Actions

```yaml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1

      - name: Get secrets from AWS
        run: |
          aws secretsmanager get-secret-value \
            --secret-id tlm/prod/users-api \
            --query SecretString \
            --output text > secrets.json

      - name: Deploy
        run: ./deploy.sh
```

### GitLab CI

```yaml
deploy:
  stage: deploy
  image: amazon/aws-cli
  script:
    - aws secretsmanager get-secret-value --secret-id tlm/prod/users-api
    - ./deploy.sh
  only:
    - main
  secrets:
    AWS_ACCESS_KEY_ID:
      vault: production/aws/access_key_id
    AWS_SECRET_ACCESS_KEY:
      vault: production/aws/secret_access_key
```

## 7. Auditoría y Compliance

### CloudTrail - Monitoreo de Acceso a Secretos

```json
{
  "eventName": "GetSecretValue",
  "eventSource": "secretsmanager.amazonaws.com",
  "userIdentity": {
    "principalId": "AIDAIOSFODNN7EXAMPLE",
    "arn": "arn:aws:iam::123456789012:user/developer"
  },
  "requestParameters": {
    "secretId": "tlm/prod/users-api"
  },
  "responseElements": null,
  "eventTime": "2024-01-15T10:30:00Z"
}
```

### Alertas de Seguridad

```yaml
# CloudWatch Alarm
alarmName: UnauthorizedSecretAccess
metricName: SecretAccessDenied
threshold: 1
evaluationPeriods: 1
actions:
  - arn:aws:sns:us-east-1:123456789012:security-alerts
```

## 📖 Referencias

### Estándares relacionados

- [Gestión de Configuraciones](/docs/fundamentos-corporativos/estandares/infraestructura/configuraciones)
- [Seguridad desde el Diseño](/docs/fundamentos-corporativos/lineamientos/seguridad-desde-diseño)

### Convenciones relacionadas

- [Variables de Entorno](/docs/fundamentos-corporativos/convenciones/infraestructura/variables-entorno)

### Recursos externos

- [AWS Secrets Manager Best Practices](https://docs.aws.amazon.com/secretsmanager/latest/userguide/best-practices.html)
- [OWASP Secrets Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)
- [Gitleaks](https://github.com/gitleaks/gitleaks)

---

**Última revisión**: 26 de enero 2026
**Responsable**: Equipo de Arquitectura
