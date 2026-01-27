---
id: integration-tests
sidebar_position: 2
title: Testing de Integración
description: Estándar para pruebas de integración con TestContainers, WebApplicationFactory, bases de datos reales y servicios externos.
---

# Estándar: Testing de Integración

## 1. Propósito

Establecer las mejores prácticas para **testing de integración** en Talma, validando la interacción entre componentes reales (APIs, bases de datos, servicios externos) sin mockear dependencias externas.

## 2. Alcance

- Tests de APIs (Controllers + Services + Repository + DB)
- Integración con bases de datos reales (PostgreSQL, SQL Server)
- Integración con servicios externos (Redis, RabbitMQ, S3)
- Tests de infraestructura (Docker, Kubernetes)
- Tests en CI/CD con containers

## 3. Diferencias con Unit Tests

| Aspecto          | Unit Tests        | Integration Tests     |
| ---------------- | ----------------- | --------------------- |
| **Dependencias** | Mocks/stubs       | Componentes reales    |
| **Velocidad**    | Muy rápidos (ms)  | Lentos (segundos)     |
| **Alcance**      | Una clase/función | Múltiples componentes |
| **Aislamiento**  | Total             | Parcial               |
| **Flakiness**    | Muy bajo          | Medio-Alto            |
| **Cobertura**    | Lógica de negocio | Interacciones reales  |

## 4. Pirámide de Testing

```
         /\
        /  \     E2E Tests (10-20%)
       /────\
      /      \   Integration Tests (30-40%) ← Este estándar
     /────────\
    /          \ Unit Tests (50-60%)
   /────────────\
```

## 5. C# con WebApplicationFactory

### 5.1 Configuración

**Packages requeridos**:

```xml
<ItemGroup>
  <PackageReference Include="Microsoft.AspNetCore.Mvc.Testing" Version="8.0.*" />
  <PackageReference Include="Testcontainers" Version="3.7.*" />
  <PackageReference Include="Testcontainers.PostgreSql" Version="3.7.*" />
  <PackageReference Include="xunit" Version="2.6.*" />
  <PackageReference Include="FluentAssertions" Version="6.12.*" />
</ItemGroup>
```

### 5.2 Fixture Base con TestContainers

```csharp
using DotNet.Testcontainers.Builders;
using DotNet.Testcontainers.Containers;
using Microsoft.AspNetCore.Mvc.Testing;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.DependencyInjection.Extensions;
using Testcontainers.PostgreSql;

public class IntegrationTestFactory : WebApplicationFactory<Program>, IAsyncLifetime
{
    private readonly PostgreSqlContainer _dbContainer;
    private readonly IContainer _redisContainer;

    public IntegrationTestFactory()
    {
        // PostgreSQL container
        _dbContainer = new PostgreSqlBuilder()
            .WithImage("postgres:16-alpine")
            .WithDatabase("talma_test")
            .WithUsername("test")
            .WithPassword("test123")
            .WithWaitStrategy(Wait.ForUnixContainer().UntilPortIsAvailable(5432))
            .Build();

        // Redis container
        _redisContainer = new ContainerBuilder()
            .WithImage("redis:7-alpine")
            .WithPortBinding(6379, true)
            .WithWaitStrategy(Wait.ForUnixContainer().UntilPortIsAvailable(6379))
            .Build();
    }

    protected override void ConfigureWebHost(IWebHostBuilder builder)
    {
        builder.ConfigureServices(services =>
        {
            // Remover DbContext original
            services.RemoveAll<DbContextOptions<AppDbContext>>();
            services.RemoveAll<AppDbContext>();

            // Configurar DbContext con container de PostgreSQL
            services.AddDbContext<AppDbContext>(options =>
                options.UseNpgsql(_dbContainer.GetConnectionString()));

            // Configurar Redis con container
            services.AddStackExchangeRedisCache(options =>
            {
                options.Configuration = $"localhost:{_redisContainer.GetMappedPublicPort(6379)}";
            });

            // Aplicar migraciones
            var sp = services.BuildServiceProvider();
            using var scope = sp.CreateScope();
            var db = scope.ServiceProvider.GetRequiredService<AppDbContext>();
            db.Database.Migrate();
        });
    }

    public async Task InitializeAsync()
    {
        await _dbContainer.StartAsync();
        await _redisContainer.StartAsync();
    }

    public new async Task DisposeAsync()
    {
        await _dbContainer.DisposeAsync();
        await _redisContainer.DisposeAsync();
    }
}
```

