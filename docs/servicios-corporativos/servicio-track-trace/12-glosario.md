# 12. Glosario

## 12.1 Términos principales

| Término | Definición |
|----------|------------|
| **Event Sourcing** | Patrón de persistencia basado en eventos |
| **CQRS** | Command Query Responsibility Segregation |
| **Event Store** | Base datos especializada en eventos |
| **Timeline** | Secuencia cronológica de eventos |
| **Deduplicación** | Prevención de eventos duplicados |
| **Snapshot** | Estado agregado en punto temporal |
| **Projection** | Vista materializada de eventos |
| **Command** | Operación que modifica estado |
| **Query** | Operación de consulta sin efectos |
| **Multi-tenant** | Soporte múltiples organizaciones |

## 12.2 Acrónimos

| Acrónimo | Significado |
|-----------|-------------|
| **CQRS** | Command Query Responsibility Segregation |
| **ES** | Event Sourcing |
| **API** | Application Programming Interface |
| **CDC** | Change Data Capture |
| **GraphQL** | Graph Query Language |

Diccionario completo de términos técnicos y de negocio utilizados en el **Sistema de Track & Trace** corporativo.

*[INSERTAR AQUÍ: Diagrama C4 - Track & Trace System Terminology]*

## A

**Aggregate**: Patrón DDD que representa una entidad raíz que mantiene consistencia transaccional y actúa como unidad de persistencia en Event Sourcing. En Track & Trace, ejemplos incluyen Flight, Shipment, o OperationalEvent.

**Append-Only Store**: Característica fundamental del Event Store donde los eventos solo pueden ser agregados, nunca modificados o eliminados, garantizando inmutabilidad y auditabilidad completa.

**At-least-once Delivery**: Garantía de entrega en sistemas distribuidos donde un mensaje puede ser entregado múltiples veces pero nunca perdido, requiriendo idempotencia en los handlers.

**Audit Trail**: Registro cronológico inmutable de todas las acciones y cambios en el sistema, crítico para compliance regulatorio y investigaciones operacionales.

**Aviation Event**: Evento específico del dominio aeronáutico como cambios de vuelo, actualizaciones de puerta, modificaciones de equipaje, etc.

## B

**Background Service**: Servicio que ejecuta tareas de larga duración o procesamiento asíncrono, como proyección de read models o procesamiento de eventos en batch.

**Bounded Context**: Límite conceptual en DDD que define el alcance donde un modelo de dominio específico es válido. Track & Trace tiene contextos como Flight Operations, Baggage Handling, y Passenger Management.

**Business Event**: Evento que representa un hecho significativo para el negocio, como "FlightDeparted", "BaggageLost", o "PassengerCheckedIn".

## C

**Causal Consistency**: Modelo de consistencia donde eventos causalmente relacionados son vistos en el mismo orden por todos los observadores, crucial para mantener la coherencia operacional.

**Checkpoint**: Marcador de posición que indica hasta qué punto han sido procesados los eventos en una proyección o read model específico.

**Circuit Breaker**: Patrón de resilencia que previene cascading failures deteniendo temporalmente llamadas a servicios que están fallando.

**Command**: Operación imperativa que representa la intención de cambiar el estado del sistema en el patrón CQRS. Ejemplos: "RecordFlightDeparture", "UpdateBaggageStatus".

**Command Handler**: Componente responsable de validar y procesar comandos, aplicando lógica de negocio y generando eventos como resultado.

**Concurrency Control**: Mecanismo para manejar acceso concurrente a datos, implementado como optimistic locking usando version numbers en eventos.

**Correlation ID**: Identificador único que permite rastrear una operación completa a través de múltiples servicios y eventos relacionados.

**CQRS**: Command Query Responsibility Segregation - Patrón arquitectónico que separa las operaciones de escritura (comandos) de las operaciones de lectura (queries).

## D

**Data Retention Policy**: Política que define cuánto tiempo se conservan diferentes tipos de eventos y datos, crucial para compliance y gestión de almacenamiento.

