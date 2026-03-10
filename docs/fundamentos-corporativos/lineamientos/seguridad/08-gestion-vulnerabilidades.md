---
id: gestion-vulnerabilidades
sidebar_position: 8
title: Gestión de Vulnerabilidades
description: Identificación, priorización y remediación de vulnerabilidades de seguridad
---

# Gestión de Vulnerabilidades

El 60% de brechas de seguridad explotan vulnerabilidades conocidas sin parchear según Verizon DBIR. Dependencias desactualizadas, componentes con CVEs críticos y ausencia de scanning automatizado exponen sistemas a ataques prevenibles. Gestión proactiva con scanning continuo, patch management automatizado y actualización de dependencias reduce superficie de ataque y mejora postura de seguridad significativamente.

**Este lineamiento aplica a:** código fuente, dependencias de aplicaciones, imágenes de contenedores, sistemas operativos, infraestructura cloud y APIs de terceros.

## Estándares Obligatorios

- [Escanear imágenes de contenedores](../../estandares/seguridad/security-scanning.md#1-container-scanning)
- [Gestionar dependencias con Package Manager](../../estandares/desarrollo/package-management.md)
- [Mantener inventario de componentes (SBOM)](../../estandares/seguridad/security-scanning.md#4-sbom-software-bill-of-materials)
- [Definir SLA de remediación por severidad](../../estandares/testing/security-testing.md#4-vulnerability-sla)
- [Implementar patch management](../../estandares/seguridad/security-governance.md#5-patch-management)
- [Realizar pentesting periódico](../../estandares/testing/security-testing.md#2-penetration-testing)
- [Mantener registro de vulnerabilidades](../../estandares/testing/security-testing.md#3-vulnerability-tracking)
