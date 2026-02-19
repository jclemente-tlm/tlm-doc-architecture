#!/usr/bin/env python3
"""
Script para corregir caracteres especiales < y > que causan problemas en MDX
"""
import re
from pathlib import Path

def fix_mdx_special_chars(content: str) -> tuple[str, int]:
    """Reemplaza < y > problemáticos con entidades HTML"""
    original = content
    replacements = 0

    # Patrones a reemplazar (fuera de bloques de código)
    patterns = [
        # En tablas y texto: <número seguido de unidad o letra
        (r'([^`])<(\d+(?:\.\d+)?(?:s|ms|h|K|M|G|\+)?(?:/\w+)?)', r'\1&lt;\2'),
        # Result<T> y similares genéricos
        (r'Result<T>', r'Result&lt;T&gt;'),
        # <número servicios/ejecutores/etc
        (r'<(\d+) (servicios|ejecutores|executors|agents|containers|workflows|pipelines)', r'&lt;\1 \2'),
        # >= seguido de número en texto (no en código)
        (r'([^`])>=(\d+)', r'\1&gt;=\2'),
        # >número seguido de K/M/G
        (r'>(\d+[KMG])', r'&gt;\1'),
    ]

    # Aplicar reemplazos solo fuera de bloques de código
    lines = content.split('\n')
    result_lines = []
    in_code_block = False
    in_inline_code = False

    for line in lines:
        # Detectar inicio/fin de bloques de código
        if line.strip().startswith('```') or line.strip().startswith('~~~'):
            in_code_block = not in_code_block
            result_lines.append(line)
            continue

        # Si estamos en bloque de código, no modificar
        if in_code_block:
            result_lines.append(line)
            continue

        # Procesar línea fuera de bloques de código
        original_line = line

        for pattern, replacement in patterns:
            line = re.sub(pattern, replacement, line)

        if line != original_line:
            replacements += 1

        result_lines.append(line)

    return '\n'.join(result_lines), replacements

def process_file(filepath: Path) -> tuple[bool, int]:
    """Procesa un archivo individual"""
    try:
        content = filepath.read_text(encoding='utf-8')
        fixed_content, replacements = fix_mdx_special_chars(content)

        if replacements > 0:
            filepath.write_text(fixed_content, encoding='utf-8')
            return True, replacements
        return False, 0
    except Exception as e:
        print(f"❌ Error procesando {filepath}: {e}")
        return False, 0

def main():
    """Procesa todos los archivos markdown"""
    base_path = Path(__file__).parent.parent

    # Archivos a procesar
    patterns_to_fix = [
        'docs/decisiones-de-arquitectura/adr-*.md',
        'docs/fundamentos-corporativos/estandares/**/*.md',
        'docs/guias-arquitectura/*.md',
    ]

    total_files = 0
    total_replacements = 0
    modified_files = []

    print("🔧 Corrigiendo caracteres especiales MDX...")

    for pattern in patterns_to_fix:
        for filepath in base_path.glob(pattern):
            modified, count = process_file(filepath)
            if modified:
                total_files += 1
                total_replacements += count
                modified_files.append(filepath.relative_to(base_path))
                print(f"✓ {filepath.relative_to(base_path)}: {count} líneas")

    print(f"\n✅ Completado:")
    print(f"   Archivos modificados: {total_files}")
    print(f"   Total líneas corregidas: {total_replacements}")

    if modified_files and total_files <= 20:
        print(f"\n📝 Archivos modificados:")
        for f in modified_files:
            print(f"   - {f}")

if __name__ == '__main__':
    main()
