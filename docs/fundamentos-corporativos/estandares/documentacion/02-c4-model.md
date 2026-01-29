---
id: c4-model
sidebar_position: 2
title: C4 Model - Diagramas Arquitectónicos
description: Estándar para crear diagramas arquitectónicos consistentes usando el modelo C4 (Context, Container, Component, Code).
---

# Estándar Técnico — C4 Model - Diagramas Arquitectónicos

---

## 1. Propósito
Establecer C4 Model como estándar para diagramas arquitectónicos en 4 niveles (Context, Container, Component, Code) usando Structurizr DSL (preferido) o PlantUML, exportados a PNG/SVG y versionados en Git.

---

## 2. Alcance

**Aplica a:**
- Documentación arquitectónica (integración con arc42)
- Presentaciones a stakeholders técnicos/no-técnicos
- Onboarding de equipos
- Revisiones de diseño (design reviews)
- Microservicios y sistemas distribuidos

**No aplica a:**
- Diagramas de flujo de procesos de negocio (usar BPMN)
- Diagramas de datos (usar ERD)
- Diagramas de secuencia (usar UML Sequence)

---

## 3. Tecnologías Aprobadas

| Componente | Tecnología | Versión mínima | Observaciones |
|-----------|------------|----------------|---------------|
| **DSL (preferido)** | Structurizr DSL | 2.0+ | C4 as code |
| **Alternativa** | C4-PlantUML | Latest | `.puml` files |
| **CLI** | Structurizr CLI | 2.0+ | Exportar PNG/SVG |
| **Embebido** | Mermaid | 10.0+ | Diagramas simples |
| **Prohibido** | Draw.io / Lucidchart | - | Formatos propietarios |

> El uso de tecnologías no listadas requiere aprobación de Arquitectura.

---

## 4. Requisitos Obligatorios 🔴

- [ ] Structurizr DSL (preferido) o C4-PlantUML
- [ ] 4 niveles C4: Context (L1), Container (L2), Component (L3), Code (L4 opcional)
- [ ] Exportación a PNG/SVG para publicación
- [ ] Archivos `.dsl`/`.puml` versionados en Git
- [ ] Integración con arc42 (secciones 3, 5, 6, 7)
- [ ] Convenciones de naming: `{sistema}-{nivel}.dsl` (ej: `users-context.dsl`)
- [ ] Tags para colores consistentes (`Main System`, `External`, `Database`)
- [ ] Leyenda con significado de colores/formas
- [ ] Nivel 1 (Context) obligatorio para todos los sistemas
- [ ] Nivel 2 (Container) obligatorio para sistemas complejos
- [ ] Actualización con cambios arquitectónicos
- [ ] NO diagramas sin fuente editable (PNG sin .dsl)

---

## 5. Prohibiciones

- ❌ Diagramas en Draw.io/Lucidchart (formatos propietarios)
- ❌ PNG/JPG sin archivo fuente (.dsl/.puml)
- ❌ Diagramas sin leyenda de colores
- ❌ Mezclar niveles C4 en un solo diagrama
- ❌ >15 elementos por diagrama (refactorizar)
- ❌ Diagramas desactualizados (>3 meses)
- ❌ Flechas sin etiquetas de relación

---

## 6. Configuración Mínima

### Structurizr DSL (Preferido)
```bash
# Instalación
brew install structurizr-cli  # macOS

# Exportar diagramas
structurizr-cli export -workspace workspace.dsl -format plantuml
structurizr-cli export -workspace workspace.dsl -format png
```

```dsl
// diagrams/users-context.dsl
workspace "Sistema de Usuarios Talma" {
    model {
        # Personas
        employee = person "Empleado" {
            description "Empleado de Talma"
        }
        
        # Sistema principal
        userSystem = softwareSystem "Sistema de Usuarios" {
            description "Gestión centralizada de usuarios"
            tags "Main System"
        }
        
        # Sistemas externos
        activeDirectory = softwareSystem "Active Directory" {
            description "Directorio corporativo"
            tags "External"
        }
        
        # Relaciones
        employee -> userSystem "Gestiona usuarios" "HTTPS"
        userSystem -> activeDirectory "Autentica" "LDAP"
    }
    
    views {
        systemContext userSystem "Context" {
            include *
            autolayout
        }
        
        styles {
            element "Main System" {
                background #1168bd
                color #ffffff
            }
            element "External" {
                background #999999
                color #ffffff
            }
        }
    }
}
```

### C4-PlantUML (Alternativa)
```plantuml
@startuml users-context
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Context.puml

Person(employee, "Empleado", "Empleado de Talma")
System(userSystem, "Sistema de Usuarios", "Gestión centralizada")
System_Ext(ad, "Active Directory", "Directorio corporativo")

Rel(employee, userSystem, "Gestiona usuarios", "HTTPS")
Rel(userSystem, ad, "Autentica", "LDAP")

@enduml
```

### Integración con Markdown
```markdown
<!-- 03-contexto-alcance.md -->
# 3. Contexto y Alcance

## Diagrama de Contexto
![Contexto](../../diagrams/users-context.png)

**Fuente**: [diagrams/users-context.dsl](../../diagrams/users-context.dsl)

## Fronteras del Sistema
**Dentro del alcance:**
- Autenticación/autorización
- Gestión usuarios/roles

**Fuera del alcance:**
- Gestión empleados (SAP HR)
```

---

## 7. Validación

```bash
# Exportar PNG desde Structurizr DSL
structurizr-cli export -workspace diagrams/users.dsl -format png -output static/diagrams/

# Verificar archivos fuente
find diagrams/ -name "*.dsl" -o -name "*.puml"

# Validar que cada PNG tiene fuente
for png in static/diagrams/*.png; do
  base=$(basename "$png" .png)
  [ -f "diagrams/$base.dsl" ] || [ -f "diagrams/$base.puml" ] || echo "Missing source: $png"
done
```

**Métricas de cumplimiento:**

| Métrica | Target | Verificación |
|---------|--------|--------------|  
| Diagramas con fuente editable | 100% | `.dsl`/`.puml` files |
| Nivel 1 (Context) | 100% | Todos los sistemas |
| Actualización | <3 meses | Git log commits |
| Tags para colores | 100% | `tags "Main System"` |

Incumplimientos deben corregirse o documentarse mediante excepción aprobada.

---

## 8. Referencias

- [arc42](01-arc42.md)
- [OpenAPI/Swagger](03-openapi-swagger.md)
- [C4 Model](https://c4model.com/)
- [Structurizr DSL](https://structurizr.com/dsl)
- [C4-PlantUML](https://github.com/plantuml-stdlib/C4-PlantUML)        # Relaciones
