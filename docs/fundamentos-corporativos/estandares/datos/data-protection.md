# Estándar Técnico — Protección de Datos

## 1. Propósito

Definir controles obligatorios para clasificación, cifrado, enmascaramiento, minimización y retención/eliminación de datos sensibles y personales, alineados a GDPR, PCI DSS y OWASP ASVS.

## 2. Alcance

**Aplica a:**

- Todos los datos en sistemas corporativos
- Bases de datos, archivos, backups, logs, APIs
- Datos en tránsito y en reposo

**No aplica a:**

- Datos públicos ya publicados oficialmente
- Metadatos de sistema no sensibles

## 3. Niveles de Clasificación

| Nivel           | Descripción                           | Ejemplos                          | Impacto |
| --------------- | ------------------------------------- | --------------------------------- | ------- |
| 🌐 Public       | Información pública sin restricciones | Precios, comunicados, marketing   | Bajo    |
| 🔒 Internal     | Solo empleados, no público            | Políticas, organigramas           | Medio   |
| 🔐 Confidencial | Sensible, negocio, clientes           | Contratos, datos clientes         | Alto    |
| 🚨 Restringido  | Altamente sensible, regulado          | PII, PCI DSS, salud, credenciales | Crítico |

## 4. Tecnologías Aprobadas

| Componente | Tecnología        | Versión mínima | Observaciones               |
| ---------- | ----------------- | -------------- | --------------------------- |
| Encryption | AWS KMS           | -              | At-rest encryption          |
| TLS        | TLS 1.3           | -              | In-transit encryption       |
| Masking    | Serilog, Regex    | 3.1+           | Enrichers, patterns PII/PCI |
| Database   | PostgreSQL        | 14+            | Column encryption, masking  |
| IAM        | AWS IAM, Keycloak | -              | RBAC granular               |
| DLP        | Manual policies   | -              | Data Loss Prevention        |

## 5. Requisitos Obligatorios 🔴

### Clasificación

- [ ] Etiquetar datos según nivel (metadata, tags AWS)
- [ ] Controles de acceso según clasificación
- [ ] Documentar clasificación en catálogos de datos

### Cifrado

- [ ] TLS 1.2+ obligatorio en tránsito (preferir 1.3)
- [ ] AES-256 en reposo (RDS, S3, EBS, backups)
- [ ] Prohibido: TLS 1.0/1.1, SSL, RC4, DES, 3DES
- [ ] Certificados válidos (no self-signed en prod)
- [ ] Rotación automática de claves (KMS, Secrets Manager)

### Enmascaramiento

- [ ] Enmascarar PII/PCI en logs, APIs, reportes
- [ ] Auto-masking en Serilog (enricher)
- [ ] Hashing para DNI, pseudonimización para nombres
- [ ] No loggear objetos completos sin sanitizar

### Minimización

- [ ] Solo recolectar datos necesarios (GDPR Art. 5)
- [ ] No guardar "por si acaso"
- [ ] No PII en logs, o enmascarar si es necesario
- [ ] TTL en logs: 90 días máximo
- [ ] Analytics sin PII, usar IDs agregados

### Retención y Eliminación

- [ ] PII: 7 años desde última actividad
- [ ] Logs aplicación: 90 días
- [ ] Backups: 30 días
- [ ] Soft delete: columna deleted_at, hard delete tras periodo de gracia
- [ ] Right to be forgotten: endpoint /api/gdpr/erase-user-data
- [ ] Auditoría de solicitudes y ejecuciones de borrado
- [ ] Jobs automáticos de cleanup y notificaciones previas

## 6. Configuración / Implementación

### Ejemplo: Cifrado en .NET y AWS

```csharp
// Cifrado en tránsito
services.AddHttpsRedirection(options =>
// Cifrado en reposo (RDS, S3)
// Terraform
resource "aws_db_instance" "main" {
  storage_encrypted = true
  kms_key_id        = aws_kms_key.db.arn
    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm     = "aws:kms"
        kms_master_key_id = aws_kms_key.s3.arn
      }
    }
  }
}
```

### Ejemplo: Enmascaramiento en logs (Serilog)

```csharp
Log.Logger = new LoggerConfiguration()
    .Enrich.With(new MaskingEnricher())
    .WriteTo.Console()
    .CreateLogger();
```

### Ejemplo: Minimización en API

```csharp
public class UserDto {
    public string Email { get; set; } // opcional
    public string? Phone { get; set; } // opcional
    // No incluir más campos de los necesarios
}
```

### Ejemplo: Soft Delete y Right to be Forgotten

```sql
ALTER TABLE users ADD COLUMN deleted_at timestamp;

-- Hard delete tras 90 días
delete from users where deleted_at < now() - interval '90 days';
```

```http
POST /api/gdpr/erase-user-data
{
  "userId": "..."
}
```

## 7. Validación

- Revisar etiquetas y clasificación en catálogos de datos
- Validar cifrado en tránsito y reposo (AWS, certificados)
- Revisar logs para enmascaramiento y ausencia de PII
- Validar TTL y políticas de retención
- Auditar logs de borrado y right to be forgotten

## 8. Referencias

- [GDPR Art. 5](https://gdpr-info.eu/art-5-gdpr/)
- [OWASP ASVS V6/V9](https://owasp.org/www-project-application-security-verification-standard/)
- [AWS KMS](https://docs.aws.amazon.com/kms/)
- [Serilog Masking](https://github.com/serilog/serilog-enrichers-sensitive)
- [PCI DSS](https://www.pcisecuritystandards.org/)
- [Terraform AWS Encryption](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/db_instance#storage_encrypted)
- [Right to be Forgotten](https://gdpr-info.eu/art-17-gdpr/)

## \*\*\* End Patch
