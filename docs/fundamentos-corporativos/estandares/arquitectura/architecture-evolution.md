---
id: architecture-evolution
sidebar_position: 7
title: Evolución de Arquitectura
description: Patrones para evolución arquitectónica incluyendo fitness functions, reversibilidad, selección tecnológica y twelve-factor app.
---

# Evolución de Arquitectura

## Contexto

Este estándar consolida prácticas para evolucionar arquitecturas de forma controlada. Complementa el lineamiento [Decisiones Arquitectónicas](../../lineamientos/gobierno/01-decisiones-arquitectonicas.md).

**Conceptos incluidos:**

- **Fitness Functions** → Tests automatizados de características arquitectónicas
- **Reversibility** → Decisiones reversibles vs irreversibles
- **Technology Selection** → Criterios para selección de tecnologías
- **Twelve-Factor App** → Metodología para apps cloud-native

---

## Stack Tecnológico

| Componente             | Tecnología       | Versión | Uso                                 |
| ---------------------- | ---------------- | ------- | ----------------------------------- |
| **Architecture Tests** | ArchUnitNET      | 0.10+   | Tests de arquitectura automatizados |
| **ADR**                | Markdown + Git   | -       | Architecture Decision Records       |
| **Evaluación tech**    | Technology Radar | -       | Trackeo de tecnologías              |

---

## Conceptos Fundamentales

Este estándar cubre 4 prácticas para evolución:

### Índice de Conceptos

1. **Fitness Functions**: Tests automatizados de arquitectura
2. **Reversibility**: Minimizar decisiones irreversibles
3. **Technology Selection**: Criterios objetivos
4. **Twelve-Factor App**: Cloud-native best practices

---

## 1. Fitness Functions

### ¿Qué son Fitness Functions?

Tests automatizados que validan que la arquitectura mantiene características deseadas.

**Propósito:** Prevenir erosión arquitectónica, validar constraints.

**Beneficios:**
✅ Arquitectura protegida automáticamente
✅ Refactoring seguro
✅ Onboarding más fácil

### Ejemplo

```csharp
// Architecture Tests con ArchUnitNET
[Fact]
public void Domain_Should_Not_Depend_On_Infrastructure()
{
    var architecture = new ArchLoader()
        .LoadAssemblies(typeof(Order).Assembly,  typeof(OrderRepository).Assembly)
        .Build();

    var rule = ArchRuleDefinition
        .Types()
        .That().ResideInNamespace("Domain")
        .Should().NotDependOnAny("Infrastructure");

    rule.Check(architecture);
}

[Fact]
public void Controllers_Should_Not_Have_Business_Logic()
{
    var architecture = new ArchLoader().LoadAssemblies(typeof(OrdersController).Assembly).Build();

    var rule = ArchRuleDefinition
        .Classes()
        .That().HaveNameEndingWith("Controller")
        .Should().HaveMaximumMethodLength(50); // Controllers delgados

    rule.Check(architecture);
}
```

---

## 2. Reversibility

### ¿Qué es Reversibility?

Capacidad de revertir decisiones arquitectónicas sin costo prohibitivo.

**Propósito:** Reducir riesgo, permitir experimentación.

**Decisiones reversibles vs irreversibles:**

- **Reversible**: UI framework, ORM, cache provider
- **Irreversible**: Modelo de datos, contratos públicos, compliance

**Beneficios:**
✅ Experimentación segura
✅ Menor riesgo de decisiones
✅ Adaptación al cambio

### Estrategias

```csharp
// Abstracciones para reversibilidad
public interface IEmailService // Decisión reversible: proveedor
{
    Task SendAsync(string to, string subject, string body);
}

// Implementación 1: SendGrid
public class SendGridEmailService : IEmailService { }

// Implementación 2: AWS SES (cambio reversible)
public class AwsSesEmailService : IEmailService { }

// Configuración permite cambio sin tocar código
builder.Services.AddScoped<IEmailService, AwsSesEmailService>();
```

---

## 3. Technology Selection

### ¿Qué es Technology Selection?

Proceso sistemático para seleccionar tecnologías usando criterios objetivos.

**Criterios:**

- Madurez y adopción
- Soporte y comunidad
- Licenciamiento
- Performance
- Curva de aprendizaje
- Costos (licencias + operación)

**Beneficios:**
✅ Decisiones documentadas
✅ Evaluación objetiva
✅ Reducción de riesgo técnico

### Template de Evaluación

