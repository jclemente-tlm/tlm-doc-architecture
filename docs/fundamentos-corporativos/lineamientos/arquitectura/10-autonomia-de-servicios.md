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

- [Implementar ownership completo de datos por servicio](../../estandares/datos/database-per-service.md)
- [Habilitar despliegue independiente sin coordinación](../../estandares/desarrollo/independent-deployment.md)
- [Utilizar comunicación asíncrona cuando sea posible](../../estandares/mensajeria/async-messaging.md)
- [Implementar modo degradado ante fallos de dependencias](../../estandares/arquitectura/resilience-patterns.md)
- [Definir contratos de API versionados](../../estandares/apis/api-versioning.md)

## Referencias Relacionadas

- [Propiedad de Datos](../../datos/03-propiedad-de-datos.md)
- [Descomposición y Límites](02-descomposicion-y-limites.md)
- [Modelado de Dominio](09-modelado-de-dominio.md)
