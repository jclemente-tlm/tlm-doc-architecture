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

## 4.3 Multi-tenancy

| Aspecto               | Implementación             | Tecnología                  |
|-----------------------|---------------------------|-----------------------------|
| `Tenant resolution`   | `JWT claims`              | `Keycloak realms`           |
| `Configuración`       | Por tenant                | Dinámico vía `SSM`/env      |
| `Rate limiting`       | Por tenant/usuario        | `Redis buckets`             |
| `Enrutamiento`        | Basado en tenant          | `YARP rules`                |

### Cabeceras de Seguridad

```http
Strict-Transport-Security: max-age=31536000; includeSubDomains
X-Frame-Options: DENY
X-Content-Type-Options: nosniff
X-XSS-Protection: 1; mode=block
Content-Security-Policy: default-src 'self'
```

## 4.4 Estrategia de despliegue y orquestación

- Despliegue en `AWS ECS Fargate` usando `Terraform` como IaC.
- Balanceo de carga y alta disponibilidad mediante `Application Load Balancer` multi-AZ.
- Autoescalado por métricas de `CloudWatch` y `Prometheus`.
- Blue-green deployment y rollback automático vía ECS y ALB.
- Observabilidad y monitoreo centralizados con `Grafana`, `Prometheus`, `Loki` y `Jaeger`.

## 4.5 Estrategia de rendimiento

| Técnica                    | Propósito                | Implementación                  |
|----------------------------|--------------------------|---------------------------------|
| `Pooling de Conexiones`    | Reducir latencia         | Pooling de clientes HTTP        |
| `Compresión de Respuesta`  | Reducir ancho de banda   | Gzip/Brotli                     |
| `HTTP/2`                   | Multiplexación           | Soporte nativo en `.NET`        |
| `Caching`                  | Reducir carga            | Headers de caché, Redis         |
| `Balanceo de Carga`        | Distribuir carga         | ALB + YARP                      |

| Métrica                    | Objetivo                 | Medición                        |
|----------------------------|--------------------------|---------------------------------|
| `Sobrecarga de Latencia`   | `< 10ms p95`             | Monitoreo APM                   |
| `Rendimiento`              | `10K req/s`              | Pruebas de carga                |
| `Uso de Memoria`           | `< 2GB` por instancia    | Métricas de contenedor          |
| `Uso de CPU`               | `< 70%` promedio         | Métricas `CloudWatch`           |
| `Tasa de Error`            | `< 0.1%`                 | Seguimiento de errores          |

## 4.6 Estrategia de configuración dinámica

- Configuración centralizada vía `AWS Systems Manager` (SSM) y `Secrets Manager`.
- Variables de entorno para overrides por ambiente y tenant.
- Recarga en caliente cada 30 segundos, validación de esquema y rollback automático si falla health check.
- Jerarquía: `Env Vars > SSM > Archivos locales > Defaults`.

## 4.7 Estrategia de testing

| Nivel         | Tipo                  | Cobertura   | Herramientas                  |
|--------------|-----------------------|-------------|-------------------------------|
| `Unitario`   | Componentes           | 80%+        | `xUnit`, `Moq`                |
| `Integración`| API                   | 70%+        | `TestServer`, `WebAppFactory` |
| `Contrato`   | API contract          | 100%        | `Pact`, validación OpenAPI    |
| `Carga`      | Performance           | Escenarios clave | `NBomber`, `Artillery`   |
| `Seguridad`  | OWASP Top 10          | Completo    | `OWASP ZAP`, `SonarQube`      |

- Testing automatizado en CI/CD (`GitHub Actions`).
- Paridad de ambientes y testing multi-tenant.
- Integración con `Keycloak` para pruebas de autenticación multi-realm.
- Validación de observabilidad: métricas, logs y trazas generadas y exportadas correctamente a `Prometheus`, `Loki` y `Jaeger`.

---

> Esta estrategia de solución está alineada con los modelos Arc42 y Structurizr DSL, asegurando portabilidad, observabilidad, seguridad y rendimiento en el despliegue y operación del API Gateway corporativo.