**Domain Event**: Evento que representa algo importante que ocurrió en el dominio de negocio y que es relevante para expertos del dominio.

**Dual Write Problem**: Problema que surge al intentar escribir en dos sistemas diferentes (ej. base de datos y message broker) sin garantías transaccionales.

**Durability**: Propiedad ACID que garantiza que los datos confirmados permanecen almacenados incluso ante fallos del sistema.

## E

**Event**: Representación inmutable de algo que ocurrió en el pasado, expresado en tiempo pasado (ej. "OrderPlaced", "FlightCancelled").

**Event Bus**: Infraestructura de comunicación que permite publicar y suscribirse a eventos de manera desacoplada.

**Event Handler**: Componente que reacciona y procesa eventos específicos, típicamente actualizando read models o ejecutando side effects.

**Event Replay**: Capacidad de re-procesar eventos históricos para reconstruir estado o actualizar proyecciones.

**Event Schema**: Definición formal de la estructura y contenido de un tipo de evento específico.

**Event Sourcing**: Patrón de persistencia donde todos los cambios de estado se almacenan como una secuencia de eventos inmutables.

**Event Store**: Base de datos especializada en almacenar eventos como secuencias append-only, actuando como única fuente de verdad.

**Event Stream**: Secuencia ordenada de eventos relacionados, típicamente agrupados por aggregate root o entidad de negocio.

**Event Versioning**: Estrategia para manejar la evolución de esquemas de eventos manteniendo compatibilidad hacia atrás.

**Eventually Consistent**: Modelo de consistencia donde el sistema alcanzará consistencia eventualmente, pero no garantiza consistencia inmediata.

**Exactly-once Delivery**: Garantía de entrega donde cada mensaje es entregado exactamente una vez, sin duplicados ni pérdidas.

## F

**Failover**: Proceso automático de cambiar a un sistema de respaldo cuando el sistema principal falla.

**Fan-out Pattern**: Patrón donde un evento se distribuye a múltiples handlers o subscribers para procesamiento paralelo.

**FIFO (First In, First Out)**: Política de ordenamiento donde el primer elemento en entrar es el primero en salir.

**Flight Event**: Eventos específicos relacionados con operaciones de vuelo como despegue, aterrizaje, cambios de puerta, etc.

## G

**Global Position**: Número secuencial único que identifica la posición de un evento en el stream global del Event Store.

**Graceful Degradation**: Capacidad del sistema de continuar funcionando con funcionalidad reducida cuando componentes fallan.

**GraphQL**: Lenguaje de consulta que permite a clientes especificar exactamente qué datos necesitan.

## H

**Health Check**: Endpoint o servicio que verifica el estado operacional de un componente del sistema.

**Hot Path**: Ruta de código que se ejecuta frecuentemente y es crítica para el rendimiento del sistema.

**Hydration**: Proceso de reconstruir el estado actual de un aggregate reproduciendo todos sus eventos históricos.

## I

**Idempotency**: Propiedad donde ejecutar la misma operación múltiples veces produce el mismo resultado.

**Infrastructure Event**: Evento técnico relacionado con la infraestructura del sistema (deployment, scaling, monitoring).

**Integration Event**: Evento diseñado para comunicación entre bounded contexts o servicios externos.

**Invariant**: Regla de negocio que debe mantenerse siempre verdadera en el sistema.

## J

**JSON Schema**: Especificación formal que define la estructura, tipos y validaciones para documentos JSON.

**JWT (JSON Web Token)**: Estándar para representar claims de manera segura entre partes.

## K

**Event Bus**: Plataforma de messaging para construir pipelines de datos en tiempo real y aplicaciones de streaming.

**Key-Value Store**: Tipo de base de datos NoSQL que almacena datos como pares clave-valor simples.

## L

**Load Balancer**: Componente que distribuye tráfico entrante entre múltiples instancias de un servicio.

**Log Compaction**: Proceso de reducir el tamaño de logs eliminando eventos obsoletos manteniendo solo el estado más reciente.

