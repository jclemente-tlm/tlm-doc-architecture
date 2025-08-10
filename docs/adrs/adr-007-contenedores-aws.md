---
title: "Contenedores en AWS"
sidebar_position: 7
---

## ✅ ESTADO

Aceptada – Agosto 2025

---

## 🗺️ CONTEXTO

Los servicios corporativos requieren una plataforma de contenedores que soporte:

- **Despliegue de microservicios** (.NET 8) con alta disponibilidad
- **Escalabilidad automática** basada en métricas de CPU/memoria/requests
- **Multi-tenancy** con aislamiento por país y cliente
- **Integración CI/CD** fluida con GitHub Actions
- **Observabilidad nativa** (logs, métricas, tracing)
- **Gestión de secretos** integrada y segura
- **Networking avanzado** con service mesh opcional

La intención estratégica es **evaluar facilidad operacional vs agnosticidad** considerando el contexto actual de infraestructura.

Las alternativas evaluadas fueron:

- **AWS ECS Fargate** (Serverless containers, gestionado AWS)
- **Kubernetes (EKS/AKS/GKE)** (Orquestador agnóstico, complejo)
- **Azure Container Instances** (Serverless containers, gestionado Azure)
- **Google Cloud Run** (Serverless containers, gestionado GCP)
- **Docker Swarm** (Simple, self-hosted, agnóstico)
- **Nomad** (HashiCorp, agnóstico, simple)

## 🔍 COMPARATIVA DE ALTERNATIVAS

### Comparativa Cualitativa

| Criterio | ECS Fargate | EKS | AKS | GKE | Docker Swarm |
|----------|-------------|-----|-----|-----|-------------|
| **Operación** | ✅ Serverless, sin gestión | 🟡 Requiere gestión cluster | 🟡 Requiere gestión cluster | 🟡 Requiere gestión cluster | 🟡 Gestión manual |
| **Integración AWS** | ✅ Nativa y completa | ✅ Muy buena | ❌ Lock-in Azure | ❌ Lock-in GCP | 🟡 Básica |
| **Escalabilidad** | ✅ Automática instantánea | ✅ Muy flexible | ✅ Muy flexible | ✅ Muy flexible | 🟡 Manual |
| **Soporte .NET** | ✅ Excelente | ✅ Excelente | ✅ Nativo Microsoft | ✅ Excelente | ✅ Excelente |
| **Complejidad** | ✅ Muy simple | ❌ Complejo (K8s) | ❌ Complejo (K8s) | ❌ Complejo (K8s) | ✅ Simple |
| **Portabilidad** | ❌ Lock-in AWS | ✅ Estándar K8s | ✅ Estándar K8s | ✅ Estándar K8s | ✅ Docker estándar |
| **Costos** | 🟡 Premium serverless | 🟡 Nodos + gestión | 🟡 Nodos + gestión | 🟡 Nodos + gestión | ✅ Solo infraestructura |

### Matriz de Decisión

| Solución | Operación | Integración AWS | Complejidad | Escalabilidad | Recomendación |
|----------|-----------|-----------------|-------------|---------------|--------------|
| **ECS Fargate** | Excelente | Excelente | Muy simple | Excelente | ✅ **Seleccionada** |
| **EKS** | Manual | Muy buena | Compleja | Excelente | 🟡 Alternativa |
| **AKS** | Manual | Mala | Compleja | Excelente | ❌ Descartada |
| **GKE** | Manual | Mala | Compleja | Excelente | ❌ Descartada |
| **Docker Swarm** | Manual | Básica | Simple | Manual | ❌ Descartada |

## 💰 ANÁLISIS DE COSTOS (TCO 3 años)

### Escenario Base: 5 servicios, 2 vCPU/4GB cada uno, 4 países

