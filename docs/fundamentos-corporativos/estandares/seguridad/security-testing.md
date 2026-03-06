---
id: security-testing
sidebar_position: 8
title: Security Testing
description: Estándares para threat modeling, penetration testing, vulnerability tracking y SLAs
tags:
  [
    seguridad,
    testing,
    threat-modeling,
    penetration-testing,
    vulnerabilidades,
    cvss,
  ]
---

# Security Testing

## Contexto

Este estándar consolida **4 conceptos relacionados** con pruebas y evaluación de seguridad. Define cómo identificar, analizar y remediar vulnerabilidades de seguridad.

**Conceptos incluidos:**

- **Threat Modeling** → Identificar amenazas en la fase de diseño
- **Penetration Testing** → Pruebas de intrusión por expertos
- **Vulnerability Tracking** → Registro centralizado de vulnerabilidades
- **Vulnerability SLA** → Tiempos de remediación según severidad

---

## Stack Tecnológico

| Componente           | Tecnología                     | Versión | Uso                                  |
| -------------------- | ------------------------------ | ------- | ------------------------------------ |
| **Threat Modeling**  | Microsoft Threat Modeling Tool | Latest  | Modelado de amenazas                 |
| **SAST**             | SonarQube                      | 9.9+    | Static Application Security Testing  |
| **DAST**             | OWASP ZAP                      | Latest  | Dynamic Application Security Testing |
| **Vulnerability DB** | Jira                           | Latest  | Tracking de vulnerabilidades         |
| **Pentest**          | Externo                        | N/A     | Firma certificada OSCP/CEH           |

---

## Threat Modeling

### ¿Qué es?

Análisis estructurado de amenazas potenciales durante la fase de diseño usando frameworks como STRIDE o PASTA.

**Propósito:** Identificar vulnerabilidades antes de implementar.

### Proceso con STRIDE

```markdown
# Threat Model: Order Service

## Assets

- Customer PII (names, emails, addresses)
- Payment information (encrypted credit cards)
- Order history

## Entry Points

- REST API (HTTPS)
- Kafka messages
- Database

## Threats (STRIDE)

### Spoofing

- **Amenaza**: Atacante falsifica identidad de usuario
- **Control**: JWT con firma RSA256, validar issuer
- **Estado**: ✅ Implementado

### Tampering

- **Amenaza**: Modificar datos en tránsito
- **Control**: TLS 1.3, mTLS entre servicios
- **Estado**: ✅ Implementado

### Repudiation

- **Amenaza**: Usuario niega realizar acción
- **Control**: Audit logs inmutables en Grafana Loki
- **Estado**: ✅ Implementado

### Information Disclosure

- **Amenaza**: Exponer PII en logs
- **Control**: Data masking automático en Serilog
- **Estado**: ✅ Implementado

### Denial of Service

- **Amenaza**: Flooding de requests
- **Control**: Rate limiting en Kong (100 req/min), AWS Shield
- **Estado**: ⚠️ Shield Standard, considerar Advanced

### Elevation of Privilege

- **Amenaza**: Usuario normal accede a funciones admin
- **Control**: RBAC/ABAC con permisos granulares
- **Estado**: ✅ Implementado
```

**MUST:**

- Threat model para cada nuevo servicio
- Revisión anual de threat models
- Actualizar tras cambios arquitectónicos

---

## Pruebas de Intrusión

### ¿Qué es?

Pruebas de intrusión por profesionales certificados para identificar vulnerabilidades explotables.

**Frecuencia:**

- **Producción**: Anual obligatorio
- **Cambios mayores**: Antes de lanzar features críticas

### Scope Document

```markdown
# Penetration Test Scope - Q1 2026

## In Scope

- api.talma.com (Order Service, Payment Service)
- Web application (app.talma.com)
- AWS infrastructure (VPC, Security Groups)

## Out of Scope

- Third-party services (Keycloak SaaS)
- Physical security

## Rules of Engagement

- Testing window: 2026-03-01 to 2026-03-15
- Business hours: No DoS testing 9AM-5PM
- Contact: security@talma.pe
- Emergency stop: +51 1 234 5678

## Testing Types

- [x] External network pentest
- [x] Web application pentest (OWASP Top 10)
- [x] API security testing
- [x] Social engineering (phishing simulation)
- [ ] Physical security (out of scope)

## Deliverables

- Executive summary
- Technical report (vulnerabilidades con CVSS)
- Remediation recommendations
- Retest after fixes
```

**MUST:**

- Usar firma certificada (OSCP, CEH, GPEN)
- Remediar Critical/High antes de go-live
- Retest tras remediation

---

## Seguimiento de Vulnerabilidades

### ¿Qué es?

Registro centralizado de vulnerabilidades con CVSS scoring, owner assignment y tracking de remediation.

### Jira Workflow

```yaml
Project: SECURITY

Issue Type: Vulnerability

Fields:
  - Title: "SQLi in /api/orders endpoint"
  - Severity: Critical / High / Medium / Low
  - CVSS Score: 9.1
  - Affected Component: Order Service v1.2.3
  - Discovered By: Pentest / SAST / DAST / Bug Bounty
  - Discovery Date: 2026-01-15
  - Owner: Engineering Team
  - SLA Due Date: Auto-calculated based on severity

States: 1. Open → Newly discovered
  2. Triaged → Severity confirmed, owner assigned
  3. In Progress → Remediation work started
  4. Fixed → Code deployed to prod
  5. Verified → Security team validated fix
  6. Closed → Accepted risk or fixed

Automations:
  - Alert Slack #security-alerts on Critical/High
  - Escalate to CTO if SLA breached
  - Auto-assign to component owner
```

