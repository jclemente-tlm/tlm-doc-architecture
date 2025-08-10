---
title: "Infraestructura como Código (IaC)"
sidebar_position: 6
---

## ✅ ESTADO

Aceptada – Agosto 2025

---

## 🗺️ CONTEXTO

Los servicios corporativos distribuidos requieren una estrategia IaC que soporte:

- **Multi-cloud deployment** (AWS, Azure, GCP) con portabilidad
- **Multi-entorno** (dev, staging, prod) con configuraciones específicas
- **Multi-tenancy** con recursos segregados por país/tenant
- **Versionado de infraestructura** con rollback y auditoría completa
- **Automatización CI/CD** integrada con pipelines de deployment
- **Compliance y seguridad** con políticas como código
- **Reutilización de módulos** para consistencia entre servicios
- **State management** distribuido y seguro
- **Disaster recovery** con infraestructura reproducible

La intención estratégica es **priorizar agnosticidad vs simplicidad operacional** para IaC empresarial.

Las alternativas evaluadas fueron:

- **Terraform** (HashiCorp, HCL, multi-cloud)
- **Pulumi** (Multi-lenguaje, programático)
- **Ansible** (Agentless, YAML)
- **AWS CloudFormation** (AWS nativo, YAML/JSON)
- **ARM Templates** (Azure nativo)
- **GCP Deployment Manager** (GCP nativo)

## 🔍 COMPARATIVA DE ALTERNATIVAS

### Comparativa Cualitativa

| Criterio | Terraform | Pulumi | Ansible | CloudFormation | ARM Templates | GCP DM |
|----------|-----------|--------|---------|----------------|---------------|--------|
| **Agnosticidad** | ✅ Multi-cloud nativo | ✅ Multi-cloud | ✅ Agnóstico | ❌ Lock-in AWS | ❌ Lock-in Azure | ❌ Lock-in GCP |
| **Operación** | ✅ HCL declarativo | 🟡 Código imperativo | ✅ YAML simple | ✅ YAML/JSON | ✅ JSON/Bicep | ✅ YAML |
| **Ecosistema** | ✅ Providers extensos | ✅ Buena cobertura | 🟡 Módulos limitados | 🟡 Solo AWS | 🟡 Solo Azure | 🟡 Solo GCP |
| **Estado** | ✅ Gestión avanzada | ✅ Gestión buena | 🟡 Sin estado | ✅ Nativo AWS | ✅ Nativo Azure | ✅ Nativo GCP |
| **CI/CD** | ✅ Integración excelente | ✅ Muy buena | ✅ Excelente | ✅ Buena | ✅ Buena | 🟡 Limitada |
| **Comunidad** | ✅ Muy activa | ✅ Creciente | ✅ Muy activa | ✅ Soporte AWS | ✅ Soporte Microsoft | 🟡 Limitada |
| **Aprendizaje** | ✅ HCL intuitivo | 🟡 Requiere programación | ✅ YAML fácil | 🟡 Sintaxis compleja | 🟡 JSON verboso | 🟡 Documentación limitada |

### Matriz de Decisión

| Solución | Agnosticidad | Ecosistema | Estado | Comunidad | Recomendación |
|----------|--------------|-----------|--------|-----------|---------------|
| **Terraform** | Excelente | Excelente | Excelente | Muy activa | ✅ **Seleccionada** |
| **Pulumi** | Excelente | Buena | Buena | Creciente | 🟡 Alternativa |
| **Ansible** | Excelente | Limitada | Sin estado | Muy activa | 🟡 Considerada |
| **CloudFormation** | Mala | Solo AWS | Nativo | Soporte AWS | ❌ Descartada |
| **ARM Templates** | Mala | Solo Azure | Nativo | Soporte MS | ❌ Descartada |
| **GCP DM** | Mala | Solo GCP | Nativo | Limitada | ❌ Descartada |

## 💰 ANÁLISIS DE COSTOS (TCO 3 años)

### Escenario Base: 5 servicios, 3 entornos, multi-cloud

