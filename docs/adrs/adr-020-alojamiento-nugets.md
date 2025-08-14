---
title: "ADR-020: Alojamiento de NuGets Internos"
sidebar_position: 20
---

## ✅ ESTADO

Aceptada – Agosto 2025

---

## 🗺️ CONTEXTO

Todos los microservicios corporativos utilizan NuGets internos para compartir código común, incluyendo:

- `Observability.Shared` (logging, métricas, tracing, health checks)
- `SecretsAndConfig.Shared` (gestión de secretos y configuraciones)
- Otros paquetes comunes que puedan surgir en el futuro

Se requiere una solución que permita:

- **Control de acceso**: sólo desarrolladores y pipelines autorizados pueden publicar/consumir paquetes.
- **Versionamiento confiable**: SemVer y control de versiones estables/pre-release.
- **Reutilización y consistencia**: todos los servicios consumen las mismas versiones.
- **Compatibilidad con AWS**: microservicios desplegados en AWS.
- **Automatización CI/CD**: publicar NuGets automáticamente en pipelines.

---

## 🔍 COMPARATIVA DE ALTERNATIVAS

### Comparativa Cualitativa

| Criterio | GitHub Packages | AWS CodeArtifact | Azure Artifacts | Artifactory/Nexus | Feed privado NuGet.org |
|----------|----------------|------------------|----------------|------------------|-----------------------|
| **Agnosticidad** | 🟡 Parcialmente agnóstico (compatible con cualquier nube, depende de GitHub) | ❌ No agnóstico (dependencia de AWS) | ❌ No agnóstico (dependencia de Azure) | ✅ Agnóstico (on-prem/cloud, sin lock-in) | 🟡 Parcial (depende de internet) |
| **Operación** | 🟡 A cargo del usuario (self-service, administración propia) | 🟢 A cargo de AWS (servicio gestionado) | 🟢 A cargo de Azure (servicio gestionado) | 🟡 A cargo del usuario (administración propia) | 🟡 A cargo del usuario (manual) |
| **Control de acceso** | ✅ Roles por repositorio y PAT | ✅ IAM y políticas AWS | ✅ Roles por proyecto | ✅ Control completo | ❌ Limitado |
| **Costo** | ✅ Sin costo adicional (incluido en GitHub) | 🟡 Tarifa variable (pago por uso) | 🟡 Tarifa fija mensual (por feed) | 🟡 Tarifa variable (licencia, infraestructura y mantenimiento) | ✅ Gratis (si es on-premise, puede tener costo de hosting) |
| **Ecosistema .NET** | ✅ Excelente soporte | ✅ Soporte oficial | ✅ Soporte oficial | ✅ Soporte oficial | 🟡 Limitado |

### Matriz de Decisión

| Solución | Agnosticidad | Operación | Control de acceso | Costo | Ecosistema .NET | Recomendación |
|----------|--------------|-----------|-------------------|-------|-----------------|---------------|
| **GitHub Packages** | Parcial | Excelente | Excelente | Excelente | Excelente | ✅ Seleccionada |
| AWS CodeArtifact | No | Excelente | Excelente | Media | Excelente | 🟡 Alternativa |
| Azure Artifacts | No | Buena | Buena | Media | Excelente | 🟡 Alternativa |
| Artifactory / Nexus | Sí | Media | Excelente | Media | Excelente | 🟡 Considerada |
| Feed privado NuGet.org | Parcial | Baja | Limitado | Alta | Limitado | ❌ Descartada |

---

## ✔️ DECISIÓN

Se selecciona **GitHub Packages** como alojamiento de los NuGets internos.

---

## Justificación

- Aprovecha la infraestructura de repositorios existente en GitHub.
- Permite control de acceso granular mediante PAT y permisos de repositorio.
- Compatible con microservicios desplegados en AWS, sin infraestructura adicional.
- Facilita CI/CD con GitHub Actions, automatizando empaquetado y publicación de NuGets.
- Versionamiento consistente con soporte para pre-release para pruebas internas.

---

## ⚠️ CONSECUENCIAS

- Todos los microservicios deberán configurar `NuGet.config` apuntando al feed privado de GitHub.
- CI/CD debe gestionar autenticación mediante PAT y publicar los paquetes automáticamente.
- Cualquier cambio futuro de proveedor (por ejemplo, migrar a Artifactory) requerirá un nuevo ADR.
- Se debe documentar el uso y acceso al feed privado internamente.

---

## 📚 REFERENCIAS

- [GitHub Packages](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-nuget-registry)
- [NuGet.config reference](https://learn.microsoft.com/en-us/nuget/consume-packages/configuring-nuget-behavior)
- [Arc42: Decisiones de arquitectura](https://arc42.org/decision/)
