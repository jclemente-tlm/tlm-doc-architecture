# Análisis Completo: Estándares por Lineamiento
**Generado:** 2026-02-17

---

## Resumen Ejecutivo

- **Lineamientos analizados:** 36
- **Estándares existentes:** 33
- **Estándares únicos referenciados:** 63
- **Referencias totales:** 181
- **Estándares que EXISTEN:** 32 ✅
- **Estándares que FALTAN:** 31 ❌

---

## Arquitectura (13 lineamientos)

### [Estilo y Enfoque Arquitectónico](arquitectura/01-estilo-y-enfoque-arquitectonico.md)

**Ubicación:** `arquitectura/01-estilo-y-enfoque-arquitectonico.md`  
**Estándares requeridos:** 2

#### ✅ Existentes (1)

- **documentacion/architecture-decision-records.md**
  - *"Documentar estilo seleccionado en ADR"*

#### ❌ Faltantes (1)

- **gobierno/architecture-review.md**
  - *"Validar coherencia entre estilo declarado y decisiones técnicas"*

---

### [Descomposición y Límites](arquitectura/02-descomposicion-y-limites.md)

**Ubicación:** `arquitectura/02-descomposicion-y-limites.md`  
**Estándares requeridos:** 3

#### ✅ Existentes (3)

- **arquitectura/bounded-contexts.md**
  - *"Identificar límites por capacidad de negocio, no por tecnología"*
- **arquitectura/bounded-contexts.md**#9-single-responsibility-principle
  - *"Definir responsabilidad única y clara por componente"*
- **arquitectura/dependency-management.md**
  - *"Evitar dependencias cíclicas entre componentes"*

---

### [Cloud Native](arquitectura/03-cloud-native.md)

**Ubicación:** `arquitectura/03-cloud-native.md`  
**Estándares requeridos:** 6

#### ✅ Existentes (6)

- **infraestructura/externalize-configuration.md**
  - *"Externalizar configuración en variables de entorno"*
- **arquitectura/bounded-contexts.md**#12-diseño-stateless
  - *"Diseñar servicios stateless con estado en backing services"*
- **observabilidad/observability.md**#8-health-checks
  - *"Implementar health checks liveness y readiness"*
- **arquitectura/bounded-contexts.md**#13-escalabilidad-horizontal
  - *"Preparar servicios para escalabilidad horizontal"*
- **arquitectura/resilience-patterns.md**#8-graceful-shutdown
  - *"Aplicar graceful shutdown para terminación ordenada"*
- **infraestructura/aws-cost-optimization.md**
  - *"Optimizar costos mediante tagging, alertas y rightsizing"*

---

### [Resiliencia y Disponibilidad](arquitectura/04-resiliencia-y-disponibilidad.md)

**Ubicación:** `arquitectura/04-resiliencia-y-disponibilidad.md`  
**Estándares requeridos:** 6

#### ✅ Existentes (6)

- **arquitectura/resilience-patterns.md**#4-circuit-breaker
  - *"Implementar circuit breakers para dependencias externas"*
- **arquitectura/resilience-patterns.md**#7-timeouts
  - *"Aplicar timeouts apropiados en llamadas remotas"*
- **arquitectura/resilience-patterns.md**#5-retry-pattern
  - *"Configurar retry con backoff exponencial"*
- **arquitectura/resilience-patterns.md**#6-graceful-degradation
  - *"Diseñar degradación graceful ante fallos"*
- **observabilidad/observability.md**#10-slos-y-slas
  - *"Definir SLOs y SLAs documentados"*
- **mensajeria/kafka-messaging.md**
  - *"Implementar Dead Letter Queue para mensajes fallidos"*

---

### [Escalabilidad y Rendimiento](arquitectura/05-escalabilidad-y-rendimiento.md)

**Ubicación:** `arquitectura/05-escalabilidad-y-rendimiento.md`  
**Estándares requeridos:** 6

#### ✅ Existentes (2)

- **arquitectura/bounded-contexts.md**#12-diseño-stateless
  - *"Diseñar servicios stateless para escalado horizontal"*
- **observabilidad/observability.md**
  - *"Monitorear métricas de rendimiento (latencia P95, throughput, errores)"*

#### ❌ Faltantes (4)

- **infraestructura/auto-scaling.md**
  - *"Implementar auto-scaling basado en métricas"*
- **arquitectura/caching-strategies.md**
  - *"Aplicar caché distribuido para datos frecuentes"*
- **mensajeria/async-messaging.md**
  - *"Mover operaciones costosas a procesamiento asíncrono"*
