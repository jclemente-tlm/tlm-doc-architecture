---
sidebar_position: 9
title: Decisiones de Arquitectura
description: Decisiones arquitectónicas relevantes del API Gateway con Kong OSS.
---

# 9. Decisiones de Arquitectura

## Decisión Principal

| ADR     | Decisión                              | Estado                | Referencia                                           |
| ------- | ------------------------------------- | --------------------- | ---------------------------------------------------- |
| ADR-010 | Kong OSS como API Gateway corporativo | Aceptado (Enero 2026) | [ADR-010](../../../adrs/adr-010-kong-api-gateway.md) |

Ver el ADR completo para la comparativa de alternativas (Kong + Keycloak vs AWS API Gateway + Cognito, Apigee, Azure APIM, Tyk).

## Decisiones Locales al API Gateway

### DEC-01: Patrón de Ruteo Basado en Sistemas (`/api/{sistema}`)

- **Estado**: Aceptado (Diciembre 2025)
- **Contexto**: Se necesita un patrón de rutas escalable para múltiples sistemas de negocio (Sisbon, Gestal, BRS, etc.) sin colisiones de nombres.
- **Decisión**: Patrón `/api/{sistema}/{módulo}/{recurso}` — cada sistema tiene su namespace como prefijo de ruta.
- **Consecuencias**: Kong necesita una sola ruta por sistema. Namespace claro en logs y métricas. URLs más largas, mitigado por la claridad que aportan.

### DEC-02: Multi-tenancy por Tenant (Consumer por Tenant)

- **Estado**: Aceptado (Diciembre 2025)
- **Contexto**: Talma opera en múltiples países/tenants con políticas de identidad independientes.
- **Decisión**: Un tenant (realm) por ámbito de negocio, con nomenclatura `tlm-{scope}`; un Kong Consumer por tenant con clave pública RSA embebida. El claim `iss` del JWT discrimina el tenant.
- **Consecuencias**: Aislamiento criptográfico real. Agregar un tenant = crear realm + consumer + `make sync`. Al rotar claves en Keycloak se debe actualizar `_consumers.yaml` manualmente.

### DEC-03: Clave Pública JWT Embebida (sin JWKS dinámico)

- **Estado**: Aceptado (Diciembre 2025)
- **Contexto**: Kong puede validar JWT vía JWKS URI (dinámico) o con clave pública embebida (estático).
- **Decisión**: Clave pública RSA embebida en `_consumers.yaml` bajo `jwt_secrets[].rsa_public_key`.
- **Consecuencias**: Validación completamente offline, sin latencia de red. Al rotar claves en Keycloak, hay un período donde los tokens nuevos son inválidos hasta que se actualice `_consumers.yaml` y se ejecute `make sync-{env}`.

### DEC-04: Configuración Declarativa con decK por Directorio de Entorno

- **Estado**: Aceptado (Diciembre 2025)
- **Contexto**: Kong puede gestionarse vía Admin API imperativa o vía `decK` (declarativo/GitOps).
- **Decisión**: Toda la configuración en `config/kong/{local,nonprod,prod}/*.yaml`; `decK` lee todos los `*.yaml` del directorio. `make sync-{env}` aplica los cambios.
- **Consecuencias**: Estado real de Kong siempre coincide con el repositorio. Entornos reproducibles. El bootstrapping inicial se hace automáticamente via `kong-deck-bootstrap`.

### DEC-05: Autorización Coarse-Grained en Gateway (Plugin `acl`)

- **Estado**: Aceptado (Diciembre 2025)
- **Contexto**: ¿Dónde implementar la autorización? ¿En Kong o en el backend?
- **Decisión**: Kong implementa ACL por sistema (grupo `sisbon-users`, `talenthub-users`). El backend implementa autorización fine-grained por recurso.
- **Consecuencias**: El backend no recibe requests de sistemas no autorizados. Claro contrato: gateway = autenticación + ACL; backend = reglas de negocio.

### DEC-06: `retries: 0` para Operaciones POST No-Idempotentes

- **Estado**: Aceptado (Diciembre 2025)
- **Contexto**: Kong reintenta requests fallidos por defecto. Los endpoints de Sisbon son POST no-idempotentes (crean bonificaciones).
- **Decisión**: `retries: 0` en todos los servicios para evitar duplicación de operaciones.
- **Consecuencias**: Sin reintentos automáticos. La resiliencia ante fallos transitorios recae en el cliente.

### DEC-07: `request-size-limiting` Uniforme de 1 MB

- **Estado**: Aceptado (Diciembre 2025)
- **Contexto**: Sin límite de tamaño, un payload grande puede consumir recursos de Kong y el backend.
- **Decisión**: `allowed_payload_size: 1` MB en todos los servicios, sin excepciones por defecto.
- **Consecuencias**: Protección uniforme. Aumentar solo si un servicio justifica payloads mayores (archivos/lotes).

### DEC-08: Rate Limiting con `policy: local` (Redis pendiente)

- **Estado**: Aceptado provisionalmente (DT-06 pendiente)
- **Contexto**: Kong ofrece rate limiting local (por instancia) o distribuido (Redis). Con múltiples instancias, el conteo local es inconsistente.
- **Decisión**: `policy: local` como solución inicial. Redis (ElastiCache) es la solución objetivo.
- **Consecuencias**: Con una sola instancia Kong, el comportamiento es correcto. Con múltiples instancias, el límite efectivo se multiplica por el número de instancias.
