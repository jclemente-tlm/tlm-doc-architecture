#!/usr/bin/env python3
"""
Analiza todos los lineamientos y verifica referencias a estándares.
"""

import os
import re
from pathlib import Path
from collections import defaultdict

# Rutas
LINEAMIENTOS_DIR = Path("docs/fundamentos-corporativos/lineamientos")
ESTANDARES_DIR = Path("docs/fundamentos-corporativos/estandares")

def extraer_referencias_estandares(contenido):
    """Extrae todas las referencias a estándares de un archivo markdown."""
    # Buscar enlaces con patrón: ../../estandares/...
    patron = r'\[([^\]]+)\]\((\.\.\/\.\.\/estandares\/[^\)#]+?)(?:#[^\)]*)?\)'
    referencias = re.findall(patron, contenido)
    return [(texto, ruta) for texto, ruta in referencias]

def normalizar_ruta(ruta_relativa):
    """Convierte ruta relativa de lineamiento a ruta de archivo real."""
    # Remover ../../estandares/ y agregar el prefijo correcto
    ruta = ruta_relativa.replace("../../estandares/", "")
    return ESTANDARES_DIR / ruta

def leer_lineamientos():
    """Lee todos los lineamientos y extrae sus referencias."""
    lineamientos_data = defaultdict(list)

    # Recorrer todas las subcarpetas de lineamientos
    for categoria_dir in LINEAMIENTOS_DIR.iterdir():
        if not categoria_dir.is_dir():
            continue

        categoria = categoria_dir.name

        for archivo in categoria_dir.glob("*.md"):
            if archivo.name.startswith("_"):
                continue

            try:
                contenido = archivo.read_text(encoding="utf-8")
                referencias = extraer_referencias_estandares(contenido)

                lineamientos_data[f"{categoria}/{archivo.name}"] = referencias
            except Exception as e:
                print(f"Error leyendo {archivo}: {e}")

    return lineamientos_data

def verificar_existencia_estandares():
    """Obtiene lista de todos los estándares existentes."""
    estandares_existentes = []

    for categoria_dir in ESTANDARES_DIR.iterdir():
        if not categoria_dir.is_dir():
            continue

        for archivo in categoria_dir.glob("*.md"):
            if archivo.name.startswith("_"):
                continue

            # Ruta relativa desde estandares/
            ruta_relativa = f"{categoria_dir.name}/{archivo.name}"
            estandares_existentes.append(ruta_relativa)

    return set(estandares_existentes)