**Long-Running Process**: Proceso de negocio que puede durar días, semanas o meses, requiriendo persistencia de estado intermedio.

## M

**Materialized View**: Vista pre-calculada y persistida de datos optimizada para consultas específicas.

**Message**: Unidad de comunicación entre servicios que puede ser un comando, evento o query.

**Message Bus**: Sistema de comunicación que permite intercambio asíncrono de mensajes entre componentes.

**Microservice**: Arquitectura donde aplicaciones se componen de servicios pequeños, independientes y desplegables por separado.

**Multi-tenancy**: Arquitectura donde una instancia de software sirve múltiples clientes (tenants) manteniendo aislamiento de datos.

## O

**Operational Event**: Evento relacionado con operaciones aeroportuarias como movimientos de aeronaves, gestión de equipaje, etc.

**Optimistic Concurrency Control**: Control de concurrencia que asume que conflictos son raros y verifica al confirmar cambios.

**Outbox Pattern**: Patrón que garantiza publicación confiable de eventos usando transacciones locales.

## P

**Partition**: División lógica de datos en sistemas distribuidos para mejorar escalabilidad y rendimiento.

**Pessimistic Locking**: Control de concurrencia que bloquea recursos preventivamente para evitar conflictos.

**Poison Message**: Mensaje que causa fallo repetido en su procesamiento, típicamente enviado a Dead Letter Queue.

**Projection**: Read model derivado de eventos que optimiza consultas específicas.

**Publisher**: Componente que emite eventos o mensajes a otros componentes del sistema.

## Q

**Query**: Operación de solo lectura que retorna datos sin modificar el estado del sistema.

**Query Handler**: Componente responsable de procesar queries específicas y retornar resultados.

**Queue**: Estructura de datos FIFO usada para comunicación asíncrona entre componentes.

## R

**Read Model**: Modelo de datos optimizado para consultas específicas, derivado de eventos del Event Store.

**Read Replica**: Copia de solo lectura de una base de datos para distribuir carga de consultas.

**Replay**: Proceso de re-ejecutar eventos históricos para reconstruir estado o actualizar proyecciones.

**Repository**: Patrón que encapsula lógica de acceso a datos proporcionando interfaz collection-like.

**Resilience**: Capacidad del sistema de recuperarse rápidamente de fallos y continuar operando.

**Retry Policy**: Configuración que define cómo y cuántas veces reintentar operaciones fallidas.

## S

**Saga**: Patrón para manejar transacciones distribuidas usando secuencia de transacciones locales compensables.

**Schema Evolution**: Proceso de modificar esquemas de eventos manteniendo compatibilidad hacia atrás.

**Sharding**: Particionamiento horizontal de datos distribuyendo filas de tabla entre múltiples bases de datos.

**Side Effect**: Operación adicional que ocurre como resultado de procesar un evento (envío de email, llamada API).

**Snapshot**: Optimización que almacena estado actual de un aggregate para evitar replay completo de eventos.

**Stream**: Secuencia ordenada de eventos relacionados lógicamente, típicamente por aggregate ID.

**Subscriber**: Componente que se registra para recibir y procesar tipos específicos de eventos.

## T

**Temporal Query**: Consulta que retorna el estado del sistema en un punto específico del tiempo.

**Timeline**: Vista cronológica de eventos relacionados con una entidad específica.

**Capacidad de procesamiento**: Número de operaciones o eventos procesados por unidad de tiempo.

**Tombstone**: Marcador especial que indica eliminación lógica de datos en sistemas inmutables.

**Transaction**: Unidad de trabajo que debe completarse completamente o no ejecutarse en absoluto.

**Transactional Outbox**: Tabla de base de datos usada para garantizar publicación confiable de eventos.

## U

**Upcasting**: Proceso de convertir eventos de versiones anteriores a versiones más recientes.

**UUID (Universally Unique Identifier)**: Identificador de 128 bits garantizando unicidad global.

## V

**Versioning**: Estrategia para manejar cambios en esquemas de datos manteniendo compatibilidad.

