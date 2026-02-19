#!/usr/bin/env python3
"""
Script para corregir nombres de archivos incorrectos en enlaces a lineamientos.
"""

import os
import re
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
DOCS_DIR = BASE_DIR / "docs"


# Mapeo de nombres incorrectos a nombres correctos de archivos
LINEAMIENTO_CORRECTIONS = {
    # Arquitectura
    '06-apis-y-contratos': '07-apis-y-contratos',
    '07-comunicacion-asincrona-y-eventos': '08-comunicacion-asincrona-y-eventos',

    # Desarrollo
    '01-calidad-de-codigo': '01-calidad-codigo',
    '03-configuracion-externa': '03-configuracion-entornos',  # Ajustar si es incorrecto
    '05-control-de-versiones': '04-control-versiones',

    # Datos
    '02-consistencia-eventual': '02-consistencia-y-sincronizacion',

    # Gobierno
    '01-gobierno-arquitectura': '01-decisiones-arquitectonicas',  # Verificar si es correcto
    '02-documentacion-arquitectonica': '03-documentacion-tecnica',  # Ajustar según corresponda

    # Operabilidad
    '04-recuperacion-ante-desastres': '04-disaster-recovery',
}


def fix_lineamiento_names(content):
    """Corrige los nombres de archivos de lineamientos."""
    for incorrect, correct in LINEAMIENTO_CORRECTIONS.items():
        content = content.replace(f'/{incorrect}', f'/{correct}')
        content = content.replace(f'/{incorrect}#', f'/{correct}#')
    return content


def process_file(file_path):
    """Procesa un archivo y corrige los nombres."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content
        content = fix_lineamiento_names(content)

        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        return False
    except Exception as e:
        print(f"Error procesando {file_path}: {e}")
        return False


def main():
    print("Corrigiendo nombres de archivos de lineamientos...\n")

    modified = []
    for md_file in DOCS_DIR.rglob("*.md"):
        if process_file(md_file):
            modified.append(md_file)
            print(f"✓ {md_file.relative_to(BASE_DIR)}")

    print(f"\nArchivos modificados: {len(modified)}")


if __name__ == "__main__":
    main()
