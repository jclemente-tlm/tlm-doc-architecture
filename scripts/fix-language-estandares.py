#!/usr/bin/env python3
"""
Script para corregir el idioma (español) en los encabezados de estándares.
Aplica las correcciones identificadas en la auditoría de idioma.
Regla: Todo el contenido en español; inglés solo para nombres de tecnologías,
       términos técnicos sin traducción natural y nombres de patrones reconocidos.
"""

import os
import re
from pathlib import Path

BASE = Path("/home/jclemente/dev/talma/tlm-doc-architecture/docs/fundamentos-corporativos/estandares")

# Mapa de archivos → lista de (original, reemplazo)
CORRECTIONS = {
    "datos/data-consistency.md": [
        ("## Consistency Models\n", "## Modelos de Consistencia\n"),
        ("## Conflict Resolution\n", "## Resolución de Conflictos\n"),
        ("## Data Replication\n", "## Replicación de Datos\n"),
    ],
    "datos/data-architecture.md": [
        ("## Data Ownership\n", "## Propiedad de Datos\n"),
        ("## Data Ownership Matrix\n", "## Matriz de Propiedad de Datos\n"),
        ("## Data Governance\n", "## Gobierno de Datos\n"),
        ("## Data Catalog\n", "## Catálogo de Datos\n"),
        ("## Data Exposure\n", "## Exposición de Datos\n"),
        ("### ¿Qué es Data Ownership?", "### ¿Qué es la Propiedad de Datos?"),
        ("### ¿Qué es Data Governance?", "### ¿Qué es el Gobierno de Datos?"),
        ("### ¿Qué es un Data Catalog?", "### ¿Qué es un Catálogo de Datos?"),
        ("### ¿Qué es Data Exposure?", "### ¿Qué es la Exposición de Datos?"),
        # H3 "Matriz de Ownership" está dentro de la sección de Ownership
        ("### Matriz de Ownership", "### Matriz de Propiedad"),
    ],
    "datos/database-standards.md": [
        ("## Database Migrations\n", "## Migraciones de Base de Datos\n"),
        ("## SQL Naming Conventions\n", "## Convenciones de Nomenclatura SQL\n"),
        ("## Database Optimization\n", "## Optimización de Base de Datos\n"),
        ("## Data Validation\n", "## Validación de Datos\n"),
    ],
    "datos/caching.md": [
        ("title: Caching\n", "title: Caché\n"),
        ("# Caching\n", "# Caché\n"),
        ("## TTL Management\n", "## Gestión de TTL\n"),
        ("## Distributed Cache (Redis ElastiCache)\n", "## Caché Distribuida (Redis ElastiCache)\n"),
        ("## Cache Invalidation\n", "## Invalidación de Caché\n"),
        ("## Cache Security\n", "## Seguridad del Caché\n"),
        ("## Checklist Caching\n", "## Lista de Verificación del Caché\n"),
    ],
    "arquitectura/cloud-native.md": [
        ("## Stateless Design\n", "## Diseño sin Estado\n"),
        ("### ¿Qué es Stateless Design?", "### ¿Qué es el Diseño sin Estado?"),
        ("## Configuration Externalization\n", "## Externalización de Configuración\n"),
        ("### ¿Qué es Configuration Externalization?", "### ¿Qué es la Externalización de Configuración?"),
        ("## Disposability (Desechabilidad)\n", "## Desechabilidad\n"),
        ("## Cost Awareness\n", "## Gestión del Costo en Cloud\n"),
        ("## Checklist Cloud-Native\n", "## Lista de Verificación Cloud-Native\n"),
    ],
    "arquitectura/scalability-performance.md": [
        ("## Stateless Design\n", "## Diseño sin Estado\n"),
        ("### ¿Qué es Stateless Design?", "### ¿Qué es el Diseño sin Estado?"),
        ("## Caching Strategies\n", "## Estrategias de Caché\n"),
        ("### ¿Qué son Caching Strategies?", "### ¿Qué son las Estrategias de Caché?"),
        ("## Horizontal Scaling\n", "## Escalado Horizontal\n"),
        ("### ¿Qué es Horizontal Scaling?", "### ¿Qué es el Escalado Horizontal?"),
        ("## Load Balancing\n", "## Balanceo de Carga\n"),
        ("### ¿Qué es Load Balancing?", "### ¿Qué es el Balanceo de Carga?"),
    ],
    "arquitectura/architecture-principles.md": [
        ("## Loose Coupling\n", "## Bajo Acoplamiento\n"),
        ("### ¿Qué es Loose Coupling?", "### ¿Qué es el Bajo Acoplamiento?"),
        ("## Dependency Management\n", "## Gestión de Dependencias\n"),
        ("### ¿Qué es Dependency Management?", "### ¿Qué es la Gestión de Dependencias?"),
    ],
    "operabilidad/deployment.md": [
        ("title: Deployment\n", "title: Despliegue\n"),
        ("# Deployment\n", "# Despliegue\n"),
        ("## Flujo de Deployment\n", "## Flujo de Despliegue\n"),
        ("## Deployment Strategies\n", "## Estrategias de Despliegue\n"),
        ("### ¿Qué son las Deployment Strategies?", "### ¿Qué son las Estrategias de Despliegue?"),
        ("## Deployment Traceability\n", "## Trazabilidad de Despliegue\n"),
        ("### ¿Qué es Deployment Traceability?", "### ¿Qué es la Trazabilidad de Despliegue?"),
        ("### Endpoint de Deployment Info\n", "### Endpoint de Información de Despliegue\n"),
        ("## Rollback Automation\n", "## Automatización de Rollback\n"),
        ("### ¿Qué es Rollback Automation?", "### ¿Qué es la Automatización de Rollback?"),
    ],
    "testing/contract-testing.md": [
        ("title: Contract Testing\n", "title: Pruebas de Contrato\n"),
        ("# Contract Testing\n", "# Pruebas de Contrato\n"),
        ("## Contract Testing\n", "## Pruebas de Contrato\n"),
        ("### ¿Qué es Contract Testing?", "### ¿Qué son las Pruebas de Contrato?"),
    ],
    "testing/test-automation.md": [
        ("title: Automatización de Tests\n", "title: Automatización de Pruebas\n"),
        ("# Automatización de Tests\n", "# Automatización de Pruebas\n"),
        ("## Automatización de Tests\n", "## Automatización de Pruebas\n"),
        ("### ¿Qué es Test Automation?", "### ¿Qué es la Automatización de Pruebas?"),
        # En description también
        ("automatización en CI/CD, quality gates y ejec\nución paralela de tests",
         "automatización en CI/CD, quality gates y ejec\nución paralela de pruebas"),
    ],
    "testing/performance-testing.md": [
        ("## Performance Testing\n", "## Pruebas de Performance\n"),
        ("### ¿Qué es Performance Testing?", "### ¿Qué son las Pruebas de Performance?"),
    ],
    "testing/testing-pyramid.md": [
        ("### ¿Qué es la Testing Pyramid?", "### ¿Qué es la Pirámide de Testing?"),
    ],
    "testing/test-coverage.md": [
        ("### ¿Qué es Test Coverage?", "### ¿Qué es la Cobertura de Código?"),
    ],
    "testing/unit-testing.md": [
        ("### ¿Qué es Unit Testing?", "### ¿Qué son las Pruebas Unitarias?"),
    ],
    "testing/integration-testing.md": [
        ("### ¿Qué es Integration Testing?", "### ¿Qué son las Pruebas de Integración?"),
    ],
    "testing/e2e-testing.md": [
        ("### ¿Qué es E2E Testing?", "### ¿Qué son las Pruebas End-to-End?"),
    ],
    "desarrollo/code-quality.md": [
        ("## Code Conventions\n", "## Convenciones de Código\n"),
        ("### ¿Qué son las Code Conventions?", "### ¿Qué son las Convenciones de Código?"),
        ("## Code Review\n", "## Revisión de Código\n"),
        ("### ¿Qué es Code Review?", "### ¿Qué es la Revisión de Código?"),
    ],
}

