---
id: rollback-automation
sidebar_position: 1
title: Rollback Automation
description: Automatización de rollbacks para recuperación rápida ante fallos en producción
---

# Rollback Automation

## Contexto

Este estándar define **Rollback Automation**: capacidad de **revertir automáticamente** despliegues cuando se detectan anomalías en producción. Reduce MTTR (Mean Time To Recovery) de horas a minutos. Complementa [Deployment Strategies](./deployment-strategies.md) y [Monitoring](./observability.md).

---

## Concepto Fundamental

```yaml
# ✅ Rollback Automation

Definition:
  Automatic reversion to previous stable version when deployment causes issues

Timeline (without automation):
  12:00 - Deploy v2.5.0 to production
  12:05 - Users report errors
  12:10 - Team investigates
  12:30 - Decision: Rollback
  12:45 - Manual rollback executed
  13:00 - Service stable
  MTTR: 60 minutes ❌

Timeline (with automation):
  12:00 - Deploy v2.5.0 to production
  12:05 - Automated health checks fail
  12:06 - Auto-rollback triggered
  12:08 - Service reverted to v2.4.3
  12:09 - Service stable
  MTTR: 9 minutes ✅

Benefits:
  - 🚀 Fast Recovery: Minutes instead of hours
  - 🤖 No Human Intervention: Auto-detection and rollback
  - 📊 Data-Driven: Metrics determine health
  - 🌙 24/7 Protection: Works outside business hours
```

## Rollback Triggers

```yaml
# ✅ Automatic Rollback Triggers

1. Health Check Failures:

  Condition: > 50% of instances failing health checks

  ECS Task Definition:
    healthCheck:
      command: ["CMD-SHELL", "curl -f http://localhost:5000/health || exit 1"]
      interval: 10s
      timeout: 5s
      retries: 3
      startPeriod: 60s

  Trigger:
    - Deploy v2.5.0
    - 3 consecutive health check failures
    - ECS marks task unhealthy
    - If > 50% tasks unhealthy → Rollback

2. Error Rate Spike:

  Condition: 5xx error rate > 5% for 5 minutes

  CloudWatch Alarm:
    MetricName: 5xxErrors
    Namespace: AWS/ApplicationELB
    Statistic: Sum
    Period: 300 (5 minutes)
    EvaluationPeriods: 1
    Threshold: 5% of total requests
    ComparisonOperator: GreaterThanThreshold
    TreatMissingData: notBreaching

  Actions:
    - Send SNS notification → Lambda function
    - Lambda triggers rollback via ECS UpdateService API
    - Revert to previous task definition

3. Latency Degradation:

  Condition: P99 latency > 2 seconds for 5 minutes

  CloudWatch Alarm:
    MetricName: TargetResponseTime
    Namespace: AWS/ApplicationELB
    Statistic: p99
    Period: 300
    EvaluationPeriods: 1
    Threshold: 2000 (2 seconds in ms)
    ComparisonOperator: GreaterThanThreshold

  Rollback: Immediate (performance regression)

4. Custom Business Metrics:

  Condition: Order completion rate < 90% for 10 minutes

  Custom Metric:
    orders_completed / orders_started < 0.90

  Implementation:
    app.Use(async (context, next) =>
    {
        var orderId = context.Request.Path.Value.Split('/').Last();
        _metrics.IncrementCounter("orders_started");

        await next();

        if (context.Response.StatusCode == 200)
            _metrics.IncrementCounter("orders_completed");

        var rate = _metrics.GetRatio("orders_completed", "orders_started");
        if (rate < 0.90)
            _metrics.PublishAlarm("OrderCompletionRate", rate);
    });

  Rollback: If sustained < 90% for 10 minutes

5. Dependency Failures:

  Condition: Database connection pool exhausted

  Symptoms:
    - ConnectionPoolExhaustedException
    - Timeouts connecting to PostgreSQL
    - Possible cause: Connection leak in new version

  Detection:
    CloudWatch Logs Insights query:
      fields @timestamp, @message
      | filter @message like /ConnectionPoolExhausted/
      | stats count() as failures by bin(5m)
      | filter failures > 10

  Rollback: Immediate (critical dependency failure)
```

