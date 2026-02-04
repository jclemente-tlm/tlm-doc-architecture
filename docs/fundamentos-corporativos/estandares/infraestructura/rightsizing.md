---
id: rightsizing
sidebar_position: 8
title: Rightsizing de Recursos AWS
description: Estándar para optimización continua de recursos con AWS Compute Optimizer, análisis de métricas CloudWatch y ajuste trimestral
---

# Estándar Técnico — Rightsizing de Recursos AWS

---

## 1. Propósito

Eliminar desperdicio de recursos mediante análisis continuo con AWS Compute Optimizer, CloudWatch métricas, y rightsizing trimestral de instancias ECS Fargate, RDS y ElastiCache basado en uso real.

---

## 2. Alcance

**Aplica a:**

- ECS Fargate tasks (CPU/memoria)
- RDS instances (tipo/tamaño)
- ElastiCache Redis clusters
- Recursos productivos con >30 días de métricas
- Costos >$500 USD/mes por servicio

**No aplica a:**

- Recursos dev/sandbox (lifecycle limitado)
- Servicios con picos impredecibles sin histórico
- Recursos temporales (<30 días)

---

## 3. Tecnologías Aprobadas

| Componente     | Tecnología            | Versión mínima | Observaciones               |
| -------------- | --------------------- | -------------- | --------------------------- |
| **Análisis**   | AWS Compute Optimizer | -              | Recomendaciones ML-based    |
| **Métricas**   | CloudWatch            | -              | CPU, memoria, network       |
| **Dashboards** | Grafana + Mimir       | -              | Visualización consumo       |
| **IaC**        | Terraform             | 1.6+           | Aplicar cambios de tamaño   |
| **Testing**    | Terraform Plan        | -              | Validar cambios antes apply |

> El uso de tecnologías no listadas requiere aprobación de Arquitectura.

---

## 4. Requisitos Obligatorios 🔴

### Proceso de Rightsizing

- [ ] **Análisis mensual** de AWS Compute Optimizer recomendaciones
- [ ] **Métricas mínimo 14 días** antes de cualquier cambio
- [ ] **Test en staging** de nuevos tamaños antes de prod
- [ ] **Ajuste trimestral** de recursos en producción
- [ ] **Documentar cambios** en ADRs si impactan arquitectura
- [ ] **Rollback plan** para cada cambio de rightsizing

### Umbrales de Utilización

| Recurso         | Target CPU | Target Memoria | Acción si <Target       |
| --------------- | ---------- | -------------- | ----------------------- |
| **ECS Fargate** | 40-70%     | 50-80%         | Reducir vCPU/RAM        |
| **RDS**         | 40-80%     | 60-85%         | Downsize instance class |
| **ElastiCache** | 50-75%     | 60-80%         | Reducir nodos o tipo    |

### Indicadores de Oversizing

- CPU promedio <30% últimos 14 días
- Memoria promedio <40% últimos 14 días
- NetworkIn/Out <20% capacidad red
- IOPS <30% del provisionado (RDS)

---

## 5. AWS Compute Optimizer - Recomendaciones

### Habilitar Compute Optimizer

```bash
# Habilitar Compute Optimizer (una vez por cuenta)
aws compute-optimizer update-enrollment-status --status Active

# Verificar estado
aws compute-optimizer get-enrollment-status
```

### Obtener Recomendaciones ECS

```bash
# Recomendaciones para ECS Fargate
aws compute-optimizer get-ecs-service-recommendations \
  --service-arns arn:aws:ecs:us-east-1:123456789:service/prod-cluster/payment-api \
  --query 'ecsServiceRecommendations[*].[
    serviceArn,
    currentPerformanceRisk,
    utilizationMetrics,
    recommendationOptions[*].[cpu, memory, savingsOpportunity]
  ]' \
  --output table

# Exportar todas las recomendaciones
aws compute-optimizer export-ecs-service-recommendations \
  --s3-destination-config bucket=cost-optimization-reports,keyPrefix=compute-optimizer/ \
  --include-member-accounts
```

### Recomendaciones RDS

```bash
# Compute Optimizer NO soporta RDS directamente
# Usar AWS Cost Explorer recomendaciones
aws ce get-rightsizing-recommendation \
  --service "Amazon RDS" \
  --configuration AccountScope=PAYER

# CloudWatch métricas manuales
aws cloudwatch get-metric-statistics \
  --namespace AWS/RDS \
  --metric-name CPUUtilization \
  --dimensions Name=DBInstanceIdentifier,Value=prod-payment-db \
  --start-time $(date -u -d '14 days ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 3600 \
  --statistics Average,Maximum
```

