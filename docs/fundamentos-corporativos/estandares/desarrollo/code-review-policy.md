---
id: code-review-policy
sidebar_position: 3
title: Política de Code Review
description: Estándar para revisión de código obligatoria (aplicación + IaC) según GitHub Flow, con checklist de seguridad, performance y arquitectura.
---

# Estándar Técnico — Política de Code Review

---

## 1. Propósito

Garantizar calidad, seguridad y mantenibilidad mediante **code review obligatorio** para todo código (aplicación + IaC), siguiendo **GitHub Flow** con aprobación mínima de 1 reviewer técnico antes de merge.

---

## 2. Alcance

**Aplica a:**

- Código de aplicación (.NET, C#)
- Infrastructure as Code (Terraform)
- Scripts de BD (migrations, stored procedures)
- Configuraciones críticas (CI/CD pipelines, security policies)
- Documentación técnica (ADRs, estándares)

**No aplica a:**

- Hotfixes SEV-1 en producción (revisar post-merge)
- Configuraciones dev/sandbox personales
- Documentación no técnica (marketing, user guides)

---

## 3. Requisitos Obligatorios 🔴

### 3.1 Proceso de Review

- [ ] **Branch protection** habilitado en `main`/`master`
- [ ] **Mínimo 1 aprobación** de reviewer técnico antes de merge
- [ ] **CI/CD passing**: tests, linters, security scans OK
- [ ] **NO self-approval** (autor ≠ reviewer)
- [ ] **Max 48 horas** para primera revisión (SLA)
- [ ] Cambios menores (<50 líneas): 1 reviewer
- [ ] Cambios mayores (>200 líneas): 2 reviewers O arquitecto
- [ ] IaC changes: reviewer debe tener experiencia AWS/Terraform

### 3.2 Responsabilidades del Autor

- [ ] PR title descriptivo: `[TICKET-123] Add user authentication`
- [ ] Descripción clara: **qué** cambia, **por qué**, **cómo** testear
- [ ] Self-review antes de pedir aprobación
- [ ] Tests incluidos (unit + integration cuando aplique)
- [ ] Documentación actualizada (README, ADRs si aplica)
- [ ] Commits atómicos con mensajes claros
- [ ] PR pequeño (<400 líneas idealmente, max 800)

### 3.3 Responsabilidades del Reviewer

- [ ] Revisar en **<48 horas** (priorizar PRs bloqueantes)
- [ ] Comentarios constructivos, no solo críticas
- [ ] Verificar checklist completo (ver sección 4)
- [ ] Probar localmente si cambios complejos
- [ ] Aprobar SOLO si entiendes el código completamente
- [ ] Sugerir mejoras, NO reescribir todo
- [ ] Distinguir: **bloqueante** (debe cambiar) vs **nice-to-have**

---

## 4. Checklist de Revisión

### 4.1 Funcionalidad

- [ ] Cumple requisitos del ticket/feature
- [ ] Casos edge cubiertos (inputs vacíos, null, errores de red)
- [ ] Validaciones de entrada implementadas
- [ ] Manejo de errores apropiado (try-catch, logs)

### 4.2 Seguridad

- [ ] **NO secrets hardcodeados** (passwords, API keys, tokens)
- [ ] Inputs sanitizados (prevención SQL injection, XSS)
- [ ] Autenticación/autorización correcta (atributos `[Authorize]`)
- [ ] HTTPS enforced para APIs públicas
- [ ] Logs NO exponen información sensible (PII, passwords)
- [ ] Dependencias sin vulnerabilidades críticas (`dotnet list package --vulnerable`)

### 4.3 Performance

- [ ] Queries BD eficientes (índices, NO N+1)
- [ ] Uso apropiado de caché (Redis, memory cache)
- [ ] Paginación implementada para listas grandes (NO `SELECT *` sin LIMIT)
- [ ] Async/await usado correctamente (NO blocking calls)
- [ ] Conexiones BD/HTTP cerradas apropiadamente

### 4.4 Arquitectura y Diseño

- [ ] Sigue principios SOLID (responsabilidad única, etc.)
- [ ] Consistente con patrones del proyecto (repositories, services)
- [ ] NO lógica de negocio en controllers
- [ ] Inyección de dependencias usada correctamente
- [ ] Nombres claros y descriptivos (métodos, variables, clases)

### 4.5 Testing

- [ ] Unit tests para lógica de negocio (coverage >80%)
- [ ] Integration tests para APIs/BD cuando aplique
- [ ] Tests pasan localmente Y en CI
- [ ] Tests nombrados: `MethodName_Scenario_ExpectedResult`
- [ ] Mocks usados apropiadamente (NO dependencias reales en unit tests)

### 4.6 Infrastructure as Code

- [ ] Recursos parametrizados (NO hardcodear IPs, ARNs)
- [ ] Tags obligatorios: `Environment`, `Project`, `Owner`
- [ ] Security groups restrictivos (NO `0.0.0.0/0` en producción)
- [ ] Encryption habilitado (RDS, S3, EBS)
- [ ] Terraform plan ejecutado y validado

### 4.7 Documentación

- [ ] README actualizado si cambian comandos/setup
- [ ] ADR creado si decisión arquitectónica significativa
- [ ] Comentarios en código SOLO cuando necesario (código auto-explicativo primero)
- [ ] API endpoints documentados (Swagger/OpenAPI)

---

## 5. Tamaño de PRs

| Tamaño | Líneas  | Tiempo Revisión | Reviewers      | Recomendación            |
| ------ | ------- | --------------- | -------------- | ------------------------ |
| **XS** | <50     | <30 min         | 1              | ✅ Ideal                 |
| **S**  | 50-200  | 1 hora          | 1              | ✅ OK                    |
| **M**  | 200-400 | 2-3 horas       | 1-2            | ⚠️ Considerar dividir    |
| **L**  | 400-800 | >4 horas        | 2              | 🔴 Dividir si es posible |
| **XL** | >800    | >1 día          | 2 + arquitecto | 🔴 Dividir obligatorio   |

**PRs >800 líneas requieren justificación** (ej: migration masivo, generación código).

---

## 6. Branch Protection Rules

```yaml
# GitHub Branch Protection Settings para 'main'
require_pull_request_reviews: true
required_approving_review_count: 1
dismiss_stale_reviews: true # Nueva commit → re-approval
require_code_owner_reviews: false # Opcional, para equipos grandes
require_status_checks_before_merging: true
required_status_checks:
  - ci/build
  - ci/test
  - security/snyk-scan
enforce_admins: true # Ni admins pueden bypass
allow_force_pushes: false
allow_deletions: false
```

---

## 7. Ejemplo de PR Template

```markdown
## Descripción

[Breve resumen del cambio]

## Ticket

Closes #[TICKET-ID]

## Tipo de cambio

- [ ] Feature nueva
- [ ] Bug fix
- [ ] Refactoring
- [ ] Cambio de infraestructura
- [ ] Documentación

## Cómo testear

1. Levantar ambiente local: `docker-compose up`
2. Ejecutar: `curl -X POST http://localhost:5000/api/orders`
3. Verificar: response 201 Created

## Checklist

- [ ] Self-review realizado
- [ ] Tests agregados/actualizados
- [ ] Documentación actualizada
- [ ] CI passing
- [ ] NO secrets hardcodeados

## Screenshots (si aplica)

[Capturas de pantalla para cambios UI]
```

---

## 8. Excepciones

### Hotfixes SEV-1

- **Merge sin review permitido** para restaurar servicio crítico
- **Post-merge review obligatorio** dentro de 24 horas
- **Postmortem** debe incluir análisis de por qué falló prevención

### Cambios cosméticos

- Typos en comentarios, formateo automático (linters)
- **1 approval suficiente**, reviewer puede aprobar rápidamente

---

## 9. Validación

**Métricas de cumplimiento:**

| Métrica                  | Target     | Verificación       |
| ------------------------ | ---------- | ------------------ |
| PRs mergeados sin review | 0%         | GitHub audit log   |
| Tiempo primera revisión  | <48 horas  | GitHub metrics     |
| PRs >800 líneas          | <5%        | GitHub metrics     |
| Vulnerabilidades en deps | 0 críticas | Snyk/Dependabot    |
| Code coverage            | >80%       | Coverlet/SonarQube |

Incumplimientos detectados en audits mensuales escalan a Tech Lead.

---

## 10. Referencias

- [GitHub Flow](https://docs.github.com/en/get-started/quickstart/github-flow)
- [Google Code Review Guidelines](https://google.github.io/eng-practices/review/)
- [Estándar: Testing Unitario](../testing/01-unit-tests.md)
- [Estándar: Infrastructure as Code](../infraestructura/infrastructure-as-code.md)
- [Estándar: Security by Design](../seguridad/security-by-design.md)
