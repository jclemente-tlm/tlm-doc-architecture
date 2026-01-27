# Checklist de Revisión: Estándares y Convenciones

## Para Estándares Técnicos

### ✅ Estructura Obligatoria

- [ ] **Frontmatter YAML** completo
  - [ ] `id`: identificador único
  - [ ] `sidebar_position`: número de orden
  - [ ] `title`: título descriptivo
  - [ ] `description`: breve descripción (1 línea)

- [ ] **Sección 1: Propósito**
  - [ ] Explica QUÉ problema resuelve
  - [ ] Menciona para QUÉ sirve este estándar
  - [ ] Referencia a convenciones si aplica

- [ ] **Sección 2: Alcance**
  - [ ] Lista clara de "Aplica a:"
  - [ ] Lista clara de "No aplica a:"
  - [ ] Casos de uso específicos

- [ ] **Sección 3: Tecnologías y Herramientas Obligatorias**
  - [ ] Versiones mínimas especificadas
  - [ ] Librerías requeridas con versiones
  - [ ] Comandos de instalación

- [ ] **Sección 4: Configuración Estándar**
  - [ ] Ejemplos de configuración completos
  - [ ] Código ejecutable
  - [ ] Explicaciones de parámetros clave

- [ ] **Sección 5: Ejemplos Prácticos**
  - [ ] Al menos 2 ejemplos completos
  - [ ] Código ejecutable y testeable
  - [ ] Explicaciones claras del contexto

- [ ] **Sección 6: Mejores Prácticas**
  - [ ] Lista de prácticas recomendadas
  - [ ] Justificación de cada práctica

- [ ] **Sección 7: NO Hacer (Antipatrones)**
  - [ ] Al menos 3 antipatrones
  - [ ] Razón clara de por qué está mal
  - [ ] Alternativa correcta para cada uno

- [ ] **Sección 8: Validación y Cumplimiento**
  - [ ] Criterios verificables (checkboxes)
  - [ ] Herramientas de validación

- [ ] **Sección 9: Referencias**
  - [ ] Referencias a Lineamientos relacionados
  - [ ] Referencias a Principios relacionados
  - [ ] Referencias a Convenciones relacionadas
  - [ ] Referencias a otros Estándares
  - [ ] Documentación externa oficial

### ✅ Contenido de Calidad

- [ ] **No incluye naming** (eso va en Convenciones)
- [ ] **Especifica tecnología concreta** (no genérico)
- [ ] **Ejemplos son ejecutables** (se pueden copiar/pegar)
- [ ] **Tiene justificaciones claras** (el "por qué")
- [ ] **Todos los links funcionan** (sin 404)
- [ ] **Usa formato consistente** (emojis, tablas, código)
- [ ] **No repite contenido** de otros documentos

### ✅ Separación de Responsabilidades

- [ ] **QUÉ tecnología usar** → Estándar ✅
- [ ] **CÓMO configurar** → Estándar ✅
- [ ] **CÓMO nombrar** → Convención ❌ (no en Estándar)

---

## Para Convenciones

### ✅ Estructura Obligatoria

- [ ] **Frontmatter YAML** completo
  - [ ] `id`: identificador único
  - [ ] `sidebar_position`: número de orden
  - [ ] `title`: título descriptivo
  - [ ] `description`: breve descripción

- [ ] **Sección 1: Principio**
  - [ ] Explicación del fundamento
  - [ ] Por qué es importante

- [ ] **Sección 2: Reglas**
  - [ ] Reglas numeradas y claras
  - [ ] Ejemplos ✅ correcto
  - [ ] Ejemplos ❌ incorrecto
  - [ ] Justificación de cada regla

- [ ] **Sección 3: Tabla de Referencia Rápida**
  - [ ] Formato tabla o lista
  - [ ] Casos comunes cubiertos

- [ ] **Sección 4: Herramientas**
  - [ ] Linters o validadores
  - [ ] Configuración de herramientas

- [ ] **Sección 5: Checklist**
  - [ ] Lista verificable
  - [ ] Criterios claros

- [ ] **Sección 6: Referencias**
  - [ ] Referencias a Estándares relacionados
  - [ ] Referencias a Lineamientos relacionados
  - [ ] Referencias a Principios relacionados
  - [ ] Otras Convenciones relacionadas

### ✅ Contenido de Calidad

- [ ] **Solo naming y formato** (no tecnología)
- [ ] **Ejemplos claros** con ✅ y ❌
- [ ] **Tabla de referencia rápida** útil
- [ ] **No incluye tecnología** (eso va en Estándares)
- [ ] **Todos los links funcionan**
- [ ] **Reglas son verificables** (objetivas)

### ✅ Separación de Responsabilidades

- [ ] **CÓMO escribir/nombrar** → Convención ✅
- [ ] **Reglas sintácticas** → Convención ✅
- [ ] **QUÉ tecnología** → Estándar ❌ (no en Convención)

---

## Checklist General (Ambos)

### Formato

- [ ] Markdown válido
- [ ] Bloques de código con lenguaje especificado
- [ ] Tablas bien formadas
- [ ] Links en formato correcto
- [ ] Emojis consistentes (si se usan)

### Calidad de Escritura

- [ ] Sin errores ortográficos
- [ ] Lenguaje claro y directo
- [ ] Sin ambigüedades
- [ ] Terminología consistente
- [ ] Tono profesional pero accesible

### SEO y Navegación

- [ ] Título descriptivo
- [ ] Description útil
- [ ] Headers jerárquicos (H1 → H2 → H3)
- [ ] Links internos funcionan
- [ ] Links externos son oficiales

---

## Validación Automatizada

Antes de hacer commit, ejecutar:

```bash
# Validar estructura
./scripts/validate-standards.sh

# Validar links
npm run check-links

# Validar markdown
npx markdownlint docs/fundamentos-corporativos/**/*.md
```

---

## Criterios de Aceptación

### Para Merge a `main`

- [ ] Todas las secciones obligatorias presentes
- [ ] Al menos 2 revisores aprobaron
- [ ] Script de validación pasa sin errores
- [ ] Sin warnings críticos de linter
- [ ] Documentación builds sin errores
- [ ] Links validados (sin 404)

### Para Publicación

- [ ] Revisión técnica completada
- [ ] Revisión de arquitectura completada
- [ ] Ejemplos de código probados
- [ ] Referencias actualizadas
- [ ] Changelog actualizado

---

## Contacto y Soporte

**Dudas sobre estructura:**
- Ver: [GUIA-CREACION-DOCUMENTOS.md](GUIA-CREACION-DOCUMENTOS.md)

**Reportar problemas:**
- Issues en GitHub
- Canal #arquitectura en Slack

**Responsable:**
- Equipo de Arquitectura de Software
