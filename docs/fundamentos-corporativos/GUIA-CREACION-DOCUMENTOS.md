# Guía para Crear Nuevos Documentos de Fundamentos Corporativos

**Propósito:** Explicar cuándo crear un Lineamiento, un Estándar o una Convención.

---

## 🎯 ¿Qué tipo de documento crear?

### Regla de Oro

| Pregunta                              | Tipo de Documento |
| ------------------------------------- | ----------------- |
| ¿Por qué hacemos esto?                | **Principio**     |
| ¿Qué debemos lograr? (arquitectónico) | **Lineamiento**   |
| ¿Con qué tecnología/framework?        | **Estándar**      |
| ¿Cómo nombrar/formatear?              | **Convención**    |

---

## 📊 Matriz de Decisión

### Crear un PRINCIPIO cuando

✅ **Defines un valor fundamental de arquitectura**

**Características:**

- Filosófico y conceptual
- Independiente de tecnología
- Duradero (no cambia frecuentemente)
- Fundamento para decisiones

**Ejemplos:**

- "Seguridad desde el Diseño"
- "Observabilidad desde el Diseño"
- "Calidad desde el Diseño"

**NO crear si:** Ya existe un principio similar

---

### Crear un LINEAMIENTO cuando

✅ **Defines una directiva arquitectónica que implementa principios**

**Características:**

- Describe "CÓMO" a nivel conceptual
- Independiente de tecnología específica
- Guía decisiones arquitectónicas
- Evaluable en proyectos

**Ejemplos:**

- "Diseñar APIs REST coherentes"
- "Aplicar Seguridad desde el Diseño"
- "Implementar Testing en múltiples niveles"

**NO crear si:**

- Prescribes tecnología específica → Es un Estándar
- Defines naming/formato → Es una Convención

---

### Crear un ESTÁNDAR cuando

✅ **Prescribes una tecnología, framework o herramienta específica**

**Características:**

- Define "QUÉ" tecnología usar
- Define "CÓMO" configurar
- Incluye código ejecutable
- Versionado técnico

**Ejemplos:**

- "Usar xUnit 2.4+ para testing en C#"
- "Usar JWT con RS256 para autenticación"
- "Usar Terraform para IaC"
- "Usar ASP.NET Core 8.0+ para APIs"

**NO crear si:**

- Solo defines naming → Es una Convención
- Es directiva conceptual → Es un Lineamiento

---

### Crear una CONVENCIÓN cuando

✅ **Defines reglas de nomenclatura, formato o sintaxis**

**Características:**

- Define "CÓMO" escribir código/nombres
- Reglas verificables objetivamente
- Independiente de tecnología
- Puede usar linters/herramientas

**Ejemplos:**

- "Clases en PascalCase en C#"
- "Endpoints en kebab-case: /api/v1/user-profiles"
- "Variables de entorno en UPPER_SNAKE_CASE"
- "Commits en formato Conventional Commits"

**NO crear si:**

- Prescribes tecnología → Es un Estándar
- Es conceptual → Es un Lineamiento

---

## 📝 Tabla Comparativa

| Aspecto             | Principio  | Lineamiento    | Estándar       | Convención      |
| ------------------- | ---------- | -------------- | -------------- | --------------- |
| **Nivel**           | Filosófico | Arquitectónico | Técnico        | Sintáctico      |
| **Pregunta**        | ¿Por qué?  | ¿Qué lograr?   | ¿Con qué?      | ¿Cómo escribir? |
| **Tecnología**      | No         | No             | **Sí**         | No              |
| **Ejemplos código** | No         | Conceptual     | **Ejecutable** | Sintaxis        |
| **Cambia**          | Raramente  | Poco           | Con tech       | Poco            |
| **Verificable**     | Subjetivo  | Checklist      | Tests/CI       | Linter          |

---

## 🎨 Ejemplos por Tema

### Tema: APIs REST

| Documento                  | Tipo        | Contenido                        |
| -------------------------- | ----------- | -------------------------------- |
| "Contratos de Integración" | Principio   | Por qué tener contratos estables |
| "Diseño de APIs"           | Lineamiento | Cómo diseñar APIs coherentes     |
| "Diseño REST"              | Estándar    | ASP.NET Core 8+, configuración   |
| "Naming Endpoints"         | Convención  | `/api/v1/users` kebab-case       |

### Tema: Seguridad

| Documento                   | Tipo        | Contenido                     |
| --------------------------- | ----------- | ----------------------------- |
| "Seguridad desde el Diseño" | Principio   | Por qué security-first        |
| "Seguridad desde el Diseño" | Lineamiento | Aplicar OWASP Top 10          |
| "Secrets Management"        | Estándar    | AWS Secrets Manager, rotación |
| "Manejo Secretos"           | Convención  | Never commit, `.env` patterns |

### Tema: Testing

| Documento                 | Tipo        | Contenido                |
| ------------------------- | ----------- | ------------------------ |
| "Calidad desde el Diseño" | Principio   | Por qué calidad importa  |
| "Testing y Calidad"       | Lineamiento | Pirámide de testing      |
| "Testing Unitario"        | Estándar    | xUnit, Jest, AAA pattern |
| (No aplica)               | Convención  | -                        |

