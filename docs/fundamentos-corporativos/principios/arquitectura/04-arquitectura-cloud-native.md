---
id: 04-nube
sidebar_position: 4
title: Nube
---

<!-- ## Principios

- Usa servicios administrados siempre que sea posible.
- Automatiza la infraestructura (IaC: Terraform, CloudFormation, Bicep).
- Aplica el principio de menor privilegio en IAM/roles.
- Diseña para alta disponibilidad y tolerancia a fallos.
- Implementa monitoreo y alertas desde el inicio.

## Buenas prácticas

- Versiona la infraestructura como código.
- Usa múltiples zonas/regiones para resiliencia.
- Protege datos en tránsito y en reposo (cifrado).
- Realiza pruebas de recuperación ante desastres.
- Documenta la arquitectura y dependencias clave. -->

# Arquitectura Cloud-Native

## Enunciado

Los sistemas deben diseñarse asumiendo infraestructuras dinámicas, distribuidas y automatizadas como condición normal de operación.

## Intención

Aprovechar elasticidad, resiliencia y automatización para soportar cargas variables y fallos parciales.

## Alcance conceptual

Aplica a sistemas desplegados sobre plataformas cloud o infraestructuras virtualizadas modernas.

No implica dependencia directa a un proveedor específico.

## Implicaciones arquitectónicas

- Los fallos se consideran inevitables.
- El escalado y la recuperación son responsabilidades del diseño.
- La infraestructura es efímera y reemplazable.
- La automatización es un supuesto arquitectónico.

## Compensaciones (trade-offs)

Reduce control directo sobre la infraestructura a cambio de mayor agilidad, escalabilidad y resiliencia.
