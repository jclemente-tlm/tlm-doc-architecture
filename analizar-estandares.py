#!/usr/bin/env python3
"""
Analiza todos los lineamientos y extrae estándares obligatorios
para detectar duplicaciones, ambigüedades y validar contra industria.
"""

import re
import json
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Tuple, Set

# Definición de categorías conocidas
CATEGORIAS = {
    'arquitectura': ['arquitectura', 'architecture', 'bounded-contexts', 'dependency', 'single-responsibility',
                     'stateless', 'circuit-breaker', 'timeout', 'retry', 'degradation', 'saga'],
    'datos': ['datos', 'data', 'database', 'schema', 'consistency', 'reconciliation', 'conflict'],
    'seguridad': ['seguridad', 'security', 'cifrado', 'encryption', 'kms', 'threat', 'vulnerability',
                  'sso', 'mfa', 'privilegio', 'tenant', 'incident'],
    'apis': ['apis', 'api', 'rest', 'openapi', 'swagger', 'versionado', 'rate-limiting', 'error-handling',
             'contract', 'deprecacion', 'portal'],
    'mensajeria': ['mensajeria', 'messaging', 'eventos', 'events', 'dlq', 'idempotencia', 'asyncapi',
                   'avro', 'topologia'],
    'observabilidad': ['observabilidad', 'observability', 'logging', 'monitoreo', 'metricas', 'tracing',
                       'correlation', 'health-check'],
    'operabilidad': ['operabilidad', 'operability', 'cicd', 'iac', 'terraform', 'testing', 'cobertura',
                     'code-review', 'paridad', 'contenedor'],
    'infraestructura': ['infraestructura', 'infrastructure', 'configuracion', 'secrets', 'kms', 'cost',
                        'rightsizing', 'tagging'],
    'documentacion': ['documentacion', 'documentation', 'adr', 'architecture-review', 'component'],
    'gobierno': ['gobierno', 'governance', 'compliance', 'review', 'exception', 'retrospective'],
    'testing': ['testing', 'test', 'prueba', 'quality', 'cobertura', 'coverage']
}

# Framework de industria y sus prácticas
FRAMEWORKS_INDUSTRIA = {
    'AWS Well-Architected': [
        'circuit-breaker', 'retry', 'timeout', 'health-check', 'observability', 'logging',
        'monitoring', 'tracing', 'resilience', 'graceful-degradation', 'stateless',
        'horizontal-scaling', 'cost-optimization', 'tagging', 'rightsizing'
    ],
    '12-Factor App': [
        'configuracion-externalizada', 'stateless', 'backing-services', 'graceful-shutdown',
        'port-binding', 'logs-estructurados', 'disposability'
    ],
    'OWASP ASVS': [
        'cifrado-transito', 'cifrado-reposo', 'mfa', 'minimo-privilegio', 'gestion-secretos',
        'modelado-amenazas', 'vulnerability-scanning', 'security-by-design'
    ],
    'Microsoft REST API Guidelines': [
        'rest-conventions', 'versionado', 'error-handling', 'rate-limiting', 'paginacion',
        'openapi'
    ],
    'Google SRE Book': [
        'slos-slas', 'monitoring', 'alerting', 'incident-response', 'postmortem',
        'error-budgets', 'toil-reduction', 'automation'
    ],
    'NIST Cybersecurity Framework': [
        'threat-detection', 'incident-response', 'vulnerability-management', 'risk-acceptance',
        'security-intelligence', 'access-control'
    ],
    'OpenAPI Specification': [
        'openapi', 'swagger', 'contract-validation', 'schema-validation', 'api-portal'
    ],
    'AsyncAPI': [
        'asyncapi', 'schemas-eventos', 'eventos-vs-comandos', 'topologia-eventos'
    ],
    'Event Sourcing / CQRS': [
        'event-sourcing', 'saga', 'eventos-inmutables', 'consistency-eventual'
    ],
    'Domain-Driven Design': [
        'bounded-contexts', 'database-per-service', 'data-ownership', 'api-driven-data-access'
    ]
}


