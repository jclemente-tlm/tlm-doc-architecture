---
id: cloud-cost-optimization
sidebar_position: 3
title: Optimización de Costos en Cloud
description: Estrategias para optimizar costos de infraestructura cloud sin comprometer performance
---

# Optimización de Costos en Cloud

## Contexto

Este estándar define estrategias para optimizar costos de infraestructura AWS mientras se mantiene performance, disponibilidad y escalabilidad. Complementa el [lineamiento de Cloud Native](../../lineamientos/arquitectura/03-cloud-native.md) implementando **eficiencia económica** en arquitecturas cloud.

---

## Stack Tecnológico

| Componente     | Tecnología             | Versión | Uso                     |
| -------------- | ---------------------- | ------- | ----------------------- |
| **Compute**    | AWS ECS Fargate Spot   | -       | Compute con ahorro 70%  |
| **Database**   | RDS Reserved Instances | -       | DB con ahorro 40-60%    |
| **Cache**      | ElastiCache Reserved   | -       | Cache con ahorro 40-55% |
| **Storage**    | S3 Intelligent-Tiering | -       | Storage automático      |
| **Monitoring** | AWS Cost Explorer      | -       | Cost analytics          |
| **Budgets**    | AWS Budgets            | -       | Alertas de costo        |

---

## Implementación Técnica

### ECS Fargate Spot (Ahorro ~70%)

```hcl
# ✅ Fargate Spot para workloads tolerantes a interrupciones

resource "aws_ecs_service" "orders_worker" {
  name            = "orders-worker"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.orders_worker.arn
  desired_count   = 3

  # ✅ Capacity provider strategy: mix Spot + On-Demand
  capacity_provider_strategy {
    capacity_provider = "FARGATE_SPOT"
    weight            = 80  # ✅ 80% en Spot
    base              = 0
  }

  capacity_provider_strategy {
    capacity_provider = "FARGATE"
    weight            = 20  # ✅ 20% en On-Demand (baseline)
    base              = 1   # ✅ Mínimo 1 on-demand siempre
  }

  # ✅ Para APIs críticas: 100% On-Demand
  # capacity_provider_strategy {
  #   capacity_provider = "FARGATE"
  #   weight            = 100
  # }
}

# Ahorro:
# - Fargate On-Demand: $0.04048/vCPU-hour + $0.004445/GB-hour
# - Fargate Spot: ~70% descuento
# Ejemplo: Task 0.5 vCPU, 1 GB = $0.03/hour → $0.009/hour con Spot
```

### Auto Scaling Agresivo

```hcl
# ✅ Scale down agresivo fuera de horas pico

resource "aws_appautoscaling_target" "orders_api" {
  max_capacity       = 10
  min_capacity       = 2  # ✅ Mínimo 2 para HA
  resource_id        = "service/${aws_ecs_cluster.main.name}/${aws_ecs_service.orders_api.name}"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"
}

# ✅ Target tracking: CPU 70%
resource "aws_appautoscaling_policy" "orders_api_cpu" {
  name               = "orders-api-cpu"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.orders_api.resource_id
  scalable_dimension = aws_appautoscaling_target.orders_api.scalable_dimension
  service_namespace  = aws_appautoscaling_target.orders_api.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageCPUUtilization"
    }

    target_value = 70.0  # ✅ 70% CPU utilization goal

    # ✅ Scale in/out agresivo
    scale_in_cooldown  = 60   # 1 min
    scale_out_cooldown = 30   # 30 sec
  }
}

# ✅ Scheduled scaling: reducir durante noche/fins de semana
resource "aws_appautoscaling_scheduled_action" "scale_down_night" {
  name               = "scale-down-night"
  service_namespace  = aws_appautoscaling_target.orders_api.service_namespace
  resource_id        = aws_appautoscaling_target.orders_api.resource_id
  scalable_dimension = aws_appautoscaling_target.orders_api.scalable_dimension

  schedule = "cron(0 23 * * ? *)"  # 11 PM UTC

  scalable_target_action {
    min_capacity = 1  # ✅ Reducir a 1 durante noche
    max_capacity = 5
  }
}

resource "aws_appautoscaling_scheduled_action" "scale_up_morning" {
  name               = "scale-up-morning"
  service_namespace  = aws_appautoscaling_target.orders_api.service_namespace
  resource_id        = aws_appautoscaling_target.orders_api.resource_id
  scalable_dimension = aws_appautoscaling_target.orders_api.scalable_dimension

  schedule = "cron(0 6 * * ? *)"  # 6 AM UTC

  scalable_target_action {
    min_capacity = 2
    max_capacity = 10
  }
}
```

