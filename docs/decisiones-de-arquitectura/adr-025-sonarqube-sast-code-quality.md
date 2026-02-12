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
- **CodeQL** (GitHub native, semantic analysis, OSS engine)
- **Veracode** (Enterprise SAST líder, completo, costoso)
- **Codacy** (SaaS, AI-powered, análisis automático)
- **Snyk Code** (SAST de Snyk, integrado con vulnerabilidades)
- **Semgrep** (OSS, policy-as-code, rápido)
- **CodeClimate** (SaaS, focus en mantenibilidad)

## 🔍 COMPARATIVA DE ALTERNATIVAS

### Comparativa Cualitativa

| Criterio              | SonarQube CE     | SonarQube Dev    | SonarCloud       | CodeQL           | Veracode            | Codacy            | Snyk Code        | Semgrep          |
| --------------------- | ---------------- | ---------------- | ---------------- | ---------------- | ------------------- | ----------------- | ---------------- | ---------------- |
| **Deployment**        | ✅ Self-hosted   | ✅ Self-hosted   | ⚠️ SaaS only     | ✅ Self/SaaS     | ⚠️ SaaS only        | ⚠️ SaaS only      | ⚠️ SaaS/Hybrid   | ✅ Self-hosted   |
| **Lenguajes**         | ✅ 29+ lenguajes | ✅ 29+ lenguajes | ✅ 29+ lenguajes | ✅ 20+ lenguajes | ✅ 130+ lenguajes   | ✅ 40+ lenguajes  | ✅ 10+ lenguajes | ✅ 30+ lenguajes |
| **Branch Analysis**   | ❌ Main only     | ✅ PRs+branches  | ✅ PRs+branches  | ✅ PRs+branches  | ✅ PRs+branches     | ✅ PRs+branches   | ✅ PRs+branches  | ✅ Todas         |
| **PR Decoration**     | ❌ No            | ✅ Inline        | ✅ Inline        | ✅ Native GitHub | ✅ Inline           | ✅ AI suggestions | ✅ Inline        | ✅ Inline        |
| **Vulnerabilidades**  | ✅ OWASP, CWE    | ✅ OWASP, CWE    | ✅ OWASP, CWE    | ✅ CWE deep      | ✅ OWASP enterprise | ✅ OWASP          | ✅ Deep SAST     | ✅ OWASP         |
| **Code Smells**       | ✅ Completo      | ✅ Completo      | ✅ Completo      | ⚠️ Básico        | ✅ Completo         | ✅ Muy completo   | ⚠️ Básico        | ⚠️ Básico        |
| **Cobertura Tests**   | ✅ Coverage      | ✅ Coverage      | ✅ Coverage      | ⚠️ No nativo     | ✅ Coverage         | ✅ Coverage       | ⚠️ No nativo     | ⚠️ No nativo     |
| **Quality Gates**     | ✅ Config        | ✅ Config        | ✅ Config        | ✅ Policies      | ✅ Policies         | ✅ Gates          | ✅ Policies      | ✅ Policies      |
| **Costos**            | ✅ Gratis OSS    | ❌ ~US$150/dev   | ❌ US$10/100 LoC | ✅ Gratis OSS    | ❌ US$50K+ setup    | ❌ US$15/dev/mes  | ❌ US$25/dev/mes | ✅ Gratis OSS    |
| **Infraestructura**   | ⚠️ Hosting       | ⚠️ Hosting       | ✅ Managed       | ⚠️ Hosting       | ✅ Managed          | ✅ Managed        | ✅ Managed       | ⚠️ Self-hosted   |
| **Custom Rules**      | ✅ Plugins       | ✅ Plugins       | ⚠️ Limited       | ✅ QL queries    | ⚠️ Limited          | ⚠️ Limited        | ⚠️ Limited       | ✅ YAML rules    |
| **Integración CI/CD** | ✅ Plugins       | ✅ Plugins       | ✅ GitHub        | ✅ Native GitHub | ✅ Plugins          | ✅ Native         | ✅ Native        | ✅ CLI           |
| **Histórico**         | ✅ BD            | ✅ BD            | ✅ Cloud         | ✅ GitHub        | ✅ Cloud            | ✅ Cloud          | ✅ Cloud         | ⚠️ Limitado      |

**Leyenda:** ✅ Cumple completamente | ⚠️ Cumple parcialmente | ❌ No cumple

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

## Alternativas descartadas

- **CodeQL:** excelente para GitHub pero limitado a vulnerabilidades/security (no code smells, duplicación, cobertura), enfoque semántico profundo pero análisis más lento, menor soporte para métricas de calidad vs SonarQube
- **Veracode:** líder enterprise SAST pero costos prohibitivos (US$50K+ setup + US$25K+/año), orientado a compliance y grandes corporaciones, sobrede-dimensionado para escala actual
- **SonarQube Developer:** US$150/dev/año = US$6.75K - branch analysis no justifica 6× el costo vs Community
- **SonarCloud:** US$10/100K LoC = US$3.6K - conveniente pero lock-in SaaS y costos crecientes con codebase
- **Codacy:** US$15/dev/mes = US$8.1K - caro para capacidades similares, AI features no esenciales
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

---

**Decisión tomada por:** Equipo de Arquitectura + Desarrollo
**Fecha:** Enero 2026
**Próxima revisión:** Julio 2026 (evaluación upgrade Developer)
