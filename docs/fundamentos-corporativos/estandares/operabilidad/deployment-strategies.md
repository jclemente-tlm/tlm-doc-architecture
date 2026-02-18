---
id: deployment-strategies
sidebar_position: 4
title: Deployment Strategies
description: Estrategias de despliegue seguro - blue/green, canary, rolling - para minimizar riesgo
---

# Deployment Strategies

## Contexto

Este estándar define **Deployment Strategies**: técnicas para desplegar nuevas versiones minimizando **riesgo** y **downtime**. Deployment directo (replace all) genera downtime y rollback lento. Estrategias graduales permiten detectar problemas rápidamente. Complementa el [lineamiento de CI/CD Pipelines](../../lineamientos/operabilidad/01-cicd-pipelines.md) con **patrones de despliegue seguro**.

---

## Concepto Fundamental

```yaml
# Deployment Strategies Comparison

1. Recreate (❌ High Risk):

   Step 1: Stop all v1 tasks → DOWNTIME starts
   Step 2: Deploy v2 tasks
   Step 3: Start v2 tasks → Service available

   Downtime: 2-5 minutes (unacceptable for prod)
   Rollback: Slow (redeploy v1)
   Risk: High (all users affected immediately)
   Use Case: Dev environment only

2. Rolling Update (⚠️ Medium Risk):

   Step 1: Deploy 1 v2 task (v1: 4 tasks, v2: 1 task)
   Step 2: Health check passes → Deploy next
   Step 3: Continue until all v2 (v1: 0 tasks, v2: 5 tasks)

   Downtime: Zero
   Rollback: Medium speed (reverse rolling)
   Risk: Medium (gradual migration, but both versions coexist)
   Use Case: Default for most services

3. Blue/Green (✅ Low Risk, High Cost):

   Blue (v1): 4 tasks running (current production)
   Green (v2): 4 tasks deployed (standby)

   Step 1: Deploy v2 to Green environment
   Step 2: Test Green environment
   Step 3: Switch traffic: Blue → Green (instant)
   Step 4: Monitor, if OK → Terminate Blue

   Downtime: Zero
   Rollback: Instant (switch back to Blue)
   Risk: Low (full test before switch)
   Cost: High (2x infrastructure during deployment)
   Use Case: Critical services, major releases

4. Canary (✅ Lowest Risk, Complex):

   Step 1: Deploy v2 to 1 task (5% traffic)
   Step 2: Monitor metrics for 10 min
   Step 3: If OK → Increase to 25% (2 tasks)
   Step 4: If OK → Increase to 50% (3 tasks)
   Step 5: If OK → Increase to 100% (all tasks)

   Downtime: Zero
   Rollback: Instant (route 100% to v1)
   Risk: Lowest (gradual exposure, early detection)
   Complexity: High (requires progressive traffic routing)
   Use Case: High-traffic services, risky changes
```

## Rolling Update (Default)

```yaml
# ✅ Rolling Update with ECS

# ECS Service Configuration
resource "aws_ecs_service" "sales" {
  name            = "sales-service"
  cluster         = aws_ecs_cluster.production.id
  task_definition = aws_ecs_task_definition.sales.arn
  desired_count   = 4

  deployment_configuration {
    minimum_healthy_percent = 75   # ✅ Keep 3/4 tasks during deploy
    maximum_percent         = 150  # ✅ Can have 6 tasks max (4 + 2 new)
  }

  # ✅ Health check before routing traffic
  health_check_grace_period_seconds = 60

  load_balancer {
    target_group_arn = aws_lb_target_group.sales.arn
    container_name   = "sales-service"
    container_port   = 8080
  }
}

# Deployment Flow

Initial State:
  - Tasks: v1.0.0 (4 running)
  - Traffic: 100% → v1.0.0

Deploy v1.1.0:

  Step 1: ECS starts 1 new task (v1.1.0)
    - Tasks: v1.0.0 (4), v1.1.0 (1) → Total 5 (125%)

  Step 2: Health check v1.1.0
    - ECS waits for health check to pass (30s)
    - ALB sends test requests
    - If 2 consecutive success → Healthy

  Step 3: ALB starts routing to v1.1.0
    - Traffic: v1.0.0 (80%), v1.1.0 (20%)

  Step 4: ECS stops 1 old task (v1.0.0)
    - Connection draining (30s)
    - Tasks: v1.0.0 (3), v1.1.0 (1) → Total 4

  Step 5: Repeat steps 1-4 until all v1.1.0
    - Final: v1.1.0 (4 running)
    - Traffic: 100% → v1.1.0

Total Time: ~10 minutes (4 tasks × 2.5 min each)

Rollback (if v1.1.0 fails):

  Option 1: Redeploy v1.0.0 (slow, ~10 min)
    aws ecs update-service --task-definition sales-service:42

  Option 2: Scale down v1.1.0, scale up v1.0.0 (faster, ~3 min)
```

