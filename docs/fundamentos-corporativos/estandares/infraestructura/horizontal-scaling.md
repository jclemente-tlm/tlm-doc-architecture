---
id: horizontal-scaling
sidebar_position: 1
title: Auto-Scaling Horizontal Basado en Métricas
description: Escalado horizontal automático con AWS ECS Fargate
---

# Auto-Scaling Horizontal Basado en Métricas

## Contexto

Este estándar define cómo configurar auto-scaling horizontal basado en métricas para manejar variaciones de carga automáticamente. Complementa el [lineamiento de Escalabilidad y Rendimiento](../../lineamientos/arquitectura/05-escalabilidad-y-rendimiento.md) y el estándar de [Diseño Stateless](../../estandares/arquitectura/stateless-design.md) especificando **cómo escalar instancias dinámicamente**.

---

## Stack Tecnológico

| Componente        | Tecnología                    | Versión | Uso                          |
| ----------------- | ----------------------------- | ------- | ---------------------------- |
| **Orchestration** | AWS ECS Fargate               | 1.4+    | Orquestación de contenedores |
| **Auto-Scaling**  | ECS Service Auto Scaling      | -       | Escalado automático          |
| **Métricas**      | AWS CloudWatch                | -       | Fuente de métricas           |
| **Load Balancer** | AWS Application Load Balancer | -       | Distribución de tráfico      |

---

## Implementación Técnica

### Tipos de Auto-Scaling

```yaml
# ✅ Target Tracking Scaling - Más simple y recomendado
Target Tracking:
  - Define métrica objetivo (ej: CPU = 70%)
  - AWS ajusta instancias automáticamente para mantener objetivo
  - Mejor para: cargas predecibles, métricas estándar

# ✅ Step Scaling - Más control
Step Scaling:
  - Define alarmas con múltiples thresholds
  - Respuestas graduales basadas en severidad
  - Mejor para: cargas variables, respuesta rápida a spikes

# ✅ Scheduled Scaling - Cargas predecibles
Scheduled Scaling:
  - Escala en horarios específicos
  - Combinable con otros métodos
  - Mejor para: patrones diarios/semanales conocidos
```

### Configuración de ECS Service (Terraform)

```hcl
# ECS Service
resource "aws_ecs_service" "orders_api" {
  name            = "orders-api"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.orders_api.arn
  desired_count   = 3  # Inicial: 3 instancias
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = var.private_subnet_ids
    security_groups  = [aws_security_group.orders_api.id]
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.orders_api.arn
    container_name   = "orders-api"
    container_port   = 8080
  }

  # ✅ Deployment configuration
  deployment_configuration {
    minimum_healthy_percent = 100  # Zero downtime
    maximum_percent         = 200  # Puede duplicar temporalmente
  }

  # ✅ Health check grace period
  health_check_grace_period_seconds = 60

  # ✅ Circuit breaker para rollback automático
  deployment_circuit_breaker {
    enable   = true
    rollback = true
  }

  lifecycle {
    ignore_changes = [desired_count]  # Managed by auto-scaling
  }
}
```

### Target Tracking Scaling - CPU

```hcl
# Auto-scaling target
resource "aws_appautoscaling_target" "orders_api" {
  max_capacity       = 20  # Máximo 20 instancias
  min_capacity       = 3   # Mínimo 3 instancias (HA)
  resource_id        = "service/${aws_ecs_cluster.main.name}/${aws_ecs_service.orders_api.name}"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"
}

# Policy: CPU Utilization
resource "aws_appautoscaling_policy" "orders_api_cpu" {
  name               = "orders-api-cpu-scaling"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.orders_api.resource_id
  scalable_dimension = aws_appautoscaling_target.orders_api.scalable_dimension
  service_namespace  = aws_appautoscaling_target.orders_api.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageCPUUtilization"
    }

    target_value       = 70.0  # Mantener CPU ~70%
    scale_in_cooldown  = 300   # 5 min antes de scale-in
    scale_out_cooldown = 60    # 1 min antes de scale-out
  }
}
```

### Target Tracking Scaling - Memory

```hcl
# Policy: Memory Utilization
resource "aws_appautoscaling_policy" "orders_api_memory" {
  name               = "orders-api-memory-scaling"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.orders_api.resource_id
  scalable_dimension = aws_appautoscaling_target.orders_api.scalable_dimension
  service_namespace  = aws_appautoscaling_target.orders_api.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageMemoryUtilization"
    }

    target_value       = 80.0  # Mantener Memory ~80%
    scale_in_cooldown  = 300
    scale_out_cooldown = 60
  }
}
```

### Target Tracking Scaling - ALB Requests

