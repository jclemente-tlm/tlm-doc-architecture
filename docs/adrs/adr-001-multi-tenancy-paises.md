---
id: adr-001-multi-tenancy-paises
title: "Multi-Tenancy y Gestión por Países"
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
- **Hybrid Approach** (Combinación según criticidad)

## 🔍 COMPARATIVA DE ALTERNATIVAS

### Comparativa Cualitativa

| Criterio | Single-Tenant | Multi-Tenant DB | Multi-Tenant Schema | Híbrido |
|----------|---------------|-----------------|---------------------|----------|
| **Aislamiento** | ✅ Total por cliente | 🟡 A nivel aplicación | 🟡 Por esquema | ✅ Flexible según cliente |
| **Escalabilidad** | ❌ Muy limitada | ✅ Excelente | ✅ Muy buena | ✅ Buena |
| **Operación** | ❌ Compleja gestión | ✅ Centralizada | 🟡 Moderada | 🟡 Compleja pero flexible |
| **Costos** | ❌ Muy altos | ✅ Muy eficiente | ✅ Eficiente | 🟡 Moderados |
| **Flexibilidad** | ✅ Máxima por cliente | ❌ Muy limitada | 🟡 Limitada | ✅ Alta |
| **Compliance** | ✅ Máximo control | 🟡 Requiere cuidado | 🟡 Bueno | ✅ Excelente |
| **Implementación** | ✅ Rápida | ✅ Rápida | 🟡 Moderada | 🟡 Compleja |

### Matriz de Decisión

| Estrategia | Aislamiento | Escalabilidad | Flexibilidad | Costos | Recomendación |
|------------|-------------|---------------|--------------|--------|--------------|
| **Híbrido** | Excelente | Buena | Excelente | Moderados | ✅ **Seleccionada** |
| **Multi-Tenant Schema** | Bueno | Muy buena | Limitada | Eficientes | 🟡 Alternativa |
| **Multi-Tenant DB** | Moderado | Excelente | Muy limitada | Muy eficientes | 🟡 Considerada |
| **Single-Tenant** | Excelente | Muy limitada | Máxima | Muy altos | ❌ Descartada |

## 💰 ANÁLISIS DE COSTOS (TCO 3 años)

### Escenario: 4 países, 50GB datos por país

| Solución | Infraestructura DB | Operación | Backup/DR | TCO 3 años |
|----------|-------------------|-----------|-----------|------------|
| **DB per Tenant** | US$48,000/año | US$60,000/año | US$24,000/año | **US$396,000** |
| **Schema per Tenant** | US$18,000/año | US$36,000/año | US$12,000/año | **US$198,000** |
| **Row-Level Security** | US$12,000/año | US$24,000/año | US$6,000/año | **US$126,000** |
| **Hybrid Approach** | US$30,000/año | US$42,000/año | US$18,000/año | **US$270,000** |

## ⚖️ DECISIÓN

**Seleccionamos Hybrid Approach** con la siguiente estrategia:

### Modelo Híbrido por Criticidad

#### Nivel 1: Database per Tenant (Datos Críticos)

```yaml
Servicios con DB separada:
  - Servicio Identidad: Usuarios, roles, permisos
  - Datos Financieros: Transacciones, facturación
  - Datos Personales: PII, información sensible

Configuración:
  talma_identity_peru
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

## 🏗️ IMPLEMENTACIÓN TÉCNICA

### Identificación de Tenant

```csharp
public class TenantContext
{
    public string TenantId { get; set; } // "peru", "ecuador", "colombia", "mexico"
    public string CountryCode { get; set; } // "PE", "EC", "CO", "MX"
    public TenantTier Tier { get; set; } // Critical, Operational, Shared
}

public enum TenantTier
{
    Critical,    // Separate Database
    Operational, // Separate Schema
    Shared       // Row-Level Security
}
```

### Middleware de Tenant Resolution

```csharp
public class TenantResolutionMiddleware
{
    public async Task InvokeAsync(HttpContext context)
    {
        var tenantId = ExtractTenantFromRequest(context);
        var tenantContext = new TenantContext
        {
            TenantId = tenantId,
            CountryCode = GetCountryCode(tenantId),
            Tier = GetTenantTier(context.Request.Path)
        };

        context.Items["TenantContext"] = tenantContext;
        await _next(context);
    }
}
```

### Connection String Strategy

```csharp
public class TenantConnectionFactory
{
    public string GetConnectionString(TenantContext tenant, string service)
    {
        return tenant.Tier switch
        {
            TenantTier.Critical => $"Server=db-{service}-{tenant.TenantId};Database={service}_{tenant.TenantId}",
            TenantTier.Operational => $"Server=db-{service};Database={service};SearchPath={tenant.TenantId}",
            TenantTier.Shared => $"Server=db-shared;Database=shared;ApplicationName={tenant.TenantId}"
        };
    }
}
```

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

### Neutras

- 🔄 **Migración gradual** posible entre niveles según evolución
- 🔄 **Monitoreo diferenciado** por tenant y tier

## 📊 CONFIGURACIÓN POR PAÍS

### Configuraciones Específicas

```yaml
Peru:
  timezone: "America/Lima"
  currency: "PEN"
  regulations: ["SUNAT", "OSINERGMIN"]
  data_residency: true

Ecuador:
  timezone: "America/Guayayquil"
  currency: "USD"
  regulations: ["SRI", "ARCERNNR"]
  data_residency: true

Colombia:
  timezone: "America/Bogota"
  currency: "COP"
  regulations: ["DIAN", "CREG"]
  data_residency: true

Mexico:
  timezone: "America/Mexico_City"
  currency: "MXN"
  regulations: ["SAT", "CRE"]
  data_residency: true
```

### Métricas por Tenant

```yaml
KPIs por País:
  - Usuarios activos por tenant
  - Throughput de transacciones
  - Latencia promedio por región
  - Utilización de recursos por tier
  - Costos por tenant
```

## 📚 REFERENCIAS

- [Multi-Tenant Data Architecture](https://docs.microsoft.com/en-us/azure/sql-database/saas-tenancy-app-design-patterns)
- [PostgreSQL Row Level Security](https://www.postgresql.org/docs/current/ddl-rowsecurity.html)
- [Multi-Tenancy Patterns](https://martinfowler.com/articles/multi-tenant/)
- [GDPR and Multi-Tenancy](https://gdpr.eu/data-protection-impact-assessment-template/)

---

**Decisión tomada por:** Equipo de Arquitectura + Legal + Compliance
**Fecha:** Agosto 2025
**Próxima revisión:** Agosto 2026
