---
id: security-architecture-review
sidebar_position: 5
title: Security Architecture Review
description: Revisión formal de seguridad antes de implementación de sistemas críticos
---

# Security Architecture Review

## Contexto

Este estándar establece **Security Architecture Review**: revisión formal de diseño de seguridad **antes de implementación**. Detectar vulnerabilidades en diseño es 100x más barato que en producción. Complementa el [lineamiento de Arquitectura Segura](../../lineamientos/seguridad/01-arquitectura-segura.md) mediante **validación experta proactiva**.

---

## Cuándo Realizar Review

```yaml
# ✅ Triggers para Security Architecture Review

MUST (Obligatorio): ✅ Nuevo sistema o servicio
  ✅ Cambios arquitectónicos significativos
  ✅ Integración con servicios externos
  ✅ Manejo de datos sensibles (PII, PCI)
  ✅ Exposición de API pública
  ✅ Multi-tenancy implementation
  ✅ Cambio en authentication/authorization
  ✅ Migración cloud

SHOULD (Recomendado): ✅ Features con input de usuarios
  ✅ Procesamiento de archivos subidos
  ✅ Cambios en políticas IAM
  ✅ Nuevos third-party integrations

Timing:
  - Design phase: ANTES de comenzar implementación
  - Pre-Production: ANTES de deploy a producción
  - Post-Incident: DESPUÉS de security breach

Frequency:
  - Quarterly: Para sistemas críticos (PCI scope)
  - Annually: Para sistemas no críticos
  - Ad-hoc: Cuando cambios significativos
```

## Review Process

```yaml
# ✅ Proceso de Security Architecture Review

Phase 1: Preparation (1-2 días)

  Architect prepara:
    - Architecture diagram (C4 Level 1-2)
    - Threat model (STRIDE)
    - Data flow diagrams
    - Trust boundaries
    - Security controls inventory
    - ADRs relevantes
    - Compliance requirements (PCI, GDPR, SOC 2)

  Security Team recibe:
    - Documentación 3 días antes de review
    - Acceso a repositorio (architecture docs)

Phase 2: Review Meeting (2-4 horas)

  Participants:
    ✅ Solution Architect (presenta)
    ✅ Security Architect (lidera review)
    ✅ Platform Engineer (infrastructure)
    ✅ Tech Lead del proyecto
    ⚫ DevSecOps Engineer (opcional)

  Agenda:
    1. Overview (15 min)
       - Business context
       - Technical scope
       - Compliance requirements

    2. Threat Model Review (45 min)
       - Assets críticos
       - Amenazas identificadas
       - Controles propuestos

    3. Architecture Deep Dive (60 min)
       - Data flow analysis
       - Trust boundaries
       - Authentication/authorization
       - Encryption strategy
       - Network topology

    4. Compliance Validation (30 min)
       - PCI-DSS checklist
       - GDPR requirements
       - SOC 2 controls

    5. Findings Discussion (30 min)
       - Security gaps
       - Recommendations
       - Risk assessment

Phase 3: Report (1 día)

  Security Team genera:
    - Findings report (critical/high/medium/low)
    - Recommendations prioritized
    - Remediation roadmap
    - Approval o Conditional Approval

  Distribute:
    - Architect (owner)
    - Tech Lead (implementation)
    - Engineering Manager (resources)
    - CISO (visibility)

Phase 4: Remediation (1-4 semanas)

  Engineering implementa:
    - Critical findings: Before go-live (blocker)
    - High findings: Within 2 weeks
    - Medium findings: Within 1 month
    - Low findings: Backlog (nice-to-have)

  Re-review:
    - Si critical findings: Re-review completo
    - Si solo medium/low: Document-based review

Phase 5: Approval

  Security Architect aprueba:
    ✅ All critical findings resolved
    ✅ High findings resolved o risk accepted
    ✅ Compensating controls documented

  Output:
    - Security sign-off (formal approval)
    - Production deployment permitido
```

## Review Checklist