```hcl
# Policy: Requests per target
resource "aws_appautoscaling_policy" "orders_api_requests" {
  name               = "orders-api-requests-scaling"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.orders_api.resource_id
  scalable_dimension = aws_appautoscaling_target.orders_api.scalable_dimension
  service_namespace  = aws_appautoscaling_target.orders_api.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ALBRequestCountPerTarget"
      resource_label         = "${aws_lb.main.arn_suffix}/${aws_lb_target_group.orders_api.arn_suffix}"
    }

    target_value       = 1000.0  # 1000 requests/target
    scale_in_cooldown  = 300
    scale_out_cooldown = 60
  }
}
```

### Step Scaling - Respuesta Rápida

```hcl
# CloudWatch Alarm - High CPU
resource "aws_cloudwatch_metric_alarm" "orders_api_cpu_high" {
  alarm_name          = "orders-api-cpu-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "CPUUtilization"
  namespace           = "AWS/ECS"
  period              = 60
  statistic           = "Average"
  threshold           = 80
  alarm_description   = "CPU above 80% for 2 minutes"

  dimensions = {
    ServiceName = aws_ecs_service.orders_api.name
    ClusterName = aws_ecs_cluster.main.name
  }

  alarm_actions = [aws_appautoscaling_policy.orders_api_scale_out.arn]
}

# CloudWatch Alarm - Low CPU
resource "aws_cloudwatch_metric_alarm" "orders_api_cpu_low" {
  alarm_name          = "orders-api-cpu-low"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = 5  # Más conservador para scale-in
  metric_name         = "CPUUtilization"
  namespace           = "AWS/ECS"
  period              = 60
  statistic           = "Average"
  threshold           = 30
  alarm_description   = "CPU below 30% for 5 minutes"

  dimensions = {
    ServiceName = aws_ecs_service.orders_api.name
    ClusterName = aws_ecs_cluster.main.name
  }

  alarm_actions = [aws_appautoscaling_policy.orders_api_scale_in.arn]
}

# Step Scaling Policy - Scale Out
resource "aws_appautoscaling_policy" "orders_api_scale_out" {
  name               = "orders-api-scale-out"
  policy_type        = "StepScaling"
  resource_id        = aws_appautoscaling_target.orders_api.resource_id
  scalable_dimension = aws_appautoscaling_target.orders_api.scalable_dimension
  service_namespace  = aws_appautoscaling_target.orders_api.service_namespace

  step_scaling_policy_configuration {
    adjustment_type         = "PercentChangeInCapacity"
    cooldown               = 60
    metric_aggregation_type = "Average"

    # ✅ Respuesta graduada según severidad
    step_adjustment {
      metric_interval_lower_bound = 0
      metric_interval_upper_bound = 10
      scaling_adjustment          = 10  # +10% si CPU 80-90%
    }

    step_adjustment {
      metric_interval_lower_bound = 10
      scaling_adjustment          = 30  # +30% si CPU > 90%
    }
  }
}

# Step Scaling Policy - Scale In
resource "aws_appautoscaling_policy" "orders_api_scale_in" {
  name               = "orders-api-scale-in"
  policy_type        = "StepScaling"
  resource_id        = aws_appautoscaling_target.orders_api.resource_id
  scalable_dimension = aws_appautoscaling_target.orders_api.scalable_dimension
  service_namespace  = aws_appautoscaling_target.orders_api.service_namespace

  step_scaling_policy_configuration {
    adjustment_type         = "ChangeInCapacity"
    cooldown               = 300  # Más conservador
    metric_aggregation_type = "Average"

    step_adjustment {
      metric_interval_upper_bound = 0
      scaling_adjustment          = -1  # Remover 1 instancia a la vez
    }
  }
}
```

### Scheduled Scaling

```hcl
# Scale up antes de horario pico (9 AM)
resource "aws_appautoscaling_scheduled_action" "orders_api_morning_scale_up" {
  name               = "orders-api-morning-scale-up"
  service_namespace  = aws_appautoscaling_target.orders_api.service_namespace
  resource_id        = aws_appautoscaling_target.orders_api.resource_id
  scalable_dimension = aws_appautoscaling_target.orders_api.scalable_dimension
  schedule           = "cron(0 8 ? * MON-FRI *)"  # 8 AM Mon-Fri (UTC)

  scalable_target_action {
    min_capacity = 10  # Aumentar mínimo a 10
    max_capacity = 30
  }
}

# Scale down después de horario pico (10 PM)
resource "aws_appautoscaling_scheduled_action" "orders_api_night_scale_down" {
  name               = "orders-api-night-scale-down"
  service_namespace  = aws_appautoscaling_target.orders_api.service_namespace
  resource_id        = aws_appautoscaling_target.orders_api.resource_id
  scalable_dimension = aws_appautoscaling_target.orders_api.scalable_dimension
  schedule           = "cron(0 22 ? * MON-FRI *)"  # 10 PM Mon-Fri (UTC)

  scalable_target_action {
    min_capacity = 3  # Volver a mínimo
    max_capacity = 20
  }
}
```

### Custom Metric Scaling (SQS Queue Depth)

