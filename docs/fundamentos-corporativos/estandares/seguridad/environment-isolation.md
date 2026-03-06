---
id: environment-isolation
sidebar_position: 6
title: Aislamiento de Ambientes y Tenants
description: Estándares para aislar ambientes (dev/staging/prod) en VPCs separadas, aislamiento de tenants en multi-tenancy y seguridad de perímetro (bastion, VPN, VPC Endpoints)
tags:
  [
    seguridad,
    network,
    environment-isolation,
    multi-tenancy,
    bastion,
    aws-vpc,
    terraform,
  ]
---

# Aislamiento de Ambientes y Tenants

## Contexto

Este estándar consolida **3 conceptos relacionados** con el aislamiento de recursos y perímetro de red. Garantiza que diferentes ambientes y tenants estén completamente separados, y que el acceso administrativo sea controlado y auditado.

**Conceptos incluidos:**

- **Environment Isolation** → Separar ambientes (dev/staging/prod) en VPCs o cuentas AWS dedicadas
- **Tenant Isolation** → Aislar datos y recursos entre tenants en sistemas multi-tenant
- **Perimeter Security** → Proteger el perímetro con bastion hosts, VPN y VPC Endpoints

---

## Stack Tecnológico

| Componente                  | Tecnología        | Versión | Uso                               |
| --------------------------- | ----------------- | ------- | --------------------------------- |
| **Cloud Platform**          | AWS               | Latest  | Infraestructura de red            |
| **Network**                 | AWS VPC           | Latest  | Aislamiento de ambientes          |
| **Multi-Account**           | AWS Organizations | Latest  | Cuentas separadas por ambiente    |
| **Container Orchestration** | AWS ECS Fargate   | Latest  | Orquestación de contenedores      |
| **Runtime**                 | .NET              | 8.0+    | Aplicaciones con tenant isolation |
| **Database**                | PostgreSQL        | 15+     | Row-Level Security por tenant     |
| **IaC**                     | Terraform         | 1.7+    | Infraestructura como código       |

---

## Aislamiento de Ambientes

### ¿Qué es Environment Isolation?

Separación completa de ambientes (dev, staging, prod) en VPCs dedicadas para prevenir contaminación y acceso no autorizado entre ambientes.

**Propósito:** Reducir riesgo de cambios en dev/staging afectando producción.

**Estrategias:**

- **Separate VPCs**: VPC dedicada por ambiente
- **Separate AWS Accounts**: Cuenta AWS separada por ambiente (recomendado)
- **No Cross-Environment Access**: Sin conectividad directa entre ambientes

**Beneficios:**
✅ Blast radius limitado a un ambiente
✅ Facilita compliance audits
✅ Previene accidentes (deploy en prod por error)
✅ Permite pruebas destructivas en dev sin riesgo

### Terraform: VPCs Separadas por Ambiente

```hcl
# terraform/environments/dev/main.tf
module "vpc_dev" {
  source             = "../../modules/vpc"
  environment        = "dev"
  vpc_cidr           = "10.0.0.0/16"
  availability_zones = ["us-east-1a", "us-east-1b"]
  tags               = { Environment = "dev", CostCenter = "engineering" }
}

# terraform/environments/staging/main.tf
module "vpc_staging" {
  source             = "../../modules/vpc"
  environment        = "staging"
  vpc_cidr           = "10.1.0.0/16"
  availability_zones = ["us-east-1a", "us-east-1b"]
  tags               = { Environment = "staging", CostCenter = "engineering" }
}

# terraform/environments/prod/main.tf
module "vpc_prod" {
  source             = "../../modules/vpc"
  environment        = "prod"
  vpc_cidr           = "10.2.0.0/16"
  availability_zones = ["us-east-1a", "us-east-1b", "us-east-1c"]
  tags               = { Environment = "prod", CostCenter = "operations", Compliance = "pci-dss" }
}
```

### AWS Organizations: Cuentas Separadas

```hcl
# terraform/organization/main.tf

resource "aws_organizations_organization" "main" {
  feature_set = "ALL"
}

resource "aws_organizations_account" "dev" {
  name      = "Talma - Development"
  email     = "aws-dev@talma.pe"
  role_name = "OrganizationAccountAccessRole"
  tags      = { Environment = "dev" }
}

resource "aws_organizations_account" "staging" {
  name      = "Talma - Staging"
  email     = "aws-staging@talma.pe"
  role_name = "OrganizationAccountAccessRole"
  tags      = { Environment = "staging" }
}

resource "aws_organizations_account" "prod" {
  name      = "Talma - Production"
  email     = "aws-prod@talma.pe"
  role_name = "OrganizationAccountAccessRole"
  tags      = { Environment = "prod", Compliance = "pci-dss" }
}

# Service Control Policy: Dev no puede acceder a prod
resource "aws_organizations_policy" "deny_prod_access_from_dev" {
  name        = "DenyProdAccessFromDev"
  description = "Prevents dev account from accessing prod resources"

  content = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Deny"
        Action   = "*"
        Resource = "arn:aws:*:*:${aws_organizations_account.prod.id}:*"
        Condition = {
          StringEquals = {
            "aws:PrincipalAccount" = aws_organizations_account.dev.id
          }
        }
      }
    ]
  })
}
```

