#!/bin/bash

# Script de validación de estructura de estándares y convenciones
# Verifica que todos los documentos tengan las secciones obligatorias

echo "🔍 Validando estructura de estándares y convenciones..."
echo ""

errors=0
warnings=0

# Colores para output
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# Directorios
STANDARDS_DIR="docs/fundamentos-corporativos/estandares"
CONVENTIONS_DIR="docs/fundamentos-corporativos/convenciones"

# Secciones obligatorias para ESTÁNDARES
declare -a STANDARD_SECTIONS=(
  "## 1. Propósito"
  "## 2. Alcance"
  "## 3. Tecnologías y Herramientas Obligatorias"
  "## 9. Referencias"
)

# Secciones recomendadas para ESTÁNDARES
declare -a STANDARD_RECOMMENDED=(
  "## 7. NO Hacer"
  "## 8. Validación y Cumplimiento"
)

# Secciones obligatorias para CONVENCIONES
declare -a CONVENTION_SECTIONS=(
  "## 1. Principio"
  "## 2. Reglas"
  "## 6. Referencias"
)

# Función para validar un archivo estándar
validate_standard() {
  local file=$1
  local file_errors=0
  
  echo "📄 Validando: $file"
  
  # Verificar secciones obligatorias
  for section in "${STANDARD_SECTIONS[@]}"; do
    if ! grep -q "^$section" "$file"; then
      echo -e "  ${RED}❌ Falta sección obligatoria: $section${NC}"
      ((file_errors++))
      ((errors++))
    fi
  done
  
  # Verificar secciones recomendadas
  for section in "${STANDARD_RECOMMENDED[@]}"; do
    if ! grep -q "^$section" "$file"; then
      echo -e "  ${YELLOW}⚠️  Falta sección recomendada: $section${NC}"
      ((warnings++))
    fi
  done
  
  # Verificar frontmatter YAML
  if ! head -n 1 "$file" | grep -q "^---$"; then
    echo -e "  ${RED}❌ Falta frontmatter YAML${NC}"
    ((file_errors++))
    ((errors++))
  fi
  
  if [ $file_errors -eq 0 ]; then
    echo -e "  ${GREEN}✅ Estructura correcta${NC}"
  fi
  
  echo ""
}

# Función para validar un archivo convención
validate_convention() {
  local file=$1
  local file_errors=0
  
  echo "📄 Validando: $file"
  
  # Verificar secciones obligatorias
  for section in "${CONVENTION_SECTIONS[@]}"; do
    if ! grep -q "^$section" "$file"; then
      echo -e "  ${RED}❌ Falta sección obligatoria: $section${NC}"
      ((file_errors++))
      ((errors++))
    fi
  done
  
  # Verificar frontmatter YAML
  if ! head -n 1 "$file" | grep -q "^---$"; then
    echo -e "  ${RED}❌ Falta frontmatter YAML${NC}"
    ((file_errors++))
    ((errors++))
  fi
  
  if [ $file_errors -eq 0 ]; then
    echo -e "  ${GREEN}✅ Estructura correcta${NC}"
  fi
  
  echo ""
}

# Validar estándares
echo "=================================="
echo "VALIDANDO ESTÁNDARES"
echo "=================================="
echo ""

# Buscar todos los archivos .md en estandares (excluyendo README)
while IFS= read -r -d '' file; do
  if [[ ! "$file" =~ README.md$ ]] && [[ ! "$file" =~ VALIDACION ]] && [[ ! "$file" =~ PROPUESTA ]]; then
    validate_standard "$file"
  fi
done < <(find "$STANDARDS_DIR" -name "*.md" -type f -print0)

# Validar convenciones
echo "=================================="
echo "VALIDANDO CONVENCIONES"
echo "=================================="
echo ""

while IFS= read -r -d '' file; do
  if [[ ! "$file" =~ README.md$ ]] && [[ ! "$file" =~ VALIDACION ]] && [[ ! "$file" =~ PROPUESTA ]]; then
    validate_convention "$file"
  fi
done < <(find "$CONVENTIONS_DIR" -name "*.md" -type f -print0)

# Resumen final
echo "=================================="
echo "RESUMEN"
echo "=================================="
echo ""

if [ $errors -eq 0 ]; then
  echo -e "${GREEN}✅ Todos los documentos tienen la estructura correcta${NC}"
  if [ $warnings -gt 0 ]; then
    echo -e "${YELLOW}⚠️  Se encontraron $warnings advertencias${NC}"
  fi
  exit 0
else
  echo -e "${RED}❌ Se encontraron $errors errores${NC}"
  if [ $warnings -gt 0 ]; then
    echo -e "${YELLOW}⚠️  Se encontraron $warnings advertencias${NC}"
  fi
  exit 1
fi
