#!/usr/bin/env python3
"""
Script para corregir enlaces rotos en la documentación de Docusaurus.
Elimina extensiones .md y corrige rutas incorrectas.
"""

import os
import re
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
DOCS_DIR = BASE_DIR / "docs"


def remove_md_extensions(content):
    """Elimina extensiones .md de enlaces Markdown."""
    # Patrón para enlaces Markdown [texto](ruta.md) o [texto](ruta.md#anchor)
    pattern = r'\[([^\]]+)\]\(([^)]+)\.md(#[^)]*?)?\)'

    def replacement(match):
        text = match.group(1)
        path = match.group(2)
        anchor = match.group(3) or ''
        return f'[{text}]({path}{anchor})'

    return re.sub(pattern, replacement, content)


def fix_absolute_paths(content):
    """Corrige rutas absolutas incorrectas."""
    replacements = {
        '/tlm-doc-architecture/fundamentos-corporativos/principios': '/docs/fundamentos-corporativos/principios',
        '/tlm-doc-architecture/fundamentos-corporativos/': '/docs/fundamentos-corporativos/',
        '/tlm-doc-architecture/decisiones-de-arquitectura': '/docs/decisiones-de-arquitectura',
        '/tlm-doc-architecture/fundamentos/': '/docs/fundamentos-corporativos/',
        '/tlm-doc-architecture/aplicaciones': '/docs/aplicaciones',
        '/tlm-doc-architecture/plataforma-corporativa/': '/docs/plataforma-corporativa/',
        '/fundamentos-corporativos/principios': '/docs/fundamentos-corporativos/principios',
        '/fundamentos/estandares/': '/docs/fundamentos-corporativos/estandares/',
        '/fundamentos/lineamientos': '/docs/fundamentos-corporativos/lineamientos',
        '/fundamentos/estilos-arquitectonicos': '/docs/fundamentos-corporativos/estilos-arquitectonicos',
    }

    for old, new in replacements.items():
        content = content.replace(old, new)

    return content


def fix_broken_relative_paths(content, file_path):
    """Corrige rutas relativas específicas según el contexto del archivo."""

    # Si el archivo está en la carpeta lineamientos, corregir referencias a estandares
    if 'lineamientos' in str(file_path):
        content = content.replace('../../estandares/principios/', '../../principios/')
        content = content.replace('../../datos/', '../../estandares/datos/')
        content = content.replace('../../arquitectura/', '../../estandares/arquitectura/')
        content = content.replace('../../desarrollo/', '../../estandares/desarrollo/')
        content = content.replace('../../documentacion/', '../../estandares/documentacion/')
        content = content.replace('../../gobierno/', '../../estandares/gobierno/')
        content = content.replace('../../testing/', '../../estandares/testing/')
        content = content.replace('../../operabilidad/', '../../estandares/operabilidad/')
        content = content.replace('../../infraestructura/', '../../estandares/infraestructura/')
        content = content.replace('../.../seguridad/', '../../estandares/seguridad/')
        content = content.replace('../../lineamientos/infraestructura', '../../lineamientos/operabilidad/03-infraestructura-como-codigo')
        content = content.replace('../..//decisiones-de-arquitectura', '/docs/decisiones-de-arquitectura')

    # Corregir referencias específicas a principios con nombres incorrectos
    if 'principios' in str(file_path) or 'estilos-arquitectonicos' in str(file_path):
        content = content.replace(
            '/tlm-doc-architecture/fundamentos-corporativos/principios/02-modularidad-y-bajo-acoplamiento',
            '/docs/fundamentos-corporativos/principios/01-modularidad-y-bajo-acoplamiento'
        )
        content = content.replace(
            '/tlm-doc-architecture/fundamentos-corporativos/principios/datos/03-consistencia-contextual',
            '/docs/fundamentos-corporativos/principios/01-modularidad-y-bajo-acoplamiento'
        )
        content = content.replace(
            '../../principios/04-seguridad-desde-el-diseno',
            '../../principios/02-seguridad-desde-el-diseno'
        )

    # Corregir enlaces malformados
    content = re.sub(r'\]\(link\)', '](#)', content)

    return content


def process_file(file_path):
    """Procesa un archivo Markdown y corrige sus enlaces."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content

        # Aplicar correcciones
        content = remove_md_extensions(content)
        content = fix_absolute_paths(content)
        content = fix_broken_relative_paths(content, file_path)

        # Si hubo cambios, guardar el archivo
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True

        return False

    except Exception as e:
        print(f"✗ Error procesando {file_path}: {e}")
        return False


def main():
    """Función principal."""
    print("Corrigiendo enlaces rotos en la documentación...\n")

    modified_files = []
    total_files = 0

    # Procesar todos los archivos .md en docs/
    for md_file in DOCS_DIR.rglob("*.md"):
        total_files += 1
        if process_file(md_file):
            modified_files.append(md_file)
            print(f"✓ Corregido: {md_file.relative_to(BASE_DIR)}")

    print(f"\n{'='*60}")
    print(f"Resumen:")
    print(f"  Archivos procesados: {total_files}")
    print(f"  Archivos modificados: {len(modified_files)}")
    print(f"{'='*60}\n")

    if modified_files:
        print("✓ Corrección completada exitosamente.")
        print("\nEjecuta 'npm run build' para verificar que no quedan enlaces rotos.")
    else:
        print("No se requirieron correcciones.")


if __name__ == "__main__":
    main()
