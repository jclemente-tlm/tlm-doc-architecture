---
title: "ADR-017: Versionado de APIs"
sidebar_position: 17
---

## ✅ ESTADO

Aceptada – Agosto 2025

---

## 🗺️ CONTEXTO

Los servicios corporativos multi-tenant requieren una estrategia de versionado de APIs que permita:

- **Evolución controlada** de contratos sin romper clientes existentes
- **Compatibilidad hacia atrás** durante períodos de transición
- **Multi-tenancy** con versiones específicas por país/tenant
- **Deprecación gradual** de versiones obsoletas
- **Documentación automática** con `OpenAPI 3.0`
- **Gestión de ciclo de vida** con políticas claras de soporte
- **Integración con `API Gateway`** para enrutamiento y políticas
- **Monitoreo de adopción** para planificar deprecaciones

La estrategia prioriza **flexibilidad evolutiva, simplicidad operativa y compatibilidad con herramientas estándar**.

Alternativas evaluadas:

- **Path Versioning** (`/v1/`, `/v2/` en URL)
- **Header Versioning** (`Accept-Version`, `API-Version`)
- **Query Parameter** (`?version=1.0`)
- **Content Negotiation** (`Accept: application/vnd.api+json;version=1`)
- **Subdomain Versioning** (`v1.api.domain.com`)
- **Sin versionado** (breaking changes directos)

## 🔍 COMPARATIVA DE ALTERNATIVAS

### Comparativa Cualitativa

| Criterio              | Path Versioning | Header Versioning | Query Parameter | Content Negotiation | Subdomain         | Sin Versionado |
|----------------------|-----------------|-------------------|-----------------|---------------------|-------------------|----------------|
| **Visibilidad**      | ✅ Muy visible en `URL` | 🟡 Oculto en headers | 🟡 Visible en query | 🟡 Oculto en `Accept` | ✅ Visible en subdomain | ❌ Invisible |
| **Herramientas**     | ✅ Soporte universal | 🟡 Requiere configuración | 🟡 Soporte básico | ✅ Soporte HTTP estándar | 🟡 Configuración DNS | ❌ Sin soporte |
| **Operación**        | ✅ Simple routing | 🟡 Lógica en headers | 🟡 Parsing parámetros | 🟡 Content negotiation | 🟡 Gestión DNS | ✅ Sin complejidad |
| **API Gateway**      | ✅ Routing nativo | ✅ Header routing | 🟡 Query routing | 🟡 Content routing | ✅ Subdomain routing | ❌ Sin routing |
| **Caching**          | ✅ Cache por `path` | 🟡 `Vary` headers | 🟡 Query cache | 🟡 `Vary Accept` | ✅ Cache por subdomain | ✅ Cache simple |
| **Adopción**         | ✅ Estándar de facto | 🟡 Usado en APIs | 🟡 Menos común | 🟡 REST puro | 🟡 Menos común | ❌ Mala práctica |
| **Flexibilidad**     | ✅ Rutas independientes | ✅ Headers flexibles | 🟡 Parámetros simples | ✅ Negociación rica | 🟡 Subdominios fijos | ❌ Sin flexibilidad |

### Matriz de Decisión

| Estrategia              | Visibilidad | Herramientas | API Gateway | Adopción | Recomendación         |
|------------------------|-------------|--------------|-------------|----------|-----------------------|
| **Path Versioning**    | Excelente   | Universal    | Nativo      | Estándar | ✅ **Seleccionada**    |
| **Subdomain Versioning**| Excelente  | Configuración| Bueno       | Moderada | 🟡 Alternativa         |
| **Content Negotiation**| Oculta      | Estándar HTTP| Moderado    | Moderada | 🟡 Considerada         |
| **Header Versioning**  | Oculta      | Configuración| Bueno       | Moderada | 🟡 Considerada         |
| **Query Parameter**    | Visible     | Básico       | Moderado    | Baja     | ❌ Descartada          |
| **Sin Versionado**     | No aplica   | No aplica    | No aplica   | Mala práctica | ❌ Descartada      |

---

## 💰 ANÁLISIS DE COSTOS (TCO 3 años)

> **Supuesto:** 5 `APIs`, 10M requests/mes, 3 versiones activas. Costos estimados para implementación, operación y mantenimiento.

