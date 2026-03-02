---
title: "ADR-004: AWS Secrets Manager"
sidebar_position: 4
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
- **GitHub Secrets** (Gestionado GitHub, CI/CD integrado)
- **HashiCorp Vault** (Open source/Enterprise, agnóstico)

## 🔍 COMPARATIVA DE ALTERNATIVAS

| Criterio                       | AWS Secrets Manager                               | Azure Key Vault                                 | Google Secret Manager                              | GitHub Secrets                     | HashiCorp Vault                             |
| ------------------------------ | ------------------------------------------------- | ----------------------------------------------- | -------------------------------------------------- | ---------------------------------- | ------------------------------------------- |
| **Agnosticidad**               | ❌ Lock-in AWS                                    | ❌ Lock-in Azure                                | ❌ Lock-in GCP                                     | ❌ Lock-in GitHub                  | ✅ Totalmente agnóstico                     |
| **Madurez**                    | ✅ Muy alta (2018, AWS enterprise)                | ✅ Muy alta (2016, Azure enterprise)            | ⚠️ Media (2019, creciente)                         | ⚠️ Básica (CI/CD limitado)         | ✅ Muy alta (2015, estable)                 |
| **Adopción**                   | ✅ Muy alta (AWS standard)                        | ✅ Muy alta (Azure standard)                    | ⚠️ Media (GCP adoption)                            | ⚠️ Limitada (GitHub Actions only)  | ✅ Muy alta (30K+ empresas)                 |
| **Modelo de gestión**          | ✅ Gestionado (AWS)                               | ✅ Gestionado (Azure)                           | ✅ Gestionado (GCP)                                | ✅ Gestionado (GitHub)             | ⚠️ Self-hosted                              |
| **Complejidad operativa**      | ✅ Baja (0.25 FTE, `<5h/sem)`                     | ✅ Baja (0.25 FTE, `<5h/sem)`                   | ✅ Baja (0.25 FTE, `<5h/sem)`                      | ✅ Baja (0.25 FTE, `<5h/sem)`      | ⚠️ Alta (1 FTE, 10-20h/sem)                 |
| **Seguridad**                  | ✅ Enterprise grade                               | ✅ Enterprise grade                             | ✅ Enterprise grade                                | ⚠️ Básica CI/CD                    | ✅ Enterprise grade                         |
| **Integración .NET**           | ✅ AWSSDK.SecretsManager (10M+ DL/mes, .NET 6+)   | ✅ Azure.Security.KeyVault.Secrets (5M+ DL/mes) | ⚠️ Google.Cloud.SecretManager (500K+ DL/mes)       | ⚠️ Solo CI/CD (no runtime)         | ✅ VaultSharp (200K+ DL/mes, .NET Standard) |
| **Multi-tenancy**              | ✅ Por paths/tags                                 | ✅ Por vaults                                   | ✅ Por proyectos                                   | ⚠️ Por repos                       | ✅ Namespaces/policies                      |
| **Rendimiento**                | ✅ `<5ms`en región                                | ✅ ~10-20ms en región Azure                     | ✅ ~20-50ms en región GCP                          | ❌ Solo CI/CD                      | ✅ `<2ms`self-hosted                        |
| **Escalabilidad**              | ✅ Hasta 10K secrets, 100K API calls/min (AWS)    | ✅ Hasta 100K+ secrets (Azure enterprise)       | ✅ Hasta 10K secrets (Google Cloud)                | ⚠️ `<1K`secrets máx (GitHub repos) | ✅ Hasta 100K+ secrets (HashiCorp cases)    |
| **Alta disponibilidad**        | ✅ 99.99% SLA                                     | ✅ 99.95% SLA Geo-redundante                    | ✅ 99.9% SLA Multi-regional                        | ✅ 99.95% SLA (global CDN)         | ⚠️ Sin SLA (manual config)                  |
| **Rotación**                   | ✅ Automática                                     | ✅ Automática                                   | ✅ Automática                                      | ❌ Manual                          | ✅ Muy flexible                             |
| **Auditoría**                  | ✅ CloudTrail                                     | ✅ Azure Monitor                                | ✅ Cloud Audit Logs                                | ⚠️ Logs básicos                    | ✅ Audit backend                            |
| **Soporte HSM**                | ✅ AWS CloudHSM integrado (FIPS 140-2 Level 3)    | ✅ Dedicated HSM, Managed HSM                   | ✅ Cloud HSM (FIPS 140-2 Level 3)                  | ❌ No soportado                    | ✅ HSM plugin (PKCS#11, AWS KMS)            |
| **Versionado de secretos**     | ✅ Múltiples versiones + AWSCURRENT/AWSPREVIOUS   | ✅ Versionado completo con tags                 | ✅ Versiones automáticas                           | ✅ Por branches/environments       | ✅ Versiones ilimitadas con history         |
| **Replicación entre regiones** | ✅ Multi-region automática                        | ✅ Geo-replication                              | ✅ Multi-regional nativo                           | ❌ Solo región única               | ⚠️ Manual (replication setup necesario)     |
| **Acceso de emergencia**       | ✅ Break-glass via IAM policies                   | ✅ Emergency access policies                    | ✅ Break-glass accounts                            | ⚠️ Admin access GitHub             | ✅ Root tokens, recovery keys               |
| **API Rate Limits**            | ✅ 1500 req/seg (configurable)                    | ✅ 2000 req/seg (configurable)                  | ✅ 1800 req/seg quota                              | ✅ 10K req/hora (GitHub API)       | ⚠️ Sin límites (self-managed)               |
| **Costos**                     | ⚠️ $0.40/secret/mes + $0.05/10K ops (~$20-40/mes) | ✅ $0.03/10K ops (~$5-15/mes)                   | ⚠️ $0.06/versión/mes + $0.03/10K ops (~$10-25/mes) | ✅ Incluido en GitHub              | ⚠️ $0 licencia + ~$200-400/mes infra        |

**Leyenda:** ✅ Cumple completamente | ⚠️ Cumple parcialmente | ❌ No cumple

## ✔️ DECISIÓN

Se selecciona **AWS Secrets Manager** como solución para la gestión de secretos en todos los entornos del servicio de notificaciones.

### Justificación

Se selecciona **AWS Secrets Manager** por las siguientes razones:

- **Integración nativa** con AWS IAM y servicios como EC2, Lambda, ECS y SQS, lo que facilita la gestión de permisos y la rotación automática de credenciales.
- **Menor complejidad operativa** frente a opciones autogestionadas como HashiCorp Vault, al ser un servicio totalmente gestionado con alta disponibilidad y escalabilidad garantizada por AWS.
- **Seguridad y cumplimiento**: cifrado en tránsito y reposo, registros de auditoría integrados con CloudTrail y cumplimiento de estándares como PCI DSS, ISO y SOC.
- **Desempeño y latencia óptimos** para cargas en AWS, superando a alternativas como Azure Key Vault en este contexto.
- **Costos operativos optimizados**, al no requerir infraestructura dedicada y estar plenamente integrado en el ecosistema AWS.
- **Simplicidad de integración** gracias a SDKs y APIs compatibles con .NET, y automatización vía IaC (CloudFormation, Terraform).

### Alternativas descartadas

- **Azure Key Vault:** lock-in Azure, infraestructura AWS ya establecida, menor integración con servicios AWS nativos
- **Google Secret Manager:** lock-in GCP, **vendor adicional sin infraestructura GCP existente** (requiere cuenta/proyecto/billing GCP activo), **SDK .NET adicional** (Google.Cloud.SecretManager) a mantener, **complejidad multi-vendor** (AWS + Azure + GCP) sin beneficio diferencial, **overhead operativo** (tercera consola cloud, tercera facturación, tercer soporte), menor integración ecosistema AWS
- **GitHub Secrets:** limitado exclusivamente a CI/CD (GitHub Actions), no soporta uso runtime en aplicaciones productivas, sin rotación automática enterprise, no reemplaza secrets manager corporativo
- **HashiCorp Vault:** complejidad operativa alta (HA, unsealing, backups), requiere expertise DevOps dedicado, costos infraestructura + mantenimiento, sobrede-dimensionado para escala actual

---

## ⚠️ CONSECUENCIAS

### Positivas

- El ciclo de vida de los secretos será gestionado exclusivamente en AWS.
- Las aplicaciones y microservicios deben autenticarse vía IAM para acceder a los secretos.
- Se documentará el uso y acceso en los manuales de operación y seguridad.

### Negativas (Riesgos y Mitigaciones)

- **Vendor lock-in AWS:** mitigado con capa de abstracción (`ISecretStore`) y plan de migración documentado
- **Costo superior:** mitigado con caché local de secretos y uso de Parameter Store para baja sensibilidad
- **Integraciones fuera de AWS:** mitigado con cross-account roles y VPC endpoints

---

## 📚 REFERENCIAS

- [AWS Secrets Manager Pricing](https://aws.amazon.com/secrets-manager/pricing/)
- [AWS Secrets Manager Docs](https://docs.aws.amazon.com/secretsmanager/latest/userguide/intro.html)
- [Azure Key Vault Pricing](https://azure.microsoft.com/en-us/pricing/details/key-vault/)
- [Azure Key Vault Docs](https://learn.microsoft.com/en-us/azure/key-vault/general/)
- [HashiCorp Vault Pricing](https://www.hashicorp.com/products/vault/pricing)
- [HashiCorp Vault Docs](https://www.vaultproject.io/docs/)
- [GitHub Secrets Docs](https://docs.github.com/en/actions/security-guides/using-secrets-in-github-actions)
- [Comparativa HashiCorp Vault vs AWS Secrets Manager vs Azure Key Vault](https://sanj.dev/post/hashicorp-vault-aws-secrets-azure-key-vault-comparison)
- [Arc42: Decisiones de arquitectura](https://arc42.org/decision/)
