---
id: defense-in-depth
sidebar_position: 4
title: Defensa en Profundidad
description: Estándar para implementar múltiples capas de seguridad (WAF, Security Groups, encriptación, IDS, backups) sin depender de un único control
---

# Estándar Técnico — Defensa en Profundidad

---

## 1. Propósito

Implementar seguridad en múltiples capas (red, aplicación, datos, identidad) para que el fallo de un control no comprometa el sistema completo, usando AWS WAF, Security Groups, encriptación at-rest/in-transit, IDS y backups.

---

## 2. Alcance

**Aplica a:**

- Toda la infraestructura AWS
- Aplicaciones en ECS Fargate
- Bases de datos (PostgreSQL, Oracle, SQL Server)
- APIs REST públicas y privadas
- Almacenamiento S3
- Tráfico de red

**No aplica a:**

- Ambientes dev/sandbox (puede relajarse algunos controles)
- Prototipos temporales sin datos reales

---

## 3. Capas de Seguridad Obligatorias

### Modelo de 7 Capas

| Capa              | Control                       | Tecnología                  | Estado         |
| ----------------- | ----------------------------- | --------------------------- | -------------- |
| **1. Perímetro**  | WAF, DDoS protection          | AWS WAF, CloudFlare         | 🔴 Obligatorio |
| **2. Red**        | Segmentación, Security Groups | VPC, NACLs, Security Groups | 🔴 Obligatorio |
| **3. Gateway**    | Rate limiting, autenticación  | Kong API Gateway            | 🔴 Obligatorio |
| **4. Aplicación** | Input validation, SAST        | FluentValidation, SonarQube | 🔴 Obligatorio |
| **5. Identidad**  | SSO, MFA, RBAC                | Keycloak, JWT RS256         | 🔴 Obligatorio |
| **6. Datos**      | Encriptación, backups         | AWS KMS, RDS encryption     | 🔴 Obligatorio |
| **7. Monitoreo**  | IDS, logging, alertas         | Grafana, CloudTrail         | 🔴 Obligatorio |

---

## 4. Tecnologías Aprobadas

| Componente     | Tecnología                | Versión mínima | Observaciones            |
| -------------- | ------------------------- | -------------- | ------------------------ |
| **WAF**        | AWS WAF                   | -              | Managed rules + custom   |
| **DDoS**       | CloudFlare                | -              | CDN + DDoS protection    |
| **Network**    | AWS VPC, Security Groups  | -              | Segmentación obligatoria |
| **Gateway**    | Kong                      | 3.5+           | Rate limiting, auth      |
| **IDS/IPS**    | AWS GuardDuty             | -              | Threat detection         |
| **Encryption** | AWS KMS                   | -              | At-rest encryption       |
| **TLS**        | TLS 1.3                   | -              | In-transit encryption    |
| **Backup**     | AWS Backup                | -              | Automated backups        |
| **Monitoring** | Grafana Stack             | -              | Loki + Mimir + Tempo     |
| **SIEM**       | CloudTrail + Grafana Loki | -              | Security logs            |

> El uso de tecnologías no listadas requiere aprobación de Arquitectura.

---

## 5. Requisitos Obligatorios 🔴

### Capa 1: Perímetro (WAF)

- [ ] **AWS WAF** habilitado en CloudFront/ALB
- [ ] **Managed Rules** activados (OWASP Top 10, Bot Control)
- [ ] **Rate limiting** global (1000 req/5min por IP)
- [ ] **Geo-blocking** si aplica (bloquear países no operacionales)
- [ ] **Custom rules** para patrones de ataque específicos

### Capa 2: Red

- [ ] **VPC aisladas** por entorno (dev, staging, prod)
- [ ] **Subnets privadas** para aplicaciones (NO public IPs)
- [ ] **Security Groups** con principio deny-by-default
- [ ] **NACLs** como capa adicional de defensa
- [ ] **VPC Flow Logs** habilitados

### Capa 3: API Gateway

- [ ] **Kong Gateway** como único punto de entrada
- [ ] **Rate limiting** por consumer (100-500 req/min)
- [ ] **JWT validation** antes de enrutar
- [ ] **Request/response size limits**
- [ ] **IP whitelisting** para APIs internas

### Capa 4: Aplicación

- [ ] **Input validation** con FluentValidation
- [ ] **Output encoding** (evitar XSS)
- [ ] **SAST** en CI/CD (SonarQube)
- [ ] **Dependency scanning** (OWASP Dependency-Check)
- [ ] **Container scanning** (Trivy)

### Capa 5: Identidad

- [ ] **Keycloak SSO** para autenticación
- [ ] **MFA obligatorio** para usuarios humanos
- [ ] **JWT RS256** con rotación de keys
- [ ] **Token TTL corto** (15 minutos)
- [ ] **RBAC granular** (claims específicos)

