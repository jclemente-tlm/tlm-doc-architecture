# 5. Vista de Bloques de Construcción

![Sistema de Identidad - Vista de Componentes](/diagrams/servicios-corporativos/identity_system.png)

> Figura 5.1: Vista de componentes del Servicio de Identidad

## 5.1 Componentes Principales

| Componente                | Responsabilidad                                      | Tecnología                  | Interfaces                  |
|---------------------------|------------------------------------------------------|-----------------------------|-----------------------------|
| Keycloak Core             | Proveedor de identidad multi-tenant (tenant/realm)   | Keycloak 23+ (Docker oficial), PostgreSQL | OAuth2/OIDC, SAML, Admin API |
| PostgreSQL                | Base de datos de identidades y configuración         | PostgreSQL 15+              | JDBC                        |
| Auditoría y Cumplimiento  | Logging estructurado, cumplimiento normativo         | Event Sourcing, ELK, Loki   | Event Bus, REST             |
| Gateway Federación        | Integración con IdPs externos                        | Conectores Keycloak         | SAML, OIDC, LDAP            |
| Consola Administración    | Interfaz administrativa                              | Keycloak Admin Console      | Web UI, Admin API           |

## 5.2 Relaciones y Estructura

- Keycloak se despliega como contenedor Docker oficial, conectado a una base de datos PostgreSQL dedicada.
- No se desarrollan componentes propios, se configura y extiende Keycloak mediante su consola y APIs.

## 5.3 Principios de Construcción

- Uso de componentes estándar y soportados por la comunidad.
- Separación de responsabilidades por componente.
- Multi-tenancy gestionado a nivel de tenant (realm) en Keycloak.
- Observabilidad y auditoría integradas desde el diseño.

## 5.4 Observabilidad y Monitoreo

- Métricas de autenticación, latencia y errores expuestas vía Prometheus y visualizadas en Grafana.
- Logs estructurados centralizados en Loki y ELK Stack.
- Trazas distribuidas recolectadas con OpenTelemetry y visualizadas en Jaeger.

## 5.5 Persistencia

- Keycloak almacena toda la información de identidades, configuración y sesiones en PostgreSQL usando su propio modelo de datos interno, el cual no es personalizado ni extendido por el equipo.

## 5.6 Interfaces Externas

| Servicio Integrado         | Propósito principal           |
|---------------------------|-------------------------------|
| API Gateway               | Validación de tokens          |
| Notification Service      | MFA, alertas                  |
| Audit Service             | Seguridad, eventos            |
| Corporate Services        | Contexto de usuario           |
| Federation Partners       | Integración IdPs externos     |
| Monitoring & Observability| Métricas, trazas, logs        |

## 5.7 Ejemplos Técnicos

### Obtención de Token de Acceso (OAuth2/OIDC Client Credentials)

_Ejemplo de autenticación máquina a máquina (M2M) usando el flujo client credentials de OAuth2/OIDC en Keycloak. Este flujo es utilizado por servicios o aplicaciones backend para obtener un token de acceso sin intervención de usuario, típico en integraciones API-to-API multi-tenant._

**Request:**

```http
POST /realms/{tenant}/protocol/openid-connect/token
Content-Type: application/x-www-form-urlencoded

grant_type=client_credentials&client_id=app-client&client_secret=secreto
```

**Response:**

```json
{
  "access_token": "...",
  "expires_in": 900,
  "refresh_expires_in": 900,
  "token_type": "Bearer",
  "scope": "profile email tenant:peru"
}
```

## 5.8 Referencias

- [Keycloak Server Administration Guide](https://www.keycloak.org/docs/latest/server_admin/)
- [Keycloak Docker Image](https://www.keycloak.org/server/containers)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Arc42 Componentes de Construcción](https://docs.arc42.org/section-5/)
- [C4 Model for Software Architecture](https://c4model.com/)
