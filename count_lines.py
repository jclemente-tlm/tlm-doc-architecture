#!/usr/bin/env python3
import os
import sys

base_path = "docs/fundamentos-corporativos/estandares"
files_data = []

for root, dirs, files in os.walk(base_path):
    for file in files:
        if file.endswith('.md') and file != 'README.md':
            filepath = os.path.join(root, file)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    line_count = sum(1 for _ in f)
                    rel_path = os.path.relpath(filepath, base_path)
                    files_data.append((line_count, rel_path))
            except Exception as e:
                print(f"Error reading {filepath}: {e}", file=sys.stderr)

files_data.sort(reverse=True)

# Escribir a archivo en el workspace
output_file = "line_counts_result.txt"
with open(output_file, 'w') as out:
    for count, path in files_data:
        out.write(f"{count} ./{path}\n")
    out.write(f"\nTotal: {len(files_data)} archivos\n")

print(f"Resultados guardados en {output_file}")

# También imprimir a stdout
for count, path in files_data:
    print(f"{count} ./{path}")
print(f"\nTotal: {len(files_data)} archivos")
