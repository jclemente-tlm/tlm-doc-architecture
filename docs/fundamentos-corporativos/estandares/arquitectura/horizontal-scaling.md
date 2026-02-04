---
id: horizontal-scaling
sidebar_position: 5
title: Escalado Horizontal
description: Estándar para auto-scaling horizontal en AWS ECS Fargate basado en métricas CPU, memoria, requests/s con Application Auto Scaling y target tracking
---

# Estándar Técnico — Escalado Horizontal

---

## 1. Propósito

Permitir crecimiento de capacidad mediante escalado horizontal automático (añadir/quitar replicas) basado en métricas de CPU, memoria, request rate y custom metrics, garantizando alta disponibilidad y optimización de costos.

---

## 2. Alcance

**Aplica a:**

- APIs REST stateless
- Microservicios backend
- Workers de procesamiento
- Consumers de Kafka
- Deployments en AWS ECS Fargate

**No aplica a:**

- Servicios stateful (databases, Redis master)
- Singleton services
- Cron jobs / scheduled tasks
- Services con límite de licencias

---

## 3. Tecnologías Aprobadas

| Componente        | Tecnología               | Versión mínima | Observaciones                    |
| ----------------- | ------------------------ | -------------- | -------------------------------- |
| **AWS ECS**       | Application Auto Scaling | -              | Target tracking                  |
| **Metrics**       | Grafana Mimir            | 2.10+          | Custom metrics via OpenTelemetry |
| **Load Balancer** | AWS ALB                  | -              | Distribución de tráfico          |

> El uso de tecnologías no listadas requiere aprobación de Arquitectura.

---

## 4. Requisitos Obligatorios 🔴

### Configuración de Auto Scaling

- [ ] **Min replicas:** ≥2 para alta disponibilidad
- [ ] **Max replicas:** límite razonable (10-50 según capacidad)
- [ ] **Target CPU:** 70% utilization
- [ ] **Target Memory:** 80% utilization
- [ ] **Scale up cooldown:** 30-60 segundos
- [ ] **Scale down cooldown:** 5-10 minutos (más conservador)

### Métricas para Autoscaling

- [ ] CPU utilization (primaria)
- [ ] Memory utilization (secundaria)
- [ ] Request rate (requests/s)
- [ ] Response time (p95 latency)
- [ ] Custom metrics (queue depth, etc.)

### Diseño Stateless

- [ ] Services completamente stateless
- [ ] No sticky sessions
- [ ] Graceful shutdown implementado
- [ ] Health checks configurados
- [ ] Readiness probes configurados

### Resource Limits

- [ ] CPU requests/limits definidos
- [ ] Memory requests/limits definidos
- [ ] Límites alineados con métricas de autoscaling
- [ ] Resource quotas por namespace

### Load Balancing

- [ ] Load balancer frente a replicas
- [ ] Health checks en load balancer
- [ ] Connection draining habilitado
- [ ] Round-robin o least-connections

---

## 5. Prohibiciones

- ❌ Min replicas = 1 (single point of failure)
- ❌ Max replicas sin límite (riesgo de costos)
- ❌ Autoscaling de services stateful
- ❌ Scale basado solo en schedule (usar metrics)
- ❌ Resource limits no definidos
- ❌ Autoscaling sin graceful shutdown
- ❌ Sticky sessions con autoscaling

---

## 6. Configuración Mínima

### AWS ECS Fargate Auto Scaling

```json
// task-definition.json
{
  "family": "payment-service",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "containerDefinitions": [
    {
      "name": "payment-service",
      "image": "ghcr.io/talma/payment-service:v1.2.0",
      "portMappings": [
        {
          "containerPort": 8080,
          "protocol": "tcp"
        }
      ],
      "healthCheck": {
        "command": [
          "CMD-SHELL",
          "curl -f http://localhost:8080/health || exit 1"
        ],
        "interval": 30,
        "timeout": 5,
        "retries": 3,
        "startPeriod": 60
      },
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/payment-service",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      },
      "stopTimeout": 30
    }
  ]
}
```

```json
// auto-scaling-policy.json
{
  "ServiceName": "payment-service",
  "ScalableDimension": "ecs:service:DesiredCount",
  "PolicyName": "payment-service-target-tracking-cpu",
  "PolicyType": "TargetTrackingScaling",
  "TargetTrackingScalingPolicyConfiguration": {
    "TargetValue": 70.0,
    "PredefinedMetricSpecification": {
      "PredefinedMetricType": "ECSServiceAverageCPUUtilization"
    },
    "ScaleOutCooldown": 60,
    "ScaleInCooldown": 300
  }
}
```

          averageUtilization: 80
    - type: Pods
      pods:
        metric:
          name: http_requests_per_second
        target:
          type: AverageValue
          averageValue: "1000" # 1000 req/s por pod

behavior:
scaleDown:
stabilizationWindowSeconds: 300 # 5 min antes de scale down
policies: - type: Percent
value: 50 # Max 50% de pods removidos
periodSeconds: 60
scaleUp:
stabilizationWindowSeconds: 0
policies: - type: Percent
value: 100 # Doblar pods si es necesario
periodSeconds: 30 - type: Pods
value: 4 # O añadir 4 pods
periodSeconds: 30
selectPolicy: Max # Elegir política más agresiva

````

### AWS ECS Auto Scaling

