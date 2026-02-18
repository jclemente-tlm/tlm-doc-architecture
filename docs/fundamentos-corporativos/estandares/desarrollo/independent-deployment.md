---
id: independent-deployment
sidebar_position: 1
title: Independent Deployment
description: Habilitar despliegue independiente de servicios sin coordinación ni impacto en otros servicios
---

# Independent Deployment

## Contexto

Este estándar define prácticas para habilitar **despliegue independiente** de servicios, permitiendo que cada servicio se despliegue sin coordinación con otros servicios. Complementa el [lineamiento de Autonomía de Servicios](../../lineamientos/arquitectura/10-autonomia-de-servicios.md) asegurando **velocidad de entrega y resiliencia**.

---

## Conceptos Fundamentales

### ¿Qué es Independent Deployment?

```yaml
# ✅ Independent Deployment = Desplegar sin afectar otros servicios

Definición:
  Capacidad de desplegar un servicio a producción sin:
    - Coordinación sincronizada con otros equipos
    - Despliegue simultáneo de otros servicios
    - Downtime de otros servicios
    - Romper funcionalidad existente

Características: ✅ Deploy en cualquier momento (24/7)
  ✅ Sin ventanas de mantenimiento sincronizadas
  ✅ Rollback independiente
  ✅ Testing independiente
  ✅ Versioning independiente

Beneficios:
  ✅ Velocidad: Deploy múltiples veces al día
  ✅ Autonomía: Equipos no bloqueados por otros equipos
  ✅ Riesgo reducido: Cambio pequeño, fácil rollback
  ✅ MTTR bajo: Rollback rápido si hay problema

Anti-patterns que impiden independent deployment:
  ❌ Shared database con breaking schema changes
  ❌ Tight coupling (llamadas síncronas sin versionado)
  ❌ Big bang deployments (todos los servicios juntos)
  ❌ Transacciones distribuidas (2PC)
```

### Comparación

```yaml
# ❌ MALO: Deployment Coordinado

Escenario: Sales Service v2.0 requiere Fulfillment Service v2.0

Viernes 8 PM:
  1. Notificar equipos: Sales + Fulfillment + QA + On-Call
  2. Aplicar DB migrations en Sales DB
  3. Aplicar DB migrations en Fulfillment DB
  4. Desplegar Sales Service v2.0
  5. ❌ Sales roto hasta que Fulfillment esté desplegado
  6. Desplegar Fulfillment Service v2.0
  7. ❌ Si falla, rollback de AMBOS servicios
  8. Smoke testing manual (30 min)
  9. Fin: 10 PM (2 horas)

Problemas:
  - Ventana de deployment larga (2 horas)
  - Coordinación de 3 equipos
  - Riesgo alto (cambio grande)
  - Rollback complejo
  - Deployment solo viernes noche

# ✅ BUENO: Independent Deployment

Escenario: Sales Service v2.1

Martes 2 PM:
  1. GitHub Actions ejecuta pipeline automático
  2. Aplicar DB migration en Sales DB
  3. Deploy Sales Service v2.1 (rolling deployment)
  4. ✅ Fulfillment no afectado (no depende de Sales v2.1)
  5. ✅ Smoke tests automáticos (5 min)
  6. ✅ Si falla, rollback automático solo Sales
  7. Fin: 2:15 PM (15 minutos)

Beneficios:
  - Sin coordinación
  - Deploy rápido (15 min)
  - Riesgo bajo (cambio pequeño)
  - Cualquier día, cualquier hora
  - Rollback simple
```

## Prácticas Clave

### 1. Versionado de APIs