---

## Aislamiento de Tenants

### ¿Qué es Tenant Isolation?

En sistemas multi-tenant, asegurar que datos y recursos de un tenant no sean accesibles por otros tenants.

**Estrategias:**

- **Physical Isolation**: Infraestructura dedicada por tenant (costoso)
- **Logical Isolation**: Infraestructura compartida con controles de acceso
- **Hybrid**: Infraestructura compartida, datos dedicados

**Implementación:**

- **Database-level**: Row-Level Security por `tenant_id`
- **Application-level**: Filtros automáticos por `tenant_id`
- **Network-level**: Security groups o VPCs por tenant (tier enterprise)

**Beneficios:**
✅ Compliance con GDPR (aislamiento de datos)
✅ Prevención de data leaks entre tenants
✅ Soporte para SLAs diferenciados

### .NET: Tenant Isolation Middleware

```csharp
// src/Shared/MultiTenancy/TenantResolutionMiddleware.cs
public class TenantResolutionMiddleware
{
    private readonly RequestDelegate _next;

    public TenantResolutionMiddleware(RequestDelegate next) => _next = next;

    public async Task InvokeAsync(HttpContext context, ITenantService tenantService)
    {
        var tenantIdClaim = context.User.FindFirst("tenant_id")?.Value;

        if (string.IsNullOrEmpty(tenantIdClaim))
        {
            context.Response.StatusCode = 400;
            await context.Response.WriteAsJsonAsync(new
            {
                error = "tenant_id_missing",
                message = "JWT token must contain tenant_id claim"
            });
            return;
        }

        if (!Guid.TryParse(tenantIdClaim, out var tenantId))
        {
            context.Response.StatusCode = 400;
            await context.Response.WriteAsJsonAsync(new { error = "invalid_tenant_id" });
            return;
        }

        var tenant = await tenantService.GetTenantByIdAsync(tenantId);
        if (tenant == null || !tenant.IsActive)
        {
            context.Response.StatusCode = 403;
            await context.Response.WriteAsJsonAsync(new { error = "tenant_inactive" });
            return;
        }

        context.Items["TenantId"] = tenantId;
        context.Items["Tenant"] = tenant;

        await _next(context);
    }
}

// EF Core: Query Filter automático por tenant
public class AppDbContext : DbContext
{
    private readonly IHttpContextAccessor _httpContextAccessor;

    private Guid GetCurrentTenantId()
    {
        var tenantId = _httpContextAccessor.HttpContext?.Items["TenantId"];
        if (tenantId == null)
            throw new InvalidOperationException("TenantId not found in HttpContext");
        return (Guid)tenantId;
    }

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        // Filtro global: todas las queries añaden automáticamente WHERE tenant_id = {current}
        modelBuilder.Entity<Order>()
            .HasQueryFilter(o => o.TenantId == GetCurrentTenantId());

        modelBuilder.Entity<Customer>()
            .HasQueryFilter(c => c.TenantId == GetCurrentTenantId());

        modelBuilder.Entity<Payment>()
            .HasQueryFilter(p => p.TenantId == GetCurrentTenantId());
    }
}

// Service: tenant_id se aplica automáticamente en todas las queries
public class OrderService
{
    public async Task<List<Order>> GetOrdersAsync()
    {
        // EF Core agrega WHERE tenant_id = {current} automáticamente
        return await _context.Orders.ToListAsync();
    }

    public async Task<Order> CreateOrderAsync(CreateOrderRequest request)
    {
        var tenantId = (Guid)_httpContext.Items["TenantId"];

        var order = new Order
        {
            TenantId = tenantId,  // MUST: Siempre setear tenant_id explícitamente
            CustomerId = request.CustomerId
        };

        _context.Orders.Add(order);
        await _context.SaveChangesAsync();
        return order;
    }
}
```

---

## Seguridad de Perímetro

### ¿Qué es Perimeter Security?

Protección del perímetro de la red limitando puntos de entrada y requiriendo autenticación/autorización para acceso a recursos internos.

**Componentes:**

