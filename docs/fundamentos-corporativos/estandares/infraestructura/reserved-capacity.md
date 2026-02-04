---
id: reserved-capacity
sidebar_position: 7
title: Capacidad Reservada AWS
description: Estándar para optimización de costos con AWS Savings Plans y análisis de usage para cargas predecibles
---

# Estándar Técnico — Capacidad Reservada AWS

---

## 1. Propósito

Reducir costos 30-70% en cargas de trabajo predecibles mediante AWS Compute Savings Plans (prioridad) y Reserved Instances, basado en análisis histórico de uso, con revisión trimestral y commitment progresivo.

---

## 2. Alcance

**Aplica a:**

- Servicios con consumo estable >6 meses (ECS Fargate, RDS, Redis)
- Entornos productivos con SLA
- Cargas base predecibles (baseline capacity)
- Presupuestos de más de $5,000 USD/mes

**No aplica a:**

- Ambientes dev/staging (usar On-Demand)
- Picos temporales (usar Auto Scaling On-Demand)
- Servicios en prueba o migración
- Presupuestos variables o proyectos experimentales

---

## 3. Tecnologías Aprobadas

| Componente   | Tecnología                    | Versión mínima | Observaciones                |
| ------------ | ----------------------------- | -------------- | ---------------------------- |
| **Savings**  | AWS Compute Savings Plans     | -              | Flexibilidad mayor que RIs   |
| **Reservas** | Reserved Instances (RDS)      | -              | Solo para databases estables |
| **Análisis** | AWS Cost Explorer             | -              | Historical usage analysis    |
| **Forecast** | AWS Cost Explorer Forecasting | -              | Predicción tendencias        |
| **IaC**      | Terraform                     | 1.6+           | Gestión Savings Plans        |

> El uso de tecnologías no listadas requiere aprobación de Arquitectura.

---

## 4. Requisitos Obligatorios 🔴

### Estrategia de Commitment

- [ ] **Análisis obligatorio** de 6 meses de uso antes de commitment
- [ ] **Prioridad Savings Plans** sobre Reserved Instances (mayor flexibilidad)
- [ ] **Commitment progresivo**: Iniciar con 50% baseline, ajustar trimestralmente
- [ ] **Término 1 año** (preferido) o 3 años solo para cargas ultra-estables
- [ ] **Payment**: All Upfront > Partial Upfront > No Upfront (mayor descuento)
- [ ] **Revisión trimestral** de utilización y ajustes

### Coverage Targets

| Entorno        | Coverage Target | Tipo de Commitment    |
| -------------- | --------------- | --------------------- |
| **Producción** | 60-80% baseline | Compute Savings Plans |
| **Staging**    | 0% (On-Demand)  | N/A                   |
| **Dev**        | 0% (On-Demand)  | N/A                   |

### Servicios Elegibles

| Servicio              | Opción de Commitment  | Ahorro Estimado | Observaciones                       |
| --------------------- | --------------------- | --------------- | ----------------------------------- |
| **ECS Fargate**       | Compute Savings Plans | 50-60%          | Auto aplicable a Fargate            |
| **RDS PostgreSQL**    | Reserved Instances    | 40-60%          | Commitment por instancia específica |
| **RDS Oracle**        | Reserved Instances    | 30-50%          | License Included model              |
| **ElastiCache Redis** | Reserved Nodes        | 30-55%          | Por tipo de nodo                    |

---

## 5. Análisis de Baseline Usage

### AWS Cost Explorer - Historical Analysis

```bash
# Obtener uso promedio últimos 6 meses (ECS Fargate)
aws ce get-usage-forecast \
  --time-period Start=$(date -d '6 months ago' +%Y-%m-%d),End=$(date +%Y-%m-%d) \
  --metric USAGE_QUANTITY \
  --granularity MONTHLY \
  --filter file://fargate-filter.json

# fargate-filter.json
{
  "Dimensions": {
    "Key": "SERVICE",
    "Values": ["Amazon Elastic Container Service"]
  },
  "Tags": {
    "Key": "Environment",
    "Values": ["prod"]
  }
}

# Calcular baseline (uso mínimo constante)
aws ce get-cost-and-usage \
  --time-period Start=2024-01-01,End=2024-06-30 \
  --granularity DAILY \
  --metrics "UsageQuantity" \
  --group-by Type=DIMENSION,Key=SERVICE \
  | jq '.ResultsByTime[].Groups[] | select(.Keys[0]=="Amazon Elastic Container Service") | .Metrics.UsageQuantity.Amount' \
  | sort -n | head -30 | awk '{sum+=$1} END {print sum/NR}'  # Promedio del 10% más bajo
```

