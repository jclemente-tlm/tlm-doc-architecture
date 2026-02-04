---
id: network-security
sidebar_position: 30
title: Estándares de Seguridad de Red
---

# Estándares Técnicos — Seguridad de Red

## 1. Propósito

Unificar los estándares para Zero Trust, segmentación de red, zonas de seguridad y límites de confianza en la infraestructura de red corporativa, asegurando defensa en profundidad, autenticación robusta y control estricto de tráfico.

## 2. Alcance

- Comunicación entre servicios y APIs
- Diseño de VPC, subnets y zonas
- Seguridad en boundaries (WAF, API Gateway, Backend, DB)
- Segmentación y micro-segmentación
- Validación y autenticación en cada capa

## 3. Tecnologías Aprobadas

| Componente  | Tecnología             | Versión mínima | Observaciones           |
| :---------- | :--------------------- | :------------- | :---------------------- |
| Network     | AWS VPC                | -              | Multi-tier, 1 VPC/amb.  |
| Firewall    | Security Groups, NACLs | -              | Deny by default         |
| API Gateway | Kong                   | 3.5+           | JWT, request validation |
| Auth        | Keycloak JWT           | 23.0+          | Service accounts        |
| Encryption  | TLS 1.3, mTLS          | -              | Obligatorio             |
| WAF         | AWS WAF                | -              | OWASP Top 10            |
| IaC         | Terraform              | 1.6+           | Automatización          |

## 4. Requisitos Obligatorios

### Principios Zero Trust

- Never trust, always verify
- Least privilege
- Assume breach
- Verify explicitly
- Micro-segmentation

### Segmentación y Zonas

- 1 VPC por ambiente
- Subnets por tier: Public, DMZ, Application, Data
- Security Groups deny-by-default, 1 por servicio
- NACLs por subnet tier, defensa en profundidad
- No 0.0.0.0/0 salvo ALB público
- No IP pública en Application/Data zones

### Boundaries y Validación

- Documentar boundaries en threat model
- Validar y sanitizar todos los inputs
- JWT obligatorio en APIs
- mTLS en servicios críticos
- Autenticación y autorización en cada boundary
- WAF con OWASP Top 10 y rate limiting

### Encriptación

- TLS 1.3 obligatorio
- mTLS para service-to-service
- Encryption in transit siempre

## 5. Ejemplo de Infraestructura (Terraform)

### VPC Multi-Tier y Subnets

```hcl
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true
  tags = { Name = "vpc-production" }
}

resource "aws_subnet" "public" {
  count                   = 2
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.${count.index}.0/24"
  availability_zone       = data.aws_availability_zones.available.names[count.index]
  map_public_ip_on_launch = true
  tags = { Name = "subnet-public-${count.index + 1}", Tier = "public" }
}

resource "aws_subnet" "dmz" {
  count             = 2
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.${10 + count.index}.0/24"
  availability_zone = data.aws_availability_zones.available.names[count.index]
  tags = { Name = "subnet-dmz-${count.index + 1}", Tier = "dmz" }
}

resource "aws_subnet" "application" {
  count             = 2
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.${20 + count.index}.0/24"
  availability_zone = data.aws_availability_zones.available.names[count.index]
  tags = { Name = "subnet-app-${count.index + 1}", Tier = "application" }
}

resource "aws_subnet" "data" {
  count             = 2
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.${30 + count.index}.0/24"
  availability_zone = data.aws_availability_zones.available.names[count.index]
  tags = { Name = "subnet-data-${count.index + 1}", Tier = "data" }
}
```

### Security Groups (Deny by Default)

```hcl
resource "aws_security_group" "alb" {
  name        = "prod-alb-sg"
  description = "ALB público"
  vpc_id      = aws_vpc.main.id
  ingress { from_port = 443, to_port = 443, protocol = "tcp", cidr_blocks = ["0.0.0.0/0"] }
  egress  { from_port = 8080, to_port = 8080, protocol = "tcp", security_groups = [aws_security_group.kong.id] }
}

resource "aws_security_group" "kong" {
  name        = "prod-kong-sg"
  description = "Kong API Gateway"
  vpc_id      = aws_vpc.main.id
  ingress { from_port = 8443, to_port = 8443, protocol = "tcp", security_groups = [aws_security_group.alb.id] }
  egress  { from_port = 8080, to_port = 8080, protocol = "tcp", security_groups = [aws_security_group.backend.id] }
}

resource "aws_security_group" "backend" {
  name        = "prod-backend-sg"
  description = "Backend Services"
  vpc_id      = aws_vpc.main.id
  ingress { from_port = 8080, to_port = 8080, protocol = "tcp", security_groups = [aws_security_group.kong.id] }
  egress  { from_port = 5432, to_port = 5432, protocol = "tcp", security_groups = [aws_security_group.postgres.id] }
  egress  { from_port = 6379, to_port = 6379, protocol = "tcp", security_groups = [aws_security_group.redis.id] }
  egress  { from_port = 443, to_port = 443, protocol = "tcp", cidr_blocks = ["0.0.0.0/0"] }
}

resource "aws_security_group" "postgres" {
  name        = "prod-postgres-sg"
  description = "PostgreSQL RDS"
  vpc_id      = aws_vpc.main.id
  ingress { from_port = 5432, to_port = 5432, protocol = "tcp", security_groups = [aws_security_group.backend.id] }
}
```

### NACLs y Routing Tables

```hcl
resource "aws_network_acl" "public" {
  vpc_id     = aws_vpc.main.id
  subnet_ids = aws_subnet.public[*].id
  ingress { rule_no = 100, protocol = "tcp", action = "allow", cidr_block = "0.0.0.0/0", from_port = 443, to_port = 443 }
  ingress { rule_no = 110, protocol = "tcp", action = "allow", cidr_block = "0.0.0.0/0", from_port = 1024, to_port = 65535 }
  egress  { rule_no = 100, protocol = "-1", action = "allow", cidr_block = "0.0.0.0/0", from_port = 0, to_port = 0 }
}
```

## 6. Validación y Cumplimiento

- Verificar VPC, subnets y SGs existen y cumplen deny-by-default
- No hay 0.0.0.0/0 salvo ALB público
- WAF habilitado en ALB
- JWT obligatorio en APIs
- mTLS en servicios críticos
- Validar inputs y sanitizar outputs
- Usuarios DB con least privilege y conexión cifrada

## 7. Ejemplo de Validación

```bash
# Verificar Security Groups tienen deny-by-default
aws ec2 describe-security-groups --region us-east-1 --query 'SecurityGroups[?length(IpPermissions)==`0`].[GroupId,GroupName]' --output table

# Verificar servicios expuestos NO tienen IP pública
aws ec2 describe-instances --region us-east-1 --filters "Name=tag:Service,Values=backend" --query 'Reservations[].Instances[?PublicIpAddress!=null].[InstanceId,PublicIpAddress]'

# Test: Request sin JWT debe fallar
curl -i https://api.talma.com/payments
# Esperado: HTTP/1.1 401 Unauthorized

# Verificar WAF habilitado en ALB
aws wafv2 list-web-acls --scope REGIONAL --region us-east-1
```

## 8. Referencias

- [NIST 800-207 Zero Trust Architecture](https://csrc.nist.gov/publications/detail/sp/800-207/final)
- [AWS VPC Security Best Practices](https://docs.aws.amazon.com/vpc/latest/userguide/vpc-security-best-practices.html)
- [OWASP Threat Modeling](https://owasp.org/www-community/Threat_Modeling)
- [OWASP Input Validation](https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html)
