---
id: proteccion-de-datos
sidebar_position: 4
title: Protección de Datos
description: Protección de datos sensibles a lo largo de su ciclo de vida
---

# Protección de Datos

La exposición de datos sensibles genera incidentes de seguridad, incumplimientos regulatorios y pérdida de confianza que afectan continuidad del negocio. Datos sin clasificar, transmitidos sin cifrar, almacenados en claro o filtrados en logs representan vectores de fuga críticos. Implementar clasificación de datos, cifrado end-to-end, gestión segura de claves, enmascaramiento y políticas de minimización protege información sensible en todo su ciclo de vida, desde creación hasta eliminación, garantizando cumplimiento normativo y resiliencia ante amenazas.

**Este lineamiento aplica a:** Datos personales (PII), datos financieros y de pago, datos de salud (PHI), secretos y credenciales, y datos confidenciales de negocio.

## Estándares Obligatorios

- [Clasificar datos según sensibilidad (público, interno, sensible, regulado)](../../estandares/seguridad/data-classification.md)
- [Cifrar datos sensibles en tránsito y reposo](../../estandares/seguridad/data-encryption.md)
- [Aplicar enmascaramiento y tokenización donde corresponda](../../estandares/seguridad/data-masking.md)
- [Gestionar claves de cifrado con servicios dedicados (KMS)](../../estandares/seguridad/key-management.md)
- [Recopilar únicamente datos estrictamente necesarios (minimización)](../../estandares/seguridad/data-minimization.md)
- [Implementar políticas de retención y eliminación automática](../../estandares/seguridad/data-retention.md)
