#!/bin/bash
# Script para validar referencias a estándares en lineamientos
# Uso: ./scripts/validar-referencias-estandares.sh

set -euo pipefail

LINEAMIENTOS_DIR="docs/fundamentos-corporativos/lineamientos"
ESTANDARES_DIR="docs/fundamentos-corporativos/estandares"
TEMP_FILE=$(mktemp)
ERROR_COUNT=0

echo "🔍 Validando referencias a estándares en lineamientos..."
echo ""

# Encontrar todas las referencias a ../../estandares/
find "$LINEAMIENTOS_DIR" -name "*.md" ! -name "_*" | while read -r lineamiento; do
    # Extraer referencias
    grep -oP '\[([^\]]+)\]\(\K\.\./\.\./estandares/[^)#]+' "$lineamiento" 2>/dev/null | while read -r ref; do
        # Convertir ruta relativa a absoluta
        estandar_path="${ref#../../estandares/}"
        full_path="$ESTANDARES_DIR/$estandar_path"

        # Verificar si existe
        if [ ! -f "$full_path" ]; then
            echo "❌ ROTO: $lineamiento"
            echo "   → Referencia: ../../estandares/$estandar_path"
            echo "   → Faltan: $full_path"
            echo ""
            ((ERROR_COUNT++)) || true
        fi
    done
done > "$TEMP_FILE"

# Mostrar resultados
if [ -s "$TEMP_FILE" ]; then
    cat "$TEMP_FILE"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "❌ Total de enlaces rotos: $ERROR_COUNT"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    rm "$TEMP_FILE"
    exit 1
else
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "✅ Todas las referencias son válidas"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    rm "$TEMP_FILE"
    exit 0
fi