**Version Vector**: Mecanismo para rastrear versiones en sistemas distribuidos.

## W

**Watermark**: Marcador temporal usado para determinar cuándo datos pueden considerarse completos.

**Write Model**: Modelo de datos optimizado para operaciones de escritura en arquitectura CQRS.

## Términos de dominio específico

### Operaciones Aeroportuarias

**Aircraft Turnaround**: Proceso completo de servicio de una aeronave entre llegada y siguiente partida.

**Baggage Handling Event**: Eventos relacionados con procesamiento de equipaje (check-in, sorting, loading, unloading).

**Flight Leg**: Segmento de vuelo entre dos aeropuertos específicos.

**Gate Assignment**: Asignación de puerta de embarque a un vuelo específico.

**Ground Handling**: Servicios terrestres proporcionados a aeronaves (catering, combustible, limpieza).

**Hub Operations**: Operaciones en aeropuertos centrales donde pasajeros y carga hacen conexiones.

**Passenger Processing Event**: Eventos relacionados con procesamiento de pasajeros (check-in, security, boarding).

**Ramp Operations**: Actividades en la plataforma del aeropuerto (marshalling, pushback, towing).

**Slot Management**: Gestión de franjas horarias para despegues y aterrizajes.

**Turnaround Time**: Tiempo entre llegada y partida de una aeronave.

### Compliance y Regulaciones

**GDPR Compliance**: Cumplimiento con el Reglamento General de Protección de Datos europeo.

**IATA Standards**: Estándares de la Asociación Internacional de Transporte Aéreo.

**Regulatory Event**: Evento requerido por regulaciones para auditoría y compliance.

**SOX Compliance**: Cumplimiento con la Ley Sarbanes-Oxley para controles financieros.

## Métricas y KPIs

**Disponibilidad**: Porcentaje de tiempo que el sistema está operacional y accesible.

**Error Rate**: Porcentaje de operaciones que resultan en error.

**Latency**: Tiempo requerido para procesar una operación individual.

**Mean Time Between Failures (MTBF)**: Tiempo promedio entre fallos del sistema.

**Mean Time To Recovery (MTTR)**: Tiempo promedio para recuperarse de un fallo.

**Recovery Point Objective (RPO)**: Máxima cantidad de datos que es aceptable perder.

**Recovery Time Objective (RTO)**: Tiempo máximo aceptable para restaurar servicio después de fallo.

**Service Level Agreement (SLA)**: Compromiso formal de nivel de servicio entre proveedor y cliente.

**Capacidad de procesamiento**: Número de operaciones procesadas por unidad de tiempo.

**Uptime**: Tiempo durante el cual el sistema está funcionando y disponible.

---

## Referencias y estándares

- **CloudEvents**: Especificación para describir eventos de manera común
- **OpenTelemetry**: Framework para observabilidad (traces, metrics, logs)
- **Event Storming**: Técnica para explorar dominios complejos usando eventos
- **C4 Model**: Modelo para documentar arquitectura de software
- **Arc42**: Template para documentación de arquitectura
- **DDD**: Domain-Driven Design methodology
- **CQRS**: Command Query Responsibility Segregation pattern
- **Event Sourcing**: Persistence pattern using events as source of truth

Este glosario sirve como referencia central para todo el equipo, facilitando comunicación clara entre desarrolladores, arquitectos, y stakeholders de negocio.

**Domain Event**: Evento que captura algo significativo que ocurrió en el dominio del negocio, como "FlightDelayed" o "SecurityCheckCompleted".

**Domain-Driven Design (DDD)**: Enfoque de desarrollo de software centrado en el dominio del negocio y su lógica compleja.

**Durability**: Garantía de que una vez que un evento es persistido, permanecerá almacenado incluso ante fallos del sistema.

## E

**Event**: Hecho inmutable que representa un cambio de estado que ocurrió en un momento específico en el tiempo, almacenado permanentemente en el Event Store.

**Event Bus**: Infrastructure component que maneja la publicación y distribución de eventos entre diferentes componentes y servicios.

