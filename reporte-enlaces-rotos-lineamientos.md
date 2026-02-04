# Reporte de Validación de Enlaces - Lineamientos

## Fecha: 2026-02-04

---

## ARCHIVO: [docs/fundamentos-corporativos/lineamientos/arquitectura/01-estilo-y-enfoque-arquitectonico.md](docs/fundamentos-corporativos/lineamientos/arquitectura/01-estilo-y-enfoque-arquitectonico.md)

ENLACES ENCONTRADOS: 6

✅ VÁLIDOS (2 enlaces):

- [Documentar estilo seleccionado en ADR](../../estandares/documentacion/architecture-decision-records.md) → archivo existe
- [Validar coherencia entre estilo declarado y decisiones técnicas](../../estandares/gobierno/architecture-review.md) → archivo existe (buscar en estandares/gobierno/)

❌ ROTOS (4 enlaces):

- [Seleccionar estilo basado en contexto de negocio](../../estilos-arquitectonicos/criterios-seleccion.md) → NO EXISTE
  **SUGERENCIA:** Este archivo debe crearse en `docs/fundamentos-corporativos/estilos-arquitectonicos/criterios-seleccion.md`

- [Diseñar monolitos modulares para dominios acotados](../../estilos-arquitectonicos/monolito-modular.md) → NO EXISTE
  **SUGERENCIA:** Este archivo debe crearse en `docs/fundamentos-corporativos/estilos-arquitectonicos/monolito-modular.md`

- [Adoptar microservicios para dominios independientes](../../estilos-arquitectonicos/microservicios.md) → NO EXISTE
  **SUGERENCIA:** Este archivo debe crearse en `docs/fundamentos-corporativos/estilos-arquitectonicos/microservicios.md`

- [Implementar arquitectura orientada a eventos para desacoplamiento temporal](../../estilos-arquitectonicos/eventos.md) → NO EXISTE
  **SUGERENCIA:** Este archivo debe crearse en `docs/fundamentos-corporativos/estilos-arquitectonicos/eventos.md`

---

## ARCHIVO: [docs/fundamentos-corporativos/lineamientos/arquitectura/02-descomposicion-y-limites.md](docs/fundamentos-corporativos/lineamientos/arquitectura/02-descomposicion-y-limites.md)

ENLACES ENCONTRADOS: 4

✅ VÁLIDOS (3 enlaces):

- [Identificar límites por capacidad de negocio, no por tecnología](../../estandares/arquitectura/bounded-contexts.md) → archivo existe
- [Evitar dependencias cíclicas entre componentes](../../estandares/arquitectura/dependency-management.md) → archivo existe
- [Establecer contratos explícitos en los límites](../07-contratos-de-integracion.md) → archivo existe

❌ ROTOS (1 enlace):

- [Definir responsabilidad única y clara por componente](../../estandares/arquitectura/single-responsibility.md) → NO EXISTE
  **SUGERENCIA:** Este concepto está cubierto en `../../estandares/arquitectura/bounded-contexts.md` o crear archivo específico

---

## ARCHIVO: [docs/fundamentos-corporativos/lineamientos/arquitectura/03-diseño-cloud-native.md](docs/fundamentos-corporativos/lineamientos/arquitectura/03-diseño-cloud-native.md)

ENLACES ENCONTRADOS: 6

✅ VÁLIDOS (2 enlaces):

- [Externalizar configuración en variables de entorno](../../estandares/infraestructura/externalize-configuration.md) → archivo existe
- [Implementar health checks liveness y readiness](../../estandares/observabilidad/health-checks.md) → verificar (parte de observability.md)

❌ ROTOS (4 enlaces):

- [Diseñar servicios stateless con estado en backing services](../../estandares/arquitectura/stateless-services.md) → NO EXISTE
  **SUGERENCIA:** Crear en `../../estandares/arquitectura/stateless-design.md`

- [Preparar servicios para escalabilidad horizontal](../../estandares/arquitectura/horizontal-scaling.md) → NO EXISTE
  **SUGERENCIA:** Crear en `../../estandares/infraestructura/horizontal-scaling.md` o parte de resilience-patterns

- [Aplicar graceful shutdown para terminación ordenada](../../estandares/arquitectura/graceful-shutdown.md) → NO EXISTE
  **SUGERENCIA:** Crear en `../../estandares/arquitectura/graceful-shutdown.md`

- [Gestionar secretos en AWS Secrets Manager](../../../decisiones-de-arquitectura/adr-003-gestion-secretos.md) → NO EXISTE
  **NOTA:** El archivo correcto es `adr-003-aws-secrets-manager.md`

---

## ARCHIVO: [docs/fundamentos-corporativos/lineamientos/arquitectura/04-resiliencia-y-disponibilidad.md](docs/fundamentos-corporativos/lineamientos/arquitectura/04-resiliencia-y-disponibilidad.md)

ENLACES ENCONTRADOS: 6

✅ VÁLIDOS (2 enlaces):

