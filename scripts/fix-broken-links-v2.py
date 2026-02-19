#!/usr/bin/env python3
"""
Fix broken links - second pass to fix duplicated paths
"""
import re
from pathlib import Path

def fix_links_v2(content, file_path):
    """Fix broken links with duplicated paths"""

    # 1. Fix double slashes and wrong fundamentos paths
    content = content.replace('//fundamentos/lineamientos', '../lineamientos')
    content = content.replace('//fundamentos/principios-de-arquitectura', '../../principios')
    content = content.replace('//decisiones-de-arquitectura/', '/decisiones-de-arquitectura/')
    content = content.replace('//fundamentos/lineamientos/', '../lineamientos/')

    # 2. Fix estandares self-references (from estandares/X to estandares/Y)
    content = content.replace('../estandares/arquitectura/', '../arquitectura/')
    content = content.replace('../estandares/apis/', '../apis/')
    content = content.replace('../estandares/datos/', '../datos/')
    content = content.replace('../estandares/desarrollo/', '../desarrollo/')
    content = content.replace('../estandares/documentacion/', '../documentacion/')
    content = content.replace('../estandares/gobierno/', '../gobierno/')
    content = content.replace('../estandares/infraestructura/', '../infraestructura/')
    content = content.replace('../estandares/mensajeria/', '../mensajeria/')
    content = content.replace('../estandares/observabilidad/', '../observabilidad/')
    content = content.replace('../estandares/operabilidad/', '../operabilidad/')
    content = content.replace('../estandares/seguridad/', '../seguridad/')
    content = content.replace('../estandares/testing/', '../testing/')

    # Same for ./estandares/
    content = content.replace('./estandares/apis', './apis')
    content = content.replace('./estandares/desarrollo', './desarrollo')
    content = content.replace('./estandares/infraestructura', './infraestructura')
    content = content.replace('./estandares/testing', './testing')
    content = content.replace('./estandares/observabilidad', './observabilidad')
    content = content.replace('./estandares/mensajeria', './mensajeria')
    content = content.replace('./estandares/documentacion', './documentacion')
    content = content.replace('./estandares/testing-strategy.md', './testing-strategy.md')

    # 3. Fix wrong paths from README index files
    content = content.replace('/fundamentos//fundamentos/', '/fundamentos/')
    content = content.replace('/docs/fundamentos//fundamentos/', '/fundamentos/')

    # 4. Fix absolute paths that should be relative
    # From decisiones-de-arquitectura/README.md
    if 'decisiones-de-arquitectura/README.md' in str(file_path):
        content = content.replace('/decisiones-de-arquitectura/', './')

    # 5. Fix paths from estandares README
    if 'estandares/README.md' in str(file_path):
        content = content.replace('/fundamentos/lineamientos', '../lineamientos')
        content = content.replace('/fundamentos/principios-de-arquitectura', '../principios')

    # 6. Fix paths from intro.md
    if 'intro.md' in str(file_path):
        content = content.replace('/fundamentos/lineamientos', '/fundamentos/lineamientos')
        content = content.replace('/aplicaciones', '/aplicaciones')
        content = content.replace('/plataforma-corporativa/plataforma-de-integracion', '/plataforma-corporativa/plataforma-de-integracion')

    # 7. Fix paths from estilos-arquitectonicos
    if 'estilos-arquitectonicos' in str(file_path):
        content = content.replace('/fundamentos/principios-de-arquitectura/', '../principios/')
        content = content.replace('/fundamentos/principios-de-arquitectura', '../principios')
        content = content.replace('..//fundamentos/lineamientos/', '../lineamientos/')
        content = content.replace('..//decisiones-de-arquitectura/', '../../../decisiones-de-arquitectura/')

    # 8. Fix paths from lineamientos
    if 'lineamientos' in str(file_path) and 'estandares' not in str(file_path):
        content = content.replace('..//fundamentos/principios-de-arquitectura/', '../../principios/')
        content = content.replace('..//fundamentos/lineamientos/', '../')
        content = content.replace('../..//fundamentos/lineamientos/', '../')
        content = content.replace('../..//decisiones-de-arquitectura/', '../../../../decisiones-de-arquitectura/')
        content = content.replace('..//decisiones-de-arquitectura/', '../../../decisiones-de-arquitectura/')

    # 9. Fix paths from principios
    if 'principios' in str(file_path) and 'lineamientos' not in str(file_path):
        content = content.replace('..//fundamentos/lineamientos/', '../lineamientos/')
        content = content.replace('..//decisiones-de-arquitectura/', '../../../decisiones-de-arquitectura/')

    # 10. Fix specific broken links
    specific_fixes = {
        './adr-023-trivy-checkov-security-scanning.md': '#security-scanning',
        '/fundamentos/estandares/documentacion/architecture-documentation': '/fundamentos/estandares/documentacion/architecture-documentation',
        '/decisiones-de-arquitectura': '/decisiones-de-arquitectura',
        '../../../../decisiones-de-arquitectura#readme': '/decisiones-de-arquitectura',
        './seguridad': '../seguridad',
        './seguridad/secrets-key-management.md': '../seguridad/secrets-key-management.md',
        './seguridad/06-segmentacion-y-aislamiento.md': '../seguridad/06-segmentacion-y-aislamiento.md',
        '..//fundamentos/lineamientos/datos/03-propiedad-de-datos.md': '../datos/01-datos-por-dominio.md',
        '..//fundamentos/lineamientos/arquitectura/08-diseno-orientado-al-dominio.md': '../arquitectura/09-modelado-de-dominio.md',
        '..//fundamentos/lineamientos/arquitectura/12-simplicidad-intencional.md': '../arquitectura/13-simplicidad-intencional.md',
        './06-apis-y-contratos.md': './06-apis-y-contratos.md',
        './04-recuperacion-ante-desastres.md': './04-recuperacion-ante-desastres.md',
        '/fundamentos/estilos-arquitectonicos': '/fundamentos/estilos-arquitectonicos',
        '/fundamentos/principios-de-arquitectura/datos/03-consistencia-contextual.md': '/fundamentos/principios-de-arquitectura',
    }

    for old, new in specific_fixes.items():
        content = content.replace(old, new)

    # 11. Fix ADR links from guias and other places
    content = re.sub(r'/decisiones-de-arquitectura/adr-(\d+)', r'/decisiones-de-arquitectura/adr-\1', content)

    return content

def process_file(file_path):
    """Process a single markdown file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        fixed_content = fix_links_v2(content, file_path)

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