**Correlación de Eventos**: Proceso de asociar eventos relacionados basándose en identificadores de negocio o relaciones causales.

**Event Handler**: Componente que procesa eventos específicos para actualizar read models, enviar notificaciones o ejecutar side effects.

**Event Sourcing**: Patrón arquitectónico donde el estado se deriva completamente de una secuencia inmutable de eventos, proporcionando auditabilidad completa.

**Event Store**: Base de datos especializada en almacenar eventos de forma inmutable, ordenada y eficiente para append operations.

**Event Stream**: Secuencia ordenada cronológicamente de eventos para una entidad o aggregate específico.

**Event Upcasting**: Proceso de convertir eventos de versiones anteriores a formatos más recientes para mantener compatibilidad backward.

**Eventual Consistency**: Modelo de consistencia donde el sistema alcanzará un estado consistente eventualmente, no inmediatamente, permitiendo alta disponibilidad.

**Exactly-once Processing**: Garantía de que cada evento es procesado exactamente una vez, evitando duplicación o pérdida de datos.

## F

**Failover**: Proceso automático de cambiar a un sistema backup cuando el sistema primario falla, minimizando downtime.

**Flight Operations**: Dominio específico que maneja todos los eventos relacionados con operaciones de vuelo como departures, arrivals, delays, y cancellations.

## G

**Global Event Ordering**: Garantía de que todos los eventos en el sistema mantienen un orden global consistente, crucial para operaciones de audit.

**GDPR Compliance**: Conformidad con el General Data Protection Regulation europeo, requiriendo capabilities como right to be forgotten y data portability.

## H

**High Disponibilidad (HA)**: Característica del sistema que garantiza disponibilidad continua mediante redundancia y failover automático.

**Historical Query**: Consulta que permite examinar el estado del sistema en cualquier punto temporal pasado, posible gracias a Event Sourcing.

**Hot Standby**: Sistema backup que está activo y sincronizado, listo para tomar control inmediatamente sin pérdida de datos.

## I

**Idempotence**: Propiedad donde múltiples ejecuciones de la misma operación producen el mismo resultado, esencial para at-least-once delivery.

**Immutable Event**: Evento que una vez creado no puede ser modificado, garantizando integridad del audit trail.

**Integration Event**: Evento publicado para comunicar cambios importantes a otros bounded contexts, servicios externos o sistemas legacy.

**IATA Standards**: Estándares internacionales de la International Air Transport Association que rigen formatos de datos y procedimientos aeronáuticos.

## J

**JSON Event Format**: Formato de serialización utilizado para almacenar eventos, proporcionando flexibilidad y legibilidad humana.

**Just-in-Time Processing**: Estrategia de procesamiento donde los read models se construyen on-demand en lugar de mantenerlos pre-computados.

## K

**Event Bus Integration**: Integración con Event Bus para streaming de eventos en tiempo real y comunicación asíncrona entre servicios.

**Key-Value Projection**: Tipo de read model que almacena datos en formato clave-valor optimizado para consultas de lookup rápidas.

## L

**Lag Monitoring**: Supervisión continua del retraso entre la escritura de eventos y su procesamiento en read models.

**Legal Hold**: Estado especial donde ciertos datos no pueden ser eliminados debido a investigaciones legales o requirements regulatorios.

**Balanceador de Carga**: Distribución de carga entre múltiples instancias de la aplicación para optimizar performance y disponibilidad.

## M

**Message Broker**: Sistema intermediario que facilita la comunicación asíncrona entre diferentes componentes mediante colas de mensajes.

**Multi-tenant Architecture**: Diseño donde una sola instancia del sistema sirve a múltiples organizaciones (tenants) con completo aislamiento de datos.

**Materialized View**: Read model pre-computado y almacenado que optimiza consultas específicas sacrificando freshness por performance.

## N

**Near Real-time Processing**: Procesamiento que ocurre con latencia muy baja (segundos) pero no instantáneamente, balanceando performance y consistencia.

**Non-functional Requirements**: Requisitos que especifican criteria de calidad como performance, reliability, y security en lugar de funcionalidad específica.

