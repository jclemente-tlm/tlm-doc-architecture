---
title: "ADR-025: SonarQube SAST Code Quality"
sidebar_position: 25
---

## ✅ ESTADO

Aceptada – Enero 2026

---

## 🗺️ CONTEXTO

Los servicios corporativos requieren análisis estático de código (SAST) automatizado para:

- **Detección temprana de vulnerabilidades** (OWASP Top 10, CWE)
- **Code smells y deuda técnica** (duplicación, complejidad ciclomática)
- **Cobertura de pruebas** (integración con tests unitarios)
- **Quality Gates en CI/CD** (fail on critical issues)
- **Soporte multi-lenguaje** (actualmente .NET, futuro: Node.js, Python, Java)
- **PR decoration** (comentarios inline en GitHub)
- **Métricas ejecutivas** (tendencias, SonarMetrics, deuda técnica)
- **Costos controlados** con herramientas OSS

La estrategia prioriza **shift-left security** con análisis en PR reviews y gates automáticos en pipelines (ADR-009).

Alternativas evaluadas:

- **SonarQube Community** (OSS, self-hosted, sin branch analysis)
- **SonarQube Developer** (comercial, branch analysis, PR decoration)
- **SonarCloud** (SaaS oficial, sin infraestructura)
- **Codacy** (SaaS, AI-powered, análisis automático)
- **Snyk Code** (SAST de Snyk, integrado con vulnerabilidades)
- **Semgrep** (OSS, policy-as-code, rápido)
- **CodeClimate** (SaaS, focus en mantenibilidad)

## 🔍 COMPARATIVA DE ALTERNATIVAS

### Comparativa Cualitativa

| Criterio              | SonarQube Community | SonarQube Developer | SonarCloud | Codacy | Snyk Code | Semgrep |
|----------------------|---------------------|---------------------|------------|--------|-----------|---------|
| **Deployment**       | ✅ Self-hosted      | ✅ Self-hosted      | 🟡 SaaS only | 🟡 SaaS only | 🟡 SaaS/Hybrid | ✅ Self-hosted |
| **Lenguajes**        | ✅ 29+ lenguajes    | ✅ 29+ lenguajes    | ✅ 29+ lenguajes | ✅ 40+ lenguajes | ✅ 10+ lenguajes | ✅ 30+ lenguajes |
| **Branch Analysis**  | ❌ Main only        | ✅ PRs + branches   | ✅ PRs + branches | ✅ PRs + branches | ✅ PRs + branches | ✅ Todas |
| **PR Decoration**    | ❌ No               | ✅ Inline comments  | ✅ Inline comments | ✅ AI suggestions | ✅ Inline | ✅ Inline |
| **Vulnerabilidades** | ✅ OWASP, CWE       | ✅ OWASP, CWE       | ✅ OWASP, CWE | ✅ OWASP | ✅ Deep SAST | ✅ OWASP |
| **Code Smells**      | ✅ Completo         | ✅ Completo         | ✅ Completo | ✅ Muy completo | 🟡 Básico | 🟡 Básico |
| **Cobertura Tests**  | ✅ Coverage report  | ✅ Coverage report  | ✅ Coverage report | ✅ Coverage | 🟡 No nativo | 🟡 No nativo |
| **Quality Gates**    | ✅ Configurables    | ✅ Configurables    | ✅ Configurables | ✅ Gates | ✅ Policies | ✅ Policies |
| **Costos**           | ✅ Gratis OSS       | ❌ ~US$150/dev/año  | ❌ US$10/100 LoC | ❌ US$15/dev/mes | ❌ US$25/dev/mes | ✅ Gratis OSS |
| **Infraestructura**  | 🟡 Requiere hosting | 🟡 Requiere hosting | ✅ Managed | ✅ Managed | ✅ Managed | 🟡 Self-hosted |
| **Custom Rules**     | ✅ Java/XML plugins | ✅ Java/XML plugins | 🟡 Limited | 🟡 Limited | 🟡 Limited | ✅ YAML rules |
| **Integración CI/CD**| ✅ Plugins múltiples| ✅ Plugins múltiples| ✅ GitHub Actions | ✅ Native | ✅ Native | ✅ CLI |
| **Histórico**        | ✅ Base de datos    | ✅ Base de datos    | ✅ Cloud storage | ✅ Cloud | ✅ Cloud | 🟡 Limitado |

