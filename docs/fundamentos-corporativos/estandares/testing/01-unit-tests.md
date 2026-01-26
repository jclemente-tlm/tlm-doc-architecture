---
id: unit-tests
sidebar_position: 1
title: Testing Unitario
description: Estándar para pruebas unitarias con xUnit, Jest, cobertura de código y mejores prácticas de testing aislado.
---

# Estándar: Testing Unitario

## 1. Propósito

Establecer las mejores prácticas para **testing unitario** en Talma, asegurando código confiable, mantenible y con alta cobertura, validando unidades de código de forma aislada.

## 2. Alcance

- Pruebas de lógica de negocio (Services, Use Cases)
- Validación de funciones puras (Utilities, Helpers)
- Testing de componentes UI aislados (React, Angular)
- Cobertura de código y calidad
- Integración en CI/CD

## 3. Principios FIRST

- **Fast**: Tests deben ejecutarse en milisegundos
- **Isolated**: Cada test independiente, sin dependencias externas
- **Repeatable**: Mismos resultados en cada ejecución
- **Self-validating**: Pass/fail automático sin intervención manual
- **Timely**: Escribir tests junto con el código (TDD recomendado)

## 4. Patrón AAA (Arrange-Act-Assert)

Todos los tests unitarios deben seguir la estructura AAA:

```csharp
[Fact]
public async Task GetUserAsync_UserExists_ReturnsUser()
{
    // Arrange: Preparar datos y mocks
    var userId = 123;
    var expectedUser = new User { Id = userId, Name = "Juan" };
    _mockRepository.Setup(r => r.GetUserAsync(userId))
        .ReturnsAsync(expectedUser);

    // Act: Ejecutar el método bajo prueba
    var result = await _sut.GetUserAsync(userId);

    // Assert: Verificar resultado esperado
    Assert.NotNull(result);
    Assert.Equal(expectedUser.Id, result.Id);
    Assert.Equal(expectedUser.Name, result.Name);
}
```

## 5. C# con xUnit y Moq

### 5.1 Configuración

**Packages requeridos**:

```xml
<ItemGroup>
  <PackageReference Include="xunit" Version="2.6.*" />
  <PackageReference Include="xunit.runner.visualstudio" Version="2.5.*" />
  <PackageReference Include="Moq" Version="4.20.*" />
  <PackageReference Include="FluentAssertions" Version="6.12.*" />
  <PackageReference Include="coverlet.collector" Version="6.0.*" />
</ItemGroup>
```

### 5.2 Estructura de Test Class

```csharp
public class UserServiceTests
{
    private readonly Mock<IUserRepository> _mockRepository;
    private readonly Mock<IValidator<CreateUserRequest>> _mockValidator;
    private readonly Mock<ILogger<UserService>> _mockLogger;
    private readonly UserService _sut; // System Under Test

    public UserServiceTests()
    {
        // Arrange global: Crear mocks
        _mockRepository = new Mock<IUserRepository>();
        _mockValidator = new Mock<IValidator<CreateUserRequest>>();
        _mockLogger = new Mock<ILogger<UserService>>();

        // Crear SUT con dependencias mockeadas
        _sut = new UserService(
            _mockRepository.Object,
            _mockValidator.Object,
            _mockLogger.Object
        );
    }

    [Fact]
    public async Task GetUserAsync_UserExists_ReturnsUser()
    {
        // Ver ejemplo AAA arriba
    }

    [Fact]
    public async Task GetUserAsync_UserNotFound_ReturnsNull()
    {
        // Arrange
        var userId = 999;
        _mockRepository
            .Setup(r => r.GetUserAsync(userId))
            .ReturnsAsync((User?)null);

        // Act
        var result = await _sut.GetUserAsync(userId);

        // Assert
        Assert.Null(result);
    }

    [Theory]
    [InlineData("")]
    [InlineData(null)]
    [InlineData("   ")]
    public async Task CreateUserAsync_InvalidName_ThrowsValidationException(string invalidName)
    {
        // Arrange
        var request = new CreateUserRequest { Name = invalidName, Email = "test@talma.com" };
        var validationResult = new ValidationResult(new[]
        {
            new ValidationFailure("Name", "Name is required")
        });

        _mockValidator
            .Setup(v => v.ValidateAsync(request, default))
            .ReturnsAsync(validationResult);

        // Act & Assert
        await Assert.ThrowsAsync<ValidationException>(
            () => _sut.CreateUserAsync(request)
        );
    }

    [Fact]
    public async Task CreateUserAsync_ValidRequest_CallsRepository()
    {
        // Arrange
        var request = new CreateUserRequest { Name = "Juan", Email = "juan@talma.com" };
        var validationResult = new ValidationResult(); // Empty = valid

        _mockValidator
            .Setup(v => v.ValidateAsync(request, default))
            .ReturnsAsync(validationResult);

        _mockRepository
            .Setup(r => r.AddAsync(It.IsAny<User>()))
            .ReturnsAsync(new User { Id = 1, Name = "Juan" });

        // Act
        await _sut.CreateUserAsync(request);

        // Assert
        _mockRepository.Verify(
            r => r.AddAsync(It.Is<User>(u => u.Name == "Juan")),
            Times.Once
        );
    }
}
```

