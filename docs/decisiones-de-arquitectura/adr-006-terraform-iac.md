---
title: "ADR-006: Terraform IaC"
sidebar_position: 6
---

## ✅ ESTADO

Aceptada – Agosto 2025

---

## 🗺️ CONTEXTO

Los servicios corporativos requieren una solución robusta de infraestructura como código para:

- **Despliegue multi-cloud** (AWS, Azure, GCP) con portabilidad
- **Multi-entorno** (dev, staging, prod) con configuraciones específicas
- **Multi-tenancy** con recursos segregados por país/tenant
- **Versionado y rollback** de infraestructura
- **Automatización CI/CD** integrada con pipelines
- **Compliance y seguridad** con políticas como código
- **Reutilización de módulos** para consistencia
- **Gestión de estado** distribuida y segura
- **Disaster recovery** con infraestructura reproducible

La intención estratégica es **evaluar agnosticidad vs facilidad operacional** considerando que la IaC es crítica para la portabilidad y la operación segura.

Alternativas evaluadas:

- **Terraform** (Gestionado por HashiCorp, HCL, multi-cloud)
- **Pulumi** (Multi-lenguaje, programático)
- **AWS CloudFormation** (AWS nativo)
- **ARM Templates** (Azure nativo)
- **GCP Deployment Manager** (GCP nativo)

## 🔍 COMPARATIVA DE ALTERNATIVAS

### Comparativa Cualitativa

| Criterio            | Terraform           | Pulumi              | AWS CloudFormation | ARM Templates    | GCP Deployment Manager |
| ------------------- | ------------------- | ------------------- | ------------------ | ---------------- | ---------------------- |
| **Agnosticidad**    | ✅ Multi-cloud      | ✅ Multi-cloud      | ❌ Lock-in AWS     | ❌ Lock-in Azure | ❌ Lock-in GCP         |
| **Operación**       | ✅ Declarativo      | 🟡 Imperativo       | ✅ Declarativo     | ✅ Declarativo   | ✅ Declarativo         |
| **Seguridad**       | ✅ Enterprise grade | ✅ Enterprise grade | ✅ AWS IAM         | ✅ Azure RBAC    | ✅ GCP IAM             |
| **Ecosistema .NET** | ✅ Muy buena        | ✅ Muy buena        | 🟡 Solo AWS        | 🟡 Solo Azure    | 🟡 Solo GCP            |
| **Versionado**      | ✅ Automática       | ✅ Automática       | ✅ Nativo          | ✅ Nativo        | ✅ Nativo              |
| **Módulos**         | ✅ Reutilizables    | ✅ Reutilizables    | 🟡 Solo AWS        | 🟡 Solo Azure    | 🟡 Solo GCP            |
| **Costos**          | 🟡 Por uso          | 🟡 Por uso          | ✅ Incluido        | ✅ Incluido      | ✅ Incluido            |

## ✔️ DECISIÓN

Se selecciona **Terraform** como solución estándar de infraestructura como código para todos los servicios corporativos, desacoplada mediante módulos reutilizables y gestión de estado segura. La arquitectura soporta migración y portabilidad multi-cloud.

### Justificación

- Agnosticidad multi-cloud y portabilidad
- Ecosistema maduro y módulos reutilizables
- Gestión de estado robusta y segura
- Integración nativa con CI/CD y pipelines
- Sintaxis declarativa fácil de mantener
- Comunidad activa y soporte extenso

### Alternativas descartadas

- Pulumi: menor adopción y ecosistema vs Terraform
- AWS CloudFormation, ARM Templates, GCP Deployment Manager: lock-in cloud, menor portabilidad

---

## ⚠️ CONSECUENCIAS

- El código IaC debe desacoplarse del proveedor concreto mediante módulos reutilizables
- Se facilita la portabilidad y despliegue multi-cloud
- Se requiere mantener buenas prácticas de gestión de estado y documentación

---

## 📚 REFERENCIAS

- [Terraform Documentation](https://www.terraform.io/docs)
- [Terraform Registry](https://registry.terraform.io/)
- [HashiCorp Learn](https://learn.hashicorp.com/terraform)