### 5.3 Test Class con Fixture

```csharp
public class UsersControllerIntegrationTests : IClassFixture<IntegrationTestFactory>
{
    private readonly HttpClient _client;
    private readonly IntegrationTestFactory _factory;

    public UsersControllerIntegrationTests(IntegrationTestFactory factory)
    {
        _factory = factory;
        _client = factory.CreateClient();
    }

    [Fact]
    public async Task GetUsers_ReturnsSuccessAndCorrectStructure()
    {
        // Arrange
        await SeedDatabase();

        // Act
        var response = await _client.GetAsync("/api/v1/users");

        // Assert
        response.StatusCode.Should().Be(HttpStatusCode.OK);

        var content = await response.Content.ReadAsStringAsync();
        var result = JsonSerializer.Deserialize<ApiResponse<List<UserDto>>>(content, _jsonOptions);

        result.Should().NotBeNull();
        result!.Status.Should().Be("success");
        result.Data.Should().NotBeNull();
        result.Data.Should().HaveCount(3);
    }

    [Fact]
    public async Task CreateUser_ValidData_ReturnsCreatedWithLocation()
    {
        // Arrange
        var newUser = new CreateUserRequest
        {
            Name = "Juan Perez",
            Email = "juan@talma.com",
            Role = "Employee"
        };

        // Act
        var response = await _client.PostAsJsonAsync("/api/v1/users", newUser);

        // Assert
        response.StatusCode.Should().Be(HttpStatusCode.Created);
        response.Headers.Location.Should().NotBeNull();
        response.Headers.Location!.ToString().Should().Contain("/api/v1/users/");

        var content = await response.Content.ReadAsStringAsync();
        var result = JsonSerializer.Deserialize<ApiResponse<UserDto>>(content, _jsonOptions);

        result!.Data!.Name.Should().Be("Juan Perez");
        result.Data.Email.Should().Be("juan@talma.com");
        result.Data.Id.Should().BeGreaterThan(0);
    }

    [Fact]
    public async Task CreateUser_DuplicateEmail_ReturnsBadRequest()
    {
        // Arrange
        await SeedDatabase(); // Ya existe user1@talma.com

        var duplicateUser = new CreateUserRequest
        {
            Name = "Duplicate",
            Email = "user1@talma.com" // Email duplicado
        };

        // Act
        var response = await _client.PostAsJsonAsync("/api/v1/users", duplicateUser);

        // Assert
        response.StatusCode.Should().Be(HttpStatusCode.BadRequest);

        var content = await response.Content.ReadAsStringAsync();
        var problemDetails = JsonSerializer.Deserialize<ProblemDetails>(content, _jsonOptions);

        problemDetails!.Title.Should().Contain("Validation");
        problemDetails.Extensions["errors"].Should().NotBeNull();
    }

    [Fact]
    public async Task UpdateUser_ValidData_ReturnsOkAndUpdatesDatabase()
    {
        // Arrange
        await SeedDatabase();
        var userId = 1;

        var updateRequest = new UpdateUserRequest
        {
            Name = "Updated Name",
            Email = "updated@talma.com"
        };

        // Act
        var response = await _client.PutAsJsonAsync($"/api/v1/users/{userId}", updateRequest);

        // Assert
        response.StatusCode.Should().Be(HttpStatusCode.OK);

        // Verificar que se actualizó en la BD
        var getResponse = await _client.GetAsync($"/api/v1/users/{userId}");
        var content = await getResponse.Content.ReadAsStringAsync();
        var result = JsonSerializer.Deserialize<ApiResponse<UserDto>>(content, _jsonOptions);

        result!.Data!.Name.Should().Be("Updated Name");
        result.Data.Email.Should().Be("updated@talma.com");
    }

    [Fact]
    public async Task DeleteUser_ExistingUser_ReturnsNoContent()
    {
        // Arrange
        await SeedDatabase();
        var userId = 1;

        // Act
        var response = await _client.DeleteAsync($"/api/v1/users/{userId}");

        // Assert
        response.StatusCode.Should().Be(HttpStatusCode.NoContent);

        // Verificar que fue eliminado
        var getResponse = await _client.GetAsync($"/api/v1/users/{userId}");
        getResponse.StatusCode.Should().Be(HttpStatusCode.NotFound);
    }

    private async Task SeedDatabase()
    {
        using var scope = _factory.Services.CreateScope();
        var db = scope.ServiceProvider.GetRequiredService<AppDbContext>();

        // Limpiar datos anteriores
        db.Users.RemoveRange(db.Users);
        await db.SaveChangesAsync();

        // Seed datos de prueba
        db.Users.AddRange(
            new User { Id = 1, Name = "User 1", Email = "user1@talma.com", IsActive = true },
            new User { Id = 2, Name = "User 2", Email = "user2@talma.com", IsActive = true },
            new User { Id = 3, Name = "User 3", Email = "user3@talma.com", IsActive = false }
        );

        await db.SaveChangesAsync();
    }
}
```

