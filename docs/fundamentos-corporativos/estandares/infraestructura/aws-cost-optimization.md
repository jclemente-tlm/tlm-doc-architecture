---
id: aws-cost-optimization
sidebar_position: 5
title: Optimización de Costos AWS
description: Estándar completo para optimización de costos AWS mediante tagging, alertas, rightsizing y capacidad reservada
---

# Estándar Técnico — Optimización de Costos AWS

---

## 1. Propósito

Optimizar costos AWS mediante tagging obligatorio, alertas proactivas, rightsizing trimestral y Savings Plans para cargas predecibles.

---

## 2. Alcance

**Aplica a:**

- **Todos** los recursos AWS con soporte de tags
- Todas las cuentas AWS (dev, staging, prod)
- Servicios críticos de alto costo (ECS Fargate, RDS, S3, ElastiCache)
- Cargas de trabajo con >30 días de métricas
- Presupuestos por equipo/proyecto

**No aplica a:**

- Cuentas sandbox personales (<30 días)
- Recursos sin soporte de tags
- Recursos experimentales temporales

---

## 3. Tecnologías Aprobadas

| Componente          | Tecnología                  | Versión mínima | Observaciones                 |
| ------------------- | --------------------------- | -------------- | ----------------------------- |
| **Tagging**         | Terraform default_tags      | 1.6+           | Tags automáticos por provider |
| **Validación Tags** | Checkov                     | 3.0+           | Policy as Code                |
| **Alertas**         | AWS Budgets                 | -              | Umbrales escalonados          |
| **Notificaciones**  | AWS SNS                     | -              | Email/Slack                   |
| **Rightsizing**     | AWS Compute Optimizer       | -              | Recomendaciones ML-based      |
| **Savings Plans**   | AWS Compute Savings Plans   | -              | Prioridad sobre RIs           |
| **Dashboards**      | Grafana + Cost Explorer API | -              | Visualización costos          |
| **Anomalías**       | AWS Cost Anomaly Detection  | -              | Detección automática picos    |
| **Métricas**        | CloudWatch                  | -              | CPU, memoria, network         |

> El uso de tecnologías no listadas requiere aprobación de Arquitectura.

---

## 4. Requisitos Obligatorios 🔴

### Tagging Obligatorio

- [ ] **6 tags mínimos**: Environment, Service, Owner, CostCenter, ManagedBy, Project
- [ ] **Validación en CI/CD**: Checkov bloqueante para tags faltantes
- [ ] **Tag Policies**: AWS Organizations Tag Policies habilitadas
- [ ] **Reportes mensuales**: Cost allocation por tags

### Alertas de Costos

- [ ] **Budget mensual**: Por cuenta AWS (dev, staging, prod)
- [ ] **Budget por servicio**: Para componentes críticos (ECS, RDS, S3)
- [ ] **Umbrales**: 50% (INFO), 80% (WARNING), 100% (CRITICAL), 120% (BLOCKER)
- [ ] **Notificaciones SNS**: Email + Slack para team leads
- [ ] **Cost Anomaly Detection**: Habilitado con alertas automáticas

### Rightsizing

- [ ] **Análisis mensual**: AWS Compute Optimizer recomendaciones
- [ ] **Métricas mínimo 14 días**: Antes de cualquier cambio
- [ ] **Test en staging**: Nuevos tamaños antes de prod
- [ ] **Ajuste trimestral**: Recursos en producción
- [ ] **Rollback plan**: Para cada cambio

### Savings Plans

- [ ] **Análisis 6 meses**: Uso histórico antes de commitment
- [ ] **Prioridad Savings Plans**: Sobre Reserved Instances
- [ ] **Commitment progresivo**: Iniciar 50% baseline, ajustar trimestral
- [ ] **Término 1 año**: Preferido sobre 3 años
- [ ] **Revisión trimestral**: Utilización y ajustes

---

## 5. Prohibiciones

- ❌ Recursos sin tags obligatorios en producción
- ❌ Budgets sin notificaciones configuradas
- ❌ Rightsizing sin test previo en staging
- ❌ Savings Plans >80% baseline sin análisis
- ❌ Reserved Instances sin evaluación de Savings Plans primero
- ❌ Cambios de tamaño sin métricas de 14+ días

