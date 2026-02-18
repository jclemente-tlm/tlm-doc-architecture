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
  - _"Documentar estilo seleccionado en ADR"_

#### ❌ Faltantes (1)

- **gobierno/architecture-review.md**
  - _"Validar coherencia entre estilo declarado y decisiones técnicas"_

---

### [Descomposición y Límites](arquitectura/02-descomposicion-y-limites.md)

**Ubicación:** `arquitectura/02-descomposicion-y-limites.md`
**Estándares requeridos:** 3

#### ✅ Existentes (3)

- **arquitectura/bounded-contexts.md**
  - _"Identificar límites por capacidad de negocio, no por tecnología"_
- **arquitectura/bounded-contexts.md**#9-single-responsibility-principle
  - _"Definir responsabilidad única y clara por componente"_
- **arquitectura/dependency-management.md**
  - _"Evitar dependencias cíclicas entre componentes"_

---

### [Cloud Native](arquitectura/03-cloud-native.md)

**Ubicación:** `arquitectura/03-cloud-native.md`
**Estándares requeridos:** 6

#### ✅ Existentes (6)

- **infraestructura/externalize-configuration.md**
  - _"Externalizar configuración en variables de entorno"_
- **arquitectura/bounded-contexts.md**#12-diseño-stateless
  - _"Diseñar servicios stateless con estado en backing services"_
- **observabilidad/observability.md**#8-health-checks
  - _"Implementar health checks liveness y readiness"_
- **arquitectura/bounded-contexts.md**#13-escalabilidad-horizontal
  - _"Preparar servicios para escalabilidad horizontal"_
- **arquitectura/resilience-patterns.md**#8-graceful-shutdown
  - _"Aplicar graceful shutdown para terminación ordenada"_
- **infraestructura/aws-cost-optimization.md**
  - _"Optimizar costos mediante tagging, alertas y rightsizing"_

---

### [Resiliencia y Disponibilidad](arquitectura/04-resiliencia-y-disponibilidad.md)

**Ubicación:** `arquitectura/04-resiliencia-y-disponibilidad.md`
**Estándares requeridos:** 6

#### ✅ Existentes (6)

- **arquitectura/resilience-patterns.md**#4-circuit-breaker
  - _"Implementar circuit breakers para dependencias externas"_
- **arquitectura/resilience-patterns.md**#7-timeouts
  - _"Aplicar timeouts apropiados en llamadas remotas"_
- **arquitectura/resilience-patterns.md**#5-retry-pattern
  - _"Configurar retry con backoff exponencial"_
- **arquitectura/resilience-patterns.md**#6-graceful-degradation
  - _"Diseñar degradación graceful ante fallos"_
- **observabilidad/observability.md**#10-slos-y-slas
  - _"Definir SLOs y SLAs documentados"_
- **mensajeria/kafka-messaging.md**
  - _"Implementar Dead Letter Queue para mensajes fallidos"_

---

### [Escalabilidad y Rendimiento](arquitectura/05-escalabilidad-y-rendimiento.md)

**Ubicación:** `arquitectura/05-escalabilidad-y-rendimiento.md`
**Estándares requeridos:** 6

#### ✅ Existentes (2)

- **arquitectura/bounded-contexts.md**#12-diseño-stateless
  - _"Diseñar servicios stateless para escalado horizontal"_
- **observabilidad/observability.md**
  - _"Monitorear métricas de rendimiento (latencia P95, throughput, errores)"_

#### ❌ Faltantes (4)

- **infraestructura/auto-scaling.md**
  - _"Implementar auto-scaling basado en métricas"_
- **arquitectura/caching-strategies.md**
  - _"Aplicar caché distribuido para datos frecuentes"_
- **mensajeria/async-messaging.md**
  - _"Mover operaciones costosas a procesamiento asíncrono"_
- **datos/database-optimization.md**
  - _"Optimizar consultas de base de datos con índices apropiados"_

---

### [Observabilidad](arquitectura/06-observabilidad.md)

**Ubicación:** `arquitectura/06-observabilidad.md`
**Estándares requeridos:** 5

