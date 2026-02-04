---
id: cost-alerts
sidebar_position: 5
title: Alertas de Costos AWS
description: Estándar para configuración de alertas de costos usando AWS Budgets con umbrales progresivos y notificaciones SNS
---

# Estándar Técnico — Alertas de Costos AWS

---

## 1. Propósito

Prevenir sobrecostos mediante alertas proactivas con AWS Budgets, umbrales escalonados (50%, 80%, 100%, 120%), notificaciones SNS inmediatas y dashboards Grafana para visibilidad continua de consumo.

---

## 2. Alcance

**Aplica a:**

- Todas las cuentas AWS (dev, staging, prod)
- Servicios críticos de alto costo (ECS Fargate, RDS, S3, data transfer)
- Presupuestos por equipo/proyecto
- Alertas de anomalías de costo

**No aplica a:**

- Sandbox/dev personal sin presupuesto asignado
- Cuentas experimentales temporales (<30 días)

---

## 3. Tecnologías Aprobadas

| Componente         | Tecnología                      | Versión mínima | Observaciones              |
| ------------------ | ------------------------------- | -------------- | -------------------------- |
| **Budgets**        | AWS Budgets                     | -              | Presupuestos y alertas     |
| **Notificaciones** | AWS SNS                         | -              | Email/Slack notifications  |
| **IaC**            | Terraform                       | 1.6+           | Gestión budgets            |
| **Dashboards**     | Grafana + AWS Cost Explorer API | -              | Visualización costos       |
| **Anomalies**      | AWS Cost Anomaly Detection      | -              | Detección automática picos |

> El uso de tecnologías no listadas requiere aprobación de Arquitectura.

---

## 4. Requisitos Obligatorios 🔴

### Configuración de Budgets

- [ ] **Budget mensual** por cuenta AWS (dev, staging, prod)
- [ ] **Budget por servicio** para componentes críticos (ECS, RDS, S3)
- [ ] **Umbrales escalonados**: 50%, 80%, 100%, 120% del presupuesto
- [ ] **Notificaciones SNS** a equipos responsables (email + Slack)
- [ ] **Cost Anomaly Detection** habilitado con alertas
- [ ] **Tags obligatorios** para atribución de costos

### Thresholds y Notificaciones

| Threshold | Severidad | Notificación               | Acción                        |
| --------- | --------- | -------------------------- | ----------------------------- |
| 50%       | INFO      | Email team lead            | Revisión semanal              |
| 80%       | WARNING   | Email + Slack              | Reunión urgente               |
| 100%      | CRITICAL  | Email + Slack + call       | Congelar recursos no críticos |
| 120%      | BLOCKER   | Email + Slack + escalation | Apagar recursos dev/staging   |

### Responsabilidades

- [ ] **Platform Team**: Configurar budgets globales
- [ ] **Team Leads**: Definir presupuestos por proyecto
- [ ] **Developers**: Responder a alertas 80%+ en <4 horas
- [ ] **FinOps (si existe)**: Revisar anomalías semanalmente

---

## 5. Terraform - Budget con Alertas Múltiples

```hcl
# budgets.tf
resource "aws_budgets_budget" "monthly_account" {
  name         = "monthly-${var.environment}-budget"
  budget_type  = "COST"
  limit_amount = var.monthly_budget_limit
  limit_unit   = "USD"
  time_unit    = "MONTHLY"

  cost_filter {
    name = "TagKeyValue"
    values = [
      "Environment$${var.environment}"
    ]
  }

  # Alerta 50%
  notification {
    comparison_operator       = "GREATER_THAN"
    threshold                 = 50
    threshold_type            = "PERCENTAGE"
    notification_type         = "FORECASTED"
    subscriber_email_addresses = var.team_emails
    subscriber_sns_topic_arns  = [aws_sns_topic.cost_alerts.arn]
  }

  # Alerta 80%
  notification {
    comparison_operator       = "GREATER_THAN"
    threshold                 = 80
    threshold_type            = "PERCENTAGE"
    notification_type         = "ACTUAL"
    subscriber_email_addresses = concat(var.team_emails, var.leadership_emails)
    subscriber_sns_topic_arns  = [aws_sns_topic.cost_alerts_critical.arn]
  }

  # Alerta 100%
  notification {
    comparison_operator       = "GREATER_THAN"
    threshold                 = 100
    threshold_type            = "PERCENTAGE"
    notification_type         = "ACTUAL"
    subscriber_email_addresses = concat(var.team_emails, var.leadership_emails, var.finops_emails)
    subscriber_sns_topic_arns  = [aws_sns_topic.cost_alerts_critical.arn]
  }

  # Alerta 120% (escalation)
  notification {
    comparison_operator       = "GREATER_THAN"
    threshold                 = 120
    threshold_type            = "PERCENTAGE"
    notification_type         = "ACTUAL"
    subscriber_email_addresses = var.executive_emails
    subscriber_sns_topic_arns  = [aws_sns_topic.cost_alerts_critical.arn]
  }

  tags = {
    Environment = var.environment
    ManagedBy   = "terraform"
    CostCenter  = "platform-engineering"
  }
}

# Budget por servicio (ejemplo: ECS Fargate)
resource "aws_budgets_budget" "ecs_fargate" {
  name         = "ecs-fargate-${var.environment}"
  budget_type  = "COST"
  limit_amount = "500"
  limit_unit   = "USD"
  time_unit    = "MONTHLY"

  cost_filter {
    name = "Service"
    values = [
      "Amazon Elastic Container Service"
    ]
  }

  cost_filter {
    name = "TagKeyValue"
    values = [
      "Environment$${var.environment}"
    ]
  }

  notification {
    comparison_operator       = "GREATER_THAN"
    threshold                 = 80
    threshold_type            = "PERCENTAGE"
    notification_type         = "ACTUAL"
    subscriber_email_addresses = var.platform_team_emails
    subscriber_sns_topic_arns  = [aws_sns_topic.cost_alerts.arn]
  }
}

# SNS Topic para alertas
resource "aws_sns_topic" "cost_alerts" {
  name = "cost-alerts-${var.environment}"

  tags = {
    Purpose = "Cost budget notifications"
  }
}

resource "aws_sns_topic_subscription" "slack" {
  topic_arn = aws_sns_topic.cost_alerts.arn
  protocol  = "https"
  endpoint  = var.slack_webhook_url
}
```

