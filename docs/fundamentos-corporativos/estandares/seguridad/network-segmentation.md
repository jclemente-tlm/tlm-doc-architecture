---
id: network-segmentation
sidebar_position: 20
title: Network Segmentation
description: Segmentar red en zonas de confianza para contener movimientos laterales
---

# Network Segmentation

## Contexto

Este estándar define **Network Segmentation**: dividir red en **zonas de confianza** con controles entre ellas. Previene movimiento lateral de atacantes. Complementa el [lineamiento de Segmentación y Aislamiento](../../lineamientos/seguridad/06-segmentacion-y-aislamiento.md) mediante **compartimentación de red**.

---

## Trust Zones

```yaml
# ✅ Definir zonas por nivel de confianza

Talma Network Architecture:

  ┌──────────────────────────────────────────────────┐
  │ ZONE 1: Internet (Untrusted)                     │
  │ - Public users                                   │
  │ - Bots, atacantes                                │
  └──────────────────────────────────────────────────┘
              │
  ════════════╪════════════  Control Point 1
              │
  ┌──────────────────────────────────────────────────┐
  │ ZONE 2: DMZ (Semi-Trusted)                       │
  │ - VPC: 10.0.0.0/16                               │
  │ - Public Subnets: 10.0.1.0/24, 10.0.2.0/24       │
  │ - Resources: ALB, NAT Gateway, Bastion           │
  │ - Security: WAF, Shield, Internet Gateway        │
  └──────────────────────────────────────────────────┘
              │
  ════════════╪════════════  Control Point 2
              │
  ┌──────────────────────────────────────────────────┐
  │ ZONE 3: Application (Trusted)                    │
  │ - Private Subnets: 10.0.10.0/24, 10.0.11.0/24    │
  │ - Resources: ECS Tasks, Lambda                   │
  │ - Security: Security Groups (restrictive)        │
  │ - Internet: Via NAT Gateway only (outbound)      │
  └──────────────────────────────────────────────────┘
              │
  ════════════╪════════════  Control Point 3
              │
  ┌──────────────────────────────────────────────────┐
  │ ZONE 4: Data (Highly Trusted)                    │
  │ - Private Subnets: 10.0.20.0/24, 10.0.21.0/24    │
  │ - Resources: RDS, ElastiCache, MSK               │
  │ - Security: Encryption at rest, IAM auth         │
  │ - Internet: NO ACCESS                            │
  └──────────────────────────────────────────────────┘
              │
  ════════════╪════════════  Control Point 4
              │
  ┌──────────────────────────────────────────────────┐
  │ ZONE 5: Management (Admin)                       │
  │ - Private Subnet: 10.0.30.0/24                   │
  │ - Resources: Bastion, Admin tools                │
  │ - Security: MFA required, Session Manager        │
  │ - Access: VPN only                               │
  └──────────────────────────────────────────────────┘

Control Points:
  1. Internet → DMZ: WAF + Shield
  2. DMZ → App: Security Groups (SG)
  3. App → Data: SG + IAM authentication
  4. Management: VPN + MFA + audit logs
```

## Segmentation Strategy