#### ✅ Existentes (5)

- **observabilidad/observability.md**#2-logging
  - _"Generar logs estructurados en formato JSON"_
- **observabilidad/observability.md**#3-métricas
  - _"Emitir métricas siguiendo metodología RED/USE"_
- **observabilidad/observability.md**#4-trazas-distribuidas
  - _"Implementar trazas distribuidas con W3C Trace Context"_
- **observabilidad/observability.md**
  - _"Usar identificadores de correlación entre servicios"_
- **observabilidad/observability.md**
  - _"Configurar health checks para orquestadores"_

---

### [APIs y Contratos de Integración](arquitectura/07-apis-y-contratos.md)

**Ubicación:** `arquitectura/07-apis-y-contratos.md`
**Estándares requeridos:** 9

#### ✅ Existentes (9)

- **apis/api-rest-standards.md**
  - _"Seguir convenciones RESTful para recursos y verbos HTTP"_
- **apis/api-rest-standards.md**#6-versionado-de-apis
  - _"Implementar versionado explícito en URL o header"_
- **apis/api-rest-standards.md**#8-paginación
  - _"Aplicar rate limiting y paginación en colecciones"_
- **apis/api-rest-standards.md**#9-manejo-de-errores
  - _"Estandarizar manejo de errores con estructura consistente"_
- **apis/api-rest-standards.md**#11-documentación-openapiswagger
  - _"Definir contratos con especificaciones estándar OpenAPI 3.0+"_
- **mensajeria/kafka-messaging.md**
  - _"Documentar APIs asíncronas con AsyncAPI"_
- **apis/api-rest-standards.md**
  - _"Validar requests/responses contra contratos en runtime"_
- **apis/api-rest-standards.md**#6-versionado-de-apis
  - _"Mantener retrocompatibilidad durante deprecación"_
- **testing/testing-standards.md**#contract-tests
  - _"Implementar contract testing automatizado (Pact)"_

---

### [Comunicación Asíncrona y Eventos](arquitectura/08-comunicacion-asincrona-y-eventos.md)

**Ubicación:** `arquitectura/08-comunicacion-asincrona-y-eventos.md`
**Estándares requeridos:** 7

#### ✅ Existentes (7)

- **mensajeria/kafka-messaging.md**
  - _"Implementar mensajería con Apache Kafka"_
- **mensajeria/kafka-messaging.md**
  - _"Definir esquemas de eventos con AsyncAPI o JSON Schema"_
- **mensajeria/kafka-messaging.md**
  - _"Usar eventos para comunicar hechos del dominio, no comandos"_
- **mensajeria/kafka-messaging.md**
  - _"Implementar idempotencia en consumidores"_
- **mensajeria/kafka-messaging.md**
  - _"Garantizar entrega at-least-once o exactly-once"_
- **mensajeria/kafka-messaging.md**
  - _"Configurar Dead Letter Queue para mensajes fallidos"_
- **mensajeria/kafka-messaging.md**
  - _"Documentar topología de eventos y consumidores"_

---

### [Modelado de Dominio](arquitectura/09-modelado-de-dominio.md)

**Ubicación:** `arquitectura/09-modelado-de-dominio.md`
**Estándares requeridos:** 5

#### ✅ Existentes (5)

- **arquitectura/bounded-contexts.md**
  - _"Identificar bounded contexts por capacidades de negocio"_
- **arquitectura/bounded-contexts.md**#lenguaje-ubicuo
  - _"Definir lenguaje ubicuo compartido con el negocio"_
- **arquitectura/bounded-contexts.md**
  - _"Asignar responsabilidades según capacidades del dominio"_
- **documentacion/c4-model.md**
  - _"Documentar modelo de dominio en diagramas de contexto"_
- **arquitectura/bounded-contexts.md**#9-single-responsibility-principle
  - _"Evitar mezclar lógicas de dominios distintos"_

---

### [Autonomía de Servicios](arquitectura/10-autonomia-de-servicios.md)

