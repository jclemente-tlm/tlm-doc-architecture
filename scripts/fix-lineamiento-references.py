#!/usr/bin/env python3
"""
Script completo para corregir todos los nombres incorrectos de enlaces a lineamientos.
"""

import re
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
DOCS_DIR = BASE_DIR / "docs"

# Mapeo completo de nombres incorrectos a correctos
CORRECTIONS = {
    # Arquitectura - Los nombres están correctos en su mayoría, solo ajustar los números que cambiaron
    'lineamientos/arquitectura/06-apis-y-contratos': 'lineamientos/arquitectura/07-apis-y-contratos',
    'lineamientos/arquitectura/07-comunicacion-asincrona-y-eventos': 'lineamientos/arquitectura/08-comunicacion-asincrona-y-eventos',

    # Desarrollo
    'lineamientos/desarrollo/01-calidad-de-codigo': 'lineamientos/desarrollo/01-calidad-codigo',
    'lineamientos/desarrollo/03-configuracion-externa': 'lineamientos/operabilidad/03-configuracion-entornos',
    'lineamientos/desarrollo/05-control-de-versiones': 'lineamientos/desarrollo/04-control-versiones',

    # Datos
    'lineamientos/datos/02-consistencia-eventual': 'lineamientos/datos/02-consistencia-y-sincronizacion',

    # Gobierno - Los nombres están completamente incorrectos
    'lineamientos/gobierno/01-gobierno-arquitectura': 'lineamientos/gobierno/01-decisiones-arquitectonicas',
    'lineamientos/gobierno/02-documentacion-arquitectonica': 'lineamientos/gobierno/02-revisiones-arquitectonicas',

    # Operabilidad
    'lineamientos/operabilidad/04-recuperacion-ante-desastres': 'lineamientos/operabilidad/04-disaster-recovery',
}

def fix_links(content):
    """Aplica todas las correcciones."""
    for incorrect, correct in CORRECTIONS.items():
        # Reemplazar en enlaces Markdown
        content = content.replace(incorrect, correct)
        # También manejar enlaces con anclas
        pattern = re.escape(incorrect)
        content = re.sub(f'{pattern}(#[^)]*)?', lambda m: f'{correct}{m.group(1) if m.group(1) else ""}', content)
    return content

def process_file(file_path):
    """Procesa un archivo."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        original = content
        content = fix_links(content)

        if content != original:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        return False
    except Exception as e:
        print(f"Error: {file_path}: {e}")
        return False

def main():
    print("Corrigiendo nombres de lineamientos...\n")

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