---

## 6. Tagging Strategy

### Tags Obligatorios

| Tag             | Descripción                    | Valores permitidos               | Ejemplo         |
| --------------- | ------------------------------ | -------------------------------- | --------------- |
| **Environment** | Entorno de deployment          | `dev`, `staging`, `prod`         | `prod`          |
| **Service**     | Nombre del servicio/aplicación | kebab-case alfanumérico          | `payment-api`   |
| **Owner**       | Equipo responsable             | Nombre del equipo                | `platform-team` |
| **CostCenter**  | Centro de costos               | Código contabilidad              | `engineering`   |
| **ManagedBy**   | Herramienta de provisión       | `terraform`, `manual`, `console` | `terraform`     |
| **Project**     | Proyecto/iniciativa            | Nombre proyecto                  | `ecommerce-v2`  |

### Tags Opcionales

| Tag            | Descripción              | Ejemplo                   |
| -------------- | ------------------------ | ------------------------- |
| **Backup**     | Política de backup       | `daily`, `weekly`, `none` |
| **Compliance** | Requisito regulatorio    | `pci-dss`, `sox`, `none`  |
| **Version**    | Versión de la aplicación | `v1.2.3`                  |

### Terraform - Default Tags

```hcl
# provider.tf
provider "aws" {
  region = var.aws_region

  # Tags aplicados automáticamente a TODOS los recursos
  default_tags {
    tags = {
      Environment = var.environment
      ManagedBy   = "terraform"
      Project     = var.project_name
      CostCenter  = var.cost_center
    }
  }
}

# variables.tf
variable "environment" {
  description = "Entorno de deployment"
  type        = string
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment debe ser: dev, staging o prod"
  }
}

variable "cost_center" {
  description = "Centro de costos"
  type        = string
  default     = "engineering"
}

# locals.tf - Tags específicos por recurso
locals {
  service_tags = {
    Service = "payment-api"
    Owner   = "platform-team"
  }
}

# main.tf - Uso de tags
resource "aws_ecs_service" "payment_api" {
  name = "payment-api"
  # ... otras configuraciones

  tags = local.service_tags
  # default_tags ya incluye: Environment, ManagedBy, Project, CostCenter
}
```

### Validación Tags - Checkov

```hcl
# .checkov.yml
framework:
  - terraform

check:
  - CKV_AWS_110: "Ensure that AWS tagging is enabled"
  - CKV_AWS_111: "Ensure IAM policies include required tags"

soft-fail:
  - CKV_AWS_110

# GitHub Actions - Bloquear si faltan tags
- name: Run Checkov
  uses: bridgecrewio/checkov-action@master
  with:
    directory: terraform/
    framework: terraform
    check: CKV_AWS_110,CKV_AWS_111
    soft_fail: false  # Bloqueante
```

---

## 7. Alertas de Costos - AWS Budgets

### Terraform - Budget con Umbrales Múltiples

```hcl
# budgets.tf
resource "aws_budgets_budget" "monthly_account" {
  name         = "monthly-${var.environment}-budget"
  budget_type  = "COST"
  limit_amount = var.monthly_budget_limit
  limit_unit   = "USD"
  time_unit    = "MONTHLY"

  cost_filter {
    name   = "TagKeyValue"
    values = ["Environment$${var.environment}"]
  }

  # Alerta 50% - INFO
  notification {
    comparison_operator        = "GREATER_THAN"
    threshold                  = 50
    threshold_type             = "PERCENTAGE"
    notification_type          = "FORECASTED"
    subscriber_email_addresses = [var.team_lead_email]
  }

  # Alerta 80% - WARNING
  notification {
    comparison_operator        = "GREATER_THAN"
    threshold                  = 80
    threshold_type             = "PERCENTAGE"
    notification_type          = "ACTUAL"
    subscriber_sns_topic_arns  = [aws_sns_topic.cost_alerts.arn]
  }

  # Alerta 100% - CRITICAL
  notification {
    comparison_operator        = "GREATER_THAN"
    threshold                  = 100
    threshold_type             = "PERCENTAGE"
    notification_type          = "ACTUAL"
    subscriber_sns_topic_arns  = [aws_sns_topic.cost_alerts_critical.arn]
  }

  # Alerta 120% - BLOCKER
  notification {
    comparison_operator        = "GREATER_THAN"
    threshold                  = 120
    threshold_type             = "PERCENTAGE"
    notification_type          = "ACTUAL"
    subscriber_sns_topic_arns  = [aws_sns_topic.cost_alerts_blocker.arn]
  }
}

# SNS Topic para notificaciones
resource "aws_sns_topic" "cost_alerts" {
  name = "${var.environment}-cost-alerts"
}

resource "aws_sns_topic_subscription" "slack" {
  topic_arn = aws_sns_topic.cost_alerts.arn
  protocol  = "https"
  endpoint  = var.slack_webhook_url
}
```