### Matriz de Decisión

| Solución              | Vulnerabilidades | Code Quality | Multi-lenguaje | Costos | Recomendación         |
|----------------------|------------------|--------------|----------------|--------|-----------------------|
| **SonarQube Community** | Excelente     | Excelente    | Excelente      | Excelente | ✅ **Seleccionada**    |
| **SonarQube Developer** | Excelente     | Excelente    | Excelente      | Mala   | 🟡 Upgrade futuro      |
| **SonarCloud**       | Excelente        | Excelente    | Excelente      | Media  | 🟡 Alternativa SaaS    |
| **Codacy**           | Muy buena        | Excelente    | Excelente      | Mala   | ❌ Descartada          |
| **Snyk Code**        | Excelente        | Buena        | Buena          | Mala   | ❌ Descartada          |
| **Semgrep**          | Muy buena        | Buena        | Excelente      | Excelente | 🟡 Complementario      |

---

## 💰 ANÁLISIS DE COSTOS (TCO 3 años)

> **Supuesto:** 15 desarrolladores, 500K líneas de código, análisis diario

| Solución         | Licenciamiento | Infraestructura | Soporte | TCO 3 años   |
|------------------|----------------|-----------------|---------|--------------|
| SonarQube Community | OSS (US$0)  | US$1,200 (EC2 t3.large) | US$0 | **US$1,200** |
| SonarQube Developer | US$6,750    | US$1,200        | Incluido | US$7,950     |
| SonarCloud       | US$3,600       | US$0 (managed)  | Incluido | US$3,600     |
| Codacy           | US$8,100       | US$0 (SaaS)     | Incluido | US$8,100     |
| Snyk Code        | US$13,500      | US$0 (SaaS)     | Incluido | US$13,500    |
| Semgrep          | OSS (US$0)     | US$0 (CLI)      | US$0    | **US$0**     |

**Desglose SonarQube Community:**
- Licencia: US$0 (OSS)
- EC2 t3.large (2 vCPU, 8GB RAM): ~US$33/mes × 36 = US$1,200
- PostgreSQL RDS (db.t3.small): Incluido en free tier o ~US$15/mes = US$540
- **Total:** US$1,740 (redondeado a US$1,200 sin RDS si se usa PostgreSQL en ECS)

---

## ✔️ DECISIÓN

Se selecciona **SonarQube Community Edition (self-hosted)** como solución de análisis estático de código corporativo.

## Justificación