## 6. TypeScript con Supertest

### 6.1 Configuración

**Packages**:

```json
{
  "devDependencies": {
    "@types/jest": "^29.5.0",
    "@types/supertest": "^6.0.0",
    "jest": "^29.7.0",
    "supertest": "^6.3.0",
    "ts-jest": "^29.1.0",
    "testcontainers": "^10.5.0"
  }
}
```

### 6.2 Setup con TestContainers

```typescript
import { GenericContainer, StartedTestContainer } from "testcontainers";
import { Pool } from "pg";

export class IntegrationTestEnvironment {
  private postgresContainer?: StartedTestContainer;
  private redisContainer?: StartedTestContainer;
  public dbPool?: Pool;

  async setup() {
    // PostgreSQL container
    this.postgresContainer = await new GenericContainer("postgres:16-alpine")
      .withEnvironment({
        POSTGRES_USER: "test",
        POSTGRES_PASSWORD: "test123",
        POSTGRES_DB: "talma_test",
      })
      .withExposedPorts(5432)
      .start();

    const postgresPort = this.postgresContainer.getMappedPort(5432);

    // Pool de conexiones
    this.dbPool = new Pool({
      host: "localhost",
      port: postgresPort,
      user: "test",
      password: "test123",
      database: "talma_test",
    });

    // Ejecutar migraciones
    await this.runMigrations();

    // Redis container
    this.redisContainer = await new GenericContainer("redis:7-alpine")
      .withExposedPorts(6379)
      .start();

    const redisPort = this.redisContainer.getMappedPort(6379);

    // Configurar variables de entorno
    process.env.DATABASE_URL = `postgresql://test:test123@localhost:${postgresPort}/talma_test`;
    process.env.REDIS_URL = `redis://localhost:${redisPort}`;
  }

  async teardown() {
    await this.dbPool?.end();
    await this.postgresContainer?.stop();
    await this.redisContainer?.stop();
  }

  async runMigrations() {
    // Implementar con herramienta de migraciones (TypeORM, Prisma, etc.)
  }

  async clearDatabase() {
    await this.dbPool!.query("TRUNCATE TABLE users CASCADE");
  }

  async seedDatabase(data: any) {
    // Implementar seeding
  }
}
```

### 6.3 Tests con Supertest

```typescript
import request from "supertest";
import { app } from "../src/app";
import { IntegrationTestEnvironment } from "./setup";