## Blue/Green Deployment

```yaml
# ✅ Blue/Green with ECS + ALB

Architecture:

  ALB (single)
    ├─► Target Group Blue (port 8080) → ECS Service Blue (v1.0.0)
    └─► Target Group Green (port 8080) → ECS Service Green (standby)

# Terraform Configuration

resource "aws_lb_listener" "sales" {
  load_balancer_arn = aws_lb.main.arn
  port              = "443"
  protocol          = "HTTPS"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.blue.arn  # ✅ Initially Blue
  }
}

resource "aws_lb_target_group" "blue" {
  name     = "sales-blue"
  port     = 8080
  protocol = "HTTP"
  vpc_id   = aws_vpc.main.id

  health_check {
    path                = "/health"
    interval            = 30
    timeout             = 5
    healthy_threshold   = 2
    unhealthy_threshold = 2
  }
}

resource "aws_lb_target_group" "green" {
  name     = "sales-green"
  port     = 8080
  protocol = "HTTP"
  vpc_id   = aws_vpc.main.id

  health_check {
    path                = "/health"
    interval            = 30
    timeout             = 5
    healthy_threshold   = 2
    unhealthy_threshold = 2
  }
}

resource "aws_ecs_service" "sales_blue" {
  name            = "sales-blue"
  cluster         = aws_ecs_cluster.production.id
  task_definition = "sales-service:42"  # v1.0.0
  desired_count   = 4

  load_balancer {
    target_group_arn = aws_lb_target_group.blue.arn
    container_name   = "sales-service"
    container_port   = 8080
  }
}

resource "aws_ecs_service" "sales_green" {
  name            = "sales-green"
  cluster         = aws_ecs_cluster.production.id
  task_definition = "sales-service:43"  # v1.1.0 (new)
  desired_count   = 0  # ✅ Initially 0 (standby)

  load_balancer {
    target_group_arn = aws_lb_target_group.green.arn
    container_name   = "sales-service"
    container_port   = 8080
  }
}

# Deployment Script

#!/bin/bash
set -e

echo "Step 1: Deploy to Green environment"
aws ecs update-service \
  --cluster production \
  --service sales-green \
  --task-definition sales-service:43 \
  --desired-count 4

echo "Waiting for Green tasks to be healthy..."
aws ecs wait services-stable \
  --cluster production \
  --services sales-green

echo "Step 2: Test Green environment"
GREEN_URL="http://green.internal.talma.com"
curl -f ${GREEN_URL}/health || exit 1
curl -f ${GREEN_URL}/api/orders | jq '.total' || exit 1

echo "Step 3: Run smoke tests"
pytest tests/smoke/test_api.py --url=${GREEN_URL}

echo "Step 4: Switch traffic to Green"
aws elbv2 modify-listener \
  --listener-arn arn:aws:elasticloadbalancing:us-east-1:123456789012:listener/app/main/abc123/def456 \
  --default-actions Type=forward,TargetGroupArn=arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/sales-green/xyz789

echo "✅ Traffic switched to Green (v1.1.0)"

echo "Step 5: Monitor for 10 minutes"
sleep 600

ERROR_RATE=$(aws cloudwatch get-metric-statistics \
  --namespace AWS/ApplicationELB \
  --metric-name HTTPCode_Target_5XX_Count \
  --dimensions Name=TargetGroup,Value=sales-green \
  --start-time $(date -u -d '10 minutes ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 600 \
  --statistics Sum \
  --query 'Datapoints[0].Sum')

if [ "$ERROR_RATE" -gt 10 ]; then
  echo "❌ High error rate detected, rolling back..."
  aws elbv2 modify-listener \
    --listener-arn ... \
    --default-actions Type=forward,TargetGroupArn=...sales-blue...
  exit 1
fi

echo "Step 6: Scale down Blue environment"
aws ecs update-service \
  --cluster production \
  --service sales-blue \
  --desired-count 0

echo "✅ Deployment complete. Green is now production."
```

## Canary Deployment