- **datos/database-optimization.md**
  - *"Optimizar consultas de base de datos con índices apropiados"*

---

### [Observabilidad](arquitectura/06-observabilidad.md)

**Ubicación:** `arquitectura/06-observabilidad.md`  
**Estándares requeridos:** 5

#### ✅ Existentes (5)

- **observabilidad/observability.md**#2-logging
  - *"Generar logs estructurados en formato JSON"*
- **observabilidad/observability.md**#3-métricas
  - *"Emitir métricas siguiendo metodología RED/USE"*
- **observabilidad/observability.md**#4-trazas-distribuidas
  - *"Implementar trazas distribuidas con W3C Trace Context"*
- **observabilidad/observability.md**
  - *"Usar identificadores de correlación entre servicios"*
- **observabilidad/observability.md**
  - *"Configurar health checks para orquestadores"*

---

### [APIs y Contratos de Integración](arquitectura/07-apis-y-contratos.md)

**Ubicación:** `arquitectura/07-apis-y-contratos.md`  
**Estándares requeridos:** 9

#### ✅ Existentes (9)

- **apis/api-rest-standards.md**
  - *"Seguir convenciones RESTful para recursos y verbos HTTP"*
- **apis/api-rest-standards.md**#6-versionado-de-apis
  - *"Implementar versionado explícito en URL o header"*
- **apis/api-rest-standards.md**#8-paginación
  - *"Aplicar rate limiting y paginación en colecciones"*
- **apis/api-rest-standards.md**#9-manejo-de-errores
  - *"Estandarizar manejo de errores con estructura consistente"*
- **apis/api-rest-standards.md**#11-documentación-openapiswagger
  - *"Definir contratos con especificaciones estándar OpenAPI 3.0+"*
- **mensajeria/kafka-messaging.md**
  - *"Documentar APIs asíncronas con AsyncAPI"*
- **apis/api-rest-standards.md**
  - *"Validar requests/responses contra contratos en runtime"*
- **apis/api-rest-standards.md**#6-versionado-de-apis
  - *"Mantener retrocompatibilidad durante deprecación"*
- **testing/testing-standards.md**#contract-tests
  - *"Implementar contract testing automatizado (Pact)"*

---

### [Comunicación Asíncrona y Eventos](arquitectura/08-comunicacion-asincrona-y-eventos.md)

**Ubicación:** `arquitectura/08-comunicacion-asincrona-y-eventos.md`  
**Estándares requeridos:** 7

#### ✅ Existentes (7)

- **mensajeria/kafka-messaging.md**
  - *"Implementar mensajería con Apache Kafka"*
- **mensajeria/kafka-messaging.md**
  - *"Definir esquemas de eventos con AsyncAPI o JSON Schema"*
- **mensajeria/kafka-messaging.md**
  - *"Usar eventos para comunicar hechos del dominio, no comandos"*
- **mensajeria/kafka-messaging.md**
  - *"Implementar idempotencia en consumidores"*
- **mensajeria/kafka-messaging.md**
  - *"Garantizar entrega at-least-once o exactly-once"*
- **mensajeria/kafka-messaging.md**
  - *"Configurar Dead Letter Queue para mensajes fallidos"*
- **mensajeria/kafka-messaging.md**
  - *"Documentar topología de eventos y consumidores"*

---

### [Modelado de Dominio](arquitectura/09-modelado-de-dominio.md)

**Ubicación:** `arquitectura/09-modelado-de-dominio.md`  
**Estándares requeridos:** 5

#### ✅ Existentes (5)

- **arquitectura/bounded-contexts.md**
  - *"Identificar bounded contexts por capacidades de negocio"*
- **arquitectura/bounded-contexts.md**#lenguaje-ubicuo
  - *"Definir lenguaje ubicuo compartido con el negocio"*
- **arquitectura/bounded-contexts.md**
  - *"Asignar responsabilidades según capacidades del dominio"*
- **documentacion/c4-model.md**
  - *"Documentar modelo de dominio en diagramas de contexto"*
- **arquitectura/bounded-contexts.md**#9-single-responsibility-principle
  - *"Evitar mezclar lógicas de dominios distintos"*

---

### [Autonomía de Servicios](arquitectura/10-autonomia-de-servicios.md)

**Ubicación:** `arquitectura/10-autonomia-de-servicios.md`  
**Estándares requeridos:** 5

#### ✅ Existentes (1)

- **arquitectura/resilience-patterns.md**
  - *"Implementar modo degradado ante fallos de dependencias"*

#### ❌ Faltantes (4)

- **datos/database-per-service.md**
  - *"Implementar ownership completo de datos por servicio"*
