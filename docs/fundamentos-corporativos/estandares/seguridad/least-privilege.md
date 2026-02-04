---
id: least-privilege
sidebar_position: 9
title: Principio de Mínimo Privilegio
description: Estándar para aplicar least privilege en IAM roles AWS, RBAC Keycloak, permisos de BD y revisión trimestral de accesos
---

# Estándar Técnico — Principio de Mínimo Privilegio

---

## 1. Propósito

Garantizar que usuarios, servicios y aplicaciones tengan **únicamente** los permisos mínimos necesarios para sus funciones, usando IAM roles específicos, RBAC granular, revisión trimestral de accesos y principio deny-by-default.

---

## 2. Alcance

**Aplica a:**

- IAM roles y policies de AWS
- Usuarios y roles en Keycloak
- Service accounts en aplicaciones
- Permisos de base de datos (PostgreSQL, Oracle, SQL Server)
- Acceso a secretos (AWS Secrets Manager)
- Permisos de red (Security Groups, NACLs)

**No aplica a:**

- Cuentas root de AWS (prohibido uso operacional)
- Usuarios personales dev local (usar dotnet user-secrets)

---

## 3. Tecnologías Aprobadas

| Componente    | Tecnología              | Versión mínima | Observaciones                  |
| ------------- | ----------------------- | -------------- | ------------------------------ |
| **IAM**       | AWS IAM                 | -              | Roles con policies específicas |
| **RBAC**      | Keycloak                | 23.0+          | Roles y claims granulares      |
| **Database**  | PostgreSQL roles        | 14+            | Row-level security             |
| **Secrets**   | AWS Secrets Manager     | -              | Políticas por servicio         |
| **IaC**       | Terraform               | 1.6+           | Gestión de permisos            |
| **Auditoría** | AWS CloudTrail          | -              | Logs de acceso                 |
| **Review**    | AWS IAM Access Analyzer | -              | Detección permisos excesivos   |

> El uso de tecnologías no listadas requiere aprobación de Arquitectura.

---

## 4. Requisitos Obligatorios 🔴

### 4.1 IAM Roles (AWS)

- [ ] **NO usar IAM Users** para servicios (solo IAM Roles)
- [ ] **Un rol por servicio** (no compartir roles entre servicios)
- [ ] **Policies específicas** por recurso (NO usar wildcards `*` innecesarios)
- [ ] **Deny-by-default** (solo permisos explícitos)
- [ ] **MFA obligatorio** para usuarios humanos
- [ ] **Revisión trimestral** de permisos no usados

### 4.2 RBAC (Keycloak)

- [ ] **Roles granulares** por funcionalidad (no "admin" global)
- [ ] **Claims específicos** en JWT (ej: `payments:write`, `orders:read`)
- [ ] **Tiempo de vida corto** para tokens (15 minutos)
- [ ] **Refresh tokens** con rotación
- [ ] **Auditoría** de cambios de roles

### 4.3 Base de Datos

- [ ] **Usuarios dedicados** por aplicación (NO compartir credenciales)
- [ ] **Row-level security** para multi-tenancy
- [ ] **Schema-level permissions** granulares
- [ ] **NO usar superuser** en aplicaciones
- [ ] **Read-only roles** para reportería

---

## 5. IAM Roles - AWS ECS Fargate

### Terraform - Task Role Específico