```csharp
// ✅ BUENO: Versionado explícito de APIs

// Sales API v1 (actual)
[ApiController]
[Route("api/v1/orders")]
[ApiVersion("1.0")]
public class OrdersV1Controller : ControllerBase
{
    [HttpPost]
    public async Task<IActionResult> CreateOrder(CreateOrderV1Request request)
    {
        var order = Order.Create(request.CustomerId);
        foreach (var item in request.Items)
        {
            order.AddLine(item.ProductId, item.Quantity, item.UnitPrice);
        }
        await _orderRepo.SaveAsync(order);
        return CreatedAtAction(nameof(GetOrder), new { id = order.OrderId }, order.ToV1Dto());
    }
}

// Sales API v2 (nueva versión)
[ApiController]
[Route("api/v2/orders")]
[ApiVersion("2.0")]
public class OrdersV2Controller : ControllerBase
{
    [HttpPost]
    public async Task<IActionResult> CreateOrder(CreateOrderV2Request request)
    {
        // ✅ V2 agrega soporte para discounts
        var order = Order.Create(request.CustomerId);
        foreach (var item in request.Items)
        {
            order.AddLine(item.ProductId, item.Quantity, item.UnitPrice);
        }

        // ✅ Nueva funcionalidad en v2
        if (request.DiscountCode != null)
        {
            var discount = await _discountService.ApplyDiscountAsync(order, request.DiscountCode);
            order.ApplyDiscount(discount);
        }

        await _orderRepo.SaveAsync(order);
        return CreatedAtAction(nameof(GetOrder), new { id = order.OrderId }, order.ToV2Dto());
    }
}

// ✅ Resultado:
// - V1 endpoint sigue funcionando (Fulfillment usa v1)
// - V2 endpoint disponible para nuevos consumers
// - Sales puede desplegar v2 SIN esperar a que Fulfillment migre
// - Fulfillment migra a v2 cuando esté listo (meses después si quieren)

// ❌ MALO: Breaking change sin versionado

// ANTES:
public class CreateOrderRequest
{
    public Guid CustomerId { get; set; }
    public List<OrderItemDto> Items { get; set; }
}

// DESPUÉS (BREAKING CHANGE):
public class CreateOrderRequest
{
    public Guid CustomerId { get; set; }
    public List<OrderItemDto> Items { get; set; }
    public string DiscountCode { get; set; }  // ✅ Nuevo campo
    public int Points { get; set; }  // ❌ Required field ROMPE consumers
}

// Resultado:
// ❌ Fulfillment rompe porque Points no es enviado
// ❌ Requiere deployment coordinado de Sales y Fulfillment
```

### 2. Backward Compatibility

```csharp
// ✅ BUENO: Cambios backward compatible

// Step 1: Agregar campo OPCIONAL (no breaking)
public class CreateOrderRequest
{
    public Guid CustomerId { get; set; }
    public List<OrderItemDto> Items { get; set; }
    public string? DiscountCode { get; set; }  // ✅ Nullable (opcional)
}

// Step 2: Deploy Sales Service v2.1
// ✅ Acepta requests CON o SIN DiscountCode
// ✅ Consumers legacy (sin DiscountCode) siguen funcionando

// Step 3: Consumers migran a enviar DiscountCode (cuando quieran)
// ✅ Sin coordinación forzada

// Step 4 (meses después): Deprecar campo
[Obsolete("Use DiscountCode instead. Will be removed in v3.0")]
public int? LegacyPoints { get; set; }

// ✅ BUENO: Expand-Contract Pattern para renaming

// Fase 1 - Expand: Agregar nuevo campo, mantener viejo
public class Order
{
    [Obsolete("Use ShippingAddress")]
    public string Address { get; set; }  // ✅ Mantener viejo

    public string ShippingAddress { get; set; }  // ✅ Nuevo campo

    public Order()
    {
        // ✅ Sincronizar ambos campos durante transición
        PropertyChanged += (s, e) =>
        {
            if (e.PropertyName == nameof(ShippingAddress))
                Address = ShippingAddress;
            else if (e.PropertyName == nameof(Address))
                ShippingAddress = Address;
        };
    }
}

// Fase 2 - Migrate: Consumers migran a ShippingAddress (6 meses)

// Fase 3 - Contract: Eliminar campo viejo
public class Order
{
    public string ShippingAddress { get; set; }  // ✅ Solo nuevo campo
}
```

### 3. Database Migrations

