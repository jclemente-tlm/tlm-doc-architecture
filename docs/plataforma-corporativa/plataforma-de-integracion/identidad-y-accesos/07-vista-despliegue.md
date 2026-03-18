---
sidebar_position: 7
title: Vista de Despliegue
description: Infraestructura AWS y configuración de despliegue de Keycloak.
---

# 7. Vista de Despliegue

![Vista de implementación del Sistema de Identidad](/diagrams/servicios-corporativos/identity_system_deployment.png)

## Estructura del Proyecto

| Componente    | Ubicación           | Tecnología              |
| ------------- | ------------------- | ----------------------- |
| `Keycloak`    | ECS Fargate         | Keycloak 23+ (`Docker`) |
| `PostgreSQL`  | AWS RDS/Aurora      | PostgreSQL 15+          |
| Configuración | AWS Secrets Manager | JSON                    |

## Infraestructura AWS

- VPC segmentada por ambientes (`dev`, `staging`, `prod`)
- Subredes públicas, privadas y de base de datos
- Balanceadores `ALB` públicos e internos
- `RDS Aurora PostgreSQL` multi-AZ
- Seguridad: Security Groups y Network ACLs
- Secrets y configuración gestionados en AWS Secrets Manager

## Despliegue y Configuración

- `Keycloak`: Contenedor único (`Docker`) desplegado en ECS Fargate, autoescalado horizontal, health checks, métricas y logs habilitados
- `Keycloak` únicamente se comunica con `PostgreSQL` (`RDS Aurora`), sin integración directa con otros servicios
- Configuración de `ALB` para HTTPS, redirección HTTP→HTTPS, certificados ACM
- Auto Scaling basado en CPU y métricas de servicio

## Ambientes

| Ambiente   | Propósito              | Configuración clave               |
| ---------- | ---------------------- | --------------------------------- |
| Desarrollo | Pruebas y desarrollo   | Recursos mínimos, sample data     |
| Staging    | QA y validación previa | Datos anonimizados, clustering    |
| Producción | Carga real, HA         | Multi-AZ, auto scaling, seguridad |

- Todos los ambientes con monitoreo, logs y backups configurados
- Acceso restringido por VPN y listas blancas de IP
- Certificados TLS gestionados por ACM

## Backup y Disaster Recovery

- Backups automáticos diarios de base de datos (`30 días prod`, `7 días staging`)
- Snapshots manuales antes de despliegues mayores
- Export diario de configuración de tenants (`realms`) a S3 versionado
- Estado de infraestructura versionado en `Terraform` (repositorio Git)
- Plan de recuperación: `RTO < 4h`, `RPO < 15min`, cross-region para base de datos
