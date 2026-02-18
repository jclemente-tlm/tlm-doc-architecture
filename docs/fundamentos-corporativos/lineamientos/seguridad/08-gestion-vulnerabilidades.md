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

- [Implementar SAST en CI/CD](../../estandares/desarrollo/sast.md)
- [Implementar SCA (dependency scanning)](../../estandares/seguridad/dependency-scanning.md)
- [Escanear imágenes de contenedores](../../estandares/seguridad/container-scanning.md)
- [Escanear código IaC](../../estandares/seguridad/iac-scanning.md)
- [Gestionar dependencias con Package Manager](../../estandares/desarrollo/package-management.md)
- [Mantener inventario de componentes (SBOM)](../../estandares/seguridad/sbom.md)
- [Definir SLA de remediación por severidad](../../estandares/seguridad/vulnerability-sla.md)
- [Implementar patch management](../../estandares/seguridad/patch-management.md)
- [Realizar pentesting periódico](../../estandares/seguridad/penetration-testing.md)
- [Mantener registro de vulnerabilidades](../../estandares/seguridad/vulnerability-tracking.md)
