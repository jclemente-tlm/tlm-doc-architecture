---
id: runbooks
sidebar_position: 5
title: Runbooks
description: Estándar para crear runbooks operacionales con procedimientos de diagnóstico, mitigación y escalación para incidentes en producción.
---

# Runbooks

## Contexto

Este estándar define cómo crear runbooks operacionales que permitan responder rápida y consistentemente a incidentes en producción. Complementa el lineamiento [Documentación Técnica](../../lineamientos/desarrollo/03-documentacion-tecnica.md).

---

## Stack Tecnológico

| Componente          | Tecnología   | Versión | Uso                          |
| ------------------- | ------------ | ------- | ---------------------------- |
| **Documentación**   | Markdown     | -       | Formato de runbooks          |
| **Observabilidad**  | Grafana      | 10.0+   | Dashboards y alertas         |
| **Logs**            | Grafana Loki | -       | Centralización de logs       |
| **Incidentes**      | PagerDuty    | -       | Alertas y escalación on-call |
| **Infraestructura** | AWS CLI      | 2.0+    | Comandos de remediación      |

---

## ¿Qué es un Runbook?

Documento operacional con procedimientos paso a paso para diagnosticar y resolver problemas comunes en producción.

**Tipos de runbooks:**

1. **Incident Response**: Qué hacer cuando hay un incidente
2. **Troubleshooting**: Diagnosticar problemas específicos
3. **Maintenance**: Procedimientos de mantenimiento
4. **Deployment**: Procedimientos de despliegue
5. **Disaster Recovery**: Recuperación ante desastres

**Propósito:** Respuesta rápida y consistente a problemas operacionales.

**Beneficios:**
✅ Resolución más rápida de incidentes
✅ Menos dependencia de individuos
✅ Procedimientos documentados y testeados
✅ Onboarding operacional más rápido

## Plantilla de Runbook: Respuesta a Incidentes

````markdown
# Runbook: Customer API - High Error Rate

## Metadata

| Campo            | Valor         |
| ---------------- | ------------- |
| **Service**      | Customer API  |
| **Severity**     | SEV-2 (Alta)  |
| **On-Call**      | Customer Team |
| **Last Updated** | 2026-02-18    |
| **Version**      | 1.2.0         |

---

## 🚨 Síntomas

### Alertas que Disparan

- `CustomerAPI_ErrorRate > 5%` (últimos 5 minutos)
- `CustomerAPI_P95Latency > 2000ms`
- `CustomerAPI_5xx_Errors > 50` (últimos 5 minutos)

### Impacto en Usuarios

- ❌ Usuarios no pueden crear/actualizar clientes
- ❌ Búsqueda de clientes lenta o fallando
- ⚠️ Otros servicios que dependen de Customer API afectados

### Grafana Dashboard

https://grafana.talma.com/d/customer-api-overview

---

## 🔍 Triage (Primeros 5 minutos)

### 1. Verificar si es incidente real

```bash
# Verificar health del servicio
curl -I https://customer-api.talma.com/health

# Respuesta esperada: 200 OK
# Si 503 Service Unavailable → Servicio caído
```
````

### 2. Verificar alcance

- **¿1 instancia o todas?**
  - Ir a AWS ECS Console → customer-service-prod cluster
  - Ver si todas las tasks son unhealthy

- **¿1 región o múltiples?**
  - Verificar si alertas solo en us-east-1 o también otras regiones

- **¿Solo Customer API o otros servicios también?**
  - Revisar Grafana dashboard general

### 3. Verificar cambios recientes

```bash
# Ver últimos deploys
aws ecs describe-services \
  --cluster customer-service-prod \
  --services customer-api \
  --query 'services[0].deployments' \
  --region us-east-1

# Ver últimos commits en main
gh api repos/talma/customer-service/commits \
  --jq '.[0:5] | .[] | {date:.commit.author.date, message:.commit.message}'
```

### 4. Declarar Incidente

Si error rate > 10% o P95 > 3s:

```bash
# Crear incidente en Slack
/incident declare Customer API High Error Rate

# Página on-call si fuera de horario
@pagerduty-customer-team
```

