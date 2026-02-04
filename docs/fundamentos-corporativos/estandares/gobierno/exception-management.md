---
id: exception-management
sidebar_position: 4
title: Exception Management
description: Estándar para gestión formal de excepciones a políticas y estándares arquitectónicos con aprobación, tracking y time-boxing
---

# Estándar Técnico — Exception Management

---

## 1. Propósito

Establecer un proceso formal para solicitar, evaluar, aprobar y rastrear excepciones a estándares técnicos y políticas arquitectónicas, balanceando flexibilidad operacional con governance y gestión de riesgos.

---

## 2. Alcance

**Aplica a:**

- Excepciones a estándares técnicos corporativos
- Uso de tecnologías no aprobadas
- Violaciones de políticas de seguridad
- Incumplimiento temporal de compliance
- Decisiones arquitectónicas fuera de estándares
- Workarounds temporales en producción

**No aplica a:**

- Configuraciones estándar permitidas
- Tecnologías ya aprobadas en el stack
- Decisiones locales dentro de estándares
- Emergencias operacionales (incident response)
- Experimentos en entornos no productivos

---

## 3. Tecnologías Aprobadas

| Componente             | Tecnología      | Uso Principal               | Observaciones                  |
| ---------------------- | --------------- | --------------------------- | ------------------------------ |
| **Exception Tracking** | Jira            | Workflow de excepciones     | Custom issue type: Exception   |
| **Exception Tracking** | ServiceNow      | ITSM integration            | Change Management module       |
| **Documentation**      | Confluence      | Exception registry          | Con plantillas estandarizadas  |
| **Approval Workflow**  | Jira/ServiceNow | Multi-step approvals        | Configurable por severidad     |
| **Risk Assessment**    | Risk Register   | Risk matrix evaluation      | Likelihood x Impact            |
| **Audit Trail**        | Audit logs      | Immutable exception history | CloudTrail, Azure Activity Log |
| **Notifications**      | Email/Slack     | Alertas de expiración       | Automated reminders            |
| **Metrics Dashboard**  | Grafana         | Exception metrics           | Por tipo, estado, antigüedad   |

> El uso de tecnologías no listadas requiere aprobación de Arquitectura.

---

## 4. Requisitos Obligatorios 🔴

### Proceso de Solicitud

- [ ] **Plantilla estandarizada:** usar template corporativo
- [ ] **Justificación de negocio:** clara y documentada
- [ ] **Análisis de riesgo:** likelihood + impact
- [ ] **Compensating controls:** medidas de mitigación
- [ ] **Timeline:** fecha de inicio y fin obligatorias
- [ ] **Alternativas consideradas:** mínimo 2 opciones

### Clasificación de Severidad

- [ ] **CRITICAL:** afecta seguridad/compliance/producción
- [ ] **HIGH:** violación de estándares core
- [ ] **MEDIUM:** violación de mejores prácticas
- [ ] **LOW:** desviación menor temporal

### Niveles de Aprobación

- [ ] **LOW:** Tech Lead aprueba
- [ ] **MEDIUM:** Domain Architect aprueba
- [ ] **HIGH:** Chief Architect + Security Lead
- [ ] **CRITICAL:** Chief Architect + Security + Compliance + CTO

### Duración Máxima

- [ ] **CRITICAL:** máximo 30 días
- [ ] **HIGH:** máximo 90 días
- [ ] **MEDIUM:** máximo 180 días
- [ ] **LOW:** máximo 1 año
- [ ] **Renovaciones:** máximo 1 renovación, requiere nueva aprobación

### Monitoreo

- [ ] **Tracking activo:** estado visible en dashboard
- [ ] **Alertas de expiración:** 30/15/7 días antes
- [ ] **Review periódica:** mensual para CRITICAL/HIGH
- [ ] **Cierre automático:** al expirar sin renovación
- [ ] **Métricas:** cantidad, tipo, tiempo promedio de resolución

### Documentación

- [ ] **Exception ID:** único y trazable
- [ ] **Affected systems:** lista completa
- [ ] **Risk assessment:** matriz de riesgo
- [ ] **Compensating controls:** implementados y verificados
- [ ] **Closure plan:** pasos para remediar
- [ ] **Audit trail:** todas las aprobaciones/cambios

---

## 5. Prohibiciones

- ❌ Excepciones sin aprobación formal
- ❌ Excepciones permanentes (sin fecha de fin)
- ❌ Falta de análisis de riesgo
- ❌ Ausencia de compensating controls
- ❌ Excepciones renovadas indefinidamente
- ❌ No documentar justificación
- ❌ Aprobar excepciones fuera del nivel de autoridad

---

## 6. Configuración Mínima

### Jira - Exception Workflow