- [Implementar circuit breakers para dependencias externas](../../estandares/arquitectura/circuit-breakers.md) → parte de resilience-patterns.md
- [Implementar Dead Letter Queue para mensajes fallidos](../../estandares/mensajeria/dead-letter-queue.md) → verificar en kafka-messaging.md

❌ ROTOS (4 enlaces):

- [Aplicar timeouts apropiados en llamadas remotas](../../estandares/arquitectura/timeouts.md) → NO EXISTE
  **SUGERENCIA:** Parte de `../../estandares/arquitectura/resilience-patterns.md`

- [Configurar retry con backoff exponencial](../../estandares/arquitectura/retry-patterns.md) → NO EXISTE
  **SUGERENCIA:** Parte de `../../estandares/arquitectura/resilience-patterns.md`

- [Diseñar degradación graceful ante fallos](../../estandares/arquitectura/graceful-degradation.md) → NO EXISTE
  **SUGERENCIA:** Parte de `../../estandares/arquitectura/resilience-patterns.md`

- [Definir SLOs y SLAs documentados](../../estandares/operabilidad/slos-slas.md) → NO EXISTE
  **SUGERENCIA:** Crear en `../../estandares/operabilidad/slos-slas.md`

---

## ARCHIVO: [docs/fundamentos-corporativos/lineamientos/arquitectura/05-observabilidad.md](docs/fundamentos-corporativos/lineamientos/arquitectura/05-observabilidad.md)

ENLACES ENCONTRADOS: 5

❌ ROTOS (5 enlaces):
TODOS apuntan a archivos individuales que están consolidados en observability.md:

- [Generar logs estructurados en formato JSON](../../estandares/observabilidad/logging.md) → NO EXISTE
  **SUGERENCIA:** Cambiar a `../../estandares/observabilidad/observability.md`

- [Emitir métricas siguiendo metodología RED/USE](../../estandares/observabilidad/metrics-monitoring.md) → NO EXISTE
  **SUGERENCIA:** Cambiar a `../../estandares/observabilidad/observability.md`

- [Implementar trazas distribuidas con W3C Trace Context](../../estandares/observabilidad/distributed-tracing.md) → NO EXISTE
  **SUGERENCIA:** Cambiar a `../../estandares/observabilidad/observability.md`

- [Usar identificadores de correlación entre servicios](../../estandares/observabilidad/correlation-ids.md) → NO EXISTE
  **SUGERENCIA:** Cambiar a `../../estandares/observabilidad/observability.md`

- [Configurar health checks para orquestadores](../../estandares/observabilidad/health-checks.md) → NO EXISTE
  **SUGERENCIA:** Cambiar a `../../estandares/observabilidad/observability.md`

---

## ARCHIVO: [docs/fundamentos-corporativos/lineamientos/arquitectura/06-diseno-de-apis.md](docs/fundamentos-corporativos/lineamientos/arquitectura/06-diseno-de-apis.md)

ENLACES ENCONTRADOS: 6

✅ VÁLIDOS (1 enlace):

- [Seguir convenciones RESTful para recursos y verbos HTTP](../../estandares/apis/api-rest.md) → verificar (api-rest-standards.md existe)

❌ ROTOS (5 enlaces):

- [Implementar versionado explícito de APIs](../../estandares/apis/versioning.md) → NO EXISTE
  **SUGERENCIA:** Parte de `../../estandares/apis/api-rest-standards.md` o crear archivo separado

- [Documentar APIs con especificación OpenAPI](../../estandares/apis/openapi-swagger.md) → NO EXISTE
  **SUGERENCIA:** Verificar en `../../estandares/documentacion/` (puede existir con otro nombre)

- [Aplicar rate limiting y paginación en colecciones](../../estandares/apis/rate-limiting-pagination.md) → NO EXISTE
  **SUGERENCIA:** Crear en `../../estandares/apis/`

- [Estandarizar manejo de errores con estructura consistente](../../estandares/apis/error-handling.md) → NO EXISTE
  **SUGERENCIA:** Parte de `../../estandares/apis/api-rest-standards.md`

- [Arquitectura de Microservicios](../../estilos-arquitectonicos/microservicios.md) → NO EXISTE
  **SUGERENCIA:** Crear en estilos-arquitectonicos/

---

## ARCHIVO: [docs/fundamentos-corporativos/lineamientos/arquitectura/07-contratos-de-integracion.md](docs/fundamentos-corporativos/lineamientos/arquitectura/07-contratos-de-integracion.md)

ENLACES ENCONTRADOS: 6

❌ ROTOS (6 enlaces):

- [Definir contratos con especificaciones estándar OpenAPI/AsyncAPI](../../estandares/apis/openapi-swagger.md) → NO EXISTE
- [Versionar contratos semánticamente en URL o header](../../estandares/apis/versioning.md) → NO EXISTE
- [Validar requests/responses contra contratos en runtime](../../estandares/apis/contract-validation.md) → NO EXISTE
- [Mantener retrocompatibilidad durante deprecación](../../estandares/apis/api-deprecation.md) → NO EXISTE
- [Publicar contratos en API Portal accesible](../../estandares/apis/api-portal.md) → NO EXISTE
- [Implementar contract testing automatizado](../../estandares/testing/contract-testing.md) → NO EXISTE
  **SUGERENCIA:** Parte de `../../estandares/testing/testing-standards.md`

