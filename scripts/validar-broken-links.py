#!/usr/bin/env python3
"""
Validación final: Verificar que no existan broken links en lineamientos.
"""

import re
from pathlib import Path

lineamientos_path = Path('docs/fundamentos-corporativos/lineamientos')
estandares_base = Path('docs/fundamentos-corporativos/estandares')
pattern = r'\]\(\.\./\.\./estandares/(.*?)\.md\)'

print("🔍 Validando integridad de referencias...\n")

# Obtener todas las referencias
referencias = {}
for md_file in lineamientos_path.rglob('*.md'):
    content = md_file.read_text()
    refs = re.findall(pattern, content)
    if refs:
        referencias[str(md_file.relative_to(lineamientos_path))] = refs

# Validar existencia
total_refs = 0
broken_links = []

for lineamiento, refs in referencias.items():
    for ref in refs:
        total_refs += 1
        archivo = estandares_base / f'{ref}.md'
        if not archivo.exists():
            broken_links.append({
                'lineamiento': lineamiento,
                'referencia': ref,
                'path_esperado': str(archivo)
            })

# Reportar resultados
print(f"📊 Total referencias únicas: {len(set(r for refs in referencias.values() for r in refs))}")
print(f"📊 Total referencias (con repeticiones): {total_refs}")
print(f"📂 Archivos físicos: {len([f for f in estandares_base.rglob('*.md') if f.is_file()])}")

if broken_links:
    print(f"\n❌ BROKEN LINKS ENCONTRADOS: {len(broken_links)}\n")
    for bl in broken_links[:20]:
        print(f"  ⚠️  {bl['lineamiento']} → {bl['referencia']}")
    if len(broken_links) > 20:
        print(f"\n  ... y {len(broken_links) - 20} más")
    exit(1)
else:
    print(f"\n✅ ÉXITO: CERO BROKEN LINKS")
    print(f"✅ Todas las referencias apuntan a archivos existentes")
    exit(0)