```yaml
# ✅ Canary with ALB Weighted Target Groups

# ALB Listener Rule (Weighted Routing)

resource "aws_lb_listener_rule" "canary" {
  listener_arn = aws_lb_listener.sales.arn
  priority     = 100

  action {
    type = "forward"

    forward {
      target_group {
        arn    = aws_lb_target_group.stable.arn
        weight = 95  # ✅ 95% traffic to stable (v1.0.0)
      }

      target_group {
        arn    = aws_lb_target_group.canary.arn
        weight = 5   # ✅ 5% traffic to canary (v1.1.0)
      }

      stickiness {
        enabled  = true
        duration = 3600  # ✅ Session stickiness (1h)
      }
    }
  }

  condition {
    path_pattern {
      values = ["/*"]
    }
  }
}

# Canary Deployment Script (Progressive)

#!/bin/bash
set -e

CANARY_STAGES=(5 10 25 50 100)
MONITORING_DURATION=600  # 10 minutes per stage

echo "Starting canary deployment..."

for WEIGHT in "${CANARY_STAGES[@]}"; do
  echo "Stage: Canary weight = ${WEIGHT}%"

  # Update ALB weights
  STABLE_WEIGHT=$((100 - WEIGHT))

  aws elbv2 modify-rule \
    --rule-arn arn:aws:elasticloadbalancing:...:listener-rule/... \
    --actions Type=forward,ForwardConfig="{
      TargetGroups=[
        {TargetGroupArn=arn:.../stable,Weight=${STABLE_WEIGHT}},
        {TargetGroupArn=arn:.../canary,Weight=${WEIGHT}}
      ],
      TargetGroupStickinessConfig={Enabled=true,DurationSeconds=3600}
    }"

  echo "Monitoring for ${MONITORING_DURATION}s..."
  sleep ${MONITORING_DURATION}

  # Check metrics
  ERROR_RATE_STABLE=$(get_error_rate "stable")
  ERROR_RATE_CANARY=$(get_error_rate "canary")

  LATENCY_P95_STABLE=$(get_latency_p95 "stable")
  LATENCY_P95_CANARY=$(get_latency_p95 "canary")

  echo "Metrics:"
  echo "  Stable: Error Rate=${ERROR_RATE_STABLE}%, Latency P95=${LATENCY_P95_STABLE}ms"
  echo "  Canary: Error Rate=${ERROR_RATE_CANARY}%, Latency P95=${LATENCY_P95_CANARY}ms"

  # Validation
  if [ "$ERROR_RATE_CANARY" -gt 1 ]; then
    echo "❌ Canary error rate > 1%, rolling back..."
    rollback_to_stable
    exit 1
  fi

  if [ "$LATENCY_P95_CANARY" -gt 1000 ]; then
    echo "❌ Canary latency > 1000ms, rolling back..."
    rollback_to_stable
    exit 1
  fi

  echo "✅ Stage passed, continuing..."
done

echo "✅ Canary deployment successful. 100% traffic on v1.1.0"
```

## Feature Flags (A/B Testing)

```yaml
# ✅ Feature Flag for Gradual Rollout

# Application-level canary (not infrastructure)

public class OrderService : IOrderService
{
    private readonly IFeatureFlagService _featureFlags;

    public async Task<Order> CreateOrderAsync(CreateOrderCommand cmd)
    {
        // ✅ Check feature flag (user-level canary)
        bool useNewPricingEngine = await _featureFlags.IsEnabledAsync(
            "new-pricing-engine",
            context: new
            {
                UserId = cmd.UserId,
                Country = cmd.Country
            });

        if (useNewPricingEngine)
        {
            // ✅ New version (10% of users)
            return await _newPricingService.CalculatePriceAsync(cmd);
        }
        else
        {
            // ✅ Old version (90% of users)
            return await _oldPricingService.CalculatePriceAsync(cmd);
        }
    }
}

# LaunchDarkly Configuration

Feature Flag: new-pricing-engine
  Status: Enabled

  Targeting:
    Rule 1: Country = "PE" → 10% enabled (canary in Peru)
    Rule 2: Country = "CL" → 0% enabled (not yet)
    Rule 3: User ID in ["test-user-1", "test-user-2"] → 100% (internal testing)

  Fallback: false (old version)

Benefits:
  ✅ Instant rollback (flip flag to false)
  ✅ User-level targeting (not just %)
  ✅ No deployment required (runtime change)
  ✅ Metrics per variant (A/B testing)
```

## Rollback Strategies