- **Bastion Hosts**: Jump servers para acceso SSH/RDP
- **VPN**: Acceso seguro a recursos privados
- **VPC Endpoints**: Acceso privado a servicios AWS sin salir a Internet
- **Private Subnets**: Sin IPs públicas en instancias de app/data

**Beneficios:**
✅ Reduce superficie de ataque
✅ Auditoría centralizada de accesos
✅ Defensa contra port scanning
✅ Prevención de exposición accidental

### Bastion Host con Session Manager

```hcl
# Bastion host sin SSH público (usa AWS Systems Manager Session Manager)
resource "aws_instance" "bastion" {
  ami           = data.aws_ami.amazon_linux_2.id
  instance_type = "t3.micro"

  subnet_id              = aws_subnet.public[0].id
  vpc_security_group_ids = [aws_security_group.bastion.id]

  iam_instance_profile = aws_iam_instance_profile.bastion.name

  # Sin IP pública: acceso exclusivamente via Session Manager
  associate_public_ip_address = false

  user_data = <<-EOF
    #!/bin/bash
    yum install -y amazon-ssm-agent
    systemctl enable amazon-ssm-agent
    systemctl start amazon-ssm-agent
  EOF

  tags = { Name = "${var.environment}-bastion" }
}

resource "aws_iam_role" "bastion" {
  name = "${var.environment}-bastion-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole"
      Principal = { Service = "ec2.amazonaws.com" }
      Effect    = "Allow"
    }]
  })
}

resource "aws_iam_role_policy_attachment" "bastion_ssm" {
  role       = aws_iam_role.bastion.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

# Uso: aws ssm start-session --target i-1234567890abcdef0
# No requiere SSH keys ni IPs públicas
```

### VPC Endpoints (PrivateLink)

```hcl
# VPC Endpoint para S3 (tráfico interno, sin internet)
resource "aws_vpc_endpoint" "s3" {
  vpc_id       = aws_vpc.main.id
  service_name = "com.amazonaws.${var.region}.s3"

  route_table_ids = concat(
    aws_route_table.private_app[*].id,
    aws_route_table.private_data[*].id
  )

  tags = { Name = "${var.environment}-s3-endpoint" }
}

# VPC Endpoint para Secrets Manager
resource "aws_vpc_endpoint" "secrets_manager" {
  vpc_id              = aws_vpc.main.id
  service_name        = "com.amazonaws.${var.region}.secretsmanager"
  vpc_endpoint_type   = "Interface"

  subnet_ids          = aws_subnet.private_app[*].id
  security_group_ids  = [aws_security_group.vpc_endpoints.id]

  private_dns_enabled = true

  tags = { Name = "${var.environment}-secrets-manager-endpoint" }
}

# Las apps acceden a Secrets Manager sin salir a Internet
```

---

## Monitoreo y Observabilidad

```promql
# Intentos de acceso entre ambientes (debe ser 0)
cross_environment_access_attempts_total

# Sesiones de Session Manager abiertas
aws_ssm_sessions_active{target_type="instance"}

# Accesos a recursos de otros tenants bloqueados
tenant_isolation_violations_total
```

---

## Requisitos Técnicos

### MUST (Obligatorio)

- **MUST** separar ambientes en VPCs dedicadas (o cuentas AWS separadas)
- **MUST** filtrar queries por `tenant_id` en todas las entidades multi-tenant
- **MUST** usar Row-Level Security en PostgreSQL para tenant isolation
- **MUST** usar bastion hosts o Session Manager para acceso a recursos privados
- **MUST** no asignar IPs públicas a instancias de app/data layers
- **MUST** usar VPC Endpoints para servicios AWS (S3, Secrets Manager, KMS)

### SHOULD (Fuertemente recomendado)

- **SHOULD** usar AWS Organizations con cuentas separadas por ambiente
- **SHOULD** aplicar Service Control Policies para prevenir acceso cross-account
- **SHOULD** habilitar VPC Flow Logs en todos los ambientes

### MUST NOT (Prohibido)

- **MUST NOT** compartir VPC entre ambientes (dev ↔ prod)
- **MUST NOT** tener conectividad directa entre VPC de dev y prod
- **MUST NOT** incluir datos de producción en ambiente de desarrollo
- **MUST NOT** desplegar código de dev directamente en prod sin pipeline

---

## Referencias

- [AWS Organizations Best Practices](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_best-practices.html)
- [AWS VPC Endpoints](https://docs.aws.amazon.com/vpc/latest/privatelink/vpc-endpoints.html)
- [Multi-Tenant SaaS Architecture](https://docs.aws.amazon.com/whitepapers/latest/saas-architecture-fundamentals/)
- [Segmentación y Controles de Acceso de Red](./network-segmentation.md)
- [Data Protection](./data-protection.md)
- [Zero Trust Networking](./zero-trust-networking.md)