## O

**Operational Event**: Evento relacionado con operaciones aeroportuarias diarias como check-ins, security screenings, boarding, y ground handling.

**Optimistic Locking**: Estrategia de control de concurrencia que asume que los conflictos son raros y valida al momento del commit.

**Outbox Pattern**: Patrón para garantizar consistencia entre database writes y message publishing usando transacciones locales.

## P

**Partition Key**: Clave utilizada para distribuir eventos across multiple partitions, típicamente tenant ID o entity ID para locality.

**Performance Monitoring**: Supervisión continua de métricas de performance como latency, capacidad de procesamiento, y resource utilization.

**Point-in-Time Recovery**: Capacidad de restaurar el sistema a cualquier momento específico en el pasado usando el event log.

**Projection**: Proceso de transformar eventos en read models optimizados para consultas específicas.

**Publisher-Subscriber Pattern**: Patrón de messaging donde publishers envían eventos sin conocer los subscribers específicos.

## Q

**Query Model**: Estructura de datos optimizada para operaciones de lectura, separada del modelo de escritura en CQRS.

**Query Side**: Parte del sistema CQRS responsable de manejar operaciones de lectura usando read models proyectados.

**Queue Depth**: Métrica que indica cuántos mensajes están esperando ser procesados en una cola, importante para monitoring.

## R

**Read Model**: Vista materializada de datos proyectada desde eventos, optimizada para consultas específicas de la aplicación.

**Read Replica**: Copia read-only de la base de datos que permite distribuir carga de consultas y mejorar performance.

**Real-time Dashboard**: Interface que muestra datos operacionales actualizados en tiempo real para toma de decisiones.

**Replay**: Capacidad de re-procesar eventos históricos para reconstruir read models o debugging.

**Resilience Pattern**: Conjunto de patterns como circuit breaker, retry, y timeout que aumentan la robustez del sistema.

**RTO/RPO**: Recovery Time Objective y Recovery Point Objective - métricas que definen tolerancia a downtime y pérdida de datos.

## S

**Saga Pattern**: Patrón para manejar transacciones distribuidas de larga duración usando secuencias de transacciones locales.

**Scalability**: Capacidad del sistema de manejar cargas de trabajo crecientes mediante scaling horizontal o vertical.

**Sequence Number**: Número que indica el orden de eventos dentro de un stream específico, usado para optimistic concurrency control.

**Service Level Agreement (SLA)**: Contrato que define niveles esperados de performance, disponibilidad, y otros metrics de calidad.

**Snapshot**: Estado consolidado de un aggregate en un punto específico en el tiempo, usado para optimizar rebuilding de grandes streams.

**SITA Integration**: Integración con el sistema global SITA para intercambio de datos aeronáuticos con aerolíneas y aeropuertos worldwide.

**Stream**: Secuencia ordenada de eventos para una entidad específica, identificada por un stream ID único.

## T

**Temporal Query**: Consulta que puede examinar el estado del sistema en cualquier momento pasado, característica clave de Event Sourcing.

**Tenant Isolation**: Garantía de que los datos de diferentes organizaciones están completamente separados y protegidos.

**Capacidad de procesamiento**: Medida de cuántas operaciones puede procesar el sistema por unidad de tiempo.

**Timeline View**: Read model que presenta eventos en orden cronológico para seguimiento visual de la evolución de una entidad.

**Traceability**: Capacidad de seguir el rastro completo de un evento o proceso a través de todo el sistema.

**Two-Phase Commit**: Protocolo para garantizar consistency en transacciones distribuidas, aunque típicamente evitado en favor de eventual consistency.

## U

**Upcasting**: Proceso de migrar eventos de versiones anteriores a formatos más recientes manteniendo backward compatibility.

**User Journey**: Secuencia completa de eventos e interacciones que un usuario realiza en el sistema.

## V

**Version Control**: Sistema para manejar diferentes versiones de event schemas manteniendo compatibility y evolution paths.

