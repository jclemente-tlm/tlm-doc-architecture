---
id: security-by-design
sidebar_position: 1
title: Security by Design
description: Integrar seguridad desde el diseño arquitectónico, no como remediación posterior
---

# Security by Design

## Contexto

Este estándar establece **Security by Design**: integrar seguridad desde las **primeras decisiones arquitectónicas**, no como parches posteriores. Vulnerabilidades en diseño se multiplican en cada capa. Complementa el [lineamiento de Arquitectura Segura](../../lineamientos/seguridad/01-arquitectura-segura.md) asegurando seguridad **inherente al sistema**.

---

## Principios Fundamentales

```yaml
# ✅ Security by Design = Seguridad desde inicio

Shift Left Security:
  ❌ Tradicional: Seguridad al final (pentest pre-producción)
  ✅ Moderno: Seguridad desde diseño (threat model, architecture review)

  Beneficio: Costo fix 100x menor en diseño que en producción

Security Requirements (non-functional):
  - Authentication: ¿Quién es el usuario?
  - Authorization: ¿Qué puede hacer?
  - Confidentiality: ¿Datos cifrados en tránsito y reposo?
  - Integrity: ¿Datos no pueden ser alterados?
  - Availability: ¿Sistema resistente a DoS?
  - Auditability: ¿Trazabilidad completa de acciones?
  - Privacy: ¿Cumple GDPR, LGPD, regulaciones?

Threat-Driven Design:
  1. Identificar assets críticos (datos clientes, transacciones)
  2. Modelar amenazas (STRIDE)
  3. Diseñar controles (authentication, encryption, rate limiting)
  4. Validar efectividad (security testing)

  Output: Arquitectura que anticipa y mitiga amenazas

Security Patterns:
  ✅ Gateway Offloading (authentication en API Gateway)
  ✅ Sidecar (mTLS, logging en proxy sidecar)
  ✅ Strangler Fig (migrar legacy sin romper seguridad)
  ✅ Bulkhead (aislar componentes)
  ✅ Circuit Breaker (prevenir cascading failures)
```

## Proceso de Diseño Seguro

```yaml
# ✅ Integrar seguridad en ciclo de arquitectura

Phase 1: Requirements
  - Identificar requisitos de seguridad/compliance
  - OWASP Top 10, PCI-DSS, ISO 27001, SOC 2
  - Data classification (public, internal, confidential, restricted)

  Example (Sales Service):
    - ✅ PCI-DSS Level 1 (procesa tarjetas)
    - ✅ GDPR (datos personales clientes EU)
    - ✅ Data: Orders (confidential), Customers (restricted)

Phase 2: Threat Modeling
  - Usar framework STRIDE
  - Identificar attack vectors
  - Priorizar por impacto y probabilidad

  Tool: Microsoft Threat Modeling Tool
  Output: Lista amenazas + controles mitigación

  Example (Sales Service):
    Threat: SQL Injection en order queries
      → Control: Parameterized queries, input validation
    Threat: Credential stuffing en login
      → Control: MFA, rate limiting, CAPTCHA

Phase 3: Architecture Design
  - Incorporar controles identificados
  - Definir trust boundaries
  - Aplicar defense in depth

  Example:
    Layer 1 (Perimeter): WAF, DDoS protection
    Layer 2 (Network): Security groups, private subnets
    Layer 3 (App): JWT authentication, input validation
    Layer 4 (Data): Encryption at rest, TDE

Phase 4: Secure Coding
  - Seguir OWASP guidelines
  - SAST en CI/CD (SonarQube)
  - Code review con security checklist

  Checklist:
    ✅ No secrets en código (AWS Secrets Manager)
    ✅ Input validation (FluentValidation)
    ✅ Output encoding (prevenir XSS)
    ✅ Safe deserialization (no Type: auto)

Phase 5: Security Testing
  - SAST: Análisis estático (SonarQube, Semgrep)
  - DAST: Análisis dinámico (OWASP ZAP)
  - SCA: Software Composition Analysis (Snyk, Dependabot)
  - Penetration testing (anual)

  CI/CD Gate: Block deploy si critical/high vulnerabilities

Phase 6: Runtime Protection
  - WAF rules (AWS WAF)
  - Runtime monitoring (GuardDuty, CloudTrail)
  - Security alerts (anomalías, accesos sospechosos)
```

