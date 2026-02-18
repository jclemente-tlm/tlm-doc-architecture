#!/usr/bin/env python3
"""
Extrae todos los enlaces a estándares desde los lineamientos
"""

import os
import re
from pathlib import Path
from collections import defaultdict

def extract_standard_links(lineamientos_dir):
    """Extrae todos los enlaces a estándares"""
    pattern = re.compile(r'\]\(\.\.\/\.\.\/estandares\/([^)]+)\)')

    all_links = []
    links_by_file = defaultdict(list)

    for md_file in Path(lineamientos_dir).rglob("*.md"):
        if md_file.name == "README.md":
            continue

        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
            matches = pattern.findall(content)

            for match in matches:
                all_links.append(match)
                links_by_file[str(md_file.relative_to(lineamientos_dir))].append(match)

    return all_links, links_by_file

def main():
    lineamientos_dir = "docs/fundamentos-corporativos/lineamientos"

    all_links, links_by_file = extract_standard_links(lineamientos_dir)

    # Enlaces únicos ordenados
    unique_links = sorted(set(all_links))

    print("=" * 80)
    print(f"TOTAL DE ENLACES ÚNICOS: {len(unique_links)}")
    print(f"TOTAL DE REFERENCIAS: {len(all_links)}")
    print("=" * 80)
    print()

    # Agrupar por categoría
    by_category = defaultdict(list)
    for link in unique_links:
        category = link.split('/')[0]
        filename = link.split('/')[-1]
        by_category[category].append(filename)

    for category in sorted(by_category.keys()):
        print(f"\n### {category.upper()} ({len(by_category[category])} archivos)")
        print("-" * 80)
        for filename in sorted(by_category[category]):
            print(f"  {filename}")

    # Guardar salida completa
    output_file = "analisis-enlaces-estandares.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write(f"ANÁLISIS DE ENLACES A ESTÁNDARES EN LINEAMIENTOS\n")
        f.write("=" * 80 + "\n\n")

        f.write(f"Total de enlaces únicos: {len(unique_links)}\n")
        f.write(f"Total de referencias: {len(all_links)}\n\n")

        for category in sorted(by_category.keys()):
            f.write(f"\n### {category.upper()} ({len(by_category[category])} archivos)\n")
            f.write("-" * 80 + "\n")
            for filename in sorted(by_category[category]):
                full_path = f"{category}/{filename}"
                count = all_links.count(full_path)
                f.write(f"  {filename} (referenciado {count} veces)\n")

        f.write("\n\n" + "=" * 80 + "\n")
        f.write("TODOS LOS ENLACES ÚNICOS (FORMATO COMPLETO)\n")
        f.write("=" * 80 + "\n")
        for link in unique_links:
            count = all_links.count(link)
            f.write(f"{link} ({count} refs)\n")

    print(f"\n\nAnálisis completo guardado en: {output_file}")

if __name__ == "__main__":
    main()