```yaml
# ✅ Fast Rollback Options

1. Rolling Update Rollback (Slow):

   aws ecs update-service \
     --cluster production \
     --service sales-service \
     --task-definition sales-service:42  # ← Previous version

   Time: ~10 minutes (same as deployment)
   Risk: Medium (rolling process)

2. Blue/Green Rollback (Instant):

   aws elbv2 modify-listener \
     --listener-arn ... \
     --default-actions Type=forward,TargetGroupArn=...blue...

   Time: < 5 seconds (traffic switch)
   Risk: Low (instant)

3. Canary Rollback (Instant):

   aws elbv2 modify-rule \
     --rule-arn ... \
     --actions Type=forward,ForwardConfig="{
       TargetGroups=[{TargetGroupArn=.../stable,Weight=100}]
     }"

   Time: < 5 seconds (route 100% to stable)
   Risk: Low (instant)

4. Feature Flag Rollback (Instant):

   curl -X PATCH https://app.launchdarkly.com/api/v2/flags/default/new-pricing-engine \
     -H "Authorization: ${LD_API_KEY}" \
     -d '{"environmentKey":"production","instructions":[{"kind":"turnFlagOff"}]}'

   Time: < 1 second (runtime change)
   Risk: None (no infrastructure change)

Recommendation:
  - Critical services: Blue/Green (instant rollback)
  - High-traffic services: Canary (gradual + instant rollback)
  - Feature changes: Feature Flags (instant + no deploy)
  - Default: Rolling (simple, zero downtime)
```

## Monitoring During Deployment

```yaml
# ✅ Metrics to Watch During Deployment

Golden Signals:

  1. Latency (p50, p95, p99):
     - Target: p95 < 500ms
     - Alert: p95 > 1000ms → Rollback

  2. Error Rate:
     - Target: < 0.1%
     - Alert: > 1% → Rollback

  3. Throughput (Requests/sec):
     - Baseline: 100 RPS
     - Alert: Drop > 20% → Investigate

  4. Saturation (CPU, Memory):
     - Target: < 70%
     - Alert: > 85% → Scale or rollback

# CloudWatch Alarms

resource "aws_cloudwatch_metric_alarm" "deployment_high_errors" {
  alarm_name          = "sales-deployment-high-errors"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "HTTPCode_Target_5XX_Count"
  namespace           = "AWS/ApplicationELB"
  period              = "60"
  statistic           = "Sum"
  threshold           = "10"
  alarm_description   = "Deployment causing high errors"

  dimensions = {
    TargetGroup = aws_lb_target_group.canary.arn_suffix
  }

  alarm_actions = [aws_sns_topic.deployment_alerts.arn]
}

# Compare Canary vs Stable

#!/bin/bash
compare_metrics() {
  STABLE_ERRORS=$(get_metric "stable" "5XX")
  CANARY_ERRORS=$(get_metric "canary" "5XX")

  # ✅ Canary errors should be similar to stable
  INCREASE=$((CANARY_ERRORS - STABLE_ERRORS))

  if [ "$INCREASE" -gt 5 ]; then
    echo "❌ Canary has $INCREASE more errors than stable"
    return 1
  fi

  return 0
}
```

---

## Requisitos Técnicos

### MUST (Obligatorio)

- **MUST** usar zero-downtime deployment (rolling/blue-green/canary)
- **MUST** implementar health checks (ECS health grace period)
- **MUST** monitorear error rate durante deployment
- **MUST** tener rollback plan (< 5 min para revertir)
- **MUST** usar connection draining (ALB deregistration delay)

### SHOULD (Fuertemente recomendado)

- **SHOULD** usar blue/green para servicios críticos
- **SHOULD** usar canary para high-traffic services
- **SHOULD** validar deployment automáticamente (error rate check)
- **SHOULD** implementar feature flags para cambios riesgosos

### MUST NOT (Prohibido)

- **MUST NOT** usar recreate strategy en producción (causes downtime)
- **MUST NOT** deploy sin health checks
- **MUST NOT** skip monitoring durante deployment
- **MUST NOT** deploy viernes tarde (weekend risk)

---

## Referencias

- [Lineamiento: CI/CD Pipelines](../../lineamientos/operabilidad/01-cicd-pipelines.md)
- [Rollback Automation](./rollback-automation.md)
- [Health Checks](../desarrollo/health-checks.md)
- [Feature Flags](../desarrollo/feature-flags.md)
- [Monitoring](./monitoring.md)