## Rollback Implementation (ECS)

```yaml
# ✅ ECS Automated Rollback

CloudFormation Stack (ECS Service with Circuit Breaker):

  Resources:
    SalesService:
      Type: AWS::ECS::Service
      Properties:
        ServiceName: sales-service
        Cluster: !Ref ECSCluster
        TaskDefinition: !Ref TaskDefinition
        DesiredCount: 4

        # ✅ Circuit Breaker (Rollback on Failure)
        DeploymentConfiguration:
          MaximumPercent: 200
          MinimumHealthyPercent: 100

          # ✅ Enable Circuit Breaker
          DeploymentCircuitBreaker:
            Enable: true
            Rollback: true  # Auto-rollback on failure

        # ✅ Health Check Grace Period
        HealthCheckGracePeriodSeconds: 60

        LoadBalancers:
          - TargetGroupArn: !Ref TargetGroup
            ContainerName: sales-api
            ContainerPort: 5000

How it Works:

  1. Deploy new task definition (v2.5.0)
  2. ECS launches new tasks
  3. Wait 60s grace period (health check start period)
  4. Check task health (every 10s)
  5. If tasks fail health checks → Circuit breaker triggers
  6. ECS automatically reverts to previous task definition (v2.4.3)
  7. Old tasks remain running (rollback complete)

Logs:

  [2024-01-28 12:05:00] Deployment started (v2.5.0)
  [2024-01-28 12:05:30] Launched 4 new tasks
  [2024-01-28 12:06:30] Health check failed: 3/4 tasks unhealthy
  [2024-01-28 12:07:00] Circuit breaker triggered
  [2024-01-28 12:07:10] Rolling back to v2.4.3
  [2024-01-28 12:08:00] Rollback complete (service stable)
```

## Rollback Implementation (Blue-Green)

