---
title: "Almacenamiento de Objetos"
sidebar_position: 14
---

## ✅ ESTADO

Aceptada – Agosto 2025

---

## 🗺️ CONTEXTO

Los servicios corporativos distribuidos requieren una estrategia de Object Storage que soporte:

- **Multi-cloud portabilidad** sin vendor lock-in entre AWS, Azure, GCP
- **Multi-tenancy** con segregación de datos por país/tenant
- **Escalabilidad masiva** para documentos, imágenes, logs y backups
- **Durabilidad garantizada** con replicación y versionado automático
- **Seguridad avanzada** con encriptación, IAM y compliance
- **API estándar S3** para máxima compatibilidad de herramientas
- **Disaster recovery** con backup cross-region automático
- **Costos optimizados** con lifecycle policies y storage classes
- **Performance consistente** para aplicaciones críticas
- **Integración CI/CD** para artifacts y deployment assets

La intención estratégica es **priorizar agnosticidad vs simplicidad operacional** para Object Storage empresarial.

Las alternativas evaluadas fueron:

- **MinIO** (S3-compatible, open source, self-hosted)
- **AWS S3** (Managed service, AWS nativo)
- **Azure Blob Storage** (Managed service, Azure nativo)
- **Google Cloud Storage** (Managed service, GCP nativo)
- **Ceph** (Distributed storage, open source)
- **OpenStack Swift** (Object storage, open source)

## 🔍 COMPARATIVA DE ALTERNATIVAS

### Comparativa Cualitativa

| Criterio | MinIO | AWS S3 | Azure Blob | GCS | Ceph | Swift |
|----------|-------|--------|------------|-----|------|-------|
| **Agnosticidad** | ✅ Totalmente agnóstico | ❌ Lock-in AWS | ❌ Lock-in Azure | ❌ Lock-in GCP | ✅ Totalmente agnóstico | ✅ Agnóstico |
| **API S3** | ✅ 100% compatible | ✅ API nativa | 🟡 Compatible parcial | 🟡 Compatible parcial | 🟡 Compatible básico | ❌ No compatible |
| **Operación** | 🟡 Self-hosted | ✅ Totalmente gestionado | ✅ Totalmente gestionado | ✅ Totalmente gestionado | 🟡 Compleja gestión | 🟡 Compleja gestión |
| **Escalabilidad** | ✅ Horizontal | ✅ Ilimitada | ✅ Ilimitada | ✅ Ilimitada | ✅ Muy buena | ✅ Buena |
| **Seguridad** | ✅ Encriptación, IAM | ✅ Enterprise grade | ✅ Enterprise grade | ✅ Enterprise grade | 🟡 Básica | 🟡 Básica |
| **Ecosistema .NET** | ✅ AWS SDK compatible | ✅ AWS SDK nativo | ✅ Azure SDK nativo | ✅ Google SDK | 🟡 Clientes terceros | 🟡 Clientes limitados |
| **Costos** | ✅ Solo infraestructura | 🟡 Por GB + requests | 🟡 Por GB + transacciones | 🟡 Por GB + operaciones | ✅ Solo infraestructura | ✅ Solo infraestructura |

### Matriz de Decisión

| Solución | Agnosticidad | API S3 | Operación | Escalabilidad | Recomendación |
|----------|--------------|--------|-----------|---------------|---------------|
| **AWS S3** | Mala | Nativa | Gestionada | Ilimitada | ✅ **Seleccionada** |
| **MinIO** | Excelente | Excelente | Self-hosted | Excelente | 🟡 Alternativa |
| **Azure Blob Storage** | Mala | Parcial | Gestionada | Ilimitada | 🟡 Considerada |
| **Google Cloud Storage** | Mala | Parcial | Gestionada | Ilimitada | ❌ Descartada |
| **Ceph** | Excelente | Básico | Compleja | Muy buena | ❌ Descartada |
| **OpenStack Swift** | Excelente | No compatible | Compleja | Buena | ❌ Descartada |

### Comparativa de costos estimados (2025)

