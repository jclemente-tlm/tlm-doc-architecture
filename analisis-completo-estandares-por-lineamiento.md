# Análisis Completo: Estándares Requeridos por Lineamiento

**Generado:** 2026-02-17
**Análisis:** Verificación exhaustiva de todos los lineamientos

---

## Resumen Ejecutivo

| Métrica                             | Valor      |
| ----------------------------------- | ---------- |
| **Lineamientos analizados**         | 35         |
| **Referencias totales**             | 181 líneas |
| **Estándares únicos referenciados** | 63         |
| **Estándares existentes**           | 33 ✅      |
| **Estándares faltantes**            | 30 ❌      |

### Distribución por Categoría

| Categoría    | Lineamientos | Referencias |
| ------------ | ------------ | ----------- |
| Arquitectura | 13           | ~80         |
| Seguridad    | 8            | ~45         |
| Desarrollo   | 4            | ~20         |
| Operabilidad | 4            | ~20         |
| Gobierno     | 3            | ~10         |
| Datos        | 3            | ~6          |

---

## Arquitectura (13 lineamientos)

### 01. [Estilo y Enfoque Arquitectónico](arquitectura/01-estilo-y-enfoque-arquitectonico.md)

**Estándares requeridos: 2**

✅ **Existentes:**

- `documentacion/architecture-decision-records.md`
  - _"Documentar estilo seleccionado en ADR"_

❌ **Faltantes:**

- `gobierno/architecture-review.md`
  - _"Validar coherencia entre estilo declarado y decisiones técnicas"_

---

### 02. [Descomposición y Límites](arquitectura/02-descomposicion-y-limites.md)

**Estándares requeridos: 3**

✅ **Existentes:**

- `arquitectura/bounded-contexts.md`
  - _"Identificar límites por capacidad de negocio, no por tecnología"_
  - _"Definir responsabilidad única y clara por componente"_

❌ **Faltantes:**

- `arquitectura/dependency-management.md`
  - _"Evitar dependencias cíclicas entre componentes"_

---

### 03. [Cloud Native](arquitectura/03-cloud-native.md)

**Estándares requeridos: 6**

✅ **Existentes:**

- `infraestructura/externalize-configuration.md`
  - _"Externalizar configuración en variables de entorno"_
- `arquitectura/bounded-contexts.md#12-diseño-stateless`
  - _"Diseñar servicios stateless con estado en backing services"_
- `observabilidad/observability.md#8-health-checks`
  - _"Implementar health checks liveness y readiness"_
- `arquitectura/bounded-contexts.md#13-escalabilidad-horizontal`
  - _"Preparar servicios para escalabilidad horizontal"_
- `arquitectura/resilience-patterns.md#8-graceful-shutdown`
  - _"Aplicar graceful shutdown para terminación ordenada"_
- `infraestructura/aws-cost-optimization.md`
  - _"Optimizar costos mediante tagging, alertas y rightsizing"_

---

### 04. [Resiliencia y Disponibilidad](arquitectura/04-resiliencia-y-disponibilidad.md)

**Estándares requeridos: 6**

✅ **Existentes:**

- `arquitectura/resilience-patterns.md#4-circuit-breaker`
  - _"Implementar circuit breakers para dependencias externas"_
- `arquitectura/resilience-patterns.md#7-timeouts`
  - _"Aplicar timeouts apropiados en llamadas remotas"_
- `arquitectura/resilience-patterns.md#5-retry-pattern`
  - _"Configurar retry con backoff exponencial"_
- `arquitectura/resilience-patterns.md#6-graceful-degradation`
  - _"Diseñar degradación graceful ante fallos"_
- `observabilidad/observability.md#10-slos-y-slas`
  - _"Definir SLOs y SLAs documentados"_
- `mensajeria/kafka-messaging.md`
  - _"Implementar Dead Letter Queue para mensajes fallidos"_

---

### 05. [Escalabilidad y Rendimiento](arquitectura/05-escalabilidad-y-rendimiento.md)

**Estándares requeridos: 6**

✅ **Existentes:**

- `arquitectura/bounded-contexts.md#12-diseño-stateless`
  - _"Diseñar servicios stateless para escalado horizontal"_