total_changes = 0
errors = []

for rel_path, pairs in CORRECTIONS.items():
    filepath = BASE / rel_path
    if not filepath.exists():
        errors.append(f"ARCHIVO NO ENCONTRADO: {rel_path}")
        continue

    content = filepath.read_text(encoding="utf-8")
    original_content = content
    file_changes = 0

    for old, new in pairs:
        if old in content:
            content = content.replace(old, new, 1)
            file_changes += 1
        else:
            # Intentar sin salto de línea al final si el original tiene \n
            old_strip = old.rstrip("\n")
            new_strip = new.rstrip("\n")
            if old_strip in content:
                content = content.replace(old_strip, new_strip, 1)
                file_changes += 1
            else:
                errors.append(f"  ⚠️  No encontrado en {rel_path}: '{old_strip[:60]}'")

    if content != original_content:
        filepath.write_text(content, encoding="utf-8")
        print(f"✅ {rel_path} → {file_changes} cambio(s)")
        total_changes += file_changes
    else:
        print(f"⏭️  {rel_path} → sin cambios")

print(f"\n{'='*60}")
print(f"TOTAL: {total_changes} correcciones aplicadas en {len(CORRECTIONS)} archivos")
if errors:
    print(f"\nADVERTENCIAS ({len(errors)}):")
    for e in errors:
        print(e)
