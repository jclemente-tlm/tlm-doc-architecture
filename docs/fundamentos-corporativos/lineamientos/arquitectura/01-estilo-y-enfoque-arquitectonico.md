---
id: estilo-y-enfoque-arquitectonico
sidebar_position: 1
title: Estilo y Enfoque Arquitectónico
description: Estilos arquitectónicos permitidos y criterios de selección
---

# Estilo y Enfoque Arquitectónico

## 1. Propósito

Definir los estilos arquitectónicos permitidos y criterios de selección para asegurar soluciones sostenibles, escalables y alineadas a las necesidades del negocio.

---

## 2. Alcance

Aplica a:

- Nuevas aplicaciones y sistemas
- Evolución de sistemas existentes
- Integraciones entre sistemas
- Plataformas y servicios compartidos

No aplica a:

- Configuraciones operativas menores
- Decisiones tecnológicas que no afecten el estilo arquitectónico
- Prototipos o POCs de corta duración

---

## 3. Lineamientos Obligatorios

- Seleccionar explícitamente uno de los estilos permitidos
- Documentar el estilo seleccionado en ADR
- No mezclar estilos sin justificación formal

**Estilos permitidos:**

### Monolito Modular

**Cuándo usar:** Dominios acotados, cambios poco frecuentes, equipos pequeños

- Módulos claramente separados por dominio
- Dependencias unidireccionales entre módulos
- Preparado para evolución hacia arquitectura distribuida

### Microservicios

**Cuándo usar:** Dominios independientes, cambios frecuentes, equipos autónomos

- Cada servicio representa una capacidad de negocio completa
- Autonomía total en despliegue y evolución
- Datos encapsulados (no compartir base de datos)
- Comunicación mediante contratos explícitos

### Arquitectura Orientada a Eventos

**Cuándo usar:** Desacoplamiento temporal, flujos asíncronos, alta resiliencia

- Eventos representan hechos del dominio (pasado)
- Productores no conocen a consumidores
- Tolera consistencia eventual

---

## 4. Decisiones de Diseño Esperadas

- Justificación del estilo seleccionado
- Mapeo de dominios/módulos/servicios
- Estrategia de comunicación (síncrona/asíncrona)
- Plan de evolución arquitectónica
- Límites y responsabilidades por componente

---

## 5. Antipatrones y Prácticas Prohibidas

- Seleccionar estilo por moda tecnológica
- Microservicios para sistemas simples o monolíticos
- Monolito sin separación modular clara
- Mezcla ad-hoc de estilos sin criterio
- Arquitectura distribuida sin necesidad real

---

## 6. Principios Relacionados

- Arquitectura Limpia
- [Arquitectura de Microservicios](../../estilos-arquitectonicos/microservicios.md)
- [Arquitectura Orientada a Eventos](../../estilos-arquitectonicos/eventos.md)
- Simplicidad Intencional
- Desacoplamiento y Autonomía

---

## 7. Validación y Cumplimiento

- Architecture review antes de implementación
- ADR documentando estilo y justificación
- Revisión de coherencia entre estilo y decisiones técnicas
- Auditoría de cumplimiento del estilo declarado
- Evaluación de desviaciones en retrospectivas
- Auditorías internas para verificar límites, responsabilidades y comunicación entre componentes.
