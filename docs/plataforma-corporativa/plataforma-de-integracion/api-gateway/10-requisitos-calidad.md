---
sidebar_position: 10
title: Requisitos de Calidad
description: Atributos y escenarios de calidad del API Gateway Kong OSS.
---

# 10. Requisitos de Calidad

## Rendimiento

| Métrica                  | Objetivo       | Crítico       | Medición                                       |
| ------------------------ | -------------- | ------------- | ---------------------------------------------- |
| Latencia overhead (Kong) | `< 10ms p95`   | `< 20ms`      | Plugin `prometheus` → Mimir, dashboard Grafana |
| Throughput               | `> 10,000 RPS` | `> 5,000 RPS` | Load testing (k6)                              |
| Rate limit check (local) | `< 1ms`        | `< 5ms`       | Contador in-memory (policy: local)             |

## Disponibilidad

| Componente                | SLA         | Downtime máx./mes | Estrategia                                      |
| ------------------------- | ----------- | ----------------- | ----------------------------------------------- |
| Kong Proxy                | 99.9%       | 43.2 min          | Múltiples instancias detrás de ALB              |
| PostgreSQL RDS (Multi-AZ) | 99.95%      | 21.6 min          | Failover automático RDS Multi-AZ                |
| Konga (Admin UI)          | Best effort | —                 | No es crítico; solo para gestión administrativa |

## Seguridad

| Aspecto              | Requisito                                                    | Implementación                                |
| -------------------- | ------------------------------------------------------------ | --------------------------------------------- |
| Autenticación        | JWT RS256 obligatorio en todas las rutas de negocio          | Plugin `jwt` con clave pública embebida       |
| TLS                  | Terminación en ALB con TLS 1.3 mínimo                        | AWS ACM                                       |
| Autorización gateway | ACL por sistema de negocio                                   | Plugin `acl` con grupos por sistema           |
| Rate limiting        | Por consumer (tenant)                                        | Plugin `rate-limiting` (policy: local)        |
| Tamaño de payload    | Máximo 1 MB por request                                      | Plugin `request-size-limiting`                |
| Admin API            | Accesible solo internamente (sin exposición pública directa) | Configuración de red / VPC                    |
| Secretos             | No en repositorio; vía variables de entorno                  | `.env` (gitignored) / AWS Secrets Manager     |
| API keys externas    | No en texto plano en YAML de Kong                            | Pendiente migración a Secrets Manager (DT-01) |

## Escalabilidad

| Aspecto       | Objetivo                               | Estrategia                          |
| ------------- | -------------------------------------- | ----------------------------------- |
| Nuevo sistema | Onboarding en `< 30 minutos`           | Copiar template + `make sync-{env}` |
| Nuevo tenant  | Crear tenant (realm) + consumer + sync | Proceso documentado en DEC-02       |
| Configuración | Sin downtime en cambios (`deck sync`)  | decK aplica cambios incrementales   |

## Escenarios de Calidad

| ID   | Estímulo                               | Respuesta Esperada                                                                    |
| ---- | -------------------------------------- | ------------------------------------------------------------------------------------- |
| Q-01 | JWT expirado en request                | Kong rechaza con 401; backend no recibe el request                                    |
| Q-02 | Consumer sin grupo ACL para el sistema | Kong rechaza con 403; backend no recibe el request                                    |
| Q-03 | Payload > 1 MB                         | Kong rechaza con 413; backend no recibe el request                                    |
| Q-04 | Rate limit superado por consumer       | Kong responde 429 con headers `RateLimit-*`; backend no recibe el request             |
| Q-05 | Despliegue de nueva configuración      | `make sync-{env}` aplica cambios sin downtime (incrementos declarativos vía decK)     |
| Q-06 | Rotación de claves RSA en Keycloak     | Tokens nuevos son inválidos hasta actualizar `_consumers.yaml` y ejecutar `sync`      |
| Q-07 | Nuevo sistema de negocio a integrar    | Copiar template, configurar service/route/plugins, `make sync-local → nonprod → prod` |
