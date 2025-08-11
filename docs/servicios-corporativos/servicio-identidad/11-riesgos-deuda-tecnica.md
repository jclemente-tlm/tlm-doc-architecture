# 11. Riesgos Y Deuda Técnica

## 11.1 Riesgos Identificados

| Riesgo                        | Probabilidad | Impacto | Mitigación                                 |
|-------------------------------|--------------|---------|--------------------------------------------|
| Vulnerabilidades `Keycloak`   | Media        | Alto    | Actualizaciones regulares                  |
| Corrupción de `tenant`        | Baja         | Alto    | Backups automáticos y pruebas de restauración |
| Fallo en federación           | Media        | Medio   | Fallback local y alertas                   |
| Degradación de rendimiento    | Media        | Medio   | Monitoreo y autoescalado                   |
| Pérdida de logs/auditoría     | Baja         | Alto    | Centralización y backups                   |

## 11.2 Deuda Técnica

| Área           | Descripción                        | Prioridad | Esfuerzo   |
|----------------|------------------------------------|-----------|------------|
| Monitoring     | Métricas custom y alertas          | Alta      | 1 sprint   |
| Backup         | Automatización y pruebas           | Alta      | 2 sprints  |
| Documentación  | Guías de administración            | Media     | 1 sprint   |
| Testing        | Pruebas de carga y resiliencia     | Media     | 2 sprints  |

## 11.3 Acciones Recomendadas

| Acción                            | Plazo      | Responsable   |
|------------------------------------|------------|--------------|
| Completar monitoreo y alertas      | 2 semanas  | SRE          |
| Mejorar backup y restauración      | 1 mes      | DevOps       |
| Pruebas de carga y stress          | 1 mes      | QA           |
| Auditoría de seguridad             | 6 semanas  | Security     |
| Revisión de documentación          | 2 semanas  | Arquitectura |

- Matriz de riesgos y deuda técnica priorizada y revisada periódicamente.
- Estrategias de mitigación claras, responsables asignados y seguimiento continuo.

## 11.4 Referencias

- [Arc42 Risk Management](https://docs.arc42.org/section-11/)
- [Keycloak Security Docs](https://www.keycloak.org/docs/latest/server_admin/#security)
- [C4 Model for Software Architecture](https://c4model.com/)
