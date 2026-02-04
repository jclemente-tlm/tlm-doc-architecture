# Matriz de Trazabilidad: Fundamentos Corporativos

**Propósito:** Visualizar la trazabilidad completa desde Principios hasta Convenciones.

---

## 📊 Estructura General

```mermaid
graph TD
    P[Principios<br/>POR QUÉ] --> L[Lineamientos<br/>QUÉ LOGRAR]
    L --> E[Estándares<br/>CON QUÉ]
    E --> C[Convenciones<br/>CÓMO ESCRIBIR]

    style P fill:#e1f5ff
    style L fill:#fff4e6
    style E fill:#e8f5e9
    style C fill:#f3e5f5
```

---

## 🔐 Seguridad desde el Diseño

### Trazabilidad Completa

```mermaid
graph LR
    P1[Principio:<br/>Seguridad desde<br/>el Diseño] --> L1[Lineamiento:<br/>Seguridad desde<br/>el Diseño]
    L1 --> E1[Estándar:<br/>APIs/Seguridad<br/>JWT/OAuth]
    L1 --> E2[Estándar:<br/>Secrets Management<br/>AWS/Azure]
    E1 --> C1[Convención:<br/>Headers HTTP<br/>Authorization Bearer]
    E2 --> C2[Convención:<br/>Manejo Secretos<br/>Never commit, .env]

    style P1 fill:#ffebee
    style L1 fill:#fff3e0
    style E1 fill:#e8f5e9
    style E2 fill:#e8f5e9
    style C1 fill:#f3e5f5
    style C2 fill:#f3e5f5
```

### Referencias

| Nivel           | Documento                 | Ubicación                                                                                                          |
| --------------- | ------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| **Principio**   | Seguridad desde el Diseño | [principios/seguridad/01-seguridad-desde-el-diseno.md](principios/seguridad/01-seguridad-desde-el-diseno.md)       |
| **Lineamiento** | Seguridad desde el Diseño | [lineamientos/seguridad/01-seguridad-desde-el-diseno.md](lineamientos/seguridad/01-seguridad-desde-el-diseno.md)   |
| **Estándar**    | APIs - Seguridad          | [estandares/apis/02-seguridad-apis.md](estandares/apis/02-seguridad-apis.md)                                       |
| **Estándar**    | Secrets Management        | [estandares/infraestructura/03-secrets-management.md](estandares/infraestructura/03-secrets-management.md)         |
| **Estándar**    | APIs REST                 | [estandares/apis/api-rest.md](estandares/apis/api-rest.md) (incluye headers HTTP)                                  |
| **Estándar**    | Secrets Management        | [estandares/seguridad/secrets-management.md](estandares/seguridad/secrets-management.md) (incluye manejo secretos) |

---

## 👁️ Observabilidad desde el Diseño

### Trazabilidad Completa

```mermaid
graph LR
    P2[Principio:<br/>Observabilidad<br/>desde el Diseño] --> L2[Lineamiento:<br/>Observabilidad]
    L2 --> E3[Estándar:<br/>Logging Estructurado<br/>Serilog]
    L2 --> E4[Estándar:<br/>Monitoreo y Métricas<br/>OpenTelemetry]
    E3 --> C3[Convención:<br/>Niveles de Log<br/>INFO/WARN/ERROR]
    E3 --> C4[Convención:<br/>Correlation IDs<br/>UUID format]

    style P2 fill:#e3f2fd
    style L2 fill:#fff9c4
    style E3 fill:#c8e6c9
    style E4 fill:#c8e6c9
    style C3 fill:#f8bbd0
    style C4 fill:#f8bbd0
```

### Referencias

| Nivel           | Documento                      | Ubicación                                                                                                                    |
| --------------- | ------------------------------ | ---------------------------------------------------------------------------------------------------------------------------- |
| **Principio**   | Observabilidad desde el Diseño | [principios/arquitectura/05-observabilidad-desde-el-diseno.md](principios/arquitectura/05-observabilidad-desde-el-diseno.md) |
| **Lineamiento** | Observabilidad                 | [lineamientos/arquitectura/05-observabilidad.md](lineamientos/arquitectura/05-observabilidad.md)                             |
| **Estándar**    | Logging Estructurado           | [estandares/observabilidad/01-logging.md](estandares/observabilidad/01-logging.md)                                           |
| **Estándar**    | Monitoreo y Métricas           | [estandares/observabilidad/02-monitoreo-metricas.md](estandares/observabilidad/02-monitoreo-metricas.md)                     |
| **Estándar**    | Logging Estructurado           | [estandares/operabilidad/logging.md](estandares/operabilidad/logging.md) (incluye niveles y correlation IDs)                 |