---

## 6. Análisis de Métricas con CloudWatch

### Query para Identificar Underutilized Tasks

```bash
# ECS Fargate - CPU baja
aws cloudwatch get-metric-statistics \
  --namespace ECS/ContainerInsights \
  --metric-name CpuUtilized \
  --dimensions Name=ServiceName,Value=payment-api Name=ClusterName,Value=prod-cluster \
  --start-time $(date -u -d '14 days ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 3600 \
  --statistics Average,Maximum \
  | jq -r '.Datapoints | sort_by(.Timestamp) | .[] | "\(.Timestamp) - CPU: \(.Average)%"'

# Memoria ECS
aws cloudwatch get-metric-statistics \
  --namespace ECS/ContainerInsights \
  --metric-name MemoryUtilized \
  --dimensions Name=ServiceName,Value=payment-api Name=ClusterName,Value=prod-cluster \
  --start-time $(date -u -d '14 days ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 3600 \
  --statistics Average,Maximum,p99
```

### Dashboard Grafana - Rightsizing Candidates

```yaml
# grafana-rightsizing.yaml
apiVersion: 1
dashboards:
  - name: Rightsizing Candidates
    folder: FinOps
    panels:
      - title: ECS Services - Low CPU (<30% avg)
        type: table
        datasource: CloudWatch
        query: |
          SELECT ServiceName, AVG(CpuUtilized) as avg_cpu
          FROM ECS/ContainerInsights
          WHERE ClusterName = 'prod-cluster'
          AND time > now() - 14d
          GROUP BY ServiceName
          HAVING avg_cpu < 30
          ORDER BY avg_cpu ASC

      - title: RDS Instances - Low Utilization
        type: table
        datasource: CloudWatch
        query: |
          SELECT DBInstanceIdentifier, AVG(CPUUtilization) as avg_cpu, AVG(FreeableMemory) as free_mem
          FROM AWS/RDS
          WHERE time > now() - 14d
          GROUP BY DBInstanceIdentifier
          HAVING avg_cpu < 40

      - title: Cost Saving Opportunity
        type: stat
        datasource: Athena
        query: |
          SELECT SUM(potential_savings) as total_savings
          FROM cost_optimizer_recommendations
          WHERE recommendation_type = 'UNDERPROVISIONED'
```

---

## 7. Terraform - Aplicar Rightsizing

### Ejemplo: Reducir ECS Fargate Task

```hcl
# ecs-service.tf (ANTES - Oversized)
resource "aws_ecs_task_definition" "payment_api" {
  family                   = "payment-api"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "1024"   # 1 vCPU
  memory                   = "2048"   # 2 GB

  container_definitions = jsonencode([{
    name  = "payment-api"
    image = "ghcr.io/tlm-svc-payment:v1.2.3"
    # ...
  }])
}

# ecs-service.tf (DESPUÉS - Rightsized basado en Compute Optimizer)
resource "aws_ecs_task_definition" "payment_api" {
  family                   = "payment-api"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "512"    # 0.5 vCPU (reducción 50%)
  memory                   = "1024"   # 1 GB (reducción 50%)

  container_definitions = jsonencode([{
    name  = "payment-api"
    image = "ghcr.io/tlm-svc-payment:v1.2.3"
    # ...
  }])

  tags = {
    Rightsizing       = "true"
    RightsizingDate   = "2024-12-01"
    PreviousSize      = "1024cpu-2048mem"
    Reason            = "Compute Optimizer - avg CPU 25%, avg MEM 35%"
  }
}
```

### RDS Instance Resize

```hcl
# rds.tf (ANTES)
resource "aws_db_instance" "payment" {
  identifier     = "prod-payment-db"
  instance_class = "db.t4g.large"  # 2 vCPU, 8 GB RAM
  # ...
}

# rds.tf (DESPUÉS - Rightsized)
resource "aws_db_instance" "payment" {
  identifier     = "prod-payment-db"
  instance_class = "db.t4g.medium"  # 2 vCPU, 4 GB RAM (ahorro ~40% costo)

  # Aplicar cambio en ventana de mantenimiento
  apply_immediately = false

  tags = {
    Rightsizing     = "true"
    RightsizingDate = "2024-12-01"
    PreviousClass   = "db.t4g.large"
    Reason          = "CloudWatch - avg CPU 35%, avg MEM 42%"
  }
}
```