- `observabilidad/observability.md`
  - _"Monitorear métricas de rendimiento (latencia P95, throughput, errores)"_

❌ **Faltantes:**

- `infraestructura/auto-scaling.md`
  - _"Implementar auto-scaling basado en métricas"_
- `arquitectura/caching-strategies.md`
  - _"Aplicar caché distribuido para datos frecuentes"_
- `mensajeria/async-messaging.md`
  - _"Mover operaciones costosas a procesamiento asíncrono"_
- `datos/database-optimization.md`
  - _"Optimizar consultas de base de datos con índices apropiados"_

---

### 06. [Observabilidad](arquitectura/06-observabilidad.md)

**Estándares requeridos: 5**

✅ **Existentes:**

- `observabilidad/observability.md#2-logging`
  - _"Generar logs estructurados en formato JSON"_
- `observabilidad/observability.md#3-métricas`
  - _"Emitir métricas siguiendo metodología RED/USE"_
- `observabilidad/observability.md#4-trazas-distribuidas`
  - _"Implementar trazas distribuidas con W3C Trace Context"_
- `observabilidad/observability.md`
  - _"Usar identificadores de correlación entre servicios"_
  - _"Configurar health checks para orquestadores"_

---

### 07. [APIs y Contratos](arquitectura/07-apis-y-contratos.md)

**Estándares requeridos: 9**

✅ **Existentes:**

- `apis/api-rest-standards.md`
  - _"Seguir convenciones RESTful para recursos y verbos HTTP"_
  - _"Implementar versionado explícito en URL o header"_
  - _"Aplicar rate limiting y paginación en colecciones"_
  - _"Estandarizar manejo de errores con estructura consistente"_
  - _"Definir contratos con especificaciones estándar OpenAPI 3.0+"_
  - _"Validar requests/responses contra contratos en runtime"_
  - _"Mantener retrocompatibilidad durante deprecación"_
- `mensajeria/kafka-messaging.md`
  - _"Documentar APIs asíncronas con AsyncAPI"_
- `testing/testing-standards.md#contract-tests`
  - _"Implementar contract testing automatizado (Pact)"_

---

### 08. [Comunicación Asíncrona y Eventos](arquitectura/08-comunicacion-asincrona-y-eventos.md)

**Estándares requeridos: 7**

✅ **Existentes (todos):**

- `mensajeria/kafka-messaging.md`
  - _"Implementar mensajería con Apache Kafka"_
  - _"Definir esquemas de eventos con AsyncAPI o JSON Schema"_
  - _"Usar eventos para comunicar hechos del dominio, no comandos"_
  - _"Implementar idempotencia en consumidores"_
  - _"Garantizar entrega at-least-once o exactly-once"_
  - _"Configurar Dead Letter Queue para mensajes fallidos"_
  - _"Documentar topología de eventos y consumidores"_

---

### 09. [Modelado de Dominio](arquitectura/09-modelado-de-dominio.md)

**Estándares requeridos: 5**

✅ **Existentes:**

- `arquitectura/bounded-contexts.md`
  - _"Identificar bounded contexts por capacidades de negocio"_
  - _"Asignar responsabilidades según capacidades del dominio"_
  - _"Evitar mezclar lógicas de dominios distintos"_
- `arquitectura/bounded-contexts.md#lenguaje-ubicuo`
  - _"Definir lenguaje ubicuo compartido con el negocio"_
- `documentacion/c4-model.md`
  - _"Documentar modelo de dominio en diagramas de contexto"_

---

### 10. [Autonomía de Servicios](arquitectura/10-autonomia-de-servicios.md)

**Estándares requeridos: 5**

✅ **Existentes:**

- `arquitectura/resilience-patterns.md`
  - _"Implementar modo degradado ante fallos de dependencias"_

❌ **Faltantes:**

- `datos/database-per-service.md`
  - _"Implementar ownership completo de datos por servicio"_
- `desarrollo/independent-deployment.md`
  - _"Habilitar despliegue independiente sin coordinación"_
- `mensajeria/async-messaging.md`
  - _"Utilizar comunicación asíncrona cuando sea posible"_
- `apis/api-versioning.md`
  - _"Definir contratos de API versionados"_

---