| Solución | Licenciamiento | Infraestructura | Operación | TCO 3 años |
|----------|----------------|-----------------|-----------|------------|
| **Terraform** | US$0 (OSS) | US$0 | US$18,000/año | **US$54,000** |
| **Pulumi** | US$0 (OSS) | US$0 | US$24,000/año | **US$72,000** |
| **Ansible** | US$0 (OSS) | US$0 | US$21,000/año | **US$63,000** |
| **CloudFormation** | US$0 (incluido) | US$0 | US$15,000/año | **US$45,000** |
| **ARM Templates** | US$0 (incluido) | US$0 | US$15,000/año | **US$45,000** |
| **GCP Deployment Manager** | US$0 (incluido) | US$0 | US$18,000/año | **US$54,000** |

### Escenario Alto Volumen: 20 servicios, multi-región, compliance

| Solución | TCO 3 años | Portabilidad | Tiempo Deployment |
|----------|------------|--------------|-------------------|
| **Terraform** | **US$180,000** | Excelente - Multi-cloud | 5-15 min |
| **Pulumi** | **US$240,000** | Excelente - Multi-cloud | 5-12 min |
| **Ansible** | **US$210,000** | Buena - Config + IaC | 10-20 min |
| **CloudFormation** | **US$150,000** | Limitada - Solo AWS | 8-25 min |
| **ARM Templates** | **US$150,000** | Limitada - Solo Azure | 8-20 min |
| **GCP Deployment Manager** | **US$180,000** | Limitada - Solo GCP | 10-30 min |

### Factores de Costo Adicionales

```yaml
Consideraciones Terraform:
  State Backend: S3 + DynamoDB vs US$20K/año Terraform Cloud
  Módulos: Registry público vs US$15K/año privado
  Validación: Sentinel OSS vs US$25K/año enterprise
  Workspaces: Locales vs US$20/usuario/mes cloud
  Migración: US$0 entre clouds vs US$100K vendor lock-in
  Capacitación: US$5K vs US$15K para herramientas propietarias
  Downtime evitado: US$200K/año vs US$500K/año manual
```

---

## 🎯 DECISIÓN

Se adopta **Terraform** como herramienta estándar de Infrastructure as Code para todos los servicios corporativos.

### Justificación Técnica

- **Agnosticidad multi-cloud** permite portabilidad entre AWS, Azure, GCP
- **Ecosistema maduro** con miles de módulos reutilizables
- **State management robusto** con backends seguros y distribuidos
- **Integración CI/CD nativa** con GitHub Actions y pipelines
- **Sintaxis declarativa HCL** fácil de leer y mantener
- **Validación y testing** integrados con plan/apply workflow
- **Comunidad activa** y documentación extensa

### Alternativas Descartadas

- **Pulumi**: Menor adopción y ecosistema vs Terraform
- **CloudFormation**: Lock-in AWS, limitada portabilidad
- **ARM Templates**: Lock-in Azure, menor ecosistema
- **Ansible**: Enfoque imperativo, state management limitado

---

## ⚖️ CONSECUENCIAS

### Positivas

✅ **Portabilidad multi-cloud** garantizada para toda la infraestructura
✅ **Reutilización de módulos** entre servicios y entornos
✅ **Versionado de infraestructura** con rollback y auditoría
✅ **Automatización CI/CD** integrada con pipelines
✅ **Ecosistema maduro** con amplia comunidad y soporte

### Negativas

⚠️ **Curva de aprendizaje** para equipos nuevos en HCL
⚠️ **Gestión de estado** requiere configuración cuidadosa
⚠️ **Dependencia de HashiCorp** para evolución del producto

### Mitigaciones

- Capacitación en Terraform y HCL para equipos
- Implementación de backends seguros para state management
- Documentación de módulos y buenas prácticas internas

---

## 📚 REFERENCIAS

- [Terraform Documentation](https://www.terraform.io/docs)
- [Terraform Registry](https://registry.terraform.io/)
- [HashiCorp Learn](https://learn.hashicorp.com/terraform)