### Thresholds y Acciones

| Threshold | Severidad | Notificación               | Acción                        |
| --------- | --------- | -------------------------- | ----------------------------- |
| 50%       | INFO      | Email team lead            | Revisión semanal              |
| 80%       | WARNING   | Email + Slack              | Reunión urgente               |
| 100%      | CRITICAL  | Email + Slack + call       | Congelar recursos no críticos |
| 120%      | BLOCKER   | Email + Slack + escalation | Apagar recursos dev/staging   |

---

## 8. Rightsizing - Análisis Continuo

### Umbrales de Utilización

| Recurso         | Target CPU | Target Memoria | Acción si <Target       |
| --------------- | ---------- | -------------- | ----------------------- |
| **ECS Fargate** | 40-70%     | 50-80%         | Reducir vCPU/RAM        |
| **RDS**         | 40-80%     | 60-85%         | Downsize instance class |
| **ElastiCache** | 50-75%     | 60-80%         | Reducir nodos o tipo    |

### AWS Compute Optimizer - Recomendaciones

```bash
# Habilitar Compute Optimizer (una vez)
aws compute-optimizer update-enrollment-status --status Active

# Obtener recomendaciones ECS
aws compute-optimizer get-ecs-service-recommendations \
  --service-arns arn:aws:ecs:us-east-1:123456789:service/prod/payment-api \
  --query 'ecsServiceRecommendations[*].[
    currentConfiguration.cpu,
    currentConfiguration.memory,
    utilizationMetrics[?name==`CPU`].value | [0],
    utilizationMetrics[?name==`MEMORY`].value | [0],
    recommendationOptions[0].cpu,
    recommendationOptions[0].memory,
    recommendationOptions[0].savingsOpportunity.savingsOpportunityPercentage
  ]' \
  --output table

# Ejemplo output:
# Current: 1024 CPU / 2048 MB → Uso: 35% CPU / 45% Memory
# Recomendado: 512 CPU / 1024 MB → Ahorro: 50%
```

### CloudWatch - Análisis Manual

```bash
# CPU promedio últimos 14 días (ECS)
aws cloudwatch get-metric-statistics \
  --namespace AWS/ECS \
  --metric-name CPUUtilization \
  --dimensions Name=ServiceName,Value=payment-api Name=ClusterName,Value=prod \
  --start-time $(date -u -d '14 days ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 3600 \
  --statistics Average \
  --query 'Datapoints[*].Average' \
  --output text | awk '{sum+=$1; count++} END {print "CPU Promedio: " sum/count "%"}'

# Memoria promedio últimos 14 días
aws cloudwatch get-metric-statistics \
  --namespace AWS/ECS \
  --metric-name MemoryUtilization \
  --dimensions Name=ServiceName,Value=payment-api Name=ClusterName,Value=prod \
  --start-time $(date -u -d '14 days ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 3600 \
  --statistics Average \
  --query 'Datapoints[*].Average' \
  --output text | awk '{sum+=$1; count++} END {print "Memoria Promedio: " sum/count "%"}'
```

### Terraform - Aplicar Rightsizing