---

## 🔧 Diagnóstico (Siguientes 10-15 minutos)

### Paso 1: Revisar Logs

```bash
# Logs de errores últimos 15 minutos
aws logs filter-log-events \
  --log-group-name /ecs/customer-service-prod \
  --start-time $(date -u -d '15 minutes ago' +%s)000 \
  --filter-pattern '{ $.level = "Error" }' \
  --limit 50 \
  --region us-east-1 | jq '.events[].message' | jq -s '.'

# Alternativamente, en Grafana Loki:
# Query: {service="customer-api", environment="production"} |= "error" | json
```

**Patrones comunes:**

- **"Connection pool exhausted"** → Ver Paso 2.1
- **"Kafka broker not available"** → Ver Paso 2.2
- **"Redis timeout"** → Ver Paso 2.3
- **"JWT validation failed"** → Ver Paso 2.4

### Paso 2: Diagnosticar Causa Raíz

#### 2.1. Database Connection Issues

```bash
# Verificar RDS instance
aws rds describe-db-instances \
  --db-instance-identifier customer-db-prod \
  --query 'DBInstances[0].{Status:DBInstanceStatus,CPU:CPUUtilization}' \
  --region us-east-1

# Check connection count
aws cloudwatch get-metric-statistics \
  --namespace AWS/RDS \
  --metric-name DatabaseConnections \
  --start-time $(date -u -d '30 minutes ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Maximum \
  --dimensions Name=DBInstanceIdentifier,Value=customer-db-prod \
  --region us-east-1
```

**Si conexiones cerca del máximo (100):**

```bash
# Escalar RDS instance temporalmente
aws rds modify-db-instance \
  --db-instance-identifier customer-db-prod \
  --db-instance-class db.r6g.2xlarge \
  --apply-immediately \
  --region us-east-1

# O reiniciar instancias de ECS para reset connection pool
aws ecs update-service \
  --cluster customer-service-prod \
  --service customer-api \
  --force-new-deployment \
  --region us-east-1
```

#### 2.2. Kafka Issues

```bash
# Check Kafka broker health
ssh kafka-broker-1.internal.talma.com

# Ver logs de Kafka
tail -f /var/log/kafka/server.log | grep ERROR

# Ver consumer lag
kafka-consumer-groups.sh \
  --bootstrap-server localhost:9092 \
  --describe \
  --group customer-service-consumer
```

**Si Kafka broker caído:**

- Contactar @platform-team en #kafka-support
- Mientras tanto, deshabilitar publicación de eventos:

```bash
aws ssm put-parameter \
  --name "/customer-service/prod/features/enable-event-publishing" \
  --value "false" \
  --type String \
  --overwrite \
  --region us-east-1

aws ecs update-service \
  --cluster customer-service-prod \
  --service customer-api \
  --force-new-deployment \
  --region us-east-1
```

#### 2.3. Redis Cache Issues

```bash
# Check ElastiCache Redis
aws elasticache describe-cache-clusters \
  --cache-cluster-id customer-redis-prod \
  --show-cache-node-info \
  --region us-east-1
```

**Si Redis no responde:**

```bash
# Deshabilitar cache temporalmente
aws ssm put-parameter \
  --name "/customer-service/prod/features/enable-cache" \
  --value "false" \
  --type String \
  --overwrite \
  --region us-east-1

aws ecs update-service \
  --cluster customer-service-prod \
  --service customer-api \
  --force-new-deployment \
  --region us-east-1

# Nota: Performance degradará pero servicio seguirá funcionando
```

#### 2.4. Authentication Issues

```bash
# Verificar Keycloak
curl -I https://keycloak.talma.com/health

# Si Keycloak caído, verificar con @security-team
# Logs mostrarán: "Unable to validate JWT: Authority is unreachable"
```

---

## 🛠 Mitigación (Acción Inmediata)

### Opción 1: Rollback a Versión Anterior (Más Seguro)

