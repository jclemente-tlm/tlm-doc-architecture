---
id: unit-integration-tests
sidebar_position: 1
title: Testing Unitario e Integración
description: Estándares para pruebas unitarias, de integración y cobertura de código
---

## 1. Principios de Testing

- **AAA Pattern**: Arrange, Act, Assert en cada test.
- **Tests independientes**: Cada test debe poder ejecutarse de forma aislada.
- **Nombres descriptivos**: El nombre del test debe describir qué se prueba y el resultado esperado.
- **Un assertion por concepto**: Evitar múltiples asserts no relacionados en un mismo test.
- **Fast, Isolated, Repeatable, Self-validating, Timely (FIRST)**.

## 2. Testing Unitario

### Estándares generales

- **Cobertura mínima**: 80% de cobertura de código.
- **Mocking**: Usar mocks para dependencias externas (bases de datos, APIs, servicios).
- **Tests deterministicos**: Evitar dependencias en tiempo actual, valores aleatorios, etc.

### C# con xUnit

```csharp
public class UserServiceTests
{
    private readonly Mock<IUserRepository> _mockRepository;
    private readonly UserService _sut; // System Under Test

    public UserServiceTests()
    {
        _mockRepository = new Mock<IUserRepository>();
        _sut = new UserService(_mockRepository.Object);
    }

    [Fact]
    public async Task GetUserAsync_UserExists_ReturnsUser()
    {
        // Arrange
        var userId = 123;
        var expectedUser = new User { Id = userId, Name = "Juan" };
        _mockRepository
            .Setup(r => r.GetUserAsync(userId))
            .ReturnsAsync(expectedUser);

        // Act
        var result = await _sut.GetUserAsync(userId);

        // Assert
        Assert.NotNull(result);
        Assert.Equal(expectedUser.Id, result.Id);
        Assert.Equal(expectedUser.Name, result.Name);
    }

    [Fact]
    public async Task GetUserAsync_UserNotFound_ReturnsNull()
    {
        // Arrange
        var userId = 999;
        _mockRepository
            .Setup(r => r.GetUserAsync(userId))
            .ReturnsAsync((User)null);

        // Act
        var result = await _sut.GetUserAsync(userId);

        // Assert
        Assert.Null(result);
    }

    [Theory]
    [InlineData("")]
    [InlineData(null)]
    [InlineData("   ")]
    public async Task CreateUserAsync_InvalidName_ThrowsException(string invalidName)
    {
        // Arrange
        var user = new CreateUserRequest { Name = invalidName };

        // Act & Assert
        await Assert.ThrowsAsync<ValidationException>(
            () => _sut.CreateUserAsync(user));
    }
}
```

### TypeScript con Jest

```typescript
describe("UserService", () => {
  let userService: UserService;
  let mockRepository: jest.Mocked<UserRepository>;

  beforeEach(() => {
    mockRepository = {
      getUser: jest.fn(),
      createUser: jest.fn(),
    } as any;

    userService = new UserService(mockRepository);
  });

  describe("getUser", () => {
    it("should return user when user exists", async () => {
      // Arrange
      const userId = 123;
      const expectedUser = { id: userId, name: "Juan" };
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
  });

  describe("createUser", () => {
    it.each([[""], [null], [undefined], ["   "]])(
      'should throw error when name is "%s"',
      async (invalidName) => {
        // Arrange
        const user = { name: invalidName };

        // Act & Assert
        await expect(userService.createUser(user)).rejects.toThrow(
          "Invalid name",
        );
      },
    );
  });
});
```

## 3. Testing de Integración

### Principios

- Probar interacciones entre componentes reales.
- Usar bases de datos de test (in-memory o contenedores).
- Limpiar estado entre tests.

### C# con WebApplicationFactory