def analizar_referencias():
    """Analiza todas las referencias y genera el reporte."""
    print("🔍 Analizando lineamientos...")
    lineamientos_data = leer_lineamientos()

    print("📚 Verificando estándares existentes...")
    estandares_existentes = verificar_existencia_estandares()

    # Recopilar todas las referencias únicas
    todas_referencias = {}
    referencias_por_archivo = defaultdict(list)

    for lineamiento, referencias in lineamientos_data.items():
        for texto, ruta_relativa in referencias:
            # Extraer solo la parte de la ruta sin ../../estandares/
            ruta_estandar = ruta_relativa.replace("../../estandares/", "")

            if ruta_estandar not in todas_referencias:
                todas_referencias[ruta_estandar] = []

            todas_referencias[ruta_estandar].append(lineamiento)
            referencias_por_archivo[lineamiento].append((texto, ruta_estandar))

    # Clasificar referencias
    rotas = {}
    existentes = {}

    for ruta_estandar, lineamientos in todas_referencias.items():
        if ruta_estandar in estandares_existentes:
            existentes[ruta_estandar] = lineamientos
        else:
            rotas[ruta_estandar] = lineamientos

    # Agrupar rotas por categoría
    rotas_por_categoria = defaultdict(list)
    for ruta in rotas.keys():
        categoria = ruta.split("/")[0] if "/" in ruta else "sin-categoria"
        rotas_por_categoria[categoria].append(ruta)

    # Identificar lineamientos sin referencias
    sin_referencias = [l for l, refs in lineamientos_data.items() if len(refs) == 0]

    # Generar reporte
    print("\n" + "="*80)
    print("📊 REPORTE DE ANÁLISIS DE REFERENCIAS A ESTÁNDARES")
    print("="*80)

    print(f"\n📈 RESUMEN:")
    print(f"  • Total de lineamientos analizados: {len(lineamientos_data)}")
    print(f"  • Total de referencias únicas: {len(todas_referencias)}")
    print(f"  • Referencias válidas (existentes): {len(existentes)}")
    print(f"  • Referencias rotas (faltantes): {len(rotas)}")
    print(f"  • Lineamientos sin referencias: {len(sin_referencias)}")

    print(f"\n\n🔴 1. ENLACES ROTOS ({len(rotas)} estándares faltantes)")
    print("-" * 80)

    for ruta, lineamientos in sorted(rotas.items()):
        print(f"\n❌ {ruta}")
        print(f"   Referenciado en:")
        for lin in sorted(lineamientos):
            print(f"     - {lin}")

    print(f"\n\n📁 2. ESTÁNDARES FALTANTES POR CATEGORÍA")
    print("-" * 80)

    for categoria, rutas in sorted(rotas_por_categoria.items()):
        print(f"\n📂 {categoria.upper()} ({len(rutas)} faltantes):")
        for ruta in sorted(rutas):
            print(f"   - {ruta}")

    if sin_referencias:
        print(f"\n\n⚠️  3. LINEAMIENTOS SIN REFERENCIAS ({len(sin_referencias)})")
        print("-" * 80)
        for lin in sorted(sin_referencias):
            print(f"   - {lin}")
    else:
        print(f"\n\n✅ 3. LINEAMIENTOS SIN REFERENCIAS")
        print("-" * 80)
        print("   Todos los lineamientos tienen al menos una referencia a estándares.")

    print(f"\n\n🎯 4. GAPS CRÍTICOS - PRIORIZACIÓN")
    print("-" * 80)
    print("\nEstándares más referenciados que faltan:\n")

    # Ordenar por número de referencias
    rotas_ordenadas = sorted(rotas.items(), key=lambda x: len(x[1]), reverse=True)

    for i, (ruta, lineamientos) in enumerate(rotas_ordenadas[:15], 1):
        categoria = ruta.split("/")[0] if "/" in ruta else "?"
        print(f"  {i}. [{categoria}] {ruta}")
        print(f"     → Referenciado {len(lineamientos)} vez/veces")

    print(f"\n\n✅ ESTÁNDARES EXISTENTES ({len(estandares_existentes)})")
    print("-" * 80)

    existentes_por_cat = defaultdict(list)
    for est in sorted(estandares_existentes):
        cat = est.split("/")[0] if "/" in est else "sin-categoria"
        existentes_por_cat[cat].append(est)

    for cat, ests in sorted(existentes_por_cat.items()):
        print(f"\n📂 {cat} ({len(ests)}):")
        for est in ests:
            nombre = est.split("/")[1] if "/" in est else est
            print(f"   ✓ {nombre}")

    # Estadísticas por categoría de lineamiento
    print(f"\n\n📊 ESTADÍSTICAS POR CATEGORÍA DE LINEAMIENTO")
    print("-" * 80)

    stats_por_cat = defaultdict(lambda: {"total": 0, "con_refs": 0, "refs_rotas": 0})

    for lineamiento, referencias in lineamientos_data.items():
        categoria = lineamiento.split("/")[0]
        stats_por_cat[categoria]["total"] += 1
        if referencias:
            stats_por_cat[categoria]["con_refs"] += 1

        for _, ruta_est in referencias:
            if ruta_est not in estandares_existentes:
                stats_por_cat[categoria]["refs_rotas"] += 1

    for cat, stats in sorted(stats_por_cat.items()):
        pct = (stats["con_refs"] / stats["total"] * 100) if stats["total"] > 0 else 0
        print(f"\n{cat}:")
        print(f"   • Lineamientos: {stats['total']}")
        print(f"   • Con referencias: {stats['con_refs']} ({pct:.0f}%)")
        print(f"   • Referencias rotas: {stats['refs_rotas']}")

    print("\n" + "="*80)
    print("✅ Análisis completado")
    print("="*80 + "\n")

if __name__ == "__main__":
    analizar_referencias()
