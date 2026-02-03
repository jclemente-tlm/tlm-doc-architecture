---
id: data-encryption
sidebar_position: 8
title: Cifrado de Datos (OWASP ASVS V6/V9)
description: Estándar para cifrado de datos sensibles en tránsito y reposo según OWASP ASVS V6 (Cryptography) y V9 (Data Protection), con algoritmos aprobados.
---

# Estándar Técnico — Cifrado de Datos (OWASP ASVS V6/V9)

---

## 1. Propósito

Garantizar **confidencialidad** e **integridad** de datos sensibles mediante cifrado en **tránsito** (TLS 1.2+) y **reposo** (AES-256), cumpliendo **OWASP ASVS V6 (Cryptography)** y **V9 (Data Protection)**.

---

## 2. Alcance

**Aplica a:**

- Datos personales (PII): nombres, emails, documentos identidad
- Datos financieros: tarjetas, cuentas bancarias, transacciones
- Credenciales: passwords, API keys, tokens, secrets
- Datos de salud (PHI)
- Backups de bases de datos
- Comunicaciones API (HTTP, gRPC, message queues)

**No aplica a:**

- Logs públicos (sin PII)
- Datos ya públicos (catálogos, precios base)
- Metadata no sensible (IDs, timestamps)

---

## 3. Algoritmos y Protocolos Aprobados

### 3.1 Cifrado en Tránsito

| Protocolo | Versión Mínima      | Cipher Suites Aprobados                 | Observaciones         |
| --------- | ------------------- | --------------------------------------- | --------------------- |
| **TLS**   | 1.2+ (preferir 1.3) | `TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384` | HTTP, gRPC            |
| **TLS**   | 1.2+                | `TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256` | Compatibilidad legacy |
| **SSH**   | 2.0                 | `aes256-gcm@openssh.com`                | Acceso bastion hosts  |

**Prohibido:**

- ❌ TLS 1.0 / 1.1 (vulnerables a BEAST, POODLE)
- ❌ SSL 3.0 y versiones anteriores
- ❌ Cipher suites con RC4, DES, 3DES
- ❌ HTTP sin TLS (permitido SOLO localhost desarrollo)

### 3.2 Cifrado en Reposo

| Componente              | Algoritmo   | Key Management   | Observaciones                  |
| ----------------------- | ----------- | ---------------- | ------------------------------ |
| **RDS (PostgreSQL)**    | AES-256     | AWS KMS          | Encryption at rest obligatorio |
| **S3**                  | AES-256-GCM | AWS KMS + SSE-S3 | Server-side encryption         |
| **DynamoDB**            | AES-256     | AWS managed keys | Encryption at rest default     |
| **EBS Volumes**         | AES-256-XTS | AWS KMS          | Para datos sensibles           |
| **ElastiCache (Redis)** | AES-256     | AWS managed      | At-rest + in-transit           |
| **Secrets Manager**     | AES-256-GCM | AWS KMS          | Rotación automática            |
| **Backups**             | AES-256     | AWS KMS          | RDS snapshots, S3 glacier      |

---

## 4. Requisitos Obligatorios 🔴

### 4.1 Cifrado en Tránsito

- [ ] **TLS 1.2+ obligatorio** para toda comunicación HTTPS
- [ ] Certificados SSL válidos (NO self-signed en producción)
- [ ] Renovación automática certificados (AWS Certificate Manager)
- [ ] HSTS header: `Strict-Transport-Security: max-age=31536000; includeSubDomains`
- [ ] HTTP → HTTPS redirect en ALB/CloudFront
- [ ] APIs internas (dentro VPC): TLS opcional PERO mTLS recomendado
- [ ] gRPC: TLS obligatorio con client/server certificates
- [ ] Message queues (Apache Kafka): encryption in transit (TLS 1.3)

### 4.2 Cifrado en Reposo

- [ ] **RDS encryption at rest** habilitado (AES-256 + KMS)
- [ ] **S3 default encryption** en todos los buckets sensibles
- [ ] **EBS encryption** para volúmenes con datos PII/PHI
- [ ] **ElastiCache encryption** at-rest + in-transit
- [ ] **Secrets Manager** para credenciales (NO environment variables en texto claro)
- [ ] Backups cifrados (RDS snapshots, S3 glacier)
- [ ] Application-level encryption para campos ultra-sensibles (ej: SSN, tarjetas)

### 4.3 Key Management

- [ ] **AWS KMS** para gestión centralizada de claves
- [ ] Customer Managed Keys (CMK) para datos críticos
- [ ] Key rotation automática cada 365 días
- [ ] Separación de claves por entorno (dev, staging, prod)
- [ ] Políticas IAM restrictivas para acceso a claves
- [ ] Audit trail de uso de claves (CloudTrail)
- [ ] NO hardcodear claves en código o configs

### 4.4 Application-Level Encryption

Para campos ultra-sensibles (SSN, números tarjeta):

