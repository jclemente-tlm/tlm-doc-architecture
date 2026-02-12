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
- **Azure Kubernetes Service (AKS)** (K8s gestionado Azure)
- **Google Kubernetes Engine (GKE)** (K8s gestionado GCP)
- **Azure Container Instances** (Serverless containers, gestionado Azure)
- **Google Cloud Run** (Serverless containers, gestionado GCP)
- **Docker Swarm** (Self-hosted, agnóstico)

## 🔍 COMPARATIVA DE ALTERNATIVAS

### Comparativa Cualitativa

| Criterio            | ECS Fargate                | EKS                         | AKS                 | GKE                      | Azure ACI           | Google Cloud Run | Docker Swarm            |
| ------------------- | -------------------------- | --------------------------- | ------------------- | ------------------------ | ------------------- | ---------------- | ----------------------- |
| **Agnosticidad**    | ❌ Lock-in AWS             | ✅ Estándar K8s             | ✅ Estándar K8s     | ✅ Estándar K8s          | ❌ Lock-in Azure    | ❌ Lock-in GCP   | ✅ Docker estándar      |
| **Operación**       | ✅ Serverless, sin gestión | ⚠️ Requiere gestión cluster | ⚠️ Requiere gestión | ⚠️ Requiere gestión      | ✅ Serverless       | ✅ Serverless    | ⚠️ Manual               |
| **Seguridad**       | ✅ IAM, VPC, Secrets       | ✅ IAM, RBAC                | ✅ Azure AD, RBAC   | ✅ GCP IAM, Workload     | ✅ Azure RBAC       | ✅ GCP IAM       | ⚠️ Limitada             |
| **Ecosistema .NET** | ✅ Excelente               | ✅ Excelente                | ✅ Nativo Microsoft | ✅ Excelente             | ✅ Nativo Microsoft | ✅ Excelente     | ✅ Excelente            |
| **Escalabilidad**   | ✅ Automática              | ✅ Flexible                 | ✅ Flexible         | ✅ Flexible (Autopilot)  | ✅ Automática       | ✅ Automática    | ⚠️ Manual               |
| **Complejidad**     | ✅ Muy simple              | ❌ Complejo (K8s)           | ❌ Complejo (K8s)   | ❌ Complejo (K8s)        | ✅ Simple           | ✅ Simple        | ✅ Simple               |
| **Costos**          | ⚠️ Premium serverless      | ⚠️ Nodos + gestión          | ⚠️ Nodos + gestión  | ⚠️ Autopilot competitivo | ⚠️ Pago por uso     | ⚠️ Pago por uso  | ✅ Solo infraestructura |

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

- **EKS/AKS/GKE (Kubernetes):** complejidad operativa alta (YAML, Helm, operators), curva de aprendizaje pronunciada, sobrede-dimensionado para necesidades actuales, costos de gestión cluster (US$0.10/hora = US$876/año), requiere expertise especializado
- **Azure ACI:** lock-in Azure, infraestructura AWS ya establecida (ADR-003, ADR-005), menor integración con servicios corporativos existentes
- **Google Cloud Run:** lock-in GCP, infraestructura AWS ya establecida, menor integración
- **Docker Swarm:** operación manual, menor adopción enterprise, ecosistema limitado vs Kubernetes, soporte comunitario decreciente

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
- [Amazon EKS](https://aws.amazon.com/eks/)
- [Azure Kubernetes Service](https://azure.microsoft.com/en-us/services/kubernetes-service/)
- [Google Kubernetes Engine](https://cloud.google.com/kubernetes-engine/)
- [Azure Container Instances](https://azure.microsoft.com/en-us/services/container-instances/)
- [Google Cloud Run](https://cloud.google.com/run/)
- [Docker Swarm](https://docs.docker.com/engine/swarm/)
