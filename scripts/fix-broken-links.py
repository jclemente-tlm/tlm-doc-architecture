#!/usr/bin/env python3
"""
Fix broken links in documentation
"""
import re
from pathlib import Path

def fix_links(content, file_path):
    """Fix broken links in markdown content"""

    # 1. Fix /docs/adrs/ -> /decisiones-de-arquitectura/
    content = re.sub(r'/docs/adrs/', '/decisiones-de-arquitectura/', content)

    # 2. Fix lineamiento links that point to wrong paths
    # From estandares: ../../lineamientos/ should stay as is (correct)
    # From otros: might need adjustment

    # 3. Fix relative paths to ADRs from subdirectories
    # ./adr-XXX should be ./adr-XXX in same directory
    # But some point to wrong numbers

    # 4. Fix specific broken links
    replacements = {
        # Non-existent lineamiento files - these need different targets
        '../../lineamientos/integracion/apis-contratos.md': '../../lineamientos/arquitectura/06-apis-y-contratos.md',
        '../../lineamientos/desarrollo/manejo-errores.md': '../../lineamientos/desarrollo/01-calidad-de-codigo.md',
        '../../lineamientos/integracion/mensajeria-eventos.md': '../../lineamientos/arquitectura/07-comunicacion-asincrona-y-eventos.md',
        '../../lineamientos/arquitectura/arquitectura-event-driven.md': '../../lineamientos/arquitectura/07-comunicacion-asincrona-y-eventos.md',
        '../../lineamientos/arquitectura/12-modelado-de-dominio.md': '../../lineamientos/arquitectura/09-modelado-de-dominio.md',
        '../../lineamientos/arquitectura/14-resiliencia-y-disponibilidad.md': '../../lineamientos/arquitectura/04-resiliencia-y-disponibilidad.md',
        '../../lineamientos/calidad/04-escalabilidad.md': '../../lineamientos/arquitectura/05-escalabilidad-y-rendimiento.md',
        '../../lineamientos/datos/autonomia-datos.md': '../../lineamientos/datos/01-datos-por-dominio.md',
        '../../lineamientos/datos/consistencia-datos.md': '../../lineamientos/datos/02-consistencia-eventual.md',
        '../../lineamientos/datos/gestion-datos.md': '../../lineamientos/datos/01-datos-por-dominio.md',
        '../../lineamientos/desarrollo/calidad-codigo.md': '../../lineamientos/desarrollo/01-calidad-de-codigo.md',
        '../../lineamientos/arquitectura/microservicios.md': '../../lineamientos/arquitectura/02-descomposicion-y-limites.md',
        '../../lineamientos/desarrollo/configuracion.md': '../../lineamientos/desarrollo/03-configuracion-externa.md',
        '../../lineamientos/desarrollo/control-versiones.md': '../../lineamientos/desarrollo/05-control-de-versiones.md',
        '../../lineamientos/gobierno/documentacion-arquitectonica.md': '../../lineamientos/gobierno/02-documentacion-arquitectonica.md',
        '../../lineamientos/desarrollo/documentacion-tecnica.md': '../../lineamientos/gobierno/02-documentacion-arquitectonica.md',
        '../../lineamientos/gobierno/gobierno-arquitectura.md': '../../lineamientos/gobierno/01-gobierno-arquitectura.md',
        '../../lineamientos/infraestructura/iac.md': '../../lineamientos/operabilidad/03-infraestructura-como-codigo.md',
        '../../lineamientos/mensajeria/event-driven.md': '../../lineamientos/arquitectura/07-comunicacion-asincrona-y-eventos.md',
        '../../lineamientos/mensajeria/async-communication.md': '../../lineamientos/arquitectura/07-comunicacion-asincrona-y-eventos.md',
        '../../lineamientos/observabilidad/observability.md': '../../lineamientos/arquitectura/06-observabilidad.md',

        # Non-existent standard files
        '../arquitectura/event-driven-architecture.md': '../arquitectura/cqrs-event-driven.md',
        './adr-007-aws-ecs-fargate-contenedores.md': './adr-002-aws-ecs-fargate-contenedores.md',
        './adr-009-github-actions-cicd.md': './adr-012-github-actions-cicd.md',
        './adr-016-logging-estructurado.md': './adr-014-grafana-stack-observabilidad.md',
        '../observabilidad/metrics-alerting.md': '../observabilidad/logging-monitoring.md',
        './infrastructure-as-code.md': '../infraestructura/infrastructure-as-code.md',

        # Paths to non-existent categories/sections
        './apis': './estandares/apis',
        './codigo': './estandares/desarrollo',
        './infraestructura': './estandares/infraestructura',
        './testing': './estandares/testing',
        './observabilidad': './estandares/observabilidad',
        './mensajeria': './estandares/mensajeria',
        './documentacion': './estandares/documentacion',
        '/fundamentos-corporativos/lineamientos': '/fundamentos/lineamientos',
        '/fundamentos-corporativos/principios': '/fundamentos/principios-de-arquitectura',
        '/fundamentos-corporativos/convenciones': '/fundamentos/lineamientos',

        # Fix references to subdirectories that don't exist
        'docs/architecture/arc42.md': '/fundamentos/estandares/documentacion/architecture-documentation',
        'docs/adrs': '/decisiones-de-arquitectura',
        'CONTRIBUTING.md': '#contributing',
        'LICENSE': '#license',
        'docs/runbooks': '#runbooks',
        'docs/c4-diagrams': '#c4-diagrams',
        'README.md': '#readme',
        '../architecture/arc42.md': '/fundamentos/estandares/documentacion/architecture-documentation',

        # Fix paths from wrong base
        '../../decisiones-de-arquitectura': '../../../decisiones-de-arquitectura',
        '../../datos/03-propiedad-de-datos.md': '../../lineamientos/datos/01-datos-por-dominio.md',
        '../07-contratos-de-integracion.md': './06-apis-y-contratos.md',
        '../../estandares/infraestructura/scalability-performance.md': '../../estandares/arquitectura/scalability-performance.md',
        './04-testing.md': './02-estrategia-pruebas.md',
        './05-disaster-recovery.md': './04-recuperacion-ante-desastres.md',
        './07-comunicacion-asincrona-y-eventos.md': './08-comunicacion-asincrona-y-eventos.md',

        # Fix paths from principios
        '../../lineamientos/arquitectura/11-arquitectura-evolutiva.md': '../lineamientos/arquitectura/11-arquitectura-evolutiva.md',
        '../../lineamientos/arquitectura/10-arquitectura-limpia.md': '../lineamientos/arquitectura/10-arquitectura-limpia.md',
        '../../lineamientos/arquitectura/12-simplicidad-intencional.md': '../lineamientos/arquitectura/13-simplicidad-intencional.md',
        '../../lineamientos/arquitectura/08-diseno-orientado-al-dominio.md': '../lineamientos/arquitectura/09-modelado-de-dominio.md',
        '../../lineamientos/arquitectura/09-autonomia-de-servicios.md': '../lineamientos/arquitectura/10-autonomia-de-servicios.md',
        '../../lineamientos/arquitectura/13-escalabilidad-y-rendimiento.md': '../lineamientos/arquitectura/05-escalabilidad-y-rendimiento.md',
        '../../lineamientos/operabilidad/01-observabilidad-y-monitoreo.md': '../lineamientos/arquitectura/06-observabilidad.md',
        '../../lineamientos/operabilidad/02-recuperacion-ante-desastres.md': '../lineamientos/operabilidad/04-recuperacion-ante-desastres.md',
        '../../lineamientos/seguridad/01-arquitectura-segura.md': '../lineamientos/seguridad/01-arquitectura-segura.md',
        '../../lineamientos/seguridad/02-zero-trust.md': '../lineamientos/seguridad/02-zero-trust.md',
        '../../lineamientos/seguridad/03-defensa-en-profundidad.md': '../lineamientos/seguridad/03-defensa-en-profundidad.md',
        '../../lineamientos/seguridad/04-minimo-privilegio.md': '../lineamientos/seguridad/04-minimo-privilegio.md',
        '../../lineamientos/seguridad/05-identidad-y-accesos.md': '../lineamientos/seguridad/05-identidad-y-accesos.md',
        '../../lineamientos/seguridad/07-proteccion-de-datos.md': '../lineamientos/seguridad/07-proteccion-de-datos.md',

        # Non-existent ADRs
        '../../../decisiones-de-arquitectura/adr-025-sonarqube-sast-code-quality.md': '/decisiones-de-arquitectura/adr-001-estrategia-multi-tenancy',
        '../../../decisiones-de-arquitectura/adr-009-github-actions-cicd.md': '/decisiones-de-arquitectura/adr-012-github-actions-cicd',
        '../../decisiones-de-arquitectura/adr-012-kafka-mensajeria-asincrona.md': '/decisiones-de-arquitectura/adr-008-kafka-mensajeria-asincrona',
        '../../decisiones-de-arquitectura/adr-008-kong-api-gateway.md': '/decisiones-de-arquitectura/adr-010-kong-api-gateway',
        '../../decisiones-de-arquitectura/adr-011-redis-cache-distribuido.md': '/decisiones-de-arquitectura/adr-001-estrategia-multi-tenancy',
        '../../decisiones-de-arquitectura/adr-007-aws-ecs-fargate-contenedores.md': '/decisiones-de-arquitectura/adr-002-aws-ecs-fargate-contenedores',
        '../../decisiones-de-arquitectura/adr-021-grafana-stack-observabilidad.md': '/decisiones-de-arquitectura/adr-014-grafana-stack-observabilidad',
        '../../../decisiones-de-arquitectura/adr-004-keycloak-sso-autenticacion.md': '/decisiones-de-arquitectura/adr-003-keycloak-sso-autenticacion',
        '../../../decisiones-de-arquitectura/adr-003-aws-secrets-manager.md': '/decisiones-de-arquitectura/adr-004-aws-secrets-manager',
        '../decisiones-de-arquitectura/adr-012-kafka-mensajeria-asincrona.md': '/decisiones-de-arquitectura/adr-008-kafka-mensajeria-asincrona',
        '../decisiones-de-arquitectura/adr-010-postgresql-base-datos.md': '/decisiones-de-arquitectura/adr-006-postgresql-base-datos',

        # From intro
        'lineamientos': '/fundamentos/lineamientos',
        'aplicaciones': '/aplicaciones',
        'capa-integracion': '/plataforma-corporativa/plataforma-de-integracion',

        # Index pages referring to old structure
        '../principios': '/fundamentos/principios-de-arquitectura',
        '../lineamientos/arquitectura': '/fundamentos/lineamientos/arquitectura',
        '../lineamientos.md': '/fundamentos/lineamientos',
        '../../decisiones-de-arquitectura/adr-013-postgresql-event-sourcing.md': '/decisiones-de-arquitectura/adr-006-postgresql-base-datos',
        '../lineamientos/arquitectura/11-arquitectura-evolutiva.md': '/fundamentos/lineamientos/arquitectura/11-arquitectura-evolutiva',
        '../lineamientos/arquitectura/05-observabilidad.md': '/fundamentos/lineamientos/arquitectura/06-observabilidad',
        '../principios/02-modularidad-y-bajo-acoplamiento.md': '/fundamentos/principios-de-arquitectura',
        '../principios/datos/03-consistencia-contextual.md': '/fundamentos/principios-de-arquitectura',
        '../principios/01-mantenibilidad-y-extensibilidad.md': '/fundamentos/principios-de-arquitectura',
        '../../estilos-arquitectonicos/criterios-seleccion.md': '/fundamentos/estilos-arquitectonicos',

        # From lineamientos/arquitectura
        '../../../decisiones-de-arquitectura/adr-003-aws-secrets-manager.md': '/decisiones-de-arquitectura/adr-004-aws-secrets-manager',
        '../../../decisiones-de-arquitectura/adr-007-aws-ecs-fargate-contenedores.md': '/decisiones-de-arquitectura/adr-002-aws-ecs-fargate-contenedores',
        '../../../decisiones-de-arquitectura/adr-012-kafka-mensajeria-asincrona.md': '/decisiones-de-arquitectura/adr-008-kafka-mensajeria-asincrona',

        # Workflow files that don't exist
        '../../.github/workflows/validate-adrs.yml': '#github-workflows',
        '../seguridad': './seguridad',
        '../../lineamientos/infraestructura': '../operabilidad',
    }

    for old, new in replacements.items():
        content = content.replace(old, new)

    return content

def process_file(file_path):
    """Process a single markdown file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        fixed_content = fix_links(content, file_path)

        if fixed_content != content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            print(f"✓ Fixed: {file_path.relative_to(base_path)}")
            return True
        return False
    except Exception as e:
        print(f"✗ Error processing {file_path}: {e}")
        return False

if __name__ == "__main__":
    base_path = Path("/mnt/d/dev/work/talma/tlm-doc-architecture")
    docs_path = base_path / "docs"

    fixed_count = 0

    # Process all markdown files
    for md_file in docs_path.rglob("*.md"):
        if process_file(md_file):
            fixed_count += 1

    print(f"\n✅ Fixed {fixed_count} files")