def extraer_estandares_de_archivo(ruta: Path) -> List[Dict]:
    """Extrae todos los estándares de un archivo de lineamiento."""
    contenido = ruta.read_text(encoding='utf-8')

    # Buscar la sección de Estándares Obligatorios
    patron = r'## Estándares Obligatorios\s*\n(.*?)(?=\n##|\Z)'
    match = re.search(patron, contenido, re.DOTALL)

    if not match:
        return []

    seccion_estandares = match.group(1)

    # Extraer enlaces markdown: [texto](ruta)
    patron_enlaces = r'\[([^\]]+)\]\(([^\)]+)\)'
    estandares = []

    for match in re.finditer(patron_enlaces, seccion_estandares):
        nombre = match.group(1).strip()
        ruta_estandar = match.group(2).strip()

        estandares.append({
            'nombre': nombre,
            'ruta': ruta_estandar,
            'lineamiento': ruta.stem,
            'categoria_lineamiento': ruta.parent.name
        })

    return estandares


def categorizar_estandar(ruta: str) -> str:
    """Determina la categoría de un estándar basado en su ruta."""
    ruta_lower = ruta.lower()

    for categoria, palabras_clave in CATEGORIAS.items():
        for palabra in palabras_clave:
            if palabra in ruta_lower:
                return categoria

    # Fallback: usar la carpeta padre si está en la ruta
    partes = ruta.split('/')
    for parte in partes:
        if parte in CATEGORIAS:
            return parte

    return 'sin-clasificar'


def validar_contra_industria(nombre_estandar: str, ruta: str) -> Tuple[str, List[str]]:
    """
    Valida si un estándar está alineado con frameworks de industria.
    Retorna: (status, [frameworks que lo soportan])
    """
    nombre_lower = nombre_estandar.lower()
    ruta_lower = ruta.lower()

    frameworks_encontrados = []

    for framework, practicas in FRAMEWORKS_INDUSTRIA.items():
        for practica in practicas:
            if practica.lower() in nombre_lower or practica.lower() in ruta_lower:
                frameworks_encontrados.append(framework)
                break

    if len(frameworks_encontrados) >= 2:
        return '✅', frameworks_encontrados
    elif len(frameworks_encontrados) == 1:
        return '⚠️', frameworks_encontrados
    else:
        return '❌', []


def detectar_ambiguedades(nombre: str) -> List[str]:
    """Detecta si un nombre es ambiguo o poco descriptivo."""
    problemas = []

    nombres_genericos = [
        'best-practices', 'guidelines', 'standards', 'configuration',
        'setup', 'config', 'general', 'common', 'utils', 'helpers'
    ]

    for generico in nombres_genericos:
        if generico in nombre.lower():
            problemas.append(f"Nombre genérico: contiene '{generico}'")

    if len(nombre.split()) > 8:
        problemas.append("Nombre excesivamente largo")

    if nombre.endswith('.md'):
        problemas.append("Incluye extensión .md en el nombre")

    return problemas


def detectar_similitud(nombre1: str, nombre2: str) -> float:
    """Calcula similitud básica entre dos nombres."""
    palabras1 = set(nombre1.lower().split())
    palabras2 = set(nombre2.lower().split())

    if not palabras1 or not palabras2:
        return 0.0

    interseccion = len(palabras1.intersection(palabras2))
    union = len(palabras1.union(palabras2))

    return interseccion / union if union > 0 else 0.0