### 11. [Arquitectura Limpia](arquitectura/11-arquitectura-limpia.md)

**Estándares requeridos: 5**

✅ **Existentes:**

- `arquitectura/bounded-contexts.md`
  - _"Separar lógica de negocio de frameworks e infraestructura"_
  - _"Estructurar sistema reflejando prioridades del negocio"_
- `documentacion/c4-model.md`
  - _"Documentar capas y responsabilidades arquitectónicas"_

❌ **Faltantes:**

- `arquitectura/dependency-inversion.md`
  - _"Orientar dependencias hacia el dominio, no hacia detalles técnicos"_
- `arquitectura/hexagonal-architecture.md`
  - _"Limitar impacto de cambios tecnológicos en el núcleo del sistema"_

---

### 12. [Arquitectura Evolutiva](arquitectura/12-arquitectura-evolutiva.md)

**Estándares requeridos: 5**

✅ **Existentes:**

- `arquitectura/bounded-contexts.md`
  - _"Priorizar reversibilidad en decisiones técnicas"_
  - _"Definir contratos y límites para contener impacto del cambio"_

❌ **Faltantes:**

- `documentacion/adr-template.md`
  - _"Documentar decisiones arquitectónicas con ADRs"_
- `gobierno/architecture-review.md`
  - _"Revisar y ajustar decisiones arquitectónicas periódicamente"_
- `desarrollo/refactoring-practices.md`
  - _"Implementar refactorización y mejora continua"_

---

### 13. [Simplicidad Intencional](arquitectura/13-simplicidad-intencional.md)

**Estándares requeridos: 5**

✅ **Existentes:**

- `arquitectura/bounded-contexts.md`
  - _"Minimizar dependencias innecesarias entre componentes"_
- `observabilidad/observability.md`
  - _"Facilitar operación, monitoreo y evolución del sistema"_

❌ **Faltantes:**

- `arquitectura/complexity-analysis.md`
  - _"Introducir complejidad solo con beneficio claro y medible"_
- `documentacion/adr-template.md`
  - _"Documentar decisiones arquitectónicas de forma comprensible"_
- `arquitectura/technology-selection.md`
  - _"Preferir soluciones conocidas y estables sobre enfoques novedosos"_

---

## Datos (3 lineamientos)

### 01. [Datos por Dominio](datos/01-datos-por-dominio.md)

**Estándares requeridos: 9**

✅ **Existentes:**

- `datos/database-standards.md`
  - _"Asignar propiedad exclusiva de datos por dominio (database per service)"_
  - _"Evitar bases de datos compartidas entre servicios"_
  - _"Versionar esquemas de BD con migraciones automatizadas (Flyway/Liquibase)"_
  - _"Validar datos contra esquemas antes de persistir"_
  - _"Gestionar cambios con estrategias expand-contract (backward compatible)"_
- `arquitectura/bounded-contexts.md`
  - _"Exponer datos mediante APIs o eventos, no acceso directo a BD"_
  - _"Documentar propiedad y lifecycle de datos por dominio"_
- `mensajeria/kafka-messaging.md`
  - _"Documentar esquemas de eventos con JSON Schema o AsyncAPI"_
  - _"Mantener retrocompatibilidad en eventos y APIs de datos"_

---

### 02. [Consistencia y Sincronización](datos/02-consistencia-y-sincronizacion.md)

**Estándares requeridos: 4**

✅ **Existentes (todos):**

- `datos/database-standards.md`
  - _"Definir modelo de consistencia explícito por caso de uso"_
- `arquitectura/saga-pattern.md`
  - _"Preferir sagas o compensaciones sobre transacciones distribuidas"_
- `mensajeria/kafka-messaging.md`
  - _"Implementar idempotencia para garantizar convergencia"_
  - _"Usar eventos de dominio para sincronización eventual"_

---

### 03. [Propiedad de Datos](datos/03-propiedad-de-datos.md)

**Estándares requeridos: 5**

❌ **Faltantes (todos):**

- `datos/database-per-service.md`
  - _"Asignar base de datos independiente por dominio/servicio"_
- `datos/no-shared-database.md`
  - _"Prohibir acceso directo a bases de datos de otros dominios"_
- `datos/data-exposure.md`
  - _"Exponer datos mediante APIs o eventos"_
