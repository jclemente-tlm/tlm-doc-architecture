---
title: "ADR-024: Checkov IaC Scanning"
sidebar_position: 24
---

## ✅ ESTADO

Aceptada – Enero 2026

---

## 🗺️ CONTEXTO

Los servicios corporativos requieren escaneo de seguridad automatizado de infraestructura como código para:

- **Análisis de misconfigurations** en Terraform antes de apply
- **Compliance** con estándares de seguridad (CIS, NIST, PCI-DSS)
- **Detección de secrets** hardcodeados en IaC
- **Integración en CI/CD** con gates automáticos (fail on critical)
- **Prevención de drift** de configuraciones seguras
- **Reportes ejecutivos** de postura de seguridad de infraestructura
- **Costos controlados** y herramientas OSS

La estrategia prioriza **shift-left security** para IaC con herramientas OSS integradas en GitHub Actions (ADR-009).

Alternativas evaluadas:

- **Checkov** (OSS, Bridgecrew/Palo Alto, 1000+ checks, multi-IaC)
- **tfsec** (OSS, Aqua Security, especializado Terraform)
- **Terraform Sentinel** (HashiCorp Enterprise, policy-as-code)
- **Snyk IaC** (comercial SaaS, completo, costoso)
- **AWS Config Rules** (nativo AWS, runtime, lock-in)

## 🔍 COMPARATIVA DE ALTERNATIVAS

### Comparativa Cualitativa

| Criterio              | Checkov                   | tfsec                 | Terraform Sentinel | Snyk IaC             | AWS Config            |
| --------------------- | ------------------------- | --------------------- | ------------------ | -------------------- | --------------------- |
| **Agnosticidad**      | ✅ Multi-IaC, multi-cloud | ✅ Terraform focus    | ⚠️ Terraform only  | ⚠️ Multi-IaC, SaaS   | ❌ Lock-in AWS        |
| **Cobertura**         | ✅ 1000+ checks           | ✅ 400+ checks        | ✅ Custom policies | ✅ Muy completa      | ⚠️ AWS resources only |
| **Frameworks**        | ✅ TF, CFN, K8s, Docker   | ⚠️ Terraform only     | ⚠️ Terraform only  | ✅ Multi-framework   | ⚠️ CFN focus          |
| **Integración CI/CD** | ✅ GitHub Actions nativo  | ✅ GitHub Actions     | ⚠️ TF Enterprise   | ✅ Plugins múltiples | ❌ Runtime only       |
| **Performance**       | ✅ Rápido (< 20s)         | ✅ Muy rápido (< 10s) | ⚠️ Medio           | ⚠️ Medio             | ✅ Runtime            |
| **Costos**            | ✅ Gratis OSS             | ✅ Gratis OSS         | ❌ Enterprise only | ❌ US$98/dev/mes     | ⚠️ Pago por uso       |
| **Custom Policies**   | ✅ Python-based           | ⚠️ Go-based           | ✅ Policy language | ✅ Rego-based        | ✅ Python Lambda      |
| **Reportes**          | ✅ SARIF, JSON, JUnit     | ✅ JSON, Checkstyle   | ⚠️ TF output       | ✅ Dashboard SaaS    | ✅ AWS Console        |
| **Suppressions**      | ✅ Inline comments        | ✅ Inline comments    | ✅ Policy-based    | ✅ Annotations       | ⚠️ Manual             |
| **Compliance**        | ✅ CIS, NIST, PCI, HIPAA  | ✅ CIS, custom        | ✅ Custom only     | ✅ Frameworks        | ✅ AWS frameworks     |

**Leyenda:** ✅ Cumple completamente | ⚠️ Cumple parcialmente | ❌ No cumple

---

## ✔️ DECISIÓN

Se selecciona **Checkov** como solución de IaC security scanning corporativa.

## Justificación

- **Costo cero** - herramienta OSS mantenida por Bridgecrew (Palo Alto Networks)
- **Cobertura más amplia** - 1000+ checks predefinidos (CIS, NIST, PCI-DSS, HIPAA)
- **Multi-framework** - Terraform, CloudFormation, Kubernetes, Dockerfiles
- **Custom policies** - Python-based para reglas corporativas específicas
- **Performance excelente** - < 20s por módulo Terraform, no impacta pipelines
- **Integración nativa GitHub Actions** - marketplace oficial, fácil configuración
- **SARIF output** - integrado con GitHub Security tab para visibilidad centralizada
- **Shift-left** - escaneo en PR y pre-commit, prevención de misconfigurations
- **Agnóstico** - funciona con cualquier cloud provider (AWS, Azure, GCP)
- **Ecosistema maduro** - 6K+ stars GitHub, comunidad activa, actualizaciones diarias

## Alternativas descartadas

- **tfsec:** Excelente para Terraform puro, pero limitado a TF (no soporta K8s, Dockerfiles)
- **Terraform Sentinel:** Requiere Terraform Enterprise (US$30K+), demasiado costoso
- **Snyk IaC:** US$98/dev/mes = US$52K/3 años - costo prohibitivo para capacidades similares
- **AWS Config:** Runtime only (no shift-left), lock-in AWS, solo evalúa recursos deployados

---

## ⚠️ CONSECUENCIAS

### Positivas

- Prevención temprana de misconfigurations en PR reviews (shift-left)
- Visibilidad centralizada en GitHub Security tab
- Compliance automatizado con CIS Benchmarks
- **Costo cero** - herramienta OSS sin licenciamiento
- Pipeline rápido (< 20s adicional por escaneo)
- Detección de secrets hardcodeados (evita leaks)

### Negativas (Riesgos y Mitigaciones)

- **False positives:** requiere configuración de suppressions corporativas (`.checkov.yaml`)
- **No auto-remediation:** solo sugerencias, requiere acción manual del equipo
- **Ruido inicial:** puede generar muchos findings - mitigado con rollout gradual y triaje
- **Mantenimiento de Checkov:** requiere actualización manual de versiones en workflows
- **Curva de aprendizaje:** equipo debe aprender a interpretar findings y crear custom policies

---

## 📚 REFERENCIAS

- [Checkov Documentation](https://www.checkov.io/)
- [Checkov GitHub Actions](https://github.com/bridgecrewio/checkov-action)
- [Checkov Policies List](https://www.checkov.io/5.Policy%20Index/terraform.html)
- [CIS Benchmarks](https://www.cisecurity.org/cis-benchmarks/)
- [Terraform Security Best Practices](https://www.terraform.io/docs/cloud/guides/recommended-practices/part1.html)
- [ADR-006: Terraform IaC](./adr-006-terraform-iac.md)
- [ADR-009: GitHub Actions CI/CD](./adr-009-github-actions-cicd.md)
- [ADR-023: Trivy Container Scanning](./adr-023-trivy-container-scanning.md)

---

**Decisión tomada por:** Equipo de Arquitectura + Security
**Fecha:** Enero 2026
**Próxima revisión:** Enero 2027
