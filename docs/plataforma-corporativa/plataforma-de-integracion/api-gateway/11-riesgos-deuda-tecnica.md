---
sidebar_position: 11
title: Riesgos y Deuda Técnica
description: Riesgos técnicos y operacionales del API Gateway Kong OSS.
---

# 11. Riesgos y Deuda Técnica

## Riesgos Técnicos

| ID    | Riesgo                                                 | Probabilidad | Impacto | Severidad  | Mitigación                                                                              |
| ----- | ------------------------------------------------------ | ------------ | ------- | ---------- | --------------------------------------------------------------------------------------- |
| RT-01 | Rotación de claves RSA en Keycloak sin actualizar Kong | Media        | Alto    | ⚠️ Alto    | Proceso documentado; actualizar `_consumers.yaml` + `make sync` inmediatamente al rotar |
| RT-02 | Rate limiting inconsistente con múltiples instancias   | Alta         | Medio   | 🟡 Medio   | Implementar Redis (DT-06); actualmente una instancia Kong mitiga el impacto             |
| RT-03 | Fallo en PostgreSQL RDS                                | Baja         | Crítico | 🔴 Crítico | RDS Multi-AZ con failover automático; Kong continúa sirviendo tráfico en cache local    |
| RT-04 | API key de TalentHub en texto plano en YAML            | Media        | Alto    | ⚠️ Alto    | Migrar a AWS Secrets Manager (DT-01); hasta entonces, acceso al repo restringido        |
| RT-05 | Configuración divergente entre entornos                | Media        | Medio   | 🟡 Medio   | `make sync-{env}` como único flujo; revisión en PR antes de aplicar                     |

## Riesgos Operacionales

| ID    | Riesgo                                               | Probabilidad | Impacto | Severidad | Mitigación                                                                                        |
| ----- | ---------------------------------------------------- | ------------ | ------- | --------- | ------------------------------------------------------------------------------------------------- |
| RO-01 | Configuración incorrecta en YAML de Kong             | Media        | Alto    | ⚠️ Alto   | `deck validate` antes del merge; rollback via Git revert + `make sync`                            |
| RO-02 | Curva de aprendizaje de decK y estructura de configs | Media        | Medio   | 🟡 Medio  | Documentación interna (esta sección + STRUCTURE.md); template `_new-service.yaml` como referencia |
| RO-03 | Actualización de Kong con breaking changes           | Media        | Alto    | ⚠️ Alto   | Probar en local/nonprod antes de producción; seguir changelog oficial                             |
| RO-04 | Docker volumes sin permisos correctos (uid 1000)     | Alta         | Medio   | 🟡 Medio  | Documentado en README; `sudo chown -R 1000:1000 /opt/kong` al provisionar el host                 |
| RO-05 | Konga MySQL sin backup automático                    | Media        | Bajo    | 🟢 Bajo   | Konga es solo UI; la fuente de verdad es el YAML en Git; se puede recrear desde `make sync`       |

## Deuda Técnica

| ID    | Deuda                                                              | Prioridad | Acción                                                                                        |
| ----- | ------------------------------------------------------------------ | --------- | --------------------------------------------------------------------------------------------- |
| DT-01 | API key de TalentHub ATS en texto plano en `gestal.yaml`           | Alta      | Migrar a AWS Secrets Manager + referencia en `request-transformer` via variable de entorno    |
| DT-02 | Tenants `tlm-ec` y `tlm-co` no tienen consumer en Kong             | Media     | Agregar consumers cuando se habiliten operaciones en Ecuador/Colombia                         |
| DT-03 | Alertas de Grafana para métricas Kong no configuradas              | Media     | Crear alertas sobre `kong_latency_bucket` p95 y `kong_http_requests_total` 5xx en Mimir       |
| DT-04 | Test de carga automatizado (k6) no integrado en pipeline           | Baja      | Integrar k6 como smoke test de rendimiento en cada despliegue a nonprod                       |
| DT-05 | `sisbon-dev` y `sisbon-qa` apuntan al mismo NLB backend            | Media     | Separar backends DEV y QA cuando se aprovisionen NLBs independientes                          |
| DT-06 | Redis (ElastiCache) para rate limiting distribuido no implementado | Alta      | Aprovisionar Redis Cluster y cambiar `policy: local` → `policy: redis` en todos los servicios |
| DT-07 | `kong-deck-bootstrap` usa imagen `kong/deck:latest`                | Baja      | Fijar a versión específica (ej. `kong/deck:1.40`) para builds reproducibles                   |

## Plan de Contingencia

| Escenario                         | Respuesta                                                                    |
| --------------------------------- | ---------------------------------------------------------------------------- |
| Configuración incorrecta aplicada | `git revert` + `make sync-{env}` (decK reconcilia al estado anterior)        |
| Kong no responde                  | Verificar logs con `docker logs kong`; revisar conectividad a PostgreSQL     |
| deck sync falla                   | `deck validate config/kong/{env}/` para identificar el archivo con error     |
| Clave RSA inválida (401 masivo)   | Obtener clave nueva de Keycloak → actualizar `_consumers.yaml` → `make sync` |
| Konga inaccesible                 | La operación de Kong no se ve afectada; usar `make sync-{env}` directamente  |
