---
id: secrets-management
sidebar_position: 3
title: Gestión de Secretos
description: Estándar técnico obligatorio para gestión segura de secretos con AWS Secrets Manager, rotación automática, least privilege y auditoría
---

# Estándar Técnico — Gestión de Secretos

---

## 1. Propósito
Garantizar cero leaks de secretos y compliance mediante AWS Secrets Manager con rotación automática (30-90 días), never hardcode, least privilege IAM, encryption AES-256 y auditoría CloudTrail completa.

---

## 2. Alcance

**Aplica a:**
- Credenciales de bases de datos (PostgreSQL, Redis)
- API keys de servicios externos (Stripe, SendGrid)
- OAuth tokens, JWT signing keys, certificados SSL/TLS privados
- Claves de encriptación, secretos en dev/staging/production

**No aplica a:**
- Configuraciones públicas (URLs endpoints públicos)
- Feature flags (usar LaunchDarkly)
- Valores no sensibles (timeouts, limits)
- Certificados públicos

---

## 3. Tecnologías Aprobadas

| Componente | Tecnología | Versión mínima | Observaciones |
|-----------|------------|----------------|---------------|
| **Secrets Store** | AWS Secrets Manager | - | Rotación automática, integración AWS |
| **Encryption** | AWS KMS (AES-256) | - | Encryption at rest managed |
| **SDK .NET** | AWSSDK.SecretsManager | 3.7+ | Cliente oficial AWS |
| **SDK Node.js** | @aws-sdk/client-secrets-manager | 3.0+ | Cliente oficial AWS v3 |
| **Rotation** | AWS Lambda + RDS rotation | - | Rotación sin downtime |
| **Auditoría** | AWS CloudTrail | - | Log de todos los accesos |

> El uso de tecnologías no listadas requiere aprobación de Arquitectura.

---

## 4. Requisitos Obligatorios 🔴

- [ ] NUNCA hardcodear secretos en código fuente, env vars o logs
- [ ] Naming convention: `{env}/{service}/{type}/{name}`
- [ ] Rotación automática configurada: DB=30d, API keys=90d, Certificates=1y
- [ ] Encryption AES-256 en reposo (AWS KMS)
- [ ] TLS 1.3 en tránsito
- [ ] IAM policies granulares por servicio (least privilege)
- [ ] CloudTrail habilitado para auditoría de accesos
- [ ] Secretos separados por entorno (dev/staging/prod)
- [ ] Tags obligatorios: Environment, Service, SecretType
- [ ] SDK oficial AWS (NO hardcode en config files)
- [ ] Rotación Lambda sin downtime para RDS
- [ ] Secrets versionados (SecretVersionId)

---

## 5. Prohibiciones

- ❌ Secretos en código fuente (.env, appsettings.json versionados)
- ❌ Secretos en logs (enmascarar passwords/tokens)
- ❌ Secretos en variables de entorno del sistema
- ❌ Secrets en Terraform state (usar data source)
- ❌ Secretos compartidos entre entornos
- ❌ Rotación manual (automatizar con Lambda)

---

## 6. Configuración Mínima

### .NET
```csharp
using Amazon.SecretsManager;
using Amazon.SecretsManager.Model;

public class SecretsService
{
    private readonly IAmazonSecretsManager _client;
    
    public async Task<string> GetSecretAsync(string secretName)
    {
        var request = new GetSecretValueRequest { SecretId = secretName };
        var response = await _client.GetSecretValueAsync(request);
        return response.SecretString;
    }
}

// Configuración en Program.cs
var dbSecret = await secretsService.GetSecretAsync("prod/users-api/database/connection");
var connectionString = JsonSerializer.Deserialize<DbSecret>(dbSecret);
```

### Node.js
```typescript
import { SecretsManagerClient, GetSecretValueCommand } from '@aws-sdk/client-secrets-manager';

const client = new SecretsManagerClient({ region: 'us-east-1' });

async function getSecret(secretName: string): Promise<string> {
  const command = new GetSecretValueCommand({ SecretId: secretName });
  const response = await client.send(command);
  return response.SecretString!;
}

// Uso
const dbSecret = JSON.parse(await getSecret('prod/orders-api/database/connection'));
const connectionString = `postgres://${dbSecret.username}:${dbSecret.password}@${dbSecret.host}:${dbSecret.port}/${dbSecret.database}`;
```

---

## 7. Validación

```bash
# Crear secreto con naming convention
aws secretsmanager create-secret \
  --name prod/users-api/database/password \
  --secret-string "MySecurePassword123!" \
  --tags Key=Environment,Value=production Key=Service,Value=users-api

# Verificar rotación configurada
aws secretsmanager describe-secret --secret-id prod/users-api/database/password | jq '.RotationEnabled'

# Verificar encryption KMS
aws secretsmanager describe-secret --secret-id prod/users-api/database/password | jq '.KmsKeyId'

# Auditar accesos (CloudTrail)
aws cloudtrail lookup-events --lookup-attributes AttributeKey=ResourceName,AttributeValue=prod/users-api/database/password

# Verificar NO hay secretos en código
git secrets --scan
grep -r "password" --exclude-dir=node_modules --exclude-dir=.git | grep -v "Secrets Manager"
```

**Métricas de cumplimiento:**

| Métrica | Target | Verificación |
|---------|--------|--------------|  
| Secretos en código fuente | 0 | `git secrets --scan` |
| Rotación habilitada | 100% | `describe-secret \| jq .RotationEnabled` |
| Encryption KMS | 100% | `describe-secret \| jq .KmsKeyId` |
| CloudTrail habilitado | 100% | Verificar logs en CloudWatch |

Incumplimientos deben corregirse o documentarse mediante excepción aprobada.

---

## 8. Referencias

- [ADR-003: Gestión de Secretos](../../../decisiones-de-arquitectura/adr-003-gestion-secretos.md)
- [Infraestructura como Código](./02-infraestructura-como-codigo.md)
- [AWS Secrets Manager Best Practices](https://docs.aws.amazon.com/secretsmanager/latest/userguide/best-practices.html)
- [Rotating AWS Secrets](https://docs.aws.amazon.com/secretsmanager/latest/userguide/rotating-secrets.html)