### Recomendación AWS Native

```bash
# Obtener recomendaciones de Savings Plans
aws ce get-savings-plans-purchase-recommendation \
  --savings-plans-type COMPUTE_SP \
  --term-in-years ONE_YEAR \
  --payment-option ALL_UPFRONT \
  --lookback-period-in-days 60

# Recomendaciones Reserved Instances (RDS)
aws ce get-reservation-purchase-recommendation \
  --service "Amazon RDS" \
  --lookback-period-in-days 60 \
  --term-in-years ONE_YEAR \
  --payment-option ALL_UPFRONT
```

---

## 6. Terraform - Compra de Savings Plan

```hcl
# savings-plans.tf
resource "aws_savingsplans_plan" "compute_savings" {
  savings_plan_type = "ComputeSavingsPlans"

  # Commitment USD/hour (ej: $50/hour = ~$36,500/year)
  commitment = var.hourly_commitment_usd

  # 1 año con pago adelantado total
  term              = "OneYear"
  payment_option    = "AllUpfront"

  # Auto-renovación deshabilitada (revisar manualmente)
  auto_renew = false

  tags = {
    Environment = "prod"
    ManagedBy   = "terraform"
    CostCenter  = "platform-engineering"
    ReviewDate  = "Q1-2025"
  }
}

# CloudWatch Alarm - Low Utilization
resource "aws_cloudwatch_metric_alarm" "savings_plan_underutilized" {
  alarm_name          = "savings-plan-low-utilization"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = 7
  metric_name         = "SavingsPlansCoveragePercentage"
  namespace           = "AWS/SavingsPlans"
  period              = 86400  # 1 día
  statistic           = "Average"
  threshold           = 90  # Alert si <90% utilization

  alarm_description = "Savings Plan con baja utilización - revisar rightsizing"
  alarm_actions     = [aws_sns_topic.cost_alerts.arn]

  dimensions = {
    SavingsPlanArn = aws_savingsplans_plan.compute_savings.arn
  }
}
```

### Reserved Instances para RDS (Terraform)

```hcl
# rds-reserved.tf
# NOTA: RIs deben comprarse manualmente vía CLI/Console
# Este código documenta la configuración

locals {
  rds_reservation = {
    instance_class        = "db.t4g.medium"
    instance_count        = 2  # 2 instancias prod
    duration              = 31536000  # 1 año en segundos
    offering_type         = "All Upfront"
    multi_az              = true
    product_description   = "postgresql"
  }
}

# Script helper para compra (ejecutar manualmente)
resource "null_resource" "purchase_ri_instructions" {
  provisioner "local-exec" {
    command = <<-EOT
      echo "Para comprar Reserved Instance:"
      echo "aws rds purchase-reserved-db-instances-offering \\"
      echo "  --reserved-db-instances-offering-id <ID> \\"
      echo "  --reserved-db-instance-id prod-payment-db-ri \\"
      echo "  --db-instance-count ${local.rds_reservation.instance_count}"
    EOT
  }
}
```

---

## 7. Monitoreo de Utilización

### CloudWatch Dashboard

```json
{
  "widgets": [
    {
      "type": "metric",
      "properties": {
        "metrics": [
          [
            "AWS/SavingsPlans",
            "SavingsPlansCoveragePercentage",
            { "stat": "Average" }
          ],
          [".", "SavingsPlansUtilizationPercentage", { "stat": "Average" }]
        ],
        "period": 86400,
        "region": "us-east-1",
        "title": "Savings Plans Utilization",
        "yAxis": { "left": { "min": 0, "max": 100 } }
      }
    },
    {
      "type": "metric",
      "properties": {
        "metrics": [
          ["AWS/RDS", "ReservedInstanceUtilization", { "stat": "Average" }]
        ],
        "period": 86400,
        "title": "RDS Reserved Instance Usage"
      }
    }
  ]
}
```

