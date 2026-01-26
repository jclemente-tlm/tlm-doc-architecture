# Estándares Técnicos Talma

Esta sección contiene los estándares técnicos que implementan los [lineamientos arquitectónicos](/docs/fundamentos-corporativos/lineamientos) de Talma.

## 📋 Estructura

### [APIs REST](./apis/)

Estándares técnicos para el desarrollo de APIs REST:

1. **Diseño REST**: Principios RESTful, naming conventions, estructura de recursos
2. **Seguridad de APIs**: Autenticación JWT, OAuth, autorización, protección de datos
3. **Validación y Errores**: FluentValidation, RFC 7807, manejo global de excepciones
4. **Versionado**: Semantic versioning, estrategias de compatibilidad
5. **Performance**: Paginación, caching, compresión, rate limiting

### [Código](./codigo/)

Estándares de Clean Code por lenguaje de programación:

1. **C# y .NET**: Principios SOLID, naming, manejo de errores, async/await
2. **TypeScript**: Clean Code adaptado para TypeScript
3. **SQL**: Estilo, buenas prácticas para PostgreSQL y Oracle

### [Infraestructura](./infraestructura/)

Estándares para contenedores e infraestructura cloud:

1. **Docker**: Dockerfile, imágenes, seguridad, multi-stage builds
2. **Infraestructura como Código**: Terraform, AWS CDK, state management, módulos
3. **Gestión de Secretos**: AWS Secrets Manager, Azure Key Vault, rotación

### [Testing](./testing/)

Estándares para pruebas y cobertura de código:

1. **Testing Unitario e Integración**: xUnit, Jest, mocking, coverage mínimo 80%

### [Observabilidad](./observabilidad/)

Estándares para logging, monitoreo y trazabilidad:

1. **Logging Estructurado**: Serilog, Winston, formato JSON, correlation IDs
2. **Monitoreo y Métricas**: OpenTelemetry, health checks, distributed tracing, Prometheus

### [Mensajería](./mensajeria/)

Estándares para mensajería asíncrona y colas:

1. **Kafka y Eventos**: Event-driven architecture, event schemas, Kafka producers/consumers
2. **Colas de Mensajes**: AWS SQS, RabbitMQ, dead letter queues, batch processing

### [Documentación](./documentacion/)

Estándares para documentación técnica y diagramas:

1. **Diagramas Arquitectónicos**: C4 model, arc42, Structurizr, PlantUML, Mermaid
2. **Documentación de APIs**: OpenAPI/Swagger, especificaciones REST

## 🔗 Relación con otros niveles

```
Principios (POR QUÉ)
    ↓
Lineamientos (CÓMO abstracto)
    ↓
Estándares (QUÉ técnico)  ← Estás aquí
    ↓
Convenciones (CÓMO escribir)
    ↓
Código de Producción
```

### Diferencias clave

| Nivel           | Descripción              | Ejemplo                                                         |
| --------------- | ------------------------ | --------------------------------------------------------------- |
| **Principio**   | Valor fundamental        | "Seguridad desde el Diseño"                                     |
| **Lineamiento** | Directriz arquitectónica | "Diseñar APIs con autenticación y autorización obligatoria"     |
| **Estándar**    | Especificación técnica   | "Usar JWT Bearer con validación de issuer, audience y lifetime" |
| **Convención**  | Regla de escritura       | "Nombres de endpoints en kebab-case: /api/v1/user-profiles"     |

## 📚 Cómo usar estos estándares

1. **Al iniciar un proyecto nuevo**: Revisar todos los estándares aplicables
2. **Durante desarrollo**: Consultar estándares específicos según el área de trabajo
3. **En code review**: Validar cumplimiento de estándares
4. **Al actualizar**: Proponer cambios vía PR a este repositorio

## 🎯 Cobertura de Lineamientos

Cada estándar debe implementar uno o más lineamientos:

| Estándar                 | Lineamientos Implementados                      |
| ------------------------ | ----------------------------------------------- |
| APIs/Diseño REST         | Lineamiento 06: Diseño de APIs                  |
| APIs/Seguridad           | Lineamiento Seguridad 02: Identidad y Accesos   |
| APIs/Performance         | Lineamiento Arq. 05: Observabilidad (parcial)   |
| Infraestructura/Docker   | Lineamiento Arq. 03: Diseño Cloud Native        |
| Infraestructura/IaC      | Lineamiento Op. 02: Infraestructura como Código |
| Testing/Unit-Integration | Lineamiento Op. 04: Testing y Calidad           |
| Observabilidad/Logging   | Lineamiento Arq. 05: Observabilidad             |

## ✅ Validación de Cumplimiento

### En desarrollo

- Linters configurados según estándares (ESLint, StyleCop, etc.)
- Pre-commit hooks para validación automática
- SonarQube para análisis estático

### En CI/CD

- Tests de cobertura mínima (80%)
- Validación de formato (terraform fmt, dotnet format)
- Security scans (Trivy, OWASP Dependency Check)

### En code review

- Checklist de estándares aplicables
- Verificación de ADRs para decisiones técnicas
- Cumplimiento de convenciones de nombres

## 📖 Referencias

- [Principios](/docs/fundamentos-corporativos/principios)
- [Lineamientos](/docs/fundamentos-corporativos/lineamientos)
- [Convenciones](/docs/fundamentos-corporativos/convenciones)
- [ADRs](/docs/decisiones-de-arquitectura)

---

**Última actualización**: 2025-01-26
**Responsable**: Equipo de Arquitectura
