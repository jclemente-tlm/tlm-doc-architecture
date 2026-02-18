---
id: simplicity-metrics
sidebar_position: 12
title: Simplicity Metrics
description: Métricas objetivas para medir y monitorear simplicidad del código
---

# Simplicity Metrics

## Contexto

Este estándar define **métricas objetivas** para medir simplicidad/complejidad del código. Permite identificar áreas problemáticas y **rastrear mejoras** en el tiempo. Complementa el [lineamiento de Simplicidad Intencional](../../lineamientos/arquitectura/13-simplicidad-intencional.md) con **mediciones concretas**.

---

## Core Metrics

```yaml
# ✅ Métricas principales de simplicidad

1. Cyclomatic Complexity (Complejidad Ciclomática):
  Definición: Número de caminos independientes en código
  Fórmula: Edges - Nodes + 2 (en control flow graph)

  Interpretación:
    ✅ 1-10: Simple (fácil testear, entender)
    ⚠️ 11-20: Moderado (considerar refactoring)
    ❌ 21+: Complejo (refactorizar urgente)

  Herramientas:
    - .NET: Visual Studio Code Metrics
    - SonarQube: Cognitive Complexity
    - Roslyn Analyzers

2. Lines of Code (LOC):
  Definición: Líneas de código por método/clase

  Targets:
    - Método: < 20 líneas (ideal), < 50 líneas (máximo)
    - Clase: < 200 líneas (ideal), < 500 líneas (máximo)

  Excepción: Domain entities pueden ser más grandes

3. Depth of Inheritance (DOI):
  Definición: Niveles de herencia en jerarquía

  Target:
    ✅ 0-2 niveles: Simple
    ⚠️ 3-4 niveles: Considerar composition
    ❌ 5+ niveles: Refactorizar (preferir composition)

4. Number of Dependencies (NOD):
  Definición: Dependencies inyectadas en clase

  Target:
    ✅ 0-5: Simple
    ⚠️ 6-10: Revisar si puede dividirse
    ❌ 11+: Viola SRP, refactorizar

5. Coupling Between Objects (CBO):
  Definición: Número de clases acopladas (usa o es usada)

  Target:
    ✅ 0-10: Bajo acoplamiento
    ⚠️ 11-20: Moderado
    ❌ 21+: Alto acoplamiento (difícil cambiar)

6. Maintainability Index (MI):
  Definición: Score compuesto (0-100)
  Fórmula: 171 - 5.2*ln(HalsteadVolume) - 0.23*CyclomaticComplexity - 16.2*ln(LOC)

  Interpretación:
    ✅ 80-100: Fácil mantener
    ⚠️ 50-79: Moderado
    ❌ 0-49: Difícil mantener
```

## Measuring Complexity

