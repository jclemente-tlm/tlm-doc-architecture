---
id: multi-tenancy
sidebar_position: 11
title: Multi-tenancy
description: Estrategias de aislamiento y configuración independiente para arquitecturas multipaís y multi-cliente
---

# Multi-tenancy

Los servicios que operan en múltiples países o para múltiples clientes deben declarar explícitamente su modelo de aislamiento de tenant y aplicarlo de forma consistente en todas las capas. Sin esta definición, los sistemas exponen datos entre tenants, las regulaciones locales no pueden cumplirse por jurisdicción y los cambios en un tenant impactan a otros sin control. Adoptar una estrategia deliberada — seleccionar el modelo correcto (realm, schema, base de datos, instancia), propagar el contexto y auditar por tenant — garantiza aislamiento de datos, cumplimiento normativo independiente por país y capacidad de evolucionar cada tenant de forma autónoma.

**Este lineamiento aplica a:** servicios con múltiples clientes o países (Perú, Ecuador, Colombia, México), plataformas de autenticación (Keycloak realms), API Gateways con workspaces por tenant (Kong), bases de datos con esquemas separados y configuración de servicios por jurisdicción.

## Prácticas Obligatorias

- [Seleccionar modelo de aislamiento explícito por servicio (realm / schema / instancia)](../../estandares/arquitectura/multi-tenancy.md#modelos-de-aislamiento)
- [Propagar contexto de tenant en todas las capas (header, claim JWT, parámetro)](../../estandares/arquitectura/multi-tenancy.md#tenant-context-propagation)
- [Prohibir row-level sin RLS en datos personales o financieros](../../estandares/arquitectura/multi-tenancy.md#modelos-de-aislamiento)
- [Versionar configuración por tenant en IaC (terraform.tfvars por tenant)](../../estandares/arquitectura/multi-tenancy.md#per-tenant-configuration)
- [Validar claims de tenant en el API Gateway antes de enrutar](../../estandares/arquitectura/multi-tenancy.md#validación-en-api-gateway)
- [Implementar auditoría con tenant_id como campo indexado](../../estandares/arquitectura/multi-tenancy.md#auditoría-por-tenant)

## Referencias Relacionadas

- [Identidad y Accesos](../seguridad/identidad-y-accesos.md)
- [Segmentación y Aislamiento](../seguridad/segmentacion-y-aislamiento.md)
- [Autonomía de Servicios](./autonomia-de-servicios.md)
- [Datos por Dominio](../datos/datos-por-dominio.md)
