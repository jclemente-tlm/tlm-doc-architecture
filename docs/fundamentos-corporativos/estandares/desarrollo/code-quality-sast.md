# Code Quality y SAST (Static Analysis)

> **Estándar corporativo** para análisis estático de código y calidad.
> **Herramienta estándar**: SonarQube Community Edition
> **Integración**: GitHub Actions (CI/CD)

---

## 🎯 Objetivo

Garantizar calidad de código y detectar vulnerabilidades de seguridad (SAST) mediante análisis estático automatizado en el ciclo de desarrollo.

## 📋 Alcance

- Análisis de código fuente (.NET, JavaScript, TypeScript, futuro: Python, Java)
- Detección de vulnerabilidades (OWASP Top 10, CWE)
- Code smells y deuda técnica
- Complejidad ciclomática y duplicación
- Cobertura de pruebas unitarias
- Quality gates en CI/CD

---

## 🛠️ Herramienta Estándar: SonarQube Community

### Selección

**SonarQube Community Edition** (self-hosted) se establece como estándar por:

- **Costo**: OSS gratuito, solo infraestructura (~US$400/año vs US$13K Snyk)
- **Cobertura**: 29+ lenguajes (C#, JavaScript, TypeScript, Python, Java, Go)
- **Análisis profundo**: Vulnerabilidades (OWASP, CWE), code smells, duplicación
- **Quality Gates**: Configurables por proyecto
- **Histórico**: Base de datos con tendencias
- **Self-hosted**: Control total de datos sensibles

### Alternativas evaluadas

- **SonarQube Developer**: US$150/dev (branch analysis) - muy costoso
- **SonarCloud**: SaaS sin control de datos, US$10/100K LoC
- **CodeQL**: excelente para SAST pero sin code smells/cobertura
- **Snyk Code**: US$25/dev/mes, costoso para toda la organización
- **Semgrep**: enfocado en security, menos features de quality

### Limitaciones Community Edition

- ❌ **No branch analysis**: Solo escanea rama principal (main)
- ❌ **No PR decoration**: Sin comentarios inline en GitHub PRs
- ✅ **Workaround**: Escanear en PR con scripts custom y reportar en comentarios

---

## 📐 Implementación

### 1. Infraestructura SonarQube

```yaml
# docker-compose.yml
version: "3"

services:
  sonarqube:
    image: sonarqube:10-community
    ports:
      - "9000:9000"
    environment:
      - SONAR_JDBC_URL=jdbc:postgresql://db:5432/sonar
      - SONAR_JDBC_USERNAME=sonar
      - SONAR_JDBC_PASSWORD=${DB_PASSWORD}
    volumes:
      - sonarqube_data:/opt/sonarqube/data
      - sonarqube_logs:/opt/sonarqube/logs
      - sonarqube_extensions:/opt/sonarqube/extensions
    networks:
      - sonarnet

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_USER=sonar
      - POSTGRES_PASSWORD=${DB_PASSWORD}
      - POSTGRES_DB=sonar
    volumes:
      - postgresql_data:/var/lib/postgresql/data
    networks:
      - sonarnet

volumes:
  sonarqube_data:
  sonarqube_logs:
  sonarqube_extensions:
  postgresql_data:

networks:
  sonarnet:
```

### 2. Configuración GitHub Actions

```yaml
name: Code Quality Analysis

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  sonarqube:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          fetch-depth: 0 # Full history para análisis incremental

      - name: Setup .NET
        uses: actions/setup-dotnet@v4
        with:
          dotnet-version: "8.0.x"

      - name: Restore dependencies
        run: dotnet restore

      - name: Build
        run: dotnet build --no-restore

      - name: Run tests with coverage
        run: |
          dotnet test \
            --no-build \
            --collect:"XPlat Code Coverage" \
            --results-directory ./coverage

      - name: SonarQube Scan
        uses: sonarsource/sonarqube-scan-action@master
        env:
          SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
          SONAR_HOST_URL: ${{ secrets.SONAR_HOST_URL }}
        with:
          args: >
            -Dsonar.projectKey=my-project
            -Dsonar.cs.opencover.reportsPaths=coverage/**/coverage.opencover.xml
            -Dsonar.qualitygate.wait=true
```

### 3. Configuración de Proyecto

Archivo `sonar-project.properties`:

```properties
# Proyecto
sonar.projectKey=servicio-identidad
sonar.projectName=Servicio Identidad
sonar.projectVersion=1.0

# Fuentes
sonar.sources=src/
sonar.tests=tests/
sonar.exclusions=**/bin/**,**/obj/**,**/Migrations/**

# .NET específico
sonar.cs.opencover.reportsPaths=coverage/**/coverage.opencover.xml
sonar.cs.vstest.reportsPaths=**/*.trx

# Quality Gate
sonar.qualitygate.wait=true
sonar.qualitygate.timeout=300
```

---

## ⚙️ Quality Gates

### Configuración Estándar

```yaml
Quality Gate: "Talma Corporate"

Condiciones:
  - Cobertura de código nuevo: >= 80%
  - Duplicación en código nuevo: <= 3%
  - Deuda técnica en código nuevo: <= 5min
  - Vulnerabilidades críticas/altas: 0
  - Code smells críticos: 0
  - Complejidad cognitiva: <= 15 por función
```

### Configuración en SonarQube UI

```
Administration → Quality Gates → Create

On New Code:
✅ Coverage is less than 80%
✅ Duplicated Lines (%) is greater than 3%
✅ Maintainability Rating is worse than A
✅ Reliability Rating is worse than A
✅ Security Rating is worse than A
✅ Security Hotspots Reviewed is less than 100%
```

---

## 📊 Métricas y KPIs

### Indicadores Clave

| Métrica              | Objetivo        | Descripción                   |
| -------------------- | --------------- | ----------------------------- |
| **Coverage**         | >= 80%          | Cobertura de código con tests |
| **Duplicación**      | <= 3%           | Líneas duplicadas             |
| **Deuda técnica**    | <= 5%           | Ratio deuda/tamaño            |
| **Vulnerabilidades** | 0 Critical/High | Problemas de seguridad        |
| **Code smells**      | < 1/100 líneas  | Problemas de mantenibilidad   |
| **Complejidad**      | <= 10 promedio  | Complejidad ciclomática       |

### Dashboard Grafana

```promql
# Deuda técnica total
sum(sonarqube_technical_debt_minutes) / 60 / 8 # En días

# Cobertura promedio
avg(sonarqube_coverage_percent)

# Vulnerabilidades por severidad
sum(sonarqube_vulnerabilities) by (severity)

# Tendencia code smells
rate(sonarqube_code_smells_total[7d])
```

---

## 🔍 Reglas Importantes

### Seguridad (OWASP Top 10)

```
# Inyección SQL
java:S2077, javascript:S3649

# Secretos hardcodeados
java:S2068, javascript:S6290

# Weak cryptography
java:S4790, javascript:S4426

# XSS
javascript:S5131, csharpsquid:S5131

# CSRF
javascript:S4502, csharpsquid:S4502
```

### Code Smells Críticos

```
# Funciones demasiado largas
csharpsquid:S138 # > 100 líneas

# Complejidad excesiva
csharpsquid:S3776 # Cognitive complexity > 15

# Demasiados parámetros
csharpsquid:S107 # > 7 parámetros

# Clases demasiado grandes
csharpsquid:S1448 # > 1000 líneas
```

---

## 🎯 Prácticas Recomendadas

### 1. Análisis en Cada PR

```bash
# Análisis incremental (solo cambios)
dotnet sonarscanner begin \
  /k:"my-project" \
  /d:sonar.host.url="${SONAR_HOST_URL}" \
  /d:sonar.login="${SONAR_TOKEN}" \
  /d:sonar.scm.revision="${GITHUB_SHA}"

dotnet build
dotnet test --collect:"XPlat Code Coverage"

dotnet sonarscanner end /d:sonar.login="${SONAR_TOKEN}"
```

### 2. Exclusiones Apropiadas

```properties
# Archivos generados
sonar.exclusions=**/obj/**,**/bin/**,**/*.Designer.cs

# Migraciones de base de datos
sonar.exclusions=**/Migrations/**

# Código de terceros
sonar.exclusions=**/Libs/**,**/packages/**

# Tests
sonar.test.exclusions=**/*Tests/**
```

### 3. Suppressions Inline

```csharp
// Para falsos positivos documentados
[SuppressMessage("Security", "S2068",
    Justification = "Variable de entorno, no hardcoded secret")]
public string ConnectionString => Environment.GetEnvironmentVariable("DB_CONN");
```

---

## 🔧 Troubleshooting

### Problema: Análisis muy lento

```bash
# Solución: Análisis incremental
sonar.scm.disabled=false
sonar.scm.provider=git

# Exclusiones amplias
sonar.exclusions=**/node_modules/**,**/dist/**
```

### Problema: Cobertura no reportada

```bash
# Verificar formato coverage
dotnet test --collect:"XPlat Code Coverage" --results-directory coverage

# Verificar paths en sonar-project.properties
sonar.cs.opencover.reportsPaths=coverage/**/coverage.opencover.xml
```

### Problema: Quality Gate falla en PR

```yaml
# Configurar para analizar solo código nuevo
sonar.analysis.mode=issues
sonar.issuesReport.html.enable=true
```

---

## 📋 Checklist Pre-Merge

- [ ] Coverage >= 80% en código nuevo
- [ ] Cero vulnerabilidades críticas/altas
- [ ] Cero code smells bloqueantes
- [ ] Duplicación <= 3%
- [ ] Complejidad cognitiva <= 15 por función
- [ ] Quality Gate PASSED
- [ ] Security Hotspots revisados

---

## 🔗 Integración con Otros Estándares

- **Container Scanning**: [Trivy](container-scanning.md)
- **IaC Scanning**: [Checkov](iac-scanning.md)
- **CI/CD**: [GitHub Actions - ADR-009](../../decisiones-de-arquitectura/adr-009-github-actions-cicd.md)
- **Testing**: [Estándar de Testing](../testing/unit-testing.md)

---

## 📚 Referencias

- [SonarQube Documentation](https://docs.sonarqube.org/latest/)
- [SonarScanner for .NET](https://docs.sonarqube.org/latest/analysis/scan/sonarscanner-for-msbuild/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Clean Code Principles](https://www.amazon.com/Clean-Code-Handbook-Software-Craftsmanship/dp/0132350882)
- [SonarQube Rules](https://rules.sonarsource.com/)

---

**Tipo**: Estándar de desarrollo
**Categoría**: Code Quality / Security
**Última actualización**: Febrero 2026
**Revisión**: Anual
