#!/usr/bin/env python3
"""
Fix broken links - third pass to fix malformed paths
"""
import re
from pathlib import Path

def fix_links_v3(content, file_path):
    """Fix malformed paths with extra dots"""

    # 1. Fix paths with 4 consecutive dots
    content = content.replace('../..../lineamientos', '../../lineamientos')
    content = content.replace('..../lineamientos', '../lineamientos')
    content = content.replace('..../../principios', '../../principios')

    # 2. Fix paths with 3 dots (security references from lineamientos)
    content = content.replace('../.../seguridad/', '../../estandares/seguridad/')
    content = content.replace('../.../seguridad/', '../../estandares/seguridad/')
    content = content.replace('.../seguridad/', '../seguridad/')

    # 3. Fix absolute paths missing corporativos
    content = content.replace('/fundamentos../lineamientos', '/fundamentos-corporativos/lineamientos')
    content = content.replace('/docs../principios', '/fundamentos-corporativos/principios')
    content = content.replace('/docs/fundamentos../', '/fundamentos-corporativos/')

    # 4. Fix paths from README that should be relative
    if 'decisiones-de-arquitectura/README.md' in str(file_path):
        # Keep ./adr- as is (correct for README in same directory)
        pass

    # 5. Fix paths from estandares README
    if 'estandares/README.md' in str(file_path):
        content = content.replace('/fundamentos/lineamientos', '../lineamientos')
        content = content.replace('/fundamentos/principios', '../principios')
        content = content.replace('/docs/fundamentos-corporativos/', '../')

    # 6. Fix category links in estandares README
    if 'estandares/README.md' in str(file_path):
        content = content.replace('./apis', './estandares/apis')
        content = content.replace('./desarrollo', './estandares/desarrollo')
        content = content.replace('./infraestructura', './estandares/infraestructura')
        content = content.replace('./testing', './estandares/testing')
        content = content.replace('./observabilidad', './estandares/observabilidad')
        content = content.replace('./mensajeria', './estandares/mensajeria')
        content = content.replace('./documentacion', './estandares/documentacion')

    # 7. Fix paths from lineamientos to estandares (should be ../../estandares/)
    if '/lineamientos/' in str(file_path) and 'arquitectura' in str(file_path):
        # From lineamientos/arquitectura to estandares
        content = re.sub(r'(\.\./\.\./)([a-z]+)/([\w-]+\.md)', r'\1estandares/\2/\3', content)

    # 8. Fix paths from lineamientos to other lineamientos
    if '/lineamientos/' in str(file_path):
        # Fix ...... patterns
        content = content.replace('../..../lineamientos', '../')
        content = content.replace('..../../principios', '../../principios')

    # 9. Fix paths from principios
    if '/principios/' in str(file_path):
        content = content.replace('..../lineamientos', '../lineamientos')
        content = content.replace('../decisiones-de-arquitectura', '../../../decisiones-de-arquitectura')

    # 10. Fix paths from estilos-arquitectonicos
    if 'estilos-arquitectonicos' in str(file_path):
        content = content.replace('..../lineamientos', '../lineamientos')
        content = content.replace('../principios', '/fundamentos-corporativos/principios')

    # 11. Fix absolute paths referenced from various files
    content = content.replace('/tlm-doc-architecture/fundamentos/', '/fundamentos-corporativos/')
    content = content.replace('/tlm-doc-architecture/docs..', '/fundamentos-corporativos')
    content = content.replace('/docs/docs/', '/docs/')

    # 12. Fix specific broken absolute paths
    content = content.replace('/tlm-doc-architecture/docs/adr-', '/decisiones-de-arquitectura/adr-')
    content = content.replace('/tlm-doc-architecture/docs/fundamentos-corporativos/decisiones-de-arquitectura', '/decisiones-de-arquitectura')
    content = content.replace('/tlm-doc-architecture/docs/fundamentos-corporativos/principios', '/fundamentos-corporativos/principios')
    content = content.replace('/tlm-doc-architecture/docs/fundamentos-corporativos/lineamientos', '/fundamentos-corporativos/lineamientos')

    # 13. Fix paths from lineamientos to decisiones-de-arquitectura
    if '/lineamientos/' in str(file_path):
        content = content.replace('../../decisiones-de-arquitectura', '/decisiones-de-arquitectura')
        content = content.replace('../decisiones-de-arquitectura', '/decisiones-de-arquitectura')

    # 14. Fix intro.md paths
    if 'intro.md' in str(file_path):
        content = content.replace('/tlm-doc-architecture/fundamentos/', '/fundamentos-corporativos/')
        content = content.replace('/tlm-doc-architecture/aplicaciones', '/aplicaciones')
        content = content.replace('/tlm-doc-architecture/plataforma-corporativa/', '/plataforma-corporativa/')

    # 15. Fix paths from principios with extra dots
    content = content.replace('../../../decisiones-de-arquitectura', '/decisiones-de-arquitectura')

    return content

def process_file(file_path):
    """Process a single markdown file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        fixed_content = fix_links_v3(content, file_path)

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
