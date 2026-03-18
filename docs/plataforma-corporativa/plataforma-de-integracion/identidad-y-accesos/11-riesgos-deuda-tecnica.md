---
sidebar_position: 11
title: Riesgos y Deuda Técnica
description: Riesgos técnicos y operacionales del Servicio de Identidad.
---

# 11. Riesgos y Deuda Técnica

## Riesgos Técnicos

| ID    | Riesgo                            | Probabilidad | Impacto | Severidad  | Mitigación                                                                           |
| ----- | --------------------------------- | ------------ | ------- | ---------- | ------------------------------------------------------------------------------------ |
| RT-01 | Vulnerabilidades en Keycloak      | Media        | Alto    | ⚠️ Alto    | Actualizaciones regulares siguiendo el changelog oficial; pruebas en staging previas |
| RT-02 | Corrupción de datos de `tenant`   | Baja         | Crítico | 🔴 Crítico | Backups automáticos en RDS Multi-AZ; pruebas de restauración periódicas              |
| RT-03 | Compromiso de claves de firma JWT | Baja         | Crítico | 🔴 Crítico | Rotación periódica de claves por realm; algoritmos RS256/ES256 únicamente            |

## Riesgos Operacionales

| ID    | Riesgo                        | Probabilidad | Impacto | Severidad | Mitigación                                                                |
| ----- | ----------------------------- | ------------ | ------- | --------- | ------------------------------------------------------------------------- |
| RO-01 | Fallo en federación LDAP/SAML | Media        | Medio   | 🟡 Medio  | Fallback a usuarios locales por realm; alertas ante errores de federación |
| RO-02 | Degradación de rendimiento    | Media        | Medio   | 🟡 Medio  | Autoescalado ECS; monitoreo de latencia p95 en Grafana                    |
| RO-03 | Pérdida de logs de auditoría  | Baja         | Alto    | ⚠️ Alto   | Centralización en Loki con retención configurada; backups de índices      |

## Deuda Técnica

| ID    | Deuda                                                                     | Prioridad | Acción                                                                              |
| ----- | ------------------------------------------------------------------------- | --------- | ----------------------------------------------------------------------------------- |
| DT-01 | Métricas custom de Keycloak y alertas en Grafana no configuradas          | Alta      | Crear dashboards sobre login failures, latencia de autenticación y sesiones activas |
| DT-02 | Automatización y pruebas de restauración de backups RDS no implementadas  | Alta      | Configurar backup automático y ejecutar drill de restauración mensual               |
| DT-03 | Redis ElastiCache para caché de sesión y JWKS pendiente de implementación | Media     | Aprovisionar Redis Cluster y configurar TTL de JWKS y sesión por realm              |
| DT-04 | Suite de pruebas de carga y resiliencia sin integrar en pipeline CI/CD    | Media     | Integrar k6 para smoke test de autenticación en cada despliegue                     |
| DT-05 | Workspaces de realms CO y MX parcialmente configurados en Terraform       | Alta      | Completar configuración de federación y roles para Colombia y México                |

## Plan de Contingencia

| Escenario                        | Respuesta                                                                                  |
| -------------------------------- | ------------------------------------------------------------------------------------------ |
| Instancia Keycloak caída         | ALB redirige tráfico a instancias sanas; ECS repone contenedor automáticamente             |
| Todas las instancias fallan      | Activar modo mantenimiento (`503` desde ALB) mientras se restaura el servicio              |
| Corrupción de base de datos      | Restaurar desde snapshot RDS más reciente; tiempo estimado < 30 min con Multi-AZ           |
| Fallo en federación LDAP/SAML    | Usuarios hacen login con credenciales locales del realm; equipo activa alerta y revisa IdP |
| Restaurar configuración de realm | `terraform apply` desde el repositorio principal de IaC; estado gestionado en S3           |
