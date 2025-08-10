# 4. Estrategia de solución

## 4.1 Decisiones clave

| Decisión         | Alternativa elegida         | Justificación                |
|------------------|----------------------------|------------------------------|
| `Proxy`          | `YARP`                     | Microsoft, alto rendimiento  |
| `Autenticación`  | `JWT` + `OAuth2`           | Estándar industria           |
| `Rate Limiting`  | `Redis`                    | Escalabilidad, multi-tenant  |
| `Resiliencia`    | `Polly`                    | Patrones probados            |
| `Observabilidad` | `Grafana`, `Prometheus`, `Loki`, `Jaeger` | Stack estándar, trazabilidad y monitoreo |
| `Despliegue`     | `AWS ECS Fargate` + `Terraform` | Portabilidad, IaC, automatización |

## 4.2 Patrones aplicados

| Patrón                | Propósito                  | Implementación              |
|-----------------------|----------------------------|-----------------------------|
| `API Gateway`         | Punto de entrada único     | `YARP`                      |
| `Circuit Breaker`     | Tolerancia a fallos        | `Polly`                     |
| `Rate Limiting`       | Protección recursos        | `Redis`                     |
| `Load Balancing`      | Distribución carga         | `ALB` + `YARP`              |
| `Observabilidad`      | Monitoreo y trazabilidad   | `Prometheus`, `Loki`, `Jaeger`, `Grafana` |