```yaml
# ✅ Terraform: Multi-subnet architecture

# VPC
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name        = "talma-vpc"
    Environment = "production"
  }
}

# ZONE 2: DMZ - Public Subnets
resource "aws_subnet" "dmz" {
  for_each = {
    "dmz-1a" = { cidr = "10.0.1.0/24", az = "us-east-1a" }
    "dmz-1b" = { cidr = "10.0.2.0/24", az = "us-east-1b" }
  }

  vpc_id                  = aws_vpc.main.id
  cidr_block              = each.value.cidr
  availability_zone       = each.value.az
  map_public_ip_on_launch = true  # Public subnet

  tags = {
    Name = each.key
    Zone = "DMZ"
    Tier = "Public"
  }
}

# Internet Gateway (DMZ only)
resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = { Name = "talma-igw" }
}

# ZONE 3: Application - Private Subnets
resource "aws_subnet" "app" {
  for_each = {
    "app-1a" = { cidr = "10.0.10.0/24", az = "us-east-1a" }
    "app-1b" = { cidr = "10.0.11.0/24", az = "us-east-1b" }
  }

  vpc_id                  = aws_vpc.main.id
  cidr_block              = each.value.cidr
  availability_zone       = each.value.az
  map_public_ip_on_launch = false  # ✅ Private

  tags = {
    Name = each.key
    Zone = "Application"
    Tier = "Private"
  }
}

# NAT Gateway (outbound only)
resource "aws_nat_gateway" "main" {
  allocation_id = aws_eip.nat.id
  subnet_id     = aws_subnet.dmz["dmz-1a"].id

  tags = { Name = "talma-nat" }
}

# ZONE 4: Data - Private Subnets
resource "aws_subnet" "data" {
  for_each = {
    "data-1a" = { cidr = "10.0.20.0/24", az = "us-east-1a" }
    "data-1b" = { cidr = "10.0.21.0/24", az = "us-east-1b" }
  }

  vpc_id                  = aws_vpc.main.id
  cidr_block              = each.value.cidr
  availability_zone       = each.value.az
  map_public_ip_on_launch = false

  tags = {
    Name = each.key
    Zone = "Data"
    Tier = "Private"
  }
}

# ZONE 5: Management - Private Subnet
resource "aws_subnet" "mgmt" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.30.0/24"
  availability_zone       = "us-east-1a"
  map_public_ip_on_launch = false

  tags = {
    Name = "mgmt-1a"
    Zone = "Management"
    Tier = "Private"
  }
}
```

## Traffic Control Between Zones

```yaml
# ✅ Security Groups por zona

# DMZ Zone: ALB
resource "aws_security_group" "alb" {
  name        = "alb-sg"
  description = "ALB in DMZ zone"
  vpc_id      = aws_vpc.main.id

  # Inbound: Internet → ALB
  ingress {
    description = "HTTPS from Internet"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  # Public ALB
  }

  # Outbound: ALB → Application Zone
  egress {
    description     = "To ECS tasks"
    from_port       = 8080
    to_port         = 8080
    protocol        = "tcp"
    security_groups = [aws_security_group.ecs.id]  # ✅ Only App Zone
  }

  tags = { Zone = "DMZ" }
}

# Application Zone: ECS Tasks
resource "aws_security_group" "ecs" {
  name        = "ecs-sg"
  description = "ECS tasks in Application zone"
  vpc_id      = aws_vpc.main.id

  # Inbound: ALB → ECS (ONLY from DMZ)
  ingress {
    description     = "From ALB"
    from_port       = 8080
    to_port         = 8080
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
  }

  # Outbound: ECS → Data Zone
  egress {
    description     = "To RDS"
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.rds.id]
  }

  egress {
    description     = "To Redis"
    from_port       = 6379
    to_port         = 6379
    protocol        = "tcp"
    security_groups = [aws_security_group.redis.id]
  }

  # Outbound: Internet (via NAT)
  egress {
    description = "External APIs"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = { Zone = "Application" }
}

# Data Zone: RDS
resource "aws_security_group" "rds" {
  name        = "rds-sg"
  description = "RDS in Data zone"
  vpc_id      = aws_vpc.main.id

  # Inbound: ONLY from Application Zone
  ingress {
    description     = "From ECS"
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.ecs.id]
  }

  # Outbound: DENY ALL (database no necesita outbound)
  # No egress rules = implicit deny all

  tags = { Zone = "Data" }
}

# Management Zone: Bastion
resource "aws_security_group" "bastion" {
  name        = "bastion-sg"
  description = "Bastion in Management zone"
  vpc_id      = aws_vpc.main.id

  # Inbound: ONLY from corporate VPN
  ingress {
    description = "SSH from VPN"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["10.100.0.0/16"]  # ✅ Corporate VPN CIDR
  }

  # Outbound: Puede acceder a todos (admin purposes)
  egress {
    description = "Admin access"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["10.0.0.0/16"]  # ✅ Only VPC
  }

  tags = { Zone = "Management" }
}
```

## Micro-Segmentation

