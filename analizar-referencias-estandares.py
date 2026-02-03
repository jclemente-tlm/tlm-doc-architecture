#!/usr/bin/env python3
import os
from pathlib import Path

# Directorio base
base_dir = "/mnt/d/dev/work/talma/tlm-doc-architecture"
estandares_dir = f"{base_dir}/docs/fundamentos-corporativos/estandares"

# Obtener lista de archivos de estándares
estandares = []
for root, dirs, files in os.walk(estandares_dir):
    for file in files:
        if file.endswith('.md'):
            if file not in ['README.md', 'VALIDACION-COHERENCIA.md']:
                if not file.startswith('ANALISIS-'):
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, estandares_dir)
                    estandares.append(rel_path)

print(f"Total de estándares: {len(estandares)}")

# Directorios donde buscar referencias
search_dirs = [
    f"{base_dir}/docs/fundamentos-corporativos/lineamientos",
    f"{base_dir}/docs/decisiones-de-arquitectura",
    f"{base_dir}/docs",
]

# Crear un set para rastrear qué estándares tienen referencias
referenciados = set()

# Buscar referencias en todos los archivos .md
for search_dir in search_dirs:
    if not os.path.exists(search_dir):
        continue

    for root, dirs, files in os.walk(search_dir):
        for file in files:
            if file.endswith('.md'):
                file_path = os.path.join(root, file)

                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                        # Para cada estándar, buscar si está referenciado
                        for estandar in estandares:
                            # nombre del archivo sin extensión
                            estandar_name = os.path.splitext(os.path.basename(estandar))[0]

                            # Buscar el nombre del archivo en el contenido
                            if estandar_name in content:
                                referenciados.add(estandar)
                except Exception as e:
                    pass

# Calcular no referenciados
no_referenciados = [std for std in estandares if std not in referenciados]
print(f"Estándares NO referenciados: {len(no_referenciados)}")
print("\nEstándares NO referenciados:")
for std in sorted(no_referenciados):
    print(f"  - {std}")
