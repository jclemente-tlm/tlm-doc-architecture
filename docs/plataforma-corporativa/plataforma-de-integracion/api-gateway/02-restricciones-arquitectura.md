# 2. Restricciones De La Arquitectura

## 2.1 Restricciones Técnicas Y De Plataforma

| Categoría         | Restricción                | Justificación              |
|-------------------|---------------------------|----------------------------|
| Runtime           | `.NET 8`                  | Estándar corporativo       |
| Proxy             | [YARP](https://microsoft.github.io/reverse-proxy/) | Alto rendimiento y soporte Microsoft |
| Base de datos     | `PostgreSQL`              | Robustez y escalabilidad   |
| Cache             | [Redis](https://redis.io/) | Rendimiento y baja latencia|
| Autenticación     | OAuth2/OIDC con `Keycloak` | Estándar de la industria   |
| Contenedores      | AWS ECS Fargate           | Serverless, portabilidad   |
| Orquestación      | `ECS`                     | Integración AWS nativa     |
| Secrets           | AWS Secrets Manager       | Seguridad y cumplimiento   |
| Observabilidad    | Grafana, Prometheus, Loki, Jaeger | Stack estándar, trazabilidad y monitoreo |

## 2.2 Restricciones De Rendimiento Y Operación

| Métrica           | Objetivo                  | Razón                      |
|-------------------|--------------------------|----------------------------|
| Latencia          | `< 100ms P95`            | Experiencia usuario        |
| Throughput        | `> 5,000 RPS`            | Carga esperada             |
| Disponibilidad    | `≥ 99.9%`                | SLA empresarial            |

- Multi-tenancy obligatorio por país y tenant (realm).
- Rate limiting por tenant usando `Redis` en modo cluster.
- Despliegue de contenedores en `ECS Fargate` con Application Load Balancer multi-AZ.
- Configuración y secretos gestionados externamente (AWS Secrets Manager).
- Observabilidad centralizada (Grafana, Prometheus, Loki, Jaeger).
- Seguridad: arquitectura zero trust, RBAC por tenant, auditoría completa de requests.

## 2.3 Restricciones De Seguridad Y Cumplimiento

| Control                  | Requisito/Implementación                  |
|--------------------------|-------------------------------------------|
| Validación de tokens     | Firma JWT, clave pública (`Keycloak`)     |
| Limitación de velocidad  | `Redis`, protección DDoS, ventanas deslizantes |
| Lista de IPs permitidas  | Restricción por tenant                    |
| Audit Logging            | Logging estructurado, retención en Loki   |
| Cifrado en tránsito      | TLS 1.3, terminación en ALB               |
| Aislamiento de red       | VPC, Security Groups, AWS WAF, Shield     |

## 2.4 Restricciones De Despliegue Y CI/CD

- Imágenes base distroless y escaneo de vulnerabilidades obligatorio.
- Límites de recursos definidos en ECS Task Definition (CPU, memoria).
- Health checks HTTP expuestos y monitoreados por ALB y Prometheus.
- Blue-green deployment obligatorio usando ECS y ALB.
- Pipeline CI/CD con GitHub Actions, pruebas automáticas, escaneo de seguridad (Checkov, Trivy) y despliegue automatizado en AWS ECS (Terraform).

## 2.5 Restricciones De Monitoreo Y Observabilidad

| Componente     | Herramienta                  | Propósito                  |
|----------------|-----------------------------|----------------------------|
| Métricas       | Prometheus, CloudWatch       | Dashboards, alertas        |
| Logging        | Loki, CloudWatch Logs        | Centralización, auditoría  |
| Tracing        | Jaeger, OpenTelemetry        | Trazabilidad de requests   |
| Visualización  | Grafana                      | Dashboards y alertas       |

## 2.6 Limitaciones Conocidas

- Actualizaciones de configuración: máximo cada 30 segundos (polling).
- Rate limiting: consistencia eventual en cluster `Redis`.
- Costo de infraestructura: optimización continua requerida.
- Ventana de migración: máximo 4 horas de downtime.

## 2.7 Decisiones Arquitectónicas Derivadas

| Restricción                | Decisión de Diseño                  | Trade-off                        | Mitigación                       |
|----------------------------|-------------------------------------|----------------------------------|----------------------------------|
| Soporte multi-tenant       | Middleware consciente de tenant     | Sobrecarga de requests           | Resolución eficiente de tenant   |
| Alta disponibilidad        | Diseño sin estado, multi-AZ         | Complejidad de sesiones          | Almacenamiento externo           |
| Seguridad                  | Validación exhaustiva, zero trust   | Latencia de procesamiento        | Pipelines optimizados            |
| Rendimiento                | Estrategias de caching y pooling    | Consistencia eventual            | Estrategias de invalidación      |

## Referencias

- [YARP](https://microsoft.github.io/reverse-proxy/)
- [AWS ECS](https://docs.aws.amazon.com/ecs/)
- [AWS Application Load Balancer](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/)
- [AWS CloudWatch](https://docs.aws.amazon.com/cloudwatch/)
- [Prometheus](https://prometheus.io/)
- [Grafana](https://grafana.com/)
- [Loki](https://grafana.com/oss/loki/)
- [Jaeger](https://www.jaegertracing.io/)
- [OAuth 2.0 (RFC 6749)](https://tools.ietf.org/html/rfc6749)
- [OpenID Connect Core](https://openid.net/specs/openid-connect-core-1_0.html)
- [JWT (RFC 7519)](https://tools.ietf.org/html/rfc7519)
- [OWASP API Security](https://owasp.org/www-project-api-security/)
- [GDPR Regulation](https://gdpr-info.eu/)
- [PCI DSS Standards](https://www.pcisecuritystandards.org/)
- [arc42: Architectural Constraints](https://docs.arc42.org/section-2/)
- [C4 Model](https://c4model.com/)
