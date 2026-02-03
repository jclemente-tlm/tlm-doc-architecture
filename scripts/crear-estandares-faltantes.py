#!/usr/bin/env python3
"""
Script para crear todos los estándares faltantes basados en frameworks de industria.
Genera 66 archivos con contenido base alineado a mejores prácticas.
"""

import re
from pathlib import Path

# Obtener estándares faltantes
lineamientos_path = Path('docs/fundamentos-corporativos/lineamientos')
estandares_base = Path('docs/fundamentos-corporativos/estandares')
pattern = r'\]\(\.\./\.\./estandares/(.*?)\.md\)'

referencias = set()
for md_file in lineamientos_path.rglob('*.md'):
    referencias.update(re.findall(pattern, md_file.read_text()))

faltantes = [ref for ref in sorted(referencias) if not (estandares_base / f'{ref}.md').exists()]

print(f"📋 Total de estándares faltantes: {len(faltantes)}\n")

# Mapeo de estándares a frameworks de industria (basado en validación previa)
FRAMEWORKS_MAP = {
    # Arquitectura
    'arquitectura/circuit-breakers': ('Circuit Breaker Pattern', 'Release It! (Michael Nygard), Netflix Hystrix, Resilience4j'),
    'arquitectura/timeouts': ('Timeout Pattern', 'Release It!, Google SRE Book'),
    'arquitectura/retry-patterns': ('Retry Pattern', 'Azure Architecture Patterns, AWS Well-Architected'),
    'arquitectura/graceful-degradation': ('Graceful Degradation', 'Release It!, Google SRE Handbook'),
    'arquitectura/stateless-services': ('Stateless Services', '12-Factor App (Factor VI), Cloud Native Patterns'),
    'arquitectura/horizontal-scaling': ('Horizontal Scaling', 'Scalability Rules (Abbott & Fisher), AWS Best Practices'),
    'arquitectura/graceful-shutdown': ('Graceful Shutdown', 'Kubernetes Best Practices, 12-Factor App'),
    'arquitectura/saga-pattern': ('Saga Pattern', 'Microservices Patterns (Chris Richardson), DDD'),

    # APIs
    'apis/rest-conventions': ('RESTful API Design', 'Roy Fielding REST, Microsoft API Guidelines'),
    'apis/versionado': ('API Versioning', 'RESTful Web APIs (Richardson & Ruby), Stripe API'),
    'apis/openapi-swagger': ('OpenAPI Specification', 'OpenAPI 3.x, Swagger'),
    'apis/rate-limiting-paginacion': ('Rate Limiting & Pagination', 'RFC 6585, GitHub API, JSON:API'),
    'apis/error-handling': ('API Error Handling', 'RFC 7807 (Problem Details), Microsoft REST API Guidelines'),
    'apis/contract-validation': ('Contract Validation', 'OpenAPI Validation, JSON Schema'),
    'apis/deprecacion-apis': ('API Deprecation', 'Stripe API Versioning, Google API Design Guide'),
    'apis/api-portal': ('API Portal', 'DeveloperExperience.io, Stoplight, Swagger UI'),

    # Datos
    'datos/data-ownership': ('Data Ownership', 'Domain-Driven Design (Eric Evans), Data Mesh (Zhamak Dehghani)'),
    'datos/database-per-service': ('Database per Service', 'Microservices Patterns (Richardson), Martin Fowler'),
    'datos/data-access-via-apis': ('Data Access via APIs', 'Microservices Patterns, API-First Design'),
    'datos/schema-documentation': ('Schema Documentation', 'JSON Schema, Avro, Protobuf'),
    'datos/least-knowledge-principle': ('Principle of Least Knowledge', 'Law of Demeter, DDD Bounded Contexts'),
    'datos/database-migrations': ('Database Migrations', 'Refactoring Databases (Ambler & Sadalage), Flyway, Liquibase'),
    'datos/schema-validation': ('Schema Validation', 'JSON Schema, Avro Schema Validation'),
    'datos/schema-evolution': ('Schema Evolution', 'Confluent Schema Registry, Avro Evolution'),
    'datos/schema-registry': ('Schema Registry', 'Confluent Schema Registry, AWS Glue Schema Registry'),
    'datos/consistency-models': ('Consistency Models', 'CAP Theorem, PACELC, BASE'),
    'datos/reconciliation': ('Data Reconciliation', 'Eventual Consistency Patterns, Saga Pattern'),
    'datos/conflict-resolution': ('Conflict Resolution', 'CRDT (Conflict-free Replicated Data Types), Last-Write-Wins'),
    'datos/consistency-slos': ('Consistency SLOs', 'Google SRE Book, Service Level Objectives'),
    'datos/data-lifecycle': ('Data Lifecycle', 'GDPR Data Retention, AWS S3 Lifecycle, Azure Blob Lifecycle'),

    # Seguridad
    'seguridad/clasificacion-datos': ('Data Classification', 'NIST 800-60, ISO 27001, GDPR'),
    'seguridad/enmascaramiento-datos': ('Data Masking', 'OWASP Data Protection, PCI DSS'),
    'seguridad/gestion-claves-kms': ('Key Management', 'NIST SP 800-57, AWS KMS, Azure Key Vault'),
    'seguridad/minimizacion-datos': ('Data Minimization', 'GDPR Article 5, Privacy by Design'),
    'seguridad/retencion-eliminacion': ('Data Retention', 'GDPR Right to Erasure, SOC 2'),
    'seguridad/security-by-design': ('Security by Design', 'OWASP Security by Design, Microsoft SDL'),
    'seguridad/threat-modeling': ('Threat Modeling', 'STRIDE (Microsoft), PASTA, OCTAVE'),
    'seguridad/trust-boundaries': ('Trust Boundaries', 'OWASP Threat Modeling, Zero Trust Architecture'),
    'seguridad/reduccion-superficie-ataque': ('Attack Surface Reduction', 'OWASP Attack Surface Analysis, NIST'),
    'seguridad/defense-in-depth': ('Defense in Depth', 'NIST SP 800-53, ISO 27001'),
    'seguridad/sso-federado': ('SSO & Federation', 'SAML 2.0, OAuth 2.0, OpenID Connect'),
    'seguridad/mfa-configuracion': ('Multi-Factor Authentication', 'NIST 800-63B, FIDO2, WebAuthn'),
    'seguridad/minimo-privilegio': ('Least Privilege', 'NIST SP 800-53 AC-6, Zero Trust'),
    'seguridad/service-identities': ('Service Identities', 'SPIFFE/SPIRE, AWS IAM Roles, Managed Identities'),
    'seguridad/gestion-secretos': ('Secrets Management', 'HashiCorp Vault, AWS Secrets Manager, Azure Key Vault'),
    'seguridad/segmentacion-redes': ('Network Segmentation', 'NIST 800-41, Zero Trust Network Access'),
    'seguridad/separacion-entornos': ('Environment Separation', 'CIS Benchmarks, AWS Multi-Account Strategy'),
    'seguridad/aislamiento-tenants': ('Tenant Isolation', 'AWS SaaS Tenant Isolation, Multi-Tenancy Patterns'),
    'seguridad/zero-trust-network': ('Zero Trust Network', 'NIST 800-207, BeyondCorp (Google), Forrester Zero Trust'),
    'seguridad/zonas-seguridad': ('Security Zones', 'NIST 800-41, Firewall DMZ Architecture'),
    'seguridad/vulnerability-scanning': ('Vulnerability Scanning', 'OWASP Dependency-Check, Snyk, Trivy'),
    'seguridad/software-bill-of-materials': ('Software Bill of Materials', 'NTIA SBOM, CycloneDX, SPDX'),
    'seguridad/container-image-scanning': ('Container Scanning', 'Trivy, Clair, Aqua Security'),

    # Mensajería
    'mensajeria/schemas-eventos': ('Event Schemas', 'AsyncAPI, CloudEvents, Avro'),
    'mensajeria/idempotencia': ('Idempotency', 'Idempotent Receiver Pattern, At-Least-Once Delivery'),
    'mensajeria/garantias-entrega': ('Delivery Guarantees', 'Kafka Delivery Semantics, Exactly-Once Processing'),
    'mensajeria/dlq': ('Dead Letter Queue', 'Enterprise Integration Patterns, AWS SQS DLQ'),
    'mensajeria/topologia-eventos': ('Event Topology', 'Event-Driven Architecture, Kafka Topics Design'),

    # Testing
    'testing/contract-testing': ('Contract Testing', 'Pact, Spring Cloud Contract, Consumer-Driven Contracts'),

    # Operabilidad
    'operabilidad/cicd-pipelines': ('CI/CD Pipelines', 'Continuous Delivery (Jez Humble), GitHub Actions, GitLab CI'),
    'operabilidad/quality-security-gates': ('Quality Gates', 'SonarQube Quality Gates, OWASP DevSecOps'),
    'operabilidad/slos-slas': ('SLOs & SLAs', 'Google SRE Book - Service Level Objectives'),

    # Infraestructura
    'infraestructura/cost-tagging-strategy': ('Cost Tagging', 'FinOps Foundation, AWS Cost Allocation Tags'),
    'infraestructura/rightsizing': ('Resource Rightsizing', 'FinOps Foundation, AWS Compute Optimizer'),
    'infraestructura/cost-alerts': ('Cost Alerting', 'AWS Budgets, Azure Cost Management'),
    'infraestructura/reserved-capacity': ('Reserved Capacity', 'AWS Reserved Instances, Azure Reserved VM Instances'),

    # Gobierno
    'gobierno/architecture-review': ('Architecture Review', 'Architecture Review Board (ARB), TOGAF ADM'),
    'gobierno/review-documentation': ('Review Documentation', 'Architecture Governance, ISO 42010'),
    'gobierno/compliance-validation': ('Compliance Validation', 'ISO 27001 Audits, SOC 2 Compliance'),
    'gobierno/exception-management': ('Exception Management', 'Risk Management, TOGAF Exception Handling'),
    'gobierno/architecture-retrospectives': ('Architecture Retrospectives', 'Agile Retrospectives, Team Topologies'),

    # Documentación
    'documentacion/architecture-review': ('Architecture Review Process', 'TOGAF ADM, Architecture Review Board')
}