```hcl
# ANTES (oversized)
resource "aws_ecs_task_definition" "payment_api" {
  cpu    = "1024"  # 1 vCPU
  memory = "2048"  # 2 GB
}

# DESPUÉS (rightsized basado en métricas)
resource "aws_ecs_task_definition" "payment_api" {
  cpu    = "512"   # 0.5 vCPU (uso real 35%)
  memory = "1024"  # 1 GB (uso real 45%)
}

# Ahorro estimado: 50% en costos ECS
```

---

## 9. Savings Plans - Capacidad Reservada

### Estrategia de Commitment

| Entorno        | Coverage Target | Tipo de Commitment    |
| -------------- | --------------- | --------------------- |
| **Producción** | 60-80% baseline | Compute Savings Plans |
| **Staging**    | 0% (On-Demand)  | N/A                   |
| **Dev**        | 0% (On-Demand)  | N/A                   |

### Servicios Elegibles

| Servicio              | Opción               | Ahorro Estimado | Observaciones            |
| --------------------- | -------------------- | --------------- | ------------------------ |
| **ECS Fargate**       | Compute Savings Plan | 50-60%          | Auto aplicable           |
| **RDS PostgreSQL**    | Reserved Instances   | 40-60%          | Por instancia específica |
| **ElastiCache Redis** | Reserved Nodes       | 30-55%          | Por tipo de nodo         |

### AWS Cost Explorer - Análisis Baseline

```bash
# Uso promedio últimos 6 meses (Fargate)
aws ce get-usage-forecast \
  --time-period Start=$(date -d '6 months ago' +%Y-%m-%d),End=$(date +%Y-%m-%d) \
  --metric USAGE_QUANTITY \
  --granularity MONTHLY \
  --filter '{
    "Dimensions": {
      "Key": "SERVICE",
      "Values": ["Amazon Elastic Container Service"]
    },
    "Tags": {
      "Key": "Environment",
      "Values": ["prod"]
    }
  }'

# Calcular baseline (percentil 50 del uso)
# Si promedio = 100 vCPU-hours/mes
# Commitment recomendado = 60 vCPU-hours (60% del baseline)
```

### Terraform - Compute Savings Plan

```hcl
# savings-plans.tf
resource "aws_savingsplans_plan" "compute" {
  savings_plan_type = "ComputeSavingsPlans"

  # Commitment por hora ($10/hora = $7,300/mes aprox)
  commitment = "10.0"

  # Término
  term = "ONE_YEAR"  # o "THREE_YEARS"

  # Pago
  payment_option = "ALL_UPFRONT"  # Mayor descuento

  tags = {
    Environment = "prod"
    ManagedBy   = "terraform"
  }
}
```

### Savings Plans Monitoring

```bash
# Utilización de Savings Plans
aws savingsplans get-savings-plans-utilization \
  --time-period Start=2026-01-01,End=2026-01-31 \
  --granularity MONTHLY

# Ejemplo output:
# Utilization: 85% (BUENO - entre 80-95%)
# On-Demand Cost: $12,000
# Savings Plan Cost: $6,000
# Ahorro real: 50%
```

---

## 10. Dashboards - Grafana

### Prometheus Queries (AWS Cost Explorer API)

```promql
# Costo mensual por servicio
sum by (service) (
  aws_cost_explorer_cost_usd{
    environment="prod",
    time_period="MONTHLY"
  }
)

# Costo por tag (Owner)
sum by (owner) (
  aws_cost_explorer_cost_usd{
    tag_key="Owner",
    time_period="MONTHLY"
  }
)

# Forecast próximo mes
aws_cost_explorer_forecast_usd{
  environment="prod"
}

# Utilización Savings Plans
aws_savings_plans_utilization_percentage
```

---

## 11. Validación de Cumplimiento

