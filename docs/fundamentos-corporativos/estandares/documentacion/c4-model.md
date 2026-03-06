---
id: c4-model
sidebar_position: 2
title: C4 Model
description: Estándar para visualizar arquitectura de software usando los 4 niveles de abstracción del C4 Model.
---

# C4 Model

## Contexto

Este estándar define cómo crear diagramas de arquitectura usando el C4 Model, un enfoque jerárquico con 4 niveles de abstracción. Complementa el estándar [arc42](./arc42.md) para documentación arquitectónica completa.

---

## Stack Tecnológico

| Componente            | Tecnología | Versión | Uso                               |
| --------------------- | ---------- | ------- | --------------------------------- |
| **Diagramas**         | Mermaid    | 10.0+   | C4 diagrams as code (preferido)   |
| **Diagramas**         | PlantUML   | 1.2024+ | C4 diagrams as code (alternativo) |
| **Generación Sitio**  | Docusaurus | 3.0+    | Renderizado de diagramas          |
| **Control Versiones** | GitHub     | -       | Versionamiento as code            |

---

## ¿Qué es el Modelo C4?

Enfoque para visualizar arquitectura de software mediante diagramas jerárquicos en 4 niveles de abstracción, similar a hacer "zoom" en un mapa.

**Niveles:**

1. **Context (C1)**: Sistema en su entorno, usuarios, sistemas externos
2. **Container (C2)**: Aplicaciones y data stores dentro del sistema
3. **Component (C3)**: Componentes dentro de un contenedor
4. **Code (C4)**: Clases y métodos (opcional, generado por IDE)

**Propósito:** Comunicar arquitectura a diferentes audiencias con el nivel apropiado de detalle.

**Beneficios:**
✅ Visualización clara y progresiva
✅ Diferentes niveles para diferentes stakeholders
✅ Complementa documentación textual
✅ Fácil mantenimiento (diagramas as code)

## C4 Level 1: Context Diagram

```mermaid
C4Context
    title System Context Diagram - E-Commerce Platform

    Person(customer, "Customer", "Compra productos online")
    Person(admin, "Administrator", "Gestiona catálogo y órdenes")

    System_Boundary(platform, "E-Commerce Platform") {
        System(customerService, "Customer Service", "Gestión de clientes")
        System(orderService, "Order Service", "Procesamiento de órdenes")
        System(productService, "Product Service", "Catálogo de productos")
        System(paymentService, "Payment Service", "Procesamiento de pagos")
    }

    System_Ext(paymentGateway, "Payment Gateway", "Stripe")
    System_Ext(emailService, "Email Service", "SendGrid")
    System_Ext(identityProvider, "Identity Provider", "Keycloak")

    Rel(customer, customerService, "Administra perfil", "HTTPS")
    Rel(customer, orderService, "Crea órdenes", "HTTPS")
    Rel(customer, productService, "Busca productos", "HTTPS")

    Rel(admin, customerService, "Administra clientes", "HTTPS")
    Rel(admin, orderService, "Gestiona órdenes", "HTTPS")
    Rel(admin, productService, "Gestiona catálogo", "HTTPS")

    Rel(orderService, customerService, "Valida cliente", "REST API")
    Rel(orderService, productService, "Valida stock", "REST API")
    Rel(orderService, paymentService, "Procesa pago", "REST API")

    Rel(paymentService, paymentGateway, "Autoriza pago", "REST API")
    Rel(orderService, emailService, "Envía confirmación", "REST API")

    Rel_Back(identityProvider, customer, "Autentica", "OAuth2")
    Rel_Back(identityProvider, admin, "Autentica", "OAuth2")
```

**Audiencia:** C-level, product managers, todos los stakeholders.

## C4 Level 2: Container Diagram

```mermaid
C4Container
    title Container Diagram - Customer Service

    Person(user, "User", "Usuario del sistema")

    System_Boundary(customerService, "Customer Service") {
        Container(api, "Customer API", ".NET 8 Web API", "Expone endpoints REST para gestión de clientes")
        ContainerDb(db, "Customer Database", "PostgreSQL 15", "Almacena datos de clientes, direcciones, documentos")
        Container(cache, "Cache", "Redis 7.2", "Cache de consultas frecuentes")
    }

    System_Ext(kafka, "Apache Kafka", "Message Broker")
    System_Ext(keycloak, "Keycloak", "Identity Provider")
    System_Ext(grafana, "Grafana Stack", "Observability")

    Rel(user, api, "Usa", "HTTPS/REST")
    Rel(api, keycloak, "Valida tokens", "OAuth2/OIDC")
    Rel(api, db, "Lee/escribe", "EF Core / ADO.NET")
    Rel(api, cache, "Cache reads", "StackExchange.Redis")
    Rel(api, kafka, "Publica eventos", "Confluent.Kafka")
    Rel(api, grafana, "Logs, metrics, traces", "OpenTelemetry")
```

**Audiencia:** Arquitectos, líderes técnicos, devops.

