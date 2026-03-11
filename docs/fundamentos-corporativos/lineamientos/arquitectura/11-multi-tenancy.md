---
id: multi-tenancy
sidebar_position: 11
title: Multi-tenancy
description: Estrategias de aislamiento y configuración independiente para arquitecturas multipaís y multi-cliente
---

# Multi-tenancy

En contextos multipaís o multi-cliente, la ausencia de aislamiento explícito genera filtraciones de datos entre tenants, configuraciones que se contaminan y dificultad para cumplir regulaciones locales. Definir una estrategia de multi-tenancy deliberada — elegir el modelo correcto (realm, schema, base de datos, instancia) y aplicarlo consistentemente — garantiza aislamiento de datos, cumplimiento normativo por jurisdicción y capacidad de evolucionar cada tenant de forma independiente.

**Este lineamiento aplica a:** servicios con múltiples clientes o países (Perú, Ecuador, Colombia, México), plataformas de autenticación (Keycloak realms), API Gateways con workspaces por tenant (Kong), bases de datos con esquemas separados y configuración de servicios por jurisdicción.

**No aplica a:** servicios con un único cliente o entorno; la estrategia de aislamiento de red (ver [Segmentación y Aislamiento](../../lineamientos/seguridad/06-segmentacion-y-aislamiento.md)).

## Estándares Obligatorios

- [Seleccionar modelo de aislamiento explícito por servicio (realm / schema / instancia)](../../estandares/arquitectura/multi-tenancy.md#modelos-de-aislamiento)
- [Propagar contexto de tenant en todas las capas (header, claim JWT, parámetro)](../../estandares/arquitectura/multi-tenancy.md#tenant-context-propagation)
- [Prohibir acceso entre tenants sin autorización explícita](../../estandares/seguridad/iam-advanced.md)
- [Versionar configuración por tenant en repositorio (IaC)](../../estandares/infraestructura/iac-standards.md)
- [Validar claims de tenant en el API Gateway antes de enrutar](../../estandares/seguridad/sso-mfa-rbac.md)
- [Implementar auditoría con tenant como campo indexado](../../estandares/seguridad/security-governance.md)

## Referencias Relacionadas

- [Identidad y Accesos](../seguridad/05-identidad-y-accesos.md)
- [Segmentación y Aislamiento](../seguridad/06-segmentacion-y-aislamiento.md)
- [Autonomía de Servicios](./07-autonomia-de-servicios.md)
- [Datos por Dominio](../datos/01-datos-por-dominio.md)
