---
sidebar_position: 11
title: Riesgos y Deuda Técnica
description: Mapa de riesgos y deuda técnica del stack de observabilidad corporativo.
---

# 11. Riesgos y Deuda Técnica

## Riesgos Técnicos

| ID    | Riesgo                                                                          | Severidad | Probabilidad | Mitigación                                                                               |
| ----- | ------------------------------------------------------------------------------- | --------- | ------------ | ---------------------------------------------------------------------------------------- |
| RT-01 | Disco del EC2 servidor saturado por crecimiento no planificado de logs/métricas | 🔴 Alta   | Media        | Monitorear `df -h` en el servidor; alertar al 75% de uso; ajustar políticas de retención |
| RT-02 | Corrupción del WAL de Loki/Mimir tras fallo de I/O en reinicio                  | 🔴 Alta   | Baja         | Backup periódico de volúmenes Docker (`loki-data`); snapshot de EBS del EC2 servidor     |
| RT-03 | Versión de Alloy incompatible con sintaxis `.alloy` al hacer upgrade            | ⚠️ Media  | Media        | Probar upgrades en entorno de staging; mantener `.alloy` bajo control de versiones       |
| RT-04 | MinIO en modo standalone: punto único de fallo de almacenamiento                | ⚠️ Media  | Baja         | Evaluar migración a MinIO en modo distribuido o replicar buckets a AWS S3                |

## Riesgos Operacionales

| ID    | Riesgo                                                                        | Severidad | Probabilidad | Mitigación                                                                                        |
| ----- | ----------------------------------------------------------------------------- | --------- | ------------ | ------------------------------------------------------------------------------------------------- |
| RO-01 | Agente Alloy mal configurado (TENANT_ID incorrecto) mezcla datos entre países | 🔴 Alta   | Media        | Validar variables `.env` antes del despliegue; checklist de onboarding de nuevos agentes          |
| RO-02 | Memcached no disponible aumenta latencia de dashboards ejecutivos             | 🟡 Baja   | Media        | Alertar si `memcached_connections_current == 0`; dashboards degradados con mayor latencia (< 2 s) |
| RO-03 | Data source en Grafana sin `X-Scope-OrgID` fijo expone datos cross-tenant     | 🔴 Alta   | Baja         | Revisión de todos los data sources en Grafana; SSO Keycloak con organizaciones por tenant         |
| RO-04 | Envoy Lua filter incorrecto enruta señal al tenant equivocado                 | ⚠️ Media  | Baja         | Tests de integración del routing en staging; revisión del filtro al cambiar el naming de tenants  |

## Deuda Técnica

| ID    | Descripción                                                                      | Área           | Esfuerzo | Impacto si no se resuelve                                                                               |
| ----- | -------------------------------------------------------------------------------- | -------------- | -------- | ------------------------------------------------------------------------------------------------------- |
| DT-01 | Grafana SSO con Keycloak no está implementado aún; usar usuario/contraseña local | Seguridad      | Medio    | Cuentas sin expiración ni rotación automática; acceso no auditado con identidad corporativa             |
| DT-02 | Derived fields en data source Loki no configurados para todos los servicios      | Observabilidad | Bajo     | La correlación log → traza no funciona en todos los servicios; troubleshooting manual                   |
| DT-03 | Políticas de retención de buckets MinIO no configuradas                          | Almacenamiento | Bajo     | Crecimiento ilimitado del almacenamiento; risco RT-01 activo                                            |
| DT-04 | IaC de aprovisionamiento de Grafana (dashboards y data sources) no automatizado  | Automatización | Medio    | Alta dependencia manual para onboarding de nuevos tenants o recuperación tras pérdida de config         |
| DT-05 | Modo monolítico de Loki/Mimir sin evaluación de límites de escalado              | Escalabilidad  | Alto     | Si el volumen supera la capacidad del modo monolítico, se requiere migración urgente a modo distribuido |
| DT-06 | Backup automatizado de volúmenes Docker del servidor no implementado             | Resiliencia    | Medio    | En caso de pérdida del EC2 servidor, los datos históricos no son recuperables                           |

## Plan de Contingencia

| Escenario                        | Respuesta                                                                                                                                   |
| -------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| Disco del servidor al 90% de uso | Eliminar bloques de datos del tenant con menor prioridad; aumentar disco EBS del EC2                                                        |
| Servidor completo caído          | Docker `restart: unless-stopped` reinicia todos los contenedores; los agentes bufferean en memoria hasta reconexión                         |
| Tenant con datos mezclados       | Identificar agente con `TENANT_ID` incorrecto; corregir `.env`; purgar los datos incorrectos via API de Loki (`DELETE /loki/api/v1/delete`) |
| Grafana sin acceso               | Acceder a Loki/Mimir/Tempo directamente via API HTTP para queries de emergencia                                                             |
| MinIO inaccesible                | Backends acumulan en WAL local; restaurar MinIO desde snapshot EBS antes de que el WAL se llene                                             |