**Ubicación:** `arquitectura/10-autonomia-de-servicios.md`
**Estándares requeridos:** 5

#### ✅ Existentes (1)

- **arquitectura/resilience-patterns.md**
  - _"Implementar modo degradado ante fallos de dependencias"_

#### ❌ Faltantes (4)

- **datos/database-per-service.md**
  - _"Implementar ownership completo de datos por servicio"_
- **desarrollo/independent-deployment.md**
  - _"Habilitar despliegue independiente sin coordinación"_
- **mensajeria/async-messaging.md**
  - _"Utilizar comunicación asíncrona cuando sea posible"_
- **apis/api-versioning.md**
  - _"Definir contratos de API versionados"_

---

### [Arquitectura Limpia](arquitectura/11-arquitectura-limpia.md)

**Ubicación:** `arquitectura/11-arquitectura-limpia.md`
**Estándares requeridos:** 5

#### ✅ Existentes (3)

- **arquitectura/bounded-contexts.md**
  - _"Separar lógica de negocio de frameworks e infraestructura"_
- **arquitectura/bounded-contexts.md**
  - _"Estructurar sistema reflejando prioridades del negocio"_
- **documentacion/c4-model.md**
  - _"Documentar capas y responsabilidades arquitectónicas"_

#### ❌ Faltantes (2)

- **arquitectura/dependency-inversion.md**
  - _"Orientar dependencias hacia el dominio, no hacia detalles técnicos"_
- **arquitectura/hexagonal-architecture.md**
  - _"Limitar impacto de cambios tecnológicos en el núcleo del sistema"_

---

### [Arquitectura Evolutiva](arquitectura/12-arquitectura-evolutiva.md)

**Ubicación:** `arquitectura/12-arquitectura-evolutiva.md`
**Estándares requeridos:** 5

#### ✅ Existentes (2)

- **arquitectura/bounded-contexts.md**
  - _"Priorizar reversibilidad en decisiones técnicas"_
- **arquitectura/bounded-contexts.md**
  - _"Definir contratos y límites para contener impacto del cambio"_

#### ❌ Faltantes (3)

- **documentacion/adr-template.md**
  - _"Documentar decisiones arquitectónicas con ADRs"_
- **gobierno/architecture-review.md**
  - _"Revisar y ajustar decisiones arquitectónicas periódicamente"_
- **desarrollo/refactoring-practices.md**
  - _"Implementar refactorización y mejora continua"_

---

### [Simplicidad Intencional](arquitectura/13-simplicidad-intencional.md)

**Ubicación:** `arquitectura/13-simplicidad-intencional.md`
**Estándares requeridos:** 5

#### ✅ Existentes (2)

- **arquitectura/bounded-contexts.md**
  - _"Minimizar dependencias innecesarias entre componentes"_
- **observabilidad/observability.md**
  - _"Facilitar operación, monitoreo y evolución del sistema"_

#### ❌ Faltantes (3)

- **arquitectura/complexity-analysis.md**
  - _"Introducir complejidad solo con beneficio claro y medible"_
- **documentacion/adr-template.md**
  - _"Documentar decisiones arquitectónicas de forma comprensible"_
- **arquitectura/technology-selection.md**
  - _"Preferir soluciones conocidas y estables sobre enfoques novedosos"_

---

## Datos (3 lineamientos)

### [Datos por Dominio](datos/01-datos-por-dominio.md)

**Ubicación:** `datos/01-datos-por-dominio.md`
**Estándares requeridos:** 9

#### ✅ Existentes (9)

- **datos/database-standards.md**
  - _"Asignar propiedad exclusiva de datos por dominio (database per service)"_
- **datos/database-standards.md**
  - _"Evitar bases de datos compartidas entre servicios"_
- **arquitectura/bounded-contexts.md**
  - _"Exponer datos mediante APIs o eventos, no acceso directo a BD"_
- **datos/database-standards.md**#4-requisitos-obligatorios
  - _"Versionar esquemas de BD con migraciones automatizadas (Flyway/Liquibase)"_