### Right-Sizing Compute

```hcl
# ✅ Ajustar CPU/Memory según uso real

# ❌ Over-provisioned
resource "aws_ecs_task_definition" "orders_api_oversized" {
  cpu    = "1024"  # 1 vCPU
  memory = "2048"  # 2 GB
  # Uso real: 20% CPU, 512 MB RAM → desperdicio 80% CPU, 75% RAM
}

# ✅ Right-sized basado en métricas
resource "aws_ecs_task_definition" "orders_api" {
  cpu    = "256"   # 0.25 vCPU
  memory = "512"   # 0.5 GB
  # Uso real: 80% CPU, 400 MB RAM → eficiente

  # ✅ Si necesita más, scale horizontally (más tasks)
  # No scale vertically (tasks más grandes)
}

# Ahorro:
# - Oversized: $0.03/hour
# - Right-sized: $0.0075/hour
# - Ahorro: 75% = $22.50/día por task
```

### RDS Reserved Instances (Ahorro 40-60%)

```hcl
# ✅ Reserved Instances para DB productiva

# On-Demand pricing:
# - db.t4g.medium: $0.064/hour = $561/year

# Reserved Instance (1 year, All Upfront):
# - db.t4g.medium: $330/year
# - Ahorro: 41%

# Reserved Instance (3 years, All Upfront):
# - db.t4g.medium: $620/3 years = $207/year
# - Ahorro: 63%

resource "aws_db_instance" "orders_db" {
  identifier     = "orders-db-prod"
  instance_class = "db.t4g.medium"  # ✅ ARM Graviton2 (20% más barato)
  engine         = "postgres"
  engine_version = "15.4"

  allocated_storage     = 100
  max_allocated_storage = 500  # ✅ Storage auto-scaling
  storage_type          = "gp3"  # ✅ gp3 más barato que gp2

  # ✅ Comprar RI manualmente desde AWS Console
  # No hay recurso Terraform para RI purchase
}

# Storage:
# - gp2: $0.10/GB-month
# - gp3: $0.08/GB-month + IOPS/throughput configurable
# - Ahorro gp3: 20%
```

### ElastiCache Reserved Instances

```hcl
# ✅ Reserved Instances para cache

# On-Demand:
# - cache.t4g.medium: $0.068/hour = $596/year

# Reserved (1 year):
# - cache.t4g.medium: $359/year (40% ahorro)

# Reserved (3 years):
# - cache.t4g.medium: $224/year (62% ahorro)

resource "aws_elasticache_replication_group" "redis" {
  replication_group_id = "orders-cache"
  description          = "Orders API cache"

  node_type            = "cache.t4g.medium"  # ✅ Graviton2
  num_cache_clusters   = 2

  parameter_group_name = "default.redis7"
  port                 = 6379

  automatic_failover_enabled = true
  multi_az_enabled          = true
}
```

### S3 Intelligent-Tiering

