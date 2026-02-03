---
id: unit-tests
sidebar_position: 1
title: Testing Unitario
description: Estándar para pruebas unitarias con xUnit, Moq, cobertura de código y mejores prácticas de testing aislado.
---

# Estándar Técnico — Testing Unitario

---

## 1. Propósito

Garantizar código confiable mediante tests unitarios con xUnit + Moq + FluentAssertions, cobertura >80%, patrón AAA (Arrange-Act-Assert) y ejecución `<500ms`.

---

## 2. Alcance

**Aplica a:**

- Lógica de negocio (Services, Use Cases)
- Funciones puras (Utilities, Helpers)
- Validadores, Mappers, Builders
- Componentes UI aislados (React, Angular)

**No aplica a:**

- Integración con BD real (usar integration tests)
- Tests E2E con navegador
- Configuración de infraestructura

---

## 3. Tecnologías Aprobadas

| Componente     | Tecnología       | Versión mínima | Observaciones       |
| -------------- | ---------------- | -------------- | ------------------- |
| **Framework**  | xUnit            | 2.6+           | Testing .NET        |
| **Mocking**    | Moq              | 4.20+          | Mocks/stubs         |
| **Assertions** | FluentAssertions | 6.12+          | Expresividad        |
| **Coverage**   | Coverlet         | 6.0+           | Cobertura de código |
| **Análisis**   | SonarQube        | 10.0+          | Calidad y cobertura |

> El uso de tecnologías no listadas requiere aprobación de Arquitectura.

---

## 4. Requisitos Obligatorios 🔴

- [ ] xUnit 2.6+ en todos los proyectos
- [ ] Patrón AAA (Arrange-Act-Assert) obligatorio
- [ ] Mocks con Moq 4.20+ (NO dependencias reales)
- [ ] Tests aislados (NO compartir estado entre tests)
- [ ] Naming: `MethodName_Scenario_ExpectedResult`
- [ ] Ejecución `<500ms` para suite completa de unit tests
- [ ] Code coverage >80% en Services/Repositories
- [ ] Integración en CI/CD (tests fallan → build falla)
- [ ] `[Theory]` para casos múltiples (evitar duplicación)
- [ ] FluentAssertions (C#) para legibilidad
- [ ] NO `Thread.Sleep()` (usar mocks para tiempo)
- [ ] SUT (System Under Test) claramente identificado

---

## 5. Prohibiciones

- ❌ Dependencias reales (BD, HTTP, filesystem)
- ❌ Tests interdependientes (cada test aislado)
- ❌ `Thread.Sleep()` o delays arbitrarios
- ❌ Lógica condicional en tests (evitar if/else)
- ❌ Tests sin asserts (no-op tests)
- ❌ Nombres genéricos (`Test1`, `TestMethod`)
- ❌ Multiple assertions no relacionadas (un concepto por test)

---

## 6. Configuración Mínima

### C# con xUnit y Moq

```xml
<!-- Tests.csproj -->
<ItemGroup>
  <PackageReference Include="xunit" Version="2.6.*" />
  <PackageReference Include="xunit.runner.visualstudio" Version="2.5.*" />
  <PackageReference Include="Moq" Version="4.20.*" />
  <PackageReference Include="FluentAssertions" Version="6.12.*" />
  <PackageReference Include="coverlet.collector" Version="6.0.*" />
</ItemGroup>
```

```csharp
public class OrderServiceTests
{
    private readonly Mock<IOrderRepository> _mockRepository;
    private readonly OrderService _sut; // System Under Test

    public OrderServiceTests()
    {
        _mockRepository = new Mock<IOrderRepository>();
        _sut = new OrderService(_mockRepository.Object);
    }

    [Fact]
    public async Task GetOrderAsync_OrderExists_ReturnsOrder()
    {
        // Arrange
        var orderId = Guid.NewGuid();
        var expectedOrder = new Order { OrderId = orderId };
        _mockRepository
            .Setup(r => r.GetByIdAsync(orderId, default))
            .ReturnsAsync(expectedOrder);

        // Act
        var result = await _sut.GetOrderAsync(orderId, default);

        // Assert
        result.Should().NotBeNull();
        result.OrderId.Should().Be(orderId);
    }

    [Theory]
    [InlineData("")]
    [InlineData(null)]
    public async Task CreateOrderAsync_InvalidUserId_ThrowsArgumentException(string invalidUserId)
    {
        // Arrange
        var request = new CreateOrderRequest { UserId = invalidUserId };

        // Act & Assert
        await Assert.ThrowsAsync<ArgumentException>(
            () => _sut.CreateOrderAsync(request, default));
    }
}
```

---

## 7. Validación

```bash
# Ejecutar tests
dotnet test

# Coverage report
dotnet test /p:CollectCoverage=true /p:CoverletOutputFormat=opencover

# Verificar coverage >80%
grep -A 5 "TOTAL" coverage/coverage-summary.json
```

**Métricas de cumplimiento:**

| Métrica                  | Target    | Verificación         |
| ------------------------ | --------- | -------------------- |
| Code coverage Services   | >80%      | Coverlet report      |
| Tests ejecutados         | 100% pass | CI/CD pipeline       |
| Ejecución suite completa | `<500ms`  | `dotnet test` output |
| Tests con patrón AAA     | 100%      | Code review          |

Incumplimientos deben corregirse o documentarse mediante excepción aprobada.

---

## 8. Referencias

- [Integration Tests](02-integration-tests.md)
- [xUnit Documentation](https://xunit.net/)
- [Moq Quickstart](https://github.com/moq/moq4)
- [FluentAssertions](https://fluentassertions.com/)
