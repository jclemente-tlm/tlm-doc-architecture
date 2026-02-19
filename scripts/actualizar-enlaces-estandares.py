#!/usr/bin/env python3
"""
Script para actualizar enlaces a estándares atómicos → enlaces a secciones en estándares consolidados
"""

import re
import os
from pathlib import Path

# Mapeo completo: estándar-atómico.md → archivo-consolidado.md#anchor
MAPEO_ESTANDARES = {
    # Testing
    "unit-testing.md": "unit-integration-testing.md#1-unit-testing",
    "integration-testing.md": "unit-integration-testing.md#2-integration-testing",
    "contract-testing.md": "contract-e2e-testing.md#1-contract-testing",
    "e2e-testing.md": "contract-e2e-testing.md#2-e2e-testing",
    "test-coverage.md": "testing-strategy.md#3-test-coverage",
    "test-automation.md": "testing-strategy.md#2-test-automation",
    # "testing-strategy.md" se mantiene sin cambios (archivo consolidado principal)
    # "performance-testing.md" se mantiene sin cambios (archivo consolidado principal)

    # Arquitectura
    "hexagonal-architecture.md": "clean-architecture.md#1-hexagonal-architecture-ports-adapters",
    "dependency-inversion.md": "clean-architecture.md#2-dependency-inversion-principle-dip",
    "layered-architecture.md": "clean-architecture.md#3-layered-architecture",
    "framework-independence.md": "clean-architecture.md#4-framework-independence",
    "domain-model.md": "domain-modeling.md#1-domain-model",
    "aggregates.md": "domain-modeling.md#2-aggregates",
    "entities-value-objects.md": "domain-modeling.md#3-entities-value-objects",
    "bounded-contexts.md": "domain-modeling.md#4-bounded-contexts",
    "context-mapping.md": "domain-modeling.md#5-context-mapping",
    "ubiquitous-language.md": "domain-modeling.md#6-ubiquitous-language",
    "domain-events.md": "domain-modeling.md#7-domain-events",
    "circuit-breaker.md": "resilience-patterns.md#1-circuit-breaker",
    "retry-patterns.md": "resilience-patterns.md#2-retry",
    "timeout-patterns.md": "resilience-patterns.md#3-timeout",
    "bulkhead-pattern.md": "resilience-patterns.md#4-bulkhead",
    "rate-limiting.md": "resilience-patterns.md#5-rate-limiting",
    "graceful-degradation.md": "resilience-patterns.md#6-graceful-degradation",
    "graceful-shutdown.md": "resilience-patterns.md#7-graceful-shutdown",
    "cqrs-pattern.md": "cqrs-event-driven.md#1-cqrs-pattern",
    "saga-pattern.md": "cqrs-event-driven.md#2-saga-pattern",
    "async-processing.md": "cqrs-event-driven.md#3-async-processing",
    "compensation-pattern.md": "cqrs-event-driven.md#4-compensation-pattern",
    "kiss-principle.md": "architecture-principles.md#1-kiss-keep-it-simple-stupid",
    "yagni-principle.md": "architecture-principles.md#2-yagni-you-arent-gonna-need-it",
    "loose-coupling.md": "architecture-principles.md#3-loose-coupling",
    "operational-simplicity.md": "architecture-principles.md#5-operational-simplicity",
    "complexity-analysis.md": "architecture-principles.md#6-complexity-analysis",
    "simplicity-metrics.md": "architecture-principles.md#7-simplicity-metrics",
    "dependency-management.md": "architecture-principles.md#4-dependency-management",
    "stateless-design.md": "scalability-performance.md#1-stateless-design",
    "caching-strategies.md": "scalability-performance.md#2-caching-strategies",
    "horizontal-scaling.md": "scalability-performance.md#3-horizontal-scaling",
    "load-balancing.md": "scalability-performance.md#4-load-balancing",
    "health-checks.md": "scalability-performance.md",
    "fitness-functions.md": "architecture-evolution.md#1-fitness-functions",
    "reversibility.md": "architecture-evolution.md#2-reversibility",
    "technology-selection.md": "architecture-evolution.md#3-technology-selection",
    "twelve-factor-app.md": "architecture-evolution.md#4-twelve-factor-app",

    # APIs
    "api-rest-standards.md": "rest-api-design.md#1-rest-standards",
    "api-contracts.md": "rest-api-design.md#2-api-contracts",
    "api-versioning.md": "rest-api-design.md#3-api-versioning",
    "api-pagination.md": "rest-api-design.md#4-api-pagination",
    "api-backward-compatibility.md": "rest-api-design.md#5-backward-compatibility",
    "event-contracts.md": "event-api-contracts.md#1-event-contracts",
    "openapi-specification.md": "event-api-contracts.md#2-asyncapi-specification",
    "api-error-handling.md": "api-error-handling.md",

    # Datos
    "database-per-service.md": "data-architecture.md#1-database-per-service",
    "no-shared-database.md": "data-architecture.md#2-no-shared-database",
    "data-ownership-definition.md": "data-architecture.md#3-data-ownership",
    "data-governance.md": "data-architecture.md#4-data-governance",
    "data-catalog.md": "data-architecture.md#5-data-catalog",
    "data-exposure.md": "data-architecture.md#6-data-exposure",
    "consistency-models.md": "data-consistency.md#1-consistency-models",
    "conflict-resolution.md": "data-consistency.md#2-conflict-resolution",
    "data-replication.md": "data-consistency.md#3-data-replication",
    "expand-contract-pattern.md": "data-consistency.md#4-expand-contract-pattern",
    "database-migrations.md": "database-standards.md#1-database-migrations",
    "database-optimization.md": "database-standards.md#2-database-optimization",
    "connection-pooling.md": "database-standards.md#3-connection-pooling",
    "data-validation.md": "database-standards.md#4-data-validation",

    # Desarrollo
    "git-workflow.md": "git-workflow.md#1-git-workflow",
    "branching-strategy.md": "git-workflow.md#2-branching-strategy",
    "merge-strategies.md": "git-workflow.md#3-merge-strategies",
    "branch-protection.md": "git-workflow.md#4-branch-protection",
    "conventional-commits.md": "git-workflow.md#5-conventional-commits",
    "code-conventions.md": "code-quality.md#1-code-conventions",
    "code-review.md": "code-quality.md#2-code-review",
    "refactoring-practices.md": "code-quality.md#3-refactoring-practices",
    "sast.md": "code-quality.md#4-sast-static-application-security-testing",
    "static-analysis.md": "code-quality.md#5-static-analysis",
    "quality-gates.md": "code-quality.md#6-quality-gates",
    "package-management.md": "dependency-configuration.md#1-package-management",
    "semantic-versioning.md": "dependency-configuration.md#2-semantic-versioning",
    "no-hardcoded-config.md": "dependency-configuration.md#3-no-hardcoded-config",
    "independent-deployment.md": "dependency-configuration.md#4-independent-deployment",
    "database-code-standards.md": "dependency-configuration.md#5-database-code-standards",

    # Documentación
    "arc42.md": "architecture-documentation.md#1-arc42-template",
    "c4-model.md": "architecture-documentation.md#2-c4-model",
    "architecture-decision-records.md": "architecture-documentation.md#3-architecture-decision-records-adrs",
    "adr-template.md": "architecture-documentation.md#4-adr-template",
    "readme-standards.md": "technical-documentation.md#1-readme-standards",
    "contributing-guides.md": "technical-documentation.md#2-contributing-guides",
    "onboarding-guides.md": "technical-documentation.md#3-onboarding-guides",
    "runbooks.md": "technical-documentation.md#4-runbooks",

    # Gobierno
    "architecture-review.md": "architecture-governance.md#1-architecture-review",
    "architecture-review-checklist.md": "architecture-governance.md#2-architecture-review-checklist",
    "architecture-board.md": "architecture-governance.md#3-architecture-board",
    "architecture-audits.md": "architecture-governance.md#4-architecture-audits",
    "architecture-retrospectives.md": "architecture-governance.md#5-architecture-retrospectives",
    "adr-registry.md": "architecture-governance.md#6-adr-registry",
    "adr-lifecycle.md": "architecture-governance.md#7-adr-lifecycle",
    "adr-versioning.md": "architecture-governance.md#8-adr-versioning",
    "review-documentation.md": "architecture-governance.md#9-review-documentation",
    "compliance-validation.md": "compliance-exceptions.md#1-compliance-validation",
    "automated-compliance.md": "compliance-exceptions.md#2-automated-compliance",
    "exception-management.md": "compliance-exceptions.md#3-exception-management",
    "exception-criteria.md": "compliance-exceptions.md#4-exception-criteria",
    "exception-review.md": "compliance-exceptions.md#5-exception-review",
    "service-ownership.md": "compliance-exceptions.md#6-service-ownership",

    # Infraestructura
    "containerization.md": "containerization.md",
    "iac-implementation.md": "infrastructure-as-code.md#1-iac-implementation",
    "iac-workflow.md": "infrastructure-as-code.md#2-iac-workflow",
    "iac-state-management.md": "infrastructure-as-code.md#3-iac-state-management",
    "iac-versioning.md": "infrastructure-as-code.md#4-iac-versioning",
    "iac-code-review.md": "infrastructure-as-code.md#5-iac-code-review",
    "drift-detection.md": "infrastructure-as-code.md#6-drift-detection",
    "virtual-networks.md": "infrastructure-as-code.md#7-virtual-networks",
    "cloud-cost-optimization.md": "infrastructure-as-code.md#8-cloud-cost-optimization",
    "externalize-configuration.md": "configuration-management.md#1-externalize-configuration",
    "centralized-configuration.md": "configuration-management.md#2-centralized-configuration",
    "environment-variables.md": "configuration-management.md#3-environment-variables",
    "environment-parity.md": "configuration-management.md#4-environment-parity",

    # Mensajería
    "async-messaging.md": "event-driven-architecture.md#1-async-messaging",
    "event-design.md": "event-driven-architecture.md#2-event-design",
    "event-catalog.md": "event-driven-architecture.md#3-event-catalog",
    "idempotency.md": "event-driven-architecture.md#4-idempotency",
    "message-delivery-guarantees.md": "message-reliability.md#1-message-delivery-guarantees",
    "dead-letter-queue.md": "message-reliability.md#2-dead-letter-queue",

    # Observabilidad
    "structured-logging.md": "logging-monitoring.md#1-structured-logging",
    "metrics-standards.md": "logging-monitoring.md#2-metrics-standards",
    "dashboards.md": "logging-monitoring.md#3-dashboards",
    "alerting.md": "logging-monitoring.md#4-alerting",
    "distributed-tracing.md": "distributed-tracing.md#1-distributed-tracing",
    "correlation-ids.md": "distributed-tracing.md#2-correlation-ids",
    "slo-sla.md": "distributed-tracing.md#3-slo-sla",

    # Operabilidad
    "cicd-pipelines.md": "cicd-deployment.md#1-ci-cd-pipelines",
    "build-automation.md": "cicd-deployment.md#2-build-automation",
    "deployment-strategies.md": "cicd-deployment.md#3-deployment-strategies",
    "deployment-traceability.md": "cicd-deployment.md#4-deployment-traceability",
    "rollback-automation.md": "cicd-deployment.md#5-rollback-automation",
    "artifact-management.md": "cicd-deployment.md#6-artifact-management",
    "backup-automation.md": "disaster-recovery.md#1-backup-automation",
    "backup-retention.md": "disaster-recovery.md#2-backup-retention",
    "restore-testing.md": "disaster-recovery.md#3-restore-testing",
    "dr-drills.md": "disaster-recovery.md#4-dr-drills",
    "dr-runbooks.md": "disaster-recovery.md#5-dr-runbooks",
    "rpo-rto-definition.md": "disaster-recovery.md#6-rpo-rto-definition",
    "multi-region-failover.md": "disaster-recovery.md#7-multi-region-failover",

    # Seguridad
    "zero-trust-networking.md": "zero-trust-architecture.md#1-zero-trust-networking",
    "mutual-authentication.md": "zero-trust-architecture.md#2-mutual-authentication",
    "mutual-tls.md": "zero-trust-architecture.md#3-mutual-tls-mtls",
    "explicit-verification.md": "zero-trust-architecture.md#4-explicit-verification",
    "assume-breach.md": "zero-trust-architecture.md#5-assume-breach",
    "trust-boundaries.md": "zero-trust-architecture.md#6-trust-boundaries",
    "sso-implementation.md": "identity-access-management.md#1-sso-implementation",
    "mfa.md": "identity-access-management.md#2-multi-factor-authentication-mfa",
    "rbac.md": "identity-access-management.md#3-role-based-access-control-rbac",
    "abac.md": "identity-access-management.md#4-attribute-based-access-control-abac",
    "identity-federation.md": "identity-access-management.md#5-identity-federation",
    "identity-lifecycle.md": "identity-access-management.md#6-identity-lifecycle",
    "jit-access.md": "identity-access-management.md#7-just-in-time-jit-access",
    "service-accounts.md": "identity-access-management.md#8-service-accounts",
    "service-identity.md": "identity-access-management.md",
    "access-reviews.md": "identity-access-management.md",
    "password-policies.md": "identity-access-management.md",
    "auth-protocols.md": "identity-access-management.md",
    "encryption-at-rest.md": "data-protection.md#1-encryption-at-rest",
    "encryption-in-transit.md": "data-protection.md#2-encryption-in-transit",
    "data-masking.md": "data-protection.md#3-data-masking",
    "data-classification.md": "data-protection.md#4-data-classification",
    "data-minimization.md": "data-protection.md",
    "data-loss-prevention.md": "data-protection.md",
    "data-security.md": "data-protection.md",
    "network-segmentation.md": "network-security.md#1-network-segmentation",
    "network-access-controls.md": "network-security.md#2-network-access-controls",
    "network-security.md": "network-security.md",
    "environment-isolation.md": "network-security.md#3-environment-isolation",
    "tenant-isolation.md": "network-security.md#4-tenant-isolation",
    "perimeter-security.md": "network-security.md#5-perimetersecurity",
    "waf-ddos.md": "network-security.md",
    "orchestration-network-policies.md": "network-security.md",
    "attack-surface-reduction.md": "network-security.md",
    "threat-modeling.md": "security-testing.md#1-threat-modeling",
    "penetration-testing.md": "security-testing.md#2-penetration-testing",
    "vulnerability-tracking.md": "security-testing.md#3-vulnerability-tracking",
    "vulnerability-sla.md": "security-testing.md#4-vulnerability-sla",
    "secrets-management.md": "secrets-key-management.md#1-secrets-management",
    "key-management.md": "secrets-key-management.md#2-key-management",
    "security-by-design.md": "security-governance.md#1-security-by-design",
    "security-architecture-review.md": "security-governance.md#2-security-architecture-review",
    "application-security.md": "security-governance.md#3-application-security-owasp-top-10",
    "defense-in-depth.md": "security-governance.md#4-defense-in-depth",
    "patch-management.md": "security-governance.md#5-patch-management",
    "segregation-of-duties.md": "security-governance.md#6-segregation-of-duties",
    "secure-defaults.md": "security-governance.md#7-secure-defaults",
    "continuous-audit.md": "security-governance.md",
    "container-scanning.md": "security-scanning.md#1-container-scanning",
    "dependency-scanning.md": "security-scanning.md#2-dependency-scanning",
    "iac-scanning.md": "security-scanning.md#3-iac-scanning-terraform",
    "sbom.md": "security-scanning.md#4-sbom-software-bill-of-materials",
}


