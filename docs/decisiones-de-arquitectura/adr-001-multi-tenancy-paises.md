---
title: "ADR-001: Multi-Tenancy y Gestión por Países"
sidebar_position: 1
---

## ✅ ESTADO

Aceptada – Agosto 2025

---

## 🗺️ CONTEXTO

Los servicios corporativos deben soportar operaciones en múltiples países (Perú, Ecuador, Colombia, México) con:

- **Aislamiento de datos** por país/cliente para cumplimiento regulatorio
- **Configuraciones específicas** por mercado y regulaciones locales
- **Escalabilidad independiente** por región según demanda
- **Gestión centralizada** con visibilidad global para operaciones
- **Costos optimizados** compartiendo infraestructura común
- **Portabilidad** entre clouds manteniendo la separación

Las alternativas de multi-tenancy evaluadas fueron:

- **Database per Tenant** (Aislamiento completo)
- **Schema per Tenant** (Aislamiento intermedio)
- **Row-Level Security** (Aislamiento lógico)
- **Hybrid Approach** (Combinación según criticidad): Consiste en aplicar diferentes patrones de multi-tenancy según el tipo de servicio o dato. Por ejemplo, servicios críticos o regulados (como Identidad o Finanzas) se implementan como single-tenant (una base de datos dedicada por país o cliente), mientras que servicios operacionales o de soporte (como Track & Trace o Notificación) pueden usar modelos multi-tenant (por ejemplo, un esquema por país en una misma base de datos). Así, se logra un balance entre cumplimiento, seguridad, costos y eficiencia operativa.

## 🔍 COMPARATIVA DE ALTERNATIVAS

### Comparativa Cualitativa

| Criterio           | Single-Tenant         | Multi-Tenant DB       | Multi-Tenant Schema | Híbrido                   |
| ------------------ | --------------------- | --------------------- | ------------------- | ------------------------- |
| **Aislamiento**    | ✅ Total por cliente  | 🟡 A nivel aplicación | 🟡 Por esquema      | ✅ Flexible según cliente |
| **Escalabilidad**  | ❌ Muy limitada       | ✅ Excelente          | ✅ Muy buena        | ✅ Buena                  |
| **Operación**      | ❌ Compleja gestión   | ✅ Centralizada       | 🟡 Moderada         | 🟡 Compleja pero flexible |
| **Costos**         | ❌ Muy altos          | ✅ Muy eficiente      | ✅ Eficiente        | 🟡 Moderados              |
| **Flexibilidad**   | ✅ Máxima por cliente | ❌ Muy limitada       | 🟡 Limitada         | ✅ Alta                   |
| **Compliance**     | ✅ Máximo control     | 🟡 Requiere cuidado   | 🟡 Bueno            | ✅ Excelente              |
| **Implementación** | ✅ Rápida             | ✅ Rápida             | 🟡 Moderada         | 🟡 Compleja               |

## ⚖️ DECISIÓN

**Seleccionamos Hybrid Approach** con la siguiente estrategia:

### Modelo Híbrido por Criticidad

#### Nivel 1: Database per Tenant (Datos Críticos)

```yaml
Servicios con DB separada:
  - Servicio Identidad: Usuarios, roles, permisos
  - Datos Financieros: Transacciones, facturación
  - Datos Personales: PII, información sensible

Configuración: talma_identity_peru
  talma_identity_ecuador
  talma_identity_colombia
  talma_identity_mexico
```

#### Nivel 2: Schema per Tenant (Datos Operacionales)

```yaml
Servicios con schema separado:
  - Servicio Notificación: Templates, configuraciones
  - Track & Trace: Estados, eventos de negocio
  - Configuraciones: Parámetros por país

Configuración:
  Database: talma_operations
  Schemas: peru, ecuador, colombia, mexico
```

#### Nivel 3: Row-Level Security (Datos Compartidos)

```yaml
Servicios con RLS:
  - Logs y auditoría
  - Métricas y monitoreo
  - Datos de referencia comunes

Configuración:
  Database: talma_shared
  RLS Policy: tenant_id = current_setting('app.tenant_id')
```

### Ventajas del Modelo Híbrido

- **Cumplimiento regulatorio**: Aislamiento completo para datos sensibles
- **Optimización de costos**: Recursos compartidos para datos no críticos
- **Escalabilidad flexible**: Escalar independientemente por criticidad
- **Operación simplificada**: Menos bases de datos que DB per Tenant completo

---

## 🔄 CONSECUENCIAS

### Positivas

- ✅ **Cumplimiento regulatorio** garantizado para datos críticos
- ✅ **Optimización de costos** con recursos compartidos apropiados
- ✅ **Escalabilidad granular** por tenant y por criticidad
- ✅ **Flexibilidad operacional** para diferentes necesidades
- ✅ **Portabilidad mantenida** entre clouds y on-premises
- ✅ **Auditoría simplificada** con separación clara

### Negativas

- ❌ **Complejidad arquitectónica** mayor que enfoques simples
- ❌ **Gestión de múltiples patrones** requiere expertise
- ❌ **Testing complejo** debe cubrir todos los niveles

---

## 📚 REFERENCIAS

- [Multi-Tenant Data Architecture](https://docs.microsoft.com/en-us/azure/sql-database/saas-tenancy-app-design-patterns)
- [PostgreSQL Row Level Security](https://www.postgresql.org/docs/current/ddl-rowsecurity.html)
- [Multi-Tenancy Patterns](https://martinfowler.com/articles/multi-tenant/)
- [GDPR and Multi-Tenancy](https://gdpr.eu/data-protection-impact-assessment-template/)

---

**Decisión tomada por:** Equipo de Arquitectura + Legal + Compliance
**Fecha:** Agosto 2025
**Próxima revisión:** Agosto 2026