```hcl
# ✅ S3 Intelligent-Tiering: ahorro automático

resource "aws_s3_bucket" "documents" {
  bucket = "talma-orders-documents"
}

# ✅ Lifecycle policy: Intelligent-Tiering
resource "aws_s3_bucket_lifecycle_configuration" "documents" {
  bucket = aws_s3_bucket.documents.id

  rule {
    id     = "intelligent-tiering"
    status = "Enabled"

    transition {
      days          = 0  # ✅ Inmediato
      storage_class = "INTELLIGENT_TIERING"
    }
  }

  rule {
    id     = "delete-old-logs"
    status = "Enabled"

    filter {
      prefix = "logs/"
    }

    expiration {
      days = 90  # ✅ Eliminar logs después de 90 días
    }
  }

  rule {
    id     = "archive-old-documents"
    status = "Enabled"

    filter {
      prefix = "archive/"
    }

    transition {
      days          = 365  # ✅ Después de 1 año
      storage_class = "GLACIER"
    }
  }
}

# Pricing:
# - S3 Standard: $0.023/GB
# - S3 Intelligent-Tiering Frequent: $0.023/GB
# - S3 Intelligent-Tiering Infrequent: $0.0125/GB (46% ahorro)
# - S3 Glacier: $0.004/GB (83% ahorro)
```

### CloudWatch Logs Retention

```hcl
# ✅ Reducir retention de logs para ahorrar

resource "aws_cloudwatch_log_group" "orders_api" {
  name              = "/ecs/orders-api"
  retention_in_days = 30  # ✅ 30 días (no indefinido)

  # Pricing:
  # - Ingestion: $0.50/GB
  # - Storage: $0.03/GB-month
  # Ejemplo: 100 GB/mes → $50 ingestion + $3 storage = $53/month
  # Con 7 días retention: $50 + $0.70 = $50.70/month (ahorro menor)
}

# ✅ Export a S3 para long-term storage (más barato)
resource "aws_cloudwatch_log_subscription_filter" "export_to_s3" {
  name            = "export-to-s3"
  log_group_name  = aws_cloudwatch_log_group.orders_api.name
  filter_pattern  = ""  # Todos los logs
  destination_arn = aws_kinesis_firehose_delivery_stream.logs_to_s3.arn
}

resource "aws_kinesis_firehose_delivery_stream" "logs_to_s3" {
  name        = "logs-to-s3"
  destination = "extended_s3"

  extended_s3_configuration {
    role_arn   = aws_iam_role.firehose.arn
    bucket_arn = aws_s3_bucket.logs_archive.arn
    prefix     = "logs/year=!{timestamp:yyyy}/month=!{timestamp:MM}/day=!{timestamp:dd}/"

    # ✅ Compression para reducir storage
    compression_format = "GZIP"
  }
}

# Long-term storage cost:
# - CloudWatch: $0.03/GB-month
# - S3 (compressed): ~$0.008/GB-month (3.75x más barato)
```

### NAT Gateway Optimization

```hcl
# ✅ NAT Gateway caro: $0.045/hour + $0.045/GB processed
# = $32.40/month + data transfer

# Opción 1: VPC Endpoints (sin NAT Gateway para AWS services)
resource "aws_vpc_endpoint" "s3" {
  vpc_id       = aws_vpc.main.id
  service_name = "com.amazonaws.us-east-1.s3"

  route_table_ids = [aws_route_table.private.id]

  # ✅ Sin costo adicional para S3/DynamoDB
}

resource "aws_vpc_endpoint" "secretsmanager" {
  vpc_id            = aws_vpc.main.id
  service_name      = "com.amazonaws.us-east-1.secretsmanager"
  vpc_endpoint_type = "Interface"

  subnet_ids         = aws_subnet.private[*].id
  security_group_ids = [aws_security_group.vpc_endpoints.id]

  # ✅ $0.01/hour = $7.20/month (vs NAT $32.40/month)
}

# Opción 2: NAT Instance (más barato que NAT Gateway)
# - t4g.nano NAT instance: $0.0042/hour = $3/month
# - vs NAT Gateway: $32.40/month
# - Ahorro: 91%
# ⚠️ Trade-off: menos throughput, requiere management
```

