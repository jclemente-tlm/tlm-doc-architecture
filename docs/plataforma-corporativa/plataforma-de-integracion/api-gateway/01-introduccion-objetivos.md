# 1. Introducción y Objetivos

El API Gateway es el punto de entrada unificado y seguro para los servicios corporativos, implementado con [YARP](https://microsoft.github.io/reverse-proxy/) y desplegado en AWS ECS mediante [Terraform](https://www.terraform.io/). Opera en entornos multi-tenant (realms) y multi-país, garantizando seguridad, resiliencia, observabilidad y cumplimiento de los objetivos de negocio.

## 1.1 Propósito y Funcionalidades

| Funcionalidad    | Descripción                                                                 |
|------------------|-----------------------------------------------------------------------------|
| Enrutamiento     | Proxy reverso inteligente para servicios backend, soporte multi-tenant (realms) y multi-país |
| Autenticación    | Validación de tokens JWT vía [OAuth2/OIDC](https://openid.net/connect/) y control de acceso granular con Keycloak |
| Rate Limiting    | Control de velocidad distribuido por tenant (realm) y cliente usando [Redis](https://redis.io/) |
| Load Balancing   | Distribución de carga entre instancias backend con ALB y YARP               |
| Observabilidad   | Logging estructurado (Serilog/Loki), métricas ([Prometheus](https://prometheus.io/)), tracing ([Jaeger](https://www.jaegertracing.io/)), dashboards ([Grafana](https://grafana.com/)) |
| Resiliencia      | Circuit breakers ([Polly](https://github.com/App-vNext/Polly)), retry policies y health checks multinivel        |

## 1.2 Objetivos de Calidad

| Atributo       | Objetivo                | Métrica                |
|----------------|------------------------|------------------------|
| Disponibilidad | Alta disponibilidad    | ≥ 99.9% uptime         |
| Rendimiento    | Baja latencia          | < 100ms P95            |
| Throughput     | Alto rendimiento       | > 5,000 RPS            |
| Seguridad      | Zero trust, cumplimiento OWASP | Autenticación obligatoria, headers y políticas de seguridad |
| Observabilidad | Trazabilidad y monitoreo en tiempo real | Dashboards, alertas y métricas en Grafana/Prometheus |
