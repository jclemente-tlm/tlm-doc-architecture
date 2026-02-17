# Correcciones de Referencias - Duplicados y Errores

## 🔧 Referencias a Actualizar

### 1. desarrollo/03-documentacion-tecnica.md

**Línea 19:**

```markdown
❌ ACTUAL:

- [Documentar decisiones arquitectónicas significativas mediante ADRs](../../estandares/arquitectura/architectural-decision-records.md)

✅ CORREGIR A:

- [Documentar decisiones arquitectónicas significativas mediante ADRs](../../estandares/documentacion/architecture-decision-records.md)
```

**Línea 20:**

```markdown
❌ ACTUAL:

- [Documentar arquitectura de servicios con plantilla arc42](../../estandares/arquitectura/arc42.md)

✅ CORREGIR A:

- [Documentar arquitectura de servicios con plantilla arc42](../../estandares/documentacion/arc42.md)
```

**Línea 21:**

```markdown
❌ ACTUAL:

- [Modelar arquitectura con notación C4 y Structurizr DSL](../../estandares/arquitectura/c4-model.md)

✅ CORREGIR A:

- [Modelar arquitectura con notación C4 y Structurizr DSL](../../estandares/documentacion/c4-model.md)
```

---

### 2. seguridad/08-gestion-vulnerabilidades.md

**Línea 19:**

```markdown
❌ ACTUAL:

- [Validar imágenes de contenedores antes de deployment](../../estandares/seguridad/container-image-scanning.md)

✅ CORREGIR A:

- [Validar imágenes de contenedores antes de deployment](../../estandares/seguridad/container-scanning.md)
```

---

### 3. seguridad/07-proteccion-de-datos.md

**Decisión necesaria:** El archivo `data-protection.md` existe en `datos/` pero se referencia desde `seguridad/`

**Opción A - Mover el archivo:**

```bash
git mv docs/fundamentos-corporativos/estandares/datos/data-protection.md \
        docs/fundamentos-corporativos/estandares/seguridad/data-protection.md
```

**Opción B - Actualizar las 6 referencias:**

```markdown
❌ ACTUAL (6 referencias en seguridad/07-proteccion-de-datos.md):
../../estandares/seguridad/data-protection.md

✅ CORREGIR A:
../../estandares/datos/data-protection.md
```

**Recomendación:** Opción A (mover a seguridad/) porque:

1. El contenido es sobre seguridad de datos
2. Se referencia desde documentos de seguridad
3. Mantiene coherencia con la categoría

---

## 🔍 Verificación de Archivos Existentes

### ✅ Archivos que SÍ existen (ubicación correcta)

- `documentacion/architecture-decision-records.md` ✓
- `documentacion/arc42.md` ✓
- `documentacion/c4-model.md` ✓
- `datos/data-protection.md` ✓ (pero debería estar en seguridad/)
- `seguridad/container-scanning.md` ✓

### ❌ Archivos que NO existen (necesitan crearse)

- `arquitectura/architectural-decision-records.md` ✗ (mal referenciado)
- `arquitectura/arc42.md` ✗ (mal referenciado)
- `arquitectura/c4-model.md` ✗ (mal referenciado)
- `seguridad/data-protection.md` ✗ (debería existir aquí)
- `seguridad/container-image-scanning.md` ✗ (mal referenciado)

---

## 📝 Plan de Acción

### Paso 1: Mover data-protection.md a seguridad/

```bash
git mv docs/fundamentos-corporativos/estandares/datos/data-protection.md \
        docs/fundamentos-corporativos/estandares/seguridad/data-protection.md
```

### Paso 2: Actualizar referencias en lineamientos

**Archivo 1:** [desarrollo/03-documentacion-tecnica.md](docs/fundamentos-corporativos/lineamientos/desarrollo/03-documentacion-tecnica.md)

- Línea 19: arquitectura/architectural-decision-records.md → documentacion/architecture-decision-records.md
- Línea 20: arquitectura/arc42.md → documentacion/arc42.md
- Línea 21: arquitectura/c4-model.md → documentacion/c4-model.md

**Archivo 2:** [seguridad/08-gestion-vulnerabilidades.md](docs/fundamentos-corporativos/lineamientos/seguridad/08-gestion-vulnerabilidades.md)

- Línea 19: container-image-scanning.md → container-scanning.md

### Paso 3: Validar correcciones

```bash
./scripts/validar-referencias-estandares.sh
```

---

## 📊 Impacto de las Correcciones

| Tipo                   | Cantidad |
| ---------------------- | -------- |
| Referencias a corregir | 4        |
| Archivos a mover       | 1        |
| Lineamientos afectados | 2        |

**Reducción de enlaces rotos:** -5 (de ~45 a ~40)

---

## 🚀 Ejecución Automática (Script)

```bash
#!/bin/bash
# Aplicar correcciones de referencias

cd docs/fundamentos-corporativos

# 1. Mover data-protection a seguridad
git mv estandares/datos/data-protection.md estandares/seguridad/data-protection.md

# 2. Actualizar desarrollo/03-documentacion-tecnica.md
sed -i 's|arquitectura/architectural-decision-records.md|documentacion/architecture-decision-records.md|g' \
    lineamientos/desarrollo/03-documentacion-tecnica.md

sed -i 's|arquitectura/arc42.md|documentacion/arc42.md|g' \
    lineamientos/desarrollo/03-documentacion-tecnica.md

sed -i 's|arquitectura/c4-model.md|documentacion/c4-model.md|g' \
    lineamientos/desarrollo/03-documentacion-tecnica.md

# 3. Actualizar seguridad/08-gestion-vulnerabilidades.md
sed -i 's|container-image-scanning.md|container-scanning.md|g' \
    lineamientos/seguridad/08-gestion-vulnerabilidades.md

echo "✅ Correcciones aplicadas"
```

**Nota:** Revisar manualmente antes de hacer commit

---

## ✅ Checklist de Validación

Después de aplicar correcciones:

- [ ] Mover `data-protection.md` a seguridad/
- [ ] Actualizar 3 referencias en desarrollo/03-documentacion-tecnica.md
- [ ] Actualizar 1 referencia en seguridad/08-gestion-vulnerabilidades.md
- [ ] Ejecutar script de validación
- [ ] Verificar que los enlaces funcionan en Docusaurus
- [ ] Hacer commit de los cambios
- [ ] Actualizar reporte de análisis

---

> **Próximo paso:** Aplicar estas correcciones antes de crear los estándares faltantes