| Estrategia              | Implementación | Operación    | Mantenimiento   | TCO 3 años   |
|------------------------|---------------|--------------|-----------------|--------------|
| **Path Versioning**    | US$15,000     | US$6,000/año | US$12,000/año   | US$69,000    |
| **Header Versioning**  | US$25,000     | US$9,000/año | US$18,000/año   | US$106,000   |
| **Content Negotiation**| US$30,000     | US$12,000/año| US$24,000/año   | US$138,000   |
| **Subdomain Versioning**| US$20,000    | US$15,000/año| US$15,000/año   | US$110,000   |
| **Query Parameter**    | US$10,000     | US$12,000/año| US$21,000/año   | US$109,000   |
| **Sin Versionado**     | US$0          | US$0         | US$50,000/año   | US$150,000   |

### Escenario Alto Volumen: 20 `APIs`, 100M requests/mes, multi-región

| Estrategia              | TCO 3 años   | Complejidad Operacional         |
|------------------------|--------------|---------------------------------|
| **Path Versioning**    | US$180,000   | Baja - Enrutamiento simple      |
| **Header Versioning**  | US$300,000   | Alta - Lógica personalizada     |
| **Content Negotiation**| US$420,000   | Muy alta - Parsing complejo     |
| **Subdomain Versioning**| US$360,000  | Media - Gestión DNS             |
| **Query Parameter**    | US$330,000   | Alta - Validación compleja      |
| **Sin Versionado**     | US$900,000   | Muy alta - Breaking changes     |

### Factores de Costo Adicionales

```yaml
Consideraciones Path Versioning:
  Documentación: OpenAPI automática (incluida)
  Testing: Herramientas estándar vs US$15K/año custom
  Monitoreo: Métricas por versión (incluidas)
  Deprecación: Proceso automatizado vs US$25K manual
  Migración: US$0 entre plataformas vs US$40K propietario
  Capacitación: US$3K vs US$15K para estrategias complejas
  Rollback: Instantáneo vs US$10K/incidente en otras estrategias
```

---

## ✔️ DECISIÓN

Se adopta el versionado en `path` (por ejemplo, `/v1/`) como estrategia estándar para todas las `APIs` públicas y privadas.

## Justificación

- Es la opción más explícita y ampliamente soportada.
- Facilita la coexistencia de múltiples versiones.
- Compatible con herramientas de documentación (`OpenAPI`), monitoreo y `API Gateway`.
- Sencillo de implementar y mantener.

## Alternativas descartadas

- **Header Versioning:** menos visible, mayor complejidad en proxies/gateways
- **Query Parameter:** considerado anti-pattern, cache problems
- **Content Negotiation:** complejidad innecesaria para versioning simple
- **Subdomain Versioning:** gestión DNS compleja, mayor costo operativo
- **Sin versionado:** breaking changes directos - mala práctica evitable

---

## ⚠️ CONSECUENCIAS

- Todas las APIs públicas deben usar path versioning: `/api/v{version}/`
- Configuración estándar con `AspNetCore.Mvc.Versioning` (ver [Estándar de Versionado](../../fundamentos-corporativos/estandares/apis/04-versionado.md))
- Periodo de deprecación mínimo: 6 meses
- Swagger multi-version obligatorio
- Headers `api-supported-versions` y `api-deprecated-versions` en responses

---

## 📚 REFERENCIAS

- [REST API Versioning Best Practices](https://restfulapi.net/versioning/)
- [Estándar: Versionado de APIs](../../fundamentos-corporativos/estandares/apis/04-versionado.md)
- [ADR-002: APIs REST Estándar](./adr-002-estandard-apis-rest.md)
- [Microsoft API Versioning](https://github.com/dotnet/aspnet-api-versioning)

- **Header Versioning:** menos visible y menos soportado por herramientas, requiere gestión de la versión en el `header` de la petición.
- **Query Parameter:** poco común y menos claro, la versión se pasa como parámetro en la `query string`.
- **Sin versionado:** no permite evolución controlada ni coexistencia de versiones, dificulta la gestión de cambios en los contratos de `API`.

---

## ⚠️ CONSECUENCIAS

- Todas las `APIs` deben exponer la versión en el `path`.
- Se recomienda documentar claramente los cambios entre versiones y mantener políticas de deprecación visibles.

---

## 📚 REFERENCIAS

- [REST API Versioning Mejores Prácticas](https://restfulapi.net/versioning/)
- [OpenAPI Specification – Versioning](https://swagger.io/docs/specification/api-host-and-base-path/)
- [arc42: Decisiones de arquitectura](https://arc42.org/decision/)
