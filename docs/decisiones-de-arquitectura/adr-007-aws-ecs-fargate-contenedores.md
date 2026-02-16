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
- **Azure Container Instances** (Serverless containers, gestionado Azure)
- **Docker Swarm** (Self-hosted, agnóstico)

## 🔍 COMPARATIVA DE ALTERNATIVAS

| Criterio                  | AWS ECS Fargate         | AWS EKS                  | Azure Kubernetes Service | Azure Container Instances | Docker Swarm            |
| ------------------------- | ----------------------- | ------------------------ | ------------------------ | ------------------------- | ----------------------- |
| **Agnosticidad**          | ❌ Lock-in AWS          | ✅ Estándar K8s          | ✅ Estándar K8s          | ❌ Lock-in Azure          | ✅ Docker estándar      |
| **Modelo de gestión**     | ✅ Serverless (AWS)     | ✅ Gestionado (AWS)      | ✅ Gestionado (Azure)    | ✅ Serverless (Azure)     | ⚠️ Self-hosted          |
| **Complejidad operativa** | ✅ Baja (sin gestión)   | ❌ Alta (K8s, Helm, ops) | ❌ Alta (K8s, ops)       | ✅ Baja (sin gestión)     | ⚠️ Media (clustering)   |
| **Multi-tenancy**         | ✅ Aislamiento por task | ✅ Namespaces + RBAC     | ✅ Namespaces + RBAC     | ✅ Container groups       | ⚠️ Manual config        |
| **Seguridad**             | ✅ IAM, VPC, Secrets    | ✅ IAM, RBAC             | ✅ Azure AD, RBAC        | ✅ Azure RBAC             | ⚠️ Limitada             |
| **Integración .NET**      | ✅ Excelente            | ✅ Muy buena             | ✅ Muy buena             | ✅ Muy buena              | ✅ Nativa Docker        |
| **Performance**           | ✅ Baja latencia        | ✅ Muy buena             | ✅ Muy buena             | ✅ Inicio rápido          | ⚠️ Depende config       |
| **Escalabilidad**         | ✅ Automática           | ✅ Flexible              | ✅ Flexible              | ✅ Automática             | ⚠️ Manual               |
| **Alta disponibilidad**   | ✅ Multi-AZ             | ✅ Multi-AZ, HA          | ✅ Multi-AZ, HA          | ✅ Multi-AZ               | ⚠️ Manual               |
| **Observabilidad**        | ✅ CloudWatch integrado | ✅ Prometheus/Grafana    | ✅ Azure Monitor         | ✅ Azure Monitor          | ⚠️ Manual setup         |
| **Costos**                | ⚠️ Premium serverless   | ⚠️ Nodos + gestión       | ⚠️ Nodos + gestión       | ⚠️ Pago por uso           | ✅ Solo infraestructura |

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

- **EKS/AKS (Kubernetes):** complejidad operativa alta (YAML, Helm, operators), curva de aprendizaje pronunciada, sobrede-dimensionado para necesidades actuales, costos de gestión cluster (US$0.10/hora = US$876/año), requiere expertise especializado
- **Azure ACI:** lock-in Azure, infraestructura AWS ya establecida (ADR-003, ADR-005), menor integración con servicios corporativos existentes
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
- [Azure Container Instances](https://azure.microsoft.com/en-us/services/container-instances/)
- [Docker Swarm](https://docs.docker.com/engine/swarm/)
