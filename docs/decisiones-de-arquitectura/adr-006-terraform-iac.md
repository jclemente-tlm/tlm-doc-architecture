---
title: "ADR-006: Terraform IaC"
sidebar_position: 6
---

## ✅ ESTADO

Aceptada – Agosto 2025

---

## 🗺️ CONTEXTO

Los servicios corporativos requieren una solución robusta de infraestructura como código para:

- **Despliegue multi-cloud** (AWS, Azure) con portabilidad
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
- **Ansible** (Config management, YAML, agentless)
- **AWS CloudFormation** (AWS nativo)
- **Azure Bicep** (Azure nativo, moderno)

## 🔍 COMPARATIVA DE ALTERNATIVAS

| Criterio            | Terraform             | Pulumi              | Ansible                   | AWS CloudFormation | Azure Bicep      |
| ------------------- | --------------------- | ------------------- | ------------------------- | ------------------ | ---------------- |
| **Agnosticidad**    | ✅ Multi-cloud        | ✅ Multi-cloud      | ✅ Multi-cloud            | ❌ Lock-in AWS     | ❌ Lock-in Azure |
| **Operación**       | ✅ Declarativo        | ⚠️ Imperativo       | ⚠️ Imperativo/Declarativo | ✅ Declarativo     | ✅ Declarativo   |
| **Seguridad**       | ✅ Enterprise grade   | ✅ Enterprise grade | ✅ SSH/Enterprise         | ✅ AWS IAM         | ✅ Azure RBAC    |
| **Integración SDK** | ✅ Muy buena          | ✅ Multi-lenguaje   | ⚠️ SSH/Python             | ⚠️ Solo AWS        | ⚠️ Solo Azure    |
| **Versionado**      | ✅ Automática         | ✅ Automática       | ✅ Git-based              | ✅ Nativo          | ✅ Nativo        |
| **Módulos**         | ✅ Reutilizables      | ✅ Reutilizables    | ✅ Roles/Collections      | ⚠️ Solo AWS        | ⚠️ Solo Azure    |
| **Comunidad**       | ✅ Muy activa (42K⭐) | ✅ Activa (21K⭐)   | ✅ Muy activa (62K⭐)     | ✅ Soporte AWS     | ✅ Soporte Azure |
| **Costos**          | ⚠️ Por uso            | ⚠️ Por uso          | ✅ Gratis OSS             | ✅ Incluido        | ✅ Incluido      |

**Leyenda:** ✅ Cumple completamente | ⚠️ Cumple parcialmente | ❌ No cumple

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

- **Ansible:** excelente para configuration management pero enfoque imperativo/procedural, estado no declarativo (no state file), menor idempotencia vs Terraform, mejor para config servers que infraestructura
- **Pulumi:** menor adopción enterprise vs Terraform (3K vs 40K stars GitHub), ecosistema módulos menos maduro, learning curve programación vs HCL declarativo
- **CloudFormation, Bicep:** lock-in cloud específico, menor portabilidad multi-cloud, requiere reescritura completa para migraciones

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