```csharp
// ✅ BUENO: Migrations compatibles con versión anterior

// Step 1: Agregar columna NULLABLE (no breaking)
migrationBuilder.AddColumn<decimal>(
    name: "discount_amount",
    table: "orders",
    type: "decimal(18,2)",
    nullable: true);  // ✅ Nullable durante transición

// ✅ Deploy Sales v2.1 (usa discount_amount si existe, null OK)

// Step 2 (después): Poblar valores por defecto
migrationBuilder.Sql(@"
    UPDATE orders
    SET discount_amount = 0
    WHERE discount_amount IS NULL");

// Step 3 (días después): Hacer NOT NULL
migrationBuilder.AlterColumn<decimal>(
    name: "discount_amount",
    table: "orders",
    type: "decimal(18,2)",
    nullable: false,
    defaultValue: 0m);

// ❌ MALO: Migration breaking

// Step 1: Agregar columna NOT NULL (BREAKING!)
migrationBuilder.AddColumn<decimal>(
    name: "discount_amount",
    table: "orders",
    type: "decimal(18,2)",
    nullable: false);  // ❌ Rompe versión anterior del servicio!

// Problema:
// - Migration aplicada
// - Sales v2.0 (vieja) sigue corriendo
// - ❌ INSERT falla porque discount_amount es required
// - ❌ Requiere deployment atómico (migration + código nuevo)
```

### 4. Feature Flags

```csharp
// ✅ BUENO: Feature flags para despliegue gradual

public class OrderService
{
    private readonly IFeatureFlagService _featureFlags;

    public async Task<Order> CreateOrderAsync(CreateOrderRequest request)
    {
        var order = Order.Create(request.CustomerId);

        // ✅ Feature flag controla nueva funcionalidad
        if (await _featureFlags.IsEnabledAsync("DiscountEngine", request.CustomerId))
        {
            // Nueva lógica de discounts (solo para 10% de usuarios)
            var discount = await _discountEngine.CalculateAsync(order, request.DiscountCode);
            order.ApplyDiscount(discount);
        }
        else
        {
            // Lógica legacy (90% de usuarios)
            if (request.DiscountCode != null)
            {
                order.ApplyFixedDiscount(request.DiscountCode);
            }
        }

        await _orderRepo.SaveAsync(order);
        return order;
    }
}

// Beneficios:
// ✅ Deploy código nuevo SIN activarlo (flag off)
// ✅ Activar gradualmente (10% → 50% → 100%)
// ✅ Rollback instantáneo (flag off) sin redeploy
// ✅ A/B testing (comparar métricas)
// ✅ Kill switch si hay problema

// Configuración (AWS AppConfig):
{
  "DiscountEngine": {
    "enabled": true,
    "percentage": 10  // 10% de usuarios
  }
}
```

### 5. Blue-Green / Rolling Deployments

```yaml
# ✅ Rolling Deployment (zero downtime)

# ECS Service configuration
resource "aws_ecs_service" "sales" {
  name            = "sales-service"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.sales.arn
  desired_count   = 4  # 4 tasks running

  deployment_configuration {
    maximum_percent         = 200  # ✅ Permite 8 tasks durante deploy (4 old + 4 new)
    minimum_healthy_percent = 100  # ✅ Mínimo 4 tasks healthy siempre
  }

  deployment_circuit_breaker {
    enable   = true  # ✅ Rollback automático si falla health check
    rollback = true
  }

  health_check_grace_period_seconds = 60

  load_balancer {
    target_group_arn = aws_lb_target_group.sales.arn
    container_name   = "sales-api"
    container_port   = 8080
  }
}

# ALB Health Check
resource "aws_lb_target_group" "sales" {
  name     = "sales-tg"
  port     = 8080
  protocol = "HTTP"
  vpc_id   = aws_vpc.main.id

  health_check {
    path                = "/health"
    interval            = 30
    timeout             = 5
    healthy_threshold   = 2
    unhealthy_threshold = 2
    matcher             = "200"
  }

  deregistration_delay = 30  # Drain connections por 30s antes de terminar
}

# Deployment Flow:
1. Deploy starts: 4 old tasks running
2. Start 4 new tasks (v2.1)
3. Wait for health checks (60s grace period)
4. ✅ New tasks healthy → ALB routes traffic a new tasks
5. Drain old tasks (30s deregistration_delay)
6. Terminate old tasks
7. ✅ Result: 4 new tasks running, zero downtime

# ✅ Circuit Breaker: Si new tasks fallan health check
1. Deploy starts
2. New tasks unhealthy (health check fails)
3. ❌ Circuit breaker triggered
4. ✅ Rollback automático: mantener old tasks
5. ✅ Zero downtime (old tasks nunca terminaron)
```