## C4 Level 3: Component Diagram

```mermaid
C4Component
    title Component Diagram - Customer API

    Container_Boundary(api, "Customer API") {
        Component(controllers, "Controllers", "ASP.NET Core MVC", "Endpoints REST (GET, POST, PUT, DELETE)")
        Component(middleware, "Middleware", "ASP.NET Core", "Auth, Exception Handling, Logging")

        Component(useCases, "Use Cases", "Application Services", "CreateCustomer, GetCustomer, UpdateCustomer, DeleteCustomer")
        Component(validators, "Validators", "FluentValidation", "Validación de DTOs")
        Component(mappers, "Mappers", "AutoMapper", "DTO ↔ Entity mapping")

        Component(domain, "Domain Model", "Domain Entities", "Customer, Address, Document (entidades + lógica)")
        Component(domainEvents, "Domain Events", "Events", "CustomerCreated, CustomerUpdated, CustomerDeleted")

        Component(repositories, "Repositories", "EF Core", "CustomerRepository, AddressRepository")
        Component(eventPublisher, "Event Publisher", "Kafka Producer", "Publicación de eventos a Kafka")
        Component(cacheService, "Cache Service", "Redis Client", "Get/Set cache")
    }

    ContainerDb_Ext(db, "PostgreSQL", "Database")
    Container_Ext(kafka, "Kafka", "Message Broker")
    Container_Ext(redis, "Redis", "Cache")

    Rel(controllers, middleware, "Pasa por")
    Rel(controllers, useCases, "Llama")
    Rel(controllers, validators, "Valida")
    Rel(useCases, domain, "Usa")
    Rel(useCases, repositories, "Persiste")
    Rel(useCases, eventPublisher, "Publica")
    Rel(useCases, cacheService, "Cache")
    Rel(domain, domainEvents, "Dispara")

    Rel(repositories, db, "Lee/Escribe")
    Rel(eventPublisher, kafka, "Produce")
    Rel(cacheService, redis, "Get/Set")
```

**Audiencia:** Desarrolladores, arquitectos de software.

## C4 con PlantUML (alternativa)

```plantuml
@startuml C4_Context
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Context.puml

LAYOUT_WITH_LEGEND()

title System Context - Customer Service

Person(customer, "Customer", "Usuario que usa el sistema")
Person(admin, "Administrator", "Administrador del sistema")

System(customerService, "Customer Service", "Gestión de clientes")

System_Ext(orderService, "Order Service", "Gestión de órdenes")
System_Ext(keycloak, "Keycloak", "Identity Provider")

Rel(customer, customerService, "Usa", "HTTPS/REST")
Rel(admin, customerService, "Administra", "HTTPS/REST")
Rel(orderService, customerService, "Valida cliente", "REST API")
Rel(customerService, keycloak, "Autentica", "OAuth2")

@enduml
```

---

## Implementación

```bash
# Crear carpeta para diagramas C4
mkdir -p docs/c4-diagrams

# Estructura recomendada
docs/c4-diagrams/
├── c1-context.md        # Context diagram del sistema completo
├── c2-containers.md     # Container diagrams por servicio
└── c3-components.md     # Component diagrams para módulos complejos
```

---

## Requisitos Técnicos

### MUST (Obligatorio)

- **MUST** incluir diagrama C4 Level 1 (Context) para cada sistema
- **MUST** incluir diagrama C4 Level 2 (Container) para cada servicio
- **MUST** usar Mermaid o PlantUML (diagramas as code)
- **MUST** mantener diagramas sincronizados con código
- **MUST** versionar diagramas en Git junto con el código

### SHOULD (Fuertemente recomendado)

- **SHOULD** incluir diagrama C4 Level 3 (Component) para módulos complejos
- **SHOULD** usar Mermaid para diagramas (mejor integración con Docusaurus)
- **SHOULD** incluir diagrama C1 en README del repositorio
- **SHOULD** referenciar los diagramas desde el arc42 sección 3 y 5

### MAY (Opcional)

- **MAY** usar C4 Level 4 (Code) para componentes críticos
- **MAY** incluir diagramas de deployment como extensión de C4 Level 2
- **MAY** generar diagramas automáticamente desde código con herramientas como Structurizr

### MUST NOT (Prohibido)

- **MUST NOT** crear diagramas binarios (Word, Visio) sin source code equivalente
- **MUST NOT** documentar diagramas solo en wikis externos sin source code
- **MUST NOT** mezclar niveles de abstracción en un mismo diagrama

---

## Referencias

- [C4 Model](https://c4model.com/)
- [Mermaid C4 Diagrams](https://mermaid.js.org/syntax/c4.html)
- [PlantUML C4](https://github.com/plantuml-stdlib/C4-PlantUML)
- [arc42](./arc42.md)
- [Gestión de ADRs](../gobierno/adr-management.md)

---

**Última actualización**: 18 de febrero de 2026
**Responsable**: Equipo de Arquitectura
