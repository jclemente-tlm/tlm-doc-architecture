#!/usr/bin/env python3
"""
Script final para corregir todos los enlaces rotos restantes.
"""

import re
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
DOCS_DIR = BASE_DIR / "docs"

def fix_content(content, file_path):
    """Aplica todas las correcciones necesarias."""
    original = content

    # 1. Corregir enlaces absolutos incorrectos
    content = content.replace('/tlm-doc-architecture/decisiones-de-arquitectura', '/docs/decisiones-de-arquitectura')
    content = content.replace('/tlm-doc-architecture/docs/fundamentos-corporativos/principios', '/docs/fundamentos-corporativos/principios')

    # 2. Corregir nombres de archivos incorrectos de principios
    content = content.replace('/principios/02-modularidad-y-bajo-acoplamiento', '/principios/01-modularidad-y-bajo-acoplamiento')
    content = content.replace('/principios/04-seguridad-desde-el-diseno', '/principios/02-seguridad-desde-el-diseno')
    content = content.replace('/principios/datos/03-consistencia-contextual', '/principios/01-modularidad-y-bajo-acoplamiento')
    content = content.replace('/principios/01-mantenibilidad-y-extensibilidad', '/principios/04-mantenibilidad-y-extensibilidad')
    content = content.replace('../../principios/01-mantenibilidad-y-extensibilidad', '../../principios/04-mantenibilidad-y-extensibilidad')
    content = content.replace('/principios/03-resiliencia-y-tolerancia-a-fallos', '/principios/03-resiliencia-y-tolerancia-a-fallos')  # Este está correcto

    # 3. Corregir enlaces relativos sin ./  en lineamientos
    if 'lineamientos/' in str(file_path):
        # Enlaces a otros archivos en el mismo directorio sin ./
        content = re.sub(r'\((\d{2}-[a-z-]+)\)', r'(./\1)', content)
        # Corregir doble ./
        content = content.replace('(././', '(./')

    # 4. Corregir enlaces en estandares/README.md
    if 'estandares/README.md' in str(file_path):
        content = content.replace('(./apis)', '(./apis)')
        content = content.replace('(./desarrollo)', '(./desarrollo)')
        content = content.replace('(./infraestructura)', '(./infraestructura)')
        content = content.replace('(./testing)', '(./testing)')
        content = content.replace('(./observabilidad)', '(./observabilidad)')
        content = content.replace('(./mensajeria)', '(./mensajeria)')
        content = content.replace('(./documentacion)', '(./documentacion)')

    # 5. Corregir enlaces en estilos-arquitectonicos
    if 'estilos-arquitectonicos' in str(file_path):
        # Corregir enlaces a archivos sin subdirectorio
        content = content.replace('](microservicios)', '](./microservicios)')
        content = content.replace('](eventos)', '](./eventos)')
        content = content.replace('](cloud-native)', '](./cloud-native)')
        content = content.replace('](monolito-modular)', '](./monolito-modular)')
        # Corregir un lineamiento que se quedó con nombre incorrecto
        content = content.replace('../lineamientos/arquitectura/08-diseno-orientado-al-dominio', '../lineamientos/arquitectura/09-modelado-de-dominio')
        content = content.replace('../lineamientos/arquitectura/09-autonomia-de-servicios', '../lineamientos/arquitectura/10-autonomia-de-servicios')
        content = content.replace('../lineamientos/arquitectura/10-arquitectura-limpia', '../lineamientos/arquitectura/11-arquitectura-limpia')
        content = content.replace('../lineamientos/arquitectura/11-arquitectura-evolutiva', '../lineamientos/arquitectura/12-arquitectura-evolutiva')
        content = content.replace('../lineamientos/arquitectura/12-simplicidad-intencional', '../lineamientos/arquitectura/13-simplicidad-intencional')
        content = content.replace('../lineamientos/arquitectura/05-observabilidad', '../lineamientos/arquitectura/06-observabilidad')

    # 6. Corregir enlaces en lineamientos/README.md
    if 'lineamientos/README.md' in str(file_path):
        content = content.replace('(./arquitectura)', '(./arquitectura)')
        content = content.replace('(./datos)', '(./datos)')
        content = content.replace('(./desarrollo)', '(./desarrollo)')
        content = content.replace('(./gobierno)', '(./gobierno)')
        content = content.replace('(./operabilidad)', '(./operabilidad)')
        content = content.replace('(./seguridad)', '(./seguridad)')

    # 7. Corregir números de lineamientos que cambiaron
    content = content.replace('lineamientos/arquitectura/06-apis-y-contratos', 'lineamientos/arquitectura/07-apis-y-contratos')
    content = content.replace('lineamientos/arquitectura/10-autonomia-de-servicios', 'lineamientos/arquitectura/10-autonomia-de-servicios')  # Ya está correcto
    content = content.replace('lineamientos/operabilidad/04-recuperacion-ante-desastres', 'lineamientos/operabilidad/04-disaster-recovery')
    content = content.replace('./04-recuperacion-ante-desastres', './04-disaster-recovery')

    # 8. Corregir lineamiento de infraestructura que no existe
    content = content.replace('../../lineamientos/infraestructura', '../../lineamientos/operabilidad/02-infraestructura-como-codigo')
    content = content.replace('../lineamientos/infraestructura', '../lineamientos/operabilidad/02-infraestructura-como-codigo')

    # 9. Corregir lineamientos de operabilidad que tienen nombre incorrecto
    content = content.replace('lineamientos/operabilidad/03-infrastructura-como-codigo', 'lineamientos/operabilidad/02-infraestructura-como-codigo')

    return content

def process_file(file_path):
    """Procesa un archivo."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        original = content
        content = fix_content(content, file_path)

        if content != original:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        return False
    except Exception as e:
        print(f"Error: {file_path}: {e}")
        return False

def main():
    print("Aplicando correcciones finales...\n")

    modified = []
    for md_file in DOCS_DIR.rglob("*.md"):
        if process_file(md_file):
            modified.append(md_file)
            print(f"✓ {md_file.relative_to(BASE_DIR)}")

    print(f"\n{'='*60}")
    print(f"Archivos modificados: {len(modified)}")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
