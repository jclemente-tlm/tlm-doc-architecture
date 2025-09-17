# 10. Requisitos de calidad

## 10.1 Disponibilidad

| Métrica                        | Objetivo           | Medición                   |
|-------------------------------|-------------------|----------------------------|
| Disponibilidad de servicios    | 99.95%            | Prometheus, AWS CloudWatch |
| Disponibilidad de ingesta      | 99.99%            | Health checks              |
| Disponibilidad de consultas    | 99.9%             | Monitoreo                  |

## 10.2 Rendimiento

| Métrica                | Objetivo         | Medición         |
|------------------------|------------------|------------------|
| Latencia ingesta       | < 100ms P95      | Prometheus       |
| Throughput             | 1k eventos/min   | Load testing     |
| Latencia consulta      | < 200ms          | Monitoreo        |

## 10.3 Escalabilidad

| Aspecto                        | Objetivo           | Estrategia                |
|-------------------------------|-------------------|---------------------------|
| Escalabilidad horizontal       | Auto-scaling       | AWS ECS Fargate           |
| Escalabilidad de base de datos | Alta disponibilidad| Réplicas de lectura       |
| Escalabilidad de mensajería    | Escalado automático| AWS SQS                   |

## 10.4 Seguridad

| Aspecto         | Requisito          | Implementación   |
|-----------------|--------------------|------------------|
| Autenticación   | JWT                | Middleware .NET  |
| Autorización    | Claims y roles     | .NET 8           |
| Cifrado         | TLS 1.3, AES-256   | HTTPS, AWS KMS   |
| Auditoría       | Registro de eventos| Serilog, PostgreSQL |

## 10.5 Confiabilidad

| Métrica                | Objetivo           | Medición         |
|------------------------|-------------------|------------------|
| Pérdida de datos       | Tolerancia cero   | Transaction logs |
| Consistencia           | Consistencia fuerte | PostgreSQL     |

## 10.6 Mantenibilidad

| Métrica                | Objetivo           | Medición         |
|------------------------|-------------------|------------------|
| Cobertura de código    | > 85%             | CI/CD            |
| Tiempo de despliegue   | < 5 min           | Pipeline         |

## 10.7 Cumplimiento

| Estándar        | Requisito          | Medición         |
|-----------------|-------------------|------------------|
| ISO 27001       | Audit trail        | 100% coverage    |
| SOC 2           | Uptime             | 99.9%            |
| GDPR            | Data retention     | 100% compliance  |

## 10.8 Estrategias de implementación

- Despliegue multi-AZ y auto-scaling en AWS ECS Fargate
- PostgreSQL con réplicas y backup automatizado
- Instrumentación con Serilog, Prometheus, OpenTelemetry
- Autenticación y autorización con JWT
- Health checks y monitoreo continuo

## 10.9 Escenarios de calidad

- Failover automático ante falla de base de datos
- Auto-scaling ante picos de tráfico
- Bloqueo inmediato ante intento de acceso no autorizado
- Disaster recovery con RTO < 15 minutos, RPO < 1 minuto

## 10.10 Métricas y monitoreo

- SLIs y SLOs definidos para disponibilidad, latencia, error rate y consistencia
- Dashboards en Prometheus y Grafana
- Alertas automáticas para eventos críticos
