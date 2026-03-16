---
title: "ADR-001: Estrategia Multi-Tenancy"
sidebar_position: 1
---

## ✅ ESTADO

Aceptada – Agosto 2025

---

## 🗺️ CONTEXTO

Los servicios corporativos deben soportar operaciones en múltiples países (Perú, Ecuador, Colombia, México) con:

- **Aislamiento de datos** por país/cliente para cumplimiento regulatorio
- **Configuraciones específicas** por mercado y regulaciones locales
- **Escalabilidad independiente** por región según demanda
- **Gestión centralizada** con visibilidad global para operaciones
- **Costos optimizados** compartiendo infraestructura común
- **Portabilidad** entre clouds manteniendo la separación

Las alternativas de multi-tenancy evaluadas fueron:

- **Single-Tenant (Por País):** cada país tiene su propia instancia completa del servicio y base de datos dedicada.
- **Multi-Tenant (Shared DB con Tenant ID):** una instancia de servicio y una base de datos compartida, con identificación de tenant en cada operación.
- **Database per Tenant (Modelo Intermedio):** instancia compartida del servicio, pero una base de datos dedicada por país.
- **Híbrido:** los países operan de manera compartida por defecto, pero casos específicos pueden aislarse como Single-Tenant según necesidad.

## 🔍 COMPARATIVA DE ALTERNATIVAS

| Criterio                     | Single-Tenant (Por País)                        | Multi-Tenant (Shared DB)                     | Database per Tenant                            | Híbrido                                      |
| ---------------------------- | ----------------------------------------------- | -------------------------------------------- | ---------------------------------------------- | -------------------------------------------- |
| **Aislamiento de datos**     | ✅ Total (instancia + BD dedicada por país)     | ⚠️ Lógico (Tenant ID por operación)          | ✅ Alto (BD separada por país)                 | ✅ Flexible (según necesidad)                |
| **Cumplimiento regulatorio** | ✅ Máximo (separación física)                   | ⚠️ Requiere políticas estrictas de acceso    | ✅ Alto (BD por país facilita regulación)      | ✅ Adaptable (aislado donde se requiere)     |
| **Escalabilidad**            | ❌ Limitada (N instancias × N países)           | ✅ Alta (un servicio, una BD)                | ✅ Buena (servicio compartido, BDs separadas)  | ✅ Buena (escala según patrón aplicado)      |
| **Seguridad**                | ✅ Máxima (aislamiento físico)                  | ⚠️ Requiere diseño cuidadoso                | ✅ Alta (datos físicamente separados)          | ✅ Adaptable (aislamiento donde se requiere) |
| **Portabilidad**             | ✅ Total (instancia independiente)              | ✅ Total (una instancia portable)            | ✅ Buena (servicio portable, BDs separables)   | ✅ Multi-cloud (stack OSS)                   |
| **Complejidad operativa**    | ❌ Alta (múltiples instancias y BDs)            | ✅ Baja (una instancia, una BD)              | ⚠️ Media (una instancia, múltiples BDs)       | ⚠️ Media (múltiples patrones coexisten)      |
| **Costos**                   | ❌ Muy altos (infraestructura duplicada)        | ✅ Mínimos (infraestructura compartida)      | ⚠️ Moderados (servicio compartido, N BDs)     | ⚠️ Moderados (balance compartido/aislado)    |
| **Flexibilidad**             | ⚠️ Rígida (todo aislado, sin excepciones)       | ❌ Limitada (mismo modelo para todos)        | ⚠️ Media (un patrón uniforme)                 | ✅ Alta (mejor patrón para cada caso)        |
| **Gestión centralizada**     | ❌ Difícil (visibilidad fragmentada)            | ✅ Simple (un punto de gestión)              | ⚠️ Media (servicio centralizado, datos dispersos) | ✅ Buena (visibilidad global con excepciones) |

**Leyenda:** ✅ Cumple completamente | ⚠️ Cumple parcialmente | ❌ No cumple

## ⚖️ DECISIÓN

**Seleccionamos el modelo Híbrido** con la siguiente estrategia:

### Estrategia Híbrida

- **Por defecto:** los países operan de forma compartida (Multi-Tenant con Tenant ID o Database per Tenant según el servicio), optimizando costos e infraestructura.
- **Excepción controlada:** si un país o caso de negocio lo requiere por regulación, seguridad o volumen, se aísla como Single-Tenant con instancia y base de datos dedicada.

### Alternativas descartadas

- **Single-Tenant (Por País):** costos e infraestructura se multiplican por cada país sin justificación general; solo se aplica como excepción cuando existe un requerimiento regulatorio o de negocio específico.
- **Multi-Tenant (Shared DB con Tenant ID):** aislamiento insuficiente para datos regulados; riesgo de data leakage si el filtro por Tenant ID falla; dificulta cumplimiento regulatorio por país.
- **Database per Tenant:** viable como modelo único, pero no ofrece la flexibilidad de aislar completamente un país cuando se requiere.

---

## 🔄 CONSECUENCIAS

### Positivas

- **Cumplimiento regulatorio** garantizado: se aísla como Single-Tenant solo donde la regulación lo exige
- **Optimización de costos** con operación compartida por defecto
- **Escalabilidad flexible** según el patrón aplicado a cada servicio o país
- **Flexibilidad operacional** para responder a requerimientos específicos sin rediseñar todo
- **Portabilidad mantenida** entre clouds y on-premises con stack OSS

### Negativas (Riesgos y Mitigaciones)

- **Coexistencia de patrones:** mitigado con documentación clara de criterios para decidir cuándo aislar
- **Complejidad en testing:** mitigado con estrategia de testing que cubra ambos modos (compartido y aislado)
- **Criterio de aislamiento:** mitigado con proceso formal (gobernanza) para aprobar excepciones Single-Tenant

---

## 📚 REFERENCIAS

- [Multi-Tenant Data Architecture](https://docs.microsoft.com/en-us/azure/sql-database/saas-tenancy-app-design-patterns)
- [PostgreSQL Row Level Security](https://www.postgresql.org/docs/current/ddl-rowsecurity.html)
- [Multi-Tenancy Patterns](https://martinfowler.com/articles/multi-tenant/)
- [GDPR and Multi-Tenancy](https://gdpr.eu/data-protection-impact-assessment-template/)

---

**Decisión tomada por:** Equipo de Arquitectura + Legal + Compliance
**Fecha:** Agosto 2025
**Próxima revisión:** Agosto 2026