### 5.3 FluentAssertions (Recomendado)

```csharp
using FluentAssertions;

[Fact]
public async Task GetUserAsync_UserExists_ReturnsUserWithCorrectData()
{
    // Arrange
    var expectedUser = new User
    {
        Id = 123,
        Name = "Juan Perez",
        Email = "juan@talma.com",
        IsActive = true
    };

    _mockRepository
        .Setup(r => r.GetUserAsync(123))
        .ReturnsAsync(expectedUser);

    // Act
    var result = await _sut.GetUserAsync(123);

    // Assert
    result.Should().NotBeNull();
    result.Should().BeEquivalentTo(expectedUser);
    result.Id.Should().Be(123);
    result.Name.Should().Be("Juan Perez");
    result.IsActive.Should().BeTrue();
}

[Fact]
public async Task GetAllUsersAsync_ReturnsMultipleUsers()
{
    // Arrange
    var users = new List<User>
    {
        new User { Id = 1, Name = "User 1" },
        new User { Id = 2, Name = "User 2" },
        new User { Id = 3, Name = "User 3" }
    };

    _mockRepository.Setup(r => r.GetAllAsync()).ReturnsAsync(users);

    // Act
    var result = await _sut.GetAllUsersAsync();

    // Assert
    result.Should().HaveCount(3);
    result.Should().Contain(u => u.Id == 1);
    result.Should().AllSatisfy(u => u.Name.Should().StartWith("User"));
}
```

## 6. TypeScript con Jest

### 6.1 Configuración

**jest.config.js**:

```javascript
module.exports = {
  preset: "ts-jest",
  testEnvironment: "node",
  roots: ["<rootDir>/src", "<rootDir>/tests"],
  testMatch: ["**/*.test.ts", "**/*.spec.ts"],
  collectCoverage: true,
  collectCoverageFrom: [
    "src/**/*.ts",
    "!src/**/*.test.ts",
    "!src/**/*.spec.ts",
    "!src/**/index.ts",
    "!src/**/*.d.ts",
  ],
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80,
    },
  },
  coverageReporters: ["text", "lcov", "html"],
};
```

**package.json**:

```json
{
  "scripts": {
    "test": "jest",
    "test:watch": "jest --watch",
    "test:coverage": "jest --coverage"
  },
  "devDependencies": {
    "@types/jest": "^29.5.0",
    "jest": "^29.7.0",
    "ts-jest": "^29.1.0"
  }
}
```

### 6.2 Ejemplo Completo