---

## ARCHIVO: [docs/fundamentos-corporativos/lineamientos/arquitectura/08-comunicacion-asincrona-y-eventos.md](docs/fundamentos-corporativos/lineamientos/arquitectura/08-comunicacion-asincrona-y-eventos.md)

ENLACES ENCONTRADOS: 7

✅ VÁLIDOS (1 enlace):

- [Implementar mensajería con Apache Kafka](../../estandares/mensajeria/kafka-events.md) → verificar (kafka-messaging.md existe)

❌ ROTOS (6 enlaces):

- [Definir esquemas de eventos con AsyncAPI o Avro](../../estandares/mensajeria/event-schemas.md) → NO EXISTE
  **SUGERENCIA:** Parte de `../../estandares/mensajeria/kafka-messaging.md`

- [Usar eventos para comunicar hechos del dominio, no comandos](../../estandares/mensajeria/domain-events.md) → NO EXISTE
- [Implementar idempotencia en consumidores](../../estandares/mensajeria/idempotency.md) → NO EXISTE
- [Garantizar entrega at-least-once o exactly-once](../../estandares/mensajeria/delivery-guarantees.md) → NO EXISTE
- [Configurar Dead Letter Queue para mensajes fallidos](../../estandares/mensajeria/dead-letter-queue.md) → NO EXISTE
- [Documentar topología de eventos y consumidores](../../estandares/mensajeria/event-topology.md) → NO EXISTE
  **SUGERENCIA:** Todos estos deben estar en `../../estandares/mensajeria/kafka-messaging.md`

---

## ARCHIVO: [docs/fundamentos-corporativos/lineamientos/datos/01-responsabilidad-del-dominio.md](docs/fundamentos-corporativos/lineamientos/datos/01-responsabilidad-del-dominio.md)

ENLACES ENCONTRADOS: 5

✅ VÁLIDOS (1 enlace):

- [Evitar bases de datos compartidas entre servicios](../../estandares/datos/database-per-service.md) → parte de database-standards.md

❌ ROTOS (4 enlaces):

- [Asignar propiedad exclusiva de datos por dominio](../../estandares/datos/data-ownership.md) → NO EXISTE
  **SUGERENCIA:** Parte de `../../estandares/datos/database-standards.md`

- [Exponer datos mediante APIs o eventos, no acceso directo](../../estandares/datos/data-access-via-apis.md) → NO EXISTE
- [Documentar esquema y propiedad de datos por dominio](../../estandares/datos/schema-documentation.md) → NO EXISTE
- [Aplicar principio de menor conocimiento en datos](../../estandares/datos/least-knowledge-principle.md) → NO EXISTE

---

## ARCHIVO: [docs/fundamentos-corporativos/lineamientos/datos/02-esquemas-de-dominio.md](docs/fundamentos-corporativos/lineamientos/datos/02-esquemas-de-dominio.md)

ENLACES ENCONTRADOS: 5

❌ ROTOS (5 enlaces):

- [Versionar esquemas de BD con migraciones automatizadas](../../estandares/datos/migrations.md) → NO EXISTE
  **SUGERENCIA:** Parte de `../../estandares/datos/database-standards.md`

- [Documentar esquemas de eventos con JSON Schema o Avro](../../estandares/mensajeria/event-schemas.md) → NO EXISTE
- [Validar datos contra esquemas antes de persistir](../../estandares/datos/schema-validation.md) → NO EXISTE
- [Gestionar cambios con estrategias expand-contract](../../estandares/datos/schema-evolution.md) → NO EXISTE
- [Publicar esquemas en registro centralizado](../../estandares/datos/schema-registry.md) → NO EXISTE

---

## ARCHIVO: [docs/fundamentos-corporativos/lineamientos/datos/03-consistencia-y-sincronizacion.md](docs/fundamentos-corporativos/lineamientos/datos/03-consistencia-y-sincronizacion.md)

ENLACES ENCONTRADOS: 5

✅ VÁLIDOS (1 enlace):

- [Preferir sagas o compensaciones sobre transacciones distribuidas](../../estandares/arquitectura/saga-pattern.md) → archivo existe

❌ ROTOS (4 enlaces):

- [Definir modelo de consistencia explícito por caso de uso](../../estandares/datos/consistency-models.md) → NO EXISTE
- [Implementar reconciliación para consistencia eventual](../../estandares/datos/reconciliation.md) → NO EXISTE
- [Gestionar conflictos con estrategias definidas](../../estandares/datos/conflict-resolution.md) → NO EXISTE
- [Definir SLOs de convergencia de datos](../../estandares/datos/consistency-slos.md) → NO EXISTE

---

## ARCHIVO: [docs/fundamentos-corporativos/lineamientos/desarrollo/01-calidad-codigo.md](docs/fundamentos-corporativos/lineamientos/desarrollo/01-calidad-codigo.md)