def main():
    # Directorio base
    base_dir = Path('/mnt/d/dev/work/talma/tlm-doc-architecture/docs/fundamentos-corporativos/lineamientos')

    # Recopilar todos los estándares
    todos_estandares = []
    estandares_por_lineamiento = defaultdict(list)

    for archivo in base_dir.rglob('*.md'):
        # Ignorar archivos de implementación
        if 'guias-implementacion' in str(archivo):
            continue

        estandares = extraer_estandares_de_archivo(archivo)
        todos_estandares.extend(estandares)

        if estandares:
            estandares_por_lineamiento[archivo.stem] = len(estandares)

    print(f"📊 ANÁLISIS DE ESTÁNDARES OBLIGATORIOS")
    print(f"=" * 80)
    print(f"\n✅ Total de lineamientos analizados: {len(estandares_por_lineamiento)}")
    print(f"📋 Total de referencias a estándares: {len(todos_estandares)}")

    # 1. LISTA COMPLETA DE ESTÁNDARES ÚNICOS
    print(f"\n{'=' * 80}")
    print("1. INVENTARIO DE ESTÁNDARES ÚNICOS (AGRUPADOS POR CATEGORÍA)")
    print(f"{'=' * 80}\n")

    estandares_unicos = {}
    for est in todos_estandares:
        key = est['ruta']
        if key not in estandares_unicos:
            estandares_unicos[key] = {
                'nombre': est['nombre'],
                'ruta': est['ruta'],
                'categoria': categorizar_estandar(est['ruta']),
                'lineamientos': []
            }
        estandares_unicos[key]['lineamientos'].append(est['lineamiento'])

    # Agrupar por categoría
    por_categoria = defaultdict(list)
    for ruta, datos in estandares_unicos.items():
        por_categoria[datos['categoria']].append(datos)

    for categoria in sorted(por_categoria.keys()):
        print(f"\n### {categoria.upper()} ({len(por_categoria[categoria])} estándares)")
        print("-" * 80)
        for est in sorted(por_categoria[categoria], key=lambda x: x['nombre']):
            refs = len(est['lineamientos'])
            print(f"  • {est['nombre']}")
            print(f"    Ruta: {est['ruta']}")
            print(f"    Referencias: {refs} lineamiento(s): {', '.join(sorted(set(est['lineamientos'])))}")

    # 2. DUPLICACIONES/SOLAPAMIENTOS
    print(f"\n\n{'=' * 80}")
    print("2. DUPLICACIONES Y SOLAPAMIENTOS")
    print(f"{'=' * 80}\n")

    # Estándares referenciados múltiples veces
    multi_ref = {k: v for k, v in estandares_unicos.items() if len(v['lineamientos']) > 1}

    print(f"### Estándares referenciados desde múltiples lineamientos ({len(multi_ref)} encontrados)")
    print("-" * 80)
    for ruta, datos in sorted(multi_ref.items(), key=lambda x: len(x[1]['lineamientos']), reverse=True):
        refs = len(datos['lineamientos'])
        print(f"\n  • {datos['nombre']}")
        print(f"    Referencias: {refs} lineamientos")
        print(f"    Lineamientos: {', '.join(sorted(set(datos['lineamientos'])))}")
        print(f"    Estado: ", end="")
        if refs > 3:
            print("⚠️ ALTO - Revisar si es apropiado")
        elif refs > 1:
            print("✅ OK - Cross-cutting concern válido")

    # Detectar nombres similares
    print(f"\n\n### Estándares con nombres similares (posibles duplicados)")
    print("-" * 80)
    similares_encontrados = False

    lista_estandares = list(estandares_unicos.values())
    for i, est1 in enumerate(lista_estandares):
        for est2 in lista_estandares[i+1:]:
            similitud = detectar_similitud(est1['nombre'], est2['nombre'])
            if similitud > 0.5 and est1['ruta'] != est2['ruta']:
                similares_encontrados = True
                print(f"\n  ⚠️ Similitud: {similitud:.0%}")
                print(f"     1) {est1['nombre']}")
                print(f"        {est1['ruta']}")
                print(f"     2) {est2['nombre']}")
                print(f"        {est2['ruta']}")

    if not similares_encontrados:
        print("  ✅ No se detectaron nombres significativamente similares")

    # 3. AMBIGÜEDADES
    print(f"\n\n{'=' * 80}")
    print("3. AMBIGÜEDADES EN NOMBRES")
    print(f"{'=' * 80}\n")

    ambiguos = []
    for ruta, datos in estandares_unicos.items():
        problemas = detectar_ambiguedades(datos['nombre'])
        if problemas:
            ambiguos.append((datos['nombre'], datos['ruta'], problemas))

    if ambiguos:
        for nombre, ruta, problemas in ambiguos:
            print(f"\n  ⚠️ {nombre}")
            print(f"     Ruta: {ruta}")
            for problema in problemas:
                print(f"     - {problema}")
    else:
        print("  ✅ No se detectaron nombres ambiguos")

    # 4. VALIDACIÓN CONTRA INDUSTRIA
    print(f"\n\n{'=' * 80}")
    print("4. VALIDACIÓN CONTRA FRAMEWORKS DE INDUSTRIA")
    print(f"{'=' * 80}\n")

    por_estado = {'✅': [], '⚠️': [], '❌': []}

    for ruta, datos in estandares_unicos.items():
        estado, frameworks = validar_contra_industria(datos['nombre'], datos['ruta'])
        por_estado[estado].append((datos['nombre'], datos['ruta'], frameworks))

    print(f"### ✅ Estándares bien alineados con industria ({len(por_estado['✅'])} estándares)")
    print("-" * 80)
    for nombre, ruta, frameworks in sorted(por_estado['✅'])[:10]:  # Mostrar solo los primeros 10
        print(f"  • {nombre}")
        print(f"    Frameworks: {', '.join(frameworks)}")
    if len(por_estado['✅']) > 10:
        print(f"\n  ... y {len(por_estado['✅']) - 10} más")

    print(f"\n\n### ⚠️ Estándares válidos pero poco comunes ({len(por_estado['⚠️'])} estándares)")
    print("-" * 80)
    for nombre, ruta, frameworks in sorted(por_estado['⚠️']):
        print(f"  • {nombre}")
        if frameworks:
            print(f"    Framework: {frameworks[0]}")

    print(f"\n\n### ❌ Estándares no reconocidos o custom ({len(por_estado['❌'])} estándares)")
    print("-" * 80)
    for nombre, ruta, _ in sorted(por_estado['❌']):
        print(f"  • {nombre}")
        print(f"    Ruta: {ruta}")

    # 5. RUIDO/SOBREDIMENSIONAMIENTO
    print(f"\n\n{'=' * 80}")
    print("5. ANÁLISIS DE RUIDO Y SOBREDIMENSIONAMIENTO")
    print(f"{'=' * 80}\n")

    print("### Lineamientos con cantidad excesiva de estándares (>7)")
    print("-" * 80)
    excesivos = {k: v for k, v in estandares_por_lineamiento.items() if v > 7}
    if excesivos:
        for lineamiento, cantidad in sorted(excesivos.items(), key=lambda x: x[1], reverse=True):
            print(f"  ⚠️ {lineamiento}: {cantidad} estándares")
    else:
        print("  ✅ Ningún lineamiento excede 7 estándares")

    # 6. RECOMENDACIONES
    print(f"\n\n{'=' * 80}")
    print("6. RECOMENDACIONES DE CONSOLIDACIÓN")
    print(f"{'=' * 80}\n")

    print("### Acciones sugeridas:")
    print("-" * 80)

    if len(por_estado['❌']) > 10:
        print(f"\n  1. ⚠️ ALTA PRIORIDAD: Revisar {len(por_estado['❌'])} estándares no alineados con industria")
        print("     - Validar si son genuinamente custom o necesitan renombre/redefinición")
        print("     - Considerar alinear con frameworks reconocidos")

    if ambiguos:
        print(f"\n  2. ⚠️ MEDIA PRIORIDAD: Renombrar {len(ambiguos)} estándares con nombres ambiguos")
        print("     - Usar nombres más descriptivos y específicos")

    multi_ref_alto = [k for k, v in multi_ref.items() if len(v['lineamientos']) > 3]
    if multi_ref_alto:
        print(f"\n  3. ℹ️ BAJA PRIORIDAD: Revisar {len(multi_ref_alto)} estándares altamente referenciados")
        print("     - Validar que las referencias múltiples son apropiadas")
        print("     - Considerar si algunos deberían ser parte de un estándar más amplio")

    if excesivos:
        print(f"\n  4. ℹ️ REVISAR: {len(excesivos)} lineamientos con >7 estándares")
        print("     - Evaluar si algunos estándares pueden consolidarse")
        print("     - Verificar que todos son necesarios y no redundantes")

    total_unicos = len(estandares_unicos)
    print(f"\n\n### Resumen Final:")
    print("-" * 80)
    print(f"  Total de estándares únicos: {total_unicos}")
    print(f"  Bien alineados con industria: {len(por_estado['✅'])} ({len(por_estado['✅'])*100//total_unicos}%)")
    print(f"  Válidos pero poco comunes: {len(por_estado['⚠️'])} ({len(por_estado['⚠️'])*100//total_unicos}%)")
    print(f"  No reconocidos o custom: {len(por_estado['❌'])} ({len(por_estado['❌'])*100//total_unicos}%)")
    print(f"  Con nombres ambiguos: {len(ambiguos)} ({len(ambiguos)*100//total_unicos}%)")

    print(f"\n{'=' * 80}\n")


if __name__ == '__main__':
    main()
