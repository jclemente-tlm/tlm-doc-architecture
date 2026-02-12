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
- **Wasabi** (administrado, muy bajo costo, S3 compatible, sin egress fees)
- **Backblaze B2** (low-cost, S3-compatible, sin egress fees primeros 3x storage)
- **MinIO** (auto-hosteado, open source, 100% S3 compatible, portable a cualquier infraestructura)

## 🔍 COMPARATIVA DE ALTERNATIVAS

### Comparativa Cualitativa

| Criterio                | AWS S3                   | Wasabi                        | Backblaze B2                | Azure Blob          | GCS                 | MinIO                   |
| ----------------------- | ------------------------ | ----------------------------- | --------------------------- | ------------------- | ------------------- | ----------------------- |
| **Agnosticidad**        | ❌ Lock-in AWS           | ✅ S3 compatible, multi-cloud | ✅ S3-compatible            | ❌ Lock-in Azure    | ❌ Lock-in GCP      | ✅ OSS, multi-cloud     |
| **API S3**              | ✅ 100% nativa           | ✅ 100% compatible            | ✅ 100% compatible          | ⚠️ Parcial          | ⚠️ Parcial          | ✅ 100% compatible      |
| **Operación**           | ✅ Gestionada            | ✅ Gestionada                 | ✅ Gestionada               | ✅ Gestionada       | ✅ Gestionada       | ⚠️ Self-hosted          |
| **Escalabilidad**       | ✅ Ilimitada             | ✅ Ilimitada                  | ✅ Ilimitada                | ✅ Ilimitada        | ✅ Ilimitada        | ✅ Horizontal           |
| **Seguridad**           | ✅ Enterprise grade      | ✅ Encriptación, IAM          | ✅ Encriptación, 2FA        | ✅ Enterprise grade | ✅ Enterprise grade | ✅ IAM, encriptación    |
| **Ecosistema .NET**     | ✅ AWS SDK nativo        | ✅ AWS SDK compatible         | ✅ AWS SDK compatible       | ✅ Azure SDK nativo | ✅ Google SDK       | ✅ AWS SDK compatible   |
| **Alta disponibilidad** | ✅ 99.99% SLA (Multi-AZ) | ✅ 11 nines durability        | ✅ 99.9% uptime             | ✅ Geo-redundante   | ✅ Multi-regional   | ⚠️ Manual (HA setup)    |
| **Costos**              | ⚠️ Pago por uso          | ✅ Bajo, sin egress fees      | ✅ Muy bajo, egress 3x free | ⚠️ Pago por uso     | ⚠️ Pago por uso     | ✅ Solo infraestructura |

**Leyenda:** ✅ Cumple completamente | ⚠️ Cumple parcialmente | ❌ No cumple

## ✔️ DECISIÓN

Se selecciona **AWS S3** como solución estándar de almacenamiento de objetos para todos los servicios y microservicios corporativos.

## Justificación

- Operación gestionada, sin infraestructura propia
- Escalabilidad y durabilidad garantizadas
- Integración nativa con AWS y .NET
- Costos bajos y pago por uso
- Compatibilidad total con API S3 y herramientas del ecosistema
- Observabilidad y monitoreo integrados

## Alternativas descartadas

- **Wasabi:** bajo costo (US$5.99/TB vs S3 US$23/TB) pero integración AWS menos madura, egress gratis requiere ratio 1:1 storage/transfer, menor ecosistema herramientas vs S3, vendor más pequeño (riesgo estabilidad)
- **Backblaze B2:** muy bajo costo (US$5/TB storage), egress gratis primeros 3x storage, pero integración AWS limitada, menor performance vs S3 (no CloudFront nativo), ecosistema reducido
- **MinIO:** portabilidad máxima pero mayor complejidad operativa (clustering, HA, backups, monitoreo), costos infraestructura ocultos, overhead vs solución gestionada, requiere expertise DevOps
- **Azure Blob Storage:** lock-in Azure, infraestructura AWS ya establecida (ADR-003, ADR-005, ADR-007), API no 100% S3-compatible (migración código)
- **Google Cloud Storage:** lock-in GCP, menor integración ecosistema AWS, API no 100% S3-compatible

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

---

**Decisión tomada por:** Equipo de Arquitectura
**Fecha:** Agosto 2025
**Próxima revisión:** Agosto 2026