- **desarrollo/independent-deployment.md**
  - *"Habilitar despliegue independiente sin coordinación"*
- **mensajeria/async-messaging.md**
  - *"Utilizar comunicación asíncrona cuando sea posible"*
- **apis/api-versioning.md**
  - *"Definir contratos de API versionados"*

---

### [Arquitectura Limpia](arquitectura/11-arquitectura-limpia.md)

**Ubicación:** `arquitectura/11-arquitectura-limpia.md`  
**Estándares requeridos:** 5

#### ✅ Existentes (3)

- **arquitectura/bounded-contexts.md**
  - *"Separar lógica de negocio de frameworks e infraestructura"*
- **arquitectura/bounded-contexts.md**
  - *"Estructurar sistema reflejando prioridades del negocio"*
- **documentacion/c4-model.md**
  - *"Documentar capas y responsabilidades arquitectónicas"*

#### ❌ Faltantes (2)

- **arquitectura/dependency-inversion.md**
  - *"Orientar dependencias hacia el dominio, no hacia detalles técnicos"*
- **arquitectura/hexagonal-architecture.md**
  - *"Limitar impacto de cambios tecnológicos en el núcleo del sistema"*

---

### [Arquitectura Evolutiva](arquitectura/12-arquitectura-evolutiva.md)

**Ubicación:** `arquitectura/12-arquitectura-evolutiva.md`  
**Estándares requeridos:** 5

#### ✅ Existentes (2)

- **arquitectura/bounded-contexts.md**
  - *"Priorizar reversibilidad en decisiones técnicas"*
- **arquitectura/bounded-contexts.md**
  - *"Definir contratos y límites para contener impacto del cambio"*

#### ❌ Faltantes (3)

- **documentacion/adr-template.md**
  - *"Documentar decisiones arquitectónicas con ADRs"*
- **gobierno/architecture-review.md**
  - *"Revisar y ajustar decisiones arquitectónicas periódicamente"*
- **desarrollo/refactoring-practices.md**
  - *"Implementar refactorización y mejora continua"*

---

### [Simplicidad Intencional](arquitectura/13-simplicidad-intencional.md)

**Ubicación:** `arquitectura/13-simplicidad-intencional.md`  
**Estándares requeridos:** 5

#### ✅ Existentes (2)

- **arquitectura/bounded-contexts.md**
  - *"Minimizar dependencias innecesarias entre componentes"*
- **observabilidad/observability.md**
  - *"Facilitar operación, monitoreo y evolución del sistema"*

#### ❌ Faltantes (3)

- **arquitectura/complexity-analysis.md**
  - *"Introducir complejidad solo con beneficio claro y medible"*
- **documentacion/adr-template.md**
  - *"Documentar decisiones arquitectónicas de forma comprensible"*
- **arquitectura/technology-selection.md**
  - *"Preferir soluciones conocidas y estables sobre enfoques novedosos"*

---

## Datos (3 lineamientos)

### [Datos por Dominio](datos/01-datos-por-dominio.md)

**Ubicación:** `datos/01-datos-por-dominio.md`  
**Estándares requeridos:** 9

#### ✅ Existentes (9)

- **datos/database-standards.md**
  - *"Asignar propiedad exclusiva de datos por dominio (database per service)"*
- **datos/database-standards.md**
  - *"Evitar bases de datos compartidas entre servicios"*
- **arquitectura/bounded-contexts.md**
  - *"Exponer datos mediante APIs o eventos, no acceso directo a BD"*
- **datos/database-standards.md**#4-requisitos-obligatorios
  - *"Versionar esquemas de BD con migraciones automatizadas (Flyway/Liquibase)"*
- **mensajeria/kafka-messaging.md**
  - *"Documentar esquemas de eventos con JSON Schema o AsyncAPI"*
- **datos/database-standards.md**
  - *"Validar datos contra esquemas antes de persistir"*
- **datos/database-standards.md**
  - *"Gestionar cambios con estrategias expand-contract (backward compatible)"*
- **mensajeria/kafka-messaging.md**
  - *"Mantener retrocompatibilidad en eventos y APIs de datos"*
- **arquitectura/bounded-contexts.md**
  - *"Documentar propiedad y lifecycle de datos por dominio"*

---

### [Consistencia y Sincronización](datos/02-consistencia-y-sincronizacion.md)

**Ubicación:** `datos/02-consistencia-y-sincronizacion.md`  
**Estándares requeridos:** 4

#### ✅ Existentes (4)

- **datos/database-standards.md**
  - *"Definir modelo de consistencia explícito por caso de uso"*
