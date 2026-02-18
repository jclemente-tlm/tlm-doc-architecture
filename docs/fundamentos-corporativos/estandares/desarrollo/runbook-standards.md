---
id: runbook-standards
sidebar_position: 8
title: Runbook Standards
description: Documentación operativa para diagnóstico, troubleshooting y resolución de incidentes
---

# Runbook Standards

## Contexto

Este estándar define **Runbooks**: documentación operativa que guía **diagnóstico, troubleshooting y resolución de incidentes** paso a paso. Incidentes en producción requieren respuesta rápida; runbooks documentan **cómo responder**. Complementa el [lineamiento de Documentación Técnica](../../lineamientos/desarrollo/03-documentacion-tecnica.md) enfocándose en **operaciones**.

---

## Concepto Fundamental

```yaml
# ¿Qué es un Runbook?

Runbook = Procedimiento operativo documentado

Contiene:
  1. Descripción del problema/tarea
  2. Síntomas y detección
  3. Pasos de diagnóstico
  4. Pasos de resolución
  5. Validación de fix
  6. Rollback si falla
  7. Postmortem/escalation

# Diferencia con otros documentos

README.md:
  - Audiencia: Developers
  - Contenido: Arquitectura, setup local, cómo contribuir

ADR (Architecture Decision):
  - Audiencia: Architects, Developers
  - Contenido: Por qué decisión X (tecnología, patrón)

Runbook:
  - Audiencia: Operations, On-Call Engineers
  - Contenido: Cómo resolver problema Y (paso a paso)

arc42:
  - Audiencia: Technical stakeholders
  - Contenido: Arquitectura completa (contexto, building blocks, deployment)

# Ejemplo

Problem: "Service is down" (500 errors)

README:       ❌ No ayuda (explica arquitectura, no troubleshooting)
ADR:          ❌ No ayuda (explica por qué elegimos ECS, no cómo debuggear)
Runbook:      ✅ Sí ayuda ("Check ECS Task health → View logs → Restart task")
```

## Estructura de Runbook

````markdown
# Runbook: [Problem/Task Name]

## Metadata

- **Service**: Sales Service
- **Severity**: P1 (critical), P2 (high), P3 (medium)
- **Owner**: Platform Team
- **Last Updated**: 2024-01-15
- **Versión**: 2.1

## Symptoms

Cómo detectar el problema:

- **Alert**: CloudWatch alarm "SalesServiceHighErrorRate" firing
- **User Impact**: Users receive 500 errors on checkout
- **Metrics**:
  - Error rate > 5% (normal: <0.1%)
  - Latency p99 > 2s (normal: <500ms)
- **Logs**: Errors in CloudWatch Logs group `/aws/ecs/sales-service`

## Diagnosis

### Step 1: Check Service Health

```bash
# ECS Task status
aws ecs describe-services \
  --cluster production \
  --services sales-service \
  --query 'services[0].{Running:runningCount,Desired:desiredCount,Status:status}'

# Expected: Running = Desired (e.g., 4/4)
# If Running < Desired → Tasks crashing
```
````

### Step 2: Check Recent Deployments

```bash
# Last 5 deployments
aws ecs list-task-definitions \
  --family-prefix sales-service \
  --sort DESC \
  --max-items 5

# Current running version
aws ecs describe-tasks \
  --cluster production \
  --tasks $(aws ecs list-tasks --cluster production --service-name sales-service --query 'taskArns[0]' --output text) \
  --query 'tasks[0].taskDefinitionArn'

# If deployed < 30 min ago → Likely cause
```

### Step 3: Review Logs

```bash
# Tail last 100 errors
aws logs tail /aws/ecs/sales-service \
  --follow \
  --filter-pattern "ERROR" \
  --since 10m

# Common patterns:
# - "Database connection timeout" → DB issue
# - "OutOfMemoryError" → Resource limits
# - "NullReferenceException" → Code bug in recent deploy
```

### Step 4: Check Dependencies

```bash
# Database connectivity
aws rds describe-db-instances \
  --db-instance-identifier sales-db \
  --query 'DBInstances[0].DBInstanceStatus'

# Expected: "available"

# Check CPU/Memory
aws rds describe-db-instance \
  --db-instance-identifier sales-db \
  --query 'DBInstances[0].{CPU:CpuUtilization,Memory:FreeableMemory}'
```

## Resolution