---

## 🧪 Calidad desde el Diseño

### Trazabilidad Completa

```mermaid
graph LR
    P3[Principio:<br/>Calidad desde<br/>el Diseño] --> L3[Lineamiento:<br/>Testing y Calidad]
    L3 --> E5[Estándar:<br/>Unit Tests<br/>xUnit]
    L3 --> E6[Estándar:<br/>Integration Tests<br/>TestContainers]
    L3 --> E7[Estándar:<br/>E2E Tests<br/>Playwright]
    L3 --> E8[Estándar:<br/>Código C#<br/>.NET 8, SOLID]
    E8 --> C5[Convención:<br/>Naming C#<br/>PascalCase]

    style P3 fill:#fce4ec
    style L3 fill:#fff8e1
    style E5 fill:#dcedc8
    style E6 fill:#dcedc8
    style E7 fill:#dcedc8
    style E8 fill:#dcedc8
    style C5 fill:#e1bee7
```

### Referencias

| Nivel           | Documento               | Ubicación                                                                                                               |
| --------------- | ----------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| **Principio**   | Calidad desde el Diseño | [principios/operabilidad/03-calidad-desde-el-diseno.md](principios/operabilidad/03-calidad-desde-el-diseno.md)          |
| **Lineamiento** | Testing y Calidad       | [lineamientos/operabilidad/04-testing-y-calidad.md](lineamientos/operabilidad/04-testing-y-calidad.md)                  |
| **Estándar**    | Testing Unitario        | [estandares/testing/01-unit-tests.md](estandares/testing/01-unit-tests.md)                                              |
| **Estándar**    | Testing Integración     | [estandares/testing/02-integration-tests.md](estandares/testing/02-integration-tests.md)                                |
| **Estándar**    | Testing E2E             | [estandares/testing/03-e2e-tests.md](estandares/testing/03-e2e-tests.md)                                                |
| **Estándar**    | C# y .NET               | [estandares/desarrollo/csharp-dotnet.md](estandares/desarrollo/csharp-dotnet.md)                                        |
| **Estándar**    | C# y .NET               | [estandares/desarrollo/csharp-dotnet.md](estandares/desarrollo/csharp-dotnet.md) (incluye convenciones de nomenclatura) |

---

## 🤖 Automatización como Principio

### Trazabilidad Completa

```mermaid
graph LR
    P4[Principio:<br/>Automatización<br/>como Principio] --> L4[Lineamiento:<br/>Automatización]
    P4 --> L5[Lineamiento:<br/>IaC]
    L4 --> E9[Estándar:<br/>Docker<br/>Multi-stage]
    L5 --> E10[Estándar:<br/>IaC<br/>Terraform/CDK]
    E10 --> C6[Convención:<br/>Naming AWS<br/>Prefijos env]
    E10 --> C7[Convención:<br/>Tags Metadatos<br/>Environment, Owner]

    style P4 fill:#e0f2f1
    style L4 fill:#fff3e0
    style L5 fill:#fff3e0
    style E9 fill:#c5e1a5
    style E10 fill:#c5e1a5
    style C6 fill:#d1c4e9
    style C7 fill:#d1c4e9
```

### Referencias

| Nivel           | Documento                     | Ubicación                                                                                                                                |
| --------------- | ----------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| **Principio**   | Automatización como Principio | [principios/operabilidad/01-automatizacion-como-principio.md](principios/operabilidad/01-automatizacion-como-principio.md)               |
| **Lineamiento** | Automatización                | [lineamientos/operabilidad/01-automatizacion.md](lineamientos/operabilidad/01-automatizacion.md)                                         |
| **Lineamiento** | Infraestructura como Código   | [lineamientos/operabilidad/02-infraestructura-como-codigo.md](lineamientos/operabilidad/02-infraestructura-como-codigo.md)               |
| **Estándar**    | Docker                        | [estandares/infraestructura/01-docker.md](estandares/infraestructura/01-docker.md)                                                       |
| **Estándar**    | IaC                           | [estandares/infraestructura/02-infraestructura-como-codigo.md](estandares/infraestructura/02-infraestructura-como-codigo.md)             |
| **Estándar**    | Infraestructura como Código   | [estandares/infraestructura/infrastructure-as-code.md](estandares/infraestructura/infrastructure-as-code.md) (incluye naming AWS y tags) |

