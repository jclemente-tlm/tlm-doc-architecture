---
title: "ADR-003: AWS Secrets Manager"
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
- **Google Secret Manager** (Gestionado GCP, integración nativa)
- **HashiCorp Vault** (Open source/Enterprise, agnóstico)
- **CyberArk Conjur** (Enterprise secrets management, agnóstico)
- **Doppler** (SaaS secrets management, multi-cloud)

## 🔍 COMPARATIVA DE ALTERNATIVAS

### Comparativa Cualitativa

| Criterio            | AWS Secrets Manager      | Azure Key Vault          | Google Secret Manager    | HashiCorp Vault         | CyberArk Conjur         | Doppler             |
| ------------------- | ------------------------ | ------------------------ | ------------------------ | ----------------------- | ----------------------- | ------------------- |
| **Agnosticidad**    | ❌ Lock-in AWS           | ❌ Lock-in Azure         | ❌ Lock-in GCP           | ✅ Totalmente agnóstico | ✅ Agnóstico            | ✅ Multi-cloud SaaS |
| **Operación**       | ✅ Totalmente gestionado | ✅ Totalmente gestionado | ✅ Totalmente gestionado | ⚠️ Requiere gestión     | ⚠️ Requiere gestión     | ✅ SaaS gestionado  |
| **Seguridad**       | ✅ Enterprise grade      | ✅ Enterprise grade      | ✅ Enterprise grade      | ✅ Máxima seguridad     | ✅ Nivel corporativo    | ✅ Enterprise grade |
| **Ecosistema .NET** | ✅ Muy buena             | ✅ Excelente             | ⚠️ Limitada              | ✅ Buena                | ✅ Buena                | ✅ Excelente SDK    |
| **Rotación**        | ✅ Automática            | ✅ Automática            | ✅ Automática            | ✅ Muy flexible         | ✅ Políticas avanzadas  | ✅ Integraciones    |
| **Costos**          | ⚠️ Por uso               | ✅ Muy económico         | ✅ Muy económico         | ⚠️ Infraestructura      | ❌ Licencias enterprise | ⚠️ US$24-120/mes    |

**Leyenda:** ✅ Cumple completamente | ⚠️ Cumple parcialmente | ❌ No cumple

## ✔️ DECISIÓN

Se selecciona **AWS Secrets Manager** como solución para la gestión de secretos en todos los entornos del servicio de notificaciones.

## Justificación

Se selecciona **AWS Secrets Manager** por las siguientes razones:

- **Integración nativa** con AWS IAM y servicios como EC2, Lambda, ECS y SQS, lo que facilita la gestión de permisos y la rotación automática de credenciales.
- **Menor complejidad operativa** frente a opciones autogestionadas como HashiCorp Vault, al ser un servicio totalmente gestionado con alta disponibilidad y escalabilidad garantizada por AWS.
- **Seguridad y cumplimiento**: cifrado en tránsito y reposo, registros de auditoría integrados con CloudTrail y cumplimiento de estándares como PCI DSS, ISO y SOC.
- **Desempeño y latencia óptimos** para cargas en AWS, superando a alternativas como Azure Key Vault en este contexto.
- **Costos operativos optimizados**, al no requerir infraestructura dedicada y estar plenamente integrado en el ecosistema AWS.
- **Simplicidad de integración** gracias a SDKs y APIs compatibles con .NET, y automatización vía IaC (CloudFormation, Terraform).

## Alternativas descartadas

- **Azure Key Vault:** lock-in Azure, infraestructura AWS ya establecida, menor integración con servicios AWS nativos
- **Google Secret Manager:** lock-in GCP, menor integración ecosistema AWS, SDK .NET menos maduro que AWS
- **HashiCorp Vault:** complejidad operativa alta (HA, unsealing, backups), requiere expertise DevOps dedicado, costos infraestructura + mantenimiento, sobrede-dimensionado para escala actual
- **CyberArk Conjur:** costos enterprise prohibitivos (US$50K+ licencias), complejidad excesiva para necesidades actuales, orientado a grandes corporaciones
- **Doppler:** SaaS lock-in (US$24-120/mes), menor madurez vs AWS Secrets Manager, vendor risk startup vs AWS, menor integración IAM/VPC

---

## ⚠️ CONSECUENCIAS

### Positivas

- El ciclo de vida de los secretos será gestionado exclusivamente en AWS.
- Las aplicaciones y microservicios deben autenticarse vía IAM para acceder a los secretos.
- Se documentará el uso y acceso en los manuales de operación y seguridad.

### Negativas (Riesgos y Mitigaciones)

- **Vendor lock-in AWS:** mitigado con capa de abstracción (`ISecretStore`), módulos IaC reutilizables y plan de migración validado anualmente.
- **Costo superior:** optimizado mediante caché local de secretos, consolidación segura y uso de AWS Parameter Store para secretos de baja sensibilidad.
- **Integraciones fuera de AWS:** mitigadas con cross-account roles, VPC endpoints y sincronización controlada en entornos híbridos.

---

## 📚 REFERENCIAS

- [AWS Secrets Manager Pricing](https://aws.amazon.com/secrets-manager/pricing/)
- [AWS Secrets Manager Docs](https://docs.aws.amazon.com/secretsmanager/latest/userguide/intro.html)
- [Azure Key Vault Pricing](https://azure.microsoft.com/en-us/pricing/details/key-vault/)
- [Azure Key Vault Docs](https://learn.microsoft.com/en-us/azure/key-vault/general/)
- [HashiCorp Vault Pricing](https://www.hashicorp.com/products/vault/pricing)
- [HashiCorp Vault Docs](https://www.vaultproject.io/docs/)
- [CyberArk Conjur](https://www.cyberark.com/products/secrets-manager-conjur/)
- [Doppler Secrets Manager](https://www.doppler.com/)
- [Comparativa HashiCorp Vault vs AWS Secrets Manager vs Azure Key Vault](https://sanj.dev/post/hashicorp-vault-aws-secrets-azure-key-vault-comparison)
- [Arc42: Decisiones de arquitectura](https://arc42.org/decision/)