### Alertas de Baja Utilización

```bash
# Script de validación semanal
#!/bin/bash
# check-ri-utilization.sh

THRESHOLD=85  # Mínimo 85% utilización

# Savings Plans
SP_UTIL=$(aws ce get-savings-plans-utilization \
  --time-period Start=$(date -d '7 days ago' +%Y-%m-%d),End=$(date +%Y-%m-%d) \
  | jq -r '.Total.Utilization.UtilizationPercentage')

if (( $(echo "$SP_UTIL < $THRESHOLD" | bc -l) )); then
  echo "⚠️ Savings Plan bajo utilización: ${SP_UTIL}%"
  # Notificar a FinOps/Platform team
fi

# Reserved Instances (RDS)
RI_UTIL=$(aws ce get-reservation-utilization \
  --time-period Start=$(date -d '7 days ago' +%Y-%m-%d),End=$(date +%Y-%m-%d) \
  --filter '{"Dimensions":{"Key":"SERVICE","Values":["Amazon RDS"]}}' \
  | jq -r '.Total.UtilizationPercentage')

if (( $(echo "$RI_UTIL < $THRESHOLD" | bc -l) )); then
  echo "⚠️ RDS RI bajo utilización: ${RI_UTIL}%"
fi
```

---

## 8. Decisión: Savings Plans vs Reserved Instances

| Característica     | Compute Savings Plans           | Reserved Instances   |
| ------------------ | ------------------------------- | -------------------- |
| **Flexibilidad**   | ✅ Alta (cualquier región/tipo) | ❌ Baja (específico) |
| **Servicios**      | EC2, Fargate, Lambda            | Solo EC2/RDS         |
| **Cambio de tipo** | ✅ Automático                   | ❌ Manual exchange   |
| **Descuento**      | 50-60%                          | 40-70% (varía)       |
| **Gestión**        | ✅ Simple                       | ⚠️ Compleja          |
| **Recomendación**  | **Usar para Fargate**           | Usar solo para RDS   |

**Decisión**: Priorizar Compute Savings Plans para ECS Fargate, usar RIs solo para RDS con cargas ultra-estables.

---

## 9. Proceso de Revisión Trimestral

```markdown
## Q1 2025 - Savings Plan Review

### Métricas Actuales

- Commitment: $50/hour ($438,000/year)
- Utilization: 94% (target: >90%)
- Coverage: 65% de baseline Fargate
- Ahorro acumulado: $180,000 (6 meses)

### Cambios Propuestos

- Incrementar commitment a $60/hour (+$87,600/year)
- Razón: Nuevo servicio "order-api" estable >4 meses
- Baseline analysis: 55 vCPU constantes

### Aprobación

- [ ] Platform Lead
- [ ] FinOps (si existe)
- [ ] CFO/Finance
```

---

## 10. Validación de Cumplimiento

```bash
# Verificar Savings Plans activos
aws savingsplans describe-savings-plans \
  --savings-plan-arns $PLAN_ARN

# Verificar utilización última semana
aws ce get-savings-plans-utilization-details \
  --time-period Start=$(date -d '7 days ago' +%Y-%m-%d),End=$(date +%Y-%m-%d) \
  --savings-plan-arn-list $PLAN_ARN

# RIs activas (RDS)
aws rds describe-reserved-db-instances \
  --query 'ReservedDBInstances[?State==`active`]'
```

---

## 11. Referencias

**AWS:**

- [Savings Plans User Guide](https://docs.aws.amazon.com/savingsplans/latest/userguide/)
- [Reserved Instances Best Practices](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ri-market-concepts-buying.html)

**FinOps:**

- [FinOps Foundation - Rate Optimization](https://www.finops.org/framework/capabilities/rate-optimization/)
- [AWS Cost Optimization Pillar](https://docs.aws.amazon.com/wellarchitected/latest/cost-optimization-pillar/)