- **mensajeria/kafka-messaging.md**
  - _"Documentar esquemas de eventos con JSON Schema o AsyncAPI"_
- **datos/database-standards.md**
  - _"Validar datos contra esquemas antes de persistir"_
- **datos/database-standards.md**
  - _"Gestionar cambios con estrategias expand-contract (backward compatible)"_
- **mensajeria/kafka-messaging.md**
  - _"Mantener retrocompatibilidad en eventos y APIs de datos"_
- **arquitectura/bounded-contexts.md**
  - _"Documentar propiedad y lifecycle de datos por dominio"_

---

### [Consistencia y Sincronización](datos/02-consistencia-y-sincronizacion.md)

**Ubicación:** `datos/02-consistencia-y-sincronizacion.md`
**Estándares requeridos:** 4

#### ✅ Existentes (4)

- **datos/database-standards.md**
  - _"Definir modelo de consistencia explícito por caso de uso"_
- **arquitectura/saga-pattern.md**
  - _"Preferir sagas o compensaciones sobre transacciones distribuidas"_
- **mensajeria/kafka-messaging.md**
  - _"Implementar idempotencia para garantizar convergencia"_
- **mensajeria/kafka-messaging.md**
  - _"Usar eventos de dominio para sincronización eventual"_

---

### [Propiedad de Datos](datos/03-propiedad-de-datos.md)

**Ubicación:** `datos/03-propiedad-de-datos.md`
**Estándares requeridos:** 5

#### ❌ Faltantes (5)

- **datos/database-per-service.md**
  - _"Asignar base de datos independiente por dominio/servicio"_
- **datos/no-shared-database.md**
  - _"Prohibir acceso directo a bases de datos de otros dominios"_
- **datos/data-exposure.md**
  - _"Exponer datos mediante APIs o eventos"_
- **datos/data-catalog.md**
  - _"Documentar ownership de cada conjunto de datos"_
- **datos/data-replication.md**
  - _"Gestionar replicación controlada cuando sea necesaria"_

---

## Desarrollo (4 lineamientos)

### [Calidad de Código](desarrollo/01-calidad-codigo.md)

**Ubicación:** `desarrollo/01-calidad-codigo.md`
**Estándares requeridos:** 5

#### ✅ Existentes (5)

- **desarrollo/code-quality-review.md**
  - _"Aplicar estándares de calidad de código: análisis estático y cobertura mínima"_
- **desarrollo/code-quality-sast.md**
  - _"Implementar análisis estático de seguridad (SAST) en pipelines"_
- **desarrollo/csharp-dotnet.md**
  - _"Seguir convenciones de código C# y .NET"_
- **desarrollo/sql.md**
  - _"Aplicar buenas prácticas de desarrollo SQL"_
- **desarrollo/code-quality-review.md**#4-requisitos-obligatorios
  - _"Realizar code review obligatorio antes de merge a ramas principales"_

---

### [Estrategia de Pruebas](desarrollo/02-estrategia-pruebas.md)

**Ubicación:** `desarrollo/02-estrategia-pruebas.md`
**Estándares requeridos:** 4

#### ❌ Faltantes (4)

- **desarrollo/testing-standards.md**
  - _"Implementar pruebas automatizadas en múltiples niveles (unitarias, integración, e2e)"_
- **desarrollo/testing-standards.md**#unit-tests
  - _"Escribir pruebas unitarias con cobertura mínima del 80%"_
- **desarrollo/testing-standards.md**#integration-tests
  - _"Implementar pruebas de integración para validar interacciones entre componentes"_
- **desarrollo/testing-standards.md**#contract-tests
  - _"Usar contract testing para validar contratos entre servicios"_

---

### [Documentación Técnica](desarrollo/03-documentacion-tecnica.md)

**Ubicación:** `desarrollo/03-documentacion-tecnica.md`
**Estándares requeridos:** 5

#### ✅ Existentes (4)

- **documentacion/architecture-decision-records.md**
  - _"Documentar decisiones arquitectónicas significativas mediante ADRs"_
- **documentacion/arc42.md**
  - _"Documentar arquitectura de servicios con plantilla arc42"_
