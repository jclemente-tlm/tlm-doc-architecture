---
id: environment-parity
sidebar_position: 7
title: Paridad de Ambientes
description: Estándares para mantener dev, staging y producción lo más similares posible, evitando discrepancias de tecnología y configuración que generan bugs exclusivos de producción.
tags: [infraestructura, configuracion, ambientes, docker, 12factor]
---

# Paridad de Ambientes

## Contexto

Minimizar las diferencias entre los ambientes de desarrollo, staging y producción para eliminar bugs que solo aparecen en producción. Aplica el principio [XII-Factor Dev/Prod Parity](https://12factor.net/dev-prod-parity) y complementa el lineamiento [Infraestructura como Código](../../lineamientos/operabilidad/02-infraestructura-como-codigo.md).

**Conceptos incluidos:**

- **Environment Parity** → Misma tecnología y versiones en todos los ambientes
- **Implementación Integrada** → Ejemplo completo end-to-end de configuración consistente

---

## Stack Tecnológico

| Componente        | Tecnología | Versión | Uso                             |
| ----------------- | ---------- | ------- | ------------------------------- |
| **Runtime**       | .NET       | 8.0     | Misma versión en todos los envs |
| **Base de datos** | PostgreSQL | 15+     | Misma versión dev/staging/prod  |
| **Cache**         | Redis      | 7+      | Misma versión en todos los envs |
| **Containers**    | Docker     | 24+     | Empaquetado consistente         |
| **IaC**           | Terraform  | 1.7+    | Reproducibilidad de ambientes   |

---

## Environment Parity

Principio de mantener ambientes de desarrollo, staging y producción lo más similares posible para minimizar sorpresas en deployment.

**XII-Factor: tres gaps a minimizar:**

1. **Time gap** — Deploy frecuente (horas, no meses)
2. **Personnel gap** — Developers involucrados en deployment
3. **Tools gap** — Mismas tecnologías dev/staging/prod

### Estado actual de paridad

| Dimensión         | Dev                    | Staging                 | Producción              | Paridad               |
| ----------------- | ---------------------- | ----------------------- | ----------------------- | --------------------- |
| **Base de Datos** | PostgreSQL 15 (Docker) | PostgreSQL 15 (RDS)     | PostgreSQL 15 (RDS)     | ✅ Misma versión      |
| **Cache**         | Redis 7 (Docker)       | Redis 7 (ElastiCache)   | Redis 7 (ElastiCache)   | ✅ Misma versión      |
| **Messaging**     | Kafka 3.6 (Docker)     | Kafka 3.6 (EC2 cluster) | Kafka 3.6 (EC2 cluster) | ✅ Misma versión      |
| **Runtime**       | .NET 8 (local)         | .NET 8 (ECS Fargate)    | .NET 8 (ECS Fargate)    | ✅ Misma versión      |
| **Container**     | Docker 24              | Docker 24 (ECS)         | Docker 24 (ECS)         | ✅ Misma imagen       |
| **Secrets**       | docker-compose env     | AWS Secrets Manager     | AWS Secrets Manager     | ⚠️ Mecanismo distinto |
| **Observability** | Console logs           | Grafana Stack           | Grafana Stack           | ⚠️ Dev simplificado   |

**Objetivo: 80-90% paridad** (100% no es necesario ni viable)

### Antipatrón: SQLite en Dev, PostgreSQL en Prod

```csharp
// ❌ ANTIPATRÓN: Diferentes bases de datos por ambiente
// appsettings.Development.json
{
  "ConnectionStrings": {
    "CustomerDb": "Data Source=customers.db"  // SQLite
  }
}

// appsettings.Production.json
{
  "ConnectionStrings": {
    "CustomerDb": "Host=prod-db;..."  // PostgreSQL
  }
}

// Problemas:
// 1. Queries funcionan en SQLite pero fallan en PostgreSQL (sintaxis diferente)
// 2. Constraints diferentes (foreign keys, unique indexes)
// 3. Performance characteristics completamente distintas
// 4. Bug encontrado en prod, no reproducible en dev
```

### Best Practice: Misma tecnología con Docker

```yaml
# docker-compose.yml — Mismas versiones que staging/prod
services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: customers_dev
      POSTGRES_USER: dev
      POSTGRES_PASSWORD: dev
    ports:
      - "5432:5432"

  redis:
    image: redis:7
    ports:
      - "6379:6379"

  kafka:
    image: apache/kafka:3.6.0
    environment:
      KAFKA_NODE_ID: 1
      KAFKA_PROCESS_ROLES: broker,controller
      KAFKA_LISTENERS: PLAINTEXT://0.0.0.0:9092,CONTROLLER://0.0.0.0:9093
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:9092
      KAFKA_CONTROLLER_LISTENER_NAMES: CONTROLLER
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: CONTROLLER:PLAINTEXT,PLAINTEXT:PLAINTEXT
      KAFKA_CONTROLLER_QUORUM_VOTERS: 1@kafka:9093
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
    ports:
      - "9092:9092"
```

### Diferencias aceptables (quantitative, no qualitative)

| Aspecto             | Dev                   | Prod                  | Justificación                     |
| ------------------- | --------------------- | --------------------- | --------------------------------- |
| **Log Level**       | Debug                 | Warning               | Dev necesita más detalle          |
| **Data Volume**     | Subset pequeño        | Full dataset          | Dev no necesita millones de filas |
| **Resource Limits** | CPU: 1 core, RAM: 2GB | CPU: 4 core, RAM: 8GB | Prod necesita más capacidad       |
| **Replication**     | Single instance       | Multi-AZ replica      | Prod necesita HA                  |
| **Backups**         | No automated          | Daily snapshots       | Prod necesita disaster recovery   |

**Regla:** Diferencias deben ser **cuantitativas** (escala), no **cualitativas** (tecnología).

---

## Implementación Integrada

Ejemplo completo: customer-service con configuración consistente end-to-end.

### 1. Terraform — Provisioning de Config por Ambiente

```hcl
# terraform/environments/production/main.tf

module "configuration" {
  source = "../../modules/configuration"

  service_name = "customer-service"
  environment  = "production"
  aws_region   = "us-east-1"

  # Non-sensitive config (Parameter Store)
  parameters = {
    "resilience/retry-attempts"            = "3"
    "resilience/timeout-seconds"           = "30"
    "resilience/circuit-breaker-threshold" = "5"
    "features/enable-advanced-search"      = "true"
    "features/enable-cache"                = "true"
    "cache/host" = aws_elasticache_cluster.redis.cache_nodes[0].address
    "cache/port" = "6379"
  }

  # Sensitive config (Secrets Manager)
  secrets = {
    "database/credentials" = jsonencode({
      username         = "customer_svc"
      password         = random_password.db_password.result
      host             = aws_db_instance.customer_db.address
      port             = aws_db_instance.customer_db.port
      dbname           = "customers"
      connectionString = "Host=${aws_db_instance.customer_db.address};..."
    })
    "external-api/api-key" = var.external_api_key
  }
}
```

### 2. Aplicación .NET 8 — Consumo de Config

```csharp
// Program.cs
var builder = WebApplication.CreateBuilder(args);

builder.Configuration
    .AddJsonFile("appsettings.json", optional: false, reloadOnChange: true)
    .AddJsonFile($"appsettings.{builder.Environment.EnvironmentName}.json", optional: true)
    .AddEnvironmentVariables();

builder.Services.Configure<ResilienceSettings>(builder.Configuration.GetSection("Resilience"));
builder.Services.Configure<FeatureSettings>(builder.Configuration.GetSection("Features"));

var connectionString = builder.Configuration.GetConnectionString("CustomerDb");
builder.Services.AddDbContext<CustomerDbContext>(options => options.UseNpgsql(connectionString));

var app = builder.Build();
app.Run();
```

```csharp
// Settings/ResilienceSettings.cs
public class ResilienceSettings
{
    public int RetryAttempts { get; set; } = 3;
    public int TimeoutSeconds { get; set; } = 30;
    public int CircuitBreakerThreshold { get; set; } = 5;
}
```

### 3. Estructura de Keys consistente en todos los ambientes

```bash
# Las keys son idénticas, solo cambian los valores

# Development (docker-compose):
ConnectionStrings__CustomerDb=Host=localhost;Database=customers_dev;...
Resilience__RetryAttempts=3

# Staging (ECS Task Definition):
ConnectionStrings__CustomerDb=Host=staging-db;Database=customers_staging;...
Resilience__RetryAttempts=3

# Production (ECS Task Definition):
ConnectionStrings__CustomerDb=Host=prod-db;Database=customers;...
Resilience__RetryAttempts=3
```

### 4. Parity Checklist

```markdown
## Environment Parity Checklist

- [ ] PostgreSQL misma versión (15) en dev/staging/prod
- [ ] Redis misma versión (7) en todos los ambientes
- [ ] Kafka misma versión (3.6) en todos los ambientes
- [ ] .NET 8 en todos los ambientes
- [ ] Misma imagen base Docker (mcr.microsoft.com/dotnet/aspnet:8.0)
- [ ] Mismos keys de config en todos los ambientes (valores diferentes OK)
- [ ] Structured JSON logs (Serilog) en todos los ambientes
- [ ] OpenTelemetry instrumentado igual dev/staging/prod
- [ ] Misma imagen Docker promovida dev → staging → prod
```

---

## Requisitos Técnicos

### MUST (Obligatorio)

- **MUST** usar misma versión de base de datos en dev/staging/prod (PostgreSQL 15)
- **MUST** usar misma versión de .NET en todos los ambientes (.NET 8)
- **MUST** usar Docker containers para dependencies en desarrollo (no instancias locales nativas)
- **MUST** promover misma imagen Docker desde staging a producción (solo cambia el tag)
- **MUST** mantener estructura de keys de configuración idéntica en todos los ambientes

### SHOULD (Fuertemente recomendado)

- **SHOULD** usar AWS Secrets Manager también en staging (no solo en producción)
- **SHOULD** documentar diferencias aceptables entre ambientes (cuantitativas, no cualitativas)
- **SHOULD** correr integration tests con Testcontainers usando mismas versiones de imágenes

### MAY (Opcional)

- **MAY** usar AWS AppConfig para feature flags distintos por ambiente con gestión centralizada

### MUST NOT (Prohibido)

- **MUST NOT** usar diferentes tecnologías de base de datos entre ambientes (SQLite dev, PostgreSQL prod)
- **MUST NOT** introducir diferencias cualitativas de tecnología entre ambientes sin justificación documentada

---

## Referencias

- [XII-Factor — X. Dev/prod parity](https://12factor.net/dev-prod-parity) — principio de paridad entre ambientes
- [XII-Factor — III. Config](https://12factor.net/config) — externalización de configuración
- [Externalización de Configuración](./configuration-management.md) — separación de config del código
- [Configuración Centralizada](./configuration-management.md) — Parameter Store y Secrets Manager
- [Containerización](./containerization.md) — misma imagen Docker en todos los ambientes
- [Infrastructure as Code — Implementación](./iac-standards.md) — reproducibilidad de ambientes con Terraform