```bash
# 1. Identificar última versión estable
aws ecs describe-services \
  --cluster customer-service-prod \
  --services customer-api \
  --query 'services[0].deployments' \
  --region us-east-1

# 2. Rollback manualmente
# Ir a AWS ECS Console → customer-service-prod → customer-api
# → Update Service → Revision: previous stable revision

# O via Terraform:
cd terraform/environments/production
git checkout <previous-stable-commit>
terraform apply -auto-approve

# 3. Monitorear deployment
aws ecs wait services-stable \
  --cluster customer-service-prod \
  --services customer-api \
  --region us-east-1
```

### Opción 2: Escalar Horizontalmente

```bash
# Si issue es de capacidad, escalar temporalmente
aws ecs update-service \
  --cluster customer-service-prod \
  --service customer-api \
  --desired-count 10 \
  --region us-east-1
```

### Opción 3: Feature Flag para Deshabilitar Funcionalidad Problemática

```bash
# Ejemplo: Si solo endpoint /customers/search falla
aws ssm put-parameter \
  --name "/customer-service/prod/features/enable-advanced-search" \
  --value "false" \
  --type String \
  --overwrite \
  --region us-east-1

aws ecs update-service \
  --cluster customer-service-prod \
  --service customer-api \
  --force-new-deployment \
  --region us-east-1
```

---

## ✅ Verificación (Post-Mitigación)

### 1. Verificar Métricas

Esperar 5-10 minutos y verificar en Grafana:

- ✅ Error Rate < 1%
- ✅ P95 Latency < 200ms
- ✅ 5xx Errors < 5/min

### 2. Smoke Tests

```bash
# Test crítico de funcionalidad
curl -X POST https://customer-api.talma.com/api/v1/customers \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Smoke Test",
    "email": "smoketest@example.com",
    "document": {
      "type": "DNI",
      "number": "99999999"
    }
  }'

# Debe retornar 201 Created
```

### 3. Comunicar Resolución

```bash
# En canal de incidente de Slack
/incident update Mitigated. Rolled back to version 1.2.3.
Error rate back to normal (<1%). Monitoring for 30 minutes before closing.
```

---

## 📊 Post-Mortem

Después de resolver incidente:

### 1. Crear Issue de Post-Mortem

```bash
gh issue create \
  --title "[Post-Mortem] Customer API High Error Rate - 2026-02-18" \
  --label "postmortem" \
  --assignee @tech-lead \
  --body "
## Incident Summary
- **Date**: 2026-02-18 14:30 UTC
- **Duration**: 45 minutes
- **Severity**: SEV-2

## Timeline
- 14:30: Alert triggered
- 14:35: On-call responded
- 14:45: Root cause identified (DB connection exhaustion)
- 15:00: Mitigated (rolled back deployment)
- 15:15: Verified resolution

## Root Cause
[TBD - To be filled after analysis]

## Action Items
- [ ] Increase DB connection pool limits
- [ ] Add circuit breaker for DB connections
- [ ] Improve monitoring alerts
- [ ] Update runbook with learnings
"
```

### 2. Agenda Post-Mortem Meeting

- **Cuándo**: Dentro de 48 horas
- **Quién**: Equipo involucrado + Tech Lead + Arquitecto
- **Duración**: 1 hora
- **Resultado**: Post-mortem document con action items

---

## 📞 Escalation

### Nivel 1: On-Call Engineer (tú)

- Diagnosticar y mitigar según runbook
- Tiempo máximo: 30 minutos antes de escalar

### Nivel 2: Tech Lead

