---
id: unit-tests
sidebar_position: 1
title: Testing Unitario
description: Estándar para pruebas unitarias con xUnit, Jest, cobertura de código y mejores prácticas de testing aislado.
---

# Estándar Técnico — Testing Unitario

---

## 1. Propósito
Garantizar código confiable mediante tests unitarios con xUnit (C#) / Jest (TypeScript), cobertura >80%, patrón AAA (Arrange-Act-Assert), mocks con Moq/jest.mock() y ejecución <500ms.

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

| Componente | Tecnología | Versión mínima | Observaciones |
|-----------|------------|----------------|---------------|
| **Framework C#** | xUnit | 2.6+ | Testing .NET |
| **Mocking C#** | Moq / NSubstitute | 4.20+ / 5.1+ | Mocks/stubs |
| **Assertions C#** | FluentAssertions | 6.12+ | Expresividad |
| **Framework TS** | Jest / Vitest | 29+ / 1.0+ | Testing Node.js |
| **Mocking TS** | jest.mock() | - | Mocks nativos Jest |
| **Coverage** | Coverlet / NYC | 6.0+ / 15.0+ | Cobertura de código |

> El uso de tecnologías no listadas requiere aprobación de Arquitectura.

---

## 4. Requisitos Obligatorios 🔴

- [ ] xUnit (C#) / Jest (TypeScript) en todos los proyectos
- [ ] Patrón AAA (Arrange-Act-Assert) obligatorio
- [ ] Mocks con Moq/jest.mock() (NO dependencias reales)
- [ ] Tests aislados (NO compartir estado entre tests)
- [ ] Naming: `MethodName_Scenario_ExpectedResult`
- [ ] Ejecución <500ms para suite completa de unit tests
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

### TypeScript con Jest
```json
// package.json
{
  "devDependencies": {
    "jest": "^29.0.0",
    "@types/jest": "^29.0.0",
    "ts-jest": "^29.0.0"
  },
  "scripts": {
    "test": "jest",
    "test:coverage": "jest --coverage"
  }
}
```

```typescript
// orderService.test.ts
import { OrderService } from './orderService';
import { IOrderRepository } from './IOrderRepository';

describe('OrderService', () => {
  let orderRepository: jest.Mocked<IOrderRepository>;
  let sut: OrderService;

  beforeEach(() => {
    orderRepository = {
      getById: jest.fn(),
      create: jest.fn(),
    } as jest.Mocked<IOrderRepository>;
    
    sut = new OrderService(orderRepository);
  });

  it('getOrder_OrderExists_ReturnsOrder', async () => {
    // Arrange
    const orderId = '123';
    const expectedOrder = { orderId, status: 'PENDING' };
    orderRepository.getById.mockResolvedValue(expectedOrder);

    // Act
    const result = await sut.getOrder(orderId);

    // Assert
    expect(result).toEqual(expectedOrder);
    expect(orderRepository.getById).toHaveBeenCalledWith(orderId);
  });

  it.each([
    [''],
    [null],
    [undefined]
  ])('createOrder_InvalidUserId_ThrowsError', async (invalidUserId) => {
    // Arrange
    const request = { userId: invalidUserId };

    // Act & Assert
    await expect(sut.createOrder(request)).rejects.toThrow();
  });
});
```

---

## 7. Validación

```bash
# C# - Ejecutar tests
dotnet test

# C# - Coverage report
dotnet test /p:CollectCoverage=true /p:CoverletOutputFormat=opencover

# TypeScript - Ejecutar tests
npm test

# TypeScript - Coverage
npm run test:coverage

# Verificar coverage >80%
grep -A 5 "TOTAL" coverage/coverage-summary.json
```

**Métricas de cumplimiento:**

| Métrica | Target | Verificación |
|---------|--------|--------------|  
| Code coverage Services | >80% | Coverlet/NYC report |
| Tests ejecutados | 100% pass | CI/CD pipeline |
| Ejecución suite completa | <500ms | `dotnet test` output |
| Tests con patrón AAA | 100% | Code review |

Incumplimientos deben corregirse o documentarse mediante excepción aprobada.

---

## 8. Referencias

- [Integration Tests](02-integration-tests.md)
- [E2E Tests](03-e2e-tests.md)
- [xUnit Documentation](https://xunit.net/)
- [Jest Documentation](https://jestjs.io/)
- [Moq Quickstart](https://github.com/moq/moq4)
