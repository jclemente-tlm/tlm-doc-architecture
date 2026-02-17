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

- [Segmentar redes por niveles de confianza (DMZ, interna, datos)](../../estandares/seguridad/network-security.md#segmentación-y-zonas)
- [Aislar recursos por entorno en cuentas/subscripciones separadas](../../estandares/seguridad/network-security.md#5-ejemplo-de-infraestructura)
- [Implementar aislamiento de tenants en soluciones multi-tenant](../../estandares/seguridad/tenant-isolation.md)
- [Aplicar principio de menor exposición de red (zero trust networking)](../../estandares/seguridad/network-security.md#principios-zero-trust)
- [Documentar zonas de seguridad y controles entre ellas](../../estandares/seguridad/network-security.md#segmentación-y-zonas)
