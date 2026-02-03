# Estándares de Calidad de Código

## Contexto

El código de baja calidad genera deuda técnica, bugs en producción y ralentiza entregas. Análisis estático automatizado y métricas de cobertura establecen línea base de calidad objetiva y detectable antes de merge.

## Decisión

Implementar control de calidad automatizado en CI/CD combinando análisis estático (linting, SAST) y métricas de cobertura con umbrales mínimos definidos.

## Estándares Obligatorios

### 1. Análisis Estático de Código

**Herramientas por lenguaje:**

- **.NET:** Roslyn Analyzers, SonarQube Community, StyleCop

**Quality Gates mínimos:**

```yaml
sonarqube:
  bugs: 0 (blocker/critical)
  vulnerabilities: 0 (blocker/critical)
  code_smells: rating_a_or_b
  security_hotspots: reviewed_100%
  duplications: <3%
  cognitive_complexity: <15_per_function
```

**Configuración CI/CD:**

```yaml
# Ejemplo GitHub Actions
- name: Run Static Analysis
  run: |
    dotnet tool install --global dotnet-sonarscanner
    sonarscanner begin /k:"project-key" /d:sonar.host.url="$SONAR_URL"
    dotnet build --no-incremental
    sonarscanner end

- name: Quality Gate Check
  run: |
    quality_status=$(curl "$SONAR_URL/api/qualitygates/project_status?projectKey=project-key")
    if [ "$quality_status" != "OK" ]; then exit 1; fi
```

### 2. Cobertura de Código

**Umbrales mínimos por tipo:**

- **Lógica de negocio crítica:** ≥80% cobertura de líneas
- **Servicios de aplicación:** ≥70% cobertura
- **Infraestructura/utilidades:** ≥60% cobertura
- **UI/presentación:** ≥50% cobertura (priorizar lógica)

**Métricas requeridas:**

- Line Coverage (cobertura de líneas)
- Branch Coverage (cobertura de ramas/condiciones)
- Mutation Score (calidad de tests) - opcional pero recomendado

**Herramientas:**

- **.NET:** Coverlet, dotCover, OpenCover

**Configuración de reporte:**

```xml
<!-- Ejemplo .NET -->
<PropertyGroup>
  <CollectCoverage>true</CollectCoverage>
  <CoverletOutputFormat>opencover,cobertura</CoverletOutputFormat>
  <Threshold>80</Threshold>
  <ThresholdType>line,branch</ThresholdType>
  <ThresholdStat>total</ThresholdStat>
</PropertyGroup>
```

### 3. Quality Gates en Pull Requests

**Requisitos bloqueantes:**

- ✅ Análisis estático aprobado (0 issues críticos)
- ✅ Cobertura ≥ umbral definido
- ✅ Build exitoso sin warnings críticos
- ✅ Code review aprobado (1+ aprobaciones)
- ✅ Tests automatizados pasando (100%)

**Branch protection:**

```yaml
# GitHub branch protection
required_status_checks:
  - sonarqube-analysis
  - code-coverage-check
  - build-and-test
required_reviews: 1
dismiss_stale_reviews: true
enforce_admins: false
```

### 4. Exclusiones Permitidas

**Archivos excluibles de cobertura:**

- Código generado automáticamente
- DTOs/POCOs sin lógica
- Program.cs/Startup.cs (configuración)
- Migraciones de base de datos
- Scripts de infraestructura

**Configuración de exclusiones:**

```xml
<!-- .coverletrc -->
<Exclude>
  [*]*.Migrations.*
  [*]*.Generated.*
  [*]*.Designer.cs
  [*]*Program.cs
</Exclude>
```

## Alineación con Industria

- **SonarQube Quality Model** - Bugs, Vulnerabilities, Code Smells, Security Hotspots
- **OWASP ASVS V14** - Static Application Security Testing (SAST)
- **Google Engineering Practices** - Code Review + Static Analysis
- **Martin Fowler - Continuous Integration** - Automated Quality Gates
- **ISO 25010 (SQuaRE)** - Software Quality Model

## Validación de Cumplimiento

**Automatizada:**

- Quality gate en SonarQube/SonarCloud
- Coverage report en PR comments
- Status checks bloqueantes en GitHub/GitLab/Azure DevOps

**Manual (code review):**

- Verificar que nuevos archivos no reducen cobertura global
- Validar que exclusiones están justificadas
- Revisar que warnings no críticos se están reduciendo

## Excepciones

**Casos válidos:**

- Legacy code sin tests (documentar plan de remediación)
- Prototipos de validación (marcar como temporal)
- Scripts de utilidades one-off

**Proceso:**
Documentar en ADR con:

- Justificación técnica
- Plan de remediación (si aplica)
- Fecha de revisión
- Aprobación de arquitectura

## Referencias

- [SonarQube Quality Model](https://docs.sonarqube.org/latest/user-guide/quality-gates/)
- [Google Code Review Guidelines](https://google.github.io/eng-practices/review/)
- [OWASP ASVS V14](https://owasp.org/www-project-application-security-verification-standard/)
- [Testing Pyramid](./testing-pyramid.md)
- [Code Review Policy](./code-review-policy.md)
