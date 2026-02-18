---
id: proteccion-de-datos
sidebar_position: 7
title: Protección de Datos
description: Protección de datos sensibles a lo largo de su ciclo de vida
---

# Protección de Datos

La exposición de datos sensibles genera incidentes de seguridad, incumplimientos regulatorios y pérdida de confianza que afectan continuidad del negocio. Datos sin clasificar, transmitidos sin cifrar, almacenados en claro o filtrados en logs representan vectores de fuga críticos. Implementar clasificación de datos, cifrado end-to-end, gestión segura de claves, enmascaramiento y políticas de minimización protege información sensible en todo su ciclo de vida, desde creación hasta eliminación, garantizando cumplimiento normativo y resiliencia ante amenazas.

**Este lineamiento aplica a:** Datos personales (PII), datos financieros y de pago, datos de salud (PHI), secretos y credenciales, y datos confidenciales de negocio.

## Estándares Obligatorios

- [Clasificar datos por sensibilidad](../../estandares/seguridad/data-classification.md)
- [Cifrar datos en tránsito (TLS 1.2+)](../../estandares/seguridad/encryption-in-transit.md)
- [Cifrar datos en reposo](../../estandares/seguridad/encryption-at-rest.md)
- [Gestionar claves con AWS KMS](../../estandares/seguridad/key-management.md)
- [Aplicar enmascaramiento y tokenización](../../estandares/seguridad/data-masking.md)
- [Implementar data loss prevention (DLP)](../../estandares/seguridad/dlp.md)
- [Aplicar minimización de datos](../../estandares/seguridad/data-minimization.md)
- [Definir políticas de retención](../../estandares/seguridad/data-retention.md)
- [No loguear datos sensibles](../../estandares/seguridad/sensitive-data-logging.md)