- **arquitectura/saga-pattern.md**
  - *"Preferir sagas o compensaciones sobre transacciones distribuidas"*
- **mensajeria/kafka-messaging.md**
  - *"Implementar idempotencia para garantizar convergencia"*
- **mensajeria/kafka-messaging.md**
  - *"Usar eventos de dominio para sincronización eventual"*

---

### [Propiedad de Datos](datos/03-propiedad-de-datos.md)

**Ubicación:** `datos/03-propiedad-de-datos.md`  
**Estándares requeridos:** 5

#### ❌ Faltantes (5)

- **datos/database-per-service.md**
  - *"Asignar base de datos independiente por dominio/servicio"*
- **datos/no-shared-database.md**
  - *"Prohibir acceso directo a bases de datos de otros dominios"*
- **datos/data-exposure.md**
  - *"Exponer datos mediante APIs o eventos"*
- **datos/data-catalog.md**
  - *"Documentar ownership de cada conjunto de datos"*
- **datos/data-replication.md**
  - *"Gestionar replicación controlada cuando sea necesaria"*

---

## Desarrollo (4 lineamientos)

### [Calidad de Código](desarrollo/01-calidad-codigo.md)

**Ubicación:** `desarrollo/01-calidad-codigo.md`  
**Estándares requeridos:** 5

#### ✅ Existentes (5)

- **desarrollo/code-quality-review.md**
  - *"Aplicar estándares de calidad de código: análisis estático y cobertura mínima"*
- **desarrollo/code-quality-sast.md**
  - *"Implementar análisis estático de seguridad (SAST) en pipelines"*
- **desarrollo/csharp-dotnet.md**
  - *"Seguir convenciones de código C# y .NET"*
- **desarrollo/sql.md**
  - *"Aplicar buenas prácticas de desarrollo SQL"*
- **desarrollo/code-quality-review.md**#4-requisitos-obligatorios
  - *"Realizar code review obligatorio antes de merge a ramas principales"*

---

### [Estrategia de Pruebas](desarrollo/02-estrategia-pruebas.md)

**Ubicación:** `desarrollo/02-estrategia-pruebas.md`  
**Estándares requeridos:** 4

#### ❌ Faltantes (4)

- **desarrollo/testing-standards.md**
  - *"Implementar pruebas automatizadas en múltiples niveles (unitarias, integración, e2e)"*
- **desarrollo/testing-standards.md**#unit-tests
  - *"Escribir pruebas unitarias con cobertura mínima del 80%"*
- **desarrollo/testing-standards.md**#integration-tests
  - *"Implementar pruebas de integración para validar interacciones entre componentes"*
- **desarrollo/testing-standards.md**#contract-tests
  - *"Usar contract testing para validar contratos entre servicios"*

---

### [Documentación Técnica](desarrollo/03-documentacion-tecnica.md)

**Ubicación:** `desarrollo/03-documentacion-tecnica.md`  
**Estándares requeridos:** 5

#### ✅ Existentes (4)

- **documentacion/architecture-decision-records.md**
  - *"Documentar decisiones arquitectónicas significativas mediante ADRs"*
- **documentacion/arc42.md**
  - *"Documentar arquitectura de servicios con plantilla arc42"*
- **documentacion/c4-model.md**
  - *"Modelar arquitectura con notación C4 y Structurizr DSL"*
- **apis/api-rest-standards.md**
  - *"Especificar APIs con OpenAPI 3.0+"*

#### ❌ Faltantes (1)

- **desarrollo/repositorios.md**#estructura-obligatoria-del-readme
  - *"Mantener README actualizado en todos los repositorios"*

---

### [Control de Versiones](desarrollo/04-control-versiones.md)

**Ubicación:** `desarrollo/04-control-versiones.md`  
**Estándares requeridos:** 6

#### ✅ Existentes (3)

- **desarrollo/git.md**
  - *"Aplicar estándares de Git: workflows, commits y versionado"*
- **desarrollo/code-quality-review.md**#4-requisitos-obligatorios
  - *"Proteger ramas principales con políticas de merge"*
- **desarrollo/cicd-pipelines.md**
  - *"Automatizar versionado y tagging en pipelines CI/CD"*

#### ❌ Faltantes (3)

- **desarrollo/repositorios.md**#estrategia-de-branching
  - *"Usar Git workflows y estrategias de branching consistentes"*
- **desarrollo/repositorios.md**#commits-semanticos
  - *"Aplicar commits semánticos (Conventional Commits)"*
- **desarrollo/repositorios.md**#versionado-de-artefactos
  - *"Versionar artefactos con Semantic Versioning (SemVer)"*

---

## Gobierno (3 lineamientos)

