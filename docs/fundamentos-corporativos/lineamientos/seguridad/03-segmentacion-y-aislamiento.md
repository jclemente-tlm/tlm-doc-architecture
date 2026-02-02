---
id: segmentacion-y-aislamiento
sidebar_position: 3
title: Segmentación y Aislamiento
description: Separación de componentes y recursos por niveles de confianza
---

# Segmentación y Aislamiento

Las arquitecturas de red plana permiten que compromisos localizados se propaguen lateralmente por toda la infraestructura, exponiendo sistemas críticos y datos sensibles. La ausencia de segmentación elimina barreras de contención que limitan el radio de impacto de incidentes de seguridad. Implementar segmentación por niveles de confianza, aislar entornos y tenants, y aplicar controles granulares de tráfico crea zonas de seguridad defensibles que contienen brechas, protegen activos críticos y permiten estrategias zero trust efectivas.

**Este lineamiento aplica a:** Segmentación de redes y subredes, aislamiento de tenants multi-tenant, separación de entornos (dev/qa/prod), contenedores y orquestación, bases de datos y almacenamiento.

## Prácticas Recomendadas

- [Segmentar redes por niveles de confianza (DMZ, interna, datos)](../../estandares/seguridad/segmentacion-redes.md)
- [Aislar recursos por entorno en cuentas/subscripciones separadas](../../estandares/seguridad/separacion-entornos.md)
- [Implementar aislamiento de tenants en soluciones multi-tenant](../../estandares/seguridad/aislamiento-tenants.md)
- [Aplicar principio de menor exposición de red (zero trust networking)](../../estandares/seguridad/zero-trust-network.md)
- [Documentar zonas de seguridad y controles entre ellas](../../estandares/seguridad/zonas-seguridad.md)