```yaml
# ✅ Blue-Green Automated Rollback

Terraform (ALB with Weighted Target Groups):

  resource "aws_lb_target_group" "blue" {
    name     = "sales-service-blue"
    port     = 5000
    protocol = "HTTP"
    vpc_id   = var.vpc_id

    health_check {
      path                = "/health"
      healthy_threshold   = 3
      unhealthy_threshold = 2
      timeout             = 5
      interval            = 10
    }
  }

  resource "aws_lb_target_group" "green" {
    name     = "sales-service-green"
    // Identical config
  }

  resource "aws_lb_listener_rule" "weighted" {
    listener_arn = aws_lb_listener.https.arn

    action {
      type = "forward"

      forward {
        target_group {
          arn    = aws_lb_target_group.blue.arn
          weight = var.blue_weight  # Initially 100
        }

        target_group {
          arn    = aws_lb_target_group.green.arn
          weight = var.green_weight  # Initially 0
        }

        stickiness {
          enabled  = true
          duration = 3600
        }
      }
    }
  }

Deployment Flow:

  1. Deploy new version to Green target group
  2. Automated health checks (Lambda function every 60s)
  3. Shift traffic: Blue 100% → Blue 90% Green 10%
  4. Wait 5 minutes, monitor metrics
  5. If Green healthy: Blue 50% Green 50%
  6. If Green unhealthy: ❌ ROLLBACK → Blue 100% Green 0%
  7. Continue until Green 100% (if all healthy)

Lambda Rollback Function:

  import boto3
  import json

  elbv2 = boto3.client('elbv2')
  cloudwatch = boto3.client('cloudwatch')

  def lambda_handler(event, context):
      listener_arn = event['listener_arn']
      blue_tg_arn = event['blue_tg_arn']
      green_tg_arn = event['green_tg_arn']

      # Get current weights
      response = elbv2.describe_rules(ListenerArn=listener_arn)
      current_green_weight = get_weight(response, green_tg_arn)

      # Check Green health
      green_healthy = check_health(green_tg_arn)

      if not green_healthy:
          print("🔴 Green unhealthy - Rolling back to Blue")

          # Revert to Blue 100%
          elbv2.modify_listener(
              ListenerArn=listener_arn,
              DefaultActions=[{
                  'Type': 'forward',
                  'ForwardConfig': {
                      'TargetGroups': [
                          {'TargetGroupArn': blue_tg_arn, 'Weight': 100},
                          {'TargetGroupArn': green_tg_arn, 'Weight': 0}
                      ]
                  }
              }]
          )

          # Send alert
          sns.publish(
              TopicArn='arn:aws:sns:us-east-1:123456789012:deployments',
              Subject='❌ Deployment Rollback',
              Message=f'Green deployment unhealthy. Rolled back to Blue.'
          )

          return {'status': 'rolled_back'}

      else:
          print("✅ Green healthy - Continue deployment")
          return {'status': 'healthy'}

  def check_health(target_group_arn):
      # Check CloudWatch metrics for last 5 minutes
      metrics = cloudwatch.get_metric_statistics(
          Namespace='AWS/ApplicationELB',
          MetricName='HTTPCode_Target_5XX_Count',
          Dimensions=[{'Name': 'TargetGroup', 'Value': target_group_arn}],
          StartTime=datetime.now() - timedelta(minutes=5),
          EndTime=datetime.now(),
          Period=300,
          Statistics=['Sum']
      )

      error_count = metrics['Datapoints'][0]['Sum'] if metrics['Datapoints'] else 0

      # Check P99 latency
      latency = cloudwatch.get_metric_statistics(
          Namespace='AWS/ApplicationELB',
          MetricName='TargetResponseTime',
          Dimensions=[{'Name': 'TargetGroup', 'Value': target_group_arn}],
          StartTime=datetime.now() - timedelta(minutes=5),
          EndTime=datetime.now(),
          Period=300,
          Statistics=['p99']
      )

      p99_latency = latency['Datapoints'][0]['p99'] if latency['Datapoints'] else 0

      # Health criteria
      is_healthy = error_count < 10 and p99_latency < 2.0

      return is_healthy

EventBridge Schedule (Run every 60 seconds during deployment):

  resource "aws_cloudwatch_event_rule" "deployment_monitor" {
    name                = "deployment-health-monitor"
    schedule_expression = "rate(1 minute)"

    # Enable only during deployments
    is_enabled = var.deployment_in_progress
  }

  resource "aws_cloudwatch_event_target" "lambda" {
    rule      = aws_cloudwatch_event_rule.deployment_monitor.name
    target_id = "DeploymentHealthCheck"
    arn       = aws_lambda_function.health_check.arn
  }
```

## Rollback Implementation (Canary)

