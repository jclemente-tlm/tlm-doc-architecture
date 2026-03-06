---
id: sast
sidebar_position: 12
title: SAST — Análisis Estático de Seguridad
description: Estándar para integrar análisis estático de seguridad (SAST) en el pipeline CI/CD con CodeQL, Semgrep y dotnet-security-scan.
tags: [seguridad, sast, static-analysis, codeql, semgrep, ci-cd]
---

# SAST — Análisis Estático de Seguridad

## Contexto

El análisis estático de seguridad detecta vulnerabilidades en el código antes del deploy. Complementa el lineamiento [Seguridad y Resiliencia](../../lineamientos/arquitectura/06-seguridad-y-resiliencia.md).

**Cuándo aplicar:** Todo servicio con pipeline CI/CD. Obligatorio antes de merge a `main`.

:::note Implementación gestionada por Seguridad
Este estándar define los **requisitos de análisis estático que los servicios deben cumplir**. La configuración de herramientas SAST, políticas de alertas y umbrales de severidad son responsabilidad del equipo de **Seguridad**. Consultar en **#security**.
:::

---

## Stack Tecnológico

| Componente | Tecnología           | Uso                                |
| ---------- | -------------------- | ---------------------------------- |
| **SAST**   | CodeQL / Semgrep     | Vulnerabilidades en código         |
| **Deps**   | dotnet-security-scan | Vulnerabilidades en paquetes NuGet |
| **CI/CD**  | GitHub Actions       | Integración en pipeline            |

---

## SAST (Static Application Security Testing)

### ¿Qué es SAST?

Análisis estático de código para identificar vulnerabilidades de seguridad sin ejecutar el código.

**Vulnerabilidades detectadas:**

- **Injection flaws**: SQL injection, command injection
- **Authentication issues**: Weak password validation
- **Sensitive data exposure**: Hardcoded secrets
- **Security misconfiguration**: Insecure defaults
- **Known vulnerable dependencies**: CVEs en packages

**Propósito:** Detectar vulnerabilidades temprano (shift-left security).

**Beneficios:**
✅ Detección temprana de vulnerabilidades
✅ Menor costo de remediación
✅ Cumplimiento de seguridad
✅ Educación del equipo

### SonarQube Configuration

```yaml
# sonar-project.properties
# Configuración de SonarQube para .NET

sonar.projectKey=customer-service
sonar.projectName=Customer Service
sonar.projectVersion=1.0

# Source
sonar.sources=src
sonar.tests=tests

# Exclusions
sonar.exclusions=**/Migrations/**,**/wwwroot/**,**/obj/**,**/bin/**

# Coverage
sonar.cs.opencover.reportsPaths=**/coverage.opencover.xml
sonar.coverage.exclusions=**/Tests/**,**/Migrations/**

# Language
sonar.language=cs

# Quality Gate
sonar.qualitygate.wait=true
sonar.qualitygate.timeout=300
```

```yaml
# .github/workflows/sonarqube.yml
# Integración de SonarQube en CI/CD

name: SonarQube Analysis

on:
  push:
    branches: [main]
  pull_request:
    types: [opened, synchronize, reopened]

jobs:
  sonarqube:
    name: SonarQube Scan
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0 # Full history for better analysis

      - uses: actions/setup-dotnet@v4
        with:
          dotnet-version: "8.0.x"

      - name: Install SonarScanner
        run: dotnet tool install --global dotnet-sonarscanner

      - name: Restore dependencies
        run: dotnet restore

      - name: Begin SonarQube analysis
        env:
          SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
        run: |
          dotnet sonarscanner begin \
            /k:"customer-service" \
            /d:sonar.host.url="${{ secrets.SONAR_HOST_URL }}" \
            /d:sonar.login="${{ secrets.SONAR_TOKEN }}" \
            /d:sonar.cs.opencover.reportsPaths="**/coverage.opencover.xml"

      - name: Build
        run: dotnet build --no-restore

      - name: Test with coverage
        run: |
          dotnet test --no-build --verbosity normal \
            /p:CollectCoverage=true \
            /p:CoverletOutputFormat=opencover

      - name: End SonarQube analysis
        env:
          SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
        run: dotnet sonarscanner end /d:sonar.login="${{ secrets.SONAR_TOKEN }}"
```

### OWASP Dependency Check

```yaml
# .github/workflows/dependency-check.yml
# Escaneo de vulnerabilidades en dependencias

name: OWASP Dependency Check

on:
  push:
    branches: [main]
  pull_request:
  schedule:
    - cron: "0 2 * * 1" # Weekly scan Monday 2am

jobs:
  dependency-check:
    name: Dependency Vulnerability Scan
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Run OWASP Dependency-Check
        uses: dependency-check/Dependency-Check_Action@main
        with:
          project: "customer-service"
          path: "."
          format: "HTML"
          args: >
            --enableRetired
            --failOnCVSS 7
            --suppression dependency-check-suppressions.xml

      - name: Upload results
        uses: actions/upload-artifact@v4
        with:
          name: dependency-check-report
          path: ${{ github.workspace }}/reports
```

---
