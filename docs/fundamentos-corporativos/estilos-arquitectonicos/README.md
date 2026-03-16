---
title: "Introducción"
sidebar_position: 0
description: "Patrones y estilos arquitectónicos que materializan los principios corporativos en contextos específicos."
---

## ¿Qué son los Estilos Arquitectónicos?

Los estilos arquitectónicos son **patrones organizacionales** que definen cómo estructurar sistemas de software para satisfacer requisitos específicos. A diferencia de los principios (valores universales), los estilos son **contextuales** y se seleccionan según las necesidades del proyecto.

---

## Diferencia entre Principios y Estilos

| Aspecto           | Principios                    | Estilos                       |
| ----------------- | ----------------------------- | ----------------------------- |
| **Naturaleza**    | Valores fundamentales         | Patrones organizacionales     |
| **Aplicabilidad** | Universal (siempre deseables) | Contextual (según necesidad)  |
| **Ejemplos**      | Desacoplamiento, Resiliencia  | Microservicios, Eventos       |
| **Decisión**      | Siempre se aplican            | Se seleccionan según contexto |

---

## Relación con Principios

Cada estilo arquitectónico **materializa** uno o más principios corporativos:

```mermaid
graph TD
    P1[Modularidad y Bajo Acoplamiento] --> E1[Microservicios]
    P1 --> E2[Eventos]
    P3[Resiliencia y Tolerancia a Fallos] --> E1
    P3 --> E3[Cloud Native]
    P4[Mantenibilidad y Extensibilidad] --> E4[Monolito Modular]
    P4 --> E1
```

---

## Estilos Disponibles

### 1. [Arquitectura de Microservicios](microservicios.md)

**Cuándo usar:**

- Dominios independientes claramente identificables
- Necesidad de escalabilidad independiente por capacidad
- Múltiples equipos autónomos
- Evolución continua y frecuente

**Principios que materializa:**

- Modularidad y Bajo Acoplamiento
- Mantenibilidad y Extensibilidad
- Resiliencia y Tolerancia a Fallos

---

### 2. [Arquitectura Orientada a Eventos](eventos.md)

**Cuándo usar:**

- Desacoplamiento temporal entre componentes
- Múltiples consumidores de la misma información
- Tolerancia a consistencia eventual
- Sistemas distribuidos con alta escalabilidad

**Principios que materializa:**

- Modularidad y Bajo Acoplamiento
- Resiliencia y Tolerancia a Fallos
- Mantenibilidad y Extensibilidad

---

### 3. [Arquitectura Cloud Native](cloud-native.md)

**Cuándo usar:**

- Sistemas desplegados en plataformas cloud
- Necesidad de elasticidad y escalado automático
- Tolerancia a fallos de infraestructura
- Despliegues frecuentes y automatizados

**Principios que materializa:**

- Resiliencia y Tolerancia a Fallos
- Seguridad desde el Diseño
- Modularidad y Bajo Acoplamiento

---

### 4. [Monolito Modular](monolito-modular.md)

**Cuándo usar:**

- Dominios acotados y cohesivos
- Equipos pequeños o únicos
- Cambios poco frecuentes
- Simplicidad operativa preferida

**Principios que materializa:**

- Mantenibilidad y Extensibilidad
- Modularidad y Bajo Acoplamiento

---

## Criterios de Selección

### Matriz de Decisión

| Criterio                                     | Monolito Modular | Microservicios | Eventos | Cloud Native |
| -------------------------------------------- | ---------------- | -------------- | ------- | ------------ |
| **Complejidad del dominio**                  | Baja-Media       | Alta           | Alta    | Variable     |
| **Tamaño del equipo**                        | 1-10             | 10+            | 10+     | Variable     |
| **Frecuencia de cambios**                    | Baja             | Alta           | Alta    | Alta         |
| **Necesidad de escalabilidad independiente** | No               | Sí             | Sí      | Sí           |
| **Tolerancia a consistencia eventual**       | No               | Parcial        | Sí      | Parcial      |
| **Madurez DevOps/SRE**                       | Baja             | Alta           | Alta    | Muy Alta     |

---

## Combinación de Estilos

Los estilos **no son mutuamente excluyentes**. Pueden combinarse:

- **Microservicios + Eventos:** Servicios que se comunican mediante eventos
- **Cloud Native + Microservicios:** Microservicios desplegados en cloud con auto-scaling
- **Monolito Modular + Eventos:** Módulos internos comunicándose mediante eventos de dominio

---

## Evolución entre Estilos

Los sistemas pueden evolucionar de un estilo a otro:

```
Monolito → Monolito Modular → Microservicios
                ↓
          Eventos Internos → Eventos Distribuidos
```

**Estrategias de evolución:**

- **Strangler Fig Pattern:** Reemplazar gradualmente
- **Branch by Abstraction:** Aislar antes de extraer
- **Extract Service:** Mover módulos a servicios

---

## Referencias

- [Principios Corporativos](../principios/)
- [Lineamientos de Arquitectura](../lineamientos/arquitectura/)