```hcl
# Policy: SQS Queue Depth
resource "aws_appautoscaling_policy" "orders_processor_queue_depth" {
  name               = "orders-processor-queue-depth"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.orders_processor.resource_id
  scalable_dimension = aws_appautoscaling_target.orders_processor.scalable_dimension
  service_namespace  = aws_appautoscaling_target.orders_processor.service_namespace

  target_tracking_scaling_policy_configuration {
    customized_metric_specification {
      metric_name = "ApproximateNumberOfMessagesVisible"
      namespace   = "AWS/SQS"
      statistic   = "Average"
      unit        = "Count"

      dimensions {
        name  = "QueueName"
        value = "tlm-orders-processing"
      }
    }

    # ✅ Escalar para mantener ~100 mensajes por worker
    target_value       = 100.0
    scale_in_cooldown  = 300
    scale_out_cooldown = 60
  }
}
```

### Graceful Shutdown

```csharp
// Program.cs
var app = builder.Build();

// ✅ Configurar graceful shutdown
var lifetime = app.Services.GetRequiredService<IHostApplicationLifetime>();

lifetime.ApplicationStopping.Register(() =>
{
    // ✅ Detener health checks inmediatamente
    // ALB dejará de enviar nuevos requests
    app.Logger.LogInformation("Graceful shutdown initiated");
});

// ✅ Delay para drenar connections existentes
var shutdownDelay = builder.Configuration.GetValue<int>("Shutdown:DelaySeconds", 30);
lifetime.ApplicationStopping.Register(async () =>
{
    app.Logger.LogInformation("Waiting {Seconds}s for connections to drain", shutdownDelay);
    await Task.Delay(TimeSpan.FromSeconds(shutdownDelay));
});

app.Run();
```

### Métricas de Auto-Scaling

```yaml
# Grafana Dashboard con métricas de scaling

# ✅ Desired vs Running Tasks
aws_ecs_service_desired_count{service_name="orders-api"}
aws_ecs_service_running_count{service_name="orders-api"}

# ✅ CPU/Memory Utilization
aws_ecs_service_cpu_utilization{service_name="orders-api"}
aws_ecs_service_memory_utilization{service_name="orders-api"}

# ✅ Requests per target
aws_alb_request_count_per_target{target_group="orders-api"}

# ✅ Scaling activities
aws_autoscaling_activities{resource="service/orders-api"}
```

---

## Requisitos Técnicos

### MUST (Obligatorio)

- **MUST** configurar auto-scaling para todos los servicios en producción
- **MUST** establecer min_capacity ≥ 2 para high availability
- **MUST** configurar scale_out_cooldown ≤ 60s
- **MUST** configurar scale_in_cooldown ≥ 300s (más conservador)
- **MUST** usar Target Tracking Scaling como default
- **MUST** implementar graceful shutdown con connection draining
- **MUST** monitorear scaling activities y alarmas

### SHOULD (Fuertemente recomendado)

- **SHOULD** usar múltiples métricas (CPU + Memory + Requests)
- **SHOULD** configurar deployment circuit breaker
- **SHOULD** establecer target_value entre 60-80% para recursos
- **SHOULD** usar Scheduled Scaling para patrones predecibles
- **SHOULD** configurar alarmas cuando se alcanza max_capacity
- **SHOULD** dimensionar task resources apropiadamente
- **SHOULD** mantener 20-30% de overhead capacity

### MAY (Opcional)

- **MAY** usar Step Scaling para respuesta más agresiva
- **MAY** escalar basado en custom metrics (queue depth, biz metrics)
- **MAY** implementar predictive scaling (ML-based)
- **MAY** usar diferentes políticas por horario
- **MAY** ajustar cooldowns por tipo de carga

### MUST NOT (Prohibido)

- **MUST NOT** configurar min_capacity = 1 en producción
- **MUST NOT** usar scale_in_cooldown < 120s
- **MUST NOT** escalar sin monitoreo de métricas clave
- **MUST NOT** ignorar alarmas de max_capacity alcanzado
- **MUST NOT** asumir que auto-scaling resuelve problemas de performance
- **MUST NOT** configurar target_value > 90% (muy agresivo)

---

## Referencias

- [Lineamiento: Escalabilidad y Rendimiento](../../lineamientos/arquitectura/05-escalabilidad-y-rendimiento.md)
- Estándares relacionados:
  - [Diseño Stateless](../../estandares/arquitectura/stateless-design.md)
  - [Load Balancing](load-balancing.md)
- ADRs:
  - [ADR-007: AWS ECS Fargate](../../../decisiones-de-arquitectura/adr-007-aws-ecs-fargate-contenedores.md)
- Especificaciones:
  - [AWS ECS Service Auto Scaling](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/service-auto-scaling.html)
  - [Target Tracking Scaling Policies](https://docs.aws.amazon.com/autoscaling/application/userguide/application-auto-scaling-target-tracking.html)