## Architecture Patterns

```yaml
# ✅ Patrones arquitectónicos seguros

1. API Gateway Pattern (Security Offloading):

   ┌─────────────────────────────────────────┐
   │ Kong API Gateway                        │
   │ - JWT validation                        │
   │ - Rate limiting (100 req/min per user)  │
   │ - OAuth 2.0 flows                       │
   │ - IP allowlist/blocklist                │
   │ - Request/response logging              │
   └─────────────────────────────────────────┘
              │
              ├──────────► Sales Service (no auth logic)
              ├──────────► Billing Service
              └──────────► Fulfillment Service

   Benefit: Servicios no implementan auth (centralized)

2. Zero Trust Architecture:

   Every component verifies explicitly:

   Client → API Gateway:
     - OAuth 2.0 token (Keycloak)
     - MFA enforced

   API Gateway → Backend Service:
     - mTLS (mutual TLS)
     - Service-to-service JWT

   Backend → Database:
     - IAM authentication (no passwords)
     - Encrypted connection (TLS 1.3)

   Backend → S3:
     - Pre-signed URLs (limited time)
     - Bucket policies (least privilege)

   Result: No implicit trust anywhere

3. Defense in Depth (Layers):

   Internet
     │
     ├─ Layer 1: AWS WAF (block OWASP Top 10)
     │
     ├─ Layer 2: CloudFront (DDoS protection)
     │
     ├─ Layer 3: ALB + Security Groups
     │        (only HTTPS 443, private subnet targets)
     │
     ├─ Layer 4: ECS Tasks (private subnet)
     │        Kong Gateway: JWT validation
     │
     ├─ Layer 5: Backend Services
     │        Input validation, business rules
     │
     └─ Layer 6: PostgreSQL RDS
              Encryption at rest (KMS)
              TLS connections only
              Private subnet (no internet)

   Breach at Layer 3 → Still protected by 4, 5, 6

4. Secure by Default Configuration:

   ❌ Mal (Insecure defaults):
     - Debug mode habilitado en producción
     - Default passwords (admin/admin)
     - Ports innecesarios abiertos (22 SSH public)
     - CORS allow all origins (*)
     - Verbose error messages (stack traces a usuarios)

   ✅ Bien (Secure defaults):
     - Debug mode OFF en producción
     - Force password change on first login
     - Only necessary ports (443 HTTPS)
     - CORS específico (https://app.talma.com)
     - Generic error messages (log details internamente)
```

## Real Example: Sales Service Design

```yaml
# ✅ Security by Design aplicado (Talma Sales Service)

Asset Classification:
  Critical:
    - Customer PII (nombres, emails, direcciones)
    - Payment information (last 4 digits card)
    - Order details (productos, precios)

  Data Classification:
    - PII: Restricted (encryption, access logs)
    - Orders: Confidential (authentication required)
    - Products: Internal (no authentication)

Threat Model (STRIDE):
  Spoofing:
    Threat: Atacante finge ser usuario legítimo
    Control: Keycloak SSO + MFA obligatorio

  Tampering:
    Threat: Modificar datos de orden en tránsito
    Control: HTTPS (TLS 1.3), JWT signatures

  Repudiation:
    Threat: Usuario niega haber creado orden
    Control: CloudTrail audit logs, orden firmada digitalmente

  Information Disclosure:
    Threat: Exposición de PII
    Control: Encryption at rest (KMS), TLS in transit, field-level masking

  Denial of Service:
    Threat: Flood de requests
    Control: Rate limiting (Kong), Auto Scaling, CloudFront

  Elevation of Privilege:
    Threat: Usuario accede órdenes de otros
    Control: Row-level security (CustomerId filter), RBAC

Architecture Controls:
  Perimeter:
    - WAF: AWS Managed Rules (OWASP Top 10)
    - CloudFront: DDoS protection, geo-blocking

  Network:
    - VPC: Private subnets para ECS tasks y RDS
    - Security Groups: Only ALB → ECS:8080, ECS → RDS:5432
    - NAT Gateway: Outbound only (external APIs)

  Application:
    - Kong Gateway: JWT validation, rate limiting (100/min)
    - Backend: FluentValidation (input), output encoding
    - Secrets: AWS Secrets Manager (no env vars)

  Data:
    - PostgreSQL: Encryption at rest (KMS), TLS connections
    - S3: Server-side encryption, bucket policies
    - Backups: Encrypted, cross-region replication

Testing:
  - SAST: SonarQube (block PR si high/critical)
  - Dependency Scanning: Snyk, Dependabot
  - Container Scanning: Trivy (block insecure base images)
  - DAST: OWASP ZAP (staging environment, pre-production)
  - Penetration Test: Anual (external firm)

Compliance:
  - PCI-DSS: No almacena CVV, tokenization (Stripe)
  - GDPR: Consent management, right to deletion
  - SOC 2 Type II: Access controls, audit logs, encryption
```