| Solución | Licenciamiento | Infraestructura | Operación | TCO 3 años |
|----------|----------------|-----------------|-----------|------------|
| **ECS Fargate** | US$0 (incluido) | Pago por uso | US$0 | **US$129,600** |
| **Kubernetes (EKS)** | US$2,160/año | US$21,600/año | US$60,000/año | **US$251,280** |
| **Azure ACI** | US$0 (incluido) | Pago por uso | US$0 | **US$155,520** |
| **Google Cloud Run** | US$0 (incluido) | Pago por uso | US$0 | **US$138,240** |
| **Docker Swarm** | US$0 (OSS) | US$14,400/año | US$36,000/año | **US$151,200** |
| **Nomad** | US$0 (OSS) | US$10,800/año | US$24,000/año | **US$104,400** |

### Escenario Alto Volumen: 20 servicios, escalabilidad dinámica

| Solución | TCO 3 años | Escalabilidad |
|----------|------------|---------------|
| **ECS Fargate** | **US$518,400** | Automática, instantánea |
| **Kubernetes (EKS)** | **US$720,000** | Automática, configuración compleja |
| **Azure ACI** | **US$622,080** | Automática, instantánea |
| **Google Cloud Run** | **US$552,960** | Automática, instantánea |
| **Docker Swarm** | **US$480,000** | Manual, limitada |
| **Nomad** | **US$360,000** | Manual, flexible |

### Factores de Costo Adicionales

```yaml
Consideraciones:
  Networking: ALB incluido en Fargate vs +US$6K/año en K8s
  Storage: EFS/EBS incluido vs configuración manual
  Monitoreo: CloudWatch incluido vs +US$12K/año en self-hosted
  Backup/DR: Snapshots automáticos vs scripts manuales
  Capacitación: US$0 Fargate vs US$15K K8s vs US$8K Nomad
  Migración: US$25K desde Fargate vs US$5K entre OSS
```

### Agnosticismo, lock-in y mitigación

- **Lock-in:** `ECS Fargate` implica dependencia de `AWS`, pero se justifica por la operación simplificada, escalabilidad y menor mantenimiento en un entorno 100% `AWS`.
- **Mitigación:** El uso de contenedores y estándares como `Docker` permite migrar a otros orquestadores ([Kubernetes](https://kubernetes.io/), [Azure Container Instances](https://azure.microsoft.com/en-us/services/container-instances/)) si el contexto cambia, aunque con esfuerzo de integración.

---

## ✔️ DECISIÓN

Se selecciona **[ECS Fargate](https://aws.amazon.com/ecs/fargate/)** para el despliegue de `microservicios` y sistemas corporativos en contenedores.

## Justificación

- Modelo `serverless`: No requiere gestión de servidores, escalado ni parches de sistema operativo.
- Despliegue y escalado automático: `Fargate` ajusta recursos según demanda, sin intervención manual.
- Integración nativa con `AWS IAM`, `VPC`, `CloudWatch`, `Secrets Manager`, etc.
- Costos optimizados: Pago por uso de recursos, sin costos fijos de instancias.
- Seguridad mejorada: Aislamiento de tareas y control granular de permisos.
- Reducción de complejidad operativa: `EC2` requiere gestión de AMIs, actualizaciones, monitoreo y escalado manual.
- Menor tiempo de provisión y despliegue: `Fargate` permite despliegues rápidos y consistentes.

## Alternativas descartadas

- **EC2:** Mayor carga operativa, menor agilidad y escalabilidad, más puntos de falla.

---

## ⚠️ CONSECUENCIAS

- Todos los `microservicios` y sistemas se despliegan como tareas Fargate en ECS.
- El equipo se enfoca en desarrollo y operación de servicios, no en infraestructura.

---

## 📚 REFERENCIAS

- [AWS ECS Fargate](https://aws.amazon.com/fargate/)
- [Comparación EC2 vs Fargate](https://aws.amazon.com/blogs/containers/should-you-use-amazon-ecs-or-amazon-ec2/)
- [Arc42: Decisiones de arquitectura](https://arc42.org/decision/)