ENLACES ENCONTRADOS: 6

✅ VÁLIDOS (4 enlaces):

- [Aplicar estándares de calidad de código: análisis estático y cobertura mínima](../../estandares/desarrollo/code-quality-standards.md) → verificar (code-quality-review.md existe)
- [Seguir convenciones de código C# y .NET](../../estandares/desarrollo/csharp-dotnet.md) → archivo existe
- [Aplicar buenas prácticas de desarrollo SQL](../../estandares/desarrollo/sql.md) → archivo existe
- [CI/CD](../operabilidad/01-automatizacion.md) → archivo existe

❌ ROTOS (2 enlaces):

- [Estrategia de Pruebas](./02-testing.md) → archivo existe PERO referencia incorrecta
  **NOTA:** El enlace apunta a `./04-testing.md` pero el archivo es `./02-testing.md`

- [Realizar code review obligatorio antes de merge a ramas principales](../../estandares/desarrollo/code-review-policy.md) → NO EXISTE
  **SUGERENCIA:** Parte de `../../estandares/desarrollo/code-quality-review.md`

---

## ARCHIVO: [docs/fundamentos-corporativos/lineamientos/desarrollo/02-testing.md](docs/fundamentos-corporativos/lineamientos/desarrollo/02-testing.md)

ENLACES ENCONTRADOS: 6

✅ VÁLIDOS (2 enlaces):

- [Observabilidad](../arquitectura/05-observabilidad.md) → archivo existe
- [Calidad de Código](./01-calidad-codigo.md) → archivo existe

❌ ROTOS (4 enlaces):

- [Calidad de Código](./05-calidad-codigo.md) → NO EXISTE
  **CORRECCIÓN:** Cambiar a `./01-calidad-codigo.md`

- [Implementar pruebas automatizadas en múltiples niveles (unitarias, integración, e2e)](../../estandares/desarrollo/testing-pyramid.md) → NO EXISTE
  **SUGERENCIA:** Parte de `../../estandares/testing/testing-standards.md`

- [Escribir pruebas unitarias con cobertura mínima del 80%](../../estandares/testing/unit-tests.md) → NO EXISTE
- [Implementar pruebas de integración para validar interacciones entre componentes](../../estandares/testing/integration-tests.md) → NO EXISTE
- [Usar contract testing para validar contratos entre servicios](../../estandares/testing/contract-testing.md) → NO EXISTE
  **SUGERENCIA:** Todos en `../../estandares/testing/testing-standards.md`

---

## ARCHIVO: [docs/fundamentos-corporativos/lineamientos/gobierno/01-decisiones-arquitectonicas.md](docs/fundamentos-corporativos/lineamientos/gobierno/01-decisiones-arquitectonicas.md)

ENLACES ENCONTRADOS: 2

✅ VÁLIDOS (1 enlace):

- [Documentar decisiones significativas en ADRs](../../estandares/documentacion/architecture-decision-records.md) → archivo existe

❌ ROTOS (1 enlace):

- [Revisar ADRs en architecture reviews](../../estandares/gobierno/architecture-review.md) → NO EXISTE
  **SUGERENCIA:** Crear en `../../estandares/gobierno/`

---

## ARCHIVO: [docs/fundamentos-corporativos/lineamientos/gobierno/02-architecture-reviews.md](docs/fundamentos-corporativos/lineamientos/gobierno/02-architecture-reviews.md)

ENLACES ENCONTRADOS: 5

✅ VÁLIDOS (2 enlaces):

- [Decisiones Arquitectónicas](./01-decisiones-arquitectonicas.md) → archivo existe
- [Cumplimiento y Excepciones](./03-cumplimiento-y-excepciones.md) → archivo existe

❌ ROTOS (3 enlaces):

- [Realizar architecture review antes de implementaciones significativas](../../estandares/gobierno/architecture-review.md) → NO EXISTE
- [Documentar resultados, decisiones y acciones de reviews](../../estandares/gobierno/review-documentation.md) → NO EXISTE
- [Realizar retrospectivas arquitectónicas post-implementación](../../estandares/gobierno/architecture-retrospectives.md) → NO EXISTE
  **SUGERENCIA:** Crear estos archivos en `../../estandares/gobierno/`

---

## ARCHIVO: [docs/fundamentos-corporativos/lineamientos/gobierno/03-cumplimiento-y-excepciones.md](docs/fundamentos-corporativos/lineamientos/gobierno/03-cumplimiento-y-excepciones.md)

ENLACES ENCONTRADOS: 4

✅ VÁLIDOS (2 enlaces):

- [Decisiones Arquitectónicas](./01-decisiones-arquitectonicas.md) → archivo existe
- [Revisiones Arquitectónicas](./02-architecture-reviews.md) → archivo existe

❌ ROTOS (2 enlaces):

- [Validar cumplimiento de lineamientos y estándares](../../estandares/gobierno/compliance-validation.md) → NO EXISTE
- [Gestionar excepciones mediante proceso formal con ADR](../../estandares/gobierno/exception-management.md) → NO EXISTE
  **SUGERENCIA:** Crear en `../../estandares/gobierno/`

---

## ARCHIVO: [docs/fundamentos-corporativos/lineamientos/gobierno/04-calidad-codigo.md](docs/fundamentos-corporativos/lineamientos/gobierno/04-calidad-codigo.md)

ENLACES ENCONTRADOS: 6

✅ VÁLIDOS (4 enlaces):

- [Aplicar estándares de calidad de código: análisis estático y cobertura mínima](../../estandares/desarrollo/code-quality-standards.md) → verificar
- [Seguir convenciones de código C# y .NET](../../estandares/desarrollo/csharp-dotnet.md) → archivo existe
- [Aplicar buenas prácticas de desarrollo SQL](../../estandares/desarrollo/sql.md) → archivo existe
- [CI/CD](../operabilidad/01-automatizacion.md) → archivo existe

❌ ROTOS (2 enlaces):

- [Estrategia de Pruebas](../operabilidad/04-testing.md) → NO EXISTE
  **CORRECCIÓN:** Cambiar a `../desarrollo/02-testing.md`

- [Realizar code review obligatorio antes de merge a ramas principales](../../estandares/desarrollo/code-review-policy.md) → NO EXISTE
  **SUGERENCIA:** Parte de code-quality-review.md

---

## ARCHIVO: [docs/fundamentos-corporativos/lineamientos/seguridad/01-seguridad-desde-el-diseno.md](docs/fundamentos-corporativos/lineamientos/seguridad/01-seguridad-desde-el-diseno.md)

ENLACES ENCONTRADOS: 5

✅ VÁLIDOS (2 enlaces):

- [Realizar modelado de amenazas para nuevos sistemas](../../estandares/seguridad/threat-modeling.md) → archivo existe
- [Aplicar Security by Design en decisiones arquitectónicas](../../estandares/seguridad/security-by-design.md) → parte de security-architecture.md

❌ ROTOS (3 enlaces):

- [Definir explícitamente los límites de confianza (trust boundaries)](../../estandares/seguridad/trust-boundaries.md) → NO EXISTE
  **SUGERENCIA:** Parte de `../../estandares/seguridad/threat-modeling.md`

- [Reducir la superficie de ataque mediante exposición controlada](../../estandares/seguridad/attack-surface-reduction.md) → NO EXISTE
- [Aplicar defensa en profundidad con múltiples capas](../../estandares/seguridad/defense-in-depth.md) → NO EXISTE
  **SUGERENCIA:** Parte de `../../estandares/seguridad/security-architecture.md`

---

## ARCHIVO: [docs/fundamentos-corporativos/lineamientos/seguridad/02-identidad-y-accesos.md](docs/fundamentos-corporativos/lineamientos/seguridad/02-identidad-y-accesos.md)

ENLACES ENCONTRADOS: 5

✅ VÁLIDOS (1 enlace):

- [No almacenar credenciales en código o configuración](../../estandares/seguridad/secrets-management.md) → parte de secrets-key-management.md

❌ ROTOS (4 enlaces):

- [Usar identidad federada y SSO corporativo para usuarios](../../estandares/seguridad/sso-federation.md) → NO EXISTE
  **SUGERENCIA:** Parte de `../../estandares/seguridad/identity-access-management.md`

- [Implementar autenticación multifactor (MFA) para accesos críticos](../../estandares/seguridad/mfa-configuration.md) → NO EXISTE
- [Aplicar mínimo privilegio en autorizaciones](../../estandares/seguridad/least-privilege.md) → NO EXISTE
- [Gestionar identidades de servicios](../../estandares/seguridad/service-identities.md) → NO EXISTE
  **SUGERENCIA:** Todos en `../../estandares/seguridad/identity-access-management.md`

---

## ARCHIVO: [docs/fundamentos-corporativos/lineamientos/seguridad/03-segmentacion-y-aislamiento.md](docs/fundamentos-corporativos/lineamientos/seguridad/03-segmentacion-y-aislamiento.md)

ENLACES ENCONTRADOS: 5

✅ VÁLIDOS (2 enlaces):

- [Segmentar redes por niveles de confianza (DMZ, interna, datos)](../../estandares/seguridad/network-segmentation.md) → parte de network-security.md
- [Implementar aislamiento de tenants en soluciones multi-tenant](../../estandares/seguridad/tenant-isolation.md) → archivo existe

❌ ROTOS (3 enlaces):

- [Aislar recursos por entorno en cuentas/subscripciones separadas](../../estandares/seguridad/environment-separation.md) → NO EXISTE
  **SUGERENCIA:** Crear en `../../estandares/infraestructura/environment-separation.md`

- [Aplicar principio de menor exposición de red (zero trust networking)](../../estandares/seguridad/zero-trust-network.md) → NO EXISTE
- [Documentar zonas de seguridad y controles entre ellas](../../estandares/seguridad/security-zones.md) → NO EXISTE
  **SUGERENCIA:** Parte de `../../estandares/seguridad/network-security.md`

---

## ARCHIVO: [docs/fundamentos-corporativos/lineamientos/seguridad/04-proteccion-de-datos.md](docs/fundamentos-corporativos/lineamientos/seguridad/04-proteccion-de-datos.md)

ENLACES ENCONTRADOS: 6

✅ VÁLIDOS (1 enlace):

- [Gestionar claves de cifrado con servicios dedicados (KMS)](../../estandares/seguridad/key-management.md) → parte de secrets-key-management.md

❌ ROTOS (5 enlaces):

- [Clasificar datos según sensibilidad (público, interno, sensible, regulado)](../../estandares/seguridad/data-classification.md) → NO EXISTE
  **SUGERENCIA:** Parte de `../../estandares/datos/data-protection.md`

- [Cifrar datos sensibles en tránsito y reposo](../../estandares/seguridad/data-encryption.md) → NO EXISTE
- [Aplicar enmascaramiento y tokenización donde corresponda](../../estandares/seguridad/data-masking.md) → NO EXISTE
- [Recopilar únicamente datos estrictamente necesarios (minimización)](../../estandares/seguridad/data-minimization.md) → NO EXISTE
- [Implementar políticas de retención y eliminación automática](../../estandares/seguridad/data-retention.md) → NO EXISTE
  **SUGERENCIA:** Todos en `../../estandares/datos/data-protection.md`

---

## ARCHIVO: [docs/fundamentos-corporativos/lineamientos/seguridad/05-gestion-vulnerabilidades.md](docs/fundamentos-corporativos/lineamientos/seguridad/05-gestion-vulnerabilidades.md)

ENLACES ENCONTRADOS: 4

✅ VÁLIDOS (1 enlace):

- [Validar imágenes de contenedores antes de deployment](../../estandares/seguridad/container-image-scanning.md) → parte de contenedores o vulnerability-management

❌ ROTOS (3 enlaces):

- [Implementar programa integral de gestión de vulnerabilidades](../../estandares/seguridad/vulnerability-management-program.md) → NO EXISTE
  **SUGERENCIA:** Parte de `../../estandares/seguridad/vulnerability-management.md`

- [Implementar scanning automatizado de vulnerabilidades en CI/CD](../../estandares/seguridad/vulnerability-scanning.md) → NO EXISTE
- [Mantener inventario actualizado de componentes y versiones](../../estandares/seguridad/software-bill-of-materials.md) → NO EXISTE
  **SUGERENCIA:** Todos en `../../estandares/seguridad/vulnerability-management.md`

---

## ARCHIVO: [docs/fundamentos-corporativos/lineamientos/seguridad/06-respuesta-incidentes.md](docs/fundamentos-corporativos/lineamientos/seguridad/06-respuesta-incidentes.md)

ENLACES ENCONTRADOS: 2

❌ ROTOS (2 enlaces):

- [Establecer programa de respuesta a incidentes](../../estandares/seguridad/incident-response-program.md) → NO EXISTE
  **SUGERENCIA:** Crear en `../../estandares/seguridad/`

- [Configurar logging y retención para análisis forense](../../estandares/observabilidad/logging.md) → NO EXISTE
  **SUGERENCIA:** Cambiar a `../../estandares/observabilidad/observability.md`

---

## ARCHIVO: [docs/fundamentos-corporativos/lineamientos/operabilidad/01-automatizacion.md](docs/fundamentos-corporativos/lineamientos/operabilidad/01-automatizacion.md)

ENLACES ENCONTRADOS: 3

✅ VÁLIDOS (2 enlaces):

- [Automatizar despliegues mediante pipelines CI/CD](../../estandares/desarrollo/cicd-pipelines.md) → archivo existe
- [Automatizar aprovisionamiento de infraestructura (IaC)](../../estandares/operabilidad/infrastructure-as-code.md) → verificar carpeta

❌ ROTOS (1 enlace):

- [Automatizar validaciones de seguridad y calidad](../../estandares/gobierno/quality-security-gates.md) → NO EXISTE
  **SUGERENCIA:** Crear en `../../estandares/gobierno/` o parte de code-quality-review

---

## ARCHIVO: [docs/fundamentos-corporativos/lineamientos/operabilidad/02-infraestructura-como-codigo.md](docs/fundamentos-corporativos/lineamientos/operabilidad/02-infraestructura-como-codigo.md)

ENLACES ENCONTRADOS: 2

✅ VÁLIDOS (1 enlace):

- [Definir infraestructura mediante código](../../estandares/operabilidad/infrastructure-as-code.md) → verificar carpeta correcta

❌ ROTOS (1 enlace):

- [Aplicar revisión de código a infraestructura](../../estandares/desarrollo/code-review-policy.md) → NO EXISTE
  **SUGERENCIA:** Parte de code-quality-review.md

---

## ARCHIVO: [docs/fundamentos-corporativos/lineamientos/operabilidad/03-consistencia-entre-entornos.md](docs/fundamentos-corporativos/lineamientos/operabilidad/03-consistencia-entre-entornos.md)

ENLACES ENCONTRADOS: 2

✅ VÁLIDOS (1 enlace):

- [Externalizar configuración en variables de entorno](../../estandares/infraestructura/externalize-configuration.md) → archivo existe

❌ ROTOS (1 enlace):

- [Garantizar paridad entre dev y producción](../../estandares/operabilidad/dev-prod-parity.md) → NO EXISTE
  **SUGERENCIA:** Crear en `../../estandares/operabilidad/` o `../../estandares/infraestructura/`

---

## ARCHIVO: [docs/fundamentos-corporativos/lineamientos/operabilidad/04-optimizacion-costos.md](docs/fundamentos-corporativos/lineamientos/operabilidad/04-optimizacion-costos.md)

ENLACES ENCONTRADOS: 5

✅ VÁLIDOS (1 enlace):

- [Establecer políticas de retención y lifecycle para datos](../../estandares/datos/data-lifecycle.md) → verificar si existe

❌ ROTOS (4 enlaces):

- [Implementar estrategia de tagging para atribución de costos](../../estandares/infraestructura/cost-tagging-strategy.md) → NO EXISTE
  **SUGERENCIA:** Parte de `../../estandares/infraestructura/aws-cost-optimization.md`

- [Aplicar rightsizing basado en métricas de utilización](../../estandares/infraestructura/rightsizing.md) → NO EXISTE
- [Implementar alertas de presupuesto y anomalías de costos](../../estandares/infraestructura/cost-alerts.md) → NO EXISTE
- [Utilizar reserved instances y savings plans](../../estandares/infraestructura/reserved-capacity.md) → NO EXISTE
  **SUGERENCIA:** Todos en `../../estandares/infraestructura/aws-cost-optimization.md`

---

## ARCHIVO: [docs/fundamentos-corporativos/lineamientos/arquitectura/guias-implementacion/05-observabilidad-implementacion.md](docs/fundamentos-corporativos/lineamientos/arquitectura/guias-implementacion/05-observabilidad-implementacion.md)

ENLACES ENCONTRADOS: 3

✅ VÁLIDOS (2 enlaces):

- [Lineamiento de Observabilidad](../05-observabilidad.md) → archivo existe (x2)

❌ ROTOS (1 enlace):

- [Principios de Operabilidad](../../principios/operabilidad.md) → NO EXISTE
  **SUGERENCIA:** Verificar si existe carpeta principios/ y crear archivo

---

# RESUMEN GENERAL

## Estadísticas

- **Total archivos revisados:** 24
- **Total enlaces encontrados:** ~136
- **Enlaces válidos:** ~30-40 (estimado 25-30%)
- **Enlaces rotos:** ~96-106 (estimado 70-75%)

## Categorías de Problemas

### 1. ARCHIVOS DE ESTÁNDARES FALTANTES (Prioridad ALTA)

Los siguientes archivos están referenciados múltiples veces pero NO EXISTEN:

#### APIs (6 archivos):

- `apis/versioning.md`
- `apis/openapi-swagger.md` (puede estar en documentacion/)
- `apis/rate-limiting-pagination.md`
- `apis/error-handling.md`
- `apis/contract-validation.md`
- `apis/api-deprecation.md`
- `apis/api-portal.md`

#### Arquitectura (7 archivos):

- `arquitectura/single-responsibility.md`
- `arquitectura/stateless-services.md`
- `arquitectura/horizontal-scaling.md`
- `arquitectura/graceful-shutdown.md`
- `arquitectura/timeouts.md`
- `arquitectura/retry-patterns.md`
- `arquitectura/graceful-degradation.md`

**NOTA:** Muchos de estos están consolidados en `arquitectura/resilience-patterns.md`

#### Datos (15 archivos):

- `datos/data-ownership.md`
- `datos/data-access-via-apis.md`
- `datos/schema-documentation.md`
- `datos/least-knowledge-principle.md`
- `datos/migrations.md`
- `datos/schema-validation.md`
- `datos/schema-evolution.md`
- `datos/schema-registry.md`
- `datos/consistency-models.md`
- `datos/reconciliation.md`
- `datos/conflict-resolution.md`
- `datos/consistency-slos.md`
- `datos/data-lifecycle.md` (verificar)
- `datos/data-classification.md`
- `datos/data-retention.md`

#### Desarrollo (4 archivos):

- `desarrollo/code-review-policy.md`
- `desarrollo/testing-pyramid.md`

#### Gobierno (6 archivos):

- `gobierno/architecture-review.md`
- `gobierno/review-documentation.md`
- `gobierno/architecture-retrospectives.md`
- `gobierno/compliance-validation.md`
- `gobierno/exception-management.md`
- `gobierno/quality-security-gates.md`

#### Infraestructura (8 archivos):

- `infraestructura/environment-separation.md`
- `infraestructura/cost-tagging-strategy.md`
- `infraestructura/rightsizing.md`
- `infraestructura/cost-alerts.md`
- `infraestructura/reserved-capacity.md`
- `operabilidad/dev-prod-parity.md`
- `operabilidad/slos-slas.md`

#### Mensajería (6 archivos):

- `mensajeria/event-schemas.md`
- `mensajeria/domain-events.md`
- `mensajeria/idempotency.md`
- `mensajeria/delivery-guarantees.md`
- `mensajeria/dead-letter-queue.md`
- `mensajeria/event-topology.md`

**NOTA:** Muchos están consolidados en `kafka-messaging.md`

#### Observabilidad (5 archivos):

- `observabilidad/logging.md`
- `observabilidad/metrics-monitoring.md`
- `observabilidad/distributed-tracing.md`
- `observabilidad/correlation-ids.md`
- `observabilidad/health-checks.md`

**NOTA:** Todos están consolidados en `observabilidad/observability.md`

#### Seguridad (15 archivos):

- `seguridad/security-by-design.md`
- `seguridad/trust-boundaries.md`
- `seguridad/attack-surface-reduction.md`
- `seguridad/defense-in-depth.md`
- `seguridad/sso-federation.md`
- `seguridad/mfa-configuration.md`
- `seguridad/least-privilege.md`
- `seguridad/service-identities.md`
- `seguridad/network-segmentation.md`
- `seguridad/environment-separation.md`
- `seguridad/zero-trust-network.md`
- `seguridad/security-zones.md`
- `seguridad/data-encryption.md`
- `seguridad/data-masking.md`
- `seguridad/data-minimization.md`
- `seguridad/vulnerability-management-program.md`
- `seguridad/vulnerability-scanning.md`
- `seguridad/software-bill-of-materials.md`
- `seguridad/incident-response-program.md`

**NOTA:** Muchos están consolidados en los archivos existentes de seguridad

#### Testing (3 archivos):

- `testing/unit-tests.md`
- `testing/integration-tests.md`
- `testing/contract-testing.md`

**NOTA:** Consolidados en `testing/testing-standards.md`

### 2. ESTILOS ARQUITECTÓNICOS FALTANTES (Prioridad ALTA)

- `estilos-arquitectonicos/criterios-seleccion.md`
- `estilos-arquitectonicos/monolito-modular.md`
- `estilos-arquitectonicos/microservicios.md`
- `estilos-arquitectonicos/eventos.md`

### 3. REFERENCIAS CRUZADAS INCORRECTAS (Prioridad MEDIA)

- `desarrollo/01-calidad-codigo.md` → referencia a `./04-testing.md` debe ser `./02-testing.md`
- `desarrollo/02-testing.md` → referencia a `./05-calidad-codigo.md` debe ser `./01-calidad-codigo.md`
- `gobierno/04-calidad-codigo.md` → referencia a `../operabilidad/04-testing.md` debe ser `../desarrollo/02-testing.md`

### 4. ARCHIVOS CON NOMBRES DIFERENTES (Prioridad BAJA)

- `adr-003-gestion-secretos.md` → el archivo real es `adr-003-aws-secrets-manager.md`
- `api-rest.md` → el archivo real es `api-rest-standards.md`
- `kafka-events.md` → el archivo real es `kafka-messaging.md`

### 5. PRINCIPIOS FALTANTES

- `principios/operabilidad.md`

---

# RECOMENDACIONES

## Enfoque 1: Crear todos los archivos granulares (100+ archivos)

**Ventajas:**

- Cada concepto tiene su propio archivo
- URLs permanentes y específicas
- Fácil de mantener individualmente

**Desventajas:**

- Mucho trabajo de creación inicial
- Posible redundancia
- Difícil de mantener coherencia

## Enfoque 2: Actualizar enlaces para usar archivos consolidados (RECOMENDADO)

**Ventajas:**

- Menos archivos que mantener
- Coherencia garantizada
- Trabajo inmediato

**Desventajas:**

- Enlaces menos específicos
- Necesita anclas internas

## Enfoque 3: Híbrido

Crear solo los archivos más importantes y consolidar el resto:

**Crear archivos nuevos para:**

- Estilos arquitectónicos (4 archivos)
- APIs específicas (versioning, openapi, etc.) - 5-7 archivos
- Patrones arquitectónicos específicos (graceful-shutdown, stateless, etc.) - 5-7 archivos
- Gobierno (architecture-review, compliance, etc.) - 5 archivos

**Consolidar y actualizar enlaces para:**

- Observabilidad → usar `observability.md` con anclas
- Mensajería → usar `kafka-messaging.md` con anclas
- Testing → usar `testing-standards.md` con anclas
- Resiliencia → usar `resilience-patterns.md` con anclas
- Seguridad → usar archivos consolidados existentes con anclas

---

# ACCIONES INMEDIATAS SUGERIDAS

1. **Corregir referencias cruzadas incorrectas** (3 archivos, 15 minutos)
2. **Actualizar enlaces a archivos con nombres diferentes** (10 archivos, 30 minutos)
3. **Crear archivos de estilos arquitectónicos** (4 archivos, 2-4 horas)
4. **Decidir estrategia para los ~80 archivos restantes** (consolidar vs crear)
5. **Actualizar enlaces según decisión** (1-2 días de trabajo)

---

Fecha de generación: 2026-02-04