describe("Users API Integration Tests", () => {
  let testEnv: IntegrationTestEnvironment;

  beforeAll(async () => {
    testEnv = new IntegrationTestEnvironment();
    await testEnv.setup();
  }, 60000); // Timeout de 60s para containers

  afterAll(async () => {
    await testEnv.teardown();
  });

  beforeEach(async () => {
    await testEnv.clearDatabase();
  });

  describe("GET /api/v1/users", () => {
    it("should return empty array when no users exist", async () => {
      const response = await request(app).get("/api/v1/users").expect(200);

      expect(response.body).toMatchObject({
        status: "success",
        data: [],
      });
    });

    it("should return all users", async () => {
      // Seed database
      await testEnv.dbPool!.query(`
        INSERT INTO users (name, email, is_active)
        VALUES
          ('User 1', 'user1@talma.com', true),
          ('User 2', 'user2@talma.com', true)
      `);

      const response = await request(app).get("/api/v1/users").expect(200);

      expect(response.body.data).toHaveLength(2);
      expect(response.body.data[0]).toMatchObject({
        name: "User 1",
        email: "user1@talma.com",
      });
    });
  });

  describe("POST /api/v1/users", () => {
    it("should create user with valid data", async () => {
      const newUser = {
        name: "Juan Perez",
        email: "juan@talma.com",
        role: "Employee",
      };

      const response = await request(app)
        .post("/api/v1/users")
        .send(newUser)
        .expect(201);

      expect(response.body.data).toMatchObject({
        name: "Juan Perez",
        email: "juan@talma.com",
        id: expect.any(Number),
      });

      expect(response.headers.location).toContain("/api/v1/users/");

      // Verificar en BD
      const result = await testEnv.dbPool!.query(
        "SELECT * FROM users WHERE email = $1",
        ["juan@talma.com"],
      );

      expect(result.rows).toHaveLength(1);
      expect(result.rows[0].name).toBe("Juan Perez");
    });

    it("should return 400 for duplicate email", async () => {
      // Crear usuario inicial
      await testEnv.dbPool!.query(`
        INSERT INTO users (name, email)
        VALUES ('Existing', 'existing@talma.com')
      `);

      const duplicateUser = {
        name: "Duplicate",
        email: "existing@talma.com",
      };

      const response = await request(app)
        .post("/api/v1/users")
        .send(duplicateUser)
        .expect(400);

      expect(response.body.title).toContain("Validation");
    });

    it("should return 400 for invalid email format", async () => {
      const invalidUser = {
        name: "Test",
        email: "not-an-email",
      };

      await request(app).post("/api/v1/users").send(invalidUser).expect(400);
    });
  });

  describe("PUT /api/v1/users/:id", () => {
    it("should update existing user", async () => {
      // Crear usuario
      const result = await testEnv.dbPool!.query(`
        INSERT INTO users (name, email)
        VALUES ('Original', 'original@talma.com')
        RETURNING id
      `);

      const userId = result.rows[0].id;

      const updateData = {
        name: "Updated Name",
        email: "updated@talma.com",
      };

      await request(app)
        .put(`/api/v1/users/${userId}`)
        .send(updateData)
        .expect(200);

      // Verificar actualización en BD
      const updatedUser = await testEnv.dbPool!.query(
        "SELECT * FROM users WHERE id = $1",
        [userId],
      );

      expect(updatedUser.rows[0].name).toBe("Updated Name");
      expect(updatedUser.rows[0].email).toBe("updated@talma.com");
    });

    it("should return 404 for non-existent user", async () => {
      await request(app)
        .put("/api/v1/users/99999")
        .send({ name: "Test" })
        .expect(404);
    });
  });

  describe("DELETE /api/v1/users/:id", () => {
    it("should delete existing user", async () => {
      const result = await testEnv.dbPool!.query(`
        INSERT INTO users (name, email)
        VALUES ('To Delete', 'delete@talma.com')
        RETURNING id
      `);

      const userId = result.rows[0].id;

      await request(app).delete(`/api/v1/users/${userId}`).expect(204);

      // Verificar eliminación
      const check = await testEnv.dbPool!.query(
        "SELECT * FROM users WHERE id = $1",
        [userId],
      );

      expect(check.rows).toHaveLength(0);
    });
  });
});
```

## 7. Testing con Respawn (C# Database Cleanup)

```csharp
using Respawn;
using Npgsql;