```yaml
# ✅ Security Architecture Review Checklist

1. Authentication & Authorization: □ ¿SSO corporativo implementado? (Keycloak)
  □ ¿MFA obligatorio para usuarios?
  □ ¿Service-to-service auth (JWT, mTLS)?
  □ ¿RBAC o ABAC definido?
  □ ¿Session management seguro? (timeout, revocation)
  □ ¿Password policies compliant? (NIST 800-63B)

2. Data Protection:
  □ ¿Data classification definida? (public/internal/confidential/restricted)
  □ ¿Encryption at rest? (AWS KMS, RDS encryption)
  □ ¿Encryption in transit? (TLS 1.3)
  □ ¿PII masking en logs?
  □ ¿Secrets management? (AWS Secrets Manager, NO env vars)
  □ ¿Backup encryption?

3. Network Security: □ ¿Backend en private subnets?
  □ ¿Security groups restrictive? (least privilege)
  □ ¿WAF implementado? (OWASP rules)
  □ ¿DDoS protection? (CloudFront, Shield)
  □ ¿VPN o PrivateLink para admin access?
  □ ¿No databases públicas?

4. Application Security: □ ¿Input validation? (FluentValidation, JSON Schema)
  □ ¿Output encoding? (XSS prevention)
  □ ¿Parameterized queries? (SQL injection prevention)
  □ ¿CSRF protection? (tokens)
  □ ¿Rate limiting? (DoS prevention)
  □ ¿File upload restrictions? (type, size, virus scan)

5. Infrastructure Security: □ ¿Infrastructure as Code? (Terraform, no manual)
  □ ¿IaC scanning? (Checkov, tfsec)
  □ ¿Container scanning? (Trivy)
  □ ¿Least privilege IAM roles?
  □ ¿No hardcoded secrets?
  □ ¿Immutable infrastructure? (no SSH, use deployments)

6. Monitoring & Auditing: □ ¿CloudTrail habilitado? (all regions)
  □ ¿Security alerts configuradas? (GuardDuty, SecurityHub)
  □ ¿Audit logs para accesos? (who, what, when)
  □ ¿Log retention? (>= 1 año para compliance)
  □ ¿SIEM integration? (opcional)
  □ ¿Incident response runbook?

7. Compliance: □ ¿PCI-DSS (si aplica)? (SAQ, quarterly scans)
  □ ¿GDPR? (consent, right to deletion, DPO)
  □ ¿SOC 2? (access controls, change management)
  □ ¿ISO 27001? (ISMS policies)
  □ ¿LGPD? (Brazilian data protection)

8. Third-Party Integrations: □ ¿Vendor security assessment?
  □ ¿Data sharing agreement?
  □ ¿API key rotation policy?
  □ ¿Webhook signature validation?
  □ ¿Rate limiting partner APIs?

9. Disaster Recovery: □ ¿Backup strategy? (RPO, RTO defined)
  □ ¿Cross-region replication?
  □ ¿Backup testing? (restore drill quarterly)
  □ ¿Failover runbook?

10. DevSecOps: □ ¿SAST en CI/CD? (SonarQube, block high/critical)
  □ ¿Dependency scanning? (Snyk, Dependabot)
  □ ¿Container scanning? (pre-deployment)
  □ ¿Security testing? (DAST en staging)
  □ ¿Secret scanning? (git pre-commit hooks)
```

## Example: Sales Service Review

```yaml
# ✅ Security Architecture Review (Sales Service - 2024)

Project: Sales Service v2.0
Date: 2024-02-18
Reviewer: Security Architect (Juan Pérez)
Architect: Solution Architect (María García)

Overview:
  - Scope: Nuevo Sales Service con multi-tenancy
  - Data: Orders (confidential), Customers PII (restricted)
  - Compliance: PCI-DSS Level 1, GDPR
  - Deployment: AWS ECS Fargate, PostgreSQL RDS

Findings:

  CRITICAL (Blockers - 2):

    1. Database Encryption Missing
       - Finding: RDS instance sin encryption at rest
       - Risk: Data breach expone PII sin cifrar
       - Recommendation: Habilitar KMS encryption (can't enable after creation)
       - Status: MUST FIX before production
       - Effort: 1 day (recreate instance with encryption)

    2. No MFA Enforcement
       - Finding: Keycloak permite login sin MFA
       - Risk: Credential stuffing compromete cuentas
       - Recommendation: Enforce MFA policy (TOTP required)
       - Status: MUST FIX before production
       - Effort: 2 days (configure Keycloak, user communication)

  HIGH (2 weeks - 3):

    3. Overly Permissive IAM Role
       - Finding: ECS task role con "s3:*" permission
       - Risk: Lateral movement si task compromised
       - Recommendation: Scope to specific buckets (s3:GetObject on sales-* only)
       - Status: Fix within 2 weeks
       - Effort: 1 day

    4. No Rate Limiting
       - Finding: API sin rate limiting
       - Risk: DDoS, credential brute-force
       - Recommendation: Kong rate-limiting (100 req/min per user)
       - Status: Fix within 2 weeks
       - Effort: 2 days

    5. Logs con PII
       - Finding: CloudWatch logs incluyen customer emails sin mask
       - Risk: GDPR violation si logs leak
       - Recommendation: Mask PII en logs (email → e***@domain.com)
       - Status: Fix within 2 weeks
       - Effort: 3 days (update logging middleware)

  MEDIUM (1 month - 2):

    6. No Container Scanning
       - Finding: Docker images no escaneados
       - Risk: Vulnerabilities en base image
       - Recommendation: Trivy scan en CI/CD (block high/critical)
       - Status: Fix within 1 month
       - Effort: 1 week (integrate, establish baseline)

    7. Security Groups Too Broad
       - Finding: Backend SG permite 0.0.0.0/0 → 443
       - Risk: Exposure innecesaria
       - Recommendation: Solo ALB SG → Backend:8080
       - Status: Fix within 1 month
       - Effort: 2 days (test, apply)

Approval Status: CONDITIONAL
  - Blockers: 2 critical findings MUST be resolved
  - Re-review: Document-based review after critical fixes
  - Target: 1 week para resolution

Action Plan:
  Week 1:
    - Recreate RDS with encryption (María - 1 día)
    - Enable MFA enforcement (Juan - 2 días)
    - Re-review findings 1 y 2

  Week 2:
    - Fix IAM role permissions (Carlos - 1 día)
    - Implement rate limiting (Ana - 2 días)
    - Mask PII en logs (Pedro - 3 días)

  Week 3-4:
    - Integrate Trivy scanning (DevOps - 1 semana)
    - Tighten security groups (Carlos - 2 días)

Follow-up:
  - 2024-03-01: Document-based re-review
  - 2024-03-15: Production deployment (if approved)
  - 2024-09-01: Post-deployment audit (6 meses)
```

