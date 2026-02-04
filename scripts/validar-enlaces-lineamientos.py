#!/usr/bin/env python3
"""
Script para validar enlaces en archivos markdown de lineamientos
"""

import os
import re
import sys
    pattern = r'\[([^\]]+)\]\(([^)]+\.md[^)]*)\)'
    matches = re.findall(pattern, content)
    return matches

def resolve_path(source_file: Path, link_path: str) -> Path:
    """Resuelve la ruta relativa desde el archivo fuente"""
    # Remover anclas (#section)
    link_path = link_path.split('#')[0]

    # Resolver la ruta relativa
    source_dir = source_file.parent
    target_path = (source_dir / link_path).resolve()

    return target_path

def find_similar_files(target_name: str, estandares_dir: Path) -> List[str]:
    """Busca archivos con nombres similares en estandares/"""
    target_name = target_name.lower()
    similar = []

    for root, dirs, files in os.walk(estandares_dir):
        for file in files:
            if file.endswith('.md'):
                if target_name in file.lower() or file.lower() in target_name:
                    rel_path = Path(root) / file
                    similar.append(str(rel_path.relative_to(estandares_dir.parent.parent)))

    return similar

def suggest_correct_path(link_text: str, broken_path: str, lineamiento_file: Path, workspace_root: Path) -> str:
    """Sugiere la ruta correcta basándose en el nombre del archivo"""
    # Extraer el nombre del archivo del enlace roto
    broken_file = Path(broken_path).name
    base_name = broken_file.replace('.md', '')

    # Buscar en estandares
    estandares_dir = workspace_root / 'docs' / 'fundamentos-corporativos' / 'estandares'

    # Mapeo conocido de nombres
    known_mappings = {
        'api-rest.md': 'apis/api-rest-standards.md',
        'versioning.md': 'apis/api-versioning.md',
        'openapi-swagger.md': 'documentacion/openapi-swagger.md',
        'rate-limiting-pagination.md': 'apis/rate-limiting.md',
        'error-handling.md': 'apis/error-handling.md',
        'contract-validation.md': 'testing/contract-testing.md',
        'api-deprecation.md': 'apis/api-deprecation.md',
        'api-portal.md': 'desarrollo/api-portal.md',
        'contract-testing.md': 'testing/contract-testing.md',
        'kafka-events.md': 'mensajeria/kafka-messaging.md',
        'event-schemas.md': 'mensajeria/event-schemas.md',
        'domain-events.md': 'mensajeria/domain-events.md',
        'idempotency.md': 'mensajeria/idempotency.md',
        'delivery-guarantees.md': 'mensajeria/delivery-guarantees.md',
        'dead-letter-queue.md': 'mensajeria/dead-letter-queue.md',
        'event-topology.md': 'mensajeria/event-topology.md',
        'logging.md': 'observabilidad/observability.md',
        'metrics-monitoring.md': 'observabilidad/observability.md',
        'distributed-tracing.md': 'observabilidad/observability.md',
        'correlation-ids.md': 'observabilidad/observability.md',
        'health-checks.md': 'observabilidad/observability.md',
        'code-quality-standards.md': 'desarrollo/code-quality-review.md',
        'csharp-dotnet.md': 'desarrollo/csharp-conventions.md',
        'sql.md': 'desarrollo/sql-standards.md',
        'code-review-policy.md': 'desarrollo/code-quality-review.md',
        'testing-pyramid.md': 'testing/testing-standards.md',
        'unit-tests.md': 'testing/testing-standards.md',
        'integration-tests.md': 'testing/testing-standards.md',
        'architecture-decision-records.md': 'documentacion/architecture-decision-records.md',
        'architecture-review.md': 'gobierno/architecture-reviews.md',
        'review-documentation.md': 'gobierno/review-documentation.md',
        'architecture-retrospectives.md': 'gobierno/architecture-retrospectives.md',
        'compliance-validation.md': 'gobierno/compliance-validation.md',
        'exception-management.md': 'gobierno/exception-management.md',
        'security-by-design.md': 'seguridad/security-architecture.md',
        'threat-modeling.md': 'seguridad/threat-modeling.md',
        'trust-boundaries.md': 'seguridad/threat-modeling.md',
        'attack-surface-reduction.md': 'seguridad/security-architecture.md',
        'defense-in-depth.md': 'seguridad/security-architecture.md',
        'sso-federation.md': 'seguridad/identity-access-management.md',
        'mfa-configuration.md': 'seguridad/identity-access-management.md',
        'least-privilege.md': 'seguridad/identity-access-management.md',
        'service-identities.md': 'seguridad/identity-access-management.md',
        'secrets-management.md': 'seguridad/secrets-key-management.md',
        'network-segmentation.md': 'seguridad/network-security.md',
        'environment-separation.md': 'infraestructura/environment-separation.md',
        'tenant-isolation.md': 'seguridad/tenant-isolation.md',
        'zero-trust-network.md': 'seguridad/network-security.md',
        'security-zones.md': 'seguridad/network-security.md',
        'data-classification.md': 'datos/data-protection.md',
        'data-encryption.md': 'datos/data-protection.md',
        'data-masking.md': 'datos/data-protection.md',
        'key-management.md': 'seguridad/secrets-key-management.md',
        'data-minimization.md': 'datos/data-protection.md',
        'data-retention.md': 'datos/data-lifecycle.md',
        'vulnerability-management-program.md': 'seguridad/vulnerability-management.md',
        'vulnerability-scanning.md': 'seguridad/vulnerability-management.md',
        'software-bill-of-materials.md': 'seguridad/vulnerability-management.md',
        'container-image-scanning.md': 'infraestructura/contenedores.md',
        'incident-response-program.md': 'seguridad/incident-response.md',
        'cicd-pipelines.md': 'arquitectura/cicd-pipelines.md',
        'infrastructure-as-code.md': 'infraestructura/infrastructure-as-code.md',
        'quality-security-gates.md': 'desarrollo/code-quality-review.md',
        'dev-prod-parity.md': 'infraestructura/dev-prod-parity.md',
        'externalize-configuration.md': 'infraestructura/externalize-configuration.md',
        'cost-tagging-strategy.md': 'infraestructura/aws-cost-optimization.md',
        'rightsizing.md': 'infraestructura/aws-cost-optimization.md',
        'cost-alerts.md': 'infraestructura/aws-cost-optimization.md',
        'reserved-capacity.md': 'infraestructura/aws-cost-optimization.md',
        'data-lifecycle.md': 'datos/data-lifecycle.md',
        'single-responsibility.md': 'arquitectura/bounded-contexts.md',
        'dependency-management.md': 'arquitectura/dependency-management.md',
        'stateless-services.md': 'arquitectura/stateless-design.md',
        'horizontal-scaling.md': 'infraestructura/horizontal-scaling.md',
        'graceful-shutdown.md': 'arquitectura/graceful-shutdown.md',
        'circuit-breakers.md': 'arquitectura/resilience-patterns.md',
        'timeouts.md': 'arquitectura/resilience-patterns.md',
        'retry-patterns.md': 'arquitectura/resilience-patterns.md',
        'graceful-degradation.md': 'arquitectura/resilience-patterns.md',
        'slos-slas.md': 'operabilidad/slos-slas.md',
        'data-ownership.md': 'datos/data-ownership.md',
        'database-per-service.md': 'datos/database-standards.md',
        'data-access-via-apis.md': 'datos/data-access-patterns.md',
        'schema-documentation.md': 'datos/data-governance.md',
        'least-knowledge-principle.md': 'arquitectura/dependency-management.md',
        'migrations.md': 'datos/database-standards.md',
        'schema-validation.md': 'datos/data-validation.md',
        'schema-evolution.md': 'datos/schema-evolution.md',
        'schema-registry.md': 'mensajeria/event-schemas.md',
        'consistency-models.md': 'datos/consistency-models.md',
        'reconciliation.md': 'datos/data-reconciliation.md',
        'conflict-resolution.md': 'datos/conflict-resolution.md',
        'saga-pattern.md': 'arquitectura/saga-pattern.md',
        'consistency-slos.md': 'datos/consistency-slos.md',
    }

    if broken_file in known_mappings:
        mapped_path = known_mappings[broken_file]
        # Calcular ruta relativa desde el archivo de lineamiento
        target_full = workspace_root / 'docs' / 'fundamentos-corporativos' / 'estandares' / mapped_path

        # Calcular cuántos niveles subir desde lineamiento
        # lineamiento está en: docs/fundamentos-corporativos/lineamientos/categoria/archivo.md
        # estandares está en: docs/fundamentos-corporativos/estandares/categoria/archivo.md

        return f"../../estandares/{mapped_path}"

    return ""

