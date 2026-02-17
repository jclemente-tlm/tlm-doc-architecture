---
title: "ADR-005: AWS Parameter Store Configs"
sidebar_position: 5
---

## ✅ ESTADO

Aceptada – Agosto 2025

---

## 🗺️ CONTEXTO

Los servicios corporativos requieren una solución robusta de gestión de configuraciones para:

- **Configuración multi-tenant y multipaís**
- **Portabilidad multi-cloud sin lock-in**
- **Configuración dinámica con hot-reload**
- **Versionado y rollback seguro**
- **Segregación por entorno y herencia**
- **Feature flags para despliegues progresivos**
- **Auditoría completa de cambios**
- **Encriptación de configuraciones sensibles (no secretos)**
- **API centralizada para gestión programática**
- **Disaster recovery con backup y replicación**

La intención estratégica es **evaluar agnosticidad vs facilidad operacional** considerando que la gestión de configuraciones es crítica para la operación y portabilidad.

Alternativas evaluadas:

- **AWS Parameter Store** (Gestionado AWS, integración nativa)
- **Azure App Configuration** (Gestionado Azure, integración nativa)
- **Google Runtime Config** (Gestionado GCP, integración nativa)
- **HashiCorp Consul** (Open source/Enterprise, agnóstico)
- **etcd** (Distributed key-value, Kubernetes ecosystem, CNCF)

## 🔍 COMPARATIVA DE ALTERNATIVAS

| Criterio                  | AWS Parameter Store                             | Azure App Configuration                              | Google Runtime Config                     | HashiCorp Consul                        | etcd                                   |
| ------------------------- | ----------------------------------------------- | ---------------------------------------------------- | ----------------------------------------- | --------------------------------------- | -------------------------------------- |
| **Agnosticidad**          | ❌ Lock-in AWS                                  | ❌ Lock-in Azure                                     | ❌ Lock-in GCP                            | ✅ Agnóstico                            | ✅ OSS, agnóstico                      |
| **Madurez**               | ✅ Alta (2015, AWS native)                      | ⚠️ Media (2020, reciente)                            | ❌ Baja (deprecado 2023)                  | ✅ Muy alta (2014, estable)             | ✅ Muy alta (2013, CNCF core)          |
| **Adopción**              | ✅ Alta (AWS standard)                          | ⚠️ Media (Azure ecosystem)                           | ❌ Deprecado                              | ✅ Muy alta (28K⭐, HashiCorp)          | ✅ Muy alta (47K⭐, CNCF)              |
| **Modelo de gestión**     | ✅ Gestionado (AWS)                             | ✅ Gestionado (Azure)                                | ✅ Gestionado (GCP)                       | ⚠️ Self-hosted                          | ⚠️ Self-hosted                         |
| **Complejidad operativa** | ✅ Baja (0.25 FTE, <5h/sem)                     | ✅ Baja (0.25 FTE, <5h/sem)                          | ⚠️ Media (0.5 FTE, 5-10h/sem)             | ⚠️ Alta (1 FTE, 10-20h/sem)             | ⚠️ Alta (1 FTE, 10-20h/sem)            |
| **Seguridad**             | ✅ Enterprise                                   | ✅ Enterprise                                        | ✅ Enterprise                             | ✅ Máxima                               | ✅ TLS, RBAC                           |
| **Integración .NET**      | ✅ AWSSDK.SimpleSystemsManagement (10M+ DL/mes) | ✅ Azure.Data.AppConfiguration (2M+ DL/mes, .NET 6+) | ⚠️ Google.Cloud.RuntimeConfig (deprecado) | ✅ Consul (500K+ DL/mes, .NET Standard) | ⚠️ dotnet-etcd (50K+ DL/mes, limitado) |
| **Multi-tenancy**         | ⚠️ Por parámetros                               | ✅ Labels                                            | ⚠️ Por proyectos                          | ✅ Namespaces                           | ⚠️ Prefixes                            |
| **Latencia**              | ✅ p95 <10ms                                    | ✅ p95 <50ms                                         | ⚠️ p95 100ms+ variable                    | ✅ p95 <5ms local                       | ✅ p95 <5ms local                      |
| **Rendimiento**           | ✅ 1K+ ops/seg                                  | ⚠️ 100 ops/seg                                       | ⚠️ 100 ops/seg                            | ✅ 10K+ ops/seg local                   | ✅ 10K+ ops/seg local                  |
| **Escalabilidad**         | ✅ Hasta 10K params, 10K+ reads/min (AWS)       | ✅ Hasta 10K+ configs (Azure scale)                  | ⚠️ Deprecado (no aplica)                  | ✅ Hasta 1M+ keys/values (Consul cases) | ✅ Millones keys máx (K8s etcd scale)  |
| **Versionado**            | ✅ Automática                                   | ✅ Automática                                        | ✅ Automática                             | ✅ Muy flexible                         | ✅ Revisions                           |
| **Feature Flags**         | ⚠️ Básico                                       | ✅ Nativo                                            | ⚠️ Básico                                 | ✅ Flexible                             | ⚠️ Manual                              |
| **Auditoría**             | ✅ CloudTrail integrado                         | ✅ Azure Monitor                                     | ✅ Cloud Audit Logs                       | ✅ Completa logs/ACL                    | ⚠️ Manual config                       |
| **Costos**                | ✅ $0.05/10K params (~$5-15/mes)                | ✅ Gratis (10K requests/día) + $0.05/10K             | ✅ Incluido en GCP                        | ⚠️ $0 licencia + ~$100-300/mes infra    | ✅ $0 licencia + ~$100-200/mes infra   |