### Capa 6: Datos

- [ ] **Encriptación at-rest** (RDS, S3 con KMS)
- [ ] **Encriptación in-transit** (TLS 1.3)
- [ ] **Backups automáticos** con retención 30 días
- [ ] **Backups encriptados**
- [ ] **Point-in-time recovery** habilitado (RDS)

### Capa 7: Monitoreo

- [ ] **CloudTrail** habilitado (logs inmutables)
- [ ] **GuardDuty** activo (threat detection)
- [ ] **Grafana Loki** para logs centralizados
- [ ] **Alertas** para eventos de seguridad
- [ ] **Incident response plan** documentado

---

## 6. Implementación por Capas

### Capa 1: AWS WAF

```hcl
# waf.tf
resource "aws_wafv2_web_acl" "main" {
  name  = "api-waf-${var.environment}"
  scope = "REGIONAL"  # Para ALB/API Gateway

  default_action {
    allow {}
  }

  # Managed Rule: OWASP Top 10
  rule {
    name     = "AWSManagedRulesCommonRuleSet"
    priority = 1

    override_action {
      none {}
    }

    statement {
      managed_rule_group_statement {
        vendor_name = "AWS"
        name        = "AWSManagedRulesCommonRuleSet"
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "AWSManagedRulesCommonRuleSetMetric"
      sampled_requests_enabled   = true
    }
  }

  # Rate Limiting
  rule {
    name     = "RateLimitRule"
    priority = 2

    action {
      block {}
    }

    statement {
      rate_based_statement {
        limit              = 1000
        aggregate_key_type = "IP"
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "RateLimitMetric"
      sampled_requests_enabled   = true
    }
  }

  # Geo-blocking (ejemplo: bloquear países no operacionales)
  rule {
    name     = "GeoBlockingRule"
    priority = 3

    action {
      block {}
    }

    statement {
      not_statement {
        statement {
          geo_match_statement {
            country_codes = ["PE", "CL", "CO", "EC", "US"]  # Solo permitir estos
          }
        }
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "GeoBlockingMetric"
      sampled_requests_enabled   = true
    }
  }

  visibility_config {
    cloudwatch_metrics_enabled = true
    metric_name                = "WAFMetric"
    sampled_requests_enabled   = true
  }
}

# Asociar WAF a ALB
resource "aws_wafv2_web_acl_association" "alb" {
  resource_arn = aws_lb.main.arn
  web_acl_arn  = aws_wafv2_web_acl.main.arn
}
```

### Capa 2: Network Segmentation

```hcl
# vpc.tf
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name        = "vpc-${var.environment}"
    Environment = var.environment
  }
}

# Subnets públicas (SOLO para ALB/NAT Gateway)
resource "aws_subnet" "public" {
  count             = 2
  vpc_id            = aws_vpc.main.id
  cidr_block        = cidrsubnet(aws_vpc.main.cidr_block, 8, count.index)
  availability_zone = data.aws_availability_zones.available.names[count.index]

  tags = {
    Name = "public-subnet-${count.index + 1}"
    Tier = "public"
  }
}

# Subnets privadas (aplicaciones ECS)
resource "aws_subnet" "private_app" {
  count             = 2
  vpc_id            = aws_vpc.main.id
  cidr_block        = cidrsubnet(aws_vpc.main.cidr_block, 8, count.index + 10)
  availability_zone = data.aws_availability_zones.available.names[count.index]

  tags = {
    Name = "private-app-subnet-${count.index + 1}"
    Tier = "application"
  }
}

# Subnets privadas (bases de datos)
resource "aws_subnet" "private_db" {
  count             = 2
  vpc_id            = aws_vpc.main.id
  cidr_block        = cidrsubnet(aws_vpc.main.cidr_block, 8, count.index + 20)
  availability_zone = data.aws_availability_zones.available.names[count.index]

  tags = {
    Name = "private-db-subnet-${count.index + 1}"
    Tier = "database"
  }
}

# Security Group: ECS Tasks (deny-by-default)
resource "aws_security_group" "ecs_tasks" {
  name        = "ecs-tasks-${var.environment}"
  description = "Security group for ECS tasks"
  vpc_id      = aws_vpc.main.id

  # Ingress: SOLO desde ALB
  ingress {
    description     = "HTTP from ALB"
    from_port       = 8080
    to_port         = 8080
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
  }

  # Egress: SOLO lo necesario
  egress {
    description = "PostgreSQL"
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    security_groups = [aws_security_group.rds.id]
  }

  egress {
    description = "HTTPS externos (APIs, NuGet)"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# NACL adicional (capa extra)
resource "aws_network_acl" "app" {
  vpc_id     = aws_vpc.main.id
  subnet_ids = aws_subnet.private_app[*].id

  # Denegar tráfico SSH/RDP
  ingress {
    protocol   = "tcp"
    rule_no    = 100
    action     = "deny"
    cidr_block = "0.0.0.0/0"
    from_port  = 22
    to_port    = 22
  }

  ingress {
    protocol   = "tcp"
    rule_no    = 101
    action     = "deny"
    cidr_block = "0.0.0.0/0"
    from_port  = 3389
    to_port    = 3389
  }

  # Permitir tráfico HTTP desde ALB
  ingress {
    protocol   = "tcp"
    rule_no    = 200
    action     = "allow"
    cidr_block = aws_subnet.public[0].cidr_block
    from_port  = 8080
    to_port    = 8080
  }

  tags = {
    Name = "nacl-app-${var.environment}"
  }
}
```

