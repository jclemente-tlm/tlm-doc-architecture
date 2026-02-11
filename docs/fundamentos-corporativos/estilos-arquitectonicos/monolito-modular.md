---
id: monolito-modular
sidebar_position: 5
title: Monolito Modular
description: Estilo de sistema unificado con módulos cohesivos y bajo acoplamiento interno
---

# Monolito Modular

> **Tipo:** Estilo Arquitectónico Contextual
> **Aplicabilidad:** Sistemas con dominios acotados, equipos pequeños y necesidad de simplicidad operativa

## Declaración del Estilo

Un sistema puede estructurarse como una aplicación única (monolito) internamente organizada en módulos cohesivos con límites claros, facilitando evolución controlada y eventual transición a arquitecturas distribuidas.

## Principios que Materializa

Este estilo arquitectónico implementa los siguientes principios corporativos:

- ✅ [Arquitectura Limpia](../lineamientos/arquitectura/10-arquitectura-limpia.md)
- ✅ [Diseño Orientado al Dominio](../lineamientos/arquitectura/08-diseno-orientado-al-dominio.md)
- ✅ [Simplicidad Intencional](../lineamientos/arquitectura/12-simplicidad-intencional.md)
- ✅ [Modularidad y Bajo Acoplamiento](../principios/02-modularidad-y-bajo-acoplamiento.md) (a nivel de módulos)

## Propósito

Obtener los beneficios de separación de responsabilidades sin la complejidad operativa de sistemas distribuidos, manteniendo opciones abiertas para futura evolución.

## Cuándo Usar este Estilo

✅ **Aplicar cuando:**

- Dominios acotados y cohesivos
- Equipos pequeños (1-10 personas)
- Cambios poco frecuentes o predecibles
- Necesidad de simplicidad operativa
- MVP o sistemas en etapa inicial
- Baja necesidad de escalabilidad independiente
- Infraestructura DevOps básica

❌ **NO aplicar cuando:**

- Múltiples equipos autónomos (10+)
- Necesidad de escalabilidad independiente por capacidad
- Cambios frecuentes en diferentes áreas del sistema
- Requisitos de alta disponibilidad por componente

---

## Justificación

El monolito modular combina:

- **Simplicidad operativa** del monolito (un solo artefacto, un despliegue)
- **Claridad estructural** de arquitecturas modulares (límites, responsabilidades)

Evita complejidad innecesaria mientras mantiene opciones abiertas para evolución futura.

## Características del Estilo

- **Un único artefacto desplegable:** Simplifica despliegues y operación
- **Módulos internos con límites claros:** Separación de responsabilidades por dominio
- **Dependencias unidireccionales:** Módulos de alto nivel no dependen de bajo nivel
- **Interfaces bien definidas:** Comunicación entre módulos mediante contratos
- **Preparado para evolución:** Módulos pueden extraerse como servicios si es necesario
- **Base de datos compartida:** Con esquemas segregados por módulo

---

## Estructura Recomendada

```
src/
├── ModuloVentas/          # Dominio de ventas
│   ├── Domain/            # Lógica de negocio
│   ├── Application/       # Casos de uso
│   ├── Infrastructure/    # Implementaciones
│   └── Api/               # Endpoints públicos
├── ModuloInventario/      # Dominio de inventario
│   ├── Domain/
│   ├── Application/
│   ├── Infrastructure/
│   └── Api/
└── Shared/                # Componentes compartidos
    ├── Kernel/
    └── Infrastructure/
```

**Reglas de dependencia:**

- Módulos de dominio NO se comunican directamente
- Comunicación mediante eventos de dominio o interfaces públicas
- Shared Kernel mínimo y controlado

---

## Patrones Comunes

### 1. Separación por Capas (dentro de cada módulo)

```
Dominio (Core)
   ↑
Aplicación (Casos de Uso)
   ↑
Infraestructura (Detalles técnicos)
```

### 2. Eventos de Dominio Internos

Los módulos se comunican mediante eventos internos sin infraestructura de mensajería:

```csharp
// Módulo Ventas publica evento
DomainEvents.Raise(new VentaCompletada(ventaId));

// Módulo Inventario escucha evento
public class ReducirStockHandler : IHandles<VentaCompletada>
{
    // Actualizar inventario
}
```

### 3. Boundary Contexts (DDD)

Cada módulo representa un Bounded Context con:

- Modelo de dominio propio
- Lenguaje ubicuo específico
- Límites transaccionales claros

---

## Evolución hacia Microservicios

**Estrategia:** Strangler Fig Pattern

1. **Fase 1:** Monolito modular bien estructurado
2. **Fase 2:** Identificar módulos candidatos a extracción
3. **Fase 3:** Extraer módulo como servicio independiente
4. **Fase 4:** Mantener coexistencia temporal (monolito + servicios)
5. **Fase 5:** Reemplazar completamente llamadas al módulo original

**Criterios de extracción:**

- Módulo con cambios muy frecuentes
- Necesidad de escalabilidad independiente
- Equipo autónomo asignado
- Complejidad justifica distribución

---

## Compensaciones (Trade-offs)

### Ventajas

✅ **Simplicidad operativa:** Un solo despliegue, un solo proceso
✅ **Menor complejidad inicial:** No requiere infraestructura distribuida
✅ **Debugging más sencillo:** Stack traces completos
✅ **Transacciones ACID:** Consistencia fuerte más fácil
✅ **Refactoring más seguro:** Cambios internos sin afectar contratos

### Desventajas

❌ **Escalabilidad limitada:** Todo escala junto
❌ **Despliegue acoplado:** Un cambio requiere redesplegar todo
❌ **Riesgo de degradación:** Puede volverse monolito acoplado sin disciplina
❌ **Límite de equipos:** Difícil con equipos grandes (> 10 personas)

---

## Relación con ADRs

Este estilo se materializa en ADRs relacionados con:

- Estructuración interna del código
- Definición de módulos y límites
- Estrategias de comunicación entre módulos
- Políticas de versionado interno
- Plan de evolución arquitectónica

**ADRs relevantes:**

- ADR-XXX: Arquitectura Modular Interna
- ADR-XXX: Eventos de Dominio vs Eventos Distribuidos
- ADR-XXX: Estrategia de Migración a Microservicios

---

## Herramientas y Prácticas

- **ArchUnit / NetArchTest:** Validar reglas de dependencia entre módulos
- **Dependency Analysis:** Detectar acoplamiento no deseado
- **Feature Toggles:** Permitir releases independientes conceptualmente
- **Module Boundaries Testing:** Pruebas de contratos entre módulos

---

## Referencias

- [Arquitectura Limpia](../lineamientos/arquitectura/10-arquitectura-limpia.md)
- [Diseño Orientado al Dominio](../lineamientos/arquitectura/08-diseno-orientado-al-dominio.md)
- [Simplicidad Intencional](../lineamientos/arquitectura/12-simplicidad-intencional.md)
- [Arquitectura de Microservicios](microservicios.md) (para evolución futura)
- [Lineamiento: Descomposición y Límites](../lineamientos/arquitectura/02-descomposicion-y-limites.md)