### [Decisiones Arquitectónicas](gobierno/01-decisiones-arquitectonicas.md)

**Ubicación:** `gobierno/01-decisiones-arquitectonicas.md`  
**Estándares requeridos:** 2

#### ✅ Existentes (1)

- **documentacion/architecture-decision-records.md**
  - *"Documentar decisiones significativas en ADRs"*

#### ❌ Faltantes (1)

- **gobierno/architecture-review.md**
  - *"Revisar ADRs en architecture reviews"*

---

### [Revisiones Arquitectónicas](gobierno/02-revisiones-arquitectonicas.md)

**Ubicación:** `gobierno/02-revisiones-arquitectonicas.md`  
**Estándares requeridos:** 3

#### ❌ Faltantes (3)

- **gobierno/architecture-review.md**
  - *"Realizar architecture review antes de implementaciones significativas"*
- **gobierno/review-documentation.md**
  - *"Documentar resultados, decisiones y acciones de reviews"*
- **gobierno/architecture-retrospectives.md**
  - *"Realizar retrospectivas arquitectónicas post-implementación"*

---

### [Cumplimiento y Excepciones](gobierno/03-cumplimiento-y-excepciones.md)

**Ubicación:** `gobierno/03-cumplimiento-y-excepciones.md`  
**Estándares requeridos:** 2

#### ❌ Faltantes (2)

- **gobierno/compliance-validation.md**
  - *"Validar cumplimiento de lineamientos y estándares"*
- **gobierno/exception-management.md**
  - *"Gestionar excepciones mediante proceso formal con ADR"*

---

## Operabilidad (4 lineamientos)

### [CI/CD y Automatización de Despliegues](operabilidad/01-cicd-pipelines.md)

**Ubicación:** `operabilidad/01-cicd-pipelines.md`  
**Estándares requeridos:** 5

#### ✅ Existentes (5)

- **desarrollo/cicd-pipelines.md**
  - *"Automatizar despliegues mediante pipelines CI/CD"*
- **desarrollo/cicd-pipelines.md**#testing-stage
  - *"Ejecutar pruebas automatizadas en cada commit"*
- **desarrollo/cicd-pipelines.md**#security-stage
  - *"Integrar validaciones de seguridad (SAST, SCA) en pipelines"*
- **desarrollo/code-quality-review.md**
  - *"Implementar quality gates con métricas mínimas"*
- **desarrollo/cicd-pipelines.md**#deployment-strategies
  - *"Aplicar estrategias de deployment seguras (blue/green, canary)"*

---

### [Infraestructura como Código (IaC)](operabilidad/02-infraestructura-como-codigo.md)

**Ubicación:** `operabilidad/02-infraestructura-como-codigo.md`  
**Estándares requeridos:** 7

#### ✅ Existentes (6)

- **infraestructura/infrastructure-as-code.md**
  - *"Definir infraestructura mediante código declarativo (Terraform)"*
- **desarrollo/code-quality-review.md**
  - *"Aplicar code review obligatorio a cambios de infraestructura"*
- **seguridad/iac-scanning.md**
  - *"Validar seguridad de código IaC con scanning automatizado"*
- **infraestructura/infrastructure-as-code.md**#state-management
  - *"Gestionar state de forma segura y compartida"*
- **infraestructura/infrastructure-as-code.md**#workflow
  - *"Validar cambios con terraform plan antes de apply"*
- **infraestructura/infrastructure-as-code.md**#modules
  - *"Crear módulos reutilizables para recursos comunes"*

#### ❌ Faltantes (1)

- **desarrollo/repositorios.md**
  - *"Versionar código de infraestructura en repositorios Git"*

---

### [Configuración y Consistencia de Entornos](operabilidad/03-configuracion-entornos.md)

**Ubicación:** `operabilidad/03-configuracion-entornos.md`  
**Estándares requeridos:** 3

#### ✅ Existentes (3)

- **infraestructura/externalize-configuration.md**
  - *"Externalizar configuración en variables de entorno (12-Factor)"*
- **seguridad/secrets-key-management.md**
  - *"Gestionar secrets con AWS Secrets Manager"*
- **infraestructura/contenedores.md**
  - *"Contenedorizar aplicaciones para consistencia"*

---

### [Disaster Recovery y Continuidad](operabilidad/04-disaster-recovery.md)

**Ubicación:** `operabilidad/04-disaster-recovery.md`  
**Estándares requeridos:** 5

#### ❌ Faltantes (5)

- **operabilidad/disaster-recovery.md**#definicion-de-objetivos
  - *"Definir objetivos RPO/RTO para cada sistema crítico"*
