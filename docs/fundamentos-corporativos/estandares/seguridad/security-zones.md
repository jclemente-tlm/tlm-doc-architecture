---
id: security-zones
sidebar_position: 19
title: Zonas de Seguridad
description: Estándar para segmentar red en zonas de seguridad (DMZ, public, private) con Security Groups, NACLs y traffic flow control
---

# Estándar Técnico — Zonas de Seguridad

---

## 1. Propósito

Segmentar red en zonas de seguridad (Internet-facing, DMZ, Application, Data) usando AWS VPC subnets, Security Groups deny-by-default, NACLs y routing tables para controlar traffic flow y limitar blast radius.

---

## 2. Alcance

**Aplica a:**

- Diseño de VPC y subnets
- Security Groups
- Network ACLs
- Routing tables
- Load balancers
- Instancias/contenedores

**No aplica a:**

- Comunicación intra-container (localhost)

---

## 3. Tecnologías Aprobadas

| Componente        | Tecnología                | Versión mínima | Observaciones           |
| ----------------- | ------------------------- | -------------- | ----------------------- |
| **Network**       | AWS VPC                   | -              | Multi-tier architecture |
| **Firewall**      | Security Groups           | -              | Stateful                |
| **Network ACL**   | NACLs                     | -              | Stateless               |
| **Load Balancer** | Application Load Balancer | -              | Internet-facing         |
| **Routing**       | Route Tables              | -              | Traffic control         |

> El uso de tecnologías no listadas requiere aprobación de Arquitectura.

---

## 4. Requisitos Obligatorios 🔴

### Zonas de Seguridad

- [ ] **Public Zone**: ALB (Internet-facing)
- [ ] **DMZ Zone**: Kong API Gateway (public subnet, sin acceso directo desde Internet)
- [ ] **Application Zone**: Backend services (private subnet)
- [ ] **Data Zone**: Databases (private subnet, no Internet)

### Security Groups

- [ ] **Deny by default**: No inbound rules por defecto
- [ ] **Explicit allows**: Solo tráfico necesario
- [ ] **Least privilege**: Mínimos puertos abiertos
- [ ] **NO 0.0.0.0/0**: En inbound (excepto ALB HTTPS:443)

### Network ACLs

- [ ] **Defense in depth**: Segunda capa después de Security Groups
- [ ] **Subnet-level**: Por subnet, no por instancia
- [ ] **Stateless**: Requiere reglas inbound + outbound

### Routing

- [ ] **Internet Gateway**: Solo en public subnets
- [ ] **NAT Gateway**: Para private subnets (outbound only)
- [ ] **NO route to Internet**: Desde data zone

---

## 5. Arquitectura de Zonas

### Diagrama de Red

```text
┌────────────────────────────────────────────────────────────────┐
│  INTERNET                                                      │
└────────────────────────────────────────────────────────────────┘
                           │
                           ▼
        ┌──────────────────────────────────┐
        │   AWS Internet Gateway (IGW)     │
        └──────────────────────────────────┘
                           │
╔══════════════════════════╧════════════════════════════════════╗
║  PUBLIC ZONE (10.0.0.0/24)                                    ║
║  • Application Load Balancer (HTTPS:443)                      ║
║  • NAT Gateway (for private subnet outbound)                  ║
║  • Route: 0.0.0.0/0 → IGW                                     ║
╚═══════════════════════════════════════════════════════════════╝
                           │
                           ▼
╔══════════════════════════════════════════════════════════════╗
║  DMZ ZONE (10.0.10.0/24) - Private Subnet                    ║
║  • Kong API Gateway (ECS Fargate)                            ║
║  • Security Group: Allow 8443 from ALB only                  ║
║  • Route: 0.0.0.0/0 → NAT Gateway (outbound only)            ║
╚══════════════════════════════════════════════════════════════╝
                           │
                           ▼
╔══════════════════════════════════════════════════════════════╗
║  APPLICATION ZONE (10.0.20.0/24) - Private Subnet            ║
║  • Backend Services (.NET APIs on ECS Fargate)               ║
║  • Security Group: Allow 8080 from Kong only                 ║
║  • Route: 0.0.0.0/0 → NAT Gateway (HTTPS external APIs)      ║
╚══════════════════════════════════════════════════════════════╝
                           │
                           ▼
╔══════════════════════════════════════════════════════════════╗
║  DATA ZONE (10.0.30.0/24) - Private DB Subnet                ║
║  • PostgreSQL RDS, Redis (Elasticache)                       ║
║  • Security Group: Allow 5432/6379 from App Zone only        ║
║  • NO route to Internet (no NAT, no IGW)                     ║
╚══════════════════════════════════════════════════════════════╝
```