- `datos/data-catalog.md`
  - _"Documentar ownership de cada conjunto de datos"_
- `datos/data-replication.md`
  - _"Gestionar replicación controlada cuando sea necesaria"_

---

## Desarrollo (4 lineamientos)

### 01. [Calidad de Código](desarrollo/01-calidad-codigo.md)

**Estándares requeridos: 5**

✅ **Existentes (todos):**

- `desarrollo/code-quality-review.md`
  - _"Aplicar estándares de calidad de código: análisis estático y cobertura mínima"_
  - _"Realizar code review obligatorio antes de merge a ramas principales"_
- `desarrollo/code-quality-sast.md`
  - _"Implementar análisis estático de seguridad (SAST) en pipelines"_
- `desarrollo/csharp-dotnet.md`
  - _"Seguir convenciones de código C# y .NET"_
- `desarrollo/sql.md`
  - _"Aplicar buenas prácticas de desarrollo SQL"_

---

### 02. [Estrategia de Pruebas](desarrollo/02-estrategia-pruebas.md)

**Estándares requeridos: 4**

✅ **Existentes (todos):**

- `desarrollo/testing-standards.md`
  - _"Implementar pruebas automatizadas en múltiples niveles (unitarias, integración, e2e)"_
  - _"Escribir pruebas unitarias con cobertura mínima del 80%"_
  - _"Implementar pruebas de integración para validar interacciones entre componentes"_
  - _"Usar contract testing para validar contratos entre servicios"_

---

### 03. [Documentación Técnica](desarrollo/03-documentacion-tecnica.md)

**Estándares requeridos: 5**

✅ **Existentes:**

- `documentacion/architecture-decision-records.md`
  - _"Documentar decisiones arquitectónicas significativas mediante ADRs"_
- `documentacion/arc42.md`
  - _"Documentar arquitectura de servicios con plantilla arc42"_
- `documentacion/c4-model.md`
  - _"Modelar arquitectura con notación C4 y Structurizr DSL"_
- `apis/api-rest-standards.md`
  - _"Especificar APIs con OpenAPI 3.0+"_

❌ **Faltantes:**

- `desarrollo/repositorios.md#estructura-obligatoria-del-readme`
  - _"Mantener README actualizado en todos los repositorios"_

---

### 04. [Control de Versiones](desarrollo/04-control-versiones.md)

**Estándares requeridos: 6**

✅ **Existentes:**

- `desarrollo/git.md`
  - _"Aplicar estándares de Git: workflows, commits y versionado"_
- `desarrollo/code-quality-review.md#4-requisitos-obligatorios`
  - _"Proteger ramas principales con políticas de merge"_
- `desarrollo/cicd-pipelines.md`
  - _"Automatizar versionado y tagging en pipelines CI/CD"_

❌ **Faltantes:**

- `desarrollo/repositorios.md#estrategia-de-branching`
  - _"Usar Git workflows y estrategias de branching consistentes"_
- `desarrollo/repositorios.md#commits-semanticos`
  - _"Aplicar commits semánticos (Conventional Commits)"_
- `desarrollo/repositorios.md#versionado-de-artefactos`
  - _"Versionar artefactos con Semantic Versioning (SemVer)"_

---

## Gobierno (3 lineamientos)

### 01. [Decisiones Arquitectónicas](gobierno/01-decisiones-arquitectonicas.md)

**Estándares requeridos: 2**

✅ **Existentes:**

- `documentacion/architecture-decision-records.md`
  - _"Documentar decisiones significativas en ADRs"_

❌ **Faltantes:**

- `gobierno/architecture-review.md`
  - _"Revisar ADRs en architecture reviews"_

---

### 02. [Revisiones Arquitectónicas](gobierno/02-revisiones-arquitectonicas.md)

**Estándares requeridos: 3**

❌ **Faltantes (todos):**

- `governo/architecture-review.md`
  - _"Realizar architecture review antes de implementaciones significativas"_
- `governo/review-documentation.md`
  - _"Documentar resultados, decisiones y acciones de reviews"_
- `governo/architecture-retrospectives.md`
  - _"Realizar retrospectivas arquitectónicas post-implementación"_

---