- **documentacion/c4-model.md**
  - _"Modelar arquitectura con notación C4 y Structurizr DSL"_
- **apis/api-rest-standards.md**
  - _"Especificar APIs con OpenAPI 3.0+"_

#### ❌ Faltantes (1)

- **desarrollo/repositorios.md**#estructura-obligatoria-del-readme
  - _"Mantener README actualizado en todos los repositorios"_

---

### [Control de Versiones](desarrollo/04-control-versiones.md)

**Ubicación:** `desarrollo/04-control-versiones.md`
**Estándares requeridos:** 6

#### ✅ Existentes (3)

- **desarrollo/git.md**
  - _"Aplicar estándares de Git: workflows, commits y versionado"_
- **desarrollo/code-quality-review.md**#4-requisitos-obligatorios
  - _"Proteger ramas principales con políticas de merge"_
- **desarrollo/cicd-pipelines.md**
  - _"Automatizar versionado y tagging en pipelines CI/CD"_

#### ❌ Faltantes (3)

- **desarrollo/repositorios.md**#estrategia-de-branching
  - _"Usar Git workflows y estrategias de branching consistentes"_
- **desarrollo/repositorios.md**#commits-semanticos
  - _"Aplicar commits semánticos (Conventional Commits)"_
- **desarrollo/repositorios.md**#versionado-de-artefactos
  - _"Versionar artefactos con Semantic Versioning (SemVer)"_

---

## Gobierno (3 lineamientos)

### [Decisiones Arquitectónicas](gobierno/01-decisiones-arquitectonicas.md)

**Ubicación:** `gobierno/01-decisiones-arquitectonicas.md`
**Estándares requeridos:** 2

#### ✅ Existentes (1)

- **documentacion/architecture-decision-records.md**
  - _"Documentar decisiones significativas en ADRs"_

#### ❌ Faltantes (1)

- **gobierno/architecture-review.md**
  - _"Revisar ADRs en architecture reviews"_

---

### [Revisiones Arquitectónicas](gobierno/02-revisiones-arquitectonicas.md)

**Ubicación:** `gobierno/02-revisiones-arquitectonicas.md`
**Estándares requeridos:** 3

#### ❌ Faltantes (3)

- **gobierno/architecture-review.md**
  - _"Realizar architecture review antes de implementaciones significativas"_
- **gobierno/review-documentation.md**
  - _"Documentar resultados, decisiones y acciones de reviews"_
- **gobierno/architecture-retrospectives.md**
  - _"Realizar retrospectivas arquitectónicas post-implementación"_

---

### [Cumplimiento y Excepciones](gobierno/03-cumplimiento-y-excepciones.md)

**Ubicación:** `gobierno/03-cumplimiento-y-excepciones.md`
**Estándares requeridos:** 2

#### ❌ Faltantes (2)

- **gobierno/compliance-validation.md**
  - _"Validar cumplimiento de lineamientos y estándares"_
- **gobierno/exception-management.md**
  - _"Gestionar excepciones mediante proceso formal con ADR"_

---

## Operabilidad (4 lineamientos)

### [CI/CD y Automatización de Despliegues](operabilidad/01-cicd-pipelines.md)

**Ubicación:** `operabilidad/01-cicd-pipelines.md`
**Estándares requeridos:** 5

#### ✅ Existentes (5)

- **desarrollo/cicd-pipelines.md**
  - _"Automatizar despliegues mediante pipelines CI/CD"_
- **desarrollo/cicd-pipelines.md**#testing-stage
  - _"Ejecutar pruebas automatizadas en cada commit"_
- **desarrollo/cicd-pipelines.md**#security-stage
  - _"Integrar validaciones de seguridad (SAST, SCA) en pipelines"_
- **desarrollo/code-quality-review.md**
  - _"Implementar quality gates con métricas mínimas"_
- **desarrollo/cicd-pipelines.md**#deployment-strategies
  - _"Aplicar estrategias de deployment seguras (blue/green, canary)"_

---