public class IntegrationTestBase : IAsyncLifetime
{
    private readonly PostgreSqlContainer _dbContainer;
    private Respawner _respawner = null!;
    private NpgsqlConnection _connection = null!;

    public IntegrationTestBase()
    {
        _dbContainer = new PostgreSqlBuilder().Build();
    }

    public async Task InitializeAsync()
    {
        await _dbContainer.StartAsync();

        _connection = new NpgsqlConnection(_dbContainer.GetConnectionString());
        await _connection.OpenAsync();

        // Configurar Respawn para limpiar BD entre tests
        _respawner = await Respawner.CreateAsync(_connection, new RespawnerOptions
        {
            DbAdapter = DbAdapter.Postgres,
            SchemasToInclude = new[] { "public" },
            TablesToIgnore = new[] { "__EFMigrationsHistory" }
        });
    }

    protected async Task ResetDatabaseAsync()
    {
        await _respawner.ResetAsync(_connection);
    }

    public async Task DisposeAsync()
    {
        await _connection.DisposeAsync();
        await _dbContainer.DisposeAsync();
    }
}

// Uso
public class UsersTests : IntegrationTestBase
{
    [Fact]
    public async Task Test1()
    {
        await ResetDatabaseAsync(); // Limpia BD antes del test
        // ... test logic
    }
}
```

## 8. Testing de Message Queues

### 8.1 RabbitMQ con TestContainers

```csharp
using Testcontainers.RabbitMq;

public class MessageQueueTests : IAsyncLifetime
{
    private readonly RabbitMqContainer _rabbitMqContainer;

    public MessageQueueTests()
    {
        _rabbitMqContainer = new RabbitMqBuilder()
            .WithImage("rabbitmq:3.12-management-alpine")
            .Build();
    }

    public async Task InitializeAsync()
    {
        await _rabbitMqContainer.StartAsync();
    }

    [Fact]
    public async Task PublishMessage_SubscriberReceivesMessage()
    {
        // Arrange
        var connectionString = _rabbitMqContainer.GetConnectionString();
        var publisher = new MessagePublisher(connectionString);
        var subscriber = new MessageSubscriber(connectionString);

        var receivedMessages = new List<string>();
        subscriber.OnMessageReceived += (msg) => receivedMessages.Add(msg);

        await subscriber.StartAsync();

        // Act
        await publisher.PublishAsync("test-queue", "Hello World");

        await Task.Delay(1000); // Esperar recepción

        // Assert
        receivedMessages.Should().Contain("Hello World");
    }

    public async Task DisposeAsync()
    {
        await _rabbitMqContainer.DisposeAsync();
    }
}
```

## 9. Mejores Prácticas

### 9.1 Limpieza de Estado entre Tests

```csharp
// ✅ BIEN: Limpiar antes de cada test
[Fact]
public async Task Test1()
{
    await ResetDatabaseAsync();
    // ... test logic
}

// ✅ BIEN: Usar transacciones con rollback
public class TransactionalTest : IDisposable
{
    private readonly DbContext _context;
    private readonly IDbContextTransaction _transaction;

    public TransactionalTest()
    {
        _context = CreateDbContext();
        _transaction = _context.Database.BeginTransaction();
    }

