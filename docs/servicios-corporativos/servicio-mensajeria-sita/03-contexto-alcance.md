# 3. Contexto y alcance del sistema

Este capítulo describe el contexto funcional y técnico del **Sistema SITA Messaging**, delimitando claramente su alcance, actores externos y relaciones clave con otros sistemas corporativos.

![Servicios Corporativos - Vista de Contexto](/diagrams/servicios-corporativos/corporate_services.png)

*Figura 3.1: Vista de contexto de los Servicios Corporativos*

![Sistema SITA Messaging - Vista de Contexto](/diagrams/servicios-corporativos/sita_messaging_system.png)

*Figura 3.2: Vista de contexto del Sistema SITA Messaging*

## 3.1 Alcance del sistema

| Aspecto      | Descripción                                                                 |
|--------------|-----------------------------------------------------------------------------|
| **Incluido** | Generación y transmisión de mensajes SITA, plantillas, enrutamiento AFTN, integración con Track & Trace, monitoreo y auditoría, cumplimiento de protocolos aeronáuticos. |
| **Excluido** | Lógica de negocio de vuelos, gestión de itinerarios, edición de contenido de mensajes, administración de usuarios finales. |

## 3.2 Actores y sistemas externos

| Actor/Sistema           | Rol         | Interacción principal                        |
|------------------------|-------------|---------------------------------------------|
| **Track & Trace System** | Proveedor   | Provee eventos operacionales para mensajería |
| **Red SITA Global**     | Destinatario| Transmisión y recepción de mensajes SITA     |
| **Partners Aeronáuticos** | Destinatario| Recepción de mensajes y coordinación operativa|
| **Sistema Identidad**   | Proveedor   | Autenticación y autorización de servicios    |
| **Observabilidad**      | Consumidor  | Consumo de métricas, logs y alertas          |

---

> Para más detalles sobre integración y restricciones, ver secciones 2 y 4.
