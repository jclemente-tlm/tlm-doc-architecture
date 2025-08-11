# 4. Estrategia De Solución

## 4.1 Decisiones Clave

| Decisión         | Alternativa Elegida         | Justificación                |
|------------------|----------------------------|------------------------------|
| Proxy            | [YARP](https://microsoft.github.io/reverse-proxy/) | Alto rendimiento, soporte Microsoft |
| Autenticación    | JWT + OAuth2 con `Keycloak` | Estándar de la industria     |
| Rate Limiting    | `Redis`                    | Escalabilidad, multi-tenant  |
| Resiliencia      | `Polly`                    | Patrones probados            |
| Observabilidad   | `Grafana`, `Prometheus`, `Loki`, `Jaeger` | Stack estándar, trazabilidad y monitoreo |
| Despliegue       | AWS ECS Fargate + `Terraform` | Portabilidad, IaC, automatización |

## 4.2 Patrones Aplicados

| Patrón                | Propósito                  | Implementación              |
|-----------------------|----------------------------|-----------------------------|
| API Gateway           | Punto de entrada único     | `YARP`                      |
| Circuit Breaker       | Tolerancia a fallos        | `Polly`                     |
| Rate Limiting         | Protección de recursos     | `Redis`                     |
| Load Balancing        | Distribución de carga      | ALB + `YARP`                |
| Observabilidad        | Monitoreo y trazabilidad   | `Prometheus`, `Loki`, `Jaeger`, `Grafana` |

Las decisiones y patrones seleccionados priorizan seguridad, escalabilidad, resiliencia y observabilidad, alineados a los objetivos de negocio y técnicos. Se evita complejidad innecesaria, empleando tecnologías estándar y ampliamente soportadas.