def actualizar_enlaces_estandares(directorio_lineamientos):
    """Actualiza todos los enlaces a estándares en los lineamientos"""

    archivos_modificados = []
    total_reemplazos = 0

    # Recorrer todos los archivos .md en lineamientos
    for md_file in Path(directorio_lineamientos).rglob("*.md"):
        contenido = md_file.read_text(encoding='utf-8')
        contenido_original = contenido

        # Buscar enlaces a estándares: ../../estandares/.../nombre.md
        for estandar_atomico, estandar_consolidado in MAPEO_ESTANDARES.items():
            # Patrón para encontrar referencias al estándar atómico
            # Puede estar en cualquier categoría de estandares
            patron = f"../../estandares/[^/]+/{estandar_atomico}"

            # Extraer categoría del estandar consolidado si no está especificada
            if "/" in estandar_consolidado:
                replacement = f"../../estandares/{estandar_consolidado}"
            else:
                # Necesitamos inferir la categoría del contexto
                # Por ahora, buscaremos el patrón y mantendremos la categoría existente
                replacement = estandar_consolidado

                # Buscar todas las referencias con la categoría
                matches = re.finditer(f"(../../estandares/[^/]+)/{estandar_atomico}", contenido)
                for match in matches:
                    categoria_path = match.group(1)
                    old_link = f"{categoria_path}/{estandar_atomico}"
                    new_link = f"{categoria_path}/{estandar_consolidado}"
                    contenido = contenido.replace(old_link, new_link)
                    total_reemplazos += 1
                continue

            # Reemplazar el enlace
            if patron in contenido:
                # Mantener la categoría original del lineamiento
                contenido = re.sub(
                    f"../../estandares/([^/]+)/{estandar_atomico}",
                    f"../../estandares/\\1/{estandar_consolidado}",
                    contenido
                )
                total_reemplazos += 1

        # Guardar si hubo cambios
        if contenido != contenido_original:
            md_file.write_text(contenido, encoding='utf-8')
            archivos_modificados.append(str(md_file))
            print(f"✓ Actualizado: {md_file.relative_to(directorio_lineamientos)}")

    return archivos_modificados, total_reemplazos


if __name__ == "__main__":
    lineamientos_dir = Path(__file__).parent.parent / "docs/fundamentos-corporativos/lineamientos"

    print("🔄 Actualizando enlaces a estándares consolidados...")
    print(f"📂 Directorio: {lineamientos_dir}\n")

    archivos, reemplazos = actualizar_enlaces_estandares(lineamientos_dir)

    print(f"\n✅ Proceso completado:")
    print(f"   - Archivos modificados: {len(archivos)}")
    print(f"   - Total reemplazos: {reemplazos}")

    if archivos:
        print(f"\n📝 Archivos actualizados:")
        for archivo in archivos[:10]:  # Mostrar solo primeros 10
            print(f"   - {Path(archivo).name}")
        if len(archivos) > 10:
            print(f"   ... y {len(archivos) - 10} más")
