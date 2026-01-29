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
- **HashiCorp Vault** (Open source/Enterprise, agnóstico)
- **Google Secret Manager** (Gestionado GCP, integración nativa)

## 🔍 COMPARATIVA DE ALTERNATIVAS

### Comparativa Cualitativa

| Criterio | AWS Secrets Manager | Azure Key Vault | Google Secret Manager | HashiCorp Vault |
|----------|---------------------|-----------------|----------------------|-----------------|
| **Agnosticidad** | ❌ Lock-in AWS | ❌ Lock-in Azure | ❌ Lock-in GCP | ✅ Totalmente agnóstico |
| **Operación** | ✅ Totalmente gestionado | ✅ Totalmente gestionado | ✅ Totalmente gestionado | 🟡 Requiere gestión |
| **Seguridad** | ✅ Enterprise grade | ✅ Enterprise grade | ✅ Enterprise grade | ✅ Máxima seguridad |
| **Ecosistema .NET** | ✅ Muy buena | ✅ Excelente | 🟡 Limitada | ✅ Buena |
| **Rotación** | ✅ Automática | ✅ Automática | ✅ Automática | ✅ Muy flexible |
| **Costos** | 🟡 Por uso | ✅ Muy económico | ✅ Muy económico | 🟡 Infraestructura |

### Matriz de Decisión

| Solución | Agnosticidad | Operación | Seguridad | Ecosistema .NET | Recomendación |
|----------|--------------|-----------|-----------|-----------------|---------------|
| **AWS Secrets Manager** | Mala | Excelente | Excelente | Muy buena | ✅ **Seleccionada** |
| **Azure Key Vault** | Mala | Excelente | Excelente | Excelente | 🟡 Alternativa |
| **Google Secret Manager** | Mala | Excelente | Excelente | Limitada | 🟡 Alternativa |
| **HashiCorp Vault** | Excelente | Manual | Excelente | Buena | 🟡 Considerada |

## 💰 ANÁLISIS DE COSTOS (TCO 3 años)

### Escenario de referencia: 20 secretos y 50,000 operaciones/mes por servicio

> **Metodología y supuestos:** Se asume un uso promedio de 20 secretos y 50,000 operaciones mensuales por servicio, considerando rotaciones y operaciones extra. Los costos de Vault OSS consideran infraestructura y operación compartida entre servicios. El TCO (Total Cost of Ownership) se calcula para un horizonte de 3 años, incluyendo costos directos y estimaciones de operación. Los valores pueden variar según la frecuencia de rotación, almacenamiento premium y número de entornos.

| Servicio         | Secretos | Operaciones/mes | Costo mensual AWS | TCO 3 años AWS | Costo mensual Azure | TCO 3 años Azure | Costo mensual GCP | TCO 3 años GCP | Costo mensual Vault OSS | TCO 3 años Vault OSS |
|------------------|----------|-----------------|-------------------|----------------|---------------------|------------------|-------------------|----------------|------------------------|----------------------|
| API Gateway      | 20       | 50,000          | US$8.50           | US$306         | US$3.30             | US$119           | US$3.30           | US$119         | US$7.50                 | US$270               |
| Identidad        | 20       | 50,000          | US$8.50           | US$306         | US$3.30             | US$119           | US$3.30           | US$119         | US$7.50                 | US$270               |
| Notificación     | 20       | 50,000          | US$8.50           | US$306         | US$3.30             | US$119           | US$3.30           | US$119         | US$7.50                 | US$270               |
| Track & Trace    | 20       | 50,000          | US$8.50           | US$306         | US$3.30             | US$119           | US$3.30           | US$119         | US$7.50                 | US$270               |
| SITA Mensajería  | 20       | 50,000          | US$8.50           | US$306         | US$3.30             | US$119           | US$3.30           | US$119         | US$7.50                 | US$270               |
| **Total**        | -        | -               | **US$42.50**      | **US$1,530**   | **US$16.50**        | **US$595**       | **US$16.50**      | **US$595**     | **US$37.50**            | **US$1,350**         |

**Detalle de cálculo AWS Secrets Manager:**

- 20 secretos × US$0.40 = US$8.00/mes
- 50,000 operaciones API: primeras 10,000 gratis, resto: 40,000/10,000=4 × US$0.05 = US$0.20/mes
- Total mensual aproximado: US$8.20 (redondeado a US$8.50 por posibles rotaciones y operaciones extra)

**Detalle de cálculo Azure Key Vault:**

- 20 secretos × US$0.03 = US$0.60/mes
- 50,000 operaciones API: primeras 10,000 gratis, resto: 40,000/10,000=4 × US$0.03 = US$0.12/mes
- Total mensual aproximado: US$0.72 (se considera US$3.30 para cubrir posibles operaciones extra, rotaciones y almacenamiento premium)

**Detalle de cálculo Google Secret Manager:**

- 20 secretos × US$0.03 = US$0.60/mes
- 50,000 operaciones API: primeras 10,000 gratis, resto: 40,000/10,000=4 × US$0.03 = US$0.12/mes
- Total mensual aproximado: US$0.72 (se considera US$3.30 para cubrir posibles operaciones extra, rotaciones y almacenamiento premium)

**Detalle de cálculo HashiCorp Vault OSS:**

- Licencia OSS: US$0
- Infraestructura mínima: 1 VM t3.medium AWS (~US$30/mes), almacenamiento y backup (~US$5/mes)
- Operación y mantenimiento: estimado US$50/mes (tiempo técnico, prorrateado por servicio)
- Total mensual aproximado por servicio: US$7.50 (asumiendo 4 servicios comparten la infraestructura)

---

## Consideraciones técnicas y riesgos

### Límites clave

- **AWS Secrets Manager:** hasta 500,000 secretos por cuenta, 64 KB por secreto, 10,000 solicitudes API/segundo.
- **Azure Key Vault:** sin límite práctico de secretos, 25 KB por secreto, 4,000 operaciones de lectura/10 seg, 300 escrituras/10 seg.
- **Google Secret Manager:** hasta 1 millón de versiones por proyecto, 64 KB por secreto, 90,000 accesos/minuto por proyecto.
- **HashiCorp Vault:** sin límite de secretos, tamaño por entrada 512 KiB (Consul) o 1 MiB (integrated), depende de la infraestructura.

### Riesgos y mitigación

- **Vendor lock-in AWS:** mitigado con capa de abstracción (`ISecretStore`), módulos IaC reutilizables y plan de migración validado anualmente.
- **Costo superior:** optimizado mediante caché local de secretos, consolidación segura y uso de AWS Parameter Store para secretos de baja sensibilidad.
- **Integraciones fuera de AWS:** mitigadas con cross-account roles, VPC endpoints y sincronización controlada en entornos híbridos.

---

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

- **AWS Secrets Manager:** lock-in AWS, costos adicionales
- **Azure Key Vault:** lock-in Azure, costos adicionales
- **Google Secret Manager:** lock-in GCP, costos adicionales
- **Vault OSS:** mayor complejidad operativa

---

## ⚠️ CONSECUENCIAS

- El ciclo de vida de los secretos será gestionado exclusivamente en AWS.
- Las aplicaciones y microservicios deben autenticarse vía IAM para acceder a los secretos.
- Se documentará el uso y acceso en los manuales de operación y seguridad.
- Se implementarán las mitigaciones descritas y un plan de revisión anual.

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
