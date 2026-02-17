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

| Criterio                     | Terraform                                        | Pulumi                                      | Ansible                              | AWS CloudFormation          | Azure Bicep                    |
| ---------------------------- | ------------------------------------------------ | ------------------------------------------- | ------------------------------------ | --------------------------- | ------------------------------ |
| **Agnosticidad**             | ✅ Multi-cloud                                   | ✅ Multi-cloud                              | ✅ Multi-cloud                       | ❌ Lock-in AWS              | ❌ Lock-in Azure               |
| **Madurez**                  | ✅ Muy alta (2014, líder IaC)                    | ⚠️ Media (2018, creciente)                  | ✅ Muy alta (2012, automation std)   | ✅ Alta (2011, AWS native)  | ⚠️ Media (2020, ARM evolution) |
| **Adopción**                 | ✅ Muy alta (48K⭐, 1K+ providers)               | ⚠️ Media (21K⭐, expanding)                 | ✅ Muy alta (68K⭐, DevOps std)      | ✅ Alta (AWS standard)      | ⚠️ Media (Azure adoption)      |
| **Modelo de gestión**        | ⚠️ Herramienta CLI                               | ⚠️ Herramienta CLI                          | ⚠️ Herramienta CLI                   | ✅ Gestionado (AWS)         | ✅ Gestionado (Azure)          |
| **Complejidad operativa**    | ⚠️ Media (0.5 FTE, 5-10h/sem)                    | ⚠️ Alta (1 FTE, 10-20h/sem)                 | ⚠️ Alta (1 FTE, 10-20h/sem)          | ✅ Baja (0.25 FTE, <5h/sem) | ✅ Baja (0.25 FTE, <5h/sem)    |
| **Seguridad**                | ✅ Enterprise grade                              | ✅ Enterprise grade                         | ✅ SSH/Enterprise                    | ✅ AWS IAM                  | ✅ Azure RBAC                  |
| **Gestión de estado**        | ✅ Robusto y seguro                              | ✅ Estado backend                           | ❌ No state file                     | ✅ S3 backend               | ✅ Azure backend               |
| **Multi-entorno**            | ✅ Workspaces nativos                            | ✅ Stacks nativos                           | ⚠️ Inventarios                       | ✅ Parameters               | ✅ Parameters                  |
| **Versionado (módulos)**     | ✅ Registry + semvering                          | ✅ Registry + versioning                    | ✅ Git tags + Galaxy                 | ✅ CloudFormation registry  | ✅ Template Specs versioning   |
| **Módulos**                  | ✅ Reutilizables                                 | ✅ Reutilizables                            | ✅ Roles/Collections                 | ⚠️ Solo AWS                 | ⚠️ Solo Azure                  |
| **Bloqueo de estado**        | ✅ DynamoDB, S3, Terraform Cloud                 | ✅ Pulumi Service (automático)              | ❌ No state file                     | ✅ S3 backend locking       | ✅ Azure Storage locking       |
| **Detección de deriva**      | ✅ terraform plan detecta drift                  | ✅ pulumi refresh + preview                 | ⚠️ Manual (ansible-playbook --check) | ✅ drift detection nativo   | ✅ what-if operations          |
| **Capacidad de importación** | ✅ terraform import completo                     | ✅ pulumi import para recursos              | ⚠️ Limitado (facts gathering)        | ✅ cloudformation import    | ✅ ARM template import         |
| **Policy as Code**           | ✅ Sentinel, OPA, Checkov integration            | ✅ Policy packs (TypeScript/Python)         | ⚠️ Custom validation modules         | ⚠️ CloudFormation Guard     | ⚠️ Azure Policy integration    |
| **Soporte de pruebas**       | ✅ Terratest, Kitchen-Terraform, Terraform test  | ✅ Unit tests (TypeScript/Python)           | ✅ Molecule, Kitchen-Ansible         | ⚠️ TaskCat, cfn-lint        | ⚠️ ARM-TTK, Pester             |
| **Costos**                   | ✅ Gratis OSS + $20/usuario/mes (Cloud opcional) | ⚠️ $1/crédito + planes desde $20/mes (SaaS) | ✅ $0 licencia                       | ✅ Incluido en AWS          | ✅ Incluido en Azure           |

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