    public void Dispose()
    {
        _transaction.Rollback(); // Rollback automático
        _transaction.Dispose();
        _context.Dispose();
    }
}
```

### 9.2 Tests Paralelos con Aislamiento

```csharp
// Cada test collection usa su propio container
[Collection("Database Collection 1")]
public class UserTests1 { }

[Collection("Database Collection 2")]
public class UserTests2 { }

// Definir collections
[CollectionDefinition("Database Collection 1")]
public class DatabaseCollection1 : ICollectionFixture<IntegrationTestFactory> { }

[CollectionDefinition("Database Collection 2")]
public class DatabaseCollection2 : ICollectionFixture<IntegrationTestFactory> { }
```

### 9.3 Timeouts Apropiados

```typescript
// ✅ BIEN: Timeout mayor para integration tests
describe("Integration Tests", () => {
  beforeAll(async () => {
    await testEnv.setup();
  }, 60000); // 60 segundos para iniciar containers

  it("should process order", async () => {
    // ...
  }, 10000); // 10 segundos para test individual
});
```

## 10. Organización de Tests

```
tests/
├── integration/
│   ├── api/
│   │   ├── UsersController.test.ts
│   │   ├── OrdersController.test.ts
│   │   └── AuthController.test.ts
│   ├── repositories/
│   │   ├── UserRepository.test.ts
│   │   └── OrderRepository.test.ts
│   ├── services/
│   │   └── PaymentService.test.ts (con API externa mockeada)
│   └── infrastructure/
│       ├── RabbitMQ.test.ts
│       └── S3Storage.test.ts
├── fixtures/
│   └── IntegrationTestFactory.cs
└── setup/
    └── TestEnvironment.ts
```

## 11. Antipatrones

❌ **Tests lentos sin justificación**: Optimizar seeding y queries
❌ **No limpiar estado**: Cada test debe partir de estado limpio
❌ **Compartir datos entre tests**: Causa flakiness
❌ **Mockear dependencias**: Si mockeas, es unit test, no integration
❌ **No usar containers**: Bases de datos in-memory no representan producción
❌ **Hardcodear URLs/puertos**: Usar containers con puertos dinámicos

## 12. Integración con CI/CD

### 12.1 GitHub Actions

```yaml
name: Integration Tests

on: [push, pull_request]

jobs:
  integration-tests:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Setup .NET
        uses: actions/setup-dotnet@v4
        with:
          dotnet-version: "8.0.x"

      - name: Start Docker (for TestContainers)
        run: |
          sudo systemctl start docker
          docker --version

      - name: Run integration tests
        run: dotnet test --filter "Category=Integration" --logger "trx;LogFileName=integration-tests.trx"

      - name: Publish test results
        if: always()
        uses: dorny/test-reporter@v1
        with:
          name: Integration Test Results
          path: "**/integration-tests.trx"
          reporter: dotnet-trx
```

### 12.2 GitLab CI with Docker-in-Docker

```yaml
integration-tests:
  stage: test
  image: mcr.microsoft.com/dotnet/sdk:8.0
  services:
    - docker:dind
  variables:
    DOCKER_HOST: tcp://docker:2375
    DOCKER_DRIVER: overlay2
  script:
    - dotnet test --filter "Category=Integration"
```

## 13. Antipatrones (NO Hacer)

### ❌ Antipatrón 1: Compartir Estado entre Tests

```csharp
// ❌ MAL - Tests comparten misma BD sin limpiar
public class OrdersControllerTests : IClassFixture<IntegrationTestFactory>
{
    [Fact]
    public async Task Test1_CreateOrder()
    {
        await _client.PostAsJsonAsync("/api/v1/orders", order);
        // No limpia la BD
    }