```yaml
# ✅ Segmentación granular (dentro de zona)

# Application Zone: Segregar por servicio

Sales Service Subnet: 10.0.10.0/25 (128 IPs)
  Security Group: solo ALB → Sales Tasks
  Puede llamar: RDS Sales DB

Billing Service Subnet: 10.0.10.128/25 (128 IPs)
  Security Group: solo ALB → Billing Tasks
  Puede llamar: RDS Billing DB

Network Policies (Kubernetes - si se usa):

  apiVersion: networking.k8s.io/v1
  kind: NetworkPolicy
  metadata:
    name: sales-service-policy
    namespace: sales
  spec:
    podSelector:
      matchLabels:
        app: sales-service

    policyTypes:
      - Ingress
      - Egress

    ingress:
      # Solo from API Gateway
      - from:
        - podSelector:
            matchLabels:
              app: api-gateway
        ports:
          - protocol: TCP
            port: 8080

    egress:
      # Solo to Sales DB
      - to:
        - podSelector:
            matchLabels:
              app: sales-db
        ports:
          - protocol: TCP
            port: 5432

      # External APIs (via NAT)
      - to:
        - namespaceSelector: {}
        ports:
          - protocol: TCP
            port: 443
```

## Monitoring & Enforcement

```yaml
# ✅ Monitorear tráfico cross-zone

VPC Flow Logs:

  resource "aws_flow_log" "main" {
    vpc_id          = aws_vpc.main.id
    traffic_type    = "ALL"  # ACCEPT + REJECT
    iam_role_arn    = aws_iam_role.flow_logs.arn
    log_destination = aws_cloudwatch_log_group.flow_logs.arn

    tags = { Name = "vpc-flow-logs" }
  }

CloudWatch Insights Queries:

  # Tráfico rechazado (posibles ataques)
  fields @timestamp, srcAddr, dstAddr, dstPort, action
  | filter action = "REJECT"
  | stats count() by srcAddr, dstPort
  | sort count desc

  # Tráfico inesperado Data → Internet (data exfiltration?)
  fields @timestamp, srcAddr, dstAddr
  | filter srcAddr like /^10\.0\.20\./  # Data subnet
    and dstAddr not like /^10\./         # External
  | count

Alerts:

  1. Unauthorized Cross-Zone Traffic:
     - Data subnet → Internet (CRITICAL)
     - DMZ → Data (bypassing App layer)
     - Action: Alert + auto-block

  2. High Volume Cross-Zone:
     - App → Data > 10GB/hour (unusual)
     - Possible data exfiltration
     - Action: Alert + investigate

  3. Security Group Changes:
     - ModifySecurityGroupRules (0.0.0.0/0)
     - Action: Alert + revert
```

---

## Requisitos Técnicos

### MUST (Obligatorio)

- **MUST** segmentar VPC en mínimo 3 zonas (DMZ, Application, Data)
- **MUST** usar private subnets para backend (no public IPs)
- **MUST** restricción cross-zone con Security Groups
- **MUST** habilitar VPC Flow Logs (ALL traffic)
- **MUST** denegar Data → Internet directo
- **MUST** usar bastion/VPN para management (no SSH público)

### SHOULD (Fuertemente recomendado)

- **SHOULD** implementar micro-segmentation (por servicio)
- **SHOULD** monitorear tráfico cross-zone (CloudWatch Insights)
- **SHOULD** alertar tráfico inusual
- **SHOULD** usar Network ACLs adicionales (defense in depth)

### MUST NOT (Prohibido)

- **MUST NOT** mezclar DMZ y Data en misma subnet
- **MUST NOT** permitir Data subnet acceso internet directo
- **MUST NOT** security groups permissive (0.0.0.0/0 all ports)
- **MUST NOT** flat network (single subnet para todo)

---

## Referencias

- [Lineamiento: Segmentación y Aislamiento](../../lineamientos/seguridad/06-segmentacion-y-aislamiento.md)
- [Network Security](./network-security.md)
- [Environment Isolation](./environment-isolation.md)
- [Virtual Networks](../../estandares/infraestructura/virtual-networks.md)
