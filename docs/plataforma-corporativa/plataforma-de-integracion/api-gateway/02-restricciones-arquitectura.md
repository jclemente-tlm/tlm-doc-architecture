---
sidebar_position: 2
title: Restricciones de Arquitectura
description: Limitaciones técnicas y organizativas que aplican al API Gateway con Kong OSS.
---

# 2. Restricciones de Arquitectura

## Restricciones Técnicas

| Restricción                  | Valor                               | Razón                                      |
| ---------------------------- | ----------------------------------- | ------------------------------------------ |
| Tecnología de gateway        | Kong OSS                            | ADR-010, agnosticidad tecnológica          |
| Plataforma de despliegue     | AWS ECS Fargate                     | ADR-003, infraestructura cloud corporativa |
| Configuración                | Declarativa vía `deck` (YAML)       | Trazabilidad, GitOps, reproducibilidad     |
| Base de datos de Kong        | PostgreSQL (RDS)                    | Modo DB para clustering nativo             |
| Identity provider            | Keycloak                            | ADR (Keycloak como IdP corporativo)        |
| Almacenamiento de contadores | Redis (ElastiCache)                 | Rate limiting distribuido entre instancias |
| Red                          | VPC privada, sin exposición directa | ADR-007, segmentación de red               |
| TLS                          | Terminación en ALB; TLS 1.3 mínimo  | Estándar corporativo de seguridad          |
| Protocolos soportados        | HTTP/1.1, HTTP/2, gRPC, WebSocket   | Requisitos de servicios backend            |

## Restricciones Organizativas

| Restricción         | Descripción                                                                            |
| ------------------- | -------------------------------------------------------------------------------------- |
| Propiedad operativa | El equipo de Plataforma es responsable del ciclo de vida de Kong                       |
| Plugins permitidos  | Solo plugins del Kong Hub oficial; plugins custom requieren aprobación de Arquitectura |
| Multi-país          | Soporte obligatorio para Perú, Ecuador, Colombia y México desde el diseño              |
| Secretos            | Nunca en repositorio; se inyectan en ECS vía AWS Secrets Manager                       |

## Restricciones de Proceso

| Restricción              | Descripción                                                                               |
| ------------------------ | ----------------------------------------------------------------------------------------- |
| Gestión de configuración | Cambios exploratorios vía Konga; cambios definitivos en `kong.yml` vía PR + `deck sync`   |
| Cambios de seguridad     | Rutas y plugins de seguridad requieren aprobación del equipo de Seguridad antes del merge |
