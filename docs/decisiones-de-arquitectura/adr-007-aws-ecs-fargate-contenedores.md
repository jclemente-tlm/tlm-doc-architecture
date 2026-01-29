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

| Criterio              | ECS Fargate | EKS | Azure ACI | Google Cloud Run | Docker Swarm | Nomad |
|----------------------|-------------|-----|-----------|------------------|--------------|-------|
| **Agnosticidad**     | ❌ Lock-in AWS | ✅ Estándar K8s | ❌ Lock-in Azure | ❌ Lock-in GCP | ✅ Docker estándar | ✅ Agnóstico |
| **Operación**        | ✅ Serverless, sin gestión | 🟡 Requiere gestión cluster | ✅ Serverless | ✅ Serverless | 🟡 Manual | 🟡 Manual |
| **Seguridad**        | ✅ IAM, VPC, Secrets | ✅ IAM, RBAC | ✅ Azure RBAC | ✅ GCP IAM | 🟡 Limitada | 🟡 Limitada |
| **Ecosistema .NET**  | ✅ Excelente | ✅ Excelente | ✅ Nativo Microsoft | ✅ Excelente | ✅ Excelente | ✅ Excelente |
| **Escalabilidad**    | ✅ Automática | ✅ Flexible | ✅ Automática | ✅ Automática | 🟡 Manual | 🟡 Manual |
| **Complejidad**      | ✅ Muy simple | ❌ Complejo (K8s) | ✅ Simple | ✅ Simple | ✅ Simple | ✅ Simple |
| **Costos**           | 🟡 Premium serverless | 🟡 Nodos + gestión | 🟡 Pago por uso | 🟡 Pago por uso | ✅ Solo infraestructura | ✅ Solo infraestructura |

### Matriz de Decisión

| Solución                | Agnosticidad | Operación | Seguridad | Escalabilidad | Recomendación         |
|------------------------|--------------|-----------|-----------|---------------|-----------------------|
| **ECS Fargate**        | Mala         | Excelente | Excelente | Excelente     | ✅ **Seleccionada**    |
| **EKS**                | Excelente    | Buena     | Excelente | Excelente     | 🟡 Alternativa         |
| **Azure ACI**          | Mala         | Excelente | Excelente | Excelente     | ❌ Descartada          |
| **Google Cloud Run**   | Mala         | Excelente | Excelente | Excelente     | ❌ Descartada          |
| **Docker Swarm**       | Excelente    | Limitada  | Limitada  | Limitada      | ❌ Descartada          |
| **Nomad**              | Excelente    | Limitada  | Limitada  | Limitada      | ❌ Descartada          |

## 💰 ANÁLISIS DE COSTOS (TCO 3 años)

> **Metodología y supuestos:** Se asume un uso promedio de 5 servicios, 2 vCPU/4GB cada uno, 4 países. El TCO (Total Cost of Ownership) se calcula para un horizonte de 3 años, incluyendo costos directos y estimaciones de operación. Los valores pueden variar según volumen y proveedor.

| Solución                | Licenciamiento     | Infraestructura | Operación         | TCO 3 años         |
|------------------------|-------------------|----------------|-------------------|--------------------|
| ECS Fargate            | Incluido          | Pago por uso   | US$0              | US$129,600         |
| Kubernetes (EKS)       | US$2,160/año      | US$21,600/año  | US$60,000/año     | US$251,280         |
| Azure ACI              | Incluido          | Pago por uso   | US$0              | US$155,520         |
| Google Cloud Run       | Incluido          | Pago por uso   | US$0              | US$138,240         |
| Docker Swarm           | OSS               | US$14,400/año  | US$36,000/año     | US$151,200         |
| Nomad                  | OSS               | US$10,800/año  | US$24,000/año     | US$104,400         |

---

## Consideraciones técnicas y riesgos

### Límites clave

- **ECS Fargate:** hasta 120 tareas por servicio, 50 servicios por cluster, 30,000 tareas por cuenta.
- **EKS:** límite de nodos y pods por cluster, depende de configuración.
- **Azure ACI:** límite de instancias y recursos por región.
- **Google Cloud Run:** límite de instancias y concurrencia por servicio.
- **Docker Swarm/Nomad:** sin límite, depende de infraestructura propia.

### Riesgos y mitigación

- **Lock-in AWS:** mitigado con uso de contenedores estándar y pipelines portables.
- **Complejidad operativa K8s:** mitigada con automatización y capacitación.
- **Costos serverless:** monitoreo y revisión anual de uso y dimensionamiento.

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

- Todos los microservicios y sistemas se despliegan como tareas Fargate en ECS
- El equipo se enfoca en desarrollo y operación de servicios, no en infraestructura

---

## 📚 REFERENCIAS

- [AWS ECS Fargate](https://aws.amazon.com/ecs/fargate/)
- [Kubernetes](https://kubernetes.io/)
- [Azure Container Instances](https://azure.microsoft.com/en-us/services/container-instances/)
- [Google Cloud Run](https://cloud.google.com/run/)
- [Docker Swarm](https://docs.docker.com/engine/swarm/)
- [Nomad](https://www.nomadproject.io/)