### 03. [Cumplimiento y Excepciones](gobierno/03-cumplimiento-y-excepciones.md)

**Estándares requeridos: 2**

❌ **Faltantes (todos):**

- `governo/compliance-validation.md`
  - _"Validar cumplimiento de lineamientos y estándares"_
- `governo/exception-management.md`
  - _"Gestionar excepciones mediante proceso formal con ADR"_

---

## Operabilidad (4 lineamientos)

### 01. [CI/CD Pipelines](operabilidad/01-cicd-pipelines.md)

**Estándares requeridos: 5**

✅ **Existentes (todos):**

- `desarrollo/cicd-pipelines.md`
  - _"Automatizar despliegues mediante pipelines CI/CD"_
  - _"Ejecutar pruebas automatizadas en cada commit"_
  - _"Integrar validaciones de seguridad (SAST, SCA) en pipelines"_
  - _"Aplicar estrategias de deployment seguras (blue/green, canary)"_
- `desarrollo/code-quality-review.md`
  - _"Implementar quality gates con métricas mínimas"_

---

### 02. [Infraestructura como Código](operabilidad/02-infraestructura-como-codigo.md)

**Estándares requeridos: 7**

✅ **Existentes:**

- `infraestructura/infrastructure-as-code.md`
  - _"Definir infraestructura mediante código declarativo (Terraform)"_
  - _"Gestionar state de forma segura y compartida"_
  - _"Validar cambios con terraform plan antes de apply"_
  - _"Crear módulos reutilizables para recursos comunes"_
- `desarrollo/code-quality-review.md`
  - _"Aplicar code review obligatorio a cambios de infraestructura"_
- `seguridad/iac-scanning.md`
  - _"Validar seguridad de código IaC con scanning automatizado"_

❌ **Faltantes:**

- `desarrollo/repositorios.md`
  - _"Versionar código de infraestructura en repositorios Git"_

---

### 03. [Configuración de Entornos](operabilidad/03-configuracion-entornos.md)

**Estándares requeridos: 3**

✅ **Existentes (todos):**

- `infraestructura/externalize-configuration.md`
  - _"Externalizar configuración en variables de entorno (12-Factor)"_
- `seguridad/secrets-key-management.md`
  - _"Gestionar secrets con AWS Secrets Manager"_
- `infraestructura/contenedores.md`
  - _"Contenedorizar aplicaciones para consistencia"_

---

### 04. [Disaster Recovery](operabilidad/04-disaster-recovery.md)

**Estándares requeridos: 5**

❌ **Faltantes (todos):**

- `operabilidad/disaster-recovery.md#definicion-de-objetivos`
  - _"Definir objetivos RPO/RTO para cada sistema crítico"_
- `operabilidad/disaster-recovery.md#estrategia-de-backups`
  - _"Implementar backups automatizados con retención apropiada"_
- `operabilidad/disaster-recovery.md#pruebas-de-recuperacion`
  - _"Probar procedimientos de restauración al menos trimestralmente"_
- `operabilidad/disaster-recovery.md#documentacion-de-procedimientos`
  - _"Documentar runbooks de DR actualizados y accesibles"_
- `operabilidad/disaster-recovery.md#simulacros`
  - _"Realizar simulacros de DR con equipos involucrados"_

---

## Seguridad (8 lineamientos)

### 01. [Arquitectura Segura](seguridad/01-arquitectura-segura.md)

**Estándares requeridos: 5**

✅ **Existentes (todos):**

- `seguridad/security-architecture.md#5-security-by-design`
  - _"Aplicar Security by Design en decisiones arquitectónicas"_
- `seguridad/threat-modeling.md`
  - _"Realizar modelado de amenazas para nuevos sistemas"_
- `seguridad/security-architecture.md#trust-boundaries`
  - _"Definir explícitamente los límites de confianza (trust boundaries)"_
- `seguridad/security-architecture.md#7-reducción-de-superficie-de-ataque`
  - _"Reducir la superficie de ataque mediante exposición controlada"_
- `seguridad/security-architecture.md#6-defensa-en-profundidad`
  - _"Aplicar defensa en profundidad con múltiples capas"_

---

### 02. [Zero Trust](seguridad/02-zero-trust.md)

**Estándares requeridos: 5**

