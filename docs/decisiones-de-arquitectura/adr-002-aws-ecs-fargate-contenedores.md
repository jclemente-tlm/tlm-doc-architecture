---
title: "ADR-002: AWS ECS Fargate Contenedores"
sidebar_position: 2
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

| Criterio                       | AWS ECS Fargate                             | AWS EKS                                             | Azure Kubernetes Service                | Azure Container Instances           | Docker Swarm                         |
| ------------------------------ | ------------------------------------------- | --------------------------------------------------- | --------------------------------------- | ----------------------------------- | ------------------------------------ |
| **Agnosticidad**               | ❌ Lock-in AWS                              | ✅ Estándar K8s                                     | ✅ Estándar K8s                         | ❌ Lock-in Azure                    | ✅ Docker estándar                   |
| **Madurez**                    | ✅ Alta (2017, serverless pioneer)          | ✅ Muy alta (2018, AWS-managed)                     | ✅ Muy alta (2018, Azure-managed)       | ⚠️ Media (2017, niche)              | ⚠️ Baja (2014, legacy)               |
| **Adopción**                   | ✅ Alta (AWS standard)                      | ✅ Muy alta (K8s CNCF std)                          | ✅ Muy alta (K8s Azure)                 | ⚠️ Media (limitado)                 | ⚠️ Baja (declinando)                 |
| **Modelo de gestión**          | ✅ Serverless (AWS)                         | ✅ Gestionado (AWS)                                 | ✅ Gestionado (Azure)                   | ✅ Serverless (Azure)               | ⚠️ Self-hosted                       |
| **Complejidad operativa**      | ✅ Baja (0.25 FTE, `<5h/sem)`                 | ❌ Muy Alta (2+ FTE, 20-40h/sem)                    | ❌ Muy Alta (2+ FTE, 20-40h/sem)        | ✅ Baja (0.25 FTE, `<5h/sem)`         | ⚠️ Alta (1 FTE, 10-20h/sem)          |
| **Multi-tenancy**              | ✅ Aislamiento por task                     | ✅ Namespaces + RBAC                                | ✅ Namespaces + RBAC                    | ✅ Container groups                 | ⚠️ Manual config                     |
| **Seguridad**                  | ✅ IAM, VPC, Secrets                        | ✅ IAM, RBAC                                        | ✅ Azure AD, RBAC                       | ✅ Azure RBAC                       | ⚠️ Limitada                          |
| **Rendimiento**                | ✅ `<30s `cold start                          | ✅ `<10s `start                                       | ✅ `<10s `start                           | ✅ `<5s `inicio                       | ⚠️ 10-60s según config               |
| **Escalabilidad**              | ✅ Hasta 10K+ tasks (AWS enterprise)        | ✅ Hasta 5K+ pods/cluster (CNCF certified)          | ✅ Hasta 5K+ pods/cluster (Azure scale) | ✅ Hasta 1K+ containers (Azure ACI) | ⚠️ Manual (depende configuración)    |
| **Alta disponibilidad**        | ✅ 99.99% SLA Multi-AZ                      | ✅ 99.95% SLA Multi-AZ                              | ✅ 99.95% SLA Multi-AZ                  | ✅ 99.9% SLA Multi-AZ               | ⚠️ Sin SLA (manual)                  |
| **Estrategias de despliegue**  | ✅ Rolling, Blue/Green, Canary              | ✅ Rolling, Blue/Green, Canary                      | ✅ Rolling, Blue/Green, Canary          | ⚠️ Básico rolling update            | ⚠️ Manual implementation             |
| **Service Mesh**               | ⚠️ App Mesh integration (manual)            | ✅ Istio, Linkerd nativos                           | ✅ Open Service Mesh                    | ❌ No soportado                     | ⚠️ Manual Envoy/Linkerd config       |
| **Opciones de almacenamiento** | ✅ EBS, EFS, FSx, S3                        | ✅ PV, EBS, EFS, NFS, S3                            | ✅ Azure Disks, Files, Blob             | ⚠️ Azure Files (limitado)           | ⚠️ Bind mounts, volumes (básico)     |
| **Modos de red**               | ✅ awsvpc (ENI por task), bridge            | ✅ CNI plugins, Calico, Cilium                      | ✅ Azure CNI, kubenet                   | ⚠️ Virtual networks (básico)        | ⚠️ Bridge, host, overlay             |
| **Soporte Spot**               | ✅ Fargate Spot (70% discount)              | ✅ Spot instances + node pools                      | ✅ Spot VMs (hasta 90% discount)        | ❌ No soportado                     | ⚠️ Manual spot instance config       |
| **Costos**                     | ⚠️ $0.04/vCPU/h + $0.004/GB/h (~$30-50/mes) | ⚠️ $73/mes control + ~$50-100/mes nodos (~$150/mes) | ⚠️ $0 control + ~$50-100/mes nodos      | ⚠️ $0.0005/vCore/seg (~$30-50/mes)  | ✅ $0 licencia + ~$100-200/mes infra |

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