| Solución             | Costo mensual base* | Costos adicionales         | Infra propia |
|----------------------|---------------------|---------------------------|--------------|
| AWS S3               | Pago por uso        | Almacenamiento, transfer. | No           |
| Azure Blob Storage   | Pago por uso        | Almacenamiento, transfer. | No           |
| Google Cloud Storage | Pago por uso        | Almacenamiento, transfer. | No           |
| MinIO                | ~US$30/mes (VM)     | Discos, backup            | Sí           |

*Precios aproximados, sujetos a variación según proveedor y volumen.

---

## ANÁLISIS DE COSTOS (TCO 3 años)

### Escenario Base: 10TB storage, 1TB transfer/mes, 4 regiones

| Solución | Licenciamiento | Infraestructura | Operación | TCO 3 años |
|----------|----------------|-----------------|-----------|------------|
| **MinIO** | US$0 (OSS) | US$14,400/año | US$36,000/año | **US$151,200** |
| **AWS S3** | Pago por uso | US$0 | US$0 | **US$10,800/año** |
| **Azure Blob** | Pago por uso | US$0 | US$0 | **US$11,520/año** |
| **Google Cloud Storage** | Pago por uso | US$0 | US$0 | **US$10,440/año** |
| **Ceph** | US$0 (OSS) | US$18,000/año | US$48,000/año | **US$198,000** |
| **OpenStack Swift** | US$0 (OSS) | US$21,600/año | US$54,000/año | **US$226,800** |

### Escenario Alto Volumen: 500TB storage, 50TB transfer/mes

| Solución | TCO 3 años | Durabilidad | Disponibilidad |
|----------|------------|-------------|----------------|
| **MinIO** | **US$540,000** | 99.999999999% | 99.9% |
| **AWS S3** | **US$540,000** | 99.999999999% | 99.99% |
| **Azure Blob** | **US$576,000** | 99.999999999% | 99.9% |
| **Google Cloud Storage** | **US$522,000** | 99.999999999% | 99.95% |
| **Ceph** | **US$720,000** | 99.9999999% | 99.5% |
| **OpenStack Swift** | **US$864,000** | 99.999999% | 99.0% |

### Factores de Costo Adicionales

```yaml
Consideraciones MinIO:
  Hardware: NVMe SSD vs HDD tradicional (3x costo vs 50% performance)
  Networking: 10Gbps vs 1Gbps (2x costo vs 10x performance)
  Replicación: 3 replicas vs erasure coding (3x storage vs 1.5x)
  Backup: S3 Glacier vs tape backup (US$0.004/GB vs US$0.0012/GB)
  Migración: US$0 entre clouds vs US$0.09/GB egress costs
  Capacitación: US$8K MinIO vs US$3K managed services
  Downtime evitado: US$150K/año vs US$50K/año managed
```

---

## DECISIÓN

Se recomienda desacoplar el almacenamiento de objetos mediante interfaces y adaptadores. Inicialmente se usará **AWS S3** como solución principal, pero la arquitectura soporta migración a MinIO o soluciones cloud equivalentes según necesidades de portabilidad o despliegue híbrido.

## Justificación

- Permite almacenar archivos y datos no estructurados de forma segura y portable.
- Facilita la portabilidad y despliegue multi-cloud.
- El desacoplamiento del backend permite cambiar de tecnología sin impacto en la lógica de negocio.
- **AWS S3** es la opción seleccionada por su operación gestionada, alta disponibilidad y costos competitivos en el contexto actual.
- MinIO es una opción madura y ampliamente soportada para escenarios on-premises o híbridos.

## Limitaciones

- AWS S3, Azure Blob y Google Cloud Storage implican lock-in y costos variables.
- MinIO requiere operación y monitoreo propio.

## Alternativas descartadas

- Azure Blob Storage y Google Cloud Storage: lock-in cloud, menor portabilidad.

---

## ⚠️ CONSECUENCIAS

- El código debe desacoplarse del proveedor concreto mediante interfaces.
- Se facilita la portabilidad y despliegue híbrido.
- Se requiere mantener adaptadores y pruebas para cada backend soportado.

---

## 📚 REFERENCIAS

- [AWS S3](https://aws.amazon.com/s3/)
- [Azure Blob Storage](https://azure.microsoft.com/en-us/services/storage/blobs/)
- [Google Cloud Storage](https://cloud.google.com/storage)
- [MinIO](https://min.io/)