**Leyenda:** ✅ Cumple completamente | ⚠️ Cumple parcialmente | ❌ No cumple

## ✔️ DECISIÓN

Se selecciona **AWS Parameter Store** como solución principal para la gestión de configuraciones, desacoplada mediante interfaces y adaptadores. La arquitectura soporta migración a Consul u otras soluciones según necesidades de portabilidad o despliegue híbrido.

### Justificación

- Gestión centralizada, segura y versionada
- Portabilidad y despliegue multi-cloud
- Desacoplamiento del backend sin impacto en la lógica de negocio
- Integración gestionada, bajo costo y facilidad de operación
- Consul es opción madura para escenarios on-premises o híbridos

### Alternativas descartadas

- **etcd:** distributed key-value store robusto pero orientado a Kubernetes ecosystem, complejidad operativa alta (clustering, quorum, backups), menor integración .NET vs Parameter Store, overhead para uso simple config
- **Azure App Configuration:** lock-in Azure, infraestructura AWS ya establecida, menor portabilidad
- **Google Runtime Config:** lock-in GCP, **vendor adicional sin infraestructura GCP existente** (requiere cuenta/proyecto/billing GCP activo), **SDK .NET adicional** (Google.Cloud.RuntimeConfig) a mantener, **complejidad multi-vendor** (AWS + Azure + GCP) sin beneficio diferencial, **overhead operativo** (tercera consola cloud, tercera facturación, tercer soporte), SDK .NET limitado, menor madurez vs otros
- **HashiCorp Consul:** mayor complejidad operativa y mantenimiento, requiere expertise, costos infraestructura

---

## ⚠️ CONSECUENCIAS

### Positivas

- El código debe desacoplarse del proveedor concreto mediante interfaces
- Se facilita la portabilidad y despliegue híbrido

### Negativas (Riesgos y Mitigaciones)

- **Vendor lock-in cloud:** mitigado con interfaces y adaptadores.
- **Complejidad operativa Consul:** mitigada con automatización y monitoreo.
- **Costos variables cloud:** monitoreo y revisión anual.

---

## 📚 REFERENCIAS

- [AWS Parameter Store](https://aws.amazon.com/systems-manager/features/#Parameter_Store)
- [Azure App Configuration](https://azure.microsoft.com/en-us/services/app-configuration/)
- [Google Runtime Config](https://cloud.google.com/deployment-manager/runtime-configurator)
- [Consul](https://www.consul.io/)