---

## 6. Cost Anomaly Detection

```hcl
# anomaly-detection.tf
resource "aws_ce_anomaly_monitor" "service_monitor" {
  name              = "service-anomaly-monitor-${var.environment}"
  monitor_type      = "DIMENSIONAL"
  monitor_dimension = "SERVICE"

  tags = {
    Environment = var.environment
  }
}

resource "aws_ce_anomaly_subscription" "alerts" {
  name      = "anomaly-alerts-${var.environment}"
  frequency = "DAILY"

  monitor_arn_list = [
    aws_ce_anomaly_monitor.service_monitor.arn
  ]

  subscriber {
    type    = "EMAIL"
    address = var.finops_email
  }

  subscriber {
    type    = "SNS"
    address = aws_sns_topic.cost_alerts.arn
  }

  threshold_expression {
    dimension {
      key           = "ANOMALY_TOTAL_IMPACT_ABSOLUTE"
      values        = ["100"]
      match_options = ["GREATER_THAN_OR_EQUAL"]
    }
  }
}
```

---

## 7. Dashboard Grafana - Cost Monitoring

```yaml
# grafana-cost-dashboard.yaml
apiVersion: 1
dashboards:
  - name: AWS Cost Monitoring
    folder: FinOps
    panels:
      - title: Monthly Cost Trend
        type: graph
        datasource: CloudWatch
        targets:
          - namespace: AWS/Billing
            metricName: EstimatedCharges
            dimensions:
              Currency: USD
            period: 86400

      - title: Cost by Service
        type: pie
        datasource: Athena
        query: |
          SELECT line_item_product_code, SUM(line_item_unblended_cost) as cost
          FROM cost_usage_report
          WHERE line_item_usage_start_date >= date_trunc('month', current_date)
          GROUP BY line_item_product_code
          ORDER BY cost DESC
          LIMIT 10

      - title: Budget vs Actual
        type: bargauge
        datasource: CloudWatch
        targets:
          - expression: m1/m2*100
            label: Budget %
```

---

## 8. Validación de Cumplimiento

```bash
# Verificar budgets configurados
aws budgets describe-budgets --account-id $AWS_ACCOUNT_ID

# Verificar anomaly detection activo
aws ce get-anomaly-monitors

# Listar suscripciones de alertas
aws budgets describe-notifications-for-budget \
  --account-id $AWS_ACCOUNT_ID \
  --budget-name monthly-prod-budget

# Simular notificación (testing)
aws sns publish \
  --topic-arn $COST_ALERT_SNS_ARN \
  --subject "Test: Budget Alert" \
  --message "Testing cost alert notification"
```

---

## 9. Referencias

**AWS:**

- [AWS Budgets Best Practices](https://docs.aws.amazon.com/cost-management/latest/userguide/budgets-best-practices.html)
- [Cost Anomaly Detection](https://docs.aws.amazon.com/cost-management/latest/userguide/manage-ad.html)

**FinOps:**

- [FinOps Foundation - Cost Alerting](https://www.finops.org/framework/capabilities/cost-allocation/)
- [Cloud Cost Optimization Playbook](https://aws.amazon.com/aws-cost-management/)
