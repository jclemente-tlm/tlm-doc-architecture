
# 11. Riesgos y deuda técnica

## 11.1 Riesgos principales

| Riesgo                        | Probabilidad | Impacto | Mitigación principal           |
|-------------------------------|--------------|---------|-------------------------------|
| Falla red SITA                | Media        | Alto    | Redundancia, failover         |
| Expiración de certificados    | Media        | Alto    | Monitoreo, automatización     |
| Degradación performance       | Alta         | Medio   | Auto-scaling, particionado    |
| Cambios regulatorios          | Alta         | Alto    | Monitoreo, arquitectura flexible |
| Expertise limitado            | Alta         | Alto    | Capacitación, documentación   |
| Vulnerabilidades protocolo    | Baja         | Crítico | Validación, monitoreo         |

## 11.2 Deuda técnica relevante

| Área                | Descripción breve                        | Prioridad | Acción recomendada         |
|---------------------|------------------------------------------|-----------|---------------------------|
| Configuración       | Endpoints hardcoded                      | Media     | Centralizar configuración |
| Testing             | Cobertura limitada de fallos             | Alta      | Pruebas integrales        |
| Observabilidad      | Logs y métricas fragmentados              | Media     | Unificar y centralizar    |
| Certificados        | Gestión manual                           | Alta      | Automatizar ciclo de vida |
| Performance DB      | Escalabilidad futura                     | Alta      | Sharding, archivado       |
| Multi-región        | Complejidad de despliegue                | Media     | Diseño region-aware       |

## 11.3 Acciones y métricas

- Automatizar gestión de certificados y monitoreo de expiración.
- Mejorar cobertura de pruebas de fallos y recuperación.
- Centralizar configuración y observabilidad.
- Preparar arquitectura para crecimiento y multi-región.

| Métrica clave                | Umbral           | Acción                |
|------------------------------|------------------|-----------------------|
| Fallos conexión SITA         | > 5/día          | Escalamiento inmediato|
| Advertencias expiración cert | < 30 días        | Renovación automática |
| Degradación performance      | > 20% baseline   | Auto-scaling          |
| Incidentes críticos seguridad| > 0              | Respuesta inmediata   |
