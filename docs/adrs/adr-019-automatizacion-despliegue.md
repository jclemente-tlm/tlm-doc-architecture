---
id: adr-019-automatizacion-de-despliegue
title: "Automatización de Despliegue"
sidebar_position: 19
---

## ✅ ESTADO

Aceptada – Agosto 2025

---

## 🗺️ CONTEXTO

Los servicios corporativos multi-tenant requieren una estrategia de configuración que soporte:

- **Configuración por entorno** (dev, staging, prod) sin duplicación
- **Multi-tenancy** con configuraciones específicas por país/tenant
- **Versionado y auditabilidad** de todos los cambios de configuración
- **Automatización CI/CD** para despliegues sin intervención manual
- **Secretos segregados** de configuración pública (ver ADR-001)
- **Rollback rápido** ante configuraciones erróneas
- **Validación previa** a aplicación en producción
- **Agnosticidad** entre proveedores cloud y on-premises

La intención estratégica es **priorizar simplicidad y auditabilidad vs flexibilidad dinámica** para configuración empresarial.

Las alternativas evaluadas fueron:

- **Scripts versionados** (SQL, PowerShell, Bash, Infrastructure as Code)
- **API de configuración** (Custom REST API, GraphQL)
- **Configuration Management** (Ansible, Puppet, Chef)
- **Cloud Config Services** (AWS Parameter Store, Azure App Config)
- **Service Mesh Config** (Istio, Consul Connect)
- **GitOps** (ArgoCD, Flux con config repos)

## 🔍 COMPARATIVA DE ALTERNATIVAS

### Comparativa Cualitativa

| Criterio | Scripts | API Config | Config Mgmt | Cloud Config | Service Mesh | GitOps |
|----------|---------|------------|-------------|--------------|--------------|--------|
| **Agnosticidad** | ✅ Totalmente agnóstico | ✅ Agnóstico | ✅ Agnóstico | ❌ Lock-in cloud | 🟡 Depende mesh | ✅ Agnóstico |
| **Auditabilidad** | ✅ Git nativo | 🟡 API logs | ✅ Playbooks versionados | 🟡 Logs cloud | 🟡 Logs limitados | ✅ Git completo |
| **Operación** | ✅ Scripts simples | 🟡 API compleja | 🟡 Playbooks complejos | ✅ Gestionado | 🟡 Mesh complejo | 🟡 GitOps learning |
| **CI/CD** | ✅ Integración nativa | ✅ API calls | ✅ Ansible tasks | 🟡 SDK calls | 🟡 Mesh APIs | ✅ Git-driven |
| **Multi-tenancy** | ✅ Por parámetros | ✅ API endpoints | ✅ Inventarios | 🟡 Por namespaces | 🟡 Por namespaces | ✅ Por repos |
| **Costos** | ✅ Solo compute | 🟡 API hosting | 🟡 Infraestructura | 🟡 Por uso | 🟡 Mesh overhead | ✅ Solo Git |
| **Seguridad** | ✅ RBAC + secrets | 🟡 API auth | ✅ Vault integration | 🟡 Cloud IAM | ✅ mTLS | ✅ Git + RBAC |

### Matriz de Decisión

| Solución | Agnosticidad | Auditabilidad | CI/CD | Simplicidad | Recomendación |
|----------|--------------|---------------|-------|-------------|---------------|
| **Scripts Versionados** | Excelente | Excelente | Nativa | Simple | ✅ **Seleccionada** |
| **GitOps** | Excelente | Excelente | Git-driven | Moderada | 🟡 Alternativa |
| **Config Management** | Excelente | Buena | Buena | Compleja | 🟡 Considerada |
| **API Config** | Excelente | Moderada | Buena | Compleja | 🟡 Considerada |
| **Cloud Config** | Mala | Moderada | Moderada | Simple | ❌ Descartada |
| **Service Mesh** | Moderada | Limitada | Moderada | Compleja | ❌ Descartada |

## 💰 ANÁLISIS DE COSTOS (TCO 3 años)

### Escenario Base: 5 servicios, 4 países, configuración por entorno

| Solución | Implementación | Infraestructura | Operación | TCO 3 años |
|----------|----------------|-----------------|-----------|------------|
| **Scripts Versionados** | US$8,000 | US$0 | US$9,000/año | **US$35,000** |
| **GitOps** | US$15,000 | US$3,600/año | US$6,000/año | **US$43,800** |
| **Configuration Management** | US$25,000 | US$7,200/año | US$15,000/año | **US$91,600** |
| **API de Configuración** | US$40,000 | US$4,800/año | US$18,000/año | **US$108,400** |
| **Cloud Config Services** | US$5,000 | US$18,000/año | US$12,000/año | **US$95,000** |
| **Service Mesh Config** | US$30,000 | US$12,000/año | US$24,000/año | **US$138,000** |

### Escenario Alto Volumen: 20 servicios, multi-región, cambios frecuentes

| Solución | TCO 3 años | Complejidad Operacional |
|----------|------------|------------------------|
| **Scripts Versionados** | **US$90,000** | Baja - Ejecución directa |
| **GitOps** | **US$120,000** | Media - Sincronización automática |
| **Configuration Management** | **US$240,000** | Alta - Agentes y orquestación |
| **API de Configuración** | **US$300,000** | Alta - Desarrollo y mantenimiento |
| **Cloud Config Services** | **US$450,000** | Media - Dependencia proveedor |
| **Service Mesh Config** | **US$600,000** | Muy alta - Configuración compleja |

### Factores de Costo Adicionales

```yaml
Consideraciones Scripts Versionados:
  Versionado: Git nativo (incluido)
  Validación: Scripts de testing vs US$15K/año herramientas
  Rollback: Instantáneo vs US$5K/incidente manual
  Auditoría: Git logs vs US$20K/año herramientas comerciales
  Migración: US$0 entre plataformas vs US$30K propietario
  Capacitación: US$2K vs US$12K para herramientas complejas
  Automatización: CI/CD nativo vs US$25K/año herramientas
```

---

## ✔️ DECISIÓN

La configuración de los servicios se gestionará mediante scripts versionados en el repositorio, evitando la gestión manual o vía `API`.

## Justificación

- Facilita la trazabilidad y control de cambios.
- Permite reproducibilidad de entornos y rollback sencillo.
- Mayor control y trazabilidad de cambios.
- Reducción de superficie de ataque y riesgos de seguridad.
- Adecuado para escenarios con baja frecuencia de cambios.
- Si la frecuencia de cambios aumenta, se puede reconsiderar exponer una `API`.

## Alternativas descartadas

- Gestión manual vía consola o UI.
- Configuración vía `API`.

---

## ⚠️ CONSECUENCIAS

- Los cambios de configuración requieren acceso controlado y personal técnico.
- Se documentan los procedimientos y scripts utilizados.

---

## 📚 REFERENCIAS

- [Gestión de configuración por scripts](https://12factor.net/config)
- [Arc42: Decisiones de arquitectura](https://arc42.org/decision/)