---

## 🌐 Contratos de Integración

### Trazabilidad Completa

```mermaid
graph LR
    P5[Principio:<br/>Contratos de<br/>Comunicación] --> L6[Lineamiento:<br/>Diseño de APIs]
    L6 --> E11[Estándar:<br/>Diseño REST<br/>ASP.NET Core]
    L6 --> E12[Estándar:<br/>Versionado APIs<br/>Semantic Versioning]
    L6 --> E13[Estándar:<br/>OpenAPI/Swagger<br/>Documentación]
    E11 --> C8[Convención:<br/>Naming Endpoints<br/>kebab-case]
    E11 --> C9[Convención:<br/>Formato Respuestas<br/>RFC 7807]

    style P5 fill=#e8eaf6
    style L6 fill:#fffde7
    style E11 fill=#b2dfdb
    style E12 fill=#b2dfdb
    style E13 fill=#b2dfdb
    style C8 fill=#ce93d8
    style C9 fill=#ce93d8
```

### Referencias

| Nivel           | Documento                 | Ubicación                                                                                                          |
| --------------- | ------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| **Principio**   | Contratos de Comunicación | [principios/arquitectura/06-contratos-de-comunicacion.md](principios/arquitectura/06-contratos-de-comunicacion.md) |
| **Lineamiento** | Diseño de APIs            | [lineamientos/arquitectura/06-diseno-de-apis.md](lineamientos/arquitectura/06-diseno-de-apis.md)                   |
| **Estándar**    | Diseño REST               | [estandares/apis/01-diseno-rest.md](estandares/apis/01-diseno-rest.md)                                             |
| **Estándar**    | Versionado APIs           | [estandares/apis/04-versionado.md](estandares/apis/04-versionado.md)                                               |
| **Estándar**    | OpenAPI/Swagger           | [estandares/documentacion/03-openapi-swagger.md](estandares/documentacion/03-openapi-swagger.md)                   |
| **Estándar**    | APIs REST                 | [estandares/apis/api-rest.md](estandares/apis/api-rest.md) (incluye naming endpoints y formato respuestas)         |

---

## 📊 Resumen de Cobertura

### Estadísticas

| Categoría           | Principios | Lineamientos | Estándares | Convenciones |
| ------------------- | ---------- | ------------ | ---------- | ------------ |
| **Seguridad**       | 6          | 4            | 1          | 1            |
| **Arquitectura**    | 8          | 8            | -          | -            |
| **Operabilidad**    | 3          | 4            | -          | -            |
| **Datos**           | 3          | 3            | -          | -            |
| **APIs**            | -          | 1            | 5          | 4            |
| **Código**          | -          | -            | 3          | 4            |
| **Infraestructura** | -          | 1            | 4          | 3            |
| **Testing**         | -          | 1            | 3          | -            |
| **Observabilidad**  | -          | 1            | 2          | 2            |
| **Mensajería**      | -          | 1            | 2          | -            |
| **Documentación**   | -          | 1            | 3          | -            |
| **Git**             | -          | -            | -          | 5            |
| **Base de Datos**   | -          | -            | -          | 2            |
| **TOTAL**           | **19**     | **21**       | **22**     | **21**       |

### Cobertura de Trazabilidad

```mermaid
pie title Cobertura de Trazabilidad
    "Con trazabilidad completa" : 15
    "Con trazabilidad parcial" : 25
    "Sin trazabilidad" : 23
```

**Meta:** 100% con trazabilidad completa

---

## 🎯 Validación

### Verificar Trazabilidad

Para cada estándar, verificar:

1. ✅ Tiene referencia a al menos 1 Lineamiento
2. ✅ Tiene referencia a al menos 1 Principio
3. ✅ Tiene referencia bidireccional con Convenciones (si aplica)

### Script de Validación

```bash
# Validar trazabilidad
./scripts/validate-traceability.sh

# Generar diagrama de trazabilidad
./scripts/generate-traceability-diagram.sh
```

---

## 📝 Mantenimiento

**Actualizar cuando:**

- Se crea un nuevo documento
- Se modifica trazabilidad
- Se reorganiza estructura

**Responsable:**

- Equipo de Arquitectura

**Frecuencia:**

- Cada sprint
- Antes de releases mayores

---

_Esta matriz asegura que todos los documentos están correctamente trazados desde principios hasta implementación._