---

## 6. Terraform - VPC y Subnets

### VPC Multi-Tier

```hcl
# terraform/vpc.tf
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name        = "${var.environment}-vpc"
    Environment = var.environment
  }
}

# Internet Gateway (Public Zone)
resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "${var.environment}-igw"
  }
}

# PUBLIC ZONE (10.0.0.0/24)
resource "aws_subnet" "public" {
  count                   = 2
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.${count.index}.0/24"
  availability_zone       = data.aws_availability_zones.available.names[count.index]
  map_public_ip_on_launch = true

  tags = {
    Name = "${var.environment}-public-subnet-${count.index + 1}"
    Tier = "Public"
  }
}

# DMZ ZONE (10.0.10.0/24)
resource "aws_subnet" "dmz" {
  count             = 2
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.${10 + count.index}.0/24"
  availability_zone = data.aws_availability_zones.available.names[count.index]

  tags = {
    Name = "${var.environment}-dmz-subnet-${count.index + 1}"
    Tier = "DMZ"
  }
}

# APPLICATION ZONE (10.0.20.0/24)
resource "aws_subnet" "application" {
  count             = 2
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.${20 + count.index}.0/24"
  availability_zone = data.aws_availability_zones.available.names[count.index]

  tags = {
    Name = "${var.environment}-app-subnet-${count.index + 1}"
    Tier = "Application"
  }
}

# DATA ZONE (10.0.30.0/24)
resource "aws_subnet" "data" {
  count             = 2
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.${30 + count.index}.0/24"
  availability_zone = data.aws_availability_zones.available.names[count.index]

  tags = {
    Name = "${var.environment}-data-subnet-${count.index + 1}"
    Tier = "Data"
  }
}

# NAT Gateway (en public subnet, para outbound de private subnets)
resource "aws_eip" "nat" {
  domain = "vpc"

  tags = {
    Name = "${var.environment}-nat-eip"
  }
}

resource "aws_nat_gateway" "main" {
  allocation_id = aws_eip.nat.id
  subnet_id     = aws_subnet.public[0].id

  tags = {
    Name = "${var.environment}-nat-gateway"
  }
}
```

---

## 7. Security Groups - Deny by Default

### Public Zone - ALB

```hcl
resource "aws_security_group" "alb" {
  name        = "${var.environment}-alb-sg"
  description = "Application Load Balancer"
  vpc_id      = aws_vpc.main.id

  # Inbound: HTTPS desde Internet
  ingress {
    description = "HTTPS from Internet"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  # ✅ OK: ALB público
  }

  # Outbound: Solo a Kong (DMZ Zone)
  egress {
    description     = "To Kong API Gateway"
    from_port       = 8443
    to_port         = 8443
    protocol        = "tcp"
    security_groups = [aws_security_group.kong.id]
  }

  tags = {
    Name = "${var.environment}-alb-sg"
    Zone = "Public"
  }
}
```

### DMZ Zone - Kong

```hcl
resource "aws_security_group" "kong" {
  name        = "${var.environment}-kong-sg"
  description = "Kong API Gateway (DMZ)"
  vpc_id      = aws_vpc.main.id

  # Inbound: SOLO desde ALB
  ingress {
    description     = "HTTPS from ALB"
    from_port       = 8443
    to_port         = 8443
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
  }

  # Outbound: Solo a backend services (Application Zone)
  egress {
    description     = "To Backend Services"
    from_port       = 8080
    to_port         = 8080
    protocol        = "tcp"
    security_groups = [aws_security_group.backend.id]
  }

  tags = {
    Name = "${var.environment}-kong-sg"
    Zone = "DMZ"
  }
}
```

### Application Zone - Backend

