#!/bin/bash

# Script para renombrar estándares: español→inglés y eliminar numeración
# Ejecutar desde la raíz del proyecto

cd "$(dirname "$0")/.." || exit

BASE_DIR="docs/fundamentos-corporativos/estandares"

echo "🔄 Renombrando estándares..."

# FASE 1: Eliminar duplicados (prevalecen los numerados)
echo "📦 Eliminando duplicados..."
git rm -f "$BASE_DIR/apis/versionado.md" 2>/dev/null || true
git rm -f "$BASE_DIR/datos/database-migrations.md" 2>/dev/null || true
git rm -f "$BASE_DIR/documentacion/architecture-review.md" 2>/dev/null || true
git rm -f "$BASE_DIR/operabilidad/infrastructure-as-code.md" 2>/dev/null || true

# FASE 2: Renombrar archivos (español→inglés + quitar numeración)

# Observabilidad
git mv "$BASE_DIR/observabilidad/02-monitoreo-metricas.md" "$BASE_DIR/observabilidad/metrics-monitoring.md" 2>/dev/null || true
git mv "$BASE_DIR/observabilidad/03-tracing-distribuido.md" "$BASE_DIR/observabilidad/distributed-tracing.md" 2>/dev/null || true
git mv "$BASE_DIR/observabilidad/01-logging.md" "$BASE_DIR/observabilidad/logging.md" 2>/dev/null || true
git mv "$BASE_DIR/observabilidad/04-correlation-ids.md" "$BASE_DIR/observabilidad/correlation-ids.md" 2>/dev/null || true
git mv "$BASE_DIR/observabilidad/05-health-checks.md" "$BASE_DIR/observabilidad/health-checks.md" 2>/dev/null || true

# APIs
git mv "$BASE_DIR/apis/01-diseno-rest.md" "$BASE_DIR/apis/rest-design.md" 2>/dev/null || true
git mv "$BASE_DIR/apis/02-seguridad-apis.md" "$BASE_DIR/apis/api-security.md" 2>/dev/null || true
git mv "$BASE_DIR/apis/03-validacion-y-errores.md" "$BASE_DIR/apis/validation-and-errors.md" 2>/dev/null || true
git mv "$BASE_DIR/apis/04-versionado.md" "$BASE_DIR/apis/versioning.md" 2>/dev/null || true
git mv "$BASE_DIR/apis/deprecacion-apis.md" "$BASE_DIR/apis/api-deprecation.md" 2>/dev/null || true
git mv "$BASE_DIR/apis/rate-limiting-paginacion.md" "$BASE_DIR/apis/rate-limiting-pagination.md" 2>/dev/null || true

# Mensajería
git mv "$BASE_DIR/mensajeria/01-kafka-eventos.md" "$BASE_DIR/mensajeria/kafka-events.md" 2>/dev/null || true

# Infraestructura
git mv "$BASE_DIR/infraestructura/externalizar-configuracion-12factor.md" "$BASE_DIR/infraestructura/externalize-configuration.md" 2>/dev/null || true
git mv "$BASE_DIR/infraestructura/01-docker.md" "$BASE_DIR/infraestructura/docker.md" 2>/dev/null || true
git mv "$BASE_DIR/infraestructura/03-secrets-management.md" "$BASE_DIR/infraestructura/secrets-management.md" 2>/dev/null || true
git mv "$BASE_DIR/infraestructura/04-docker-compose.md" "$BASE_DIR/infraestructura/docker-compose.md" 2>/dev/null || true

# Datos
git mv "$BASE_DIR/datos/02-migrations.md" "$BASE_DIR/datos/migrations.md" 2>/dev/null || true

# Testing
git mv "$BASE_DIR/testing/01-unit-tests.md" "$BASE_DIR/testing/unit-tests.md" 2>/dev/null || true
git mv "$BASE_DIR/testing/02-integration-tests.md" "$BASE_DIR/testing/integration-tests.md" 2>/dev/null || true

# Documentación
git mv "$BASE_DIR/documentacion/01-arc42.md" "$BASE_DIR/documentacion/arc42.md" 2>/dev/null || true
git mv "$BASE_DIR/documentacion/02-c4-model.md" "$BASE_DIR/documentacion/c4-model.md" 2>/dev/null || true
git mv "$BASE_DIR/documentacion/03-openapi-swagger.md" "$BASE_DIR/documentacion/openapi-swagger.md" 2>/dev/null || true

# Código
git mv "$BASE_DIR/codigo/01-csharp-dotnet.md" "$BASE_DIR/codigo/csharp-dotnet.md" 2>/dev/null || true
git mv "$BASE_DIR/codigo/03-sql.md" "$BASE_DIR/codigo/sql.md" 2>/dev/null || true

echo "✅ Renombrado completado"
echo ""
echo "📊 Resumen de cambios:"
git status --short | grep -E "(renamed|deleted)" | wc -l
echo "   archivos modificados"