### Capa 6: Encriptación

```hcl
# encryption.tf

# KMS Key para encriptación at-rest
resource "aws_kms_key" "main" {
  description             = "KMS key for ${var.environment} encryption"
  deletion_window_in_days = 30
  enable_key_rotation     = true

  tags = {
    Environment = var.environment
  }
}

resource "aws_kms_alias" "main" {
  name          = "alias/${var.environment}-encryption"
  target_key_id = aws_kms_key.main.key_id
}

# RDS con encriptación
resource "aws_db_instance" "main" {
  identifier     = "${var.service_name}-${var.environment}"
  engine         = "postgres"
  engine_version = "15.4"

  # Encriptación at-rest
  storage_encrypted = true
  kms_key_id        = aws_kms_key.main.arn

  # Backups encriptados
  backup_retention_period = 30
  backup_window           = "03:00-04:00"

  # Point-in-time recovery
  enabled_cloudwatch_logs_exports = ["postgresql", "upgrade"]

  # SSL/TLS obligatorio
  parameter_group_name = aws_db_parameter_group.ssl_required.name
}

resource "aws_db_parameter_group" "ssl_required" {
  name   = "ssl-required-${var.environment}"
  family = "postgres15"

  parameter {
    name  = "rds.force_ssl"
    value = "1"
  }
}

# S3 con encriptación
resource "aws_s3_bucket" "storage" {
  bucket = "${var.service_name}-storage-${var.environment}"
}

resource "aws_s3_bucket_server_side_encryption_configuration" "storage" {
  bucket = aws_s3_bucket.storage.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = aws_kms_key.main.arn
    }
  }
}

# Bloquear acceso público
resource "aws_s3_bucket_public_access_block" "storage" {
  bucket = aws_s3_bucket.storage.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
```

### Capa 7: Threat Detection

```hcl
# guardduty.tf
resource "aws_guardduty_detector" "main" {
  enable = true

  datasources {
    s3_logs {
      enable = true
    }
    kubernetes {
      audit_logs {
        enable = false  # No usamos EKS
      }
    }
  }

  tags = {
    Environment = var.environment
  }
}

# CloudWatch Event para alertas
resource "aws_cloudwatch_event_rule" "guardduty_findings" {
  name        = "guardduty-findings-${var.environment}"
  description = "Alerta para hallazgos de GuardDuty"

  event_pattern = jsonencode({
    source      = ["aws.guardduty"]
    detail-type = ["GuardDuty Finding"]
    detail = {
      severity = [4, 5, 6, 7, 8]  # HIGH y CRITICAL
    }
  })
}

resource "aws_cloudwatch_event_target" "sns" {
  rule      = aws_cloudwatch_event_rule.guardduty_findings.name
  target_id = "SendToSNS"
  arn       = aws_sns_topic.security_alerts.arn
}
```

---

## 7. Validación de Cumplimiento

```bash
# Verificar WAF activo
aws wafv2 list-web-acls --scope REGIONAL

# GuardDuty habilitado
aws guardduty list-detectors

# VPC Flow Logs
aws ec2 describe-flow-logs

# Encriptación RDS
aws rds describe-db-instances \
  --query 'DBInstances[*].[DBInstanceIdentifier,StorageEncrypted]' \
  --output table

# S3 encryption
aws s3api get-bucket-encryption --bucket my-bucket

# Backups configurados
aws backup list-backup-plans
```

---

## 8. Referencias

**AWS:**

- [AWS Security Best Practices](https://docs.aws.amazon.com/wellarchitected/latest/security-pillar/)
- [Defense in Depth Strategy](https://aws.amazon.com/blogs/security/)

**NIST:**

- [NIST SP 800-53 - Security Controls](https://csrc.nist.gov/pubs/sp/800/53/r5/upd1/final)

**ISO:**

- [ISO 27001:2022 - Information Security](https://www.iso.org/standard/27001)
