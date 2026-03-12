---
id: gestion-vulnerabilidades
sidebar_position: 8
title: Gestión de Vulnerabilidades
description: Identificación, priorización y remediación de vulnerabilidades de seguridad
---

# Gestión de Vulnerabilidades

Los sistemas deben mantener una gestión proactiva y continua de vulnerabilidades en todas sus capas: dependencias, imágenes de contenedores, sistemas operativos e infraestructura cloud. Dependencias desactualizadas, componentes con CVEs críticos y ausencia de scanning automatizado exponen sistemas a ataques que explotan vulnerabilidades conocidas — muchas con parche disponible. Implementar scanning continuo, patch management automatizado y SLAs de remediación por severidad reduce la superficie de ataque, cierra ventanas de exposición y mantiene una postura de seguridad verificable y auditable.

**Este lineamiento aplica a:** código fuente, dependencias de aplicaciones, imágenes de contenedores, sistemas operativos, infraestructura cloud y APIs de terceros.

## Prácticas Obligatorias

- [Escanear imágenes de contenedores](../../estandares/seguridad/security-scanning.md#1-container-scanning)
- [Gestionar dependencias con Package Manager](../../estandares/desarrollo/package-management.md)
- [Mantener inventario de componentes (SBOM)](../../estandares/seguridad/security-scanning.md#4-sbom-software-bill-of-materials)
- [Definir SLA de remediación por severidad](../../estandares/testing/security-testing.md#4-vulnerability-sla)
- [Implementar patch management](../../estandares/seguridad/security-governance.md#5-patch-management)
- [Realizar pentesting periódico](../../estandares/testing/security-testing.md#2-penetration-testing)
- [Mantener registro de vulnerabilidades](../../estandares/testing/security-testing.md#3-vulnerability-tracking)