**Vertical Scaling**: Estrategia de escalabilidad que aumenta la capacidad agregando más recursos (CPU, memoria) a máquinas existentes.

## W

**Write Model**: Parte del sistema CQRS optimizada para operations de escritura, enfocada en business logic y validation.

**Write-through Cache**: Estrategia de caching donde las escrituras van tanto al cache como al storage persistente simultáneamente.

## Acrónimos y Abreviaciones

| Acrónimo | Significado | Descripción |
|----------|-------------|-------------|
| **API** | Application Programming Interface | Interface para comunicación entre software components |
| **CQRS** | Command Query Responsibility Segregation | Patrón que separa read y write operations |
| **DDD** | Domain-Driven Design | Approach centrado en el business domain |
| **GDPR** | General Data Protection Regulation | Regulación europea de protección de datos |
| **IATA** | International Air Transport Association | Organización global de aerolíneas |
| **JSON** | JavaScript Object Notation | Formato de intercambio de datos |
| **JWT** | JSON Web Token | Standard para tokens de seguridad |
| **MTBF** | Mean Time Between Failures | Métrica de reliability |
| **MTTR** | Mean Time To Recovery | Métrica de recovery time |
| **OIDC** | OpenID Connect | Standard de identity layer |
| **P95/P99** | 95th/99th Percentile | Métricas de latency distribution |
| **RLS** | Row Level Security | Seguridad a nivel de fila en bases de datos |
| **RPO** | Recovery Point Objective | Máxima pérdida de datos aceptable |
| **RTO** | Recovery Time Objective | Máximo tiempo de recovery aceptable |
| **SITA** | Société Internationale de Télécommunications Aéronautiques | Red global de comunicaciones aeronáuticas |
| **SLA** | Service Level Agreement | Acuerdo de nivel de servicio |
| **SOX** | Sarbanes-Oxley Act | Regulación de compliance financiero |
| **TLS** | Transport Layer Security | Protocolo de seguridad en transporte |
| **UUID** | Universally Unique Identifier | Identificador único universal |

## Referencias Técnicas

