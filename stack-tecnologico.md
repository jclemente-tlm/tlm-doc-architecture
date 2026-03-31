# Stack Tecnológico

Referencia oficial de tecnologías aprobadas en Talma. Cualquier desviación requiere un ADR que la respalde.

---

## Cloud — AWS

| Servicio        | Uso                                   |
| --------------- | ------------------------------------- |
| ECS Fargate     | Orquestación de contenedores          |
| EC2             | Cómputo general y contenedores Docker |
| S3              | Almacenamiento de objetos             |
| Secrets Manager | Gestión de secretos                   |
| Parameter Store | Configuración por entorno             |
| ALB             | Load balancer HTTP/HTTPS              |

---

## Plataformas de Despliegue

| Plataforma    | Contexto                                                                         |
| ------------- | -------------------------------------------------------------------------------- |
| ECS (Fargate) | Servicios cloud en contenedores                                                  |
| EC2           | Servicios cloud en VM o contenedores Docker                                      |
| Docker        | Contenedores en cualquier entorno: ECS, EC2 o servidores propios (Linux/Windows) |
| IIS           | Servicios y aplicaciones .NET en servidores Windows on-premise                   |

---

## Contenedores

| Tecnología                          | Uso                                  |
| ----------------------------------- | ------------------------------------ |
| Docker                              | Empaquetado y ejecución de servicios |
| Docker Compose                      | Entornos locales de desarrollo       |
| GitHub Container Registry (ghcr.io) | Registro de imágenes                 |

**Convenciones:**

- Imágenes base: `mcr.microsoft.com/dotnet/aspnet:8.0-alpine` (runtime) / `mcr.microsoft.com/dotnet/sdk:8.0-alpine` (build)
- Siempre multi-stage builds; nunca `latest`

---

## Lenguaje y Runtime

| Tecnología   | Versión | Uso                  |
| ------------ | ------- | -------------------- |
| C# / .NET    | 8+      | Lenguaje principal   |
| ASP.NET Core | 8+      | APIs y servicios web |

---

## Arquitectura y Patrones

| Patrón                     | Aplicación                                             |
| -------------------------- | ------------------------------------------------------ |
| Clean Architecture         | Separación de responsabilidades en todos los servicios |
| Domain-Driven Design (DDD) | Modelado de dominio y reglas de negocio                |
| CQRS (sin MediatR)         | Comandos y queries en la capa de aplicación            |

---

## Librerías .NET

| Librería                                      | Uso                                                                 |
| --------------------------------------------- | ------------------------------------------------------------------- |
| Entity Framework Core                         | ORM — acceso y persistencia de datos relacionales                   |
| EF Core Migrations                            | Migraciones de esquema de base de datos                             |
| Dapper                                        | Micro-ORM — consultas SQL directas cuando se requiere mayor control |
| FluentValidation                              | Validación de datos en capa de aplicación                           |
| Mapster                                       | Mapeo DTOs ↔ entidades (no AutoMapper)                              |
| Serilog                                       | Logs estructurados                                                  |
| OpenTelemetry                                 | Trazas distribuidas y métricas                                      |
| Microsoft.Extensions.Diagnostics.HealthChecks | Health check endpoints                                              |

---

## Bases de Datos

| Motor      | Uso                                              |
| ---------- | ------------------------------------------------ |
| PostgreSQL | Base de datos relacional principal + event store |
| Oracle 19c | Sistemas legados                                 |
| SQL Server | Sistemas legados / on-premise                    |

---

## Cache

| Tecnología | Uso               |
| ---------- | ----------------- |
| Redis      | Cache distribuido |

---

## Mensajería

| Tecnología                | Uso                                                                 |
| ------------------------- | ------------------------------------------------------------------- |
| Apache Kafka (modo KRaft) | Mensajería asíncrona — implementación propia sin Confluent Platform |
| Debezium                  | CDC (Change Data Capture) — captura de cambios desde bases de datos |

---

## Infraestructura de Red

| Tecnología | Uso                                                                      |
| ---------- | ------------------------------------------------------------------------ |
| nginx      | Reverse proxy — entrada al stack de observabilidad (Grafana, Loki, etc.) |

---

## API Gateway

| Tecnología       | Uso                           |
| ---------------- | ----------------------------- |
| Kong API Gateway | Gateway corporativo para APIs |

---

## Observabilidad

| Función         | Tecnología               |
| --------------- | ------------------------ |
| Logs            | Loki + Serilog           |
| Métricas        | Mimir                    |
| Trazas          | Tempo                    |
| Visualización   | Grafana                  |
| Recolección     | Grafana Alloy            |
| Instrumentación | OpenTelemetry (.NET SDK) |

---

## Seguridad

| Tecnología             | Uso                                                    |
| ---------------------- | ------------------------------------------------------ |
| Keycloak               | SSO — autenticación y autorización (realms/tenants)    |
| Trivy                  | Scanning de vulnerabilidades en imágenes de contenedor |
| Checkov                | Scanning de seguridad en IaC (Terraform)               |
| SonarQube Community    | Análisis estático de código (SAST)                     |
| OWASP Dependency-Check | Detección de dependencias vulnerables                  |

---

## DevOps

| Tecnología      | Uso                          |
| --------------- | ---------------------------- |
| GitHub          | Control de versiones         |
| GitHub Actions  | CI/CD                        |
| GitHub Packages | Registro de paquetes NuGet   |
| Terraform       | Infrastructure as Code (IaC) |

---

## Tecnologías Excluidas

No usar en ningún servicio nuevo. Requieren ADR para excepciones.

| Tecnología                                     | Motivo                                    |
| ---------------------------------------------- | ----------------------------------------- |
| AutoMapper                                     | Reemplazado por Mapster                   |
| MediatR                                        | CQRS implementado sin frameworks externos |
| Kubernetes                                     | No forma parte del stack de orquestación  |
| RabbitMQ                                       | Reemplazado por Kafka                     |
| Confluent Platform / AWS MSK / Schema Registry | Kafka en modo KRaft propio                |
| SQS / SNS                                      | No en uso                                 |
| HashiCorp Vault                                | Reemplazado por AWS Secrets Manager       |
| Java / Python / Node.js / JavaScript           | Lenguajes fuera del stack                 |
| MySQL                                          | No en uso                                 |