```yaml
# ✅ Canary Automated Rollback

Deployment Pipeline (GitHub Actions):
  name: Canary Deployment with Auto-Rollback

  jobs:
    deploy-canary:
      runs-on: ubuntu-latest
      steps:
        - name: Deploy Canary (10%)
          run: |
            aws elbv2 modify-listener --listener-arn $LISTENER_ARN \
              --default-actions Type=forward,ForwardConfig='{
                "TargetGroups": [
                  {"TargetGroupArn": "$BASELINE_TG", "Weight": 90},
                  {"TargetGroupArn": "$CANARY_TG", "Weight": 10}
                ]
              }'

        - name: Wait 5 minutes
          run: sleep 300

        - name: Check Canary Health
          id: health_check
          run: |
            ERROR_RATE=$(aws cloudwatch get-metric-statistics \
              --namespace AWS/ApplicationELB \
              --metric-name HTTPCode_Target_5XX_Count \
              --dimensions Name=TargetGroup,Value=$CANARY_TG \
              --start-time $(date -u -d '5 minutes ago' +%Y-%m-%dT%H:%M:%S) \
              --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
              --period 300 \
              --statistics Sum \
              --query 'Datapoints[0].Sum' \
              --output text)

            BASELINE_ERROR_RATE=$(aws cloudwatch get-metric-statistics \
              --namespace AWS/ApplicationELB \
              --metric-name HTTPCode_Target_5XX_Count \
              --dimensions Name=TargetGroup,Value=$BASELINE_TG \
              --start-time $(date -u -d '5 minutes ago' +%Y-%m-%dT%H:%M:%S) \
              --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
              --period 300 \
              --statistics Sum \
              --query 'Datapoints[0].Sum' \
              --output text)

            # Rollback if Canary error rate > Baseline + 0.5%
            if (( $(echo "$ERROR_RATE > $BASELINE_ERROR_RATE + 5" | bc -l) )); then
              echo "🔴 Canary error rate too high: $ERROR_RATE vs $BASELINE_ERROR_RATE"
              echo "rollback=true" >> $GITHUB_OUTPUT
            else
              echo "✅ Canary healthy"
              echo "rollback=false" >> $GITHUB_OUTPUT
            fi

        - name: Rollback to Baseline
          if: steps.health_check.outputs.rollback == 'true'
          run: |
            echo "❌ Rolling back to baseline"
            aws elbv2 modify-listener --listener-arn $LISTENER_ARN \
              --default-actions Type=forward,ForwardConfig='{
                "TargetGroups": [
                  {"TargetGroupArn": "$BASELINE_TG", "Weight": 100},
                  {"TargetGroupArn": "$CANARY_TG", "Weight": 0}
                ]
              }'

            # Send alert
            aws sns publish \
              --topic-arn $SNS_TOPIC_ARN \
              --subject "❌ Canary Deployment Failed" \
              --message "Canary error rate exceeded threshold. Rolled back to baseline."

            exit 1

        - name: Increase Canary to 50%
          if: steps.health_check.outputs.rollback == 'false'
          run: |
            echo "✅ Proceeding to 50% canary"
            aws elbv2 modify-listener --listener-arn $LISTENER_ARN \
              --default-actions Type=forward,ForwardConfig='{
                "TargetGroups": [
                  {"TargetGroupArn": "$BASELINE_TG", "Weight": 50},
                  {"TargetGroupArn": "$CANARY_TG", "Weight": 50}
                ]
              }'

        # Repeat health check for 50% phase, then 100%
```

## Database Migration Rollback

```yaml
# ✅ Database Rollback Strategy

Forward-Only Migrations (Preferred):

  # ✅ Add column (backward compatible)

  Migration 001_AddDiscountColumn.sql:
    ALTER TABLE orders
    ADD COLUMN discount DECIMAL(10,2) NULL DEFAULT 0;

  Rollback: NOT NEEDED (new column nullable, doesn't break old code)

  # ✅ Add table (backward compatible)

  Migration 002_CreatePromotionsTable.sql:
    CREATE TABLE promotions (
      id UUID PRIMARY KEY,
      code VARCHAR(50) UNIQUE,
      discount_percent INT
    );

  Rollback: NOT NEEDED (old code ignores new table)

Backward-Compatible Changes:

  # ✅ Rename column (2-phase migration)

  Phase 1 (Deploy v2.5.0):
    Migration 003_AddNewColumn.sql:
      ALTER TABLE orders ADD COLUMN customer_email VARCHAR(255);
      UPDATE orders SET customer_email = email;  -- Copy data

    Code: Write to BOTH columns (customer_email, email)

  Phase 2 (Deploy v2.6.0, after v2.5.0 stable):
    Migration 004_DropOldColumn.sql:
      ALTER TABLE orders DROP COLUMN email;

    Code: Write only to customer_email

  Rollback: Revert to v2.5.0 (both columns present, no data loss)

Breaking Changes (Require Coordination):

  # ⚠️ Change column type (requires downtime or careful migration)

  Migration 005_ChangeOrderTotalType.sql:
    -- Bad: ALTER TABLE orders ALTER COLUMN total TYPE DECIMAL(12,2);
    -- Breaks old code expecting INT

  Better Approach:
    1. Add new column: total_decimal DECIMAL(12,2)
    2. Populate: UPDATE orders SET total_decimal = total / 100.0
    3. Deploy code reading from total_decimal
    4. Drop old column: DROP COLUMN total

  Rollback: Revert to step 2 (both columns exist)

Migration Rollback Script:

  # Entity Framework Core

  dotnet ef migrations add AddDiscountColumn
  dotnet ef database update  # Apply migration

  # Rollback (if needed)
  dotnet ef database update PreviousMigrationName

  # Flyway

  flyway migrate  # Apply pending migrations
  flyway undo     # Rollback last migration (requires Flyway Teams)

  # Custom rollback script (stored in repo)

  migrations/
    001_add_discount_column_up.sql
    001_add_discount_column_down.sql  # Rollback script

  # Apply
  psql < 001_add_discount_column_up.sql

  # Rollback
  psql < 001_add_discount_column_down.sql
```