```yaml
# Exception Request Workflow
issueType: Exception
workflow:
  states:
    - DRAFT:
        description: "Being prepared by requester"
        transitions: [SUBMIT_FOR_REVIEW]

    - PENDING_REVIEW:
        description: "Awaiting initial review"
        transitions: [UNDER_RISK_ASSESSMENT, REJECTED]

    - UNDER_RISK_ASSESSMENT:
        description: "Security/Risk team evaluating"
        transitions: [PENDING_APPROVAL, REJECTED, REQUEST_MORE_INFO]

    - REQUEST_MORE_INFO:
        description: "Additional information needed"
        transitions: [PENDING_REVIEW]

    - PENDING_APPROVAL:
        description: "Awaiting approver decision"
        transitions: [APPROVED, APPROVED_WITH_CONDITIONS, REJECTED]

    - APPROVED:
        description: "Exception granted"
        transitions: [ACTIVE, CANCELLED]

    - APPROVED_WITH_CONDITIONS:
        description: "Approved pending conditions"
        transitions: [ACTIVE, REJECTED]

    - ACTIVE:
        description: "Exception in effect"
        transitions: [REMEDIATED, EXPIRED, CANCELLED, RENEWAL_REQUESTED]

    - RENEWAL_REQUESTED:
        description: "Extension requested"
        transitions: [APPROVED, REJECTED, EXPIRED]

    - REMEDIATED:
        description: "Issue fixed, exception no longer needed"
        final: true

    - EXPIRED:
        description: "Exception time limit reached"
        final: true

    - CANCELLED:
        description: "Exception cancelled by requester"
        final: true

    - REJECTED:
        description: "Exception denied"
        final: true

# Custom fields
customFields:
  - exception_id: text (auto-generated: EXC-YYYY-NNN)
  - severity: select [CRITICAL, HIGH, MEDIUM, LOW]
  - affected_systems: multi-text
  - policy_violated: text
  - business_justification: textarea
  - risk_likelihood: select [Very Low, Low, Medium, High, Very High]
  - risk_impact: select [Very Low, Low, Medium, High, Very High]
  - risk_score: calculated (likelihood x impact)
  - compensating_controls: textarea
  - start_date: date
  - expiration_date: date
  - approvers: multi-user
  - approval_date: datetime
  - closure_plan: textarea
  - renewal_count: number
```

### Exception Request Template

