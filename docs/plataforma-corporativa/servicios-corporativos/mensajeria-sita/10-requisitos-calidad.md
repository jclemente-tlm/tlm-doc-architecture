
# 10. Requisitos de calidad

## 10.1 Requisitos clave

| Categoría      | Métrica/Objetivo                  | Implementación/Medición         |
|--------------- |-----------------------------------|---------------------------------|
| Disponibilidad | 99.9% uptime                      | Health checks, failover         |
| Rendimiento    | Latencia < 500ms (p95)            | Prometheus, logs                |
| Procesamiento  | 10,000 msg/min                    | Métricas de throughput          |
| Seguridad      | TLS 1.3, X.509, validación total  | Certificados, logs, auditoría   |
| Integridad     | 100% delivery, checksums          | Validación, logs                |
| Escalabilidad  | Auto-scaling, multi-tenant        | Pool conexiones, particionado   |
| Recuperación   | RTO < 1 min, RPO < 10 seg         | Pruebas de failover, backups    |

## 10.2 Escenarios de calidad

| Escenario                        | Estímulo/Condición                  | Respuesta esperada                  |
|-----------------------------------|-------------------------------------|-------------------------------------|
| Pico de tráfico                   | 500% incremento de mensajes         | Latencia < 500ms, sin pérdida       |
| Falla de red SITA                 | Caída de conexión principal         | Failover automático, sin pérdida    |
| Ataque o acceso no autorizado     | Mensaje malicioso o intento acceso  | Bloqueo inmediato, alerta, auditoría|
| Onboarding de nuevos tenants      | Alta de 10 tenants simultáneos      | Provisioning automático, sin impacto|

## 10.3 Métricas de calidad

| Métrica                  | Objetivo                | Frecuencia |
|--------------------------|-------------------------|------------|
| MTBF                     | > 720 horas             | Continua   |
| MTTR                     | < 30 segundos           | Por evento |
| Éxito entrega mensajes   | 99.99%                  | Continua   |
| Latencia end-to-end      | < 500ms (p95)           | Continua   |
| Uso CPU                  | < 70%                   | Continua   |
| Uso memoria              | < 80%                   | Continua   |
| Incidentes seguridad     | < 5 min respuesta       | Por evento |

## 10.4 Monitoreo y alertas

- Dashboards: latencia, throughput, errores, estado conexiones, incidentes seguridad.
- Alertas críticas: caídas SITA, fallos entrega, incidentes seguridad, degradación performance.
- Reportes periódicos: cumplimiento SLA, tendencias de calidad, incidentes relevantes.