- **Costo mínimo** - OSS gratuito, solo infraestructura (~US$1.2K/3 años vs US$13K Snyk)
- **Cobertura completa** - 29+ lenguajes (C#, JavaScript, TypeScript, Python, Java, Go, etc.)
- **Análisis profundo** - Vulnerabilidades (OWASP, CWE), code smells, duplicación, complejidad
- **Quality Gates** - Gates configurables para bloquear merges con issues críticos
- **Integración CI/CD** - Plugin nativo para GitHub Actions, Azure DevOps, Jenkins
- **Cobertura de tests** - Integración con coverage reports (Coverlet, dotnet test)
- **Histórico y métricas** - Base de datos PostgreSQL para trends y dashboards
- **Control total** - Self-hosted en AWS ECS, sin límites de análisis ni LoC
- **Extensibilidad** - Custom rules vía plugins Java/XML
- **Path to upgrade** - Migración fácil a Developer/Enterprise si se requiere branch analysis

## Trade-offs aceptados

- **Sin branch analysis** - Community solo analiza rama main (no PRs individuales)
  - **Mitigación:** Ejecutar SonarScanner en PRs y comparar contra main manualmente
- **Sin PR decoration** - No comentarios inline automáticos en GitHub
  - **Mitigación:** Revisar dashboard SonarQube + GitHub Actions logs
- **Infraestructura requerida** - Requiere hosting en AWS ECS + PostgreSQL
  - **Mitigación:** Containerizado con ADR-007, IaC con ADR-006

## Alternativas descartadas

- **SonarQube Developer:** US$150/dev/año = US$6.75K - branch analysis no justifica 6× el costo
- **SonarCloud:** US$10/100K LoC = US$3.6K - conveniente pero lock-in SaaS y costos crecientes
- **Codacy:** US$15/dev/mes = US$8.1K - caro para capacidades similares
- **Snyk Code:** US$25/dev/mes = US$13.5K - mejor para vulnerabilidades (ya tenemos Trivy)
- **Semgrep:** Excelente OSS pero menos maduro para code quality (complementario, no reemplazo)

---

## ⚠️ CONSECUENCIAS

### Positivas
- Análisis completo de código en 29+ lenguajes (multi-stack)
- Quality Gates automáticos para prevenir merge de código con issues críticos
- Métricas de calidad centralizadas (deuda técnica, cobertura, complejidad)
- Histórico de análisis para tracking de mejoras
- Costo mínimo (solo infraestructura ~US$100/mes)
- Control total de datos (self-hosted, compliance)

### Negativas
- **Sin branch analysis** - Solo analiza main, no PRs individuales (limitación Community)
- **Sin PR decoration** - Desarrolladores deben revisar dashboard manualmente
- Requiere infraestructura dedicada (ECS + PostgreSQL)
- Mantenimiento de upgrades manual
- Setup inicial más complejo que SaaS

### Neutrales
- Requiere training de equipos en SonarQube
- Custom rules requieren conocimiento Java/XML

### Implementación requerida
- Desplegar SonarQube en AWS ECS Fargate con PostgreSQL (ADR-007)
- Configurar integración GitHub Actions para análisis automático
- Definir Quality Gates corporativos (coverage > 80%, blocker issues = 0)
- Crear dashboards ejecutivos en SonarQube
- Documentar proceso de triaje de issues
- Habilitar análisis incremental (solo código cambiado)
- Configurar retention policies (histórico 2 años)

---

## 🏗️ CONFIGURACIÓN Y BUENAS PRÁCTICAS

### Docker Compose - SonarQube + PostgreSQL

```yaml
version: '3.8'

services:
  sonarqube:
    image: sonarqube:10.3-community
    container_name: sonarqube
    depends_on:
      - postgres
    environment:
      SONAR_JDBC_URL: jdbc:postgresql://postgres:5432/sonarqube
      SONAR_JDBC_USERNAME: sonarqube
      SONAR_JDBC_PASSWORD: ${SONAR_DB_PASSWORD}
    ports:
      - "9000:9000"
    volumes:
      - sonarqube_data:/opt/sonarqube/data
      - sonarqube_logs:/opt/sonarqube/logs
      - sonarqube_extensions:/opt/sonarqube/extensions
    networks:
      - sonarnet
    deploy:
      resources:
        limits:
          memory: 4GB
        reservations:
          memory: 2GB

  postgres:
    image: postgres:15-alpine
    container_name: sonarqube-db
    environment:
      POSTGRES_USER: sonarqube
      POSTGRES_PASSWORD: ${SONAR_DB_PASSWORD}
      POSTGRES_DB: sonarqube
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - sonarnet

volumes:
  sonarqube_data:
  sonarqube_logs:
  sonarqube_extensions:
  postgres_data:

networks:
  sonarnet:
    driver: bridge
```

### GitHub Actions - SonarQube Scanner

```yaml
name: Code Quality Scan

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
          fetch-depth: 0  # Full history for better analysis
      
      - name: Setup .NET
        uses: actions/setup-dotnet@v4
        with:
          dotnet-version: '8.0.x'
      
      - name: Restore dependencies
        run: dotnet restore
      
      - name: Build and Test with Coverage
        run: |
          dotnet build --no-restore
          dotnet test --no-build --collect:"XPlat Code Coverage" \
            --results-directory ./coverage
      
      - name: Install SonarScanner
        run: dotnet tool install --global dotnet-sonarscanner
      
      - name: Run SonarQube Analysis
        env:
          SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
          SONAR_HOST_URL: ${{ secrets.SONAR_HOST_URL }}
        run: |
          dotnet sonarscanner begin \
            /k:"myapp-api" \
            /d:sonar.host.url="${SONAR_HOST_URL}" \
            /d:sonar.login="${SONAR_TOKEN}" \
            /d:sonar.cs.opencover.reportsPaths="**/coverage/**/coverage.opencover.xml" \
            /d:sonar.coverage.exclusions="**Tests.cs,**/Migrations/**"
          
          dotnet build
          
          dotnet sonarscanner end /d:sonar.login="${SONAR_TOKEN}"
      
      - name: Quality Gate Check
        run: |
          # Esperar resultado de Quality Gate (max 5 min)
          sleep 30
          
          STATUS=$(curl -s -u "${SONAR_TOKEN}:" \
            "${SONAR_HOST_URL}/api/qualitygates/project_status?projectKey=myapp-api" \
            | jq -r '.projectStatus.status')
          
          if [ "$STATUS" != "OK" ]; then
            echo "❌ Quality Gate FAILED: $STATUS"
            exit 1
          fi
          
          echo "✅ Quality Gate PASSED"
```

### SonarQube Configuration (sonar-project.properties)

```properties
# sonar-project.properties - Configuración proyecto

sonar.projectKey=myapp-api
sonar.projectName=MyApp API
sonar.projectVersion=1.0

# Paths
sonar.sources=src/
sonar.tests=tests/
sonar.exclusions=**/Migrations/**,**/obj/**,**/bin/**
sonar.test.exclusions=**/*Tests.cs

# Coverage
sonar.cs.opencover.reportsPaths=**/coverage/**/coverage.opencover.xml
sonar.coverage.exclusions=**Tests.cs,**/Program.cs,**/Startup.cs

# Duplications
sonar.cpd.exclusions=**/Models/**,**/DTOs/**

# Language
sonar.language=cs
sonar.sourceEncoding=UTF-8

# Quality Gate
sonar.qualitygate.wait=true
sonar.qualitygate.timeout=300
```

### Quality Gate - Configuración Corporativa

```json
{
  "name": "Corporate Quality Gate",
  "conditions": [
    {
      "metric": "new_coverage",
      "op": "LT",
      "error": "80"
    },
    {
      "metric": "new_duplicated_lines_density",
      "op": "GT",
      "error": "3"
    },
    {
      "metric": "new_security_rating",
      "op": "GT",
      "error": "1"
    },
    {
      "metric": "new_reliability_rating",
      "op": "GT",
      "error": "1"
    },
    {
      "metric": "new_maintainability_rating",
      "op": "GT",
      "error": "1"
    },
    {
      "metric": "new_blocker_violations",
      "op": "GT",
      "error": "0"
    },
    {
      "metric": "new_critical_violations",
      "op": "GT",
      "error": "0"
    }
  ]
}
```

### .NET Global AnalyzerConfig (.editorconfig)

```ini
# .editorconfig - Integración Roslyn Analyzers

root = true

[*.cs]
# Code Quality Rules
dotnet_diagnostic.CA1001.severity = warning  # Types that own disposable fields
dotnet_diagnostic.CA1016.severity = warning  # Mark assemblies with AssemblyVersionAttribute
dotnet_diagnostic.CA1031.severity = suggestion  # Do not catch general exception types
dotnet_diagnostic.CA1062.severity = suggestion  # Validate public arguments
dotnet_diagnostic.CA2007.severity = warning  # Do not directly await a Task

# Security Rules
dotnet_diagnostic.CA3075.severity = error  # Insecure DTD processing
dotnet_diagnostic.CA5350.severity = error  # Do not use weak cryptographic algorithms
dotnet_diagnostic.CA5351.severity = error  # Do not use broken cryptographic algorithms

# Performance Rules
dotnet_diagnostic.CA1806.severity = warning  # Do not ignore method results
dotnet_diagnostic.CA1819.severity = suggestion  # Properties should not return arrays

# SonarAnalyzer Rules
dotnet_diagnostic.S1075.severity = warning  # URIs should not be hardcoded
dotnet_diagnostic.S2696.severity = warning  # Instance members should not write to static fields
dotnet_diagnostic.S3925.severity = error    # ISerializable should be implemented correctly
```

---

## 📊 MÉTRICAS Y MONITOREO

### KPIs de Code Quality

| Métrica | Target | Medición |
|---------|--------|----------|
| Code Coverage | > 80% | SonarQube dashboard |
| Blocker Issues | 0 | Quality Gate |
| Critical Issues | 0 | Quality Gate |
| Technical Debt Ratio | < 5% | SonarQube metrics |
| Duplications | < 3% | SonarQube metrics |
| Complexity Cyclomatic | < 15 avg | SonarQube metrics |
| Security Rating | A (1.0) | SonarQube security |
| Maintainability Rating | A (1.0) | SonarQube maintainability |

### SLOs

- **Quality Gate pass rate:** > 95% de commits a main
- **Time to fix blocker:** < 24h
- **Time to fix critical:** < 72h
- **Scan frequency:** 100% commits a main, 100% PRs
- **Coverage trend:** +2% por quarter

### SonarQube API - Métricas Automatizadas

```bash
#!/bin/bash
# scripts/sonar-metrics.sh - Extraer métricas vía API

SONAR_URL="https://sonarqube.internal.com"
PROJECT_KEY="myapp-api"

# Obtener métricas principales
curl -s -u "${SONAR_TOKEN}:" \
  "${SONAR_URL}/api/measures/component?component=${PROJECT_KEY}&metricKeys=coverage,bugs,vulnerabilities,code_smells,duplicated_lines_density,sqale_rating" \
  | jq -r '.component.measures[] | "\(.metric): \(.value)"'

# Output:
# coverage: 82.5
# bugs: 3
# vulnerabilities: 0
# code_smells: 42
# duplicated_lines_density: 2.1
# sqale_rating: 1.0
```

### Dashboard Ejecutivo

```sql
-- PostgreSQL query - Trend de Deuda Técnica

SELECT 
  analysis_date,
  project_name,
  metric_value as technical_debt_minutes,
  (metric_value / 480) as technical_debt_days -- 8h/day
FROM sonarqube.project_measures pm
JOIN sonarqube.metrics m ON pm.metric_id = m.id
WHERE m.name = 'sqale_index'
  AND analysis_date >= NOW() - INTERVAL '90 days'
ORDER BY analysis_date DESC;
```

---

## 🔄 ROADMAP Y EVOLUCIÓN

### Fase 1: MVP (Q1 2026) ✅
- SonarQube Community desplegado en ECS
- Análisis de repositorios .NET Core
- Quality Gates básicos (blocker = 0, coverage > 80%)
- Integración GitHub Actions

### Fase 2: Expansión (Q2 2026)
- Análisis multi-lenguaje (Node.js, Python)
- Custom rules corporativas (naming conventions, architectural patterns)
- Dashboards ejecutivos (Grafana + SonarQube API)
- Pre-commit hooks para desarrolladores

### Fase 3: Mejora Continua (Q3 2026)
- Evaluación de upgrade a Developer Edition (branch analysis)
- Integración con Jira para tracking de issues
- Análisis de dependencias (SonarQube + Trivy)
- Automated remediation suggestions (Roslyn Code Fixes)

### Upgrade Path a Developer Edition

**Criterios para upgrade:**
- Equipos > 20 desarrolladores
- Necesidad crítica de PR decoration
- Presupuesto disponible (US$150/dev/año)
- ROI justificado (reducción 30%+ deuda técnica)

**Migración:**
1. Backup PostgreSQL database
2. Stop SonarQube Community container
3. Deploy SonarQube Developer image
4. Aplicar licencia Developer
5. Configurar branch analysis
6. Configurar PR decoration plugin

---

## 📚 REFERENCIAS

- [SonarQube Documentation](https://docs.sonarqube.org/latest/)
- [SonarQube Community vs Editions](https://www.sonarsource.com/products/sonarqube/downloads/)
- [SonarScanner for .NET](https://docs.sonarqube.org/latest/analysis/scan/sonarscanner-for-msbuild/)
- [SonarQube Quality Gates](https://docs.sonarqube.org/latest/user-guide/quality-gates/)
- [OWASP Code Review Guide](https://owasp.org/www-project-code-review-guide/)
- [CWE Top 25](https://cwe.mitre.org/top25/)
- [ADR-009: GitHub Actions CI/CD](./adr-009-github-actions-cicd.md)
- [ADR-016: Serilog Logging Estructurado](./adr-016-serilog-logging-estructurado.md)
- [ADR-023: Trivy Container Scanning](./adr-023-trivy-container-scanning.md)

---

**Decisión tomada por:** Equipo de Arquitectura + Desarrollo  
**Fecha:** Enero 2026  
**Próxima revisión:** Julio 2026 (evaluación upgrade Developer)