```csharp
// Ejemplo: Cifrado campo-específico con AWS KMS
public class EncryptionService
{
    private readonly IAmazonKeyManagementService _kms;
    private readonly string _keyId = "arn:aws:kms:us-east-1:123456789012:key/abc123";

    public async Task<string> EncryptAsync(string plaintext)
    {
        var request = new EncryptRequest
        {
            KeyId = _keyId,
            Plaintext = new MemoryStream(Encoding.UTF8.GetBytes(plaintext))
        };
        var response = await _kms.EncryptAsync(request);
        return Convert.ToBase64String(response.CiphertextBlob.ToArray());
    }

    public async Task<string> DecryptAsync(string ciphertext)
    {
        var request = new DecryptRequest
        {
            CiphertextBlob = new MemoryStream(Convert.FromBase64String(ciphertext))
        };
        var response = await _kms.DecryptAsync(request);
        return Encoding.UTF8.GetString(response.Plaintext.ToArray());
    }
}
```

---

## 5. Configuración Mínima

### 5.1 ALB/CloudFront — Enforce HTTPS

```yaml
# CloudFormation: ALB Listener
Type: AWS::ElasticLoadBalancingV2::Listener
Properties:
  Protocol: HTTPS
  Port: 443
  SslPolicy: ELBSecurityPolicy-TLS-1-2-2017-01
  Certificates:
    - CertificateArn: !Ref SSLCertificate
  DefaultActions:
    - Type: forward
      TargetGroupArn: !Ref TargetGroup

# HTTP Redirect to HTTPS
Type: AWS::ElasticLoadBalancingV2::Listener
Properties:
  Protocol: HTTP
  Port: 80
  DefaultActions:
    - Type: redirect
      RedirectConfig:
        Protocol: HTTPS
        Port: 443
        StatusCode: HTTP_301
```

### 5.2 RDS — Encryption at Rest

```bash
aws rds create-db-instance \
  --db-instance-identifier prod-db \
  --engine postgres \
  --storage-encrypted \
  --kms-key-id arn:aws:kms:us-east-1:123456789012:key/abc123 \
  --db-instance-class db.r6g.large \
  --allocated-storage 100
```

### 5.3 S3 — Default Encryption

```json
{
  "Rules": [
    {
      "ApplyServerSideEncryptionByDefault": {
        "SSEAlgorithm": "aws:kms",
        "KMSMasterKeyID": "arn:aws:kms:us-east-1:123456789012:key/abc123"
      },
      "BucketKeyEnabled": true
    }
  ]
}
```

### 5.4 .NET API — Enforce HTTPS

```csharp
// Program.cs
var builder = WebApplication.CreateBuilder(args);

// Enforce HTTPS redirection
builder.Services.AddHttpsRedirection(options =>
{
    options.RedirectStatusCode = StatusCodes.Status308PermanentRedirect;
    options.HttpsPort = 443;
});

// HSTS header
builder.Services.AddHsts(options =>
{
    options.MaxAge = TimeSpan.FromDays(365);
    options.IncludeSubDomains = true;
});

var app = builder.Build();

app.UseHttpsRedirection();
app.UseHsts();
```

---

## 6. Prohibiciones

- ❌ HTTP sin TLS para APIs públicas (permitido SOLO localhost dev)
- ❌ Self-signed certificates en producción
- ❌ TLS 1.0 / 1.1 / SSL 3.0
- ❌ Cipher suites débiles (RC4, DES, 3DES)
- ❌ Passwords en texto claro en BD
- ❌ API keys en environment variables (usar Secrets Manager)
- ❌ Hardcodear claves de cifrado en código
- ❌ RDS sin encryption at rest para datos sensibles
- ❌ S3 buckets públicos con PII/PHI

---

## 7. Validación

**Checklist de cumplimiento:**

- [ ] `nmap --script ssl-enum-ciphers -p 443 api.talma.com` → Solo TLS 1.2+
- [ ] `curl -I https://api.talma.com` → Header `Strict-Transport-Security` presente
- [ ] RDS instances: `aws rds describe-db-instances --query 'DBInstances[*].[DBInstanceIdentifier,StorageEncrypted]'` → todos `true`
- [ ] S3 buckets: verificar default encryption enabled
- [ ] Secrets Manager: NO env vars con `PASSWORD`, `SECRET`, `KEY` en ECS task definitions
- [ ] KMS key rotation: `aws kms get-key-rotation-status` → `KeyRotationEnabled: true`

**Métricas de cumplimiento:**

| Métrica                    | Target           | Verificación               |
| -------------------------- | ---------------- | -------------------------- |
| APIs con TLS 1.2+          | 100%             | SSL Labs scan              |
| RDS instances cifradas     | 100%             | AWS Config rule            |
| S3 buckets con encryption  | 100% (sensibles) | AWS Config rule            |
| Secrets en Secrets Manager | 100%             | Manual audit + git-secrets |
| Key rotation habilitada    | 100%             | KMS audit                  |

Incumplimientos bloquean deployment mediante AWS Config rules.

---

## 8. Referencias

- [OWASP ASVS V6 — Cryptography](https://owasp.org/www-project-application-security-verification-standard/)
- [OWASP ASVS V9 — Data Protection](https://owasp.org/www-project-application-security-verification-standard/)
- [AWS Encryption SDK](https://docs.aws.amazon.com/encryption-sdk/)
- [AWS KMS Best Practices](https://docs.aws.amazon.com/kms/latest/developerguide/best-practices.html)
- [ADR-003: Gestión de Secretos](../../../decisiones-de-arquitectura/adr-003-gestion-secretos.md)