```hcl
# iam-payment-api.tf

# Task Execution Role (pull image, logs)
resource "aws_iam_role" "payment_api_execution" {
  name = "ecs-execution-payment-api-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "ecs-tasks.amazonaws.com"
      }
    }]
  })
}

# Permissions: SOLO lo necesario para execution
resource "aws_iam_role_policy" "payment_api_execution" {
  name = "execution-policy"
  role = aws_iam_role.payment_api_execution.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ecr:GetAuthorizationToken",
          "ecr:BatchCheckLayerAvailability",
          "ecr:GetDownloadUrlForLayer",
          "ecr:BatchGetImage"
        ]
        Resource = "*"  # ECR requires wildcard
      },
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:${var.region}:${data.aws_caller_identity.current.account_id}:log-group:/ecs/payment-api:*"
      }
    ]
  })
}

# Task Role (runtime permissions)
resource "aws_iam_role" "payment_api_task" {
  name = "ecs-task-payment-api-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "ecs-tasks.amazonaws.com"
      }
    }]
  })
}

# Permissions: SOLO acceso a secrets de ESTE servicio
resource "aws_iam_role_policy" "payment_api_secrets" {
  name = "secrets-access"
  role = aws_iam_role.payment_api_task.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue",
          "secretsmanager:DescribeSecret"
        ]
        # ESPECÍFICO: Solo secretos de payment-api
        Resource = "arn:aws:secretsmanager:${var.region}:${data.aws_caller_identity.current.account_id}:secret:/${var.environment}/payment-api/*"
      },
      {
        Effect = "Allow"
        Action = [
          "kms:Decrypt",
          "kms:DescribeKey"
        ]
        Resource = aws_kms_key.secrets.arn
      }
    ]
  })
}

# S3 access: SOLO bucket específico
resource "aws_iam_role_policy" "payment_api_s3" {
  name = "s3-access"
  role = aws_iam_role.payment_api_task.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = [
        "s3:GetObject",
        "s3:PutObject"
      ]
      # ESPECÍFICO: Solo prefix de payment-api
      Resource = "arn:aws:s3:::${var.bucket_name}/payments/*"
    }]
  })
}
```

---

## 6. RBAC - Keycloak Roles

### Roles Granulares (NO "admin" global)

```json
// Keycloak Realm Roles
{
  "roles": [
    {
      "name": "payment:read",
      "description": "Ver pagos (read-only)"
    },
    {
      "name": "payment:write",
      "description": "Crear/modificar pagos"
    },
    {
      "name": "payment:approve",
      "description": "Aprobar pagos >$10,000"
    },
    {
      "name": "order:read",
      "description": "Ver órdenes"
    },
    {
      "name": "order:write",
      "description": "Crear órdenes"
    },
    {
      "name": "report:financial",
      "description": "Acceso a reportes financieros"
    }
  ]
}
```

### .NET - Claims-Based Authorization

```csharp
// Program.cs
builder.Services.AddAuthorization(options =>
{
    // Policy específica por acción
    options.AddPolicy("CanCreatePayment", policy =>
        policy.RequireClaim("realm_access", "payment:write"));

    options.AddPolicy("CanApprovePayment", policy =>
        policy.RequireClaim("realm_access", "payment:approve"));

    options.AddPolicy("CanViewFinancialReports", policy =>
        policy.RequireClaim("realm_access", "report:financial"));
});

// Controller
[Authorize(Policy = "CanCreatePayment")]
[HttpPost("/api/payments")]
public async Task<IActionResult> CreatePayment([FromBody] PaymentRequest request)
{
    // Solo usuarios con claim "payment:write" pueden acceder
    return Ok(await _paymentService.CreateAsync(request));
}

[Authorize(Policy = "CanApprovePayment")]
[HttpPost("/api/payments/{id}/approve")]
public async Task<IActionResult> ApprovePayment(Guid id)
{
    // Requiere claim adicional "payment:approve"
    return Ok(await _paymentService.ApproveAsync(id));
}
```

---

## 7. Database - PostgreSQL Roles

### Usuarios Dedicados por Aplicación

```sql
-- Crear rol read-only para reportería
CREATE ROLE payment_readonly LOGIN PASSWORD 'secure_password';

-- Permisos mínimos: SOLO SELECT
GRANT CONNECT ON DATABASE payment_db TO payment_readonly;
GRANT USAGE ON SCHEMA public TO payment_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO payment_readonly;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO payment_readonly;

-- Crear rol write para aplicación
CREATE ROLE payment_api LOGIN PASSWORD 'secure_password';

-- Permisos: SELECT, INSERT, UPDATE (NO DELETE, NO DDL)
GRANT CONNECT ON DATABASE payment_db TO payment_api;
GRANT USAGE ON SCHEMA public TO payment_api;
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO payment_api;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO payment_api;

-- Row-Level Security (Multi-tenancy)
ALTER TABLE payments ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_isolation ON payments
  USING (tenant_id = current_setting('app.current_tenant')::uuid);

-- Revocar acceso a tablas sensibles
REVOKE ALL ON TABLE audit_logs FROM payment_api;
GRANT INSERT ON TABLE audit_logs TO payment_api;  -- Solo insertar, no leer
```

---

## 8. Revisión de Permisos - IAM Access Analyzer

### Terraform - Habilitar Access Analyzer

