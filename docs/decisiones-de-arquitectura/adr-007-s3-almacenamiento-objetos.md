---
title: "ADR-007: S3 Almacenamiento Objetos"
sidebar_position: 7
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

| Criterio                         | AWS S3                                               | Digital Ocean Spaces                         | Azure Blob Storage                             | Google Cloud Storage                          | MinIO                                  |
| -------------------------------- | ---------------------------------------------------- | -------------------------------------------- | ---------------------------------------------- | --------------------------------------------- | -------------------------------------- |
| **Agnosticidad**                 | ⚠️ Lock-in AWS (API S3 estándar)                     | ✅ S3-compatible                             | ⚠️ Lock-in Azure                               | ⚠️ Lock-in GCP                                | ✅ OSS, multi-cloud                    |
| **Madurez**                      | ✅ Muy alta (2006, AWS pioneer)                      | ⚠️ Media (2017, CDN-focused)                 | ✅ Muy alta (2010, Azure Storage)              | ✅ Muy alta (2010, GCP storage)               | ✅ Alta (2015, CNCF)                   |
| **Adopción**                     | ✅ Muy alta (estándar de facto)                      | ⚠️ Limitada (CDN niche)                      | ✅ Muy alta (Azure enterprise)                 | ✅ Muy alta (GCP enterprise)                  | ⚠️ Alta (60K⭐, repo archivado 2024)   |
| **Modelo de gestión**            | ✅ Gestionado (AWS)                                  | ✅ Gestionado (SaaS)                         | ✅ Gestionado (Azure)                          | ✅ Gestionado (GCP)                           | ⚠️ Self-hosted                         |
| **Complejidad operativa**        | ✅ Baja (0.25 FTE, `<5h/sem)`                          | ✅ Baja (0.25 FTE, `<5h/sem)`                  | ✅ Baja (0.25 FTE, `<5h/sem)`                    | ✅ Baja (0.25 FTE, `<5h/sem)`                   | ⚠️ Alta (1 FTE, 10-20h/sem)            |
| **Seguridad**                    | ✅ Enterprise grade                                  | ✅ Encriptación, CDN                         | ✅ Enterprise grade                            | ✅ Enterprise grade                           | ✅ IAM, encriptación                   |
| **Integración .NET**             | ✅ AWSSDK.S3 (15M+ DL/mes, .NET 6+, async)           | ✅ AWSSDK.S3 compatible (S3 API)             | ✅ Azure.Storage.Blobs (10M+ DL/mes, .NET 6+)  | ✅ Google.Cloud.Storage (3M+ DL/mes, .NET 6+) | ✅ Minio (500K+ DL/mes, S3 compatible) |
| **Multi-tenancy**                | ✅ Buckets + IAM políticas                           | ⚠️ Spaces + CORS                             | ✅ Containers + RBAC                           | ✅ Buckets + IAM                              | ✅ Buckets + policies                  |
| **Escalabilidad**                | ✅ Hasta exabyte-scale, 100T+ objetos (AWS)          | ⚠️ Hasta 250TB máx (límites empresa)         | ✅ Hasta petabyte-scale (Microsoft enterprise) | ✅ Hasta exabyte-scale (Google Cloud)         | ✅ Hasta multi-PB (MinIO production)   |
| **Rendimiento**                  | ✅ `<100ms `p50, CDN global                            | ✅ CDN integrado                             | ✅ `<100ms `Geo-replicación                      | ✅ `<100ms `Multi-regional                      | ⚠️ Depende config                      |
| **Alta disponibilidad**          | ✅ 99.99% SLA Multi-AZ                               | ✅ 99.95% SLA                                | ✅ 99.9% SLA Geo-redundante                    | ✅ 99.95% SLA Multi-regional                  | ⚠️ Sin SLA (manual HA)                 |
| **Integración AWS**              | ✅ Nativa (ECS, IAM, VPC)                            | ❌ Externa                                   | ❌ Externa                                     | ❌ Externa                                    | ❌ Externa                             |
| **API S3**                       | ✅ 100% nativa                                       | ✅ 100% compatible                           | ⚠️ Parcial                                     | ⚠️ Parcial                                    | ✅ 100% compatible                     |
| **Versionado**                   | ✅ Nativo (inmutable)                                | ⚠️ Limitado                                  | ✅ Nativo                                      | ✅ Nativo                                     | ✅ Nativo                              |
| **Clases de almacenamiento**     | ✅ Standard, IA, Glacier, Deep Archive               | ⚠️ Solo Standard                             | ✅ Hot, Cool, Archive tiers                    | ✅ Standard, Nearline, Coldline, Archive      | ⚠️ Solo Standard                       |
| **Políticas de ciclo de vida**   | ✅ Transitions + Expiration automáticas              | ❌ No soportado                              | ✅ Políticas completas                         | ✅ Políticas completas                        | ⚠️ Básico (expiration)                 |
| **Replicación**                  | ✅ Cross-region + Same-region async                  | ❌ No soportado                              | ✅ Geo-replication                             | ✅ Multi-region replication                   | ⚠️ Manual (rsync/rclone)               |
| **Aceleración de transferencia** | ✅ S3 Transfer Acceleration (CloudFront edge)        | ❌ No soportado                              | ⚠️ Custom CDN integration                      | ⚠️ Google Cloud CDN                           | ❌ No soportado                        |
| **Notificaciones de eventos**    | ✅ S3 Events (Lambda, SQS, SNS, EventBridge)         | ❌ No soportado                              | ✅ Event Grid integration                      | ✅ Cloud Functions triggers                   | ⚠️ Webhook notifications (básico)      |
| **Bloqueo de objetos**           | ✅ S3 Object Lock (WORM, legal hold, retention)      | ❌ No soportado                              | ✅ Immutable storage with legal hold           | ✅ Bucket Lock + retention policies           | ✅ Object locking (WORM mode)          |
| **Certificaciones**              | ✅ SOC2, HIPAA, PCI-DSS, ISO                         | ⚠️ SOC2                                      | ✅ Completo                                    | ✅ Completo                                   | ❌ Self-managed                        |
| **Costos**                       | ⚠️ $0.023/GB storage + $0.09/GB egress (~$25-50/mes) | ✅ $0.005/GB + $0.01/GB egress (~$6/mes 1TB) | ⚠️ $0.018/GB + $0.087/GB egress (~$20-45/mes)  | ⚠️ $0.020/GB + $0.12/GB egress (~$25-55/mes)  | ✅ $0 licencia + ~$200-400/mes infra   |

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