- **operabilidad/disaster-recovery.md**#estrategia-de-backups
  - *"Implementar backups automatizados con retención apropiada"*
- **operabilidad/disaster-recovery.md**#pruebas-de-recuperacion
  - *"Probar procedimientos de restauración al menos trimestralmente"*
- **operabilidad/disaster-recovery.md**#documentacion-de-procedimientos
  - *"Documentar runbooks de DR actualizados y accesibles"*
- **operabilidad/disaster-recovery.md**#simulacros
  - *"Realizar simulacros de DR con equipos involucrados"*

---

## Seguridad (9 lineamientos)

### [Arquitectura Segura](seguridad/01-arquitectura-segura.md)

**Ubicación:** `seguridad/01-arquitectura-segura.md`  
**Estándares requeridos:** 5

#### ✅ Existentes (5)

- **seguridad/security-architecture.md**#5-security-by-design
  - *"Aplicar Security by Design en decisiones arquitectónicas"*
- **seguridad/threat-modeling.md**
  - *"Realizar modelado de amenazas para nuevos sistemas"*
- **seguridad/security-architecture.md**#trust-boundaries
  - *"Definir explícitamente los límites de confianza (trust boundaries)"*
- **seguridad/security-architecture.md**#7-reducción-de-superficie-de-ataque
  - *"Reducir la superficie de ataque mediante exposición controlada"*
- **seguridad/security-architecture.md**#6-defensa-en-profundidad
  - *"Aplicar defensa en profundidad con múltiples capas"*

---

### [Arquitectura Segura](seguridad/01-seguridad-desde-el-diseno.md)

**Ubicación:** `seguridad/01-seguridad-desde-el-diseno.md`  
**Estándares requeridos:** 5

#### ✅ Existentes (5)

- **seguridad/security-architecture.md**#5-security-by-design
  - *"Aplicar Security by Design en decisiones arquitectónicas"*
- **seguridad/threat-modeling.md**
  - *"Realizar modelado de amenazas para nuevos sistemas"*
- **seguridad/security-architecture.md**#trust-boundaries
  - *"Definir explícitamente los límites de confianza (trust boundaries)"*
- **seguridad/security-architecture.md**#7-reducción-de-superficie-de-ataque
  - *"Reducir la superficie de ataque mediante exposición controlada"*
- **seguridad/security-architecture.md**#6-defensa-en-profundidad
  - *"Aplicar defensa en profundidad con múltiples capas"*

---

### [Zero Trust](seguridad/02-zero-trust.md)

**Ubicación:** `seguridad/02-zero-trust.md`  
**Estándares requeridos:** 5

#### ✅ Existentes (3)

- **seguridad/network-security.md**#zero-trust
  - *"Aplicar principios Zero Trust en arquitectura de red"*
- **seguridad/security-architecture.md**#trust-boundaries
  - *"Definir límites de confianza explícitos"*
- **observabilidad/observability.md**
  - *"Implementar trazabilidad completa de interacciones"*

#### ❌ Faltantes (2)

- **seguridad/authentication.md**
  - *"Implementar autenticación explícita para toda interacción"*
- **seguridad/authorization.md**
  - *"Evaluar acceso según identidad, contexto y propósito"*

---

### [Defensa en Profundidad](seguridad/03-defensa-en-profundidad.md)

**Ubicación:** `seguridad/03-defensa-en-profundidad.md`  
**Estándares requeridos:** 5

#### ✅ Existentes (4)

- **seguridad/security-architecture.md**#7-reducción-de-superficie-de-ataque
  - *"Eliminar puntos únicos de falla en seguridad"*
- **seguridad/security-architecture.md**#6-defense-in-depth
  - *"Diseñar capas de seguridad independientes y complementarias"*
- **observabilidad/observability.md**
  - *"Facilitar detección, contención y aislamiento de incidentes"*
- **seguridad/network-security.md**
  - *"Distribuir controles en distintos niveles arquitectónicos"*

#### ❌ Faltantes (1)

- **seguridad/authorization.md**
  - *"Limitar acceso y capacidades progresivamente"*

---

### [Mínimo Privilegio](seguridad/04-minimo-privilegio.md)

**Ubicación:** `seguridad/04-minimo-privilegio.md`  
**Estándares requeridos:** 5

#### ✅ Existentes (1)

- **arquitectura/bounded-contexts.md**
  - *"Evitar componentes con acceso excesivo o transversal"*

#### ❌ Faltantes (4)

- **seguridad/authorization.md**
  - *"Definir permisos de forma explícita y granular"*