```markdown
---
id: EXC-2024-XXX
status: DRAFT
severity: [CRITICAL|HIGH|MEDIUM|LOW]
requested_by: [Name]
requested_date: YYYY-MM-DD
---

# Exception Request — [Short Title]

## 1. Executive Summary

[1-2 paragraph summary of what exception is requested and why]

---

## 2. Policy/Standard Being Violated

**Policy ID:** [e.g., SEC-NET-001]
**Policy Name:** [e.g., "All network traffic must be encrypted with TLS 1.2+"]
**Policy Owner:** [Chief Architect / Security Lead]
**Severity of Violation:** [CRITICAL|HIGH|MEDIUM|LOW]

**Full Policy Text:**

> [Quote the specific policy being violated]

---

## 3. Affected Systems

| System Name       | Environment | Impact              | Criticality |
| ----------------- | ----------- | ------------------- | ----------- |
| legacy-api-v1     | Production  | Encryption disabled | HIGH        |
| internal-admin-ui | Production  | No TLS              | MEDIUM      |

**Total Systems Affected:** 2
**Affected Users:** ~500 internal users

---

## 4. Business Justification

**Problem:**
Legacy API (deployed 2015) doesn't support TLS 1.2. Modern client libraries fail to connect.

**Business Impact if Not Approved:**

- Critical internal tool (admin panel) becomes unusable
- 500+ customer service reps cannot process orders
- Estimated revenue impact: $50k/day

**Why Standard Practice Isn't Feasible:**

- API codebase is .NET Framework 2.0, TLS 1.2 not supported
- Full rewrite to .NET 8 planned for Q2 2024
- Interim solution needed to maintain operations

---

## 5. Alternatives Considered

### Option 1: Immediate Full Rewrite

- **Pros:** Complies with standard, modern codebase
- **Cons:** 6 months timeline, $200k cost, business disruption
- **Rejected Because:** Timeline too long, business cannot wait

### Option 2: TLS Proxy/Termination

- **Pros:** Adds TLS without changing legacy code
- **Cons:** Additional infrastructure complexity, performance overhead
- **Rejected Because:** Complexity doesn't justify 4-month temporary need

### Option 3: Exception with Compensating Controls (Recommended)

- **Pros:** Balances security with business continuity
- **Cons:** Temporary risk increase
- **Selected Because:** Lowest risk for short-term need

---

## 6. Risk Assessment

### Likelihood & Impact Matrix

| Threat                   | Likelihood | Impact | Risk Score |
| ------------------------ | ---------- | ------ | ---------- |
| Man-in-the-middle attack | MEDIUM     | HIGH   | **HIGH**   |
| Data interception        | MEDIUM     | HIGH   | **HIGH**   |
| Compliance audit failure | LOW        | MEDIUM | **MEDIUM** |
| Reputational damage      | LOW        | HIGH   | **MEDIUM** |

**Overall Risk Level:** **HIGH**

### Risk Justification

- API operates on internal network only (not internet-facing)
- Network segmentation limits exposure
- Temporary 4-month exception until migration complete

---

## 7. Compensating Controls

✅ **Implemented:**

1. **Network Segmentation:**
   - API in isolated VLAN
   - Firewall rules restrict access to internal IPs only
   - No public internet access

2. **Application-Level Encryption:**
   - Sensitive fields (PII, payment data) encrypted at application layer
   - AES-256 encryption for data at rest

3. **Access Controls:**
   - API requires JWT token authentication
   - Token expiration: 15 minutes
   - MFA required for token issuance

4. **Monitoring:**
   - CloudWatch logs for all API requests
   - Anomaly detection for unusual traffic patterns
   - Security team alerted on suspicious activity

5. **Audit Logging:**
   - All API calls logged to immutable audit trail
   - Logs retained 2 years

6. **Vulnerability Scanning:**
   - Weekly automated scans (Qualys)
   - Manual penetration test scheduled for next month

---

## 8. Timeline & Closure Plan

**Exception Start Date:** 2024-03-01
**Exception End Date:** 2024-06-30 (4 months)

**Remediation Plan:**

| Phase | Activity                 | Owner     | Deadline   |
| ----- | ------------------------ | --------- | ---------- |
| 1     | Design new .NET 8 API    | @john-dev | 2024-03-15 |
| 2     | Develop & test new API   | @john-dev | 2024-05-01 |
| 3     | User acceptance testing  | @qa-team  | 2024-05-15 |
| 4     | Deploy to production     | @sre-team | 2024-06-15 |
| 5     | Migrate users to new API | @product  | 2024-06-30 |
| 6     | Decommission legacy API  | @sre-team | 2024-07-07 |

**Checkpoints:**

- Monthly status update to Chief Architect
- Go/No-Go review at each phase
- Exception auto-expires if migration delayed beyond 2024-06-30

---

## 9. Approval

**Approvers Required (Severity: HIGH):**

- [ ] **Chief Architect:** **********\_********** Date: **\_\_\_**
- [ ] **Security Lead:** **********\_\_\_\_********** Date: **\_\_\_**

**Conditions of Approval:**

1. Weekly progress updates on migration
2. Penetration test results must show no CRITICAL vulnerabilities
3. Automatic expiration if deadline missed (no auto-renewal)

---

## 10. Monitoring & Reporting

**KPIs:**

- API usage (should decline as users migrate)
- Security incidents (target: 0)
- Migration progress (% users migrated)

**Reporting:**

- Weekly dashboard published to #security-exceptions Slack channel
- Monthly review meeting with approvers

---

## 11. Attachments

- [Network Diagram](link)
- [Penetration Test Results](link)
- [Migration Project Plan](link)
- [Risk Register Entry](link)
```

### Auto-Expiration Script

```python
# scripts/expire_exceptions.py
import os
from datetime import datetime, timedelta
from jira import JIRA

JIRA_URL = os.getenv('JIRA_URL')
JIRA_USER = os.getenv('JIRA_USER')
JIRA_TOKEN = os.getenv('JIRA_TOKEN')
SLACK_WEBHOOK = os.getenv('SLACK_WEBHOOK')

jira = JIRA(server=JIRA_URL, basic_auth=(JIRA_USER, JIRA_TOKEN))

def expire_exceptions():
    """Expire exceptions that have reached their end date."""
    today = datetime.now().date()

    # Query active exceptions
    jql = 'project = "Architecture Governance" AND issuetype = Exception AND status = ACTIVE'
    exceptions = jira.search_issues(jql, maxResults=False)

    expired_count = 0
    expiring_soon = []

    for exc in exceptions:
        exp_date_str = exc.fields.customfield_10050  # expiration_date
        if not exp_date_str:
            continue

        exp_date = datetime.strptime(exp_date_str, '%Y-%m-%d').date()
        days_until_expiration = (exp_date - today).days

        # Expire if past due
        if days_until_expiration < 0:
            jira.transition_issue(exc, 'EXPIRED')
            notify_slack(f"❌ Exception {exc.key} has EXPIRED: {exc.fields.summary}")
            expired_count += 1

        # Alert if expiring soon
        elif days_until_expiration in [30, 15, 7, 3, 1]:
            expiring_soon.append({
                'key': exc.key,
                'summary': exc.fields.summary,
                'days': days_until_expiration,
                'owner': exc.fields.assignee.displayName
            })

    # Send expiring soon alerts
    if expiring_soon:
        message = "⚠️ *Exceptions Expiring Soon:*\n\n"
        for exc in expiring_soon:
            message += f"• *{exc['key']}:* {exc['summary']}\n"
            message += f"  Owner: {exc['owner']}, Expires in {exc['days']} days\n\n"
        notify_slack(message)

    print(f"Expired {expired_count} exceptions")
    print(f"Found {len(expiring_soon)} exceptions expiring soon")

def notify_slack(message):
    """Send notification to Slack."""
    import requests
    requests.post(SLACK_WEBHOOK, json={"text": message})

if __name__ == '__main__':
    expire_exceptions()
```