- Si no puedes resolver en 30 min
- Para decisiones que requieren cambios significativos
- Contacto: @tech-lead-customer en Slack (#customer-service), Tel: +51-XXX-XXX-XXX

### Nivel 3: Platform Team

- Para issues de infraestructura (Kafka, RDS, networking)
- Contacto: @platform-team en Slack (#platform-support)

### Nivel 4: Arquitecto

- Para decisiones arquitectónicas críticas
- Contacto: @arquitecto en Slack, Tel: +51-YYY-YYY-YYY

---

## 🔗 Referencias del Runbook

- **Grafana Dashboard**: [Ver Dashboard](https://grafana.talma.com/d/customer-api-overview)
- **AWS ECS Console**: [Ver Consola](https://console.aws.amazon.com/ecs/home?region=us-east-1#/clusters/customer-service-prod)
- **Jira Board**: [Ver Board](https://talma.atlassian.net/browse/CUST)
- **Otros Runbooks**: [Índice](README.md)

---

**Versión**: 1.2.0
**Última Actualización**: 2026-02-18
**Próxima Revisión**: 2026-05-18 (cada 3 meses)

```

## Organización de Runbooks

```

docs/runbooks/
├── README.md # Índice de runbooks
├── incident-response/
│ ├── high-error-rate.md
│ ├── service-down.md
│ ├── high-latency.md
│ └── database-connection-exhaustion.md
├── troubleshooting/
│ ├── kafka-consumer-lag.md
│ ├── redis-cache-misses.md
│ ├── authentication-failures.md
│ └── memory-leaks.md
├── maintenance/
│ ├── database-maintenance-window.md
│ ├── scaling-for-high-traffic.md
│ └── certificate-renewal.md
├── deployment/
│ ├── production-deployment.md
│ ├── rollback-procedure.md
│ └── blue-green-deployment.md
└── disaster-recovery/
├── database-restore.md
├── region-failover.md
└── complete-service-recovery.md

````

---

## Implementación

```bash
# 1. Crear estructura de runbooks
mkdir -p docs/runbooks/{incident-response,troubleshooting,maintenance,deployment,disaster-recovery}

# 2. Crear índice de runbooks
cat > docs/runbooks/README.md << 'EOF'
# Runbooks - Customer Service

## Incident Response
- [High Error Rate](incident-response/high-error-rate.md)
- [Service Down](incident-response/service-down.md)
- [High Latency](incident-response/high-latency.md)

## Troubleshooting
- [Kafka Consumer Lag](troubleshooting/kafka-consumer-lag.md)
- [Redis Cache Issues](troubleshooting/redis-cache-misses.md)

## Maintenance
- [Database Maintenance](maintenance/database-maintenance-window.md)
- [Scaling for High Traffic](maintenance/scaling-for-high-traffic.md)

## Deployment
- [Production Deployment](deployment/production-deployment.md)
- [Rollback Procedure](deployment/rollback-procedure.md)

## Disaster Recovery
- [Database Restore](disaster-recovery/database-restore.md)
- [Region Failover](disaster-recovery/region-failover.md)
EOF

# 3. Verificar con markdownlint
npm install -g markdownlint-cli
markdownlint 'docs/**/*.md'
````

---

## Requisitos Técnicos

### MUST (Obligatorio)

- **MUST** crear runbooks para incidentes críticos (SEV-1, SEV-2)
- **MUST** incluir síntomas, diagnóstico, mitigación y verificación
- **MUST** incluir ruta de escalación
- **MUST** revisar runbooks cada 3 meses

### SHOULD (Fuertemente recomendado)

- **SHOULD** probar runbooks en simulacros de recuperación ante desastres
- **SHOULD** incluir tiempo estimado de resolución en runbooks
- **SHOULD** incluir runbooks para todos los procedimientos operacionales frecuentes
- **SHOULD** incluir pruebas de verificación post-mitigación

### MAY (Opcional)

- **MAY** automatizar pasos repetibles del runbook con scripts
- **MAY** crear chatbot con runbooks automatizados
- **MAY** generar runbooks desde incidentes post-mortem

### MUST NOT (Prohibido)

- **MUST NOT** incluir secretos o credentials en runbooks
- **MUST NOT** documentar sin versionar en Git
- **MUST NOT** crear runbooks con pasos manuales sin intentar automatización posible

---

## Referencias

- [Google SRE Book - Runbooks](https://sre.google/sre-book/practical-alerting/)
- [PagerDuty Runbook Guide](https://www.pagerduty.com/resources/learn/what-is-a-runbook/)
- [Guía de Onboarding](./onboarding-guide.md)
- [Procedimientos de DR](../operabilidad/dr-procedures.md)

---

**Última actualización**: 18 de febrero de 2026
**Responsable**: Equipo de Arquitectura
