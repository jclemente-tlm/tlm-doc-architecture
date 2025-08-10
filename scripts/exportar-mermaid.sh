#!/bin/bash
# Script para exportar todos los bloques Mermaid de archivos .md a imágenes SVG
# Requiere: @mermaid-js/mermaid-cli instalado globalmente (npm install -g @mermaid-js/mermaid-cli)

set -e

WORKDIR="$(dirname "$0")/.."
STATIC_IMG="$WORKDIR/static/img/mermaid"
mkdir -p "$STATIC_IMG"

# Limpia archivos temporales previos
rm -f /tmp/mermaid_block_*.mmd

# Busca todos los archivos .md en docs y extrae bloques mermaid
find "$WORKDIR/docs" -name '*.md' | while read -r file; do
  awk '
    BEGIN {block=0; n=0; filename="";}
    /```mermaid/ {block=1; filename="/tmp/mermaid_block_" n ".mmd"; next}
    /```/ {if(block){block=0; n++} else {print $0} next}
    {if(block) print $0 >> filename}
  ' "$file"
  for mmd in /tmp/mermaid_block_*.mmd; do
    [ -f "$mmd" ] || continue
    base="$(basename "$file" .md)_$(basename "$mmd" .mmd)"
    mmdc -i "$mmd" -o "$STATIC_IMG/$base.svg" || echo "Error exportando $mmd"
    rm "$mmd"
  done
  # Limpia archivos temporales para el siguiente archivo
  rm -f /tmp/mermaid_block_*.mmd

done

echo "Exportación Mermaid finalizada. Imágenes en $STATIC_IMG"
