---
id: adr-019-configuraciones-scripts-bd
title: "Configuraciones por Scripts en BD"
sidebar_position: 4
---

## ✅ ESTADO

Aceptada – Agosto 2025

---

## 🗺️ CONTEXTO

Algunos microservicios requieren **configuraciones iniciales o poco frecuentes** directamente en la base de datos, como:

- **Carga inicial de parámetros de negocio** (catálogos, valores por defecto).
- **Ajustes estructurales menores** que no justifican una migración completa de esquema.
- **Habilitación/deshabilitación de características** mediante flags en tablas de configuración.
- **Corrección puntual de datos** durante despliegues o mantenimiento.

Dado que estos cambios:

- Se realizan al inicio o de forma muy esporádica.
- No justifican crear un API o interfaz dedicada.
- Deben ser **versionados, auditables y reproducibles**.
- Idealmente deben ser **agnósticos de motor de BD**.

La intención estratégica es **permitir la ejecución controlada y trazable de scripts** integrados al ciclo de despliegue, evitando cambios manuales no registrados.

---

## 🔍 COMPARATIVA DE ALTERNATIVAS

### Comparativa Cualitativa

| Criterio | DbUp (.NET) | RoundhousE (.NET) | Flyway (CLI/Java) | Liquibase (CLI/Java) | EF Core Migrations |
|----------|-------------|-------------------|-------------------|----------------------|--------------------|
| **Agnosticidad** | ✅ Multi-motor | ✅ Multi-motor | ✅ Multi-motor | ✅ Multi-motor | 🟡 Depende del provider |
| **Integración .NET** | ✅ Nativo C# | ✅ Nativo C# | 🟡 Indirecta | 🟡 Indirecta | ✅ Nativo C# |
| **Versionado de scripts** | ✅ Por convención | ✅ Por convención | ✅ Estricto | ✅ Estricto | ✅ Automático |
| **Complejidad operativa** | ✅ Baja | ✅ Baja | 🟡 Media | ❌ Alta | ✅ Baja |
| **Rollbacks** | ❌ Manuales | ❌ Manuales | 🟡 Básicos | ✅ Avanzados | 🟡 Limitados |
| **Idempotencia** | 🟡 Depende del script | 🟡 Depende del script | 🟡 Depende del script | 🟡 Depende del script | 🟡 Depende del script |

---

### Matriz de Decisión

| Solución | Agnosticidad | Integración .NET | Operación | Recomendación |
|----------|--------------|------------------|-----------|---------------|
| **DbUp** | Excelente | Excelente | Excelente | ✅ **Seleccionada** |
| **RoundhousE** | Excelente | Excelente | Excelente | 🟡 Alternativa |
| **Flyway** | Excelente | Media | Media | 🟡 Alternativa |
| **Liquibase** | Excelente | Media | Baja | ❌ Descartada |
| **EF Core Migrations** | Media | Excelente | Excelente | 🟡 Uso parcial |

---

## ✔️ DECISIÓN

Se selecciona **DbUp** como herramienta principal para la ejecución de configuraciones iniciales y puntuales en base de datos.

---

## Justificación

- **Compatibilidad multi-motor** (SQL Server, PostgreSQL, MySQL, etc.).
- **Integración directa con .NET 8** sin dependencias externas (Java/CLI).
- **Baja complejidad operativa**: scripts en SQL puro, versionados y aplicados de forma ordenada.
- **Facilidad de integración en pipelines CI/CD**, pudiendo ejecutar en despliegues iniciales o bajo demanda.
- **Posibilidad de migrar** a Flyway/Liquibase en el futuro manteniendo el formato SQL base.

---

## Alternativas descartadas

- **RoundhousE**: buena opción, pero menos activo y con menor comunidad que DbUp.
- **Flyway**: más maduro en entornos mixtos, pero introduce dependencia Java y mayor complejidad para este escenario puntual.
- **Liquibase**: potente pero sobre-dimensionado para cambios ocasionales.
- **EF Core Migrations**: útil para cambios de esquema ligados al modelo de datos, pero no ideal para configuraciones iniciales que puedan ejecutarse en múltiples motores.

---

## ⚠️ CONSECUENCIAS

- Los scripts deben ser **idempotentes** para evitar errores en re-ejecuciones.
- La nomenclatura de archivos (`yyyy.MM.dd__descripcion.sql`) debe ser consistente para asegurar orden y trazabilidad.
- La responsabilidad de escribir y validar los scripts recae en el equipo técnico, no en usuarios finales.
- No se implementará UI ni API dedicada para este tipo de configuraciones.

---

## 📚 REFERENCIAS

- [DbUp Documentation](https://dbup.readthedocs.io/en/latest/)
- [RoundhousE GitHub](https://github.com/chucknorris/roundhouse)
- [Flyway Documentation](https://documentation.red-gate.com/fd)
- [Liquibase Documentation](https://www.liquibase.org/)
- [EF Core Migrations Docs](https://learn.microsoft.com/en-us/ef/core/managing-schemas/migrations/)
