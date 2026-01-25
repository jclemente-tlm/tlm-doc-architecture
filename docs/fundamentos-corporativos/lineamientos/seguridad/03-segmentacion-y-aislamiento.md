---
id: segmentacion-y-aislamiento
sidebar_position: 3
title: Segmentación y Aislamiento
description: Separación de componentes y recursos por niveles de confianza
---

# Segmentación y Aislamiento

## 1. Propósito

Definir cómo segmentar y aislar componentes, servicios y datos según niveles de confianza, sensibilidad y requisitos de seguridad.

---

## 2. Alcance

Aplica a:

- Segmentación de redes y subredes
- Aislamiento de tenants (multi-tenancy)
- Separación de entornos (dev, qa, prod)
- Contenedores y orquestación
- Bases de datos y almacenamiento

---

## 3. Lineamientos Obligatorios

- Segmentar redes por niveles de confianza (DMZ, interna, datos)
- Aislar recursos por entorno (dev/qa/prod en cuentas/subscripciones separadas)
- Implementar aislamiento de tenants en soluciones multi-tenant
- Aplicar principio de menor exposición de red (zero trust networking)
- Documentar zonas de seguridad y controles entre ellas

---

## 4. Decisiones de Diseño Esperadas

- Arquitectura de segmentación de red
- Estrategia de multi-tenancy (shared DB, DB per tenant, etc.)
- Separación de entornos en cloud (cuentas, VPCs, subscripciones)
- Controles de tráfico entre segmentos (firewalls, security groups)
- Políticas de aislamiento de datos

---

## 5. Antipatrones y Prácticas Prohibidas

- Red plana sin segmentación
- Recursos de producción en misma cuenta/subscription que dev
- Multi-tenancy sin aislamiento de datos
- Acceso directo entre todas las zonas
- Ausencia de controles de tráfico entre segmentos

---

## 6. Principios Relacionados

- Zero Trust
- Defensa en Profundidad
- Mínimo Privilegio
- Seguridad desde el Diseño

---

## 7. Validación y Cumplimiento

- Revisión de diagramas de arquitectura de red
- Auditoría de configuración de firewalls y security groups
- Verificación de aislamiento de tenants
- Pruebas de penetración entre segmentos
- Documentación en ADRs de estrategia de segmentación

### Minimización de Datos

Los sistemas deben:

- Recopilar únicamente los datos estrictamente necesarios
- Exponer solo la información requerida para cada caso de uso
- Evitar replicaciones innecesarias entre sistemas o dominios

La minimización reduce la superficie de ataque y simplifica el cumplimiento normativo.

---

## Antipatrones

- Compartir modelos de datos completos entre sistemas
- Persistir información “por si acaso”
- Exponer datos sensibles en logs, eventos o mensajes
- Replicar datos sin una justificación arquitectónica clara

## Resultado Esperado

Arquitecturas que reducen riesgos y exposición mediante un manejo consciente, controlado y responsable de los datos.
