
# 2. Restricciones de la arquitectura

## 2.1 Restricciones técnicas

| Categoría         | Restricción                        | Justificación                  |
|-------------------|------------------------------------|-------------------------------|
| Plataforma        | .NET 8, ASP.NET Core               | Estándar corporativo          |
| Base de datos     | PostgreSQL                         | Robustez y ACID               |
| Cola de eventos   | SNS+SQS                            | Mensajería empresarial        |
| Contenedores      | Docker (Docker Compose)            | Portabilidad                  |
| Registro          | Serilog                            | Observabilidad                |
| Protocolos        | SITA                | Estándares aeronáuticos       |

## 2.2 Restricciones de integración y conectividad

| Sistema/Interfaz         | Protocolo/Medio      | Restricción                    | Implementación                |
|-------------------------|----------------------|-------------------------------|-------------------------------|
| Red SITA                | SITA sobre X.25/IP| Soporte protocolo legacy       | Adaptador dedicado            |
| Aerolíneas Partner      | AFTN/CIDIN           | Mensajería estándar industria  | Gateway multi-protocolo       |
| Sistemas Aeropuerto     | REST                 | Integración heterogénea        | API REST interno              |
| Track & Trace           | REST interno         | Entrega eventos tiempo real    | Cliente HTTP asíncrono        |
| Sistemas Gubernamentales| VPN/TLS              | Cumplimiento seguridad         | Túneles cifrados, certificados|

## 2.3 Restricciones de operación y mantenimiento

| Área                | Restricción                        | Justificación                        | Implementación                      |
|---------------------|------------------------------------|--------------------------------------|-------------------------------------|
| Operación 24/7      | Soporte continuo requerido         | Operaciones críticas                  | Monitoreo y alertas                 |
| Ventanas de cambio  | Mantenimiento en horarios específicos| Minimizar impacto operacional       | Ventanas de cambio controladas      |
| Modelo de soporte   | Estructura de soporte escalonado   | Procedimientos de escalamiento       | Documentación y monitoreo           |
| Recuperación ante desastres | RTO: 4h, RPO: 15min         | Continuidad de negocio               | Replicación geográfica              |

## 2.4 Restricciones organizacionales y regulatorias

| Área                | Restricción                        | Autoridad                        | Implementación                      |
|---------------------|------------------------------------|----------------------------------|-------------------------------------|
| Seguridad           | OAuth2/OIDC obligatorio, RBAC      | Keycloak, políticas internas     | Pruebas de seguridad, roles         |
| Privacidad          | Cumplimiento GDPR                  | UE                               | Anonimización, gestión de consent.  |
| Auditoría           | Trazabilidad completa              | Normativa interna                | Registros y reportes                |
| Localización        | Soporte multi-país                 | Requisito corporativo            | Configuración por país              |

## 2.5 Restricciones de calidad y monitoreo

| Aspecto             | Restricción                        | Implementación                   | Validación                          |
|---------------------|------------------------------------|----------------------------------|-------------------------------------|
| Métricas            | Monitoreo con Prometheus           | Métricas personalizadas          | Paneles y alertas                   |
| Registro de eventos | Centralizado con Serilog           | Registros estructurados, retención| Auditoría y monitoreo               |
| Trazabilidad        | OpenTelemetry                      | Correlación de solicitudes       | Revisión de trazas                  |
| Chequeos de salud   | ASP.NET Core Health Checks         | Endpoints /health                | Monitoreo de disponibilidad         |