def main():
    workspace_root = Path('/mnt/d/dev/work/talma/tlm-doc-architecture')
    lineamientos_dir = workspace_root / 'docs' / 'fundamentos-corporativos' / 'lineamientos'

    # Encontrar todos los archivos markdown
    md_files = sorted(lineamientos_dir.rglob('*.md'))

    results = []
    total_links = 0
    valid_links = 0
    broken_links = 0

    print("=" * 80)
    print("VALIDACIÓN DE ENLACES EN LINEAMIENTOS")
    print("=" * 80)
    print()

    for md_file in md_files:
        if md_file.name == '_category_.json':
            continue

        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()

        links = find_markdown_links(content)

        if not links:
            continue

        file_results = {
            'file': md_file.relative_to(workspace_root),
            'links': [],
            'valid_count': 0,
            'broken_count': 0
        }

        for link_text, link_path in links:
            # Solo analizar enlaces a archivos .md (no URLs externas)
            if link_path.startswith('http://') or link_path.startswith('https://'):
                continue

            total_links += 1
            target_path = resolve_path(md_file, link_path)

            exists = target_path.exists()

            link_info = {
                'text': link_text,
                'path': link_path,
                'exists': exists,
                'suggestion': ''
            }

            if exists:
                valid_links += 1
                file_results['valid_count'] += 1
            else:
                broken_links += 1
                file_results['broken_count'] += 1
                # Buscar sugerencias
                suggestion = suggest_correct_path(link_text, link_path, md_file, workspace_root)
                link_info['suggestion'] = suggestion

            file_results['links'].append(link_info)

        results.append(file_results)

    # Imprimir resultados
    for result in results:
        total_in_file = result['valid_count'] + result['broken_count']
        print(f"ARCHIVO: {result['file']}")
        print(f"ENLACES ENCONTRADOS: {total_in_file}")
        print()

        # Enlaces válidos
        valid_links_list = [l for l in result['links'] if l['exists']]
        if valid_links_list:
            print(f"✅ VÁLIDOS ({len(valid_links_list)} enlaces):")
            for link in valid_links_list:
                print(f"- [{link['text']}]({link['path']}) → archivo existe")
            print()

        # Enlaces rotos
        broken_links_list = [l for l in result['links'] if not l['exists']]
        if broken_links_list:
            print(f"❌ ROTOS ({len(broken_links_list)} enlaces):")
            for link in broken_links_list:
                print(f"- [{link['text']}]({link['path']}) → NO EXISTE")
                if link['suggestion']:
                    print(f"  SUGERENCIA: Cambiar a {link['suggestion']}")
            print()

        print("---")
        print()

    # Resumen final
    print("=" * 80)
    print("RESUMEN")
    print("=" * 80)
    print(f"- Total archivos revisados: {len(results)}")
    print(f"- Total enlaces encontrados: {total_links}")
    print(f"- Enlaces válidos: {valid_links}")
    print(f"- Enlaces rotos: {broken_links}")
    print()

    # Generar lista de correcciones necesarias
    if broken_links > 0:
        print("=" * 80)
        print("CORRECCIONES NECESARIAS")
        print("=" * 80)
        print()

        for result in results:
            broken_links_list = [l for l in result['links'] if not l['exists']]
            if broken_links_list:
                print(f"\n### {result['file']}")
                for link in broken_links_list:
                    old_string = f"[{link['text']}]({link['path']})"
                    if link['suggestion']:
                        new_string = f"[{link['text']}]({link['suggestion']})"
                        print(f"\noldString: {old_string}")
                        print(f"newString: {new_string}")
                    else:
                        print(f"\nENLACE ROTO SIN SUGERENCIA: {old_string}")

if __name__ == '__main__':
    main()