---

## 7. Ejemplos

### Exception Dashboard (Grafana)

```promql
# Total active exceptions
count(jira_exception{status="ACTIVE"})

# Exceptions by severity
count(jira_exception{status="ACTIVE"}) by (severity)

# Average time to remediation
avg(jira_exception_duration_days{status="REMEDIATED"})

# Expiring in next 30 days
count(jira_exception{status="ACTIVE", days_until_expiration < 30})

# Exceptions past SLA for closure
count(jira_exception{status="ACTIVE", days_active > max_duration_days})
```

### Risk Matrix Calculation

```python
# Risk scoring algorithm
LIKELIHOOD = {
    'Very Low': 1,
    'Low': 2,
    'Medium': 3,
    'High': 4,
    'Very High': 5
}

IMPACT = {
    'Very Low': 1,
    'Low': 2,
    'Medium': 3,
    'High': 4,
    'Very High': 5
}

def calculate_risk_score(likelihood: str, impact: str) -> tuple:
    """
    Calculate risk score and severity.

    Returns:
        (score, severity) where severity is CRITICAL/HIGH/MEDIUM/LOW
    """
    score = LIKELIHOOD[likelihood] * IMPACT[impact]

    if score >= 20:
        return (score, 'CRITICAL')
    elif score >= 12:
        return (score, 'HIGH')
    elif score >= 6:
        return (score, 'MEDIUM')
    else:
        return (score, 'LOW')

# Example usage
score, severity = calculate_risk_score('High', 'Very High')
print(f"Risk Score: {score}, Severity: {severity}")
# Output: Risk Score: 20, Severity: CRITICAL
```

---

## 8. Validación y Auditoría

### Checklist

- [ ] Todas las excepciones con template completo
- [ ] Aprobación formal por nivel de autoridad correcto
- [ ] Análisis de riesgo documentado
- [ ] Compensating controls implementados y verificados
- [ ] Fecha de expiración definida (no excepciones permanentes)
- [ ] Tracking activo en dashboard
- [ ] Alertas de expiración configuradas

### Métricas

```promql
# Exception lifecycle metrics
count(jira_exception) by (status)

# Time to approval
histogram_quantile(0.95, jira_exception_approval_duration_days)

# Remediation rate
count(jira_exception{status="REMEDIATED"}) / count(jira_exception) * 100

# Exceptions by team/domain
count(jira_exception{status="ACTIVE"}) by (team)

# Renewal rate (should be low)
count(jira_exception{renewal_count > 0}) / count(jira_exception) * 100
```

### Dashboard SLIs

| Métrica                     | SLI      | Alertar si |
| --------------------------- | -------- | ---------- |
| Active exceptions (total)   | < 20     | > 30       |
| CRITICAL exceptions active  | < 2      | > 3        |
| Exceptions past expiration  | 0        | > 0        |
| Time to approval (CRITICAL) | < 24h    | > 48h      |
| Time to approval (HIGH)     | < 3 días | > 7 días   |
| Remediation rate            | > 70%    | < 50%      |
| Renewal rate                | < 10%    | > 25%      |

---

## 9. Referencias

**Frameworks:**

- [TOGAF - Exception Handling Process](https://pubs.opengroup.org/architecture/togaf9-doc/arch/)
- [COBIT - Governance Exemptions](https://www.isaca.org/resources/cobit)
- [ISO 27001 - Risk Treatment](https://www.iso.org/standard/27001)

**Risk Management:**

- [NIST Risk Management Framework](https://csrc.nist.gov/projects/risk-management)
- [FAIR Risk Framework](https://www.fairinstitute.org/)

**Buenas Prácticas:**

- ITIL Change Management - Exception handling
- AWS Well-Architected - Operational Excellence (exception management)
- "Managing Risk in Organizations" - Howard Rothman
