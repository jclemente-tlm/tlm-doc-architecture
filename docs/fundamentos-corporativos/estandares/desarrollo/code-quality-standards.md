---
id: code-quality-standards
sidebar_position: 3
title: Estándares de Calidad de Código
description: Estándar para implementar control de calidad automatizado con SonarQube, cobertura de código y quality gates en CI/CD
---

# Estándar Técnico — Calidad de Código

---

## 1. Propósito

Establecer línea base de calidad de código objetiva y automatizada mediante análisis estático (SonarQube, Roslyn Analyzers), métricas de cobertura (Coverlet) y quality gates bloqueantes en CI/CD antes de merge.

---

## 2. Alcance

**Aplica a:**

- Todo código .NET 8+ (backend, APIs, servicios)
- Pull requests a branches protegidas (main, develop)
- Pipelines de CI/CD en GitHub Actions
- Código de aplicación (no infraestructura)

**No aplica a:**

- Scripts de infraestructura (Terraform, bash)
- Código generado automáticamente
- Prototipos descartables (< 1 semana de vida)
- Migraciones de base de datos (EF Core Migrations)

---

## 3. Tecnologías Aprobadas

| Componente           | Tecnología           | Versión mínima | Observaciones                 |
| -------------------- | -------------------- | -------------- | ----------------------------- |
| **Static Analysis**  | SonarQube Community  | 10.0+          | SAST + code smells            |
| **Linting**          | Roslyn Analyzers     | Built-in       | .NET analyzers                |
| **Code Coverage**    | Coverlet             | 6.0+           | Cross-platform .NET           |
| **Mutation Testing** | Stryker.NET          | 4.0+           | Opcional pero recomendado     |
| **Security Scan**    | OWASP Dependency-Chk | 9.0+           | Vulnerabilidades de librerías |
| **CI/CD**            | GitHub Actions       | -              | Automatización de gates       |
| **IDE Integration**  | SonarLint            | Latest         | Feedback en tiempo real       |

> El uso de tecnologías no listadas requiere aprobación de Arquitectura.

---

## 4. Requisitos Obligatorios 🔴

### Quality Gates Bloqueantes

- [ ] **Bugs críticos**: 0 blocker/critical bugs
- [ ] **Vulnerabilidades**: 0 blocker/critical vulnerabilities
- [ ] **Code Smells**: Rating A o B (< 50 code smells)
- [ ] **Security Hotspots**: 100% reviewed
- [ ] **Duplicación**: < 3% código duplicado
- [ ] **Complejidad cognitiva**: < 15 por función
- [ ] **Cobertura de código**: ≥ umbral definido

### Cobertura por Tipo de Código

- [ ] **Lógica de negocio crítica**: ≥ 80% cobertura
- [ ] **Servicios de aplicación**: ≥ 70% cobertura
- [ ] **Infraestructura/utilidades**: ≥ 60% cobertura
- [ ] **Controllers/UI**: ≥ 50% cobertura

### Métricas de Cobertura

- [ ] **Line Coverage**: Líneas ejecutadas
- [ ] **Branch Coverage**: Ramas condicionales
- [ ] **Mutation Score**: Opcional (≥ 70%)

### Branch Protection

- [ ] **Análisis estático**: Status check obligatorio
- [ ] **Code coverage**: Status check obligatorio
- [ ] **Build + tests**: Status check obligatorio
- [ ] **Code review**: Mínimo 1 aprobación
- [ ] **Merge strategies**: Squash or rebase (no merge commits)

### Exclusiones Permitidas

- [ ] Código generado automáticamente
- [ ] DTOs/POCOs sin lógica
- [ ] Program.cs/Startup.cs (configuración)
- [ ] Migraciones de base de datos
- [ ] Archivos \*.Designer.cs

---

## 5. Prohibiciones

- ❌ Merge sin pasar quality gates
- ❌ Deshabilitar analyzers para "hacer pasar" el build
- ❌ Secretos o credentials en código
- ❌ `#pragma warning disable` sin justificación en comentario
- ❌ Reducir umbrales de cobertura sin ADR aprobado
- ❌ Code smells con severidad "Critical" sin resolver

---

## 6. Configuración SonarQube

### sonar-project.properties

```properties
# Proyecto
sonar.projectKey=talma-payment-api
sonar.projectName=Payment API
sonar.projectVersion=1.0.0

# Código fuente
sonar.sources=src
sonar.tests=tests
sonar.sourceEncoding=UTF-8

# Exclusiones
sonar.coverage.exclusions=**/Migrations/**,**/Program.cs,**/*.Designer.cs
sonar.exclusions=**/obj/**,**/bin/**,**/*.Generated.cs

# .NET específico
sonar.cs.opencover.reportsPaths=**/coverage.opencover.xml
sonar.cs.vstest.reportsPaths=**/*.trx

# Quality Gate
sonar.qualitygate.wait=true
sonar.qualitygate.timeout=300
```

