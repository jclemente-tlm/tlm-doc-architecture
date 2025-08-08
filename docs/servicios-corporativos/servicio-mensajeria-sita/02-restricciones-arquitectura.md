# 2. Restricciones de la arquitectura

Esta sección documenta todas las limitaciones técnicas, de rendimiento, seguridad, organizacionales y regulatorias que condicionan el diseño y operación del sistema de mensajería SITA. Las restricciones aquí descritas son obligatorias y deben ser consideradas en cada decisión arquitectónica.

## 2.1 Restricciones técnicas

| Categoría | Restricción | Justificación |
|------------|---------------|---------------|
| **Runtime** | .NET 8 | Estándar corporativo |
| **Base de datos** | PostgreSQL | Robustez y ACID |
| **Cola de eventos** | PostgreSQL inicial, SNS+SQS futuro | Simplicidad inicial, escalabilidad futura |
| **Contenedores** | Docker | Portabilidad |
| **Protocolos SITA** | SITATEX, AFTN | Estándares aeronáuticos |

### Protocolos SITA obligatorios

- **SITA SITATEX** para comunicación aeronáutica
- **Direccionamiento AFTN** para enrutamiento
- **Estándares ICAO** para formatos de mensaje
- **Mensajes Tipo B** para operaciones aeroportuarias

### Infraestructura y Plataforma

| Área | Restricción | Justificación | Solución Adoptada |
|------|-------------|---------------|-------------------|
| **Contenedorización** | Despliegue obligatorio en contenedores Docker | Estandarización DevOps, portabilidad | Orquestación Docker + Kubernetes |
| **Base de Datos** | PostgreSQL como RDBMS principal | Experiencia del equipo, requisitos cumplimiento | PostgreSQL 15+ con replicación |
| **Entorno de Ejecución** | .NET 8 LTS como plataforma principal | Estandarización corporativa, soporte empresarial | APIs Web ASP.NET Core |
| **Colas de Mensajes** | Bus de eventos agnóstico para transmisión de mensajes | Alto rendimiento, capacidades de abastecimiento de eventos | Cluster de bus de eventos con particionado |
| **Registro** | Serilog para logging estructurado | Observabilidad, resolución problemas | Logging JSON estructurado |

### Integración y Conectividad

| Sistema Externo | Protocolo Requerido | Restricción | Implementación |
|-----------------|---------------------|-------------|----------------|
| **Red SITA** | SITATEX sobre X.25/IP | Soporte protocolo legacy | Adaptador puente protocolo |
| **Aerolíneas Partner** | AFTN/CIDIN | Mensajería estándar industria | Gateway multi-protocolo |
| **Sistemas Aeropuerto** | Varios (SOAP, REST, MQ) | Integración heterogénea | Patrón Enterprise Service Bus |
| **Track & Trace** | APIs REST internas | Entrega de eventos en tiempo real | Clientes HTTP asíncronos |
| **Sistemas Gubernamentales** | Canales seguros (VPN/TLS) | Cumplimiento seguridad | Túneles cifrados, certificados |

### Performance y Capacidad

| Métrica | Restricción | Justificación | Arquitectura Requerida |
|---------|-------------|---------------|------------------------|
| **Capacidad de Procesamiento de Mensajes** | 10,000 mensajes/hora pico | Operaciones aeroportuarias críticas | Procesamiento asíncrono, basado en colas |
| **Latencia** | < 30 segundos extremo a extremo | Tiempo crítico para operaciones de vuelo | Caché en memoria, enrutamiento optimizado |
| **Disponibilidad** | 99.95% tiempo de actividad | Operaciones 24/7, impacto en vuelos | Agrupación activo-pasivo |
| **Tamaño de Mensaje** | Hasta 32KB por mensaje SITA | Limitación de protocolo SITATEX | Fragmentación de mensaje, compresión |

## 2.2 Restricciones organizacionales y regulatorias

### Cumplimiento y Regulatorio

| Área | Restricción | Autoridad | Implementación Requerida |
|------|-------------|-----------|--------------------------|
| **Aviation Security** | ICAO Annex 17 compliance | International Civil Aviation Organization | Security controls, trazas de auditoría |
| **Data Privacy** | GDPR compliance en operaciones EU | European Data Protection Authorities | Data anonymization, consent management |
| **Financial Controls** | SOX compliance para data financiera | Corporate audit requirements | Access controls, change management |
| **Local Regulations** | Compliance con regulaciones por país | Aviation authorities per country | Country-specific adapters |

### Arquitectura Corporativa

| Restricción | Origen | Impacto | Solución |
|-------------|--------|---------|----------|
| **Multi-tenant Architecture** | Requisito corporativo | Aislamiento de datos por cliente | Tenant-aware data layer |
| **Multi-country Support** | Expansión regional | Localización, regulaciones locales | Country-specific configurations |
| **Identity Integration** | SSO corporativo | Autenticación centralizada vía Keycloak | OAuth2/OIDC integration |
| **Audit Requirements** | Compliance corporativo | Logging de todas las operaciones | Comprehensive audit logging |

### Operaciones y Mantenimiento

| Área | Restricción | Justificación | Implementación |
|------|-------------|---------------|----------------|
| **24/7 Operations** | Soporte continuo requerido | Operaciones aeroportuarias críticas | Monitoring, alertas, runbooks |
| **Change Windows** | Mantenimiento solo en horarios específicos | Minimizar impacto operacional | Blue-green deployments |
| **Support Model** | L1/L2/L3 support structure | Escalation procedures defined | Operational dashboards, documentation |
| **Disaster Recovery** | RTO: 4 horas, RPO: 15 minutos | Business continuity requirements | Cross-region replication |

