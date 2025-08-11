---
id: adr-005-gestion-de-configuraciones
title: "Gestión de Configuraciones"
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

## 🔍 COMPARATIVA DE ALTERNATIVAS

### Comparativa Cualitativa

| Criterio              | AWS Parameter Store | Azure App Configuration | Google Runtime Config | HashiCorp Consul |
|----------------------|--------------------|------------------------|----------------------|------------------|
| **Agnosticidad**     | ❌ Lock-in AWS     | ❌ Lock-in Azure       | ❌ Lock-in GCP        | ✅ Totalmente agnóstico |
| **Operación**        | ✅ Totalmente gestionado | ✅ Totalmente gestionado | ✅ Totalmente gestionado | 🟡 Requiere gestión |
| **Seguridad**        | ✅ Enterprise grade | ✅ Enterprise grade     | ✅ Enterprise grade   | ✅ Máxima seguridad |
| **Ecosistema .NET**  | ✅ Muy buena        | ✅ Excelente           | 🟡 Limitada           | ✅ Buena |
| **Versionado**       | ✅ Automática       | ✅ Automática          | ✅ Automática         | ✅ Muy flexible |
| **Feature Flags**    | 🟡 Básico           | ✅ Nativo, completo    | 🟡 Básico             | ✅ Flexible |
| **Multi-tenancy**    | 🟡 Por parámetros   | ✅ Labels y filtros    | 🟡 Por proyectos      | ✅ Namespaces |
| **Costos**           | 🟡 Por uso          | ✅ Muy económico       | ✅ Muy económico      | 🟡 Infraestructura |

### Matriz de Decisión

| Solución                | Agnosticidad | Operación | Seguridad | Ecosistema .NET | Recomendación         |
|------------------------|--------------|-----------|-----------|-----------------|-----------------------|
| **AWS Parameter Store**| Mala         | Excelente | Excelente | Muy buena       | ✅ **Seleccionada**    |
| **Azure App Configuration** | Mala    | Excelente | Excelente | Excelente       | 🟡 Considerada         |
| **Google Runtime Config**   | Mala    | Excelente | Excelente | Limitada        | ❌ Descartada          |
| **HashiCorp Consul**        | Excelente | Manual  | Excelente | Buena           | 🟡 Alternativa         |

## 💰 ANÁLISIS DE COSTOS (TCO 3 años)

> **Metodología y supuestos:** Se asume un uso promedio de 1000 parámetros, 10,000 requests/mes, 4 entornos. El TCO (Total Cost of Ownership) se calcula para un horizonte de 3 años, incluyendo costos directos y estimaciones de operación. Los valores pueden variar según volumen y proveedor.

| Solución                | Licenciamiento     | Infraestructura | Operación         | TCO 3 años         |
|------------------------|-------------------|----------------|-------------------|--------------------|
| AWS Parameter Store    | Pago por uso      | US$0           | US$0              | US$1,440/año       |
| Azure App Configuration| Pago por uso      | US$0           | US$0              | US$1,800/año       |
| Google Runtime Config  | Pago por uso      | US$0           | US$0              | US$1,680/año       |
| HashiCorp Consul       | OSS               | US$2,160/año   | US$24,000/año     | US$78,480          |

---

## Consideraciones técnicas y riesgos

### Límites clave

- **AWS Parameter Store:** hasta 10,000 parámetros por cuenta, 4 KB por parámetro, 40 TPS por cuenta.
- **Azure App Configuration:** sin límite práctico, 10 KB por clave, 30,000 solicitudes/día gratis.
- **Google Runtime Config:** hasta 100,000 variables por proyecto.
- **HashiCorp Consul:** sin límite, depende de infraestructura.

### Riesgos y mitigación

- **Vendor lock-in cloud:** mitigado con interfaces y adaptadores.
- **Complejidad operativa Consul:** mitigada con automatización y monitoreo.
- **Costos variables cloud:** monitoreo y revisión anual.

---

## ✔️ DECISIÓN

Se selecciona **AWS Parameter Store** como solución principal para la gestión de configuraciones, desacoplada mediante interfaces y adaptadores. La arquitectura soporta migración a Consul u otras soluciones según necesidades de portabilidad o despliegue híbrido.

## Justificación

- Gestión centralizada, segura y versionada
- Portabilidad y despliegue multi-cloud
- Desacoplamiento del backend sin impacto en la lógica de negocio
- Integración gestionada, bajo costo y facilidad de operación
- Consul es opción madura para escenarios on-premises o híbridos

## Alternativas descartadas

- **Azure App Configuration:** lock-in cloud, menor portabilidad
- **Google Runtime Config:** lock-in cloud, menor portabilidad
- **HashiCorp Consul:** mayor complejidad operativa y mantenimiento

---

## ⚠️ CONSECUENCIAS

- El código debe desacoplarse del proveedor concreto mediante interfaces
- Se facilita la portabilidad y despliegue híbrido
- Se requiere mantener adaptadores y pruebas para cada backend soportado

---

## 📚 REFERENCIAS

- [AWS Parameter Store](https://aws.amazon.com/systems-manager/features/#Parameter_Store)
- [Azure App Configuration](https://azure.microsoft.com/en-us/services/app-configuration/)
- [Google Runtime Config](https://cloud.google.com/deployment-manager/runtime-configurator)
- [Consul](https://www.consul.io/)
