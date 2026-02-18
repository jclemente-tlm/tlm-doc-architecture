---
id: autonomia-de-servicios
sidebar_position: 10
title: Autonomía de Servicios
description: Servicios capaces de evolucionar, desplegarse y operar de forma independiente
---

# Autonomía de Servicios

Los servicios deben ser autónomos, capaces de evolucionar, desplegarse y operar independientemente sin coordinación sincronizada con otros servicios. Sin autonomía, los despliegues requieren coordinación entre equipos, los cambios quedan bloqueados por dependencias externas y la escalabilidad organizacional se limita. La autonomía permite que cada servicio asuma responsabilidad completa sobre comportamiento, datos, evolución y ciclo de vida, reduciendo dependencias operativas y permitiendo que equipos entreguen valor continuamente.

**Este lineamiento aplica a:** servicios en microservicios, bounded contexts, componentes modulares con ciclos de vida independientes, equipos autónomos con responsabilidad end-to-end.

## Estándares Obligatorios

- [Implementar database per service](../../estandares/datos/database-per-service.md)
- [Prohibir bases de datos compartidas](../../estandares/datos/no-shared-database.md)
- [Habilitar despliegue independiente](../../estandares/desarrollo/independent-deployment.md)
- [Versionar APIs para evolución independiente](../../estandares/apis/api-versioning.md)
- [Mantener retrocompatibilidad en contratos](../../estandares/apis/api-backward-compatibility.md)
- [Usar comunicación asíncrona para desacoplamiento](../../estandares/mensajeria/async-messaging.md)
- [Implementar circuit breakers y degradación graceful](../../estandares/arquitectura/circuit-breaker.md)
- [Definir bounded contexts claros](../../estandares/arquitectura/bounded-contexts.md)
- [Implementar observabilidad completa por servicio](../../estandares/observabilidad/observability-stack.md)

## Referencias Relacionadas

- [Propiedad de Datos](../../datos/03-propiedad-de-datos.md)
- [Descomposición y Límites](02-descomposicion-y-limites.md)
- [Modelado de Dominio](09-modelado-de-dominio.md)
