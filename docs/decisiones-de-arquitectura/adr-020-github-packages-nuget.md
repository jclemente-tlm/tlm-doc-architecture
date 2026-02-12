---
title: "ADR-020: GitHub Packages NuGet"
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

Alternativas evaluadas:

- **GitHub Packages** (integrado GitHub, control granular)
- **AWS CodeArtifact** (gestionado AWS, integración IAM)
- **Azure Artifacts** (gestionado Azure, .NET-nativo)
- **MyGet** (SaaS NuGet especializado)
- **ProGet** (Inedo, self-hosted/cloud)
- **Artifactory/Nexus** (enterprise repository manager)
- **Feed privado NuGet.org** (simple, limitado)

---

## 🔍 COMPARATIVA DE ALTERNATIVAS

### Comparativa Cualitativa

| Criterio              | GitHub Packages                                                              | AWS CodeArtifact                        | Azure Artifacts                           | MyGet                            | ProGet                                    | Artifactory/Nexus                                              | Feed privado NuGet.org                                     |
| --------------------- | ---------------------------------------------------------------------------- | --------------------------------------- | ----------------------------------------- | -------------------------------- | ----------------------------------------- | -------------------------------------------------------------- | ---------------------------------------------------------- |
| **Agnosticidad**      | ⚠️ Parcialmente agnóstico (compatible con cualquier nube, depende de GitHub) | ❌ No agnóstico (dependencia de AWS)    | ❌ No agnóstico (dependencia de Azure)    | ✅ SaaS independiente, agnóstico | ✅ Agnóstico (self-hosted/cloud)          | ✅ Agnóstico (on-prem/cloud, sin lock-in)                      | ⚠️ Parcial (depende de internet)                           |
| **Operación**         | ⚠️ A cargo del usuario (self-service, administración propia)                 | 🟢 A cargo de AWS (servicio gestionado) | 🟢 A cargo de Azure (servicio gestionado) | ✅ Totalmente gestionado SaaS    | ⚠️ Self-hosted o cloud gestionado         | ⚠️ A cargo del usuario (administración propia)                 | ⚠️ A cargo del usuario (manual)                            |
| **Control de acceso** | ✅ Roles por repositorio y PAT                                               | ✅ IAM y políticas AWS                  | ✅ Roles por proyecto                     | ✅ Equipos y permisos granulares | ✅ Control completo                       | ✅ Control completo                                            | ❌ Limitado                                                |
| **Costo**             | ✅ Sin costo adicional (incluido en GitHub)                                  | ⚠️ Tarifa variable (pago por uso)       | ⚠️ Tarifa fija mensual (por feed)         | ⚠️ US$11-45/mes (10-100 feeds)   | ⚠️ US$300/año base (ProGet Free limitado) | ⚠️ Tarifa variable (licencia, infraestructura y mantenimiento) | ✅ Gratis (si es on-premise, puede tener costo de hosting) |
| **Ecosistema .NET**   | ✅ Excelente soporte                                                         | ✅ Soporte oficial                      | ✅ Soporte oficial                        | ✅ Especializado NuGet           | ✅ Excelente, diseñado para .NET          | ✅ Soporte oficial                                             | ⚠️ Limitado                                                |

**Leyenda:** ✅ Cumple completamente | ⚠️ Cumple parcialmente | ❌ No cumple

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

## Alternativas descartadas

- **AWS CodeArtifact:** lock-in AWS, costos variables (US$0.05/GB storage + US$0.05/request), configuración más compleja vs GitHub
- **Azure Artifacts:** lock-in Azure, costos US$2/usuario/mes (5 usuarios gratis), infraestructura AWS ya establecida
- **MyGet:** costos SaaS crecientes (US$11-45/mes), funcionalidad similar GitHub Packages sin ventaja diferencial
- **ProGet:** self-hosted requiere infraestructura y mantenimiento, costos US$300/año base, sobrede-dimensionado para necesidades actuales
- **Artifactory/Nexus:** enterprise-grade pero complejo, costos licencias + infraestructura, overhead operativo innecesario para escala actual
- **Feed privado NuGet.org:** control acceso limitado, seguridad básica, menor integración CI/CD

---

## ⚠️ CONSECUENCIAS

- Todos los microservicios deberán configurar `NuGet.config` apuntando al feed privado de GitHub.
- CI/CD debe gestionar autenticación mediante PAT y publicar los paquetes automáticamente.
- Cualquier cambio futuro de proveedor (por ejemplo, migrar a Artifactory) requerirá un nuevo ADR.
- Se debe documentar el uso y acceso al feed privado internamente.

---

## 📚 REFERENCIAS

- [GitHub Packages](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-nuget-registry)
- [AWS CodeArtifact](https://aws.amazon.com/codeartifact/)
- [Azure Artifacts](https://azure.microsoft.com/en-us/services/devops/artifacts/)
- [MyGet](https://www.myget.org/)
- [ProGet](https://inedo.com/proget)
- [NuGet.config reference](https://learn.microsoft.com/en-us/nuget/consume-packages/configuring-nuget-behavior)
- [Arc42: Decisiones de arquitectura](https://arc42.org/decision/)
