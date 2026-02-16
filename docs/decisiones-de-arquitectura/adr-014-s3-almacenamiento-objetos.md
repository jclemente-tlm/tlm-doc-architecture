---
title: "ADR-014: S3 Almacenamiento Objetos"
sidebar_position: 14
---

## ✅ ESTADO

Aceptada – Agosto 2025

---

## 🗺️ CONTEXTO

Los servicios corporativos requieren una solución de almacenamiento de objetos que permita:

- **Portabilidad multi-cloud** sin lock-in (AWS, Azure, GCP, on-premises)
- **Multi-tenancy** con segregación de datos por país/tenant
- **Escalabilidad masiva** para documentos, imágenes, logs y backups
- **Durabilidad garantizada** con replicación y versionado automático
- **Seguridad avanzada** con encriptación, IAM y compliance
- **API estándar S3** para máxima compatibilidad
- **Disaster recovery** con backup cross-region
- **Costos optimizados** con lifecycle policies y storage classes
- **Performance consistente** para aplicaciones críticas
- **Integración CI/CD** para artifacts y deployment assets

Alternativas evaluadas:

- **AWS S3** (estándar de mercado, alta durabilidad, ecosistema enorme)
- **Azure Blob Storage** (fuerte en entornos Microsoft, buena integración)
- **Google Cloud Storage (GCS)** (muy rápido, buen manejo de clases de almacenamiento)
- **Digital Ocean Spaces** (S3-compatible, pricing simple, CDN integrado)
- **MinIO** (auto-hosteado, open source, 100% S3 compatible, portable a cualquier infraestructura)

## 🔍 COMPARATIVA DE ALTERNATIVAS

| Criterio                  | AWS S3                           | Digital Ocean Spaces     | Azure Blob Storage      | Google Cloud Storage   | MinIO                   |
| ------------------------- | -------------------------------- | ------------------------ | ----------------------- | ---------------------- | ----------------------- |
| **Integración AWS**       | ✅ Nativa (ECS, IAM, VPC)        | ❌ Externa               | ❌ Externa              | ❌ Externa             | ❌ Externa              |
| **Madurez/Ecosistema**    | ✅ Estándar de facto (2006)      | ⚠️ Limitado              | ✅ Enterprise maduro    | ✅ Enterprise maduro   | ✅ CNCF, muy activo     |
| **Modelo de gestión**     | ✅ Gestionado (AWS)              | ✅ Gestionado (SaaS)     | ✅ Gestionado (Azure)   | ✅ Gestionado (GCP)    | ⚠️ Self-hosted          |
| **Complejidad operativa** | ✅ Baja (infra AWS)              | ⚠️ Media (vendor nuevo)  | ⚠️ Media (vendor nuevo) | ❌ Alta (vendor GCP)   | ⚠️ Media (setup)        |
| **Multi-tenancy**         | ✅ Buckets + IAM políticas       | ⚠️ Spaces + CORS         | ✅ Containers + RBAC    | ✅ Buckets + IAM       | ✅ Buckets + policies   |
| **Escalabilidad**         | ✅ Ilimitada probada             | ⚠️ Limitada enterprise   | ✅ Ilimitada            | ✅ Ilimitada           | ✅ Horizontal           |
| **Performance**           | ✅ Multi-AZ + CloudFront         | ✅ CDN integrado         | ✅ Geo-replicación      | ✅ Multi-regional      | ⚠️ Depende config       |
| **Features avanzados**    | ✅ Lifecycle, Classes, Replica   | ❌ Muy limitados         | ✅ Completos            | ✅ Completos           | ⚠️ Básicos              |
| **API S3**                | ✅ 100% nativa                   | ✅ 100% compatible       | ⚠️ Parcial              | ⚠️ Parcial             | ✅ 100% compatible      |
| **Versionado**            | ✅ Nativo (inmutable)            | ⚠️ Limitado              | ✅ Nativo               | ✅ Nativo              | ✅ Nativo               |
| **Seguridad**             | ✅ Enterprise grade              | ✅ Encriptación, CDN     | ✅ Enterprise grade     | ✅ Enterprise grade    | ✅ IAM, encriptación    |
| **Alta disponibilidad**   | ✅ 99.99% SLA (Multi-AZ)         | ✅ 99.95% SLA            | ✅ Geo-redundante       | ✅ Multi-regional      | ⚠️ Manual (HA setup)    |
| **Integración .NET**      | ✅ AWS SDK oficial               | ✅ AWS SDK compatible    | ✅ Azure SDK oficial    | ✅ Google SDK oficial  | ✅ AWS SDK compatible   |
| **Certificaciones**       | ✅ SOC2, HIPAA, PCI-DSS, ISO     | ⚠️ SOC2                  | ✅ Completo             | ✅ Completo            | ❌ Self-managed         |
| **Agnosticidad**          | ⚠️ Lock-in AWS (API S3 estándar) | ✅ S3-compatible         | ⚠️ Lock-in Azure        | ⚠️ Lock-in GCP         | ✅ OSS, multi-cloud     |
| **Costos**                | ⚠️ Moderado (US$23/TB + egress)  | ✅ Flat (US$5/mes 250GB) | ⚠️ Moderado pago x uso  | ⚠️ Moderado pago x uso | ✅ Solo infraestructura |