### Tema: Código

| Documento                 | Tipo        | Contenido                        |
| ------------------------- | ----------- | -------------------------------- |
| "Calidad desde el Diseño" | Principio   | Por qué Clean Code               |
| "Testing y Calidad"       | Lineamiento | Aplicar SOLID, DRY               |
| "C# y .NET"               | Estándar    | .NET 8, SOLID, async/await       |
| "Naming C#"               | Convención  | PascalCase, camelCase, \_private |

---

## 📋 Templates

### Template: Lineamiento

```text
---
id: {id}
sidebar_position: {n}
title: {Título}
description: {Descripción}
---

# {Título}

## 1. Propósito

Qué se busca lograr con este lineamiento (directiva arquitectónica).

## 2. Alcance

**Aplica a:**
- Tipo de proyecto 1
- Tipo de proyecto 2

**No aplica a:**
- Excepciones

## 3. Lineamientos Obligatorios

- Lineamiento 1
- Lineamiento 2

## 4. Decisiones de Diseño Esperadas

- Qué debe decidir el equipo

## 5. Antipatrones y Prácticas Prohibidas

- Qué NO hacer

## 6. Principios Relacionados

- Links a principios

## 7. Validación y Cumplimiento

- Cómo verificar cumplimiento
```

### Template: Estándar

````text
---
id: {id}
sidebar_position: {n}
title: {Título}
description: {Descripción}
---

# {Título}

## 1. Propósito

Qué problema técnico resuelve este estándar.

## 2. Alcance

**Aplica a:** ...
**No aplica a:** ...

## 3. Tecnologías y Herramientas Obligatorias

**Versión mínima:** ...
**Librerías:**
- lib1 (version)

**Instalación:**
```bash
comando install
````

## 4. Configuración Estándar

```code
// Configuración
```

## 5. Ejemplos Prácticos

### Ejemplo 1: \{Caso de Uso\}

```code
// Código ejecutable
```

## 6. Mejores Prácticas

✅ SÍ hacer: ...

## 7. NO Hacer (Antipatrones)

❌ NO hacer: ...
**Razón:** ...
**Alternativa:** ...

## 8. Validación y Cumplimiento

- [ ] Criterio verificable

## 9. Referencias

### Lineamientos Relacionados

- [Link]

### Principios Relacionados

- [Link]

### Convenciones Relacionadas

- [Link]

### Documentación Externa

- [Link oficial]

````

### Template: Convención

```text
---
id: {id}
sidebar_position: {n}
title: {Título}
description: {Descripción}
---

## 1. Principio

Por qué esta convención es importante.

## 2. Reglas

### Regla 1: \{Nombre\}

- **Formato:** `formato`
- **Ejemplo correcto:** `ejemplo`
- **Ejemplo incorrecto:** `ejemplo`
- **Justificación:** ...

```code
✅ Correcto:
ejemplo

❌ Incorrecto:
ejemplo
````

## 3. Tabla de Referencia Rápida

| Tipo | Formato | Ejemplo |
| ---- | ------- | ------- |
| X    | Y       | Z       |

## 4. Herramientas

- Linter/Tool
- Configuración

## 5. Checklist

- [ ] Criterio 1
- [ ] Criterio 2

## 6. Referencias

### Estándares Relacionados

- [Link]

### Lineamientos Relacionados

- [Link]

```

---

## ✅ Checklist Antes de Crear

Antes de crear un nuevo documento, pregúntate:

- [ ] ¿Ya existe un documento similar?
- [ ] ¿Estoy usando el tipo correcto? (Principio/Lineamiento/Estándar/Convención)
- [ ] ¿El contenido no está en otro documento?
- [ ] ¿Tengo suficiente información para llenarlo completamente?
- [ ] ¿Hay ejemplos reales que pueda incluir?
- [ ] ¿Puedo trazar este documento a niveles superiores?

---

## 🚨 Errores Comunes

### ❌ Error 1: Mezclar Estándar con Convención

**Incorrecto:**
```

Estándar C# → Incluye naming (PascalCase, camelCase)

```

**Correcto:**
```

Estándar C# → Solo Clean Code, SOLID, async/await
Convención C# → Solo naming (PascalCase, camelCase)

```

### ❌ Error 2: Lineamiento demasiado técnico

**Incorrecto:**
```

Lineamiento → "Usar xUnit con FluentAssertions"

```

**Correcto:**
```

Lineamiento → "Aplicar pirámide de testing"
Estándar → "Usar xUnit con FluentAssertions"

```

### ❌ Error 3: Convención con tecnología

**Incorrecto:**
```

Convención → "Usar AWS Secrets Manager para secretos"

```

**Correcto:**
```

Convención → "Never commit secrets, usar .env"
Estándar → "Usar AWS Secrets Manager con rotación"

```

---

## 📞 Contacto

**Dudas sobre qué crear:**
- Consultar con Arquitecto Principal
- Revisar documentos existentes
- Usar checklist de revisión

**Proceso de aprobación:**
1. Crear documento con template
2. PR con revisores asignados
3. Validación con script
4. Aprobación de 2+ revisores
5. Merge a `main`

---

_Esta guía asegura coherencia y evita duplicación en la documentación de fundamentos corporativos._
```