```csharp
// ❌ COMPLEJO: Cyclomatic Complexity = 15

public decimal CalculateDiscount(Order order, Customer customer)
{
    decimal discount = 0;

    // +1 por cada if/else/case/loop
    if (customer.IsVip)  // +1 = 2
    {
        if (order.Total > 1000)  // +2 = 4
            discount = 0.20m;
        else if (order.Total > 500)  // +3 = 7
            discount = 0.15m;
        else
            discount = 0.10m;
    }
    else if (customer.YearsActive > 5)  // +4 = 11
    {
        if (order.Total > 500)  // +5 = 16... etc
            discount = 0.10m;
        else
            discount = 0.05m;
    }
    else
    {
        if (order.ItemCount > 10)
            discount = 0.03m;
    }

    if (order.HasPromotionCode)
    {
        if (order.PromotionCode == "WELCOME")
            discount += 0.05m;
        else if (order.PromotionCode == "LOYAL")
            discount += 0.10m;
    }

    return Math.Min(discount, 0.50m);
}

// Problemas:
// - Cyclomatic Complexity: 15 (difícil testear)
// - Nested ifs (difícil leer)
// - Lógica mezclada (VIP + promotion + years)

// ✅ SIMPLE: Cyclomatic Complexity = 3

public decimal CalculateDiscount(Order order, Customer customer)
{
    var discount = 0m;

    discount += CalculateCustomerDiscount(customer, order.Total);  // +1
    discount += CalculatePromotionDiscount(order);  // +2
    discount += CalculateVolumeDiscount(order);  // +3

    return Math.Min(discount, 0.50m);
}

private decimal CalculateCustomerDiscount(Customer customer, decimal total)
{
    if (customer.IsVip)
        return GetVipDiscount(total);  // Extract Method

    if (customer.YearsActive > 5)
        return total > 500 ? 0.10m : 0.05m;

    return 0;
}

private decimal GetVipDiscount(decimal total) =>
    total switch
    {
        > 1000 => 0.20m,
        > 500 => 0.15m,
        _ => 0.10m
    };

private decimal CalculatePromotionDiscount(Order order)
{
    if (!order.HasPromotionCode) return 0;

    return order.PromotionCode switch
    {
        "WELCOME" => 0.05m,
        "LOYAL" => 0.10m,
        _ => 0
    };
}

private decimal CalculateVolumeDiscount(Order order) =>
    order.ItemCount > 10 ? 0.03m : 0;

// Mejoras:
// ✅ Cyclomatic Complexity: 3 (main) + 2-3 (cada método) = Simple
// ✅ Métodos pequeños (< 10 líneas cada uno)
// ✅ Responsabilidades separadas
// ✅ Fácil testear (1 test por método)
```

## Automated Measurement

```yaml
# ✅ Herramientas para medir automáticamente

1. SonarQube (Recomendado):

   Setup (Docker):
     docker run -d --name sonarqube \
       -p 9000:9000 \
       sonarqube:community

   Scan (.NET):
     dotnet tool install --global dotnet-sonarscanner
     dotnet sonarscanner begin /k:"sales-service" /d:sonar.host.url="http://localhost:9000"
     dotnet build
     dotnet sonarscanner end

   Métricas reportadas:
     - Cognitive Complexity (similar a Cyclomatic)
     - Code Smells
     - Technical Debt (tiempo estimado para fix)
     - Duplicación
     - Coverage

   Quality Gate (configurar):
     - Cognitive Complexity < 15 per method
     - Duplicación < 3%
     - Coverage > 80%
     - 0 Blocker issues

2. Visual Studio Code Metrics:

   Usar:
     - Visual Studio → Analyze → Calculate Code Metrics

   Output:
     Assembly: Talma.Sales.Api
       - Maintainability Index: 85 ✅
       - Cyclomatic Complexity: 234 (total)
       - Lines of Code: 1247

       Namespace: Talma.Sales.Application
         Class: CreateOrderHandler
           - MI: 72 ⚠️
           - Complexity: 8 ✅
           - LOC: 45

           Method: ExecuteAsync
             - MI: 68 ⚠️
             - Complexity: 6 ✅
             - LOC: 32

3. NDepend (Comercial):

   Features:
     - Dependency graphs
     - Code Query Language (CQL)
     - Trend analysis
     - Technical Debt estimation

   Queries útiles:
     // Methods with high complexity
     from m in Methods
     where m.CyclomaticComplexity > 15
     orderby m.CyclomaticComplexity descending
     select new { m, m.CyclomaticComplexity }

     // Classes with too many dependencies
     from t in Types
     where t.NbTypesUsed > 20
     select new { t, t.NbTypesUsed }

4. GitHub Actions (CI/CD):

   .github/workflows/code-quality.yml:
     name: Code Quality
     on: [pull_request]

     jobs:
       sonar:
         runs-on: ubuntu-latest
         steps:
           - uses: actions/checkout@v3

           - name: SonarQube Scan
             run: |
               dotnet sonarscanner begin /k:"sales" /d:sonar.host.url="${{ secrets.SONAR_URL }}"
               dotnet build
               dotnet sonarscanner end

           - name: Quality Gate
             run: |
               # Fail PR if quality gate no pasa
               curl "${SONAR_URL}/api/qualitygates/project_status?projectKey=sales" | grep '"status":"OK"'

   Result: PR bloqueado si complejidad supera threshold
```