## 2.3 Restricciones convencionales y de calidad

### Estándares de Desarrollo

| Categoría | Estándar | Herramienta/Framework | Enforcement |
|-----------|----------|----------------------|-------------|
| **Coding Standards** | Microsoft C# Guidelines | StyleCop, EditorConfig | CI/CD pipeline checks |
| **API Design** | OpenAPI 3.0 specification | Swashbuckle, NSwag | Automated documentation |
| **Testing** | Unit tests > 80% coverage | xUnit, NSubstitute | SonarQube quality gates |
| **Documentation** | Arc42 methodology | Markdown, Structurizr | Documentation reviews |

### Seguridad

| Aspecto | Restricción | Implementación | Validación |
|---------|-------------|----------------|------------|
| **Authentication** | OAuth2/OIDC mandatory | Keycloak integration | Security testing |
| **Authorization** | RBAC with fine-grained permissions | Claims-based authorization | Penetration testing |
| **Data Encryption** | TLS 1.3 for transport, AES-256 at rest | .NET encryption libraries | Security audits |
| **Secret Management** | Azure Key Vault / HashiCorp Vault | Centralized secret storage | Secret rotation policies |

### Monitoreo y Observabilidad

| Componente | Herramienta Requerida | Propósito | Configuración |
|------------|----------------------|-----------|---------------|
| **Application Metrics** | Prometheus + Grafana | Performance monitoring | Custom metrics, dashboards |
| **Logging** | ELK Stack (Elasticsearch, Logstash, Kibana) | Centralized logging | Structured logs, retention |
| **Tracing** | OpenTelemetry + Jaeger | Distributed tracing | Request correlation |
| **Health Checks** | ASP.NET Core Health Checks | Service disponibilidad | /health endpoints |

## 2.4 Restricciones específicas SITA

### Conectividad SITA Network

| Aspecto | Restricción | Detalle Técnico |
|---------|-------------|-----------------|
| **Network Access** | Conexión dedicada SITA requerida | Línea dedicada, no internet público |
| **Addressing Scheme** | AFTN addresses format | 8-character ICAO location codes |
| **Message Priority** | Priority levels (SS, DD, FF, GG) | Routing based on message urgency |
| **Manejo de Errores** | SITA-specific error codes | Standard SITA error reporting |

### Message Format Compliance

| Tipo Mensaje | Standard | Validación Requerida | Ejemplo |
|--------------|---------|---------------------|---------|
| **Flight Plans** | ICAO 4444 format | Syntax, route validation | FPL messages |
| **Flight Updates** | Type B messages | Field validation, timing | CHG, CNL, DLA messages |
| **Airport Operations** | SITA specifications | Operational constraints | Gate assignments, baggage |
| **Weather Data** | ICAO Annex 3 | Meteorological format | METAR, TAF messages |

### Certification Requirements

| Certificación | Organismo | Frecuencia | Scope |
|---------------|-----------|------------|-------|
| **SITA Network Certification** | SITA IT Services | Annual | Message format compliance |
| **ICAO Compliance** | Local aviation authority | Bi-annual | Operational procedures |
| **Security Certification** | Corporate security | Quarterly | Security controls audit |

## 2.5 Impacto en el diseño

### Decisiones Arquitectónicas Derivadas

| Restricción | Decisión de Diseño | Rationale |
|-------------|-------------------|-----------|
| **Legacy Protocol Support** | Adapter Pattern implementation | Isolation of legacy complexity |
| **High Disponibilidad** | Active-Passive clustering | Meet 99.95% uptime requirement |
| **Multi-tenant** | Database per tenant strategy | Data isolation and compliance |
| **Message Validation** | Pipeline pattern with validators | Extensible validation chain |
| **Manejo de Errores** | Circuit breaker pattern | Resilience for external dependencies |

### Trade-offs Aceptados

| Trade-off | Decisión | Justificación |
|-----------|----------|---------------|
| **Performance vs Compliance** | Priorizar compliance | Regulatory requirements non-negotiable |
| **Flexibility vs Standards** | Adherir a standards SITA | Industry interoperability critical |
| **Cost vs Reliability** | Invertir en redundancia | Operational impact of downtime |
| **Simplicity vs Features** | Feature completeness | Support diverse airline requirements |

## Referencias

### Estándares y Especificaciones

- [SITA SITATEX Protocol Specification](https://www.sita.aero/solutions/airline-operations/sitatex/)
- [ICAO Doc 4444 - PANS-ATM](https://www.icao.int/publications/documents/4444_cons_en.pdf)
- [AFTN Manual (ICAO Doc 7030)](https://www.icao.int/publications/pages/publication.aspx?docnum=7030)
- [Type B Message Format Standard](https://www.sita.aero/resources/type-b-message-standard/)

### Regulaciones

- [ICAO Annex 17 - Aviation Security](https://www.icao.int/Security/Pages/Annex-17---Aviation-Security.aspx)
- [GDPR Regulation (EU) 2016/679](https://gdpr-info.eu/)
- [Sarbanes-Oxley Act](https://www.congress.gov/bill/107th-congress/house-bill/3763)

### Documentación Corporativa

- [Keycloak Documentation](https://www.keycloak.org/documentation)
- [.NET 8 Documentation](https://docs.microsoft.com/en-us/dotnet/)
- [Arc42 Architecture Template](https://arc42.org/)
