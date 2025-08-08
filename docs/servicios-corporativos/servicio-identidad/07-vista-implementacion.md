# 7. Vista De Implementación

## 7.1 Estructura Del Proyecto

| Componente      | Ubicación            | Tecnología         |
|-----------------|---------------------|--------------------|
| Keycloak        | Docker/ECS           | Keycloak 23+       |
| PostgreSQL      | AWS RDS/Aurora       | PostgreSQL 15+     |
| Configuración   | AWS Secrets Manager  | JSON               |
| Despliegue      | AWS ECS Fargate      | Docker             |
| Redis           | AWS ElastiCache      | Redis 7+           |
| API Identidad   | ECS                  | ASP.NET Core 8     |
| Token Service   | ECS                  | .NET 8, gRPC       |

## 7.2 Dependencias Principales

| Dependencia     | Versión | Propósito           |
|-----------------|---------|---------------------|
| Keycloak        | 23+     | Identity Provider   |
| PostgreSQL      | 15+     | Base de datos       |
| Docker          | 20+     | Contenedorización   |
| AWS ECS         | -       | Orquestación        |
| Redis           | 7+      | Cache/sesiones      |

## 7.3 Infraestructura AWS

- VPC segmentada por ambientes (dev, staging, prod)
- Subredes públicas, privadas y de base de datos
- Balanceadores ALB públicos e internos
- RDS Aurora PostgreSQL multi-AZ
- ElastiCache Redis cluster
- Seguridad: Security Groups y Network ACLs
- Secrets y configuración gestionados en AWS Secrets Manager

## 7.4 Despliegue Y Configuración De Servicios

- Keycloak: ECS Fargate, 3+ instancias, health checks, métricas y logs habilitados
- API Identidad: ECS Fargate, 2+ instancias, health checks, integración Keycloak y Redis
- Token Validation Service: ECS Fargate, gRPC, integración JWKS Keycloak
- Configuración de ALB para HTTPS, redirección HTTP→HTTPS, certificados ACM
- Auto Scaling basado en CPU y métricas de servicio

## 7.5 Ambientes Y Buenas Prácticas

| Ambiente     | Propósito                | Configuración clave                |
|--------------|--------------------------|------------------------------------|
| Desarrollo   | Pruebas y desarrollo     | Recursos mínimos, sample data      |
| Staging      | QA y validación previa   | Datos anonimizados, clustering     |
| Producción   | Carga real, HA           | Multi-AZ, auto scaling, seguridad  |

- Todos los ambientes con monitoreo, logs y backups configurados
- Acceso restringido por VPN y listas blancas de IP
- Certificados TLS gestionados por ACM

## 7.6 Backup Y Disaster Recovery

- Backups automáticos diarios de base de datos (30 días prod, 7 días staging)
- Snapshots manuales antes de despliegues mayores
- Export diario de configuración de tenants (realms) a S3 versionado
- Backups de estado de infraestructura (Terraform, CloudFormation)
- Plan de recuperación: RTO < 4h, RPO < 15min, cross-region para base de datos

## 7.7 Seguridad Y Cumplimiento

- Seguridad de red: Security Groups, NACLs, subredes privadas
- Secrets y credenciales fuera del código, gestionados en AWS Secrets Manager
- TLS 1.3, HSTS, certificados ACM EV en producción
- Auditoría de accesos y cambios críticos
- Cumplimiento: GDPR, SOX, ISO 27001, controles automatizados

## 7.8 Referencias

- [Keycloak Server Administration Guide](https://www.keycloak.org/docs/latest/server_admin/)
- [AWS ECS Documentation](https://docs.aws.amazon.com/ecs/)
- [AWS RDS Aurora Documentation](https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/)
- [Arc42 Implementation View](https://docs.arc42.org/section-7/)
- [C4 Model for Software Architecture](https://c4model.com/)