### [Infraestructura como Código (IaC)](operabilidad/02-infraestructura-como-codigo.md)

**Ubicación:** `operabilidad/02-infraestructura-como-codigo.md`
**Estándares requeridos:** 7

#### ✅ Existentes (6)

- **infraestructura/infrastructure-as-code.md**
  - _"Definir infraestructura mediante código declarativo (Terraform)"_
- **desarrollo/code-quality-review.md**
  - _"Aplicar code review obligatorio a cambios de infraestructura"_
- **seguridad/iac-scanning.md**
  - _"Validar seguridad de código IaC con scanning automatizado"_
- **infraestructura/infrastructure-as-code.md**#state-management
  - _"Gestionar state de forma segura y compartida"_
- **infraestructura/infrastructure-as-code.md**#workflow
  - _"Validar cambios con terraform plan antes de apply"_
- **infraestructura/infrastructure-as-code.md**#modules
  - _"Crear módulos reutilizables para recursos comunes"_

#### ❌ Faltantes (1)

- **desarrollo/repositorios.md**
  - _"Versionar código de infraestructura en repositorios Git"_

---

### [Configuración y Consistencia de Entornos](operabilidad/03-configuracion-entornos.md)

**Ubicación:** `operabilidad/03-configuracion-entornos.md`
**Estándares requeridos:** 3

#### ✅ Existentes (3)

- **infraestructura/externalize-configuration.md**
  - _"Externalizar configuración en variables de entorno (12-Factor)"_
- **seguridad/secrets-key-management.md**
  - _"Gestionar secrets con AWS Secrets Manager"_
- **infraestructura/contenedores.md**
  - _"Contenerizar aplicaciones para consistencia"_

---

### [Disaster Recovery y Continuidad](operabilidad/04-disaster-recovery.md)

**Ubicación:** `operabilidad/04-disaster-recovery.md`
**Estándares requeridos:** 5

#### ❌ Faltantes (5)

- **operabilidad/disaster-recovery.md**#definicion-de-objetivos
  - _"Definir objetivos RPO/RTO para cada sistema crítico"_
- **operabilidad/disaster-recovery.md**#estrategia-de-backups
  - _"Implementar backups automatizados con retención apropiada"_
- **operabilidad/disaster-recovery.md**#pruebas-de-recuperacion
  - _"Probar procedimientos de restauración al menos trimestralmente"_
- **operabilidad/disaster-recovery.md**#documentacion-de-procedimientos
  - _"Documentar runbooks de DR actualizados y accesibles"_
- **operabilidad/disaster-recovery.md**#simulacros
  - _"Realizar simulacros de DR con equipos involucrados"_

---

## Seguridad (9 lineamientos)

### [Arquitectura Segura](seguridad/01-arquitectura-segura.md)

**Ubicación:** `seguridad/01-arquitectura-segura.md`
**Estándares requeridos:** 5

#### ✅ Existentes (5)

- **seguridad/security-architecture.md**#5-security-by-design
  - _"Aplicar Security by Design en decisiones arquitectónicas"_
- **seguridad/threat-modeling.md**
  - _"Realizar modelado de amenazas para nuevos sistemas"_
- **seguridad/security-architecture.md**#trust-boundaries
  - _"Definir explícitamente los límites de confianza (trust boundaries)"_
- **seguridad/security-architecture.md**#7-reducción-de-superficie-de-ataque
  - _"Reducir la superficie de ataque mediante exposición controlada"_
- **seguridad/security-architecture.md**#6-defensa-en-profundidad
  - _"Aplicar defensa en profundidad con múltiples capas"_

---

### [Arquitectura Segura](seguridad/01-seguridad-desde-el-diseno.md)

**Ubicación:** `seguridad/01-seguridad-desde-el-diseno.md`
**Estándares requeridos:** 5

#### ✅ Existentes (5)

- **seguridad/security-architecture.md**#5-security-by-design
  - _"Aplicar Security by Design en decisiones arquitectónicas"_
- **seguridad/threat-modeling.md**
  - _"Realizar modelado de amenazas para nuevos sistemas"_
