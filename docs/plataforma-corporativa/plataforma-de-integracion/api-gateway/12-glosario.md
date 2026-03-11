---
sidebar_position: 12
title: Glosario
description: Términos y acrónimos del API Gateway corporativo basado en Kong OSS.
---

# 12. Glosario

## Términos del Dominio

| Término             | Definición                                                                                                                                                                                     |
| ------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **API Gateway**     | Punto de entrada único y centralizado para todas las APIs corporativas. Gestiona autenticación, enrutamiento, rate limiting y observabilidad.                                                  |
| **Kong OSS**        | Solución de API Gateway open source, basada en NGINX + Lua, con un ecosistema extenso de plugins. Seleccionada en ADR-010.                                                                     |
| **deck**            | Herramienta CLI declarativa para gestionar la configuración de Kong vía archivos YAML en GitOps.                                                                                               |
| **Konga**           | Interfaz web open source para administrar Kong visualmente. Se conecta al Admin API (:8001). Los cambios realizados en Konga deben reflejarse en `kong.yml` para mantener trazabilidad GitOps. |
| **Service**         | Entidad Kong que representa un servicio backend (URL o Upstream) al que se enrutan requests.                                                                                                   |
| **Route**           | Regla de enrutamiento en Kong (por host, path o método) que vincula una request a un Service.                                                                                                  |
| **Upstream**        | Pool de targets en Kong con balanceo de carga y health checks activos/pasivos.                                                                                                                 |
| **Target**          | Instancia concreta de un backend (`host:port`) dentro de un Upstream.                                                                                                                          |
| **Plugin**          | Componente Kong que añade comportamiento (auth, rate limiting, logging, etc.) a nivel global, Service o Route.                                                                                 |
| **Consumer**        | Identidad de un cliente/tenant en Kong, usada para aplicar rate limits o autenticación diferenciada.                                                                                           |
| **Workspace**       | Namespace de aislamiento en Kong para separar configuración por tenant o entorno.                                                                                                              |
| **Rate Limiting**   | Control del número máximo de requests por ventana de tiempo, aplicado por consumer, IP o ruta.                                                                                                 |
| **Circuit Breaker** | Mecanismo de exclusión de targets no saludables del pool de balanceo, basado en health checks pasivos.                                                                                         |
| **JWT**             | JSON Web Token; token compacto y firmado para autenticación y autorización entre servicios.                                                                                                    |
| **JWKS**            | JSON Web Key Set; conjunto de claves públicas publicado por Keycloak para verificación de JWT.                                                                                                 |
| **tenant (realm)**  | Contexto de un cliente/país en Keycloak (`realm`) y en Kong (`workspace` o `consumer`). Término corporativo: tenant.                                                                           |
| **Loki**            | Sistema de agregación de logs del stack de observabilidad corporativo (Grafana Labs). Kong envía logs via Fluent Bit/FireLens.                                                                 |
| **Tempo**           | Backend de trazas distribuidas del stack corporativo. Acepta API Zipkin-compatible en `:9411`.                                                                                                 |
| **Mimir**           | Backend de métricas a largo plazo del stack corporativo; compatible con Prometheus remote_write.                                                                                               |
| **FireLens**        | Sidecar de ECS Fargate basado en Fluent Bit que redirige stdout de contenedores a destinos como Loki.                                                                                          |

## Acrónimos

| Acrónimo | Significado                             |
| -------- | --------------------------------------- |
| `ALB`    | Application Load Balancer (AWS)         |
| `ECS`    | Elastic Container Service (AWS Fargate) |
| `TLS`    | Transport Layer Security                |
| `CORS`   | Cross-Origin Resource Sharing           |
| `SLA`    | Service Level Agreement                 |
| `RTO`    | Recovery Time Objective                 |
| `RPO`    | Recovery Point Objective                |
| `RPS`    | Requests Per Second                     |
| `OIDC`   | OpenID Connect                          |
| `PDK`    | Plugin Development Kit (Kong)           |
