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
- **HashiCorp Consul** (Open source/enterprise, agnóstico)
- **etcd** (Distributed key-value, Kubernetes ecosystem, CNCF)

---

## 🔍 COMPARATIVA DE ALTERNATIVAS

| Criterio                      | AWS Parameter Store                             | Azure App Configuration                              | HashiCorp Consul                        | etcd                                   |
| ----------------------------- | ----------------------------------------------- | ---------------------------------------------------- | --------------------------------------- | -------------------------------------- |
| **Agnosticidad**              | ❌ Lock-in AWS                                  | ❌ Lock-in Azure                                     | ✅ Agnóstico                            | ✅ OSS, agnóstico                      |
| **Madurez**                   | ✅ Alta (2015, AWS native)                      | ⚠️ Media (2020, reciente)                            | ✅ Muy alta (2014, estable)             | ✅ Muy alta (2013, CNCF core)          |
| **Adopción**                  | ✅ Alta (AWS standard)                          | ⚠️ Media (Azure ecosystem)                           | ✅ Muy alta (líder service mesh/KV)         | ✅ Muy alta (core CNCF, Kubernetes)    |
| **Modelo de gestión**         | ✅ Gestionado (AWS)                             | ✅ Gestionado (Azure)                                | ⚠️ Self-hosted                          | ⚠️ Self-hosted                         |
| **Complejidad operativa**     | ✅ Baja (0.25 FTE, `<5h/sem)`                   | ✅ Baja (0.25 FTE, `<5h/sem)`                        | ⚠️ Alta (1 FTE, 10-20h/sem)             | ⚠️ Alta (1 FTE, 10-20h/sem)            |
| **Seguridad**                 | ✅ Enterprise                                   | ✅ Enterprise                                        | ✅ Máxima                               | ✅ TLS, RBAC                           |
| **Integración .NET**          | ✅ `AWSSDK.SimpleSystemsManagement` (.NET 6+)      | ✅ `Azure.Data.AppConfiguration` (.NET 6+)             | ✅ `Consul` (.NET Standard 2.0+)        | ⚠️ `dotnet-etcd` (.NET Standard 2.0+, limitado) |
| **Multi-tenancy**             | ⚠️ Por parámetros                               | ✅ Labels                                            | ✅ Namespaces                           | ⚠️ Prefixes                            |
| **Latencia**                  | ✅ p95 `<10ms `                                 | ✅ p95 `<50ms `                                      | ✅ p95 `<5ms `local                     | ✅ p95 `<5ms `local                    |
| **Rendimiento**               | ✅ 1K+ ops/seg                                  | ⚠️ 100 ops/seg                                       | ✅ 10K+ ops/seg local                   | ✅ 10K+ ops/seg local                  |
| **Escalabilidad**             | ✅ Hasta 10K params, 10K+ reads/min (AWS)       | ✅ Hasta 10K+ configs (Azure scale)                  | ✅ Hasta 1M+ keys/values (Consul cases) | ✅ Millones keys máx (K8s etcd scale)  |
| **Versionado**                | ✅ Automática                                   | ✅ Automática                                        | ✅ Muy flexible                         | ✅ Revisions                           |
| **Feature Flags**             | ⚠️ Básico                                       | ✅ Nativo                                            | ✅ Flexible                             | ⚠️ Manual                              |
| **Auditoría**                 | ✅ CloudTrail integrado                         | ✅ Azure Monitor                                     | ✅ Completa logs/ACL                    | ⚠️ Manual config                       |
| **Recarga en caliente**       | ⚠️ Polling necesario (sin push)                 | ✅ Configuration refresh nativo                      | ✅ Watch API para cambios real-time     | ✅ Watch API nativo                    |
| **Validación de esquemas**    | ❌ No soportado                                 | ✅ JSON Schema validation                            | ⚠️ Via policies (manual)                | ⚠️ Via admission controllers           |
| **Notificaciones de cambios** | ✅ EventBridge para cambios                     | ✅ Event Grid notifications                          | ⚠️ Watch API (manual)                   | ⚠️ Watch API (manual)                  |
| **Opciones de cifrado**       | ✅ KMS keys (AWS managed, customer managed)     | ✅ Customer-managed keys, Azure Key Vault            | ✅ Encryption in transit + at rest      | ✅ Encryption at rest nativo           |
| **Límites de jerarquía**      | ✅ 15 niveles profundidad                       | ✅ Sin límite de profundidad                         | ✅ Flexible folder/namespace structure  | ✅ Namespace hierarchy ilimitado       |
| **Costos**                    | ✅ $0.05/10K params (~$5-15/mes)                | ✅ Gratis (10K requests/día) + $0.05/10K             | ⚠️ $0 licencia + ~$100-300/mes infra    | ✅ $0 licencia + ~$100-200/mes infra   |

**Leyenda:** ✅ Cumple completamente | ⚠️ Cumple parcialmente | ❌ No cumple

---

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
- **HashiCorp Consul:** mayor complejidad operativa y mantenimiento, requiere expertise, costos infraestructura

---

## ⚠️ CONSECUENCIAS

### Positivas

- El código debe desacoplarse del proveedor concreto mediante interfaces
- Se facilita la portabilidad y despliegue híbrido

### Negativas (Riesgos y Mitigaciones)

- **Vendor lock-in cloud:** mitigado con interfaces y adaptadores
- **Complejidad operativa Consul:** mitigado con automatización y monitoreo
- **Costos variables cloud:** mitigado con monitoreo y revisión anual

---

## 📚 REFERENCIAS

- [AWS Parameter Store](https://aws.amazon.com/systems-manager/features/#Parameter_Store)
- [Azure App Configuration](https://azure.microsoft.com/en-us/services/app-configuration/)
- [Consul](https://www.consul.io/)
