#!/bin/bash
# Script para exportar todos los bloques Mermaid de archivos .md a imágenes SVG
# Requiere: @mermaid-js/mermaid-cli instalado globalmente (npm install -g @mermaid-js/mermaid-cli)

set -e

WORKDIR="$(dirname "$0")/.."
STATIC_IMG="$WORKDIR/static/img/mermaid"
mkdir -p "$STATIC_IMG"

# Busca todos los archivos .md en docs y extrae bloques mermaid
find "$WORKDIR/docs" -name '*.md' | while read -r file; do
  # Extrae bloques mermaid y los exporta
  awk '/```mermaid/{flag=1;next}/```/{flag=0}flag' "$file" | \
  awk 'BEGIN{n=0} {if($0!=""){print $0 > "/tmp/mermaid_block_"n".mmd"} else {n++}}'
  for mmd in /tmp/mermaid_block_*.mmd; do
    [ -f "$mmd" ] || continue
    base="$(basename "$file" .md)_$(basename "$mmd" .mmd)"
    mmdc -i "$mmd" -o "$STATIC_IMG/$base.svg" || echo "Error exportando $mmd"
    rm "$mmd"
  done
done

echo "Exportación Mermaid finalizada. Imágenes en $STATIC_IMG"
