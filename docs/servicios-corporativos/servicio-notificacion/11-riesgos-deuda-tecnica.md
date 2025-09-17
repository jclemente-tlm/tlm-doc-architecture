# 11. Riesgos y deuda técnica

## 11.1 Riesgos identificados

| Riesgo                        | Probabilidad | Impacto | Mitigación Técnica                                                                 |
|-------------------------------|--------------|---------|------------------------------------------------------------------------------------|
| Falla de `Redis`              | Media        | Alto    | Clustering, backup automatizado, monitoreo con `Prometheus`, failover              |
| Corrupción de plantillas      | Baja         | Medio   | Versionado, validación, backups, pruebas automatizadas                             |
| Límites de proveedores        | Media        | Medio   | Multi-proveedor, failover automático, alertas, desacoplamiento vía interfaces      |
| Overflow en colas             | Media        | Alto    | Autoescalado, monitoreo de profundidad, alertas críticas, DLQ                      |
| Exposición de datos sensibles | Baja         | Crítico | Cifrado (`AES-256`), sanitización de logs, controles de acceso (`Keycloak`)        |
| Cambios regulatorios          | Baja         | Alto    | Arquitectura flexible, revisiones legales periódicas, automatización de compliance  |
| Abuso del sistema             | Baja         | Medio   | `Rate limiting` por `tenant (realm)`, monitoreo de patrones anómalos               |

## 11.2 Deuda técnica

| Área           | Descripción                        | Prioridad | Esfuerzo | Impacto en Calidad           |
|----------------|-----------------------------------|-----------|----------|------------------------------|
| Monitoreo      | Métricas custom insuficientes      | Alta      | 1 sprint | Observabilidad, alertabilidad|
| Testing        | Pruebas de carga limitadas         | Media     | 2 sprints| Fiabilidad, performance      |
| Plantillas     | Editor visual incompleto           | Baja      | 3 sprints| Usabilidad, mantenibilidad   |
| Analytics      | Métricas de entrega parciales      | Media     | 2 sprints| Trazabilidad, reporting      |
| Configuración  | Parámetros hardcodeados            | Alta      | 1 sprint | Seguridad, flexibilidad      |

## 11.3 Acciones recomendadas

| Acción                                 | Plazo     | Responsable | Entregable Principal                |
|----------------------------------------|-----------|-------------|-------------------------------------|
| Implementar monitoreo integral         | 2 semanas | SRE         | Dashboards y alertas en `Grafana`   |
| Clustering y failover de `Redis`       | 1 mes     | DevOps      | Alta disponibilidad, pruebas de failover |
| Pruebas de carga y stress              | 1 mes     | QA          | Reportes de performance y tuning    |
| Dashboard de analytics                 | 6 semanas | Product     | Paneles de métricas de entrega      |
| Refactorizar configuración externa     | 2 semanas | DevOps      | Uso de `AWS Secrets Manager`        |
| Completar documentación y runbooks     | 2 semanas | Equipo      | Manuales operativos y API           |

## 11.4 Gestión de riesgos

- Proveedores: fallo simultáneo mitigado con multi-proveedor, failover automático y monitoreo de SLA (`Prometheus`).
- Infraestructura: saturación de colas en `Redis` o base de datos mitigada con autoescalado, alertas y DLQ.
- Seguridad: exposición de datos personales mitigada con cifrado, sanitización de logs (`Serilog`), controles de acceso (`Keycloak`).
- Cumplimiento: cambios regulatorios (`GDPR`, `CAN-SPAM`, `TCPA`) mitigados con arquitectura flexible y automatización de compliance.
- Operacional: abuso del sistema mitigado con `rate limiting` por `tenant (realm)`, monitoreo de patrones anómalos y alertas automáticas.

## 11.5 Métricas y seguimiento

- SLA de proveedores: `> 99.5%` disponibilidad (`Prometheus`)
- Tiempo de respuesta de base de datos: `< 50ms p95` (`OpenTelemetry`)
- Code coverage: meta `85%` (`SonarQube`)
- Complejidad ciclomática: meta `< 10` (`SonarQube`)
- Duplicación de código: meta `< 5%` (`SonarQube`)
- Error rate: `> 1%` en 5 minutos → alerta inmediata (`Loki`)
- Profundidad de cola: `> 10,000` mensajes → escalación automática
- Delivery rate: `< 99%` → revisión semanal
- Incidentes críticos: reporte y análisis post-mortem obligatorio

## 11.6 Plan de remediación

- Refactorización hacia interfaces abstractas para desacoplar proveedores y facilitar multi-proveedor
- Implementar test contracts y mocks mejorados para integración continua
- Estandarizar logging estructurado con `Serilog` y exportación a `Loki`
- Migrar parámetros hardcodeados a configuración externa segura (`AWS Secrets Manager`)
- Completar documentación de APIs y runbooks operativos accesibles
- Automatizar pruebas de resiliencia y failover

## 11.7 Proceso de revisión

- Revisión quincenal en retrospectivas técnicas
- Escalación si riesgo crítico > `50%` o deuda impacta > `20%` en velocity
- Seguimiento de acciones y métricas en tablero de calidad
- Actualización continua de riesgos y deuda técnica según evolución del sistema
