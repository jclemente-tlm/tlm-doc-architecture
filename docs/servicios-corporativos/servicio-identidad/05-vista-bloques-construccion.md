# 5. Vista De Bloques De Construcción

## 5.1 Componentes Principales

| Componente                        | Responsabilidad                                      | Tecnología                  | Interfaces                  |
|------------------------------------|------------------------------------------------------|-----------------------------|-----------------------------|
| Keycloak Core                      | Proveedor de identidad multi-tenant (realm)           | Keycloak 23+, Java 21, PostgreSQL | OAuth2/OIDC, SAML, Admin API |
| API Gestión Identidad               | Gestión programática de identidades                   | ASP.NET Core 8, EF Core     | API REST, GraphQL           |
| Servicio Validación Tokens          | Validación distribuida de JWT, introspección, caché   | .NET 8, gRPC, Redis         | gRPC, HTTP/2                |
| Auditoría Y Cumplimiento            | Logging estructurado, cumplimiento normativo          | Event Sourcing, ELK, Loki   | Event Bus, REST             |
| Gateway Federación                  | Integración con IdPs externos                        | Conectores personalizados   | SAML, OIDC, LDAP            |
| Consola Administración              | Interfaz administrativa                              | React SPA                   | Consumo API REST            |

## 5.2 Diagrama De Bloques (C4: Container/Component)

```mermaid
flowchart TD
    subgraph Keycloak[Keycloak Core]
        KC[Keycloak 23+ (multi-tenant/realm)]
    end
    subgraph API[API Gestión Identidad]
        APIID[ASP.NET Core 8]
    end
    subgraph Token[Servicio Validación Tokens]
        TVS[.NET 8 gRPC]
    end
    subgraph Audit[Auditoría y Cumplimiento]
        AUD[Event Sourcing]
        LOKI[Loki]
        ELK[ELK Stack]
    end
    subgraph Federation[Gateway Federación]
        FED[Conectores SAML/OIDC/LDAP]
    end
    subgraph Admin[Consola Administración]
        ADMIN[React SPA]
    end
    KC <--> APIID
    KC <--> TVS
    KC <--> AUD
    KC <--> FED
    APIID <--> ADMIN
    TVS <--> KC
    AUD <--> KC
    FED <--> KC
```

## 5.3 Despliegue Automatizado (Terraform + AWS ECS)

```hcl
resource "aws_ecs_cluster" "identity" {
  name = "identity-service-cluster"
}
resource "aws_ecs_task_definition" "keycloak" {
  family                   = "keycloak"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = "1024"
  memory                   = "2048"
  container_definitions    = file("keycloak-container.json")
}
resource "aws_ecs_service" "keycloak" {
  name            = "keycloak"
  cluster         = aws_ecs_cluster.identity.id
  task_definition = aws_ecs_task_definition.keycloak.arn
  desired_count   = 3
  launch_type     = "FARGATE"
  network_configuration {
    subnets          = ["subnet-xxxx", "subnet-yyyy"]
    security_groups  = ["sg-xxxx"]
    assign_public_ip = true
  }
  load_balancer {
    target_group_arn = aws_lb_target_group.keycloak.arn
    container_name   = "keycloak"
    container_port   = 8080
  }
}
```

## 5.4 Observabilidad Y Monitoreo

- Métricas de autenticación, latencia y errores expuestas vía Prometheus y visualizadas en Grafana.
- Logs estructurados centralizados en Loki y ELK Stack.
- Trazas distribuidas recolectadas con OpenTelemetry y visualizadas en Jaeger.
- Ejemplo de integración de métricas custom:

```csharp
using Prometheus;
public class AuthMetrics
{
    private static readonly Counter AuthSuccess = Metrics.CreateCounter("auth_success_total", "Total de autenticaciones exitosas");
    private static readonly Counter AuthFailure = Metrics.CreateCounter("auth_failure_total", "Total de autenticaciones fallidas");
    public static void IncSuccess() => AuthSuccess.Inc();
    public static void IncFailure() => AuthFailure.Inc();
}
```

## 5.5 Relación Con C4 Y Structurizr DSL

- Cada bloque corresponde a un Container o Component en el modelo C4.
- Los tenants (realms) de Keycloak están modelados explícitamente en los diagramas Structurizr DSL.
- Las relaciones, flujos y dependencias técnicas están documentadas en los archivos `.dsl` bajo `design/`.

## 5.6 Modelo De Datos Y Persistencia

| Tabla                | Propósito                        | Relaciones Clave                |
|----------------------|----------------------------------|---------------------------------|
| REALM                | Configuración de tenants (realms) | 1:N con USERS, ROLES            |
| USER_ENTITY          | Usuarios principales              | N:1 con REALM, 1:N con USER_ROLE_MAPPING |
| KEYCLOAK_ROLE        | Definición de roles               | N:1 con REALM, N:M con USERS    |
| CLIENT               | Aplicaciones cliente OAuth2       | N:1 con REALM                   |
| USER_SESSION         | Sesiones activas                  | N:1 con USER_ENTITY             |
| user_profiles        | Perfiles extendidos               | 1:1 con USER_ENTITY             |
| identity_audit_log   | Auditoría de eventos              | N:1 con USER_ENTITY, N:1 con REALM |

## 5.7 Interfaces Externas

| Servicio Integrado         | Propósito principal           |
|---------------------------|-------------------------------|
| API Gateway               | Validación de tokens          |
| Notification Service      | MFA, alertas                  |
| Audit Service             | Seguridad, eventos            |
| Corporate Services        | Contexto de usuario           |
| Federation Partners       | Integración IdPs externos     |
| Monitoring & Observability| Métricas, trazas, logs        |

## 5.8 Ejemplos Técnicos

### Token Exchange (OAuth2/OIDC)

```json
{
  "access_token": "...",
  "token_type": "Bearer",
  "expires_in": 900,
  "refresh_token": "...",
  "id_token": "...",
  "scope": "openid profile email tenant:peru"
}
```

### User Management API

```json
{
  "userId": "uuid",
  "tenantId": "peru|ecuador|colombia|mexico",
  "username": "string",
  "email": "string",
  "profile": { "firstName": "string", "lastName": "string" },
  "roles": ["role1", "role2"],
  "attributes": { "employeeId": "string" }
}
```

## 5.9 Referencias

- [Keycloak Server Administration Guide](https://www.keycloak.org/docs/latest/server_admin/)
- [OAuth 2.0 RFC 6749](https://tools.ietf.org/html/rfc6749)
- [OpenID Connect Core 1.0](https://openid.net/specs/openid-connect-core-1_0.html)
- [Arc42 Componentes de Construcción](https://docs.arc42.org/section-5/)
- [C4 Model for Software Architecture](https://c4model.com/)

---
