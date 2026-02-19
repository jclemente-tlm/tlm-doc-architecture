#!/usr/bin/env python3
"""
Script para generar mapeo completo de referencias atómicas a secciones consolidadas.
Extrae todas las secciones de nivel 2 (## 1., ## 2., etc.) de archivos consolidados.
"""

import os
import re
import unicodedata
from pathlib import Path
from typing import List, Tuple

def slugify(text: str) -> str:
    """
    Convierte un encabezado de Markdown a un anchor slug compatible con Docusaurus.

    Reglas Docusaurus (github-slugger):
    - Convertir caracteres Unicode a ASCII (quitar acentos)
    - Convertir a minúsculas
    - Reemplazar espacios por guiones (-)
    - Mantener números y letras
    - Eliminar paréntesis, comas y la mayoría de caracteres especiales
    - & se convierte en - (ampersand)
    - / se convierte en -
    - Múltiples guiones se reducen a uno solo
    """
    # Remover el ## al inicio
    text = re.sub(r'^##\s+', '', text).strip()

    # Normalizar Unicode: quitar acentos
    text = unicodedata.normalize('NFD', text)
    text = text.encode('ascii', 'ignore').decode('utf-8')

    # Convertir a minúsculas
    text = text.lower()

    # Reemplazar caracteres especiales por guiones o eliminarlos
    text = text.replace('&', '-')  # & → -
    text = text.replace('/', '-')  # / → -

    # Eliminar paréntesis (sin su contenido, solo los símbolos)
    text = text.replace('(', '')
    text = text.replace(')', '')

    # Eliminar comas
    text = text.replace(',', '')

    # Reemplazar espacios por guiones
    text = text.replace(' ', '-')

    # Mantener solo letras, números y guiones
    text = re.sub(r'[^a-z0-9\-]', '', text)

    # Limpiar guiones múltiples
    text = re.sub(r'-+', '-', text)

    # Remover guiones al inicio y final
    text = text.strip('-')

    return text

def extract_sections(file_path: Path) -> List[Tuple[str, str]]:
    """
    Extrae todas las secciones de nivel 2 (## 1., ## 2., etc.) de un archivo.

    Returns:
        Lista de tuplas (texto_seccion, anchor)
    """
    sections = []

    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            # Buscar líneas que empiecen con ## seguido de un número y punto
            match = re.match(r'^##\s+(\d+\..*)', line.strip())
            if match:
                section_text = match.group(1).strip()
                full_header = f"## {section_text}"
                anchor = slugify(full_header)
                sections.append((section_text, anchor))

    return sections

def get_category_from_path(file_path: Path, base_path: Path) -> str:
    """Extrae la categoría (nombre de la carpeta) del path del archivo."""
    relative_path = file_path.relative_to(base_path)
    return relative_path.parts[0] if len(relative_path.parts) > 1 else ""

def main():
    # Directorio base de estándares
    base_dir = Path(__file__).parent / "docs" / "fundamentos-corporativos" / "estandares"

    # Carpetas a procesar
    categories = [
        "apis", "arquitectura", "datos", "desarrollo", "documentacion",
        "gobierno", "infraestructura", "mensajeria", "observabilidad",
        "operabilidad", "seguridad", "testing"
    ]

    # Resultados
    results = []

    # Procesar cada categoría
    for category in categories:
        category_path = base_dir / category

        if not category_path.exists():
            print(f"⚠️  Categoría no encontrada: {category}")
            continue

        # Buscar todos los archivos .md (excepto _category_.json)
        md_files = sorted(category_path.glob("*.md"))

        for md_file in md_files:
            if md_file.name.startswith("_"):
                continue

            sections = extract_sections(md_file)

            for section_text, anchor in sections:
                results.append({
                    "category": category,
                    "file": md_file.name,
                    "section": section_text,
                    "anchor": f"#{anchor}"
                })

            if sections:
                print(f"✅ {category}/{md_file.name}: {len(sections)} secciones")
            else:
                print(f"⚠️  {category}/{md_file.name}: sin secciones de nivel 2")

    # Generar tabla Markdown
    output_file = Path(__file__).parent / "MAPEO-REFERENCIAS-ATOMICAS.md"

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# Mapeo de Referencias Atómicas a Secciones Consolidadas\n\n")
        f.write("Este documento mapea todas las referencias atómicas (secciones de nivel 2) ")
        f.write("a sus archivos consolidados correspondientes.\n\n")
        f.write(f"**Total de secciones:** {len(results)}\n\n")
        f.write("---\n\n")

        # Tabla principal
        f.write("| Categoría | Archivo Consolidado | Sección | Anchor |\n")
        f.write("|-----------|---------------------|---------|--------|\n")

        for item in results:
            f.write(f"| {item['category']} | {item['file']} | {item['section']} | {item['anchor']} |\n")

        f.write("\n---\n\n")

        # Resumen por categoría
        f.write("## Resumen por Categoría\n\n")

        category_counts = {}
        for item in results:
            cat = item['category']
            category_counts[cat] = category_counts.get(cat, 0) + 1

        f.write("| Categoría | Total Secciones |\n")
        f.write("|-----------|----------------|\n")

        for cat in sorted(category_counts.keys()):
            f.write(f"| {cat} | {category_counts[cat]} |\n")

        f.write(f"\n**Total:** {len(results)} secciones\n")

    print(f"\n✅ Mapeo generado en: {output_file}")
    print(f"📊 Total de secciones procesadas: {len(results)}")

if __name__ == "__main__":
    main()
