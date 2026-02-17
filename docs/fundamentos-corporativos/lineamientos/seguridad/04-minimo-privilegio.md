---
id: minimo-privilegio
sidebar_position: 4
title: Mínimo Privilegio
description: Práctica de seguridad que establece que cada usuario, componente o sistema debe operar con el nivel mínimo de privilegios necesario para cumplir su función.
tags: [lineamiento, seguridad, least-privilege, iam, rbac]
---

# Mínimo Privilegio

## Tipo de Lineamiento

**Lineamiento de Seguridad** - Implementa el principio de [Seguridad desde el Diseño](../../principios/04-seguridad-desde-el-diseno.md)

## 1. Declaración

Todo usuario, componente o sistema debe operar con el nivel mínimo de privilegios necesario para cumplir su función, y solo durante el tiempo requerido.

## 2. Justificación

Este principio busca reducir el impacto de errores, fallos de seguridad o usos indebidos, limitando el alcance de las acciones que cada actor puede realizar dentro del sistema.

Los privilegios excesivos amplifican el impacto de cualquier incidente:

- Errores de configuración
- Fallos de software
- Credenciales comprometidas
- Accesos indebidos

Cuando los sistemas otorgan más permisos de los necesarios, un fallo localizado puede convertirse en un incidente sistémico.
El principio de mínimo privilegio reduce el radio de impacto y facilita el control, la auditoría y la corrección de incidentes.

## 3. Alcance y Contexto

Este principio aplica a:

- Usuarios finales y operadores
- Servicios, procesos y componentes
- Integraciones internas y externas
- Acceso a datos, APIs, eventos y recursos de infraestructura

Incluye privilegios funcionales, operativos y de administración.

## 4. Implicaciones

- Los permisos deben definirse de forma explícita y granular.
- Los accesos deben otorgarse por necesidad, no por conveniencia.
- Los privilegios deben ser revisables, revocables y temporales cuando sea posible.
- La arquitectura debe evitar componentes con acceso excesivo o transversal.
- Las capacidades críticas deben estar claramente segregadas.

**Compensaciones (Trade-offs):**

Requiere mayor esfuerzo inicial de diseño, definición de roles y gestión de accesos, a cambio de una reducción significativa del riesgo, mayor control operativo y mejor trazabilidad de acciones.