### Directory.Build.props (Roslyn Analyzers)

```xml
<Project>
  <PropertyGroup>
    <AnalysisLevel>latest</AnalysisLevel>
    <EnforceCodeStyleInBuild>true</EnforceCodeStyleInBuild>
    <TreatWarningsAsErrors>true</TreatWarningsAsErrors>
  </PropertyGroup>

  <ItemGroup>
    <PackageReference Include="SonarAnalyzer.CSharp" Version="9.12.0">
      <PrivateAssets>all</PrivateAssets>
      <IncludeAssets>runtime; build; native; contentfiles; analyzers</IncludeAssets>
    </PackageReference>
    <PackageReference Include="Microsoft.CodeAnalysis.NetAnalyzers" Version="8.0.0">
      <PrivateAssets>all</PrivateAssets>
      <IncludeAssets>runtime; build; native; contentfiles; analyzers</IncludeAssets>
    </PackageReference>
  </ItemGroup>

  <!-- Warnings as Errors -->
  <PropertyGroup>
    <WarningsAsErrors>
      S1200,   <!-- Classes should not be coupled to too many other classes -->
      S3776,   <!-- Cognitive Complexity of methods should not be too high -->
      CA1062,  <!-- Validate arguments of public methods -->
      CA2007   <!-- Do not directly await a Task -->
    </WarningsAsErrors>
  </PropertyGroup>
</Project>
```

### Coverlet Configuration

```xml
<!-- PaymentApi.csproj -->
<Project Sdk="Microsoft.NET.Sdk.Web">
  <PropertyGroup>
    <TargetFramework>net8.0</TargetFramework>
  </PropertyGroup>

  <!-- Coverlet -->
  <ItemGroup>
    <PackageReference Include="coverlet.collector" Version="6.0.0">
      <IncludeAssets>runtime; build; native; contentfiles; analyzers</IncludeAssets>
      <PrivateAssets>all</PrivateAssets>
    </PackageReference>
  </ItemGroup>

  <PropertyGroup>
    <CollectCoverage>true</CollectCoverage>
    <CoverletOutputFormat>opencover,cobertura,json</CoverletOutputFormat>
    <CoverletOutput>./coverage/</CoverletOutput>

    <!-- Umbrales -->
    <Threshold>80</Threshold>
    <ThresholdType>line,branch</ThresholdType>
    <ThresholdStat>total</ThresholdStat>

    <!-- Exclusiones -->
    <ExcludeByFile>**/Migrations/**/*.cs,**/Program.cs</ExcludeByFile>
    <ExcludeByAttribute>GeneratedCodeAttribute,ExcludeFromCodeCoverageAttribute</ExcludeByAttribute>
  </PropertyGroup>
</Project>
```

---

## 7. GitHub Actions - Pipeline

### .github/workflows/quality-gates.yml

```yaml
name: Quality Gates

on:
  pull_request:
    branches: [main, develop]
  push:
    branches: [main]

jobs:
  quality-check:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0 # Shallow clones should be disabled for SonarQube

      - name: Setup .NET
        uses: actions/setup-dotnet@v4
        with:
          dotnet-version: "8.0.x"

      # SonarQube Scan
      - name: Install SonarScanner
        run: dotnet tool install --global dotnet-sonarscanner

      - name: Begin SonarQube Analysis
        run: |
          dotnet sonarscanner begin \
            /k:"talma-payment-api" \
            /d:sonar.host.url="${{ secrets.SONAR_HOST_URL }}" \
            /d:sonar.token="${{ secrets.SONAR_TOKEN }}" \
            /d:sonar.cs.opencover.reportsPaths="**/coverage.opencover.xml"

      # Build + Tests + Coverage
      - name: Build and Test
        run: |
          dotnet build --configuration Release --no-incremental
          dotnet test \
            --configuration Release \
            --no-build \
            --collect:"XPlat Code Coverage" \
            --results-directory ./coverage \
            -- DataCollectionRunSettings.DataCollectors.DataCollector.Configuration.Format=opencover

      - name: End SonarQube Analysis
        run: dotnet sonarscanner end /d:sonar.token="${{ secrets.SONAR_TOKEN }}"

      # Coverage Report
      - name: Code Coverage Report
        uses: irongut/CodeCoverageSummary@v1.3.0
        with:
          filename: coverage/**/coverage.opencover.xml
          badge: true
          fail_below_min: true
          format: markdown
          hide_branch_rate: false
          hide_complexity: false
          indicators: true
          output: both
          thresholds: "70 80"

      - name: Add Coverage PR Comment
        uses: marocchino/sticky-pull-request-comment@v2
        if: github.event_name == 'pull_request'
        with:
          recreate: true
          path: code-coverage-results.md

      # Quality Gate Status Check
      - name: SonarQube Quality Gate Check
        uses: sonarsource/sonarqube-quality-gate-action@master
        timeout-minutes: 5
        env:
          SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
          SONAR_HOST_URL: ${{ secrets.SONAR_HOST_URL }}
```