### 6. Contract Testing

```csharp
// ✅ BUENO: Contract tests para validar compatibilidad

// Consumer (Fulfillment) define contrato esperado

[Fact]
public async Task Sales_API_Should_Return_Order_With_Required_Fields()
{
    // Arrange: Fulfillment espera estos campos
    var client = new HttpClient { BaseAddress = new Uri("https://sales-api.com") };

    // Act: Llamar Sales API v1
    var response = await client.GetAsync("/api/v1/orders/12345");
    var json = await response.Content.ReadAsStringAsync();
    var order = JsonSerializer.Deserialize<OrderDto>(json);

    // Assert: Contract validation
    Assert.NotNull(order);
    Assert.NotEqual(Guid.Empty, order.OrderId);  // ✅ Required
    Assert.NotEqual(Guid.Empty, order.CustomerId);  // ✅ Required
    Assert.NotEmpty(order.Lines);  // ✅ Required
    Assert.True(order.Total > 0);  // ✅ Required

    // ✅ Nuevo campo opcional no rompe contrato
    // Assert.NotNull(order.DiscountCode);  // ❌ NO requerirlo (es opcional)
}

// ✅ Provider (Sales) valida que cumple contratos

[Fact]
public async Task Sales_V1_API_Should_Fulfill_Fulfillment_Contract()
{
    // Arrange
    var order = await CreateTestOrderAsync();

    // Act
    var response = await _client.GetAsync($"/api/v1/orders/{order.OrderId}");
    var dto = await response.Content.ReadFromJsonAsync<OrderDto>();

    // Assert: Cumple contrato de Fulfillment
    Assert.NotNull(dto);
    Assert.Equal(order.OrderId, dto.OrderId);
    Assert.NotEmpty(dto.Lines);
    Assert.True(dto.Total > 0);

    // ✅ Si agregamos campo nuevo, NO rompe este test
}

// ✅ Si Sales cambia y rompe contrato, test falla ANTES de deploy
```

## Pipeline de CI/CD

