#!/usr/bin/env python3
"""
Script para corregir enlaces rotos en la documentación de Docusaurus.
Basado en el reporte de errores de build de Docusaurus.
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Tuple

# Directorio base del proyecto
BASE_DIR = Path(__file__).parent.parent
DOCS_DIR = BASE_DIR / "docs"


class LinkFixer:
    """Clase para corregir enlaces rotos en archivos Markdown."""

    def __init__(self):
        self.fixes_applied = 0
        self.files_modified = set()

        # Mapeo de correcciones de enlaces
        self.link_corrections = {
            # Correcciones para decisiones-de-arquitectura/README.md
            "./adr-001-estrategia-multi-tenancy": "./adr-001-estrategia-multi-tenancy",
            "./adr-002-aws-ecs-fargate-contenedores": "./adr-002-aws-ecs-fargate-contenedores",
            "./adr-003-keycloak-sso-autenticacion": "./adr-003-keycloak-sso-autenticacion",
            "./adr-004-aws-secrets-manager": "./adr-004-aws-secrets-manager",
            "./adr-005-aws-parameter-store-configs": "./adr-005-aws-parameter-store-configs",
            "./adr-006-postgresql-base-datos": "./adr-006-postgresql-base-datos",
            "./adr-007-s3-almacenamiento-objetos": "./adr-007-s3-almacenamiento-objetos",
            "./adr-008-kafka-mensajeria-asincrona": "./adr-008-kafka-mensajeria-asincrona",
            "./adr-009-debezium-cdc": "./adr-009-debezium-cdc",
            "./adr-010-kong-api-gateway": "./adr-010-kong-api-gateway",
            "./adr-011-terraform-iac": "./adr-011-terraform-iac",
            "./adr-012-github-actions-cicd": "./adr-012-github-actions-cicd",
            "./adr-013-github-container-registry": "./adr-013-github-container-registry",
            "./adr-014-grafana-stack-observabilidad": "./adr-014-grafana-stack-observabilidad",

            # Correcciones para fundamentos-corporativos/estandares/README.md (remover extensiones .md)
            "../lineamientos": "../lineamientos",
            "./estandares/apis": "./apis",
            "./estandares/desarrollo": "./desarrollo",
            "./estandares/infraestructura": "./infraestructura",
            "./estandares/testing": "./testing",
            "./estandares/observabilidad": "./observabilidad",
            "./estandares/mensajeria": "./mensajeria",
            "./estandares/documentacion": "./documentacion",

            # Correcciones de URLs absolutas incorrectas
            "/tlm-doc-architecture/fundamentos-corporativos/principios": "/docs/fundamentos-corporativos/principios",
            "/tlm-doc-architecture/decisiones-de-arquitectura": "/docs/decisiones-de-arquitectura",
            "/tlm-doc-architecture/fundamentos/estandares/documentacion/architecture-documentation": "/docs/fundamentos-corporativos/estandares/documentacion/architecture-documentation",
            "/tlm-doc-architecture/fundamentos/estilos-arquitectonicos": "/docs/fundamentos-corporativos/estilos-arquitectonicos",
            "/tlm-doc-architecture/fundamentos/lineamientos": "/docs/fundamentos-corporativos/lineamientos",
            "/tlm-doc-architecture/aplicaciones": "/docs/aplicaciones",
            "/tlm-doc-architecture/plataforma-corporativa/plataforma-de-integracion": "/docs/plataforma-corporativa/plataforma-de-integracion",

            # Correcciones específicas para lineamientos (remover extensiones .md)
            "../../lineamientos/arquitectura/06-apis-y-contratos.md": "../../lineamientos/arquitectura/06-apis-y-contratos",
            "../../lineamientos/desarrollo/01-calidad-de-codigo.md": "../../lineamientos/desarrollo/01-calidad-de-codigo",
            "../../lineamientos/arquitectura/07-comunicacion-asincrona-y-eventos.md": "../../lineamientos/arquitectura/07-comunicacion-asincrona-y-eventos",
            "../../lineamientos/gobierno/01-gobierno-arquitectura.md": "../../lineamientos/gobierno/01-gobierno-arquitectura",
            "../../lineamientos/datos/02-consistencia-eventual.md": "../../lineamientos/datos/02-consistencia-eventual",
            "../../lineamientos/desarrollo/03-configuracion-externa.md": "../../lineamientos/desarrollo/03-configuracion-externa",
            "../../lineamientos/desarrollo/05-control-de-versiones.md": "../../lineamientos/desarrollo/05-control-de-versiones",
            "../../lineamientos/gobierno/02-documentacion-arquitectonica.md": "../../lineamientos/gobierno/02-documentacion-arquitectonica",
            "../../lineamientos/operabilidad/03-infraestructura-como-codigo.md": "../../lineamientos/operabilidad/03-infraestructura-como-codigo",
            "../lineamientos/arquitectura/11-arquitectura-evolutiva.md": "../lineamientos/arquitectura/11-arquitectura-evolutiva",
            "../lineamientos/arquitectura/05-observabilidad.md": "../lineamientos/arquitectura/05-observabilidad",
            "../lineamientos/arquitectura/09-autonomia-de-servicios.md": "../lineamientos/arquitectura/09-autonomia-de-servicios",
            "../lineamientos/arquitectura/08-diseno-orientado-al-dominio.md": "../lineamientos/arquitectura/08-diseno-orientado-al-dominio",
            "../lineamientos/arquitectura/10-arquitectura-limpia.md": "../lineamientos/arquitectura/10-arquitectura-limpia",
            "../lineamientos/arquitectura/12-simplicidad-intencional.md": "../lineamientos/arquitectura/12-simplicidad-intencional",
            "./06-apis-y-contratos.md": "./06-apis-y-contratos",
            "../lineamientos.md": "../lineamientos",
            "../lineamientos/arquitectura": "../lineamientos/arquitectura",
            "../../estandares/principios/01-mantenibilidad-y-extensibilidad.md": "../../principios/04-mantenibilidad-y-extensibilidad",
            "./04-recuperacion-ante-desastres.md": "./04-recuperacion-ante-desastres",
            "../../principios/04-seguridad-desde-el-diseno.md": "../../principios/02-seguridad-desde-el-diseno",
            "../lineamientos/operabilidad/04-recuperacion-ante-desastres.md": "../lineamientos/operabilidad/04-recuperacion-ante-desastres",

            # Correcciones de URLs a ADRs
            "/tlm-doc-architecture/decisiones-de-arquitectura/adr-004-aws-secrets-manager": "/docs/decisiones-de-arquitectura/adr-004-aws-secrets-manager",
            "/tlm-doc-architecture/decisiones-de-arquitectura/adr-002-aws-ecs-fargate-contenedores": "/docs/decisiones-de-arquitectura/adr-002-aws-ecs-fargate-contenedores",
            "/tlm-doc-architecture/decisiones-de-arquitectura/adr-008-kafka-mensajeria-asincrona": "/docs/decisiones-de-arquitectura/adr-008-kafka-mensajeria-asincrona",
            "/tlm-doc-architecture/decisiones-de-arquitectura/adr-001-estrategia-multi-tenancy": "/docs/decisiones-de-arquitectura/adr-001-estrategia-multi-tenancy",
            "/tlm-doc-architecture/decisiones-de-arquitectura/adr-012-github-actions-cicd": "/docs/decisiones-de-arquitectura/adr-012-github-actions-cicd",
            "/tlm-doc-architecture/decisiones-de-arquitectura/adr-010-kong-api-gateway": "/docs/decisiones-de-arquitectura/adr-010-kong-api-gateway",
            "/tlm-doc-architecture/decisiones-de-arquitectura/adr-003-keycloak-sso-autenticacion": "/docs/decisiones-de-arquitectura/adr-003-keycloak-sso-autenticacion",
            "/tlm-doc-architecture/decisiones-de-arquitectura/adr-014-grafana-stack-observabilidad": "/docs/decisiones-de-arquitectura/adr-014-grafana-stack-observabilidad",
            "/tlm-doc-architecture/decisiones-de-arquitectura/adr-008-kafka-mensajeria-asincrona#-garant%C3%ADas-de-entrega": "/docs/decisiones-de-arquitectura/adr-008-kafka-mensajeria-asincrona#-garantías-de-entrega",
            "/tlm-doc-architecture/decisiones-de-arquitectura/adr-006-postgresql-base-datos": "/docs/decisiones-de-arquitectura/adr-006-postgresql-base-datos",

            # Correcciones de URLs a principios
            "/tlm-doc-architecture/fundamentos-corporativos/principios/02-modularidad-y-bajo-acoplamiento.md": "/docs/fundamentos-corporativos/principios/01-modularidad-y-bajo-acoplamiento",
            "/tlm-doc-architecture/fundamentos-corporativos/principios/datos/03-consistencia-contextual.md": "/docs/fundamentos-corporativos/principios/01-modularidad-y-bajo-acoplamiento",

            # Correcciones de enlaces a estándares que no existen
            "../../lineamientos/infraestructura": "../../lineamientos/operabilidad/03-infraestructura-como-codigo",
            "../seguridad": "../seguridad",

            # Correcciones de enlaces rotos complejos
            "../../datos/data-consistency.md#1-consistency-models": "../../estandares/datos/data-consistency#1-consistency-models",
            "../../arquitectura/cqrs-event-driven.md#2-saga-pattern": "../../estandares/arquitectura/cqrs-event-driven#2-saga-pattern",
            "../../datos/data-consistency.md#2-conflict-resolution": "../../estandares/datos/data-consistency#2-conflict-resolution",
            "../../datos/data-consistency.md#3-data-replication": "../../estandares/datos/data-consistency#3-data-replication",
            "../../arquitectura/cqrs-event-driven.md#1-cqrs-pattern": "../../estandares/arquitectura/cqrs-event-driven#1-cqrs-pattern",
            "../../arquitectura/cqrs-event-driven.md#4-compensation-pattern": "../../estandares/arquitectura/cqrs-event-driven#4-compensation-pattern",
            "../../datos/data-architecture.md#1-database-per-service": "../../estandares/datos/data-architecture#1-database-per-service",
            "../../datos/data-architecture.md#2-no-shared-database": "../../estandares/datos/data-architecture#2-no-shared-database",
            "../../datos/data-architecture.md#6-data-exposure": "../../estandares/datos/data-architecture#6-data-exposure",
            "../../datos/database-standards.md#1-database-migrations": "../../estandares/datos/database-standards#1-database-migrations",
            "../../datos/database-standards.md#4-data-validation": "../../estandares/datos/database-standards#4-data-validation",
            "../../datos/data-consistency.md#4-expand-contract-pattern": "../../estandares/datos/data-consistency#4-expand-contract-pattern",
            "../../datos/data-architecture.md#3-data-ownership": "../../estandares/datos/data-architecture#3-data-ownership",
            "../../datos/data-architecture.md#5-data-catalog": "../../estandares/datos/data-architecture#5-data-catalog",
            "../../datos/data-architecture.md#4-data-governance": "../../estandares/datos/data-architecture#4-data-governance",
            "../../desarrollo/code-quality.md#1-code-conventions": "../../estandares/desarrollo/code-quality#1-code-conventions",
            "../../desarrollo/dependency-configuration.md#5-database-code-standards": "../../estandares/desarrollo/dependency-configuration#5-database-code-standards",
            "../../desarrollo/code-quality.md#5-static-analysis": "../../estandares/desarrollo/code-quality#5-static-analysis",
            "../../desarrollo/code-quality.md#4-sast-static-application-security-testing": "../../estandares/desarrollo/code-quality#4-sast-static-application-security-testing",
            "../../desarrollo/code-quality.md#2-code-review": "../../estandares/desarrollo/code-quality#2-code-review",
            "../../desarrollo/code-quality.md#6-quality-gates": "../../estandares/desarrollo/code-quality#6-quality-gates",
            "../../desarrollo/git-workflow.md#1-git-workflow": "../../estandares/desarrollo/git-workflow#1-git-workflow",
            "../../desarrollo/git-workflow.md#2-branching-strategy": "../../estandares/desarrollo/git-workflow#2-branching-strategy",
            "../../desarrollo/git-workflow.md#5-conventional-commits": "../../estandares/desarrollo/git-workflow#5-conventional-commits",
            "../../desarrollo/dependency-configuration.md#2-semantic-versioning": "../../estandares/desarrollo/dependency-configuration#2-semantic-versioning",
            "../../desarrollo/git-workflow.md#4-branch-protection": "../../estandares/desarrollo/git-workflow#4-branch-protection",
            "../../desarrollo/git-workflow.md#3-merge-strategies": "../../estandares/desarrollo/git-workflow#3-merge-strategies",
            "../../documentacion/technical-documentation.md#1-readme-standards": "../../estandares/documentacion/technical-documentation#1-readme-standards",
            "../../documentacion/architecture-documentation.md#3-architecture-decision-records-adrs": "../../estandares/documentacion/architecture-documentation#3-architecture-decision-records-adrs",
            "../../documentacion/architecture-documentation.md#1-arc42-template": "../../estandares/documentacion/architecture-documentation#1-arc42-template",
            "../../documentacion/architecture-documentation.md#2-c4-model": "../../estandares/documentacion/architecture-documentation#2-c4-model",
            "../../documentacion/technical-documentation.md#4-runbooks": "../../estandares/documentacion/technical-documentation#4-runbooks",
            "../../documentacion/technical-documentation.md#3-onboarding-guides": "../../estandares/documentacion/technical-documentation#3-onboarding-guides",
            "../../documentacion/technical-documentation.md#2-contributing-guides": "../../estandares/documentacion/technical-documentation#2-contributing-guides",
            "../..//decisiones-de-arquitectura#readme": "/docs/decisiones-de-arquitectura",
            "../../testing/unit-integration-testing.md#1-unit-testing": "../../estandares/testing/unit-integration-testing#1-unit-testing",
            "../../testing/unit-integration-testing.md#2-integration-testing": "../../estandares/testing/unit-integration-testing#2-integration-testing",
            "../../testing/contract-e2e-testing.md#1-contract-testing": "../../estandares/testing/contract-e2e-testing#1-contract-testing",
            "../../testing/contract-e2e-testing.md#2-e2e-testing": "../../estandares/testing/contract-e2e-testing#2-e2e-testing",
            "../../testing/testing-strategy.md#3-test-coverage": "../../estandares/testing/testing-strategy#3-test-coverage",
            "../../testing/testing-strategy.md#2-test-automation": "../../estandares/testing/testing-strategy#2-test-automation",
            "../../testing/performance-testing.md": "../../estandares/testing/performance-testing",
            "../../gobierno/compliance-exceptions.md#1-compliance-validation": "../../estandares/gobierno/compliance-exceptions#1-compliance-validation",
            "../../gobierno/compliance-exceptions.md#2-automated-compliance": "../../estandares/gobierno/compliance-exceptions#2-automated-compliance",
            "../../gobierno/architecture-governance.md#4-architecture-audits": "../../estandares/gobierno/architecture-governance#4-architecture-audits",
            "../../gobierno/compliance-exceptions.md#3-exception-management": "../../estandares/gobierno/compliance-exceptions#3-exception-management",
            "../../gobierno/compliance-exceptions.md#4-exception-criteria": "../../estandares/gobierno/compliance-exceptions#4-exception-criteria",
            "../../gobierno/compliance-exceptions.md#5-exception-review": "../../estandares/gobierno/compliance-exceptions#5-exception-review",
            "../../documentacion/architecture-documentation.md#4-adr-template": "../../estandares/documentacion/architecture-documentation#4-adr-template",
            "../../gobierno/architecture-governance.md#1-architecture-review": "../../estandares/gobierno/architecture-governance#1-architecture-review",
            "../../gobierno/architecture-governance.md#8-adr-versioning": "../../estandares/gobierno/architecture-governance#8-adr-versioning",
            "../../gobierno/architecture-governance.md#6-adr-registry": "../../estandares/gobierno/architecture-governance#6-adr-registry",
            "../../gobierno/architecture-governance.md#7-adr-lifecycle": "../../estandares/gobierno/architecture-governance#7-adr-lifecycle",
            "../../gobierno/architecture-governance.md#2-architecture-review-checklist": "../../estandares/gobierno/architecture-governance#2-architecture-review-checklist",
            "../../gobierno/architecture-governance.md#9-review-documentation": "../../estandares/gobierno/architecture-governance#9-review-documentation",
            "../../gobierno/architecture-governance.md#5-architecture-retrospectives": "../../estandares/gobierno/architecture-governance#5-architecture-retrospectives",
            "../../gobierno/architecture-governance.md#3-architecture-board": "../../estandares/gobierno/architecture-governance#3-architecture-board",
            "../../operabilidad/cicd-deployment.md#1-ci-cd-pipelines": "../../estandares/operabilidad/cicd-deployment#1-ci-cd-pipelines",
            "../../operabilidad/cicd-deployment.md#2-build-automation": "../../estandares/operabilidad/cicd-deployment#2-build-automation",
            "../../operabilidad/cicd-deployment.md#3-deployment-strategies": "../../estandares/operabilidad/cicd-deployment#3-deployment-strategies",
            "../../operabilidad/cicd-deployment.md#5-rollback-automation": "../../estandares/operabilidad/cicd-deployment#5-rollback-automation",
            "../../operabilidad/cicd-deployment.md#6-artifact-management": "../../estandares/operabilidad/cicd-deployment#6-artifact-management",
            "../../operabilidad/cicd-deployment.md#4-deployment-traceability": "../../estandares/operabilidad/cicd-deployment#4-deployment-traceability",
            "../../infraestructura/configuration-management.md#1-externalize-configuration": "../../estandares/infraestructura/configuration-management#1-externalize-configuration",
            "../.../seguridad/secrets-key-management.md#1-secrets-management": "../../estandares/seguridad/secrets-key-management#1-secrets-management",
            "../../infraestructura/configuration-management.md#2-centralized-configuration": "../../estandares/infraestructura/configuration-management#2-centralized-configuration",
            "../../infraestructura/configuration-management.md#4-environment-parity": "../../estandares/infraestructura/configuration-management#4-environment-parity",
            "../../infraestructura/configuration-management.md#3-environment-variables": "../../estandares/infraestructura/configuration-management#3-environment-variables",
            "../../desarrollo/dependency-configuration.md#3-no-hardcoded-config": "../../estandares/desarrollo/dependency-configuration#3-no-hardcoded-config",
            "../../operabilidad/disaster-recovery.md#6-rpo-rto-definition": "../../estandares/operabilidad/disaster-recovery#6-rpo-rto-definition",
            "../../operabilidad/disaster-recovery.md#1-backup-automation": "../../estandares/operabilidad/disaster-recovery#1-backup-automation",
            "../../operabilidad/disaster-recovery.md#2-backup-retention": "../../estandares/operabilidad/disaster-recovery#2-backup-retention",
            "../../operabilidad/disaster-recovery.md#3-restore-testing": "../../estandares/operabilidad/disaster-recovery#3-restore-testing",
            "../../operabilidad/disaster-recovery.md#5-dr-runbooks": "../../estandares/operabilidad/disaster-recovery#5-dr-runbooks",
            "../../operabilidad/disaster-recovery.md#4-dr-drills": "../../estandares/operabilidad/disaster-recovery#4-dr-drills",
            "../../operabilidad/disaster-recovery.md#7-multi-region-failover": "../../estandares/operabilidad/disaster-recovery#7-multi-region-failover",
            "../../infraestructura/infrastructure-as-code.md#1-iac-implementation": "../../estandares/infraestructura/infrastructure-as-code#1-iac-implementation",
            "../../infraestructura/infrastructure-as-code.md#4-iac-versioning": "../../estandares/infraestructura/infrastructure-as-code#4-iac-versioning",
            "../../infraestructura/infrastructure-as-code.md#5-iac-code-review": "../../estandares/infraestructura/infrastructure-as-code#5-iac-code-review",
            "../../infraestructura/infrastructure-as-code.md#3-iac-state-management": "../../estandares/infraestructura/infrastructure-as-code#3-iac-state-management",
            "../../infraestructura/infrastructure-as-code.md#2-iac-workflow": "../../estandares/infraestructura/infrastructure-as-code#2-iac-workflow",
            "../../infraestructura/infrastructure-as-code.md#6-drift-detection": "../../estandares/infraestructura/infrastructure-as-code#6-drift-detection",
            "../../desarrollo/dependency-configuration.md#1-package-management": "../../estandares/desarrollo/dependency-configuration#1-package-management",
            "../.../seguridad/secrets-key-management.md#2-key-management": "../../estandares/seguridad/secrets-key-management#2-key-management",
            "../../infraestructura/infrastructure-as-code.md#7-virtual-networks": "../../estandares/infraestructura/infrastructure-as-code#7-virtual-networks",
        }

    def fix_file(self, file_path: Path) -> int:
        """
        Corrige los enlaces rotos en un archivo específico.

        Args:
            file_path: Ruta del archivo a corregir

        Returns:
            Número de correcciones aplicadas
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            original_content = content
            fixes_in_file = 0

            # Aplicar todas las correcciones definidas
            for old_link, new_link in self.link_corrections.items():
                # Buscar el patrón en Markdown links [text](link)
                pattern = re.escape(old_link)
                if pattern in content:
                    content = content.replace(old_link, new_link)
                    fixes_in_file += 1

            # Corrección adicional: eliminar "link" solitario malformado
            content = re.sub(r'\[([^\]]+)\]\(link\)', r'[\1](#)', content)

            # Si hubo cambios, guardar el archivo
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.files_modified.add(file_path)
                self.fixes_applied += fixes_in_file
                print(f"✓ Corregido: {file_path.relative_to(BASE_DIR)} ({fixes_in_file} correcciones)")
                return fixes_in_file

            return 0

        except Exception as e:
            print(f"✗ Error procesando {file_path}: {e}")
            return 0

    def fix_all_markdown_files(self):
        """Corrige enlaces rotos en todos los archivos Markdown del directorio docs."""
        print("Iniciando corrección de enlaces rotos...\n")

        # Recorrer todos los archivos .md en docs/
        for md_file in DOCS_DIR.rglob("*.md"):
            self.fix_file(md_file)

        print(f"\n{'='*60}")
        print(f"Resumen:")
        print(f"  Archivos modificados: {len(self.files_modified)}")
        print(f"  Correcciones aplicadas: {self.fixes_applied}")
        print(f"{'='*60}\n")


def main():
    """Función principal."""
    fixer = LinkFixer()
    fixer.fix_all_markdown_files()

    if fixer.fixes_applied > 0:
        print("✓ Corrección completada exitosamente.")
        print("\nPor favor, ejecuta 'npm run build' para verificar que no quedan enlaces rotos.")
    else:
        print("No se aplicaron correcciones.")


if __name__ == "__main__":
    main()