```hcl
# iam-access-analyzer.tf
resource "aws_accessanalyzer_analyzer" "main" {
  analyzer_name = "least-privilege-analyzer-${var.environment}"
  type          = "ACCOUNT"

  tags = {
    Environment = var.environment
    Purpose     = "Detect overprivileged roles"
  }
}

# CloudWatch Event para alertas
resource "aws_cloudwatch_event_rule" "access_analyzer_findings" {
  name        = "iam-access-analyzer-findings"
  description = "Alerta cuando Access Analyzer detecta permisos excesivos"

  event_pattern = jsonencode({
    source      = ["aws.access-analyzer"]
    detail-type = ["Access Analyzer Finding"]
    detail = {
      status = ["ACTIVE"]
    }
  })
}

resource "aws_cloudwatch_event_target" "sns" {
  rule      = aws_cloudwatch_event_rule.access_analyzer_findings.name
  target_id = "SendToSNS"
  arn       = aws_sns_topic.security_alerts.arn
}
```

### Script de Revisión Trimestral

```bash
#!/bin/bash
# quarterly-permissions-review.sh

# 1. Listar roles con permisos no usados (últimos 90 días)
aws iam generate-service-last-accessed-details \
  --arn arn:aws:iam::123456789:role/ecs-task-payment-api-prod

JOB_ID=$(aws iam generate-service-last-accessed-details \
  --arn arn:aws:iam::123456789:role/ecs-task-payment-api-prod \
  --query 'JobId' --output text)

# Esperar resultado
aws iam get-service-last-accessed-details --job-id $JOB_ID

# 2. Access Analyzer findings
aws accessanalyzer list-findings \
  --analyzer-arn arn:aws:access-analyzer:us-east-1:123456789:analyzer/least-privilege-analyzer-prod \
  --filter '{ "status": { "eq": ["ACTIVE"] } }'

# 3. Revisar usuarios sin MFA
aws iam list-users --query 'Users[?not_null(PasswordLastUsed)]' \
  | jq -r '.[] | select(.MfaDevices | length == 0) | .UserName'
```

---

## 9. Principio Deny-by-Default

### Security Groups - Whitelist Approach

```hcl
# security-groups.tf

# ❌ MAL: Permite todo saliente
resource "aws_security_group" "bad_example" {
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# ✅ BIEN: Solo lo necesario
resource "aws_security_group" "payment_api" {
  name        = "payment-api-${var.environment}"
  description = "Security group for payment API"
  vpc_id      = aws_vpc.main.id

  # Ingress: Solo desde Kong Gateway
  ingress {
    description     = "HTTP from Kong Gateway"
    from_port       = 8080
    to_port         = 8080
    protocol        = "tcp"
    security_groups = [aws_security_group.kong.id]
  }

  # Egress: SOLO lo necesario
  egress {
    description = "PostgreSQL"
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = [aws_subnet.database.cidr_block]
  }

  egress {
    description = "HTTPS to Stripe API"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  # External API
  }

  # NO permitir acceso saliente general
}
```

---

## 10. Validación de Cumplimiento

```bash
# Verificar roles sin MFA (usuarios humanos)
aws iam list-users --query 'Users[*].[UserName,PasswordLastUsed]' --output table

# Detectar policies con wildcards excesivos
aws iam list-policies --scope Local \
  | jq -r '.Policies[] | select(.PolicyName) | .Arn' \
  | while read arn; do
      aws iam get-policy-version --policy-arn $arn --version-id v1 \
        | jq -r '.PolicyVersion.Document.Statement[] | select(.Resource == "*") | "WILDCARD: " + $arn'
    done

# Access Analyzer findings activos
aws accessanalyzer list-findings \
  --analyzer-arn $ANALYZER_ARN \
  --filter '{"status": {"eq": ["ACTIVE"]}}' \
  --query 'findings[*].[id, resourceType, principal]'

# Revisar permisos de BD
psql -U admin payment_db -c "\du+"  # Listar roles y permisos
```

---

## 11. Referencias

**AWS:**

- [IAM Best Practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html)
- [IAM Access Analyzer](https://docs.aws.amazon.com/IAM/latest/UserGuide/what-is-access-analyzer.html)

**NIST:**

- [NIST SP 800-53 AC-6 - Least Privilege](https://csrc.nist.gov/pubs/sp/800/53/r5/upd1/final)

**OWASP:**

- [Authorization Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html)