**Leyenda:** ✅ Cumple completamente | ⚠️ Cumple parcialmente | ❌ No cumple

## ✔️ DECISIÓN

Se selecciona **AWS S3** como solución estándar de almacenamiento de objetos para todos los servicios y microservicios corporativos.

### Justificación

- Operación gestionada, sin infraestructura propia
- Escalabilidad y durabilidad garantizadas
- Integración nativa con AWS y .NET
- Costos bajos y pago por uso
- Compatibilidad total con API S3 y herramientas del ecosistema
- Observabilidad y monitoreo integrados

### Alternativas descartadas

- **Digital Ocean Spaces:** pricing simple ($5/mes 250GB+1TB transfer), CDN integrado, pero límite escalabilidad vs S3, menor SLA (99.95% vs 99.99%), ecosistema herramientas reducido, no ideal para almacenamiento masivo enterprise
- **MinIO:** portabilidad máxima pero mayor complejidad operativa (clustering, HA, backups, monitoreo), costos infraestructura ocultos, overhead vs solución gestionada, requiere expertise DevOps
- **Azure Blob Storage:** lock-in Azure, infraestructura AWS ya establecida (ADR-003, ADR-005, ADR-007), API no 100% S3-compatible (migración código)
- **Google Cloud Storage:** lock-in GCP, **vendor adicional sin infraestructura GCP existente** (requiere cuenta/proyecto/billing GCP activo), **SDK .NET adicional** (Google.Cloud.Storage) a mantener, **complejidad multi-vendor** (AWS + Azure + GCP) sin beneficio diferencial, **overhead operativo** (tercera consola cloud, tercera facturación, tercer soporte), menor integración ecosistema AWS, API no 100% S3-compatible

---

## ⚠️ CONSECUENCIAS

### Positivas

- Operación gestionada sin infraestructura propia
- Escalabilidad y durabilidad automáticas (99.999999999%)
- Integración nativa con AWS SDK y .NET
- API S3 compatible con herramientas del ecosistema
- Versionado, replicación y lifecycle policies nativas

### Negativas (Riesgos y Mitigaciones)

- **Lock-in AWS:** mitigado con interfaces desacopladas y API S3 estándar (compatible MinIO/Wasabi)
- **Costos variables:** mitigados con políticas de lifecycle y monitoreo mensual
- **Egress fees:** mitigados con uso de CloudFront CDN para contenido público

---

## 📚 REFERENCIAS

- [AWS S3](https://aws.amazon.com/s3/)
- [MinIO](https://min.io/)
- [Azure Blob Storage](https://azure.microsoft.com/en-us/services/storage/blobs/)
- [Google Cloud Storage](https://cloud.google.com/storage/)
- [Wasabi](https://wasabi.com/)
- [Digital Ocean Spaces](https://www.digitalocean.com/products/spaces)

---

**Decisión tomada por:** Equipo de Arquitectura
**Fecha:** Agosto 2025
**Próxima revisión:** Agosto 2026
