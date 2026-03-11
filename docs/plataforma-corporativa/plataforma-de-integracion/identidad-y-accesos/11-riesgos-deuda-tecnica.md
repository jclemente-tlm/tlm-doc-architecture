---
sidebar_position: 11
title: Riesgos y Deuda Técnica
description: Riesgos técnicos y operacionales del Servicio de Identidad.
---

# 11. Riesgos y Deuda Técnica

## Riesgos Identificados

| Riesgo                      | Probabilidad | Impacto | Mitigación                                    |
| --------------------------- | ------------ | ------- | --------------------------------------------- |
| Vulnerabilidades `Keycloak` | Media        | Alto    | Actualizaciones regulares                     |
| Corrupción de `tenant`      | Baja         | Alto    | Backups automáticos y pruebas de restauración |
| Fallo en federación         | Media        | Medio   | Fallback local y alertas                      |
| Degradación de rendimiento  | Media        | Medio   | Monitoreo y autoescalado                      |
| Pérdida de logs/auditoría   | Baja         | Alto    | Centralización y backups                      |

## Deuda Técnica

| ID    | Área          | Descripción                                        | Prioridad | Esfuerzo  |
| ----- | ------------- | -------------------------------------------------- | --------- | --------- |
| DT-01 | Monitoring    | Métricas custom y alertas                          | Alta      | 1 sprint  |
| DT-02 | Backup        | Automatización y pruebas                           | Alta      | 2 sprints |
| DT-03 | Documentación | Guías de administración                            | Media     | 1 sprint  |
| DT-04 | Testing       | Pruebas de carga y resiliencia                     | Media     | 2 sprints |
| DT-05 | Caching       | Redis ElastiCache para sesión y JWKS _(pendiente)_ | Media     | 1 sprint  |

## Plan de Contingencia

| Escenario              | Acción inmediata             | Plazo     | Responsable |
| ---------------------- | ---------------------------- | --------- | ----------- |
| Completar monitoreo    | Completar métricas y alertas | 2 semanas | SRE         |
| Backup y restauración  | Automatizar y probar backups | 1 mes     | DevOps      |
| Pruebas de carga       | Ejecutar suite de stress     | 1 mes     | QA          |
| Auditoría de seguridad | Revisión independiente       | 6 semanas | Security    |
| Implementar Redis      | Configurar ElastiCache + TTL | 2 sprints | Backend     |