# Plantilla base
def generar_contenido(ruta, titulo, framework_info):
    nombre_framework, frameworks = framework_info

    return f"""# {titulo}

## Contexto

[Descripción del problema que este estándar resuelve]

## Decisión

Implementar {nombre_framework} siguiendo las mejores prácticas de la industria.

## Estándares Obligatorios

### 1. [Aspecto Principal]

[Detalles de implementación]

### 2. [Aspecto Secundario]

[Detalles de implementación]

## Alineación con Industria

**Frameworks de referencia:**
{frameworks}

## Validación de Cumplimiento

- [ ] [Criterio de validación 1]
- [ ] [Criterio de validación 2]
- [ ] [Criterio de validación 3]

## Referencias

- [Documentación del framework principal]
- [Recursos adicionales]

## Notas

⚠️ **PENDIENTE DE COMPLETAR:** Este archivo fue generado automáticamente.
Requiere revisión y completado de detalles específicos de implementación.
"""

# Crear archivos
creados = 0
for ruta in faltantes:
    archivo = estandares_base / f'{ruta}.md'
    archivo.parent.mkdir(parents=True, exist_ok=True)

    # Obtener título del nombre del archivo
    nombre = ruta.split('/')[-1].replace('-', ' ').title()

    # Obtener framework info si existe
    framework_info = FRAMEWORKS_MAP.get(ruta, (nombre, 'Pendiente de documentar frameworks de referencia'))

    with open(archivo, 'w', encoding='utf-8') as f:
        f.write(generar_contenido(ruta, nombre, framework_info))

    creados += 1
    if creados % 10 == 0:
        print(f"✅ Creados {creados}/{len(faltantes)} archivos...")

print(f"\n🎉 COMPLETADO: {creados} archivos de estándares creados")
print(f"📍 Ubicación: docs/fundamentos-corporativos/estandares/")
print(f"\n⚠️  NOTA: Los archivos contienen estructura base. Requieren revisión y completado.")