```typescript
import { UserService } from "../services/UserService";
import { UserRepository } from "../repositories/UserRepository";
import { User, CreateUserRequest } from "../types";

// Mock del repository
jest.mock("../repositories/UserRepository");

describe("UserService", () => {
  let userService: UserService;
  let mockRepository: jest.Mocked<UserRepository>;

  beforeEach(() => {
    // Arrange global: Crear mocks
    mockRepository = new UserRepository() as jest.Mocked<UserRepository>;
    userService = new UserService(mockRepository);

    // Resetear mocks entre tests
    jest.clearAllMocks();
  });

  describe("getUser", () => {
    it("should return user when user exists", async () => {
      // Arrange
      const userId = 123;
      const expectedUser: User = {
        id: userId,
        name: "Juan",
        email: "juan@talma.com",
        isActive: true,
      };

      mockRepository.getUser.mockResolvedValue(expectedUser);

      // Act
      const result = await userService.getUser(userId);

      // Assert
      expect(result).toEqual(expectedUser);
      expect(mockRepository.getUser).toHaveBeenCalledWith(userId);
      expect(mockRepository.getUser).toHaveBeenCalledTimes(1);
    });

    it("should return null when user not found", async () => {
      // Arrange
      const userId = 999;
      mockRepository.getUser.mockResolvedValue(null);

      // Act
      const result = await userService.getUser(userId);

      // Assert
      expect(result).toBeNull();
    });

    it("should throw error when repository fails", async () => {
      // Arrange
      const userId = 123;
      const error = new Error("Database connection failed");
      mockRepository.getUser.mockRejectedValue(error);

      // Act & Assert
      await expect(userService.getUser(userId)).rejects.toThrow(
        "Database connection failed",
      );
    });
  });

  describe("createUser", () => {
    it.each([
      ["empty string", ""],
      ["null", null],
      ["undefined", undefined],
      ["whitespace", "   "],
    ])("should throw error when name is %s", async (_, invalidName) => {
      // Arrange
      const request: CreateUserRequest = {
        name: invalidName as string,
        email: "test@talma.com",
      };

      // Act & Assert
      await expect(userService.createUser(request)).rejects.toThrow(
        "Invalid name",
      );
    });

    it("should create user with valid data", async () => {
      // Arrange
      const request: CreateUserRequest = {
        name: "Juan Perez",
        email: "juan@talma.com",
      };

      const createdUser: User = {
        id: 1,
        ...request,
        isActive: true,
      };

      mockRepository.create.mockResolvedValue(createdUser);

      // Act
      const result = await userService.createUser(request);

      // Assert
      expect(result).toEqual(createdUser);
      expect(mockRepository.create).toHaveBeenCalledWith(
        expect.objectContaining({
          name: "Juan Perez",
          email: "juan@talma.com",
        }),
      );
    });
  });
});
```

### 6.3 Mocking Avanzado

```typescript
describe("UserService Advanced Mocking", () => {
  it("should mock different return values on consecutive calls", async () => {
    mockRepository.getUser
      .mockResolvedValueOnce({ id: 1, name: "User 1" })
      .mockResolvedValueOnce({ id: 2, name: "User 2" })
      .mockResolvedValueOnce(null);

    const user1 = await userService.getUser(1);
    const user2 = await userService.getUser(2);
    const user3 = await userService.getUser(3);

    expect(user1?.name).toBe("User 1");
    expect(user2?.name).toBe("User 2");
    expect(user3).toBeNull();
  });

  it("should use mock implementation", async () => {
    mockRepository.getUser.mockImplementation(async (id: number) => {
      if (id < 100) {
        return { id, name: `User ${id}`, email: `user${id}@talma.com` };
      }
      return null;
    });

    const user50 = await userService.getUser(50);
    const user150 = await userService.getUser(150);

    expect(user50).not.toBeNull();
    expect(user50?.name).toBe("User 50");
    expect(user150).toBeNull();
  });

  it("should verify call arguments with matchers", async () => {
    await userService.updateUser(123, { name: "New Name" });

    expect(mockRepository.update).toHaveBeenCalledWith(
      123,
      expect.objectContaining({
        name: expect.stringMatching(/^New/),
      }),
    );
  });
});
```

## 7. Test Data Builders

### 7.1 C# Builder Pattern

```csharp
public class UserBuilder
{
    private int _id = 1;
    private string _name = "Default User";
    private string _email = "default@talma.com";
    private bool _isActive = true;
    private DateTime _createdAt = DateTime.UtcNow;

    public UserBuilder WithId(int id)
    {
        _id = id;
        return this;
    }

    public UserBuilder WithName(string name)
    {
        _name = name;
        return this;
    }

    public UserBuilder WithEmail(string email)
    {
        _email = email;
        return this;
    }

    public UserBuilder Inactive()
    {
        _isActive = false;
        return this;
    }

    public UserBuilder CreatedAt(DateTime date)
    {
        _createdAt = date;
        return this;
    }

    public User Build()
    {
        return new User
        {
            Id = _id,
            Name = _name,
            Email = _email,
            IsActive = _isActive,
            CreatedAt = _createdAt
        };
    }
}

// Uso en tests
[Fact]
public async Task GetActiveUsers_ReturnsOnlyActiveUsers()
{
    // Arrange
    var activeUser = new UserBuilder()
        .WithId(1)
        .WithName("Active User")
        .Build();

    var inactiveUser = new UserBuilder()
        .WithId(2)
        .WithName("Inactive User")
        .Inactive()
        .Build();

    var users = new List<User> { activeUser, inactiveUser };
    _mockRepository.Setup(r => r.GetAllAsync()).ReturnsAsync(users);

    // Act
    var result = await _sut.GetActiveUsersAsync();

    // Assert
    result.Should().HaveCount(1);
    result.First().Id.Should().Be(1);
}
```