✅ **Existentes:**

- `seguridad/network-security.md#zero-trust`
  - _"Aplicar principios Zero Trust en arquitectura de red"_
- `seguridad/security-architecture.md#trust-boundaries`
  - _"Definir límites de confianza explícitos"_
- `observabilidad/observability.md`
  - _"Implementar trazabilidad completa de interacciones"_

❌ **Faltantes:**

- `seguridad/authentication.md`
  - _"Implementar autenticación explícita para toda interacción"_
- `seguridad/authorization.md`
  - _"Evaluar acceso según identidad, contexto y propósito"_

---

### 03. [Defensa en Profundidad](seguridad/03-defensa-en-profundidad.md)

**Estándares requeridos: 5**

✅ **Existentes:**

- `seguridad/security-architecture.md#7-reducción-de-superficie-de-ataque`
  - _"Eliminar puntos únicos de falla en seguridad"_
- `seguridad/security-architecture.md#6-defense-in-depth`
  - _"Diseñar capas de seguridad independientes y complementarias"_
- `observabilidad/observability.md`
  - _"Facilitar detección, contención y aislamiento de incidentes"_
- `seguridad/network-security.md`
  - _"Distribuir controles en distintos niveles arquitectónicos"_

❌ **Faltantes:**

- `seguridad/authorization.md`
  - _"Limitar acceso y capacidades progresivamente"_

---

### 04. [Mínimo Privilegio](seguridad/04-minimo-privilegio.md)

**Estándares requeridos: 5**

✅ **Existentes:**

- `arquitectura/bounded-contexts.md`
  - _"Evitar componentes con acceso excesivo o transversal"_

❌ **Faltantes:**

- `seguridad/authorization.md`
  - _"Definir permisos de forma explícita y granular"_
- `seguridad/rbac.md`
  - _"Otorgar accesos por necesidad, no por conveniencia"_
- `seguridad/access-review.md`
  - _"Implementar privilegios revisables, revocables y temporales"_
- `seguridad/segregation-of-duties.md`
  - _"Segregar capacidades críticas claramente"_

---

### 05. [Identidad y Accesos](seguridad/05-identidad-y-accesos.md)

**Estándares requeridos: 5**

✅ **Existentes (todos):**

- `seguridad/identity-access-management.md#4-autenticación-sso`
  - _"Usar identidad federada y SSO corporativo para usuarios"_
- `seguridad/identity-access-management.md#43-multi-factor-authentication-mfa`
  - _"Implementar autenticación multifactor (MFA) para accesos críticos"_
- `seguridad/identity-access-management.md#rbac`
  - _"Aplicar mínimo privilegio en autorizaciones"_
- `seguridad/identity-access-management.md`
  - _"Gestionar identidades de servicios"_
- `seguridad/secrets-key-management.md`
  - _"No almacenar credenciales en código o configuración"_

---

### 06. [Segmentación y Aislamiento](seguridad/06-segmentacion-y-aislamiento.md)

**Estándares requeridos: 5**

✅ **Existentes (todos):**

- `seguridad/network-security.md#segmentación-y-zonas`
  - _"Segmentar redes por niveles de confianza (DMZ, interna, datos)"_
  - _"Documentar zonas de seguridad y controles entre ellas"_
- `seguridad/network-security.md#5-ejemplo-de-infraestructura`
  - _"Aislar recursos por entorno en cuentas/subscripciones separadas"_
- `seguridad/tenant-isolation.md`
  - _"Implementar aislamiento de tenants en soluciones multi-tenant"_
- `seguridad/network-security.md#principios-zero-trust`
  - _"Aplicar principio de menor exposición de red (zero trust networking)"_

---

### 07. [Protección de Datos](seguridad/07-proteccion-de-datos.md)

**Estándares requeridos: 6**

✅ **Existentes (todos):**

- `seguridad/data-protection.md#classification`
  - _"Clasificar datos según sensibilidad (público, interno, sensible, regulado)"_
- `seguridad/data-protection.md#encryption`
  - _"Cifrar datos sensibles en tránsito y reposo"_
- `seguridad/data-protection.md`
  - _"Aplicar enmascaramiento y tokenización donde corresponda"_
  - _"Recopilar únicamente datos estrictamente necesarios (minimización)"_
  - _"Implementar políticas de retención y eliminación automática"_
