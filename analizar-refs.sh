#!/bin/bash

cd /mnt/d/dev/work/talma/tlm-doc-architecture

echo "=== ANÁLISIS DE REFERENCIAS DE ESTÁNDARES ==="
echo ""

# Obtener lista de estándares
estandares=$(find docs/fundamentos-corporativos/estandares -type f -name "*.md" | \
  grep -v README.md | \
  grep -v VALIDACION-COHERENCIA.md | \
  grep -v "ANALISIS-")

total=$(echo "$estandares" | wc -l)
echo "Total de estándares: $total"

# Contador de referenciados y no referenciados
referenciados=0
no_referenciados=0
lista_no_ref=""

# Para cada estándar, buscar referencias
while IFS= read -r estandar_path; do
  # Obtener nombre del archivo sin extensión
  estandar_name=$(basename "$estandar_path" .md)

  # Buscar en docs/ excluyendo el propio archivo
  refs=$(grep -r "$estandar_name" docs/ 2>/dev/null | grep -v "$estandar_path" | wc -l)

  if [ "$refs" -gt 0 ]; then
    referenciados=$((referenciados + 1))
  else
    no_referenciados=$((no_referenciados + 1))
    # Guardar path relativo
    rel_path=$(echo "$estandar_path" | sed 's|docs/fundamentos-corporativos/estandares/||')
    lista_no_ref="${lista_no_ref}  - ${rel_path}\n"
  fi
done <<< "$estandares"

echo "Estándares referenciados: $referenciados"
echo "Estándares NO referenciados: $no_referenciados"
echo ""
echo "Estándares NO referenciados:"
echo -e "$lista_no_ref"