### 7.2 TypeScript Factory Functions

```typescript
// factories/user.factory.ts
export const createUser = (overrides: Partial<User> = {}): User => ({
  id: 1,
  name: "Default User",
  email: "default@talma.com",
  isActive: true,
  createdAt: new Date(),
  ...overrides,
});

export const createUsers = (count: number): User[] =>
  Array.from({ length: count }, (_, i) =>
    createUser({
      id: i + 1,
      name: `User ${i + 1}`,
      email: `user${i + 1}@talma.com`,
    }),
  );

// Uso en tests
import { createUser, createUsers } from "../factories/user.factory";

describe("UserService with Factories", () => {
  it("should filter active users", async () => {
    // Arrange
    const activeUser = createUser({ id: 1, isActive: true });
    const inactiveUser = createUser({ id: 2, isActive: false });

    mockRepository.getAll.mockResolvedValue([activeUser, inactiveUser]);

    // Act
    const result = await userService.getActiveUsers();

    // Assert
    expect(result).toHaveLength(1);
    expect(result[0].id).toBe(1);
  });

  it("should handle large list of users", async () => {
    // Arrange
    const users = createUsers(100); // 100 usuarios de prueba
    mockRepository.getAll.mockResolvedValue(users);

    // Act
    const result = await userService.getAll();

    // Assert
    expect(result).toHaveLength(100);
  });
});
```

## 8. Cobertura de Código

### 8.1 Configuración C# (coverlet)

**Directory.Build.props**:

```xml
<Project>
  <PropertyGroup>
    <CollectCoverage>true</CollectCoverage>
    <CoverletOutputFormat>opencover,lcov,cobertura</CoverletOutputFormat>
    <CoverletOutput>./coverage/</CoverletOutput>
    <Threshold>80</Threshold>
    <ThresholdType>line,branch</ThresholdType>
    <ThresholdStat>total</ThresholdStat>
    <ExcludeByFile>**/Migrations/**/*.cs</ExcludeByFile>
  </PropertyGroup>
</Project>
```

**Comandos**:

```bash
# Ejecutar tests con coverage
dotnet test /p:CollectCoverage=true

# Generar reporte HTML
dotnet tool install -g dotnet-reportgenerator-globaltool
reportgenerator \
  -reports:"**/coverage.opencover.xml" \
  -targetdir:"coverage/report" \
  -reporttypes:Html

# Abrir reporte
open coverage/report/index.html
```

### 8.2 Configuración TypeScript (Jest)

Ver sección 6.1 para configuración de coverageThreshold.

```bash
# Ejecutar con coverage
npm test -- --coverage

# Coverage en modo watch
npm test -- --coverage --watch

# Generar solo HTML report
npm test -- --coverage --coverageReporters=html

# Abrir reporte
open coverage/index.html
```

### 8.3 Excluir Archivos

```javascript
// jest.config.js
collectCoverageFrom: [
  'src/**/*.ts',
  '!src/**/*.test.ts',        // Excluir tests
  '!src/**/*.spec.ts',
  '!src/**/index.ts',         // Excluir barrels
  '!src/migrations/**',       // Excluir migraciones
  '!src/**/*.d.ts',           // Excluir type definitions
  '!src/main.ts',             // Excluir entry point
],
```

## 9. Organización de Tests

```
tests/
├── unit/
│   ├── services/
│   │   ├── UserService.test.ts
│   │   ├── AuthService.test.ts
│   │   └── OrderService.test.ts
│   ├── utils/
│   │   ├── validators.test.ts
│   │   ├── formatters.test.ts
│   │   └── helpers.test.ts
│   └── domain/
│       ├── User.test.ts
│       └── Order.test.ts
├── factories/
│   ├── user.factory.ts
│   ├── order.factory.ts
│   └── index.ts
└── fixtures/
    ├── users.json
    └── orders.json
```

## 10. Mejores Prácticas

### 10.1 Naming Conventions

```csharp
// ✅ BIEN: Descriptivo y claro
[Fact]
public async Task GetUserAsync_UserExists_ReturnsUser()

[Fact]
public async Task GetUserAsync_UserNotFound_ReturnsNull()

[Fact]
public async Task CreateUserAsync_InvalidEmail_ThrowsValidationException()

// ❌ MAL: No descriptivo
[Fact]
public async Task Test1()

[Fact]
public async Task UserTest()

[Fact]
public async Task It_Works()
```

