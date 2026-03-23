---
sidebar_position: 12
title: Glosario
description: Términos y acrónimos del API Gateway corporativo basado en Kong OSS.
---

# 12. Glosario

## Términos del Dominio

| Término                 | Definición                                                                                                                                                               |
| ----------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **API Gateway**         | Punto de entrada único y centralizado para todas las APIs corporativas. Gestiona autenticación, enrutamiento, rate limiting y observabilidad.                            |
| **Kong Gateway**        | Solución de API Gateway open source, basada en NGINX + Lua, con un ecosistema extenso de plugins. Versión en uso: 3.9.1.                                                 |
| **decK**                | Herramienta CLI declarativa para gestionar la configuración de Kong vía archivos YAML en GitOps. Lee todos los `*.yaml` del directorio de entorno.                       |
| **Konga**               | Interfaz web open source para administrar Kong visualmente. Versión: 0.14.9. Accesible vía nginx en `:3366/konga/`. Los cambios deben reflejarse en YAML de Kong.        |
| **nginx**               | Reverse proxy que expone Konga con path rewriting (`/konga/` → Konga `:1337`). Imagen: `nginx:1.29.3`.                                                                   |
| **Service**             | Entidad Kong que representa un sistema backend (URL o NLB). Ejemplo: `sisbon-prod`, `ext-talenthub-ats-prod`.                                                            |
| **Route**               | Regla de enrutamiento en Kong (por path) que vincula un request a un Service. Ejemplo: `/api/sisbon` → `sisbon-prod`.                                                    |
| **Plugin**              | Componente Kong que añade comportamiento (auth, rate limiting, logging, etc.) a nivel global o por Service.                                                              |
| **Consumer**            | Identidad de un tenant (realm) en Kong. Nombre de ejemplo: `tlm-mx-realm`, `tlm-pe-realm`.                                                                               |
| **ACL Group**           | Grupo de autorización en Kong. Cada sistema define qué grupos pueden acceder. Ejemplo: `sisbon-users`, `talenthub-users`.                                                |
| **Rate Limiting**       | Control del número máximo de requests por ventana de tiempo, aplicado por consumer.                                                                                      |
| **tenant (realm)**      | Ámbito de negocio en Keycloak y Kong. Cada tenant es un realm con nomenclatura `tlm-{scope}`, donde `{scope}` es el código geográfico (`mx`, `pe`) o funcional (`corp`). |
| **strip_path**          | Configuración de Route en Kong. `true` = el prefijo de la ruta se elimina antes de enviar al backend. `false` = el path completo se preserva.                            |
| **kong-deck-bootstrap** | Contenedor de arranque que ejecuta `deck sync` una vez que Kong está disponible. Usa `wait-for-kong.sh`. `restart: "no"`.                                                |
| **JWT RS256**           | JSON Web Token firmado con RSA 256 bits. La clave pública del realm se embebe en `_consumers.yaml` para validación offline.                                              |
| **JWKS**                | JSON Web Key Set; conjunto de claves públicas publicado por Keycloak. En esta implementación, la clave se embebe estáticamente en vez de consultarse dinámicamente.      |
| **NLB**                 | Network Load Balancer de AWS. Balanceador usado como backend de Sisbon.                                                                                                  |
| **Sisbon**              | Sistema de Bonificaciones de Talma. Multi-país: México (`tlm-mx`) y Perú (`tlm-pe`). Backend: NLB en AWS.                                                                |
| **Gestal / ATS**        | Sistema de Gestión de Tickets de Talma integrado con TalentHub ATS (externo). Solo Perú (`tlm-pe`).                                                                      |
| **TalentHub ATS**       | Sistema externo de gestión de talento (`api.talenthub.pe`). Kong adapta el request con `x-api-key` y reescritura de URI.                                                 |
| **Mimir**               | Backend de métricas a largo plazo del stack corporativo; compatible con Prometheus remote_write.                                                                         |

## Acrónimos

| Acrónimo | Significado                     |
| -------- | ------------------------------- |
| `ALB`    | Application Load Balancer (AWS) |
| `NLB`    | Network Load Balancer (AWS)     |
| `TLS`    | Transport Layer Security        |
| `SLA`    | Service Level Agreement         |
| `RTO`    | Recovery Time Objective         |
| `RPS`    | Requests Per Second             |
| `OIDC`   | OpenID Connect                  |
| `PDK`    | Plugin Development Kit (Kong)   |
| `ACL`    | Access Control List             |
| `IAM`    | Identity and Access Management  |
| `JWT`    | JSON Web Token                  |
| `JWKS`   | JSON Web Key Set                |