### Scenario A: Bad Deployment

If deployed < 30 min ago + new errors:

```bash
# Rollback to previous task definition
PREVIOUS_VERSION=$(aws ecs list-task-definitions --family-prefix sales-service --sort DESC --max-items 2 --query 'taskDefinitionArns[1]' --output text)

aws ecs update-service \
  --cluster production \
  --service sales-service \
  --task-definition $PREVIOUS_VERSION

# Monitor rollback (takes ~2 min)
watch -n 5 'aws ecs describe-services --cluster production --services sales-service --query "services[0].deployments"'

# Expected: 2 deployments (PRIMARY=old version rolling out, ACTIVE=new version draining)
```

### Scenario B: Database Connection Issue

If logs show "Database connection timeout":

```bash
# Check Security Group (Application → Database)
aws ec2 describe-security-groups \
  --group-ids sg-xxxxxxxxx \
  --query 'SecurityGroups[0].IpPermissions[].[FromPort,ToPort,IpRanges[0].CidrIp]'

# Expected: Port 5432 from 10.0.10.0/24 (Application subnet)

# Check RDS availability
aws rds describe-db-instances \
  --db-instance-identifier sales-db \
  --query 'DBInstances[0].Endpoint.Address'

# Test connectivity from ECS Task
aws ecs execute-command \
  --cluster production \
  --task <task-arn> \
  --container sales-service \
  --interactive \
  --command "/bin/sh"

# Inside container:
# nc -zv sales-db.xxxxx.us-east-1.rds.amazonaws.com 5432
# Expected: "Connection succeeded"
```

Resolution:

- If Security Group wrong → Update SG rules
- If RDS unavailable → Check RDS maintenance window, failover to standby

### Scenario C: Resource Exhaustion (OOM)

If logs show "OutOfMemoryError":

```bash
# Check Task memory usage
aws cloudwatch get-metric-statistics \
  --namespace AWS/ECS \
  --metric-name MemoryUtilization \
  --dimensions Name=ServiceName,Value=sales-service \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Average

# If consistently > 85% → Increase memory limit

# Temporary fix: Restart tasks (clears memory leak)
aws ecs update-service \
  --cluster production \
  --service sales-service \
  --force-new-deployment

# Permanent fix: Update Task Definition memory
# Edit terraform/production/ecs.tf:
# memory = 1024 → memory = 2048
# Then: terraform apply
```

## Validation

Verificar que el servicio se recuperó:

```bash
# 1. Check Task health
aws ecs describe-services --cluster production --services sales-service \
  --query 'services[0].{Running:runningCount,Desired:desiredCount}'

# Expected: Running = Desired

# 2. Check error rate
aws cloudwatch get-metric-statistics \
  --namespace AWS/ApiGateway \
  --metric-name 5XXError \
  --dimensions Name=ApiName,Value=sales-api \
  --start-time $(date -u -d '10 minutes ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 60 \
  --statistics Sum

# Expected: < 5 errors/min

# 3. Smoke test
curl -X POST https://api.talma.com/api/orders \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"customerId":"test-123","total":100}'

# Expected: HTTP 201 Created
```

## Rollback

If resolution didn't work:

```bash
# Revert to last known good version
aws ecs update-service \
  --cluster production \
  --service sales-service \
  --task-definition sales-service:42  # ← Last stable version

# Scale up for extra capacity
aws ecs update-service \
  --cluster production \
  --service sales-service \
  --desired-count 6  # From 4 to 6

# Enable maintenance mode (if needed)
aws s3 cp maintenance.html s3://talma-sales-frontend/index.html
```

## Escalation

If problema persiste > 30 min:

1. **Page on-call engineer**: PagerDuty "Sales Service Down"
2. **Notify stakeholders**: Slack #incidents channel
3. **Create incident**: `POST /api/incidents` with severity P1
4. **Engage vendor support** (si es issue de AWS/third-party):
   - AWS Support case (Enterprise Support)
   - Twilio, Stripe, etc.

## Postmortem

After resolution:

1. **Document timeline** (detection → resolution)
2. **Root cause analysis** (5 Whys)
3. **Action items** (prevent recurrence)
4. **Update runbook** (mejorar troubleshooting)

Template: `/docs/postmortems/YYYY-MM-DD-service-outage.md`

---

## Runbooks Comunes

### 1. Service is Down (500 Errors)