```bash
#!/bin/bash
# scripts/validate-cost-optimization.sh

echo "🔍 Validando optimización de costos AWS..."

# 1. Verificar tags obligatorios en recursos
echo "1. Validando tags obligatorios..."
MISSING_TAGS=$(aws resourcegroupstaggingapi get-resources \
  --tag-filters Key=Environment,Values=prod \
  --tags-per-page 100 \
  | jq -r '.ResourceTagMappingList[] | select(
      (.Tags | map(.Key) | contains(["Environment", "Service", "Owner", "CostCenter", "ManagedBy", "Project"]) | not)
    ) | .ResourceARN')

if [ -n "$MISSING_TAGS" ]; then
  echo "   ❌ Recursos sin tags completos:"
  echo "$MISSING_TAGS"
  exit 1
fi
echo "   ✅ Todos los recursos tienen tags obligatorios"

# 2. Verificar budgets configurados
echo "2. Verificando budgets..."
BUDGETS=$(aws budgets describe-budgets --account-id $(aws sts get-caller-identity --query Account --output text) --query 'Budgets[*].BudgetName' --output text)
if [ -z "$BUDGETS" ]; then
  echo "   ❌ No hay budgets configurados"
  exit 1
fi
echo "   ✅ Budgets configurados: $BUDGETS"

# 3. Verificar Cost Anomaly Detection habilitado
echo "3. Verificando Cost Anomaly Detection..."
MONITORS=$(aws ce get-anomaly-monitors --query 'AnomalyMonitors[*].MonitorName' --output text)
if [ -z "$MONITORS" ]; then
  echo "   ⚠️  WARN: Cost Anomaly Detection no habilitado"
fi

# 4. Verificar Compute Optimizer habilitado
echo "4. Verificando Compute Optimizer..."
OPTIMIZER_STATUS=$(aws compute-optimizer get-enrollment-status --query 'status' --output text)
if [ "$OPTIMIZER_STATUS" != "Active" ]; then
  echo "   ❌ Compute Optimizer no habilitado"
  exit 1
fi
echo "   ✅ Compute Optimizer activo"

# 5. Verificar Savings Plans activos
echo "5. Verificando Savings Plans..."
SAVINGS_PLANS=$(aws savingsplans describe-savings-plans --filters name=state,values=active --query 'savingsPlans[*].savingsPlanId' --output text)
if [ -z "$SAVINGS_PLANS" ]; then
  echo "   ⚠️  WARN: No hay Savings Plans activos"
fi

# 6. Obtener recomendaciones pendientes de Compute Optimizer
echo "6. Recomendaciones de Compute Optimizer..."
ECS_RECS=$(aws compute-optimizer get-ecs-service-recommendations --query 'ecsServiceRecommendations | length(@)' --output text)
echo "   ECS Services con recomendaciones: $ECS_RECS"

echo "✅ Validación de optimización de costos completada"
```

### Métricas de Cumplimiento

| Métrica                           | Target | Verificación                                     |
| --------------------------------- | ------ | ------------------------------------------------ |
| Recursos con tags completos       | 100%   | `aws resourcegroupstaggingapi get-resources`     |
| Budgets configurados              | 100%   | `aws budgets describe-budgets`                   |
| Budget alerts SNS configurados    | 100%   | Verificar notificaciones en cada budget          |
| Compute Optimizer habilitado      | 100%   | `aws compute-optimizer get-enrollment-status`    |
| Savings Plans coverage (prod)     | 60-80% | `aws savingsplans get-savings-plans-utilization` |
| Rightsizing aplicado trimestral   | 100%   | ADRs documentando cambios                        |
| Cost Anomaly Detection habilitado | 100%   | `aws ce get-anomaly-monitors`                    |
| CloudWatch dashboards configurado | 100%   | Grafana panels validación                        |

---

## 12. Referencias

**AWS Docs:**

- [AWS Cost Optimization](https://aws.amazon.com/aws-cost-management/aws-cost-optimization/)
- [AWS Budgets](https://docs.aws.amazon.com/cost-management/latest/userguide/budgets-managing-costs.html)
- [AWS Compute Optimizer](https://docs.aws.amazon.com/compute-optimizer/)
- [AWS Savings Plans](https://aws.amazon.com/savingsplans/)
- [Tagging Best Practices](https://docs.aws.amazon.com/whitepapers/latest/tagging-best-practices/)

**FinOps Foundation:**

- [FinOps Principles](https://www.finops.org/framework/principles/)
- [Cloud Cost Optimization Best Practices](https://www.finops.org/framework/capabilities/)

**Talma ADRs:**

- [ADR-006: Infraestructura como Código](../../decisiones-de-arquitectura/adr-006-infraestructura-iac.md)