## Documentation Template

```markdown
# Security Architecture Review

## Project Information

- **Project Name**: [Sales Service v2.0]
- **Review Date**: [2024-02-18]
- **Reviewer**: [Security Architect Name]
- **Architect**: [Solution Architect Name]
- **Participants**: [List attendees]

## Scope

- **Business Context**: [Why this system exists]
- **Technical Scope**: [Components in scope]
- **Data Classification**: [What data, classification level]
- **Compliance**: [PCI, GDPR, SOC 2, etc.]

## Architecture Overview

- **Diagram**: [Link to C4 diagrams]
- **Components**: [List services, databases, integrations]
- **Trust Boundaries**: [Identified boundaries]
- **Threat Model**: [Link to threat model document]

## Security Controls

- **Authentication**: [Method, MFA status]
- **Authorization**: [RBAC, policies]
- **Encryption**: [At rest, in transit]
- **Network**: [Topology, security groups]
- **Monitoring**: [Logs, alerts, auditing]

## Findings Summary

- **Critical**: [Count] (blockers)
- **High**: [Count] (2 weeks)
- **Medium**: [Count] (1 month)
- **Low**: [Count] (backlog)

## Detailed Findings

### CRITICAL-001: [Title]

- **Description**: [What is vulnerable]
- **Risk**: [Impact if exploited]
- **Recommendation**: [How to fix]
- **Effort**: [Time estimate]
- **Owner**: [Person responsible]
- **Due Date**: [Before production]

[Repeat for each finding]

## Approval Decision

- **Status**: [Approved / Conditional / Rejected]
- **Blockers**: [Critical findings to resolve]
- **Next Steps**: [Action plan]

## Sign-off

- **Security Architect**: [Signature, Date]
- **Solution Architect**: [Signature, Date]
- **Engineering Manager**: [Signature, Date]
```

---

## Requisitos Técnicos

### MUST (Obligatorio)

- **MUST** realizar Security Architecture Review para nuevos sistemas
- **MUST** resolver critical findings ANTES de producción
- **MUST** documentar findings y remediation plan
- **MUST** obtener Security sign-off formal
- **MUST** incluir Security Architect en review
- **MUST** re-review si cambios arquitectónicos post-approval

### SHOULD (Fuertemente recomendado)

- **SHOULD** usar checklist estandarizado
- **SHOULD** preparar documentación 3 días antes de review
- **SHOULD** realizar post-deployment audit (6 meses)
- **SHOULD** tracking de findings en JIRA/Backlog

### MUST NOT (Prohibido)

- **MUST NOT** deploy a producción sin Security sign-off
- **MUST NOT** ignorar critical findings
- **MUST NOT** realizar review solo con documentos (meeting requerido)
- **MUST NOT** auto-approve (architect ≠ reviewer)

---

## Referencias

- [Lineamiento: Arquitectura Segura](../../lineamientos/seguridad/01-arquitectura-segura.md)
- [Security by Design](./security-by-design.md)
- [Threat Modeling](./threat-modeling.md)
- [Architecture Review (General)](../../estandares/arquitectura/architecture-review.md)