- **seguridad/rbac.md**
  - *"Otorgar accesos por necesidad, no por conveniencia"*
- **seguridad/access-review.md**
  - *"Implementar privilegios revisables, revocables y temporales"*
- **seguridad/segregation-of-duties.md**
  - *"Segregar capacidades críticas claramente"*

---

### [Identidad y Accesos](seguridad/05-identidad-y-accesos.md)

**Ubicación:** `seguridad/05-identidad-y-accesos.md`  
**Estándares requeridos:** 5

#### ✅ Existentes (5)

- **seguridad/identity-access-management.md**#4-autenticación-sso
  - *"Usar identidad federada y SSO corporativo para usuarios"*
- **seguridad/identity-access-management.md**#43-multi-factor-authentication-mfa
  - *"Implementar autenticación multifactor (MFA) para accesos críticos"*
- **seguridad/identity-access-management.md**#rbac
  - *"Aplicar mínimo privilegio en autorizaciones"*
- **seguridad/identity-access-management.md**
  - *"Gestionar identidades de servicios"*
- **seguridad/secrets-key-management.md**
  - *"No almacenar credenciales en código o configuración"*

---

### [Segmentación y Aislamiento](seguridad/06-segmentacion-y-aislamiento.md)

**Ubicación:** `seguridad/06-segmentacion-y-aislamiento.md`  
**Estándares requeridos:** 5

#### ✅ Existentes (5)

- **seguridad/network-security.md**#segmentación-y-zonas
  - *"Segmentar redes por niveles de confianza (DMZ, interna, datos)"*
- **seguridad/network-security.md**#5-ejemplo-de-infraestructura
  - *"Aislar recursos por entorno en cuentas/subscripciones separadas"*
- **seguridad/tenant-isolation.md**
  - *"Implementar aislamiento de tenants en soluciones multi-tenant"*
- **seguridad/network-security.md**#principios-zero-trust
  - *"Aplicar principio de menor exposición de red (zero trust networking)"*
- **seguridad/network-security.md**#segmentación-y-zonas
  - *"Documentar zonas de seguridad y controles entre ellas"*

---

### [Protección de Datos](seguridad/07-proteccion-de-datos.md)

**Ubicación:** `seguridad/07-proteccion-de-datos.md`  
**Estándares requeridos:** 6

#### ✅ Existentes (1)

- **seguridad/secrets-key-management.md**
  - *"Gestionar claves de cifrado con servicios dedicados (KMS)"*

#### ❌ Faltantes (5)

- **seguridad/data-protection.md**#classification
  - *"Clasificar datos según sensibilidad (público, interno, sensible, regulado)"*
- **seguridad/data-protection.md**#encryption
  - *"Cifrar datos sensibles en tránsito y reposo"*
- **seguridad/data-protection.md**
  - *"Aplicar enmascaramiento y tokenización donde corresponda"*
- **seguridad/data-protection.md**
  - *"Recopilar únicamente datos estrictamente necesarios (minimización)"*
- **seguridad/data-protection.md**
  - *"Implementar políticas de retención y eliminación automática"*

---

### [Gestión de Vulnerabilidades](seguridad/08-gestion-vulnerabilidades.md)

**Ubicación:** `seguridad/08-gestion-vulnerabilidades.md`  
**Estándares requeridos:** 6

#### ✅ Existentes (6)

- **seguridad/vulnerability-management.md**
  - *"Implementar programa integral de gestión de vulnerabilidades"*
- **seguridad/vulnerability-management.md**#3-scanning-automatizado
  - *"Implementar scanning automatizado de vulnerabilidades en CI/CD"*
- **seguridad/vulnerability-management.md**
  - *"Mantener inventario actualizado de componentes y versiones"*
- **desarrollo/package-management.md**
  - *"Gestionar dependencias y paquetes de forma segura"*
- **seguridad/container-scanning.md**
  - *"Validar imágenes de contenedores antes de deployment"*
- **seguridad/iac-scanning.md**
  - *"Validar código de infraestructura (IaC) con scanning de seguridad"*

---

## 📋 Estándares Faltantes (Lista Completa)

Total: **31** estándares únicos

### apis/ (1 archivos)

🟡 **api-versioning.md** (1 refs)
   - Autonomía de Servicios


### arquitectura/ (5 archivos)

🟡 **caching-strategies.md** (1 refs)
   - Escalabilidad y Rendimiento

🟡 **complexity-analysis.md** (1 refs)
   - Simplicidad Intencional

🟡 **dependency-inversion.md** (1 refs)
   - Arquitectura Limpia

🟡 **hexagonal-architecture.md** (1 refs)
   - Arquitectura Limpia