**Symptoms**: High error rate, users can't access service

**Diagnosis**:

- Check ECS Task health
- Review recent deployments
- Check logs for errors
- Verify database connectivity

**Resolution**:

- Rollback bad deployment OR
- Restart tasks if transient OR
- Scale up if resource exhaustion OR
- Fix database connection

### 2. High Latency (Slow Response)

**Symptoms**: p99 latency > 2s (normal <500ms)

**Diagnosis**:

- Check database slow queries (RDS Performance Insights)
- Check external API calls (X-Ray tracing)
- Review Task CPU/memory usage
- Check cache hit rate (Redis)

**Resolution**:

- Optimize slow query (add index) OR
- Increase cache TTL OR
- Scale horizontally (more Tasks) OR
- Scale vertically (larger instance)

### 3. Database Connection Pool Exhausted

**Symptoms**: "Unable to obtain connection from pool"

**Diagnosis**:

```sql
-- Check active connections
SELECT count(*) FROM pg_stat_activity WHERE state = 'active';

-- Max connections
SHOW max_connections;  -- Default: 100
```

**Resolution**:

- Increase RDS max_connections parameter OR
- Increase app connection pool size OR
- Fix connection leaks (code review)

### 4. Kafka Consumer Lag High

**Symptoms**: Events processing delayed (lag > 1000 messages)

**Diagnosis**:

```bash
kafka-consumer-groups --bootstrap-server kafka:9092 \
  --describe --group sales-consumer

# Check lag per partition
```

**Resolution**:

- Scale consumer instances (parallel processing) OR
- Increase batch size (process more per poll) OR
- Optimize processing logic (reduce latency)

### 5. S3 Upload Failing

**Symptoms**: "403 Forbidden" or "NoSuchBucket"

**Diagnosis**:

```bash
# Check bucket exists
aws s3 ls s3://talma-sales-documents/

# Check IAM permissions
aws iam simulate-principal-policy \
  --policy-source-arn arn:aws:iam::123456789012:role/SalesServiceRole \
  --action-names s3:PutObject \
  --resource-arns arn:aws:s3:::talma-sales-documents/*
```

**Resolution**:

- Fix IAM policy (add s3:PutObject) OR
- Fix bucket name typo OR
- Check bucket policy (not blocking role)

---

## Runbook Governance

### Creation

Crear runbook cuando:

- Incident ocurre 2+ veces (patrón identificado)
- Resolución requiere > 30 min (complexity)
- Múltiples servicios involucrados (cross-team)

### Maintenance

- **Review quarterly**: Validate commands still work
- **Update after incidents**: Add lessons learned
- **Version control**: Git (like code)
- **Location**: `/docs/runbooks/` en repo

### Testing

```yaml
# Chaos Engineering: Test runbooks

Experiment:
  - Hypothesis: "Runbook allows recovery < 10 min"
  - Inject fault: Stop ECS Task
  - Execute runbook: Follow diagnosis → resolution steps
  - Measure: Time to recovery
  - Result: Update runbook if > 10 min
```

---

## Requisitos Técnicos

### MUST (Obligatorio)

- **MUST** crear runbook para cada servicio crítico (P1/P2)
- **MUST** incluir: symptoms, diagnosis, resolution, validation, rollback
- **MUST** usar comandos reproducibles (not "click here")
- **MUST** actualizar runbook después de cada incident
- **MUST** versionar runbooks en Git

### SHOULD (Fuertemente recomendado)

- **SHOULD** incluir scripts automatizados (diagnosis + resolution)
- **SHOULD** probar runbooks quarterly (chaos engineering)
- **SHOULD** tener runbook-per-alert (cada alarm tiene runbook)
- **SHOULD** incluir escalation path (cuando llamar on-call)

### MUST NOT (Prohibido)

- **MUST NOT** omitir validation steps (verify fix worked)
- **MUST NOT** usar screenshots (obsolete quickly)
- **MUST NOT** hardcodear secrets en runbooks (use Parameter Store)

---

## Referencias

- [Lineamiento: Documentación Técnica](../../lineamientos/desarrollo/03-documentacion-tecnica.md)
- [README Standards](./readme-standards.md)
- [Incident Response](../operabilidad/incident-response.md)
- [Observability](../operabilidad/observability.md)
- [Chaos Engineering](../operabilidad/chaos-engineering.md)