    [Fact]
    public async Task Test2_GetOrders() // Depende de Test1
    {
        var response = await _client.GetAsync("/api/v1/orders");
        var orders = await response.Content.ReadFromJsonAsync<List<Order>>();
        orders.Should().HaveCount(1); // Asume orden de Test1
    }
}

// ✅ BIEN - Cada test limpia su estado
public class OrdersControllerTests : IClassFixture<IntegrationTestFactory>
{
    private readonly Respawner _respawner;

    [Fact]
    public async Task CreateOrder_ValidData_ReturnsCreated()
    {
        // Arrange: Limpiar BD antes del test
        await _respawner.ResetAsync(_dbConnection);
        
        // Act & Assert
        await _client.PostAsJsonAsync("/api/v1/orders", order);
    }
}
```

**Problema**: Tests fallan aleatoriamente según orden de ejecución.  
**Solución**: Usar Respawn o limpiar BD en cada test con `beforeEach`.

### ❌ Antipatrón 2: No Usar TestContainers (usar BD local)

```csharp
// ❌ MAL - Conectar a PostgreSQL local del desarrollador
services.AddDbContext<AppDbContext>(options =>
    options.UseNpgsql("Host=localhost;Database=talma_dev")); // ❌ BD compartida

// ✅ BIEN - Usar TestContainers para aislamiento
var dbContainer = new PostgreSqlBuilder()
    .WithImage("postgres:16-alpine")
    .WithDatabase("talma_test")
    .Build();

await dbContainer.StartAsync();

services.AddDbContext<AppDbContext>(options =>
    options.UseNpgsql(dbContainer.GetConnectionString())); // ✅ BD aislada por test run
```

**Problema**: Tests interfieren con desarrollo local, no aislados, fallan en CI.  
**Solución**: Siempre usar TestContainers para crear BD efímera por ejecución.

### ❌ Antipatrón 3: Tests Lentos sin Paralelización

```csharp
// ❌ MAL - Tests secuenciales (lentos)
[Collection("Sequential")] // Fuerza ejecución secuencial
public class SlowIntegrationTests { }

// ✅ BIEN - Tests paralelos con aislamiento
[Collection("IntegrationTests")] // Permite paralelización
public class OrdersControllerTests : IClassFixture<IntegrationTestFactory>
{
    // Cada instancia de factory = contenedor separado
}
```

**Problema**: Suite de 100 integration tests toma 30+ minutos.  
**Solución**: Permitir paralelización con fixtures independientes.

### ❌ Antipatrón 4: No Verificar BD después de operaciones

```csharp
// ❌ MAL - Solo verificar HTTP response
[Fact]
public async Task CreateUser_ReturnsCreated()
{
    var response = await _client.PostAsJsonAsync("/api/v1/users", newUser);
    response.StatusCode.Should().Be(HttpStatusCode.Created); // Solo verifica API
}

