# 4. Estrategia De Solución

## 4.1 Decisiones Clave De Arquitectura

| Decisión                | Alternativas Evaluadas         | Seleccionada             |
|-------------------------|-------------------------------|--------------------------|
| Proveedor de Identidad  | Auth0, Okta, `Keycloak`       | `Keycloak`               |
| Multi-tenancy           | Single tenant (`realm`), multi-tenant (`realms`) | Multi-tenant (`realms`) |
| Federación de Identidad | Solo externo, híbrido         | Híbrido                  |
| Base de Datos           | MySQL, `PostgreSQL`           | `PostgreSQL`             |
| Despliegue              | VM, contenedores, serverless  | Contenedores             |

## 4.2 Patrones Y Estrategias Aplicadas

- Multi-tenancy: Cada `tenant` (`realm`) es independiente en `Keycloak`, con aislamiento total de datos y configuración.
- Federación: Integración con `LDAP` y `SAML`/`OIDC` para federar usuarios desde sistemas legados y Google Workspace.
- API Gateway: Validación centralizada de tokens `JWT`, forwarding seguro, control de acceso y observabilidad.
- Arquitectura limpia (Clean Architecture) y CQRS: Separación de comandos/consultas y dependencias, usando `.NET 8`, `FluentValidation`, `Mapster`.
- Observabilidad: Métricas, logs y trazas expuestos vía `Prometheus`, `Grafana`, `Loki`, `Jaeger`.
- Infraestructura como código: `Terraform` para provisión y despliegue reproducible.
- Contenedores y orquestación: `Docker` y `AWS ECS` para portabilidad y escalabilidad.
- DSLs de arquitectura: Modelado de contexto y componentes con C4 Model DSL y Structurizr DSL para trazabilidad y visualización.

## 4.3 Mitigación De Riesgos

| Riesgo                   | Probabilidad | Impacto | Mitigación                                    |
|--------------------------|--------------|---------|-----------------------------------------------|
| Bloqueo de usuarios      | Media        | Alta    | Autenticación paralela, rollback documentado  |
| Degradación de rendimiento| Baja        | Media   | Pruebas de carga, escalado progresivo         |
| Fallos en federación     | Media        | Media   | Circuit breakers, fallback local              |
| Pérdida de datos         | Baja         | Alta    | Backups, validación post-migración            |
| Configuración inconsistente| Baja       | Alta    | Infraestructura como código, validaciones CI  |

## 4.4 Referencias

- [Arc42 Solution Strategy](https://docs.arc42.org/section-4/)
- [Keycloak Architecture](https://www.keycloak.org/architecture/)
- [C4 Model DSL](https://c4model.com/)
- [Structurizr DSL](https://structurizr.com/dsl)
- [Terraform Documentation](https://www.terraform.io/docs)
- [AWS ECS Documentation](https://docs.aws.amazon.com/ecs/)