### Data Transfer Optimization

```yaml
# ✅ Minimizar data transfer entre AZs y regiones

# Costs:
# - Within same AZ: FREE
# - Between AZs: $0.01/GB
# - Between Regions: $0.02/GB
# - To Internet: $0.09/GB (first 10 TB)

# ✅ Strategies:
1. Colocar servicios relacionados en misma AZ (cuando sea posible)
2. Usar CloudFront para cachear assets estáticos
3. Comprimir responses (gzip)
4. Optimizar payloads (GraphQL vs REST)
```

### CloudFront para Cacheo

```hcl
# ✅ CloudFront reduce data transfer costs

resource "aws_cloudfront_distribution" "api" {
  enabled = true

  origin {
    domain_name = aws_lb.api.dns_name
    origin_id   = "api-alb"

    custom_origin_config {
      http_port              = 80
      https_port             = 443
      origin_protocol_policy = "https-only"
      origin_ssl_protocols   = ["TLSv1.2"]
    }
  }

  default_cache_behavior {
    target_origin_id       = "api-alb"
    viewer_protocol_policy = "redirect-to-https"

    allowed_methods = ["GET", "HEAD", "OPTIONS"]
    cached_methods  = ["GET", "HEAD"]

    # ✅ Cache estático 1 día
    min_ttl     = 0
    default_ttl = 86400
    max_ttl     = 31536000

    forwarded_values {
      query_string = false
      cookies {
        forward = "none"
      }
    }
  }

  price_class = "PriceClass_100"  # ✅ Solo US, Canada, Europe

  restrictions {
    geo_restriction {
      restriction_type = "whitelist"
      locations        = ["US", "CA", "PE", "CL", "CO"]  # ✅ Solo países necesarios
    }
  }
}

# Savings:
# - Direct from ALB: $0.09/GB
# - Via CloudFront: $0.085/GB (first 10 TB)
# - Cache hit ratio 80% → effective cost: $0.017/GB (80% ahorro)
```

### AWS Budgets & Alertas

```hcl
# ✅ Budget alerts para prevenir over-spending

resource "aws_budgets_budget" "monthly_cost" {
  name         = "monthly-cost-budget"
  budget_type  = "COST"
  limit_amount = "5000"
  limit_unit   = "USD"
  time_unit    = "MONTHLY"

  notification {
    comparison_operator        = "GREATER_THAN"
    threshold                  = 80
    threshold_type             = "PERCENTAGE"
    notification_type          = "FORECASTED"
    subscriber_email_addresses = ["platform-team@talma.com"]
  }

  notification {
    comparison_operator        = "GREATER_THAN"
    threshold                  = 100
    threshold_type             = "PERCENTAGE"
    notification_type          = "ACTUAL"
    subscriber_email_addresses = ["platform-team@talma.com", "cto@talma.com"]
  }
}

resource "aws_budgets_budget" "service_budget" {
  name         = "orders-api-budget"
  budget_type  = "COST"
  limit_amount = "500"
  limit_unit   = "USD"
  time_unit    = "MONTHLY"

  cost_filter {
    name   = "Service"
    values = ["Amazon Elastic Container Service"]
  }

  cost_filter {
    name   = "TagKeyValue"
    values = ["user:Application$orders-api"]
  }
}
```

### Cost Allocation Tags

```hcl
# ✅ Tags para tracking de costos

resource "aws_ecs_service" "orders_api" {
  # ...

  tags = {
    Application = "orders-api"
    Environment = "production"
    Team        = "platform"
    CostCenter  = "engineering"
    ManagedBy   = "terraform"
  }

  propagate_tags = "SERVICE"  # ✅ Propagar a tasks
}

# ✅ Activar cost allocation tags en AWS Console:
# - Billing → Cost Allocation Tags → Activate tags
# - Esperar 24h para que aparezcan en Cost Explorer
```

### Métricas de Costo

