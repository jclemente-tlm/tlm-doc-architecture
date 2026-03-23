---
sidebar_position: 1
title: Introducción y Objetivos
description: Objetivos, requisitos y partes interesadas del API Gateway corporativo basado en Kong OSS.
---

# 1. Introducción y Objetivos

El **API Gateway corporativo** es el punto de entrada unificado y seguro para todos los sistemas de negocio y servicios de Talma.
Está implementado con **Kong Gateway**, desplegado como contenedores Docker gestionados mediante `docker-compose` con configuración declarativa vía `decK` ([ADR-010](../../../adrs/adr-010-kong-api-gateway.md)).

## Objetivos Principales

| Objetivo                        | Descripción                                                                                               |
| ------------------------------- | --------------------------------------------------------------------------------------------------------- |
| Enrutamiento centralizado       | Un único punto de entrada para sistemas de negocio: Sisbon, Gestal, TalentHub ATS y futuros sistemas      |
| Autenticación y autorización    | Validación de JWT (RS256) emitidos por Keycloak; autorización coarse-grained vía plugin `acl` por sistema |
| Rate limiting                   | Control de tráfico por consumer (tenant) mediante el plugin `rate-limiting`                               |
| Observabilidad                  | Métricas con plugin `prometheus` → Grafana/Mimir; correlación de requests con `correlation-id`            |
| Multi-tenancy                   | Un tenant (realm) por scope (`tlm-{scope}`); un Kong Consumer por tenant con ACL groups por sistema       |
| Agnosticidad tecnológica        | Kong no impone stack tecnológico en los servicios backend                                                 |
| Separación de responsabilidades | Autenticación en el gateway; autorización de negocio en el backend                                        |

## Sistemas Integrados

| Sistema             | Tipo    | Backend                                          | Tenants            |
| ------------------- | ------- | ------------------------------------------------ | ------------------ |
| **Sisbon**          | Interno | `nlb-services-ecs-*.elb.us-east-1.amazonaws.com` | `tlm-mx`, `tlm-pe` |
| **Gestal / ATS**    | Externo | `api-uat.talenthub.pe` / `api.talenthub.pe`      | `tlm-pe`           |
| **BRS** _(roadmap)_ | Interno | Por definir                                      | Por definir        |

## Ambientes

| Ambiente | Dominio público        | Patrón de ruta       |
| -------- | ---------------------- | -------------------- |
| PROD     | `api.talma.com.pe`     | `/api/{sistema}`     |
| QA       | `api-qa.talma.com.pe`  | `/api-qa/{sistema}`  |
| DEV      | `api-dev.talma.com.pe` | `/api-dev/{sistema}` |
| Local    | `localhost:8000`       | `/api-dev/{sistema}` |

## Requisitos de Calidad

| Atributo             | Objetivo                     | Crítico        |
| -------------------- | ---------------------------- | -------------- |
| Latencia p95         | `< 10ms` overhead de gateway | `< 20ms`       |
| Throughput           | `> 10,000 RPS`               | `> 5,000 RPS`  |
| Disponibilidad       | `99.9%`                      | `99.5%`        |
| Tiempo de despliegue | `< 5 minutos` (deck sync)    | `< 15 minutos` |

## Partes Interesadas

| Rol                    | Interés                                                   |
| ---------------------- | --------------------------------------------------------- |
| Equipo de Plataforma   | Operación, despliegue y monitoreo de Kong                 |
| Equipo de Arquitectura | Definición de estándares, plugins y topología             |
| Equipos de Desarrollo  | Registro de servicios y rutas; consumo de APIs            |
| Equipo de Seguridad    | Configuración de autenticación, TLS y políticas de acceso |

## Decisión de Tecnología

Kong OSS fue seleccionado en [ADR-010](../../../adrs/adr-010-kong-api-gateway.md). Las decisiones específicas del repositorio se detallan en la sección [9. Decisiones de Arquitectura](./09-decisiones-arquitectura.md).