```csharp
public class UsersControllerIntegrationTests : IClassFixture<WebApplicationFactory<Program>>
{
    private readonly WebApplicationFactory<Program> _factory;
    private readonly HttpClient _client;

    public UsersControllerIntegrationTests(WebApplicationFactory<Program> factory)
    {
        _factory = factory.WithWebHostBuilder(builder =>
        {
            builder.ConfigureServices(services =>
            {
                // Usar base de datos en memoria
                services.AddDbContext<AppDbContext>(options =>
                    options.UseInMemoryDatabase("TestDb"));
            });
        });

        _client = _factory.CreateClient();
    }

    [Fact]
    public async Task GetUsers_ReturnsSuccessAndUsers()
    {
        // Act
        var response = await _client.GetAsync("/api/v1/users");

        // Assert
        response.EnsureSuccessStatusCode();
        var content = await response.Content.ReadAsStringAsync();
        var result = JsonSerializer.Deserialize<ApiResponse<List<UserDto>>>(content);

        Assert.NotNull(result);
        Assert.Equal("success", result.Status);
        Assert.NotNull(result.Data);
    }

    [Fact]
    public async Task CreateUser_ValidData_ReturnsCreated()
    {
        // Arrange
        var newUser = new CreateUserRequest
        {
            Name = "Test User",
            Email = "test@talma.pe"
        };

        // Act
        var response = await _client.PostAsJsonAsync("/api/v1/users", newUser);

        // Assert
        Assert.Equal(HttpStatusCode.Created, response.StatusCode);
        var location = response.Headers.Location;
        Assert.NotNull(location);
    }
}
```

## 4. Configuración de Coverage

### C# - coverlet

```xml
<!-- Directory.Build.props -->
<Project>
  <PropertyGroup>
    <CollectCoverage>true</CollectCoverage>
    <CoverletOutputFormat>opencover,lcov,cobertura</CoverletOutputFormat>
    <CoverletOutput>./coverage/</CoverletOutput>
    <Threshold>80</Threshold>
    <ThresholdType>line,branch</ThresholdType>
    <ThresholdStat>total</ThresholdStat>
  </PropertyGroup>
</Project>
```

```bash
# Ejecutar tests con coverage
dotnet test /p:CollectCoverage=true

# Generar reporte HTML
reportgenerator -reports:"coverage/coverage.opencover.xml" -targetdir:"coverage/report"
```

### TypeScript - Jest

```javascript
// jest.config.js
module.exports = {
  preset: "ts-jest",
  testEnvironment: "node",
  collectCoverage: true,
  collectCoverageFrom: [
    "src/**/*.ts",
    "!src/**/*.spec.ts",
    "!src/**/*.test.ts",
    "!src/**/index.ts",
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

## 5. Buenas Prácticas

### Organización de tests

```
tests/
├── unit/
│   ├── services/
│   │   └── UserService.test.ts
│   └── utils/
│       └── validators.test.ts
├── integration/
│   └── api/
│       └── UsersController.test.cs
└── fixtures/
    └── users.json
```

### Test Data Builders

```csharp
public class UserBuilder
{
    private int _id = 1;
    private string _name = "Default Name";
    private string _email = "default@talma.pe";
    private bool _active = true;

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

    public UserBuilder Inactive()
    {
        _active = false;
        return this;
    }

    public User Build()
    {
        return new User
        {
            Id = _id,
            Name = _name,
            Email = _email,
            Active = _active
        };
    }
}

// Uso
var user = new UserBuilder()
    .WithId(123)
    .WithName("Juan")
    .Inactive()
    .Build();
```

## 6. Antipatrones a Evitar

- ❌ Tests que dependen del orden de ejecución.
- ❌ Tests con sleeps o timeouts arbitrarios.
- ❌ Tests que modifican estado global.
- ❌ Tests sin assertions (solo verifican que no hay excepciones).
- ❌ Tests que prueban implementación en lugar de comportamiento.

## 📖 Referencias

### Lineamientos relacionados

- [Testing y Calidad](/docs/fundamentos-corporativos/lineamientos/operabilidad/testing-y-calidad)

### Recursos externos

- [xUnit Documentation](https://xunit.net/)
- [Moq Documentation](https://github.com/moq/moq4)
- [Jest Documentation](https://jestjs.io/)
- [Test Driven Development](https://martinfowler.com/bliki/TestDrivenDevelopment.html)