```yaml
# Technology Evaluation Template
technology: Redis
version: 7.2+
purpose: Cache distribuido

evaluation:
  maturity:
    score: 9/10
    notes: Probado en producción por años

  performance:
    score: 10/10
    notes: Sub-millisecond latency

  cost:
    score: 8/10
    license: BSD (open source)
    operational: AWS ElastiCache ~$50/mes

  learning_curve:
    score: 7/10
    team_experience: 3/5 developers
    training_needed: false

  support:
    score: 9/10
    community: Muy activa
    enterprise_support: Disponible

alternatives_considered:
  - Memcached
  - Hazelcast

decision: ADOPT
rationale: Performance superior, equipo con experiencia, bajo costo
decision_date: 2026-02-18
review_date: 2026-08-18
```

---

## 4. Twelve-Factor App

### ¿Qué es Twelve-Factor App?

Metodología de 12 principios para construir apps cloud-native.

**Factores clave:**

1. **Codebase**: Un repo por app
2. **Dependencies**: Declarar explícitamente
3. **Config**: En environment variables
4. **Backing Services**: Recursos adjuntos vía URL
5. **Build/Release/Run**: Separación estricta
6. **Processes**: Stateless
7. **Port Binding**: Auto-contenido
8. **Concurrency**: Escalar horizontalmente
9. **Disposability**: Fast startup/shutdown
10. **Dev/Prod Parity**: Minimizar diferencias
11. **Logs**: Streams de eventos
12. **Admin Processes**: One-off tasks

**Beneficios:**
✅ Portabilidad cloud
✅ Escalamiento horizontal
✅ Deployment continuo

### Ejemplo

```csharp
// Program.cs siguiendo twelve-factor
var builder = WebApplication.CreateBuilder(args);

// Factor 2: Dependencies explícitas (NuGet packages)
builder.Services.AddControllers();
builder.Services.AddHealthChecks();

// Factor 3: Config en environment variables
var dbConnection = builder.Configuration["DATABASE_URL"]
    ?? throw new InvalidOperationException("DATABASE_URL required");

// Factor 4: Backing services como recursos
builder.Services.AddDbContext<ApplicationDbContext>(options =>
    options.UseNpgsql(dbConnection));

builder.Services.AddStackExchangeRedisCache(options =>
{
    options.Configuration = builder.Configuration["REDIS_URL"];
});

// Factor 11: Logs como streams
builder.Logging.AddJsonConsole();

var app = builder.Build();

// Factor 7: Port binding
app.Urls.Add($"http://+:{Environment.GetEnvironmentVariable("PORT") ?? "8080"}");

// Factor 6: Stateless processes
// Factor 9: Graceful shutdown
var lifetime = app.Services.GetRequiredService<IHostApplicationLifetime>();
lifetime.ApplicationStopping.Register(() =>
{
    Console.WriteLine("Application stopping - draining requests");
});

app.Run();
```

---

## Matriz de Decisión

| Escenario         | Fitness Functions | Reversibility | Tech Selection | Twelve-Factor |
| ----------------- | ----------------- | ------------- | -------------- | ------------- |
| **Nueva app**     | ✅✅              | ✅✅✅        | ✅✅✅         | ✅✅✅        |
| **Refactoring**   | ✅✅✅            | ✅✅          | ✅             | ✅            |
| **Microservicio** | ✅✅              | ✅✅          | ✅✅           | ✅✅✅        |

---

## Requisitos Técnicos

### MUST (Obligatorio)

**Fitness Functions:**

- **MUST** implementar architecture tests en CI/CD

**Reversibility:**

- **MUST** evaluar reversibilidad antes de decisiones mayores

**Technology Selection:**

- **MUST** documentar evaluación para tecnologías nuevas
- **MUST** usar ADR para decisiones arquitectónicas

**Twelve-Factor:**

- **MUST** externalizar configuración
- **MUST** diseñar stateless processes
- **MUST** declarar dependencias explícitamente

### SHOULD (Fuertemente recomendado)

- **SHOULD** revisar ADRs trimestralmente
- **SHOULD** mantener technology radar actualizado
- **SHOULD** hacer apps disposable (fast startup)

### MUST NOT (Prohibido)

- **MUST NOT** hardcodear configuración
- **MUST NOT** adoptar tecnologías sin evaluación
- **MUST NOT** ignorar fitness function failures

---

## Referencias

- [Building Evolutionary Architectures (ThoughtWorks)](https://evolutionaryarchitecture.com/)
- [The Twelve-Factor App](https://12factor.net/)
- [ArchUnit](https://www.archunit.org/)
- [Architecture Decision Records](https://adr.github.io/)