- **seguridad/security-architecture.md**#trust-boundaries
  - _"Definir explícitamente los límites de confianza (trust boundaries)"_
- **seguridad/security-architecture.md**#7-reducción-de-superficie-de-ataque
  - _"Reducir la superficie de ataque mediante exposición controlada"_
- **seguridad/security-architecture.md**#6-defensa-en-profundidad
  - _"Aplicar defensa en profundidad con múltiples capas"_

---

### [Zero Trust](seguridad/02-zero-trust.md)

**Ubicación:** `seguridad/02-zero-trust.md`
**Estándares requeridos:** 5

#### ✅ Existentes (3)

- **seguridad/network-security.md**#zero-trust
  - _"Aplicar principios Zero Trust en arquitectura de red"_
- **seguridad/security-architecture.md**#trust-boundaries
  - _"Definir límites de confianza explícitos"_
- **observabilidad/observability.md**
  - _"Implementar trazabilidad completa de interacciones"_

#### ❌ Faltantes (2)

- **seguridad/authentication.md**
  - _"Implementar autenticación explícita para toda interacción"_
- **seguridad/authorization.md**
  - _"Evaluar acceso según identidad, contexto y propósito"_

---

### [Defensa en Profundidad](seguridad/03-defensa-en-profundidad.md)

**Ubicación:** `seguridad/03-defensa-en-profundidad.md`
**Estándares requeridos:** 5

#### ✅ Existentes (4)

- **seguridad/security-architecture.md**#7-reducción-de-superficie-de-ataque
  - _"Eliminar puntos únicos de falla en seguridad"_
- **seguridad/security-architecture.md**#6-defense-in-depth
  - _"Diseñar capas de seguridad independientes y complementarias"_
- **observabilidad/observability.md**
  - _"Facilitar detección, contención y aislamiento de incidentes"_
- **seguridad/network-security.md**
  - _"Distribuir controles en distintos niveles arquitectónicos"_

#### ❌ Faltantes (1)

- **seguridad/authorization.md**
  - _"Limitar acceso y capacidades progresivamente"_

---

### [Mínimo Privilegio](seguridad/04-minimo-privilegio.md)

**Ubicación:** `seguridad/04-minimo-privilegio.md`
**Estándares requeridos:** 5

#### ✅ Existentes (1)

- **arquitectura/bounded-contexts.md**
  - _"Evitar componentes con acceso excesivo o transversal"_

#### ❌ Faltantes (4)

- **seguridad/authorization.md**
  - _"Definir permisos de forma explícita y granular"_
- **seguridad/rbac.md**
  - _"Otorgar accesos por necesidad, no por conveniencia"_
- **seguridad/access-review.md**
  - _"Implementar privilegios revisables, revocables y temporales"_
- **seguridad/segregation-of-duties.md**
  - _"Segregar capacidades críticas claramente"_

---

### [Identidad y Accesos](seguridad/05-identidad-y-accesos.md)

**Ubicación:** `seguridad/05-identidad-y-accesos.md`
**Estándares requeridos:** 5

#### ✅ Existentes (5)

- **seguridad/identity-access-management.md**#4-autenticación-sso
  - _"Usar identidad federada y SSO corporativo para usuarios"_
- **seguridad/identity-access-management.md**#43-multi-factor-authentication-mfa
  - _"Implementar autenticación multifactor (MFA) para accesos críticos"_
- **seguridad/identity-access-management.md**#rbac
  - _"Aplicar mínimo privilegio en autorizaciones"_
- **seguridad/identity-access-management.md**
  - _"Gestionar identidades de servicios"_
- **seguridad/secrets-key-management.md**
  - _"No almacenar credenciales en código o configuración"_

---

### [Segmentación y Aislamiento](seguridad/06-segmentacion-y-aislamiento.md)

**Ubicación:** `seguridad/06-segmentacion-y-aislamiento.md`
**Estándares requeridos:** 5

#### ✅ Existentes (5)

- **seguridad/network-security.md**#segmentación-y-zonas
  - _"Segmentar redes por niveles de confianza (DMZ, interna, datos)"_