```yaml
# ✅ GitHub Actions pipeline para independent deployment

name: Deploy Sales Service

on:
  push:
    branches: [main]
    paths:
      - "src/Sales/**" # ✅ Solo deploy si Sales cambió

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Run Unit Tests
        run: dotnet test src/Sales.Tests/

      - name: Run Contract Tests
        run: dotnet test src/Sales.ContractTests/
        # ✅ Valida compatibilidad con consumers

      - name: Run Integration Tests
        run: dotnet test src/Sales.IntegrationTests/

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - name: Build Docker Image
        run: |
          docker build -t sales-api:${{ github.sha }} .
          docker tag sales-api:${{ github.sha }} sales-api:latest

      - name: Push to GHCR
        run: |
          echo "${{ secrets.GITHUB_TOKEN }}" | docker login ghcr.io -u ${{ github.actor }} --password-stdin
          docker push ghcr.io/talma/sales-api:${{ github.sha }}
          docker push ghcr.io/talma/sales-api:latest

  deploy-staging:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to Staging ECS
        run: |
          aws ecs update-service \
            --cluster talma-staging \
            --service sales-service \
            --force-new-deployment \
            --task-definition sales-api:${{ github.sha }}

      - name: Wait for deployment
        run: aws ecs wait services-stable --cluster talma-staging --services sales-service

      - name: Run Smoke Tests
        run: |
          curl -f https://sales-api-staging.talma.com/health || exit 1
          dotnet test src/Sales.SmokeTests/ --filter "Environment=Staging"

  deploy-production:
    needs: deploy-staging
    runs-on: ubuntu-latest
    environment: production # ✅ Requiere approval manual (opcional)
    steps:
      - name: Apply DB Migrations
        run: |
          dotnet ef database update --connection "${{ secrets.SALES_DB_CONNECTION }}"
        # ✅ Migrations backward-compatible

      - name: Deploy to Production ECS
        run: |
          aws ecs update-service \
            --cluster talma-production \
            --service sales-service \
            --force-new-deployment \
            --task-definition sales-api:${{ github.sha }}

      - name: Wait for deployment
        run: aws ecs wait services-stable --cluster talma-production --services sales-service
        timeout-minutes: 10

      - name: Run Smoke Tests
        run: dotnet test src/Sales.SmokeTests/ --filter "Environment=Production"

      - name: Notify Slack
        run: |
          curl -X POST ${{ secrets.SLACK_WEBHOOK }} \
            -d '{"text":"Sales Service deployed to production: v${{ github.sha }}"}'

# ✅ Resultado:
# - Sales desplegado en 10-15 minutos
# - Fulfillment, Billing no afectados
# - Rollback automático si smoke tests fallan
# - Sin coordinación con otros equipos
```

---

## Requisitos Técnicos

### MUST (Obligatorio)

- **MUST** versionar APIs públicas (v1, v2, v3)
- **MUST** mantener backward compatibility al cambiar APIs
- **MUST** hacer DB migrations backward-compatible
- **MUST** implementar health checks en todos los servicios
- **MUST** usar rolling deployments (zero downtime)
- **MUST** implementar circuit breaker para rollback automático
- **MUST** ejecutar contract tests antes de deploy
- **MUST** mantener versión anterior de API funcionando mínimo 6 meses

### SHOULD (Fuertemente recomendado)

- **SHOULD** usar feature flags para funcionalidad nueva
- **SHOULD** implementar Blue-Green deployment para cambios críticos
- **SHOULD** ejecutar smoke tests automáticos post-deploy
- **SHOULD** usar Expand-Contract pattern para breaking changes
- **SHOULD** documentar deprecation timeline (6-12 meses)
- **SHOULD** monitorear métricas durante y después de deploy

### MAY (Opcional)

- **MAY** usar canary deployments (deploy gradual 5% → 50% → 100%)
- **MAY** implementar A/B testing con feature flags
- **MAY** requerir approval manual para deploy a producción
- **MAY** usar chaos engineering para validar resilience

### MUST NOT (Prohibido)

- **MUST NOT** hacer breaking changes sin versionado
- **MUST NOT** requerir deployment coordinado entre servicios
- **MUST NOT** aplicar DB migrations que rompen versión anterior
- **MUST NOT** desplegar sin health checks
- **MUST NOT** desplegar sin rollback plan
- **MUST NOT** eliminar endpoints deprecated sin avisar (mínimo 6 meses)

---

## Referencias

- [Lineamiento: Autonomía de Servicios](../../lineamientos/arquitectura/10-autonomia-de-servicios.md)
- Estándares relacionados:
  - [API Contracts](../apis/api-contracts.md)
  - [Database per Service](../datos/database-per-service.md)
  - [API Versioning](../apis/api-versioning.md)
- ADRs:
  - [ADR-009: GitHub Actions para CI/CD](../../decisiones-de-arquitectura/adr-009-github-actions-cicd.md)
  - [ADR-007: AWS ECS Fargate](../../decisiones-de-arquitectura/adr-007-aws-ecs-fargate-contenedores.md)
- Especificaciones:
  - [Continuous Delivery (Jez Humble)](https://continuousdelivery.com/)
  - [Accelerate (Nicole Forsgren)](https://www.amazon.com/Accelerate-Software-Performing-Technology-Organizations/dp/1942788339)
