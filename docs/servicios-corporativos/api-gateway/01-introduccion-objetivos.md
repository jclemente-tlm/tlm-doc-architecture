# 1. Introducción y objetivos

El `API Gateway` es el punto de entrada unificado y seguro para todos los servicios corporativos, implementado sobre `YARP` y desplegado en `AWS ECS` usando `Terraform`. Está diseñado para operar en entornos multi-tenant y multi-país, garantizando seguridad, resiliencia, observabilidad y cumplimiento de los objetivos de negocio.

## 1.1 Propósito y funcionalidades

| Funcionalidad      | Descripción                                    |
|--------------------|------------------------------------------------|
| `Enrutamiento`     | Proxy reverso inteligente para servicios downstream, con soporte multi-tenant y multi-país |
| `Autenticación`    | Validación de tokens `JWT` vía `OAuth2/OIDC` y control de acceso granular |
| `Rate Limiting`    | Control de velocidad distribuido por `tenant` y cliente usando `Redis` |
| `Load Balancing`   | Distribución de carga entre instancias backend con `ALB` y `YARP` |
| `Observabilidad`   | `Logging` estructurado (`Serilog`/`Loki`), métricas (`Prometheus`), tracing (`Jaeger`) y dashboards (`Grafana`) |
| `Resiliencia`      | `Circuit breakers` (`Polly`), `retry policies` y health checks multinivel |

## 1.2 Objetivos de calidad

| Atributo           | Objetivo                | Métrica            |
|--------------------|------------------------|--------------------|
| `Disponibilidad`   | Alta disponibilidad    | `99.9% uptime`     |
| `Rendimiento`      | Baja latencia          | `< 100ms P95`      |
| `Throughput`       | Alto rendimiento       | `> 5,000 RPS`      |
| `Seguridad`        | Zero trust, cumplimiento OWASP | Autenticación obligatoria, headers de seguridad |
| `Observabilidad`   | Trazabilidad y monitoreo en tiempo real | Dashboards y alertas en `Grafana` |

> El `API Gateway` centraliza la gestión de autenticación, autorización, control de tráfico, resiliencia y observabilidad, facilitando la integración, operación segura y monitoreo avanzado de los microservicios corporativos. Todo el diseño está alineado a los modelos C4/Structurizr DSL y la documentación Arc42.
