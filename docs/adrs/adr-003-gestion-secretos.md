---
id: adr-003-gestion-de-secretos
title: "Gestión de Secretos"
sidebar_position: 3
---

## ✅ ESTADO

Aceptada – Agosto 2025

---

## 🗺️ CONTEXTO

Los servicios corporativos requieren una solución robusta de gestión de secretos para:

- **Credenciales de servicios externos** (APIs de notificación, SITA, proveedores)
- **Tokens y claves de autenticación** entre microservicios
- **Certificados y claves criptográficas** para comunicación segura
- **Cadenas de conexión** a bases de datos y servicios
- **Rotación automática** de credenciales críticas
- **Auditoría completa** de acceso y uso de secretos

La intención estratégica es **evaluar agnosticidad vs facilidad operacional** considerando que la gestión de secretos es crítica para la seguridad.

Las alternativas evaluadas fueron:

- **AWS Secrets Manager** (Gestionado AWS, integración nativa)
- **Azure Key Vault** (Gestionado Azure, integración nativa)
- **HashiCorp Vault** (Open source/Enterprise, agnóstico)
- **Kubernetes Secrets** (Nativo K8s, básico)

## 🔍 COMPARATIVA DE ALTERNATIVAS

### Comparativa Cualitativa

| Criterio | AWS Secrets Manager | Azure Key Vault | HashiCorp Vault | K8s Secrets |
|----------|---------------------|------------------|-----------------|-------------|
| **Agnosticidad** | ❌ Lock-in AWS | ❌ Lock-in Azure | ✅ Totalmente agnóstico | 🟡 Agnóstico pero básico |
| **Operación** | ✅ Totalmente gestionado | ✅ Totalmente gestionado | 🟡 Requiere gestión | ✅ Nativo en K8s |
| **Seguridad** | ✅ Enterprise grade | ✅ Enterprise grade | ✅ Máxima seguridad | 🟡 Básica |
| **Ecosistema .NET** | ✅ Integración nativa | ✅ Muy buena | ✅ Buena | 🟡 Limitada |
| **Rotación** | ✅ Automática | ✅ Automática | ✅ Muy flexible | ❌ Manual |
| **Costos** | 🟡 Por uso | ✅ Muy económico | 🟡 Infraestructura | ✅ Gratuito |

### Matriz de Decisión

| Solución | Agnosticidad | Operación | Seguridad | Ecosistema .NET | Recomendación |
|----------|--------------|-----------|-----------|-----------------|---------------|
| **AWS Secrets Manager** | Mala | Excelente | Excelente | Excelente | ✅ **Seleccionada** |
| **Azure Key Vault** | Mala | Excelente | Excelente | Muy buena | 🟡 Alternativa |
| **HashiCorp Vault** | Excelente | Manual | Excelente | Buena | 🟡 Considerada |
| **K8s Secrets** | Buena | Automática | Básica | Limitada | ❌ Descartada |

## 💰 ANÁLISIS DE COSTOS (TCO 3 años)

### Escenario Base: 100 secretos, 1M operaciones/mes, 4 países

| Solución | Licenciamiento | Infraestructura | Operación | TCO 3 años |
|----------|----------------|-----------------|-----------|------------|
| **AWS Secrets Manager** | Pago por uso | US$0 | US$0 | **US$14,400** |
| **Azure Key Vault** | Pago por uso | US$0 | US$0 | **US$1,080** |
| **HashiCorp Vault OSS** | US$0 (OSS) | US$3,600/año | US$36,000/año | **US$118,800** |
| **HashiCorp Vault Enterprise** | US$25,000/año | US$3,600/año | US$36,000/año | **US$193,800** |
| **Kubernetes Secrets** | US$0 (nativo) | US$0 | US$12,000/año | **US$36,000** |

### Escenario Alto Volumen: 1,000 secretos, 10M operaciones/mes

| Solución | TCO 3 años | Escalabilidad |
|----------|------------|---------------|
| **AWS Secrets Manager** | **US$144,000** | Automática |
| **Azure Key Vault** | **US$10,800** | Automática |
| **HashiCorp Vault OSS** | **US$180,000** | Manual |
| **HashiCorp Vault Enterprise** | **US$255,000** | Manual |
| **Kubernetes Secrets** | **US$60,000** | Limitada |

### Factores de Costo Adicionales

```yaml
Consideraciones:
  Rotación automática: +30% operaciones en AWS/Azure
  Auditoría: Incluida en AWS/Azure, +US$12K/año en Vault
  Backup/DR: Incluido en AWS/Azure, +US$6K/año en Vault
  Compliance: Certificaciones incluidas vs auditorías propias
  Migración: US$0 en cloud vs US$15K en Vault
```

### Ejemplos de cálculo de costos mensuales

#### [AWS Secrets Manager](https://aws.amazon.com/secrets-manager/)

- 100 secretos activos: 100 × US$0.40 = US$40/mes
- 100,000 operaciones API: 10 × US$0.05 = US$0.50/mes
- **Total estimado:** US$40.50/mes