## Complexity Budget

```yaml
# ✅ Límites por proyecto (enforcement)

Talma.Sales.Application (Core Business Logic):
  Target:
    Maintainability Index: > 80
    Avg Cyclomatic Complexity: < 5
    Max Cyclomatic Complexity: < 10
    Max Method LOC: 20
    Max Class LOC: 200

  Current (2024-12):
    MI: 85 ✅
    Avg Complexity: 4.2 ✅
    Max Complexity: 12 ⚠️ (CreateOrderHandler.ExecuteAsync)
    Avg Method LOC: 15 ✅
    Max Class LOC: 320 ❌ (Order entity)

  Actions:
    - Refactor CreateOrderHandler (split validation logic)
    - Review Order entity (considerar Value Objects)

Talma.Sales.Infrastructure:
  Target:
    MI: > 70 (más complejo permitido, integrations)
    Max Complexity: < 15

  Current:
    MI: 76 ✅
    Max Complexity: 11 ✅

Enforcement (SonarQube Quality Gate):
  - Fail build if:
      - New code MI < 80
      - New code complexity > 10
      - Duplicación > 3%
      - Coverage < 80%
```

## Tracking Trends

```yaml
# ✅ Monitorear evolución en tiempo

SonarQube Dashboard:

  Proyecto: sales-service

  Timeline (últimos 6 meses):

    ┌─────────┬────────┬────────┬──────────┬──────────┐
    │ Metric  │ Jun    │ Sep    │ Dec      │ Trend    │
    ├─────────┼────────┼────────┼──────────┼──────────┤
    │ MI      │ 78     │ 82     │ 85       │ ✅ Mejora│
    │ Smell   │ 45     │ 32     │ 28       │ ✅ Mejora│
    │ Debt    │ 8.5d   │ 5.2d   │ 4.1d     │ ✅ Reduce│
    │ Dupl    │ 5.2%   │ 3.8%   │ 2.9%     │ ✅ Reduce│
    │ Cover   │ 72%    │ 78%    │ 83%      │ ✅ Mejora│
    └─────────┴────────┴────────┴──────────┴──────────┘

  Interpretación:
    ✅ Tendencia positiva (refactoring continuo funciona)
    ✅ Technical debt reduciendo
    ✅ Coverage creciendo

  Goal (2025-Q1): MI > 88, Debt < 3d, Cover > 85%

Git Commit Messages (track refactoring):
  - "refactor: Extract CalculateDiscount methods (complexity 15→5)"
  - "refactor: Split OrderValidator (LOC 240→120)"
  - "test: Add unit tests for DiscountCalculator (cover +12%)"

  Tool: conventional-commits + dashboard
```

---

## Requisitos Técnicos

### MUST (Obligatorio)

- **MUST** medir complejidad ciclomática (target: < 10 por método)
- **MUST** mantener métodos < 50 líneas (ideal: < 20)
- **MUST** limitar dependencies < 10 por clase (ideal: < 5)
- **MUST** integrar SonarQube en CI/CD
- **MUST** configurar Quality Gate para bloquear PRs con alta complejidad

### SHOULD (Fuertemente recomendado)

- **SHOULD** monitorear Maintainability Index (target: > 80)
- **SHOULD** rastrear tendencias de complejidad mensualmente
- **SHOULD** refactorizar cuando métrica supera threshold
- **SHOULD** visualizar métricas en dashboard (Grafana/SonarQube)

### MUST NOT (Prohibido)

- **MUST NOT** mergear código con complejidad > 20
- **MUST NOT** ignorar warnings de complejidad sin justificación
- **MUST NOT** crear métodos > 100 líneas
- **MUST NOT** permitir herencia > 5 niveles

---

## Referencias

- [Lineamiento: Simplicidad Intencional](../../lineamientos/arquitectura/13-simplicidad-intencional.md)
- [Complexity Analysis](./complexity-analysis.md)
- [KISS Principle](./kiss-principle.md)
- [Refactoring Practices](./refactoring-practices.md)