### Event Sourcing & CQRS
- [Event Sourcing Pattern](https://martinfowler.com/eaaDev/EventSourcing.html) - Martin Fowler
- [CQRS Journey](https://docs.microsoft.com/en-us/previous-versions/msp-n-p/jj554200(v=pandp.10)) - Microsoft Patterns & Practices
- [Event Store Documentation](https://developers.eventstore.com/) - Event Store DB

### Domain-Driven Design
- [Domain-Driven Design Reference](https://www.domainlanguage.com/ddd/reference/) - Eric Evans
- [Implementing Domain-Driven Design](https://vaughnvernon.co/?page_id=168) - Vaughn Vernon

### Aviation Industry Standards
- [IATA Standards](https://www.iata.org/en/publications/standards/) - International Air Transport Association
- [SITA Specifications](https://www.sita.aero/solutions/) - SITA Communications Network

### Architecture Patterns
- [Microservices Patterns](https://microservices.io/patterns/) - Chris Richardson
- [Enterprise Integration Patterns](https://www.enterpriseintegrationpatterns.com/) - Gregor Hohpe

### Compliance and Security
- [GDPR Compliance Guide](https://gdpr.eu/) - Official GDPR Resource
- [OAuth 2.0 Security Mejores Prácticas](https://tools.ietf.org/html/draft-ietf-oauth-security-topics) - IETF RFC

**Event Bus**: Plataforma de messaging para manejo de eventos en tiempo real.

## O

**Optimistic Concurrency Control**: Técnica que asume que las operaciones concurrentes raramente entran en conflicto.

**Operational Event**: Evento que captura actividades operacionales del negocio para propósitos de trazabilidad.

## P

**Projection**: Vista materializada generada a partir de eventos para optimizar consultas específicas.

**PostgreSQL**: Sistema de gestión de base de datos relacional usado como Event Store.

## Q

**Query**: Operación que lee datos sin modificar el estado del sistema en el patrón CQRS.

**Query Model**: Modelo de datos optimizado para consultas, también conocido como read model.

## R

**Read Model**: Vista especializada de datos optimizada para casos de uso específicos de consulta.

**Replay**: Proceso de reproducir eventos históricos para reconstruir estado o generar nuevas proyecciones.

**Redis**: Base de datos en memoria utilizada para caching distribuido.

## S

**Saga**: Patrón para manejar transacciones distribuidas a través de múltiples agregados o servicios.

**Snapshot**: Estado capturado de un agregado en un momento específico para optimizar la reconstrucción.

**Stream**: Secuencia ordenada de eventos relacionados con una entidad específica.

**Strong Consistency**: Garantía de que todas las lecturas reciben la escritura más reciente.

## T

**Timeline**: Vista cronológica de eventos relacionados con una entidad específica.

**Tenant**: Organización cliente que usa el sistema con datos completamente aislados.

**Traceability**: Capacidad de rastrear el historial completo de cambios de una entidad.

## V

**Version**: Número incremental asociado a cada evento en un stream para control de concurrencia.

**Versioning**: Estrategia para evolucionar esquemas de eventos manteniendo compatibilidad.

## Conceptos de negocio específicos

**Entity Timeline**: Representación cronológica completa de todos los eventos relacionados con una entidad operacional específica.

**Operational Tracking**: Capacidad de seguimiento completo de actividades y cambios en procesos de negocio.

**Correlación de Eventos**: Proceso de relacionar eventos que forman parte del mismo proceso de negocio.

**Audit Trail**: Rastro completo e inmutable de todas las actividades del sistema para propósitos de auditoría.

**Business Event**: Evento que tiene significado directo para el negocio y es relevante para stakeholders no técnicos.

**Performance Analytics**: Análisis de métricas derivadas de eventos operacionales para identificar tendencias y optimizaciones.

## Acrónimos técnicos

| Acrónimo | Significado | Contexto |
|----------|-------------|----------|
| ACID | Atomicity, Consistency, Isolation, Durability | Propiedades transaccionales |
| ADR | Architecture Decision Record | Documentación de decisiones |
| API | Application Programming Interface | Interfaz de servicios |
| CRUD | Create, Read, Update, Delete | Operaciones básicas |
| DDD | Domain-Driven Design | Metodología de diseño |
| ETL | Extract, Transform, Load | Procesamiento de datos |
| FIFO | First In, First Out | Orden de procesamiento |
| JSONB | JSON Binary | Tipo de dato PostgreSQL |
| JWT | JSON Web Token | Token de autenticación |
| KPI | Key Performance Indicator | Métrica de negocio |
| MTBF | Mean Time Between Failures | Métrica de confiabilidad |
| MTTR | Mean Time To Recovery | Métrica de recuperación |
| OLAP | Online Analytical Processing | Procesamiento analítico |
| OLTP | Online Transaction Processing | Procesamiento transaccional |
| REST | Representational State Transfer | Arquitectura de APIs |
| RPC | Remote Procedure Call | Llamada a procedimiento remoto |
| SLA | Service Level Agreement | Acuerdo de nivel de servicio |
| SQL | Structured Query Language | Lenguaje de consulta |
| TTL | Time To Live | Tiempo de vida de cache |
| UUID | Universally Unique Identifier | Identificador único global |

## Patrones y conceptos arquitectónicos

**Bounded Context**: Límite explícito dentro del cual un modelo de dominio es aplicable.

**Circuit Breaker**: Patrón que previene llamadas a servicios que están fallando.

**Command Handler**: Componente responsable de procesar un comando específico.

**Compensating Action**: Acción que deshace los efectos de una operación previa.

**Event Handler**: Componente que reacciona a eventos específicos.

**Message Bus**: Infraestructura para el intercambio asíncrono de mensajes.

**Query Handler**: Componente responsable de procesar una consulta específica.

**Repository**: Abstracción para acceso a datos que encapsula la lógica de persistencia.

**Unit of Work**: Patrón que mantiene una lista de objetos afectados por una transacción de negocio.