### 10.2 Un Concepto por Test

```csharp
// ✅ BIEN: Un test, un assertion lógico
[Fact]
public async Task CreateUserAsync_ValidData_ReturnsCreatedUser()
{
    var result = await _sut.CreateUserAsync(validRequest);
    result.Should().NotBeNull();
    result.Id.Should().BeGreaterThan(0);
}

[Fact]
public async Task CreateUserAsync_ValidData_CallsRepository()
{
    await _sut.CreateUserAsync(validRequest);
    _mockRepository.Verify(r => r.AddAsync(It.IsAny<User>()), Times.Once);
}

// ❌ MAL: Múltiples conceptos no relacionados
[Fact]
public async Task CreateUser_Works()
{
    var result = await _sut.CreateUserAsync(validRequest);
    result.Should().NotBeNull(); // Assertion 1
    _mockRepository.Verify(...); // Assertion 2 (diferente concepto)
    _mockLogger.Verify(...);     // Assertion 3 (diferente concepto)
}
```

### 10.3 Tests Deterministicos

```typescript
// ✅ BIEN: Inyectar tiempo, no usar Date.now()
class UserService {
  constructor(
    private repository: UserRepository,
    private dateProvider: DateProvider = new DateProvider()
  ) {}

  async createUser(request: CreateUserRequest): Promise<User> {
    return this.repository.create({
      ...request,
      createdAt: this.dateProvider.now(), // Inyectable
    });
  }
}

// Test
it('should set createdAt to current date', async () => {
  const fixedDate = new Date('2026-01-26T10:00:00Z');
  const mockDateProvider = { now: () => fixedDate };
  const service = new UserService(mockRepository, mockDateProvider);

  const result = await service.createUser(request);

  expect(result.createdAt).toEqual(fixedDate);
});

// ❌ MAL: No determinístico
async createUser(request: CreateUserRequest): Promise<User> {
  return this.repository.create({
    ...request,
    createdAt: new Date(), // No testable
  });
}
```

## 11. Antipatrones

❌ **Tests interdependientes**: Cada test debe ejecutarse independientemente
❌ **Sleeps/Timeouts**: `await Task.Delay(1000)` hace tests lentos y frágiles
❌ **Estado global**: Modificar singletons o variables estáticas
❌ **Tests sin assertions**: Solo verificar que no hay excepciones
❌ **Tests frágiles**: Depender de orden de ejecución
❌ **Over-mocking**: Mockear todo, incluso clases simples (DTOs, models)
❌ **Tests que prueban mocks**: Verificar comportamiento del mock, no del SUT

## 12. Integración con CI/CD

### 12.1 GitHub Actions

```yaml
name: Unit Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Setup .NET
        uses: actions/setup-dotnet@v4
        with:
          dotnet-version: "8.0.x"

      - name: Restore dependencies
        run: dotnet restore

      - name: Build
        run: dotnet build --no-restore

      - name: Test with coverage
        run: dotnet test --no-build --verbosity normal /p:CollectCoverage=true

      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          files: "**/coverage.opencover.xml"
```

### 12.2 GitLab CI

```yaml
test:
  stage: test
  script:
    - dotnet restore
    - dotnet test /p:CollectCoverage=true /p:CoverletOutputFormat=cobertura
  coverage: '/Total\s+\|\s+(\d+\.?\d*)%/'
  artifacts:
    reports:
      coverage_report:
        coverage_format: cobertura
        path: "**/coverage.cobertura.xml"
```

## 13. Referencias

### Documentación Oficial

- [xUnit Documentation](https://xunit.net/)
- [Moq Documentation](https://github.com/moq/moq4)
- [Jest Documentation](https://jestjs.io/)
- [FluentAssertions](https://fluentassertions.com/)

### Lineamientos Relacionados

- [Lineamiento Dev. 03: Testing](../../lineamientos/desarrollo/03-testing.md)
- [Lineamiento Arq. 07: Calidad y Testing](../../lineamientos/arquitectura/07-calidad-testing.md)

### Otros Estándares

- [Integration Tests](./02-integration-tests.md) - Testing con dependencias reales
- [E2E Tests](./03-e2e-tests.md) - Testing end-to-end con Playwright
- [C# / .NET](../codigo/01-csharp-dotnet.md) - Clean Code y mejores prácticas
