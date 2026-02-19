#!/usr/bin/env python3
"""
Script definitivo para corregir TODOS los enlaces rotos en la documentación.
"""

import re
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
DOCS_DIR = BASE_DIR / "docs"


def fix_all_links(content, file_path):
    """Aplica TODAS las correcciones necesarias."""

    # 1. CORREGIR URLS ABSOLUTAS INCORRECTAS - PRIORIDAD MÁXIMA
    content = content.replace('/tlm-doc-architecture/decisiones-de-arquitectura/', '/docs/decisiones-de-arquitectura/')
    content = content.replace('/tlm-doc-architecture/decisiones-de-arquitectura', '/docs/decisiones-de-arquitectura')
    content = content.replace('/tlm-doc-architecture/docs/fundamentos-corporativos/principios', '/docs/fundamentos-corporativos/principios')
    content = content.replace('/tlm-doc-architecture/docs/aplicaciones', '/docs/aplicaciones')

    # 2. CORREGIR ESTRUCTURA DE ESTANDARES/README.md
    if str(file_path).endswith('estandares/README.md'):
        # Los subdirectorios de estandares necesitan la carpeta intermedia
        content = content.replace('](./apis)', '](./estandares/apis)')
        content = content.replace('](./desarrollo)', '](./estandares/desarrollo)')
        content = content.replace('](./infraestructura)', '](./estandares/infraestructura)')
        content = content.replace('](./testing)', '](./estandares/testing)')
        content = content.replace('](./observabilidad)', '](./estandares/observabilidad)')
        content = content.replace('](./mensajeria)', '](./estandares/mensajeria)')
        content = content.replace('](./documentacion)', '](./estandares/documentacion)')

        # Corregir enlaces a principios y lineamientos
        content = content.replace('](../principios)', '](../../fundamentos-corporativos/principios)')
        content = content.replace('](../lineamientos)', '](../../fundamentos-corporativos/lineamientos)')

    # 3. CORREGIR ESTRUCTURA DE LINEAMIENTOS/README.md
    if str(file_path).endswith('lineamientos/README.md'):
        # Los subdirectorios necesitan apuntar a la carpeta lineamientos correcta
        content = content.replace('](./arquitectura)', '](./lineamientos/arquitectura)')
        content = content.replace('](./datos)', '](./lineamientos/datos)')
        content = content.replace('](./desarrollo)', '](./lineamientos/desarrollo)')
        content = content.replace('](./gobierno)', '](./lineamientos/gobierno)')
        content = content.replace('](./operabilidad)', '](./lineamientos/operabilidad)')
        content = content.replace('](./seguridad)', '](./lineamientos/seguridad)')

    # 4. CORREGIR ESTILOS-ARQUITECTONICOS/README.md
    if 'estilos-arquitectonicos' in str(file_path) and str(file_path).endswith('README.md'):
        content = content.replace('](microservicios)', '](./estilos-arquitectonicos/microservicios)')
        content = content.replace('](eventos)', '](./estilos-arquitectonicos/eventos)')
        content = content.replace('](cloud-native)', '](./estilos-arquitectonicos/cloud-native)')
        content = content.replace('](monolito-modular)', '](./estilos-arquitectonicos/monolito-modular)')
        content = content.replace('](../lineamientos/arquitectura)', '](../../fundamentos-corporativos/lineamientos/arquitectura)')
        content = content.replace('](../lineamientos)', '](../../fundamentos-corporativos/lineamientos)')

    # 5. CORREGIR CONFIG-MANAGEMENT QUE APUNTA A INFRAESTRUCTURA-COMO-CODIGO INCORRECTO
    if 'configuration-management' in str(file_path):
        content = content.replace('lineamientos/operabilidad/03-infraestructura-como-codigo',
                                 'lineamientos/operabilidad/02-infraestructura-como-codigo')

    return content


def process_file(file_path):
    """Procesa un archivo."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        original = content
        content = fix_all_links(content, file_path)

        if content != original:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        return False
    except Exception as e:
        print(f"Error: {file_path}: {e}")
        return False


def main():
    print("Aplicando correcciones definitivas...\n")

    modified = []
    for md_file in DOCS_DIR.rglob("*.md"):
        if process_file(md_file):
            modified.append(md_file)
            print(f"✓ {md_file.relative_to(BASE_DIR)}")

    print(f"\n{'='*60}")
    print(f"Archivos modificados: {len(modified)}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