🟡 **technology-selection.md** (1 refs)
   - Simplicidad Intencional


### datos/ (6 archivos)

🟠 **database-per-service.md** (2 refs)
   - Autonomía de Servicios
   - Propiedad de Datos

🟡 **data-catalog.md** (1 refs)
   - Propiedad de Datos

🟡 **data-exposure.md** (1 refs)
   - Propiedad de Datos

🟡 **data-replication.md** (1 refs)
   - Propiedad de Datos

🟡 **database-optimization.md** (1 refs)
   - Escalabilidad y Rendimiento

🟡 **no-shared-database.md** (1 refs)
   - Propiedad de Datos


### desarrollo/ (4 archivos)

🔴 **repositorios.md** (5 refs)
   - Documentación Técnica
   - Control de Versiones
   - Control de Versiones
   - ... y 2 más

🔴 **testing-standards.md** (4 refs)
   - Estrategia de Pruebas
   - Estrategia de Pruebas
   - Estrategia de Pruebas
   - ... y 1 más

🟡 **independent-deployment.md** (1 refs)
   - Autonomía de Servicios

🟡 **refactoring-practices.md** (1 refs)
   - Arquitectura Evolutiva


### documentacion/ (1 archivos)

🟠 **adr-template.md** (2 refs)
   - Arquitectura Evolutiva
   - Simplicidad Intencional


### gobierno/ (5 archivos)

🔴 **architecture-review.md** (4 refs)
   - Estilo y Enfoque Arquitectónico
   - Arquitectura Evolutiva
   - Decisiones Arquitectónicas
   - ... y 1 más

🟡 **architecture-retrospectives.md** (1 refs)
   - Revisiones Arquitectónicas

🟡 **compliance-validation.md** (1 refs)
   - Cumplimiento y Excepciones

🟡 **exception-management.md** (1 refs)
   - Cumplimiento y Excepciones

🟡 **review-documentation.md** (1 refs)
   - Revisiones Arquitectónicas


### infraestructura/ (1 archivos)

🟡 **auto-scaling.md** (1 refs)
   - Escalabilidad y Rendimiento


### mensajeria/ (1 archivos)

🟠 **async-messaging.md** (2 refs)
   - Escalabilidad y Rendimiento
   - Autonomía de Servicios


### operabilidad/ (1 archivos)

🔴 **disaster-recovery.md** (5 refs)
   - Disaster Recovery y Continuidad
   - Disaster Recovery y Continuidad
   - Disaster Recovery y Continuidad
   - ... y 2 más


### seguridad/ (6 archivos)

🔴 **data-protection.md** (5 refs)
   - Protección de Datos
   - Protección de Datos
   - Protección de Datos
   - ... y 2 más

🔴 **authorization.md** (3 refs)
   - Zero Trust
   - Defensa en Profundidad
   - Mínimo Privilegio

🟡 **access-review.md** (1 refs)
   - Mínimo Privilegio

🟡 **authentication.md** (1 refs)
   - Zero Trust

🟡 **rbac.md** (1 refs)
   - Mínimo Privilegio

🟡 **segregation-of-duties.md** (1 refs)
   - Mínimo Privilegio


## 📊 Top 15 Estándares Más Referenciados

| # | Estándar | Referencias | Estado |
|---|----------|-------------|--------|
| 1 | `arquitectura/bounded-contexts.md` | 17 | ✅ Existe |
| 2 | `mensajeria/kafka-messaging.md` | 13 | ✅ Existe |
| 3 | `observabilidad/observability.md` | 11 | ✅ Existe |
| 4 | `seguridad/security-architecture.md` | 11 | ✅ Existe |
| 5 | `apis/api-rest-standards.md` | 8 | ✅ Existe |
| 6 | `arquitectura/resilience-patterns.md` | 6 | ✅ Existe |
| 7 | `datos/database-standards.md` | 6 | ✅ Existe |
| 8 | `seguridad/network-security.md` | 6 | ✅ Existe |
| 9 | `desarrollo/code-quality-review.md` | 5 | ✅ Existe |
| 10 | `desarrollo/repositorios.md` | 5 | ❌ Falta |
| 11 | `desarrollo/cicd-pipelines.md` | 5 | ✅ Existe |
| 12 | `operabilidad/disaster-recovery.md` | 5 | ❌ Falta |
| 13 | `seguridad/data-protection.md` | 5 | ❌ Falta |
| 14 | `gobierno/architecture-review.md` | 4 | ❌ Falta |
| 15 | `desarrollo/testing-standards.md` | 4 | ❌ Falta |

---

**Generado automáticamente por script de análisis**