### .NET: Security Issue Template

````csharp
// docs/security-issue-template.md
## Vulnerability Report

**Title**: SQL Injection in Order Search

**Severity**: 🔴 Critical (CVSS 9.1)

**Description**:
User input in `search` query parameter is concatenated directly into SQL without parameterization.

**Affected Endpoint**:
`GET /api/orders?search={user_input}`

**Proof of Concept**:
```http
GET /api/orders?search='; DROP TABLE orders; --
````

**Impact**:

- Unauthorized data access
- Data manipulation/deletion
- Potential RCE via xp_cmdshell

**Remediation**:

```csharp
// ❌ Vulnerable
var sql = $"SELECT * FROM orders WHERE customer_name LIKE '%{search}%'";
var orders = await _context.Database.SqlQueryRaw<Order>(sql).ToListAsync();

// ✅ Fixed
var orders = await _context.Orders
    .Where(o => EF.Functions.Like(o.CustomerName, $"%{search}%"))
    .ToListAsync();
```

**SLA**: 7 days (Critical)

**Owner**: @backend-team

````

---

## SLA de Remediación

### Tiempos de Remediación

| Severity | CVSS Score | SLA         | Approval for Exception   |
|----------|------------|-------------|---------------------------|
| Critical | 9.0 - 10.0 | **7 days**  | CTO                       |
| High     | 7.0 - 8.9  | **30 days** | Engineering Manager       |
| Medium   | 4.0 - 6.9  | **90 days** | Team Lead                 |
| Low      | 0.1 - 3.9  | **180 days**| Team Lead                 |

### Automated Monitoring

```csharp
// src/SecurityDashboard/VulnerabilitySlaMonitor.cs
public class VulnerabilitySlaMonitor : BackgroundService
{
    private readonly IVulnerabilityRepository _vulnRepo;
    private readonly INotificationService _notifications;

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        using var timer = new PeriodicTimer(TimeSpan.FromHours(4));

        while (await timer.WaitForNextTickAsync(stoppingToken))
        {
            await CheckSlaBreachesAsync();
        }
    }

    private async Task CheckSlaBreachesAsync()
    {
        var openVulns = await _vulnRepo.GetOpenVulnerabilitiesAsync();

        foreach (var vuln in openVulns)
        {
            var daysOpen = (DateTime.UtcNow - vuln.DiscoveredDate).Days;
            var sla = GetSlaForSeverity(vuln.Severity);

            if (daysOpen > sla)
            {
                // SLA breached
                await _notifications.SendSlackAlertAsync(
                    channel: "#security-alerts",
                    message: $"⚠️ SLA BREACH: {vuln.Title} ({vuln.Severity}) open for {daysOpen} days (SLA: {sla} days)",
                    mention: vuln.Owner
                );

                // Escalate to leadership
                if (vuln.Severity == "Critical" && daysOpen > sla + 3)
                {
                    await _notifications.SendEmailAsync(
                        to: "cto@talma.pe",
                        subject: $"URGENT: Critical vulnerability SLA breached",
                        body: $"Vulnerability '{vuln.Title}' has been open for {daysOpen} days."
                    );
                }
            }
            else if (daysOpen > sla * 0.8)
            {
                // Warning: 80% of SLA consumed
                await _notifications.SendSlackAlertAsync(
                    channel: "#engineering",
                    message: $"⏰ SLA Warning: {vuln.Title} ({vuln.Severity}) - {daysOpen}/{sla} days used",
                    mention: vuln.Owner
                );
            }
        }
    }

    private int GetSlaForSeverity(string severity) => severity switch
    {
        "Critical" => 7,
        "High" => 30,
        "Medium" => 90,
        "Low" => 180,
        _ => 90
    };
}
````

### Metrics

```promql
# Prometheus metrics

# Vulnerabilities abiertas por severity
vulnerabilities_open_total{severity="critical"}
vulnerabilities_open_total{severity="high"}

# Vulnerabilities con SLA breached
vulnerabilities_sla_breached_total{severity="critical"}

# Tiempo promedio para remediar
vulnerability_remediation_duration_days{severity="critical"}

# Dashboard en Grafana
```

---

## Requisitos Técnicos

### MUST

- **MUST** realizar threat modeling para nuevos servicios
- **MUST** realizar pentest anual en producción
- **MUST** remediar vulnerabilities Critical en 7 días
- **MUST** usar CVSS v3.1 para scoring
- **MUST** tracking centralizado en Jira

### SHOULD

- **SHOULD** integrar SAST en CI/CD (SonarQube)
- **SHOULD** realizar DAST mensualmente (OWASP ZAP)
- **SHOULD** bug bounty program para sistemas críticos

### MUST NOT

- **MUST NOT** ignorar vulnerabilities Critical/High sin approval
- **MUST NOT** lanzar a producción con Critical unresolved

---

## Referencias

- [OWASP Threat Modeling](https://owasp.org/www-community/Threat_Modeling)
- [STRIDE Framework](https://learn.microsoft.com/en-us/azure/security/develop/threat-modeling-tool-threats)
- [CVSS v3.1 Specification](https://www.first.org/cvss/v3.1/specification-document)
- [Security Scanning](./security-scanning.md)
- [Security Governance](./security-governance.md)
