---
sidebar_position: 11
title: Riesgos y Deuda Técnica
description: Riesgos técnicos y operacionales del API Gateway Kong OSS.
---

# 11. Riesgos y Deuda Técnica

## Riesgos Técnicos

| ID    | Riesgo                                      | Probabilidad | Impacto | Severidad  | Mitigación                                                                                       |
| ----- | ------------------------------------------- | ------------ | ------- | ---------- | ------------------------------------------------------------------------------------------------ |
| RT-01 | Punto único de falla en Kong                | Media        | Crítico | 🔴 Crítico | Mínimo 2 instancias ECS en multi-AZ; ALB con health checks                                       |
| RT-02 | Fallo en PostgreSQL RDS                     | Baja         | Crítico | 🔴 Crítico | RDS Multi-AZ con failover automático; Kong continúa sirviendo tráfico (cache en memoria)         |
| RT-03 | Degradación por fallo de Redis              | Media        | Medio   | 🟡 Medio   | Fallback a `policy: local` en rate-limiting; Redis Cluster con réplicas                          |
| RT-04 | Vulnerabilidades en JWT                     | Baja         | Alto    | ⚠️ Alto    | Usar solo algoritmos RS256/ES256; configurar `claims_to_verify: exp, nbf`; auditorías periódicas |
| RT-05 | Desincronización de config entre instancias | Baja         | Alto    | ⚠️ Alto    | `deck sync` como única fuente de cambios; PostgreSQL como estado compartido                      |

## Riesgos Operacionales

| ID    | Riesgo                                                | Probabilidad | Impacto | Severidad  | Mitigación                                                                                                |
| ----- | ----------------------------------------------------- | ------------ | ------- | ---------- | --------------------------------------------------------------------------------------------------------- |
| RO-01 | Configuración incorrecta en `kong.yml`                | Media        | Alto    | ⚠️ Alto    | `deck validate` en CI antes del merge; rollback via Git revert + deck sync                                |
| RO-02 | Curva de aprendizaje de Kong / Lua                    | Alta         | Medio   | 🟡 Medio   | Documentación interna, training del equipo de Plataforma, plugins solo del Hub oficial                    |
| RO-03 | Actualización de versión de Kong con breaking changes | Media        | Alto    | ⚠️ Alto    | Pruebas en ambiente de staging; seguir changelog official; Kong mantiene compatibilidad por versión mayor |
| RO-04 | Exposición accidental del Admin API                   | Baja         | Crítico | 🔴 Crítico | Admin API en `127.0.0.1:8001`; acceso solo desde CI/CD vía VPN/tunnel                                     |

## Deuda Técnica

| ID    | Deuda                                                                | Prioridad | Acción                                                                               |
| ----- | -------------------------------------------------------------------- | --------- | ------------------------------------------------------------------------------------ |
| DT-01 | Plugin `custom-auth` no homologado pendiente de revisión             | Alta      | Reemplazar con plugin `jwt` del Hub oficial                                          |
| DT-02 | Workspaces de multi-tenancy parcialmente configurados (solo PE y EC) | Media     | Completar CO y MX antes de lanzamiento en esos países                                |
| DT-03 | Alertas de Grafana para latencia Kong no definidas                   | Media     | Crear alertas sobre `kong_latency_bucket` p95 > umbral en Mimir                      |
| DT-04 | Test de carga automatizado en pipeline CI/CD                         | Baja      | Integrar k6 para smoke test de regresión de rendimiento en cada despliegue           |
| DT-05 | Log forwarding CloudWatch → Loki no configurado en ECS task          | Media     | Habilitar FireLens (Fluent Bit) en la task definition para reenviar logs a Loki      |
| DT-06 | Redis (ElastiCache) para rate limiting no implementado               | Alta      | Aprovisionar Redis Cluster y configurar `policy: redis` en el plugin `rate-limiting` |

## Plan de Contingencia

| Escenario                   | Respuesta                                                                  |
| --------------------------- | -------------------------------------------------------------------------- |
| Instancia Kong caída        | ALB detecta el fallo y redirige tráfico a instancias sanas automáticamente |
| Todas las instancias fallan | Activar modo mantenimiento (`503` desde ALB) mientras se restaura          |
| Restaurar configuración     | `deck sync --state kong-backup.yml` desde el repositorio de infra          |