---

## 8. Proceso de Validación Pre-Cambio

```bash
#!/bin/bash
# validate-rightsizing.sh

SERVICE="payment-api"
PROPOSED_CPU="512"
PROPOSED_MEM="1024"

# 1. Validar métricas últimos 14 días
AVG_CPU=$(aws cloudwatch get-metric-statistics \
  --namespace ECS/ContainerInsights \
  --metric-name CpuUtilized \
  --dimensions Name=ServiceName,Value=$SERVICE \
  --start-time $(date -u -d '14 days ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 3600 \
  --statistics Average \
  | jq -r '.Datapoints | map(.Average) | add/length')

echo "CPU promedio últimos 14 días: ${AVG_CPU}%"

if (( $(echo "$AVG_CPU > 70" | bc -l) )); then
  echo "❌ RIESGO: CPU promedio >70%, no se recomienda reducir"
  exit 1
fi

# 2. Terraform plan
cd infrastructure/
terraform plan -out=rightsizing.tfplan

# 3. Revisar cambios
terraform show rightsizing.tfplan | grep -A 10 "cpu\|memory"

echo "✅ Validación completada - revisar plan manualmente"
```

---

## 9. Rollback Plan

```hcl
# locals.tf - Versioning de configuraciones
locals {
  task_configurations = {
    current = {
      cpu    = "512"
      memory = "1024"
    }
    previous = {
      cpu    = "1024"
      memory = "2048"
    }
  }

  # Flag para rollback rápido
  use_previous_config = var.rollback_enabled ? local.task_configurations.previous : local.task_configurations.current
}

resource "aws_ecs_task_definition" "payment_api" {
  family = "payment-api"
  cpu    = local.use_previous_config.cpu
  memory = local.use_previous_config.memory
  # ...
}
```

### Rollback Command

```bash
# Rollback inmediato si rightsizing causa problemas
terraform apply -var="rollback_enabled=true"

# O actualizar service manualmente
aws ecs update-service \
  --cluster prod-cluster \
  --service payment-api \
  --task-definition payment-api:$PREVIOUS_REVISION \
  --force-new-deployment
```

---

## 10. Reporting Mensual

```markdown
## Rightsizing Report - Diciembre 2024

### Cambios Aplicados

| Servicio    | Tipo | Config Anterior | Nueva Config  | Ahorro Mensual |
| ----------- | ---- | --------------- | ------------- | -------------- |
| payment-api | ECS  | 1024/2048       | 512/1024      | $145 USD       |
| order-api   | ECS  | 2048/4096       | 1024/2048     | $290 USD       |
| payment-db  | RDS  | db.t4g.large    | db.t4g.medium | $92 USD        |

**Total Ahorro Mensual:** $527 USD
**Ahorro Anual Proyectado:** $6,324 USD

### Métricas Post-Cambio (7 días)

- payment-api: CPU 55% avg (dentro de rango), latencia p95 estable
- order-api: CPU 62% avg, sin degradación performance
- payment-db: CPU 48% avg, query times sin cambios

### Recomendaciones Pendientes

1. inventory-api: CPU 18% → Candidato para Q1 2025
2. notification-api: MEM 22% → Evaluar en Enero
```

---

## 11. Validación de Cumplimiento

```bash
# Listar recursos con CPU <30% últimos 14 días
aws cloudwatch get-metric-statistics --namespace ECS/ContainerInsights \
  --metric-name CpuUtilized --statistics Average \
  --start-time $(date -u -d '14 days ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 86400 \
  | jq '.Datapoints | map(.Average) | add/length'

# Verificar tags de rightsizing
aws resourcegroupstaggingapi get-resources \
  --tag-filters Key=Rightsizing,Values=true \
  --query 'ResourceTagMappingList[*].[ResourceARN, Tags[?Key==`RightsizingDate`].Value]'
```

---

## 12. Referencias

**AWS:**

- [AWS Compute Optimizer User Guide](https://docs.aws.amazon.com/compute-optimizer/latest/ug/)
- [Rightsizing Recommendations](https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/ce-rightsizing.html)

**FinOps:**

- [FinOps Foundation - Rightsizing](https://www.finops.org/framework/capabilities/rightsizing/)
- [AWS Well-Architected - Cost Optimization](https://docs.aws.amazon.com/wellarchitected/latest/cost-optimization-pillar/)
