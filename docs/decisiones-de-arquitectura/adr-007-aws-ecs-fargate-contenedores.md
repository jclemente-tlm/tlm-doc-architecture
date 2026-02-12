---
title: "ADR-007: AWS ECS Fargate Contenedores"
sidebar_position: 7
---

## ✅ ESTADO

Aceptada – Agosto 2025

---

## 🗺️ CONTEXTO

Los servicios corporativos requieren una solución robusta de orquestación de contenedores para:

- **Despliegue de microservicios (.NET 8) con alta disponibilidad**
- **Escalabilidad automática** basada en métricas
- **Multi-tenancy** con aislamiento por país y cliente
- **Integración CI/CD** con GitHub Actions
- **Observabilidad nativa** (logs, métricas, trazas)
- **Gestión de secretos integrada y segura**
- **Networking avanzado y service mesh opcional**

La intención estratégica es **evaluar facilidad operacional vs agnosticidad** considerando el contexto actual de infraestructura.

Alternativas evaluadas:

- **AWS ECS Fargate** (Serverless containers, gestionado AWS)
- **Kubernetes (EKS)** (Orquestador agnóstico, gestionado AWS)
- **Azure Container Instances** (Serverless containers, gestionado Azure)
- **Google Cloud Run** (Serverless containers, gestionado GCP)
- **Docker Swarm** (Self-hosted, agnóstico)
- **Nomad** (HashiCorp, agnóstico)

## 🔍 COMPARATIVA DE ALTERNATIVAS

### Comparativa Cualitativa

| Criterio            | ECS Fargate                | EKS                         | Azure ACI           | Google Cloud Run | Docker Swarm            | Nomad                   |
| ------------------- | -------------------------- | --------------------------- | ------------------- | ---------------- | ----------------------- | ----------------------- |
| **Agnosticidad**    | ❌ Lock-in AWS             | ✅ Estándar K8s             | ❌ Lock-in Azure    | ❌ Lock-in GCP   | ✅ Docker estándar      | ✅ Agnóstico            |
| **Operación**       | ✅ Serverless, sin gestión | ⚠️ Requiere gestión cluster | ✅ Serverless       | ✅ Serverless    | ⚠️ Manual               | ⚠️ Manual               |
| **Seguridad**       | ✅ IAM, VPC, Secrets       | ✅ IAM, RBAC                | ✅ Azure RBAC       | ✅ GCP IAM       | ⚠️ Limitada             | ⚠️ Limitada             |
| **Ecosistema .NET** | ✅ Excelente               | ✅ Excelente                | ✅ Nativo Microsoft | ✅ Excelente     | ✅ Excelente            | ✅ Excelente            |
| **Escalabilidad**   | ✅ Automática              | ✅ Flexible                 | ✅ Automática       | ✅ Automática    | ⚠️ Manual               | ⚠️ Manual               |
| **Complejidad**     | ✅ Muy simple              | ❌ Complejo (K8s)           | ✅ Simple           | ✅ Simple        | ✅ Simple               | ✅ Simple               |
| **Costos**          | ⚠️ Premium serverless      | ⚠️ Nodos + gestión          | ⚠️ Pago por uso     | ⚠️ Pago por uso  | ✅ Solo infraestructura | ✅ Solo infraestructura |

**Leyenda:** ✅ Cumple completamente | ⚠️ Cumple parcialmente | ❌ No cumple

---

## ✔️ DECISIÓN

Se selecciona **ECS Fargate** como solución estándar para el despliegue de microservicios y sistemas corporativos en contenedores, priorizando simplicidad operativa, integración nativa y escalabilidad automática.

### Justificación

- Modelo serverless: sin gestión de servidores ni parches
- Despliegue y escalado automático según demanda
- Integración nativa con IAM, VPC, CloudWatch, Secrets Manager
- Costos optimizados: pago por uso, sin costos fijos
- Seguridad mejorada: aislamiento de tareas y control granular de permisos
- Reducción de complejidad operativa y menor tiempo de provisión

### Alternativas descartadas

- **EKS:** mayor complejidad operativa y costos
- **Azure ACI:** lock-in cloud, menor integración
- **Google Cloud Run:** lock-in cloud, menor integración
- **Docker Swarm:** operación manual, menor integración y soporte
- **Nomad:** operación manual, menor integración y soporte

---

## ⚠️ CONSECUENCIAS

### Positivas

- Modelo serverless: sin gestión de servidores ni parches
- Despliegue y escalado automático según demanda
- Integración nativa con IAM, VPC, CloudWatch, Secrets Manager
- Seguridad mejorada: aislamiento de tareas y control granular
- Reducción de complejidad operativa

### Negativas (Riesgos y Mitigaciones)

- **Lock-in AWS:** mitigado con contenedores estándar Docker y pipelines portables
- **Costos serverless premium:** mitigados con monitoreo, dimensionamiento adecuado y Savings Plans
- **Límites por cuenta:** mitigados con planificación de cuotas y multi-account strategy

---

## 📚 REFERENCIAS

- [AWS ECS Fargate](https://aws.amazon.com/ecs/fargate/)
- [Kubernetes](https://kubernetes.io/)
- [Azure Container Instances](https://azure.microsoft.com/en-us/services/container-instances/)
- [Google Cloud Run](https://cloud.google.com/run/)
- [Docker Swarm](https://docs.docker.com/engine/swarm/)
- [Nomad](https://www.nomadproject.io/)
