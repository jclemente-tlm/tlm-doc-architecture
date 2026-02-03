#!/usr/bin/env python3
import os
import sys

base_dir = "/mnt/d/dev/work/talma/tlm-doc-architecture"
estandares_dir = os.path.join(base_dir, "docs/fundamentos-corporativos/estandares")
docs_dir = os.path.join(base_dir, "docs")

# Listar estándares
estandares = []
for root, dirs, files in os.walk(estandares_dir):
    for f in files:
        if f.endswith('.md') and f not in ['README.md', 'VALIDACION-COHERENCIA.md'] and not f.startswith('ANALISIS-'):
            full = os.path.join(root, f)
            rel = os.path.relpath(full, estandares_dir)
            estandares.append((rel, f[:-3]))  # (path, nombre sin .md)

print(f"Total de estándares: {len(estandares)}")

# Buscar referencias
referenciados = set()
for root, dirs, files in os.walk(docs_dir):
    for f in files:
        if not f.endswith('.md'):
            continue

        fpath = os.path.join(root, f)
        try:
            with open(fpath, 'r', encoding='utf-8', errors='ignore') as file:
                contenido = file.read()
                for rel_path, nombre in estandares:
                    if nombre in contenido:
                        referenciados.add(rel_path)
        except:
            pass

no_refs = [e[0] for e in estandares if e[0] not in referenciados]

print(f"Estándares referenciados: {len(referenciados)}")
print(f"Estándares NO referenciados: {len(no_refs)}")
print("\nEstándares NO referenciados:")
for nr in sorted(no_refs):
    print(f"  - {nr}")