- `seguridad/secrets-key-management.md`
  - _"Gestionar claves de cifrado con servicios dedicados (KMS)"_

---

### 08. [Gestión de Vulnerabilidades](seguridad/08-gestion-vulnerabilidades.md)

**Estándares requeridos: 6**

✅ **Existentes (todos):**

- `seguridad/vulnerability-management.md`
  - _"Implementar programa integral de gestión de vulnerabilidades"_
  - _"Implementar scanning automatizado de vulnerabilidades en CI/CD"_
  - _"Mantener inventario actualizado de componentes y versiones"_
- `desarrollo/package-management.md`
  - _"Gestionar dependencias y paquetes de forma segura"_
- `seguridad/container-scanning.md`
  - _"Validar imágenes de contenedores antes de deployment"_
- `seguridad/iac-scanning.md`
  - _"Validar código de infraestructura (IaC) con scanning de seguridad"_

---

## Resumen de Estándares Faltantes

### 🔴 Prioridad CRÍTICA (3+ referencias)

1. **gobierno/architecture-review.md** (4 refs)
   - arquitectura/12-arquitectura-evolutiva
   - arquitectura/01-estilo-y-enfoque-arquitectonico
   - gobierno/01-decisiones-arquitectonicas
   - gobierno/02-revisiones-arquitectonicas

2. **documentacion/adr-template.md** (4 refs)
   - arquitectura/13-simplicidad-intencional
   - arquitectura/12-arquitectura-evolutiva
   - arquitectura/01-estilo-y-enfoque-arquitectonico
   - gobierno/01-decisiones-arquitectonicas

3. **datos/database-per-service.md** (3 refs)
   - datos/03-propiedad-de-datos
   - arquitectura/10-autonomia-de-servicios

4. **mensajeria/async-messaging.md** (3 refs)
   - arquitectura/10-autonomia-de-servicios
   - arquitectura/05-escalabilidad-y-rendimiento

5. **desarrollo/repositorios.md** (3 refs)
   - desarrollo/03-documentacion-tecnica
   - desarrollo/04-control-versiones
   - operabilidad/02-infraestructura-como-codigo

6. **operabilidad/disaster-recovery.md** (5 refs)
   - operabilidad/04-disaster-recovery (todas las secciones)

7. **seguridad/authorization.md** (3 refs)
   - seguridad/04-minimo-privilegio
   - seguridad/03-defensa-en-profundidad
   - seguridad/02-zero-trust

### 🟠 Prioridad ALTA (2 referencias)

8. gobierno/review-documentation.md
9. governo/architecture-retrospectives.md
10. governo/compliance-validation.md
11. governo/exception-management.md
12. seguridad/authentication.md
13. seguridad/rbac.md
14. seguridad/access-review.md

### 🟡 Prioridad MEDIA (1 referencia)

15-30. Ver lista completa en reporte anterior

---

## Top 10 Estándares Más Referenciados

| #   | Estándar                                         | Referencias | Estado    |
| --- | ------------------------------------------------ | ----------- | --------- |
| 1   | `arquitectura/bounded-contexts.md`               | 17          | ✅ Existe |
| 2   | `mensajeria/kafka-messaging.md`                  | 13          | ✅ Existe |
| 3   | `observabilidad/observability.md`                | 11          | ✅ Existe |
| 4   | `arquitectura/resilience-patterns.md`            | 9           | ✅ Existe |
| 5   | `apis/api-rest-standards.md`                     | 8           | ✅ Existe |
| 6   | `desarrollo/code-quality-review.md`              | 6           | ✅ Existe |
| 7   | `seguridad/security-architecture.md`             | 6           | ✅ Existe |
| 8   | `desarrollo/cicd-pipelines.md`                   | 5           | ✅ Existe |
| 9   | `datos/database-standards.md`                    | 5           | ✅ Existe |
| 10  | `documentacion/architecture-decision-records.md` | 4           | ✅ Existe |

---

**✅ Análisis completo finalizado**

- Total lineamientos: 35
- Referencias totales: 181
- Estándares únicos: 63
- Existentes: 33 ✅
- Faltantes: 30 ❌