```json
// ecs-service.json
{
  "serviceName": "payment-service",
  "cluster": "production-cluster",
  "desiredCount": 2,
  "deploymentConfiguration": {
    "minimumHealthyPercent": 100,
    "maximumPercent": 200
  },
  "loadBalancers": [
    {
      "targetGroupArn": "arn:aws:elasticloadbalancing:...",
      "containerName": "payment-service",
      "containerPort": 8080
    }
  ]
}
````

```bash
# AWS CLI - Configurar auto scaling
aws application-autoscaling register-scalable-target \
  --service-namespace ecs \
  --scalable-dimension ecs:service:DesiredCount \
  --resource-id service/production-cluster/payment-service \
  --min-capacity 2 \
  --max-capacity 20

# Target tracking policy - CPU
aws application-autoscaling put-scaling-policy \
  --policy-name payment-cpu-scaling \
  --service-namespace ecs \
  --scalable-dimension ecs:service:DesiredCount \
  --resource-id service/production-cluster/payment-service \
  --policy-type TargetTrackingScaling \
  --target-tracking-scaling-policy-configuration '{
    "TargetValue": 70.0,
    "PredefinedMetricSpecification": {
      "PredefinedMetricType": "ECSServiceAverageCPUUtilization"
    },
    "ScaleInCooldown": 300,
    "ScaleOutCooldown": 60
  }'

# Target tracking policy - Request count
aws application-autoscaling put-scaling-policy \
  --policy-name payment-request-scaling \
  --service-namespace ecs \
  --scalable-dimension ecs:service:DesiredCount \
  --resource-id service/production-cluster/payment-service \
  --policy-type TargetTrackingScaling \
  --target-tracking-scaling-policy-configuration '{
    "TargetValue": 1000.0,
    "PredefinedMetricSpecification": {
      "PredefinedMetricType": "ALBRequestCountPerTarget",
      "ResourceLabel": "app/payment-alb/..."
    },
    "ScaleInCooldown": 300,
    "ScaleOutCooldown": 60
  }'
```

---

## 7. Ejemplos

### HPA con custom metrics (Prometheus)

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: order-service-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: order-service
  minReplicas: 3
  maxReplicas: 50
  metrics:
    # CPU
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
    # Latencia p95 (custom metric)
    - type: Pods
      pods:
        metric:
          name: http_request_duration_p95
        target:
          type: AverageValue
          averageValue: "500m" # 500ms
    # Queue depth (KEDA)
    - type: External
      external:
        metric:
          name: kafka_consumergroup_lag
          selector:
            matchLabels:
              topic: orders
              consumergroup: order-processor
        target:
          type: AverageValue
          averageValue: "100" # 100 msgs lag por pod
```

### Graceful shutdown para autoscaling

```csharp
// Program.cs
var builder = WebApplication.CreateBuilder(args);
var app = builder.Build();

// Registrar handler para SIGTERM (Kubernetes shutdown)
var lifetime = app.Services.GetRequiredService<IHostApplicationLifetime>();

lifetime.ApplicationStopping.Register(() =>
{
    Console.WriteLine("Received SIGTERM. Starting graceful shutdown...");

    // 1. Marcar como no-ready
    HealthCheckService.IsReady = false;

    // 2. Esperar a que load balancer deje de enviar tráfico
    Thread.Sleep(TimeSpan.FromSeconds(15));

    // 3. Completar requests en proceso
    Console.WriteLine("Waiting for in-flight requests to complete...");
});

app.MapHealthChecks("/health/ready", new HealthCheckOptions
{
    Predicate = check => check.Tags.Contains("ready")
});

app.Run();

public static class HealthCheckService
{
    public static bool IsReady { get; set; } = true;
}

public class ReadinessHealthCheck : IHealthCheck
{
    public Task<HealthCheckResult> CheckHealthAsync(
        HealthCheckContext context,
        CancellationToken cancellationToken = default)
    {
        if (HealthCheckService.IsReady)
            return Task.FromResult(HealthCheckResult.Healthy());

        return Task.FromResult(HealthCheckResult.Unhealthy("Shutting down"));
    }
}
```

---

## 8. Validación y Auditoría

```bash
# Kubernetes - Ver estado de HPA
kubectl get hpa -n production
kubectl describe hpa payment-service-hpa -n production

# Ver métricas actuales
kubectl top pods -n production

# AWS ECS - Ver scaling policies
aws application-autoscaling describe-scaling-policies \
  --service-namespace ecs

# Ver scaling activity
aws application-autoscaling describe-scaling-activities \
  --service-namespace ecs \
  --resource-id service/production-cluster/payment-service
```

**Métricas de cumplimiento:**

| Métrica                      | Umbral | Verificación         |
| ---------------------------- | ------ | -------------------- |
| Services con min replicas ≥2 | 100%   | kubectl/AWS review   |
| Services con HPA configurado | 100%   | kubectl get hpa      |
| Resource limits definidos    | 100%   | kubectl describe pod |
| Graceful shutdown            | 100%   | Code review          |

**Checklist de auditoría:**

- [ ] Min replicas ≥ 2
- [ ] Max replicas definido
- [ ] Target CPU 70%
- [ ] Resource requests/limits configurados
- [ ] Health checks y readiness probes
- [ ] Graceful shutdown implementado
- [ ] Load balancer configurado

---

## 9. Referencias

- [Kubernetes HPA Documentation](https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/)
- [AWS ECS Service Auto Scaling](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/service-auto-scaling.html)
- [KEDA Documentation](https://keda.sh/docs/)
- [12-Factor App - Concurrency](https://12factor.net/concurrency)
- [The Art of Scalability](https://theartofscalability.com/)
- [AWS Well-Architected - Performance Efficiency](https://docs.aws.amazon.com/wellarchitected/latest/performance-efficiency-pillar/)