// ✅ BIEN - Verificar que se guardó en BD
[Fact]
public async Task CreateUser_SavesToDatabase()
{
    var response = await _client.PostAsJsonAsync("/api/v1/users", newUser);
    response.StatusCode.Should().Be(HttpStatusCode.Created);

    // Verificar BD directamente
    using var scope = _factory.Services.CreateScope();
    var dbContext = scope.ServiceProvider.GetRequiredService<AppDbContext>();
    var savedUser = await dbContext.Users.FirstOrDefaultAsync(u => u.Email == newUser.Email);
    
    savedUser.Should().NotBeNull();
    savedUser!.Name.Should().Be(newUser.Name);
}
```

**Problema**: API retorna 201 pero no guardó en BD (false positive).  
**Solución**: Siempre verificar persistencia real consultando BD directamente.

## 14. Validación y Cumplimiento

### 14.1 Checklist de Implementación

- [ ] **WebApplicationFactory** (C#) o **Supertest** (TypeScript) configurado
- [ ] **TestContainers** para PostgreSQL/SQL Server/Redis
- [ ] **Limpieza de BD** con Respawn entre tests
- [ ] **Migrations aplicadas** automáticamente en test setup
- [ ] **Seed data** consistente y mínimo
- [ ] **Tests independientes** (sin estado compartido)
- [ ] **Verificación de BD** después de operaciones POST/PUT/DELETE
- [ ] **Paralelización** habilitada (fixtures independientes)
- [ ] **Integración con CI/CD** (GitHub Actions, GitLab CI)
- [ ] **Cobertura 30-40%** de la suite total de tests

### 14.2 Métricas de Calidad

| Métrica                           | Target  | Verificación                           |
| --------------------------------- | ------- | -------------------------------------- |
| Tiempo ejecución por test         | < 5s    | Reportes de xUnit / Jest               |
| Flakiness rate                    | < 2%    | Retries en CI, análisis de fallos      |
| Cobertura integration tests       | 30-40%  | Proporción vs total de tests           |
| Tests con TestContainers          | 100%    | Code review                            |
| Tests con limpieza de BD          | 100%    | Validación de Respawn usage            |
| Paralelización habilitada         | Sí      | Configuración de test runner           |

## 15. Referencias

### Estándares Relacionados

- [Unit Tests](./01-unit-tests.md) - Testing unitario con mocks
- [E2E Tests](./03-e2e-tests.md) - Testing end-to-end con Playwright
- [Docker](../infraestructura/01-docker.md) - Containerización
- [PostgreSQL](../bases-de-datos/01-postgresql.md) - Configuración de base de datos

### Convenciones Relacionadas

- [Naming Tests](../../convenciones/testing/01-naming-tests.md) - Nomenclatura de métodos de test

### Lineamientos Relacionados

- [Testing](../../lineamientos/desarrollo/03-testing.md) - Lineamientos generales de testing
- [Calidad y Testing](../../lineamientos/arquitectura/07-calidad-testing.md) - Enfoque arquitectónico

### Principios Relacionados

- [Calidad desde el Diseño](../../principios/arquitectura/08-calidad-desde-el-diseno.md) - Fundamento de calidad
- [Observabilidad desde el Diseño](../../principios/arquitectura/05-observabilidad-desde-el-diseno.md) - Testing de observabilidad

### ADRs Relacionados

- [ADR-010: Estándar Base de Datos](../../../decisiones-de-arquitectura/adr-010-standard-base-datos.md) - PostgreSQL y migraciones
- [ADR-007: Contenedores AWS](../../../decisiones-de-arquitectura/adr-007-contenedores-aws.md) - Containerización

### Documentación Externa

- [WebApplicationFactory](https://learn.microsoft.com/en-us/aspnet/core/test/integration-tests) - Microsoft Docs
- [TestContainers](https://testcontainers.com/) - Documentación oficial
- [Supertest](https://github.com/ladjs/supertest) - GitHub
- [Respawn](https://github.com/jbogard/Respawn) - Database cleanup
- [Integration Testing Best Practices](https://martinfowler.com/bliki/IntegrationTest.html) - Martin Fowler

---

**Última actualización**: 27 de enero 2026  
**Responsable**: Equipo de Arquitectura

### Documentación Oficial

- [WebApplicationFactory](https://learn.microsoft.com/en-us/aspnet/core/test/integration-tests)
- [TestContainers](https://testcontainers.com/)
- [Supertest](https://github.com/ladjs/supertest)
- [Respawn](https://github.com/jbogard/Respawn)

### Lineamientos Relacionados

- [Lineamiento Dev. 03: Testing](../../lineamientos/desarrollo/03-testing.md)
- [Lineamiento Arq. 07: Calidad y Testing](../../lineamientos/arquitectura/07-calidad-testing.md)

### Otros Estándares

- [Unit Tests](./01-unit-tests.md) - Testing unitario con mocks
- [E2E Tests](./03-e2e-tests.md) - Testing end-to-end con Playwright
- [Docker](../infraestructura/01-docker.md) - Containerización