#### [Azure Key Vault](https://azure.microsoft.com/en-us/services/key-vault/)

- 100 secretos activos: 100 × US$0.03 = US$3/mes
- 100,000 operaciones API: 10 × US$0.03 = US$0.30/mes
- **Total estimado:** US$3.30/mes

#### [HashiCorp Vault](https://www.vaultproject.io/) (OSS, instalación mínima)

- Licencia OSS: US$0
- Infraestructura mínima: 1 VM t3.medium AWS (~US$30/mes), almacenamiento y backup (~US$5/mes)
- Operación y mantenimiento: estimado US$50/mes (tiempo técnico)
- **Total estimado:** US$85/mes (solo infraestructura y operación básica, sin HA ni soporte)

#### [HashiCorp Vault](https://www.vaultproject.io/) (Enterprise, instalación mínima)

- Licencia Enterprise: ~US$2,000/mes (precio base, puede variar)
- Infraestructura mínima: 1 VM t3.medium AWS (~US$30/mes), almacenamiento y backup (~US$5/mes)
- Operación y mantenimiento: estimado US$50/mes (tiempo técnico)
- **Total estimado:** US$2,085/mes (solo infraestructura y operación básica, sin HA ni soporte)

> Nota: `HashiCorp Vault OSS` no genera gastos por licencias, pero sí por infraestructura, operación y mantenimiento. La versión Enterprise puede superar los US$2,000/mes dependiendo de la escala y soporte.

### Límites y consideraciones

- **AWS Secrets Manager:** hasta 500,000 secretos por cuenta, 10,000 solicitudes API/segundo, tamaño máximo de secreto 64 KB.
- **Azure Key Vault:** hasta 1 millón de secretos por bóveda, límites de solicitudes API por región.
- **HashiCorp Vault:** sin límites por software, pero limitado por capacidad de infraestructura y configuración.

### Agnosticismo, lock-in y mitigación

- **Lock-in:** AWS Secrets Manager implica dependencia de AWS, pero se justifica por la integración nativa, menor latencia y operación simplificada en un entorno 100% AWS.
- **Mitigación:** El uso de SDKs estándar y automatización IaC permite migrar a otras soluciones si el contexto cambia. La arquitectura desacopla el acceso a secretos mediante interfaces, facilitando un eventual reemplazo.

---

## ✔️ DECISIÓN

Se selecciona **AWS Secrets Manager** como solución para la gestión de secretos en todos los entornos del servicio de notificaciones.

## Justificación

- Integración nativa con AWS IAM y servicios AWS (EC2, Lambda, ECS, SQS, etc.), facilitando la gestión de permisos y rotación automática de credenciales.
- Reducción de complejidad operativa: No requiere despliegue ni mantenimiento adicional, a diferencia de HashiCorp Vault.
- Alta disponibilidad y escalabilidad gestionada por AWS, sin necesidad de configuración manual.
- Auditoría y trazabilidad: Registros de acceso y cambios integrados con CloudTrail.
- Costos operativos optimizados: Incluido en el ecosistema AWS, sin costos adicionales por infraestructura dedicada.
- Cumplimiento de estándares de seguridad (PCI DSS, ISO, SOC) y cifrado en tránsito y en reposo.
- Desempeño y latencia: Menor latencia para servicios desplegados en AWS, comparado con Azure Key Vault.
- Simplicidad de integración: SDK y APIs compatibles con .NET y automatización vía IaC (CloudFormation, Terraform).

## Alternativas descartadas

- **Azure Key Vault:** Requiere integración adicional y mayor latencia fuera de Azure; no aporta ventajas en el contexto AWS.
- **HashiCorp Vault:** Solución robusta pero implica mayor complejidad operativa, despliegue y mantenimiento, innecesarios para el alcance actual.

---

## ⚠️ CONSECUENCIAS

- El ciclo de vida de los secretos será gestionado exclusivamente en AWS.
- Las aplicaciones y microservicios deben autenticarse vía IAM para acceder a los secretos.
- Se documentará el uso y acceso en los manuales de operación y seguridad.

---

## 📚 REFERENCIAS

- [AWS Secrets Manager Pricing](https://aws.amazon.com/secrets-manager/pricing/)
- [AWS Secrets Manager Docs](https://docs.aws.amazon.com/secretsmanager/latest/userguide/intro.html)
- [Azure Key Vault Pricing](https://azure.microsoft.com/en-us/pricing/details/key-vault/)
- [Azure Key Vault Docs](https://learn.microsoft.com/en-us/azure/key-vault/general/)
- [HashiCorp Vault Pricing](https://www.hashicorp.com/products/vault/pricing)
- [HashiCorp Vault Docs](https://www.vaultproject.io/docs/)
- [Comparativa HashiCorp Vault vs AWS Secrets Manager vs Azure Key Vault](https://sanj.dev/post/hashicorp-vault-aws-secrets-azure-key-vault-comparison)
- [Arc42: Decisiones de arquitectura](https://arc42.org/decision/)