- **seguridad/network-security.md**#5-ejemplo-de-infraestructura
  - _"Aislar recursos por entorno en cuentas/subscripciones separadas"_
- **seguridad/tenant-isolation.md**
  - _"Implementar aislamiento de tenants en soluciones multi-tenant"_
- **seguridad/network-security.md**#principios-zero-trust
  - _"Aplicar principio de menor exposición de red (zero trust networking)"_
- **seguridad/network-security.md**#segmentación-y-zonas
  - _"Documentar zonas de seguridad y controles entre ellas"_

---

### [Protección de Datos](seguridad/07-proteccion-de-datos.md)

**Ubicación:** `seguridad/07-proteccion-de-datos.md`
**Estándares requeridos:** 6

#### ✅ Existentes (1)

- **seguridad/secrets-key-management.md**
  - _"Gestionar claves de cifrado con servicios dedicados (KMS)"_

#### ❌ Faltantes (5)

- **seguridad/data-protection.md**#classification
  - _"Clasificar datos según sensibilidad (público, interno, sensible, regulado)"_
- **seguridad/data-protection.md**#encryption
  - _"Cifrar datos sensibles en tránsito y reposo"_
- **seguridad/data-protection.md**
  - _"Aplicar enmascaramiento y tokenización donde corresponda"_
- **seguridad/data-protection.md**
  - _"Recopilar únicamente datos estrictamente necesarios (minimización)"_
- **seguridad/data-protection.md**
  - _"Implementar políticas de retención y eliminación automática"_

---

### [Gestión de Vulnerabilidades](seguridad/08-gestion-vulnerabilidades.md)

**Ubicación:** `seguridad/08-gestion-vulnerabilidades.md`
**Estándares requeridos:** 6

#### ✅ Existentes (6)

- **seguridad/vulnerability-management.md**
  - _"Implementar programa integral de gestión de vulnerabilidades"_
- **seguridad/vulnerability-management.md**#3-scanning-automatizado
  - _"Implementar scanning automatizado de vulnerabilidades en CI/CD"_
- **seguridad/vulnerability-management.md**
  - _"Mantener inventario actualizado de componentes y versiones"_
- **desarrollo/package-management.md**
  - _"Gestionar dependencias y paquetes de forma segura"_
- **seguridad/container-scanning.md**
  - _"Validar imágenes de contenedores antes de deployment"_
- **seguridad/iac-scanning.md**
  - _"Validar código de infraestructura (IaC) con scanning de seguridad"_

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

| #   | Estándar                              | Referencias | Estado    |
| --- | ------------------------------------- | ----------- | --------- |
| 1   | `arquitectura/bounded-contexts.md`    | 17          | ✅ Existe |
| 2   | `mensajeria/kafka-messaging.md`       | 13          | ✅ Existe |
| 3   | `observabilidad/observability.md`     | 11          | ✅ Existe |
| 4   | `seguridad/security-architecture.md`  | 11          | ✅ Existe |
| 5   | `apis/api-rest-standards.md`          | 8           | ✅ Existe |
| 6   | `arquitectura/resilience-patterns.md` | 6           | ✅ Existe |
| 7   | `datos/database-standards.md`         | 6           | ✅ Existe |
| 8   | `seguridad/network-security.md`       | 6           | ✅ Existe |
| 9   | `desarrollo/code-quality-review.md`   | 5           | ✅ Existe |
| 10  | `desarrollo/repositorios.md`          | 5           | ❌ Falta  |
| 11  | `desarrollo/cicd-pipelines.md`        | 5           | ✅ Existe |
| 12  | `operabilidad/disaster-recovery.md`   | 5           | ❌ Falta  |
| 13  | `seguridad/data-protection.md`        | 5           | ❌ Falta  |
| 14  | `gobierno/architecture-review.md`     | 4           | ❌ Falta  |
| 15  | `desarrollo/testing-standards.md`     | 4           | ❌ Falta  |

---

**Generado automáticamente por script de análisis**