## Monitoring Rollbacks

```yaml
# ✅ Rollback Metrics & Alerts

CloudWatch Dashboard:
  Widgets:
    - Deployment Timeline:
        Type: Line graph
        Metrics:
          - DeploymentStarted (annotation)
          - DeploymentCompleted (annotation)
          - RollbackTriggered (annotation)

    - Error Rate:
        Type: Line graph
        Metrics:
          - 5xx Error Rate (before/after deployment)
          - Threshold line (5%)

    - Latency:
        Type: Line graph
        Metrics:
          - P50 Latency
          - P99 Latency
          - Threshold line (2s)

    - Rollback Count:
        Type: Number
        Metric: Sum(RollbackTriggered) last 30 days

SNS Notifications:
  RollbackTriggered:
    Subject: ❌ Deployment Rollback - Sales Service
    Message: |
      Service: sales-service
      Version: v2.5.0
      Trigger: Health check failures (3/4 tasks unhealthy)
      Action: Auto-rollback to v2.4.3
      Status: Rollback complete
      Time: 2024-01-28 12:08:00 UTC
      MTTR: 8 minutes

      Logs: https://console.aws.amazon.com/cloudwatch/logs/...
      Metrics: https://console.aws.amazon.com/cloudwatch/dashboards/...

    Recipients:
      - DevOps team
      - On-call engineer
      - Tech lead

SLI (Service Level Indicator):
  Deployment Success Rate:
    Formula: (Successful Deployments) / (Total Deployments) * 100
    Target: ≥ 95%

    Example:
      January 2024: 18 deployments, 1 rollback = 94.4% ⚠️
      Action: Investigate root cause of rollback

MTTR (Mean Time To Recovery):
  Manual Rollback (Before Automation):
    Average: 60 minutes

  Automated Rollback (After Automation):
    Average: 8 minutes

  Improvement: 87% reduction in MTTR ✅
```

---

## Requisitos Técnicos

### MUST (Obligatorio)

- **MUST** implementar automated rollback para servicios críticos (payments, orders)
- **MUST** configurar health checks (intervalo ≤ 10s, timeout ≤ 5s)
- **MUST** definir rollback triggers claros (error rate > 5%, P99 latency > 2s)
- **MUST** usar ECS Circuit Breaker o equivalente (auto-rollback on failure)
- **MUST** enviar notificación cuando rollback se ejecuta (SNS → Slack/email)
- **MUST** usar backward-compatible database migrations (no breaking changes)

### SHOULD (Fuertemente recomendado)

- **SHOULD** monitorear custom business metrics (order completion rate, payment success)
- **SHOULD** implementar Blue-Green o Canary para deployments críticos
- **SHOULD** validar health durante grace period (60s start period)
- **SHOULD** mantener MTTR < 15 minutes con automated rollback
- **SHOULD** mantener deployment success rate > 95%

### MUST NOT (Prohibido)

- **MUST NOT** desplegar sin automated rollback en producción (servicios críticos)
- **MUST NOT** ignorar health check failures (siempre investigar causa)
- **MUST NOT** hacer database migrations breaking sin plan de rollback
- **MUST NOT** desactivar Circuit Breaker para "agilizar" deployment

---

## Referencias

- [Deployment Strategies](./deployment-strategies.md)
- [Health Check Patterns](./health-check-patterns.md)
- [Observability](./observability.md)
- [Infrastructure as Code](./infrastructure-as-code.md)
- [Database Migration Patterns](../datos/database-migration.md)
