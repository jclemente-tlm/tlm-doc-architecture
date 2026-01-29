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
- **MinIO** (auto-hosteado, open source, 100% S3 compatible, portable a cualquier infraestructura)

## 🔍 COMPARATIVA DE ALTERNATIVAS

### Comparativa Cualitativa

| Criterio              | AWS S3 | Wasabi | Azure Blob | GCS | MinIO |
|----------------------|--------|--------|------------|-----|-------|
| **Agnosticidad**     | ❌ Lock-in AWS | ✅ S3 compatible, multi-cloud | ❌ Lock-in Azure | ❌ Lock-in GCP | ✅ OSS, multi-cloud |
| **API S3**           | ✅ Nativa | ✅ 100% compatible | 🟡 Parcial | 🟡 Parcial | ✅ 100% compatible |
| **Operación**        | ✅ Gestionada | ✅ Gestionada | ✅ Gestionada | ✅ Gestionada | 🟡 Self-hosted |
| **Escalabilidad**    | ✅ Ilimitada | ✅ Ilimitada | ✅ Ilimitada | ✅ Ilimitada | ✅ Horizontal |
| **Seguridad**        | ✅ Enterprise grade | ✅ Encriptación, IAM | ✅ Enterprise grade | ✅ Enterprise grade | ✅ IAM, encriptación |
| **Ecosistema .NET**  | ✅ AWS SDK nativo | ✅ AWS SDK compatible | ✅ Azure SDK nativo | ✅ Google SDK | ✅ AWS SDK compatible |
| **Costos**           | 🟡 Pago por uso | ✅ Bajo costo, sin egress fees | 🟡 Pago por uso | 🟡 Pago por uso | ✅ Solo infraestructura |

### Matriz de Decisión

| Solución         | Agnosticidad | API S3 | Operación | Escalabilidad | Recomendación         |
|------------------|--------------|--------|-----------|---------------|-----------------------|
| **AWS S3**       | Mala         | Nativa | Gestionada| Ilimitada     | ✅ **Seleccionada**    |
| **Wasabi**       | Excelente    | Excelente | Gestionada | Excelente   | 🟡 Alternativa         |
| **Azure Blob**   | Mala         | Parcial | Gestionada| Ilimitada     | 🟡 Considerada         |
| **GCS**          | Mala         | Parcial | Gestionada| Ilimitada     | ❌ Descartada          |
| **MinIO**        | Excelente    | Excelente | Self-hosted | Excelente   | 🟡 Alternativa         |

## 💰 ANÁLISIS DE COSTOS (TCO 3 años)

> **Metodología y supuestos:** Se asume un uso promedio de 10TB storage, 1TB transferencia/mes, 4 regiones. El TCO (Total Cost of Ownership) se calcula para un horizonte de 3 años, incluyendo costos directos y estimaciones de operación. Los valores pueden variar según volumen y proveedor.

| Solución         | Licenciamiento | Infraestructura | Operación      | TCO 3 años   |
|------------------|---------------|----------------|---------------|--------------|
| AWS S3           | Pago por uso  | US$0           | US$0          | US$10,800/año |
| MinIO            | OSS           | US$14,400/año  | US$36,000/año | US$151,200   |
| Azure Blob       | Pago por uso  | US$0           | US$0          | US$11,520/año |
| GCS              | Pago por uso  | US$0           | US$0          | US$10,440/año |
| Wasabi            | OSS           | US$5,400/año  | US$13,500/año | US$54,600   |

---

## Consideraciones técnicas y riesgos

### Límites clave

- **AWS S3:** ilimitado, gestión automática de escalabilidad y durabilidad
- **MinIO:** depende de infraestructura propia, requiere operación
- **Azure Blob/GCS:** límites por cuenta y región, lock-in cloud
- **Wasabi:** límites por cuenta, requiere evaluación de costos

### Riesgos y mitigación

- **Lock-in cloud:** mitigado con interfaces y adaptadores desacoplados
- **Complejidad operativa MinIO:** mitigada con automatización y monitoreo
- **Costos variables cloud:** monitoreo y revisión anual

---

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

- **MinIO:** mayor complejidad operativa y costos de infraestructura
- **Azure Blob Storage:** lock-in Azure, menor portabilidad
- **Google Cloud Storage:** lock-in GCP, menor portabilidad
- **Wasabi:** aunque es una alternativa viable, se prefiere una solución con mayor integración nativa como AWS S3

---

## ⚠️ CONSECUENCIAS

- Todos los servicios nuevos deben usar AWS S3 salvo justificación técnica documentada
- Se debe estandarizar la gestión de buckets, políticas y monitoreo
- El equipo debe mantener adaptadores desacoplados para facilitar migración futura

---

## 🏗️ ARQUITECTURA DE DESPLIEGUE

- Buckets segregados por país/tenant
- Versionado y replicación cross-region
- Integración con AWS SDK y librerías .NET
- Monitoreo con CloudWatch y Prometheus

---

## 📊 MÉTRICAS Y MONITOREO

### KPIs Clave

- **Objetos almacenados**: > 99.99% disponibilidad
- **Latencia promedio**: < 100ms
- **Throughput**: > 10K objetos/minuto
- **Errores de acceso**: < 0.01%

### Alertas Críticas

- Latencia > 500ms
- Fallos de replicación
- Errores de integración SDK
- Objetos pendientes de replicar > umbral

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