```csharp
// ✅ Monitorear costo por request (unit economics)

public class CostMetrics
{
    private readonly Counter<double> _estimatedCost;

    public CostMetrics(IMeterFactory meterFactory)
    {
        var meter = meterFactory.Create("Talma.Cost");

        _estimatedCost = meter.CreateCounter<double>(
            "estimated_cost", "USD",
            "Estimated cost of operation");
    }

    public void RecordComputeCost(TimeSpan duration)
    {
        // ✅ Fargate cost: $0.04048/vCPU-hour
        var costPerSecond = 0.04048 / 3600;  // $0.00001124/second
        var cost = duration.TotalSeconds * costPerSecond;

        _estimatedCost.Add(cost,
            new KeyValuePair<string, object?>("resource", "compute"));
    }

    public void RecordStorageCost(long bytes)
    {
        // ✅ S3 cost: $0.023/GB-month
        var costPerByte = 0.023 / (1024 * 1024 * 1024);  // Per byte per month
        var costPerDay = costPerByte * bytes / 30;

        _estimatedCost.Add(costPerDay,
            new KeyValuePair<string, object?>("resource", "storage"));
    }
}

// Dashboard:
// - Cost per request: sum(estimated_cost) / sum(http_requests_total)
// - Cost by resource: sum(estimated_cost) by (resource)
// - Monthly projection: sum(estimated_cost) * 30
```

---

## Requisitos Técnicos

### MUST (Obligatorio)

- **MUST** usar Fargate Spot para workloads no críticos (70% ahorro)
- **MUST** implementar auto-scaling agresivo (scale down rápido)
- **MUST** right-size compute basado en métricas reales
- **MUST** configurar S3 lifecycle policies (Intelligent-Tiering)
- **MUST** configurar CloudWatch Logs retention (no indefinido)
- **MUST** implementar AWS Budgets con alertas
- **MUST** usar cost allocation tags para tracking

### SHOULD (Fuertemente recomendado)

- **SHOULD** comprar Reserved Instances para workloads estables (40-60% ahorro)
- **SHOULD** usar VPC Endpoints para reducir NAT Gateway costs
- **SHOULD** implementar scheduled scaling (reduce noche/fines de semana)
- **SHOULD** usar CloudFront para cachear assets
- **SHOULD** comprimir logs antes de almacenar (GZIP)
- **SHOULD** usar ARM Graviton instances (20% más barato)
- **SHOULD** monitorear unit economics (cost per request)

### MAY (Opcional)

- **MAY** usar Savings Plans para mayor ahorro
- **MAY** implementar NAT Instance si throughput lo permite
- **MAY** usar Spot Instances para batch processing

### MUST NOT (Prohibido)

- **MUST NOT** sobre-provisionar recursos sin justificación
- **MUST NOT** mantener logs indefinidamente en CloudWatch
- **MUST NOT** usar NAT Gateway si VPC Endpoints son suficientes
- **MUST NOT** ignorar alertas de budget
- **MUST NOT** omitir cost allocation tags
- **MUST NOT** usar On-Demand para workloads predecibles (usar RI)
- **MUST NOT** desactivar auto-scaling por simplicidad

---

## Referencias

- [Lineamiento: Cloud Native](../../lineamientos/arquitectura/03-cloud-native.md)
- [ADR-007: AWS ECS Fargate](../../decisiones-de-arquitectura/adr-007-aws-ecs-fargate-contenedores.md)
- Estándares relacionados:
  - [Horizontal Scaling](../arquitectura/horizontal-scaling.md)
- Especificaciones:
  - [AWS Pricing Calculator](https://calculator.aws/)
  - [AWS Cost Explorer](https://aws.amazon.com/aws-cost-management/aws-cost-explorer/)
  - [Fargate Spot](https://aws.amazon.com/fargate/pricing/)
  - [S3 Intelligent-Tiering](https://aws.amazon.com/s3/storage-classes/intelligent-tiering/)