---

## 8. Validación de Cumplimiento

```bash
#!/bin/bash
# scripts/validate-code-quality.sh

echo "🔍 Validando estándares de calidad de código..."

# 1. Verificar SonarQube configurado
echo "1. SonarQube configuración..."
test -f sonar-project.properties && echo "✅ sonar-project.properties exists" || echo "❌ Missing sonar-project.properties"

# 2. Verificar Roslyn Analyzers
echo "2. Roslyn Analyzers..."
grep -r "SonarAnalyzer.CSharp" **/*.csproj && echo "✅ SonarAnalyzer configured" || echo "❌ Missing SonarAnalyzer"

# 3. Ejecutar análisis local
echo "3. Ejecutando análisis estático..."
dotnet build /p:TreatWarningsAsErrors=true

# 4. Ejecutar tests con cobertura
echo "4. Ejecutando tests con cobertura..."
dotnet test \
  --collect:"XPlat Code Coverage" \
  --results-directory ./coverage \
  -- DataCollectionRunSettings.DataCollectors.DataCollector.Configuration.Format=opencover

# 5. Verificar umbrales de cobertura
echo "5. Verificando umbrales de cobertura..."
COVERAGE=$(grep -oP 'line-rate="\K[^"]+' coverage/**/coverage.cobertura.xml | head -1)
COVERAGE_PERCENT=$(echo "$COVERAGE * 100" | bc)
echo "Cobertura actual: ${COVERAGE_PERCENT}%"

if (( $(echo "$COVERAGE_PERCENT < 70" | bc -l) )); then
  echo "❌ Cobertura por debajo del umbral (70%)"
  exit 1
else
  echo "✅ Cobertura cumple umbral"
fi

# 6. Verificar complejidad ciclomática
echo "6. Verificando complejidad..."
dotnet tool install --global dotnet-complexity
dotnet complexity **/*.cs --threshold 15

# 7. Verificar duplicación de código
echo "7. Verificando duplicación..."
# Requiere jscpd instalado: npm install -g jscpd
jscpd src --threshold 3 --reporters json

# 8. SonarQube Quality Gate (si está disponible)
if [ -n "$SONAR_HOST_URL" ]; then
  echo "8. Verificando SonarQube Quality Gate..."
  PROJECT_STATUS=$(curl -s -u "$SONAR_TOKEN:" \
    "$SONAR_HOST_URL/api/qualitygates/project_status?projectKey=talma-payment-api" \
    | jq -r '.projectStatus.status')

  if [ "$PROJECT_STATUS" = "OK" ]; then
    echo "✅ SonarQube Quality Gate: PASSED"
  else
    echo "❌ SonarQube Quality Gate: FAILED"
    exit 1
  fi
fi

echo "✅ Validación de calidad completada"
```

### Métricas de Cumplimiento

| Métrica                    | Target | Verificación                 |
| -------------------------- | ------ | ---------------------------- |
| Bugs críticos              | 0      | SonarQube dashboard          |
| Vulnerabilidades críticas  | 0      | SonarQube security tab       |
| Code Smells rating         | A o B  | SonarQube maintainability    |
| Cobertura de código        | ≥ 70%  | Coverage report en PR        |
| Complejidad cognitiva      | < 15   | SonarQube complexity metrics |
| Duplicación                | < 3%   | SonarQube duplications       |
| Security Hotspots reviewed | 100%   | SonarQube security review    |
| Build warnings             | 0      | GitHub Actions build log     |

---

## 9. Referencias

**SonarQube:**

- [SonarQube Quality Model](https://docs.sonarqube.org/latest/user-guide/quality-gates/)
- [SonarQube for .NET](https://docs.sonarqube.org/latest/analyzing-source-code/languages/csharp/)

**Code Quality:**

- [Google Code Review Guidelines](https://google.github.io/eng-practices/review/)
- [Clean Code, Robert C. Martin](https://www.oreilly.com/library/view/clean-code-a/9780136083238/)

**Security:**

- [OWASP ASVS V14 - SAST](https://owasp.org/www-project-application-security-verification-standard/)

**Testing:**

- [Coverlet Documentation](https://github.com/coverlet-coverage/coverlet)
- [Stryker.NET Mutation Testing](https://stryker-mutator.io/docs/stryker-net/introduction/)
