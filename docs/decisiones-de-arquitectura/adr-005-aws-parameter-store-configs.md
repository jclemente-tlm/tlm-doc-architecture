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

### Comparativa Cualitativa

| Criterio            | Parameter Store   | Azure App Config | Google Runtime    | Consul                | etcd              |
| ------------------- | ----------------- | ---------------- | ----------------- | --------------------- | ----------------- |
| **Agnosticidad**    | ❌ Lock-in AWS    | ❌ Lock-in Azure | ❌ Lock-in GCP    | ✅ Agnóstico          | ✅ OSS, agnóstico |
| **Operación**       | ✅ Gestionado     | ✅ Gestionado    | ✅ Gestionado     | ⚠️ Requiere gestión   | ⚠️ Self-hosted    |
| **Seguridad**       | ✅ Enterprise     | ✅ Enterprise    | ✅ Enterprise     | ✅ Máxima             | ✅ TLS, RBAC      |
| **Ecosistema .NET** | ✅ Muy buena      | ✅ Excelente     | ⚠️ Limitada       | ✅ Buena              | ⚠️ Limitada       |
| **Versionado**      | ✅ Automática     | ✅ Automática    | ✅ Automática     | ✅ Muy flexible       | ✅ Revisions      |
| **Feature Flags**   | ⚠️ Básico         | ✅ Nativo        | ⚠️ Básico         | ✅ Flexible           | ⚠️ Manual         |
| **Multi-tenancy**   | ⚠️ Por parámetros | ✅ Labels        | ⚠️ Por proyectos  | ✅ Namespaces         | ⚠️ Prefixes       |
| **Comunidad**       | ✅ Soporte AWS    | ✅ Soporte Azure | ✅ Soporte Google | ✅ Muy activa (28K⭐) | ✅ CNCF (47K⭐)   |
| **Costos**          | ⚠️ Por uso        | ✅ Económico     | ✅ Económico      | ⚠️ Infraestructura    | ✅ Gratis OSS     |

**Leyenda:** ✅ Cumple completamente | ⚠️ Cumple parcialmente | ❌ No cumple

## ✔️ DECISIÓN

Se selecciona **AWS Parameter Store** como solución principal para la gestión de configuraciones, desacoplada mediante interfaces y adaptadores. La arquitectura soporta migración a Consul u otras soluciones según necesidades de portabilidad o despliegue híbrido.

## Justificación

- Gestión centralizada, segura y versionada
- Portabilidad y despliegue multi-cloud
- Desacoplamiento del backend sin impacto en la lógica de negocio
- Integración gestionada, bajo costo y facilidad de operación
- Consul es opción madura para escenarios on-premises o híbridos

## Alternativas descartadas

- **etcd:** distributed key-value store robusto pero orientado a Kubernetes ecosystem, complejidad operativa alta (clustering, quorum, backups), menor integración .NET vs Parameter Store, overhead para uso simple config
- **Azure App Configuration:** lock-in Azure, infraestructura AWS ya establecida, menor portabilidad
- **Google Runtime Config:** lock-in GCP, SDK .NET limitado, menor madurez vs otros
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