```hcl
resource "aws_security_group" "backend" {
  name        = "${var.environment}-backend-sg"
  description = "Backend Services (Application Zone)"
  vpc_id      = aws_vpc.main.id

  # Inbound: SOLO desde Kong
  ingress {
    description     = "HTTP from Kong"
    from_port       = 8080
    to_port         = 8080
    protocol        = "tcp"
    security_groups = [aws_security_group.kong.id]
  }

  # Outbound: A PostgreSQL y Redis (Data Zone)
  egress {
    description     = "To PostgreSQL"
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.postgres.id]
  }

  egress {
    description     = "To Redis"
    from_port       = 6379
    to_port         = 6379
    protocol        = "tcp"
    security_groups = [aws_security_group.redis.id]
  }

  # Outbound: HTTPS para APIs externas
  egress {
    description = "HTTPS to Internet"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.environment}-backend-sg"
    Zone = "Application"
  }
}
```

### Data Zone - PostgreSQL

```hcl
resource "aws_security_group" "postgres" {
  name        = "${var.environment}-postgres-sg"
  description = "PostgreSQL RDS (Data Zone)"
  vpc_id      = aws_vpc.main.id

  # Inbound: SOLO desde Backend
  ingress {
    description     = "PostgreSQL from Backend"
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.backend.id]
  }

  # NO egress rules (no necesita salir)

  tags = {
    Name = "${var.environment}-postgres-sg"
    Zone = "Data"
  }
}
```

---

## 8. Routing Tables

### Public Subnet Route Table

```hcl
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  # Route a Internet via IGW
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }

  tags = {
    Name = "${var.environment}-public-rt"
  }
}

resource "aws_route_table_association" "public" {
  count          = 2
  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}
```

### Private Subnet Route Table (DMZ, Application)

```hcl
resource "aws_route_table" "private" {
  vpc_id = aws_vpc.main.id

  # Route a Internet via NAT Gateway (outbound only)
  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.main.id
  }

  tags = {
    Name = "${var.environment}-private-rt"
  }
}

resource "aws_route_table_association" "dmz" {
  count          = 2
  subnet_id      = aws_subnet.dmz[count.index].id
  route_table_id = aws_route_table.private.id
}

resource "aws_route_table_association" "application" {
  count          = 2
  subnet_id      = aws_subnet.application[count.index].id
  route_table_id = aws_route_table.private.id
}
```

### Data Subnet Route Table (NO Internet)

```hcl
resource "aws_route_table" "data" {
  vpc_id = aws_vpc.main.id

  # NO route to Internet (ni IGW ni NAT)
  # Solo VPC local traffic

  tags = {
    Name = "${var.environment}-data-rt"
  }
}

resource "aws_route_table_association" "data" {
  count          = 2
  subnet_id      = aws_subnet.data[count.index].id
  route_table_id = aws_route_table.data.id
}
```

---

## 9. Validación de Cumplimiento

```bash
# Verificar VPC existe
aws ec2 describe-vpcs --filters "Name=tag:Environment,Values=production"

# Listar subnets por tier
aws ec2 describe-subnets \
  --filters "Name=tag:Tier,Values=Data" \
  --query 'Subnets[*].[SubnetId,CidrBlock,AvailabilityZone]' \
  --output table

# Verificar NO hay instancias con IP pública en Application/Data zones
aws ec2 describe-instances \
  --filters "Name=subnet-id,Values=$(aws ec2 describe-subnets --filters 'Name=tag:Tier,Values=Application' --query 'Subnets[0].SubnetId' --output text)" \
  --query 'Reservations[].Instances[?PublicIpAddress!=null].[InstanceId,PublicIpAddress]'
# Esperado: Sin resultados

# Verificar Security Groups tienen deny-by-default
aws ec2 describe-security-groups \
  --filters "Name=tag:Zone,Values=Data" \
  --query 'SecurityGroups[*].[GroupId,IpPermissions]'
# Esperado: Solo reglas específicas, no 0.0.0.0/0 en inbound
```

---

## 10. Referencias

**AWS:**

- [VPC Security Best Practices](https://docs.aws.amazon.com/vpc/latest/userguide/vpc-security-best-practices.html)
- [Security Groups vs NACLs](https://docs.aws.amazon.com/vpc/latest/userguide/VPC_Security.html)

**NIST:**

- [NIST 800-41 Firewall Guidelines](https://csrc.nist.gov/publications/detail/sp/800-41/rev-1/final)
