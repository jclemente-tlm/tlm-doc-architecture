---
sidebar_position: 10
title: Requisitos de Calidad
description: Atributos y escenarios de calidad del API Gateway Kong OSS.
---

# 10. Requisitos de Calidad

## Rendimiento

| Métrica                    | Objetivo       | Crítico       | Medición                                       |
| -------------------------- | -------------- | ------------- | ---------------------------------------------- |
| Latencia overhead (Kong)   | `< 10ms p95`   | `< 20ms`      | Plugin `prometheus` → Mimir, dashboard Grafana |
| Latencia extremo-a-extremo | `< 100ms p95`  | `< 200ms`     | Trazas en Tempo                                |
| Throughput                 | `> 10,000 RPS` | `> 5,000 RPS` | Load testing (k6)                              |
| Latencia rate limit check  | `< 2ms`        | `< 5ms`       | Redis ElastiCache                              |

## Disponibilidad

| Componente                     | SLA    | Downtime máx./mes | RTO                            |
| ------------------------------ | ------ | ----------------- | ------------------------------ |
| Kong Proxy (2+ instancias ECS) | 99.9%  | 43.2 min          | < 30 seg (ECS health check)    |
| PostgreSQL RDS (Multi-AZ)      | 99.95% | 21.6 min          | < 60 seg (failover automático) |
| Redis ElastiCache              | 99.9%  | 43.2 min          | Fallback a rate limiting local |

## Seguridad

| Aspecto              | Requisito                                              | Implementación                 |
| -------------------- | ------------------------------------------------------ | ------------------------------ |
| Autenticación        | JWT obligatorio en todas las rutas (excepto `/health`) | Plugin `jwt`                   |
| TLS                  | Terminación en ALB con TLS 1.3 mínimo                  | AWS ACM                        |
| Rate limiting        | Por consumer y por IP                                  | Plugin `rate-limiting` + Redis |
| Headers de seguridad | HSTS, X-Frame-Options, X-Content-Type-Options          | Plugin `response-transformer`  |
| Admin API            | Accesible solo desde VPC (sin exposición pública)      | Security Group                 |

## Escalabilidad

| Aspecto             | Objetivo                                         | Estrategia               |
| ------------------- | ------------------------------------------------ | ------------------------ |
| Escalado horizontal | Auto-scaling ECS basado en CPU/RPS               | ECS Service Auto Scaling |
| Balanceo de carga   | Round-robin con health checks                    | ALB + Kong Upstreams     |
| Configuración       | Sincronización automática via deck en despliegue | deck sync en pipeline    |
| Multi-región        | Replicable por región con mismo kong.yml         | Terraform + deck         |

## Escenarios de Calidad

| ID   | Estímulo                              | Respuesta Esperada                                                          |
| ---- | ------------------------------------- | --------------------------------------------------------------------------- |
| Q-01 | 10,000 RPS sostenidos                 | Latencia p95 < 10ms en Kong, sin degradación                                |
| Q-02 | JWT expirado                          | Kong rechaza con 401; backend no recibe request                             |
| Q-03 | Backend caído (3 fallos consecutivos) | Kong excluye el target; tráfico se redirige a instancias sanas              |
| Q-04 | Rate limit superado                   | Kong responde 429 con headers `RateLimit-*`; backend no recibe request      |
| Q-05 | Despliegue de nueva configuración     | `deck sync` aplica cambios sin downtime (rolling update ECS)                |
| Q-06 | Rotación de claves JWKS en Keycloak   | Kong recarga JWKS al expirar TTL de cache; sin impacto en requests en vuelo |
