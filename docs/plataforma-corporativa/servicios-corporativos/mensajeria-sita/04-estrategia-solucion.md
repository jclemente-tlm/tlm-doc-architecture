
# 4. Estrategia de solución

## 4.1 Decisiones clave

| Decisión         | Alternativa elegida         | Justificación                       |
|------------------|----------------------------|-------------------------------------|
| Arquitectura     | Procesamiento asíncrono    | Escalabilidad y desacoplamiento     |
| Plantillas       | Motor de plantillas propio | Flexibilidad para formatos SITA     |
| Almacenamiento   | Archivos y base de datos   | Cumplimiento de protocolos SITA     |
| Mensajería       | SNS+SQS                    | Integración y entrega confiable     |
| Contenedores     | Docker Compose             | Portabilidad y despliegue sencillo  |

## 4.2 Patrones y enfoques aplicados

| Patrón/Enfoque   | Propósito                        | Implementación           |
|------------------|----------------------------------|--------------------------|
| Event-driven     | Procesamiento asíncrono de eventos| SNS+SQS, .NET 8         |
| Worker Service   | Procesos background              | .NET 8                  |
| API REST         | Integración interna y externa     | ASP.NET Core            |
| Validación       | Cumplimiento de formatos SITA     | Validadores dedicados    |

## 4.3 Estrategia de integración y seguridad

- Conexión segura a red SITA mediante VPN y TLS 1.3.
- Autenticación y autorización centralizada con Keycloak (OAuth2/OIDC, RBAC).
- Validación y trazabilidad de mensajes con firmas digitales y registros estructurados.
- Gestión de certificados y control de acceso por IP autorizada.

## 4.4 Estrategia de operación y monitoreo

- Monitoreo de métricas técnicas y de negocio con Prometheus y alertas configuradas.
- Registro centralizado y estructurado con Serilog.
- Chequeos de salud y disponibilidad vía endpoints dedicados.
- Soporte a operación 24/7 y recuperación ante desastres con replicación geográfica.

## 4.5 Estrategia de despliegue

- Despliegue de servicios en contenedores Docker Compose.
- Ambientes diferenciados: desarrollo (simuladores), pruebas (entorno SITA test), producción (red SITA real).

## Referencias

- [IATA Type B Message Standards](https://www.iata.org/standards/)
- [ICAO Aeronautical Telecommunications](https://www.icao.int/safety/acp/)