## Security Decision Records

```yaml
# ✅ Documentar decisiones de seguridad (ADR)

ADR-SEC-001: Authentication Strategy

  Decision: OAuth 2.0 con Keycloak SSO

  Rationale:
    - Centralizar identidades (no múltiples user DBs)
    - MFA built-in (TOTP, SMS)
    - OIDC compliance (standard)
    - Battle-tested (usado por Red Hat, NASA)

  Security Benefits:
    - Single source of truth (identities)
    - Credential rotation centralizada
    - Auditoría unificada
    - Reduce attack surface (no auth en cada servicio)

  Trade-offs:
    - Single point of failure (mitigation: HA cluster)
    - Latency overhead (mitigation: token caching)

ADR-SEC-002: Secrets Management

  Decision: AWS Secrets Manager

  Rationale:
    - Automatic rotation (PostgreSQL, API keys)
    - Encryption at rest (KMS)
    - Fine-grained IAM policies
    - Audit trail (CloudTrail)

  Security Benefits:
    - No secrets en código, env vars, config files
    - Rotation sin downtime
    - Versioning (rollback si needed)

  Cost: $0.40/secret/month + $0.05/10K API calls

ADR-SEC-003: Network Architecture

  Decision: Private subnets + NAT Gateway

  Rationale:
    - Zero inbound internet access (ECS, RDS)
    - Outbound via NAT (external APIs, updates)
    - ALB en public subnet (only ingress)

  Security Benefits:
    - Reduce attack surface (no direct internet)
    - Prevent data exfiltration (egress rules)
    - DMZ-style architecture
```

---

## Requisitos Técnicos

### MUST (Obligatorio)

- **MUST** realizar threat modeling para todo nuevo sistema/feature crítico
- **MUST** identificar data classification (public/internal/confidential/restricted)
- **MUST** diseñar trust boundaries explícitos
- **MUST** aplicar defense in depth (mínimo 3 capas)
- **MUST** implementar secure defaults (no debug, no default passwords)
- **MUST** documentar decisiones de seguridad (ADRs)
- **MUST** ejecutar SAST en CI/CD (block si critical vulnerabilities)

### SHOULD (Fuertemente recomendado)

- **SHOULD** usar security patterns establecidos (Gateway Offloading, Zero Trust)
- **SHOULD** realizar security architecture review (pre-implementación)
- **SHOULD** ejecutar DAST en staging (pre-producción)
- **SHOULD** realizar penetration testing anualmente

### MUST NOT (Prohibido)

- **MUST NOT** agregar seguridad como "afterthought" (post-desarrollo)
- **MUST NOT** hardcodear secrets en código
- **MUST NOT** exponer servicios directamente a internet (usar Gateway)
- **MUST NOT** usar default/insecure configurations en producción
- **MUST NOT** almacenar PII sin encryption

---

## Referencias

- [Lineamiento: Arquitectura Segura](../../lineamientos/seguridad/01-arquitectura-segura.md)
- [Threat Modeling](./threat-modeling.md)
- [Trust Boundaries](./trust-boundaries.md)
- [Attack Surface Reduction](./attack-surface-reduction.md)
- [ADR-004: Keycloak SSO](../../../decisiones-de-arquitectura/adr-004-keycloak-sso-autenticacion.md)
- [ADR-003: AWS Secrets Manager](../../../decisiones-de-arquitectura/adr-003-aws-secrets-manager.md)
