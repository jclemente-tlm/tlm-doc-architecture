---
id: segmentacion-y-aislamiento
sidebar_position: 6
title: Segmentación y Aislamiento
description: Separación de componentes y recursos por niveles de confianza
---

# Segmentación y Aislamiento

Las arquitecturas de red plana permiten que compromisos localizados se propaguen lateralmente por toda la infraestructura, exponiendo sistemas críticos y datos sensibles. La ausencia de segmentación elimina barreras de contención que limitan el radio de impacto de incidentes de seguridad. Implementar segmentación por niveles de confianza, aislar entornos y tenants, y aplicar controles granulares de tráfico crea zonas de seguridad defensibles que contienen brechas, protegen activos críticos y permiten estrategias zero trust efectivas.

**Este lineamiento aplica a:** Segmentación de redes y subredes, aislamiento de tenants multi-tenant, separación de entornos (dev/qa/prod), contenedores y orquestación, bases de datos y almacenamiento.

## Estándares Obligatorios

- [Segmentar redes por trust zones](../../estandares/seguridad/network-segmentation.md)
- [Aislar entornos en cuentas separadas](../../estandares/seguridad/environment-isolation.md)
- [Implementar aislamiento de tenants](../../estandares/seguridad/tenant-isolation.md)
- [Usar redes virtuales aisladas](../../estandares/infraestructura/virtual-networks.md)
- [Configurar grupos de seguridad y listas de control](../../estandares/seguridad/network-access-controls.md)
- [Implementar políticas de red en orquestación](../../estandares/seguridad/orchestration-network-policies.md)
