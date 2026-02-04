---
id: single-responsibility
sidebar_position: 2
title: Single Responsibility Principle (SRP)
description: Estándar para aplicar el principio de responsabilidad única en clases, servicios y microservicios con separación de concerns y cohesión alta
---

# Estándar Técnico — Single Responsibility Principle (SRP)

---

## 1. Propósito

Aplicar el principio de responsabilidad única donde cada clase, módulo o servicio tiene UNA SOLA razón para cambiar, evitando acoplamiento, facilitando testing y mejorando mantenibilidad.

---

## 2. Alcance

**Aplica a:**

- Clases de dominio y servicios
- Controladores REST API
- Microservicios
- Módulos y componentes
- Funciones y métodos

**No aplica a:**

- DTOs simples (pueden tener múltiples propiedades sin lógica)
- Configuration classes (agrupan configuración relacionada)

---

## 3. Tecnologías Aprobadas

| Componente       | Tecnología       | Versión mínima | Observaciones                 |
| ---------------- | ---------------- | -------------- | ----------------------------- |
| **Backend**      | .NET             | 8+             | SOLID principles              |
| **Analysis**     | SonarQube        | Community      | Code smells detection         |
| **Testing**      | xUnit + Moq      | -              | Single responsibility testing |
| **DI Container** | ASP.NET Core DI  | -              | Dependency injection          |
| **Linting**      | Roslyn Analyzers | -              | Code quality rules            |

> El uso de tecnologías no listadas requiere aprobación de Arquitectura.

---

## 4. Requisitos Obligatorios 🔴

### Nivel de Clase

- [ ] **Una razón para cambiar**: Cada clase tiene UNA responsabilidad
- [ ] **Nombre descriptivo**: Revela la responsabilidad única
- [ ] **NO God Objects**: Máximo 200 líneas por clase
- [ ] **Alta cohesión**: Métodos relacionados entre sí

### Nivel de Servicio

- [ ] **Separación de concerns**: Validación ≠ persistencia ≠ notificación
- [ ] **Dependency Injection**: Composición sobre herencia
- [ ] **Interface segregation**: Interfaces pequeñas y específicas
- [ ] **NO circular dependencies**: Arquitectura en capas clara

### Nivel de Microservicio

- [ ] **Bounded context alineado**: Un servicio = una capacidad de negocio
- [ ] **Database per service**: BD independiente
- [ ] **Independent deployment**: Deploy sin coordinación
- [ ] **API cohesiva**: Endpoints relacionados

### Evitar

- [ ] **NO God Services**: Servicio con 10+ responsabilidades
- [ ] **NO Manager/Helper/Utility**: Nombres vagos
- [ ] **NO mixed concerns**: Lógica de negocio + infraestructura

---

## 5. Aplicación a Nivel de Clase

### ❌ Violación de SRP

```csharp
// ❌ MAL: Múltiples responsabilidades (validación + persistencia + email + logging)
public class UserService
{
    private readonly AppDbContext _dbContext;
    private readonly IEmailService _emailService;
    private readonly ILogger<UserService> _logger;

    // Responsabilidad #1: Validación
    public bool ValidateEmail(string email)
    {
        return Regex.IsMatch(email, @"^[^@\s]+@[^@\s]+\.[^@\s]+$");
    }

    // Responsabilidad #2: Persistencia
    public async Task SaveUserAsync(User user)
    {
        _dbContext.Users.Add(user);
        await _dbContext.SaveChangesAsync();
    }

    // Responsabilidad #3: Envío de email
    public async Task SendWelcomeEmailAsync(User user)
    {
        await _emailService.SendAsync(user.Email, "Welcome", "...");
    }

    // Responsabilidad #4: Logging
    public void LogUserActivity(User user, string action)
    {
        _logger.LogInformation("User {UserId} performed {Action}", user.Id, action);
    }

    // ❌ God Method: Hace DEMASIADO
    public async Task RegisterUserAsync(string email, string password)
    {
        // Validar
        if (!ValidateEmail(email))
            throw new ArgumentException("Invalid email");

        // Hash password
        var hashedPassword = BCrypt.Net.BCrypt.HashPassword(password);

        // Crear user
        var user = new User { Email = email, PasswordHash = hashedPassword };

        // Guardar
        await SaveUserAsync(user);

        // Enviar email
        await SendWelcomeEmailAsync(user);

        // Log
        LogUserActivity(user, "Registered");
    }
}
```

**Problemas:**

- 4 razones para cambiar (validación, DB, email, logging)
- Difícil testear (necesita mock de todo)
- Violación de Open/Closed (agregar SMS requiere modificar clase)

### ✅ Aplicación Correcta de SRP

```csharp
// ✅ BIEN: Cada clase UNA responsabilidad

// Responsabilidad #1: Validación de reglas de negocio
public class UserValidator : AbstractValidator<RegisterUserCommand>
{
    public UserValidator()
    {
        RuleFor(x => x.Email)
            .NotEmpty()
            .EmailAddress()
            .WithMessage("Email inválido");

        RuleFor(x => x.Password)
            .MinimumLength(8)
            .Matches(@"[A-Z]").WithMessage("Debe contener mayúscula")
            .Matches(@"[0-9]").WithMessage("Debe contener número");
    }
}

// Responsabilidad #2: Persistencia de usuarios
public class UserRepository : IUserRepository
{
    private readonly AppDbContext _dbContext;

    public UserRepository(AppDbContext dbContext)
    {
        _dbContext = dbContext;
    }

    public async Task<User> CreateAsync(User user)
    {
        _dbContext.Users.Add(user);
        await _dbContext.SaveChangesAsync();
        return user;
    }

    public async Task<User?> GetByEmailAsync(string email)
    {
        return await _dbContext.Users
            .FirstOrDefaultAsync(u => u.Email == email);
    }
}

// Responsabilidad #3: Hash de passwords
public class PasswordHasher : IPasswordHasher
{
    public string Hash(string password)
    {
        return BCrypt.Net.BCrypt.HashPassword(password, workFactor: 12);
    }

    public bool Verify(string password, string hash)
    {
        return BCrypt.Net.BCrypt.Verify(password, hash);
    }
}

// Responsabilidad #4: Envío de notificaciones
public class WelcomeEmailSender : INotificationSender
{
    private readonly IEmailService _emailService;

    public WelcomeEmailSender(IEmailService emailService)
    {
        _emailService = emailService;
    }

    public async Task SendAsync(User user)
    {
        await _emailService.SendAsync(
            to: user.Email,
            subject: "Bienvenido a Talma",
            body: $"Hola {user.Name}, tu cuenta ha sido creada."
        );
    }
}

// Orquestación (Command Handler) - UNA responsabilidad: Coordinar
public class RegisterUserCommandHandler : IRequestHandler<RegisterUserCommand, UserDto>
{
    private readonly IUserRepository _userRepository;
    private readonly IPasswordHasher _passwordHasher;
    private readonly INotificationSender _notificationSender;
    private readonly IMapper _mapper;

    public RegisterUserCommandHandler(
        IUserRepository userRepository,
        IPasswordHasher passwordHasher,
        INotificationSender notificationSender,
        IMapper mapper)
    {
        _userRepository = userRepository;
        _passwordHasher = passwordHasher;
        _notificationSender = notificationSender;
        _mapper = mapper;
    }

    public async Task<UserDto> Handle(RegisterUserCommand request, CancellationToken cancellationToken)
    {
        // Cada paso delegado a clase con responsabilidad única
        var user = new User
        {
            Id = Guid.NewGuid(),
            Email = request.Email,
            Name = request.Name,
            PasswordHash = _passwordHasher.Hash(request.Password),
            CreatedAt = DateTime.UtcNow
        };

        await _userRepository.CreateAsync(user);
        await _notificationSender.SendAsync(user);

        return _mapper.Map<UserDto>(user);
    }
}
```

**Ventajas:**

- ✅ Fácil testear cada clase aisladamente
- ✅ Cambiar validación NO afecta persistencia
- ✅ Cambiar de BCrypt a Argon2 solo toca PasswordHasher
- ✅ Agregar SMS notification sin tocar email sender

---

## 6. Aplicación a Controladores REST

### ❌ Controlador con Múltiples Responsabilidades

```csharp
// ❌ MAL: Controlador con lógica de negocio + validación + persistencia
[ApiController]
[Route("api/payments")]
public class PaymentsController : ControllerBase
{
    private readonly AppDbContext _dbContext;
    private readonly IStripeClient _stripeClient;
    private readonly ILogger<PaymentsController> _logger;

    [HttpPost]
    public async Task<IActionResult> CreatePayment([FromBody] CreatePaymentRequest request)
    {
        // Validación manual ❌
        if (request.Amount <= 0)
            return BadRequest("Amount must be positive");

        // Lógica de negocio ❌
        var payment = new Payment
        {
            Amount = request.Amount,
            Currency = "USD",
            Status = "pending"
        };

        // Llamada a API externa ❌
        var charge = await _stripeClient.CreateChargeAsync(new ChargeRequest
        {
            Amount = (int)(request.Amount * 100),
            Currency = "usd"
        });

        payment.ExternalId = charge.Id;
        payment.Status = charge.Status;

        // Persistencia directa ❌
        _dbContext.Payments.Add(payment);
        await _dbContext.SaveChangesAsync();

        // Logging ❌
        _logger.LogInformation("Payment {PaymentId} created", payment.Id);

        return Ok(payment);
    }
}
```

### ✅ Controlador con Responsabilidad Única (Routing)

```csharp
// ✅ BIEN: Controlador solo mapea HTTP → Comando → HTTP
[ApiController]
[Route("api/payments")]
public class PaymentsController : ControllerBase
{
    private readonly IMediator _mediator;

    public PaymentsController(IMediator mediator)
    {
        _mediator = mediator;
    }

    /// <summary>
    /// Crea un nuevo pago.
    /// </summary>
    [HttpPost]
    [ProducesResponseType(typeof(PaymentDto), StatusCodes.Status201Created)]
    [ProducesResponseType(StatusCodes.Status400BadRequest)]
    public async Task<IActionResult> CreatePayment([FromBody] CreatePaymentCommand command)
    {
        var result = await _mediator.Send(command);
        return CreatedAtAction(nameof(GetPayment), new { id = result.Id }, result);
    }

    [HttpGet("{id}")]
    [ProducesResponseType(typeof(PaymentDto), StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    public async Task<IActionResult> GetPayment(Guid id)
    {
        var query = new GetPaymentQuery { PaymentId = id };
        var result = await _mediator.Send(query);
        return result != null ? Ok(result) : NotFound();
    }
}

// La lógica está en el Handler (responsabilidad única)
public class CreatePaymentCommandHandler : IRequestHandler<CreatePaymentCommand, PaymentDto>
{
    private readonly IPaymentRepository _paymentRepository;
    private readonly IPaymentGateway _paymentGateway;
    private readonly IMapper _mapper;

    public async Task<PaymentDto> Handle(CreatePaymentCommand request, CancellationToken cancellationToken)
    {
        // Lógica de negocio delegada
        var payment = await _paymentGateway.ChargeAsync(request.Amount, request.Currency);
        await _paymentRepository.SaveAsync(payment);
        return _mapper.Map<PaymentDto>(payment);
    }
}
```

---

## 7. Aplicación a Microservicios

### ❌ Monolito Disfrazado

```text
┌───────────────────────────────────────────────────┐
│  CORE-API (❌ Múltiples responsabilidades)        │
│                                                   │
│  - User management                                │
│  - Payment processing                             │
│  - Product catalog                                │
│  - Order fulfillment                              │
│  - Notification sending                           │
│  - Reporting                                      │
│  - Analytics                                      │
│                                                   │
│  → 7 razones para cambiar                        │
│  → Deploy de todo o nada                          │
│  → Escalado ineficiente                           │
└───────────────────────────────────────────────────┘
```

### ✅ Microservicios con Responsabilidad Única

```text
┌─────────────────────┐
│  PAYMENT SERVICE    │  ← UNA responsabilidad: Procesar pagos
│  - Charge cards     │
│  - Refunds          │
│  - Payment history  │
└─────────────────────┘

┌─────────────────────┐
│  CUSTOMER SERVICE   │  ← UNA responsabilidad: Gestión de clientes
│  - Registration     │
│  - Profile updates  │
│  - Customer search  │
└─────────────────────┘

┌─────────────────────┐
│  NOTIFICATION SVC   │  ← UNA responsabilidad: Envío de notificaciones
│  - Email sending    │
│  - SMS delivery     │
│  - Template mgmt    │
└─────────────────────┘

┌─────────────────────┐
│  ORDER SERVICE      │  ← UNA responsabilidad: Gestión de pedidos
│  - Order creation   │
│  - Order tracking   │
│  - Order history    │
└─────────────────────┘
```

### Terraform - Microservicios Independientes

```hcl
# terraform/services/payment-service.tf

# Payment Service - UNA responsabilidad
resource "aws_ecs_service" "payment_service" {
  name            = "${var.environment}-payment-service"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.payment.arn
  desired_count   = 3

  # Base de datos independiente
  depends_on = [aws_db_instance.payment_db]

  # Deployment independiente (no afecta otros servicios)
  deployment_configuration {
    maximum_percent         = 200
    minimum_healthy_percent = 100
  }

  tags = {
    Responsibility = "Payment Processing"
    BoundedContext = "Payment"
  }
}

# Payment Database - Aislada
resource "aws_db_instance" "payment_db" {
  identifier = "${var.environment}-payment-db"
  engine     = "postgres"
  db_name    = "payment_db"

  tags = {
    Service = "payment-service"
  }
}

# terraform/services/customer-service.tf

# Customer Service - Responsabilidad diferente
resource "aws_ecs_service" "customer_service" {
  name            = "${var.environment}-customer-service"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.customer.arn
  desired_count   = 2

  # Base de datos independiente
  depends_on = [aws_db_instance.customer_db]

  tags = {
    Responsibility = "Customer Management"
    BoundedContext = "Customer"
  }
}

# Customer Database - Aislada
resource "aws_db_instance" "customer_db" {
  identifier = "${var.environment}-customer-db"
  engine     = "postgres"
  db_name    = "customer_db"

  tags = {
    Service = "customer-service"
  }
}
```

---

## 8. Interface Segregation (ISP)

### ❌ Interface Gorda (Fat Interface)

```csharp
// ❌ MAL: Interface con demasiadas responsabilidades
public interface IUserService
{
    // Authentication
    Task<bool> LoginAsync(string email, string password);
    Task LogoutAsync(Guid userId);

    // Profile management
    Task UpdateProfileAsync(Guid userId, UpdateProfileRequest request);
    Task<UserProfile> GetProfileAsync(Guid userId);

    // Password management
    Task ChangePasswordAsync(Guid userId, string oldPassword, string newPassword);
    Task ResetPasswordAsync(string email);

    // Email management
    Task VerifyEmailAsync(string token);
    Task ResendVerificationEmailAsync(Guid userId);

    // Preferences
    Task UpdatePreferencesAsync(Guid userId, UserPreferences preferences);

    // Notifications
    Task SendNotificationAsync(Guid userId, string message);

    // ❌ Clientes forzados a implementar TODO aunque solo necesiten login
}
```

### ✅ Interfaces Segregadas (Small Interfaces)

```csharp
// ✅ BIEN: Interfaces pequeñas y cohesivas

// Responsabilidad #1: Autenticación
public interface IAuthenticationService
{
    Task<AuthResult> LoginAsync(string email, string password);
    Task LogoutAsync(Guid userId);
    Task<bool> ValidateTokenAsync(string token);
}

// Responsabilidad #2: Gestión de perfil
public interface IProfileService
{
    Task UpdateAsync(Guid userId, UpdateProfileRequest request);
    Task<UserProfile> GetAsync(Guid userId);
}

// Responsabilidad #3: Gestión de contraseña
public interface IPasswordService
{
    Task ChangeAsync(Guid userId, string oldPassword, string newPassword);
    Task ResetAsync(string email);
    Task<bool> VerifyStrengthAsync(string password);
}

// Responsabilidad #4: Verificación de email
public interface IEmailVerificationService
{
    Task<bool> VerifyAsync(string token);
    Task ResendVerificationAsync(Guid userId);
}

// Cliente SOLO implementa lo que necesita
public class LoginController : ControllerBase
{
    private readonly IAuthenticationService _authService; // Solo lo necesario

    public LoginController(IAuthenticationService authService)
    {
        _authService = authService;
    }

    [HttpPost("login")]
    public async Task<IActionResult> Login([FromBody] LoginRequest request)
    {
        var result = await _authService.LoginAsync(request.Email, request.Password);
        return Ok(result);
    }
}
```

---

## 9. Detección de Violaciones de SRP

### SonarQube Rules

```xml
<!-- .editorconfig o sonar-project.properties -->

# Complejidad ciclomática máxima (detecta métodos God)
sonar.cs.metrics.complexity.maximum=10

# Líneas máximas por método
sonar.cs.metrics.methodLines.maximum=50

# Líneas máximas por clase
sonar.cs.metrics.classLines.maximum=200

# Número máximo de dependencias
sonar.cs.metrics.dependenciesMax=10
```

### Roslyn Analyzers

```xml
<!-- Directory.Build.props -->
<Project>
  <ItemGroup>
    <PackageReference Include="SonarAnalyzer.CSharp" Version="9.12.0.78982">
      <PrivateAssets>all</PrivateAssets>
      <IncludeAssets>runtime; build; native; contentfiles; analyzers; buildtransitive</IncludeAssets>
    </PackageReference>
  </ItemGroup>

  <PropertyGroup>
    <!-- S1200: Classes should not be coupled to too many other classes -->
    <WarningsAsErrors>S1200</WarningsAsErrors>

    <!-- S1118: Utility classes should not have public constructors -->
    <WarningsAsErrors>S1118</WarningsAsErrors>

    <!-- S3776: Cognitive Complexity of methods should not be too high -->
    <WarningsAsErrors>S3776</WarningsAsErrors>
  </PropertyGroup>
</Project>
```

---

## 10. Testing de Responsabilidad Única

### Unit Test - Clase con SRP

```csharp
// Test fácil porque PasswordHasher tiene UNA responsabilidad
public class PasswordHasherTests
{
    private readonly IPasswordHasher _passwordHasher;

    public PasswordHasherTests()
    {
        _passwordHasher = new PasswordHasher();
    }

    [Fact]
    public void Hash_ShouldReturnDifferentHashForSamePassword()
    {
        // Arrange
        var password = "MySecurePassword123";

        // Act
        var hash1 = _passwordHasher.Hash(password);
        var hash2 = _passwordHasher.Hash(password);

        // Assert
        hash1.Should().NotBe(hash2); // Diferentes salts
    }

    [Fact]
    public void Verify_ShouldReturnTrueForCorrectPassword()
    {
        // Arrange
        var password = "MySecurePassword123";
        var hash = _passwordHasher.Hash(password);

        // Act
        var isValid = _passwordHasher.Verify(password, hash);

        // Assert
        isValid.Should().BeTrue();
    }

    [Fact]
    public void Verify_ShouldReturnFalseForIncorrectPassword()
    {
        // Arrange
        var password = "MySecurePassword123";
        var hash = _passwordHasher.Hash(password);

        // Act
        var isValid = _passwordHasher.Verify("WrongPassword", hash);

        // Assert
        isValid.Should().BeFalse();
    }

    // SOLO 3 tests necesarios porque UNA responsabilidad: Hash passwords
}

// Test complejo porque God Class tiene MÚLTIPLES responsabilidades
public class UserServiceTests
{
    private readonly Mock<AppDbContext> _dbContextMock;
    private readonly Mock<IEmailService> _emailServiceMock;
    private readonly Mock<ILogger<UserService>> _loggerMock;
    private readonly UserService _userService;

    public UserServiceTests()
    {
        // ❌ Necesita mockear TODO
        _dbContextMock = new Mock<AppDbContext>();
        _emailServiceMock = new Mock<IEmailService>();
        _loggerMock = new Mock<ILogger<UserService>>();

        _userService = new UserService(
            _dbContextMock.Object,
            _emailServiceMock.Object,
            _loggerMock.Object
        );
    }

    // Necesita 20+ tests para cubrir todas las responsabilidades ❌
}
```

---

## 11. Validación de Cumplimiento

```bash
#!/bin/bash
# scripts/validate-srp.sh

echo "🔍 Validando Single Responsibility Principle..."

# 1. Detectar clases God (>200 líneas)
echo "1. Buscando God Classes (>200 líneas)..."
find src -name "*.cs" -exec wc -l {} \; | awk '$1 > 200 {print $2 " tiene " $1 " líneas ❌"}'

# 2. Detectar métodos God (>50 líneas)
echo "2. Buscando God Methods (>50 líneas)..."
# Requiere SonarQube Scanner
sonar-scanner \
  -Dsonar.projectKey=talma-platform \
  -Dsonar.sources=src \
  -Dsonar.host.url=http://sonarqube.local

# 3. Verificar arquitectura en capas (no circular dependencies)
echo "3. Verificando dependencias circulares..."
dotnet list package --include-transitive | grep -E "(Domain|Application|Infrastructure)" || echo "✅ No circular dependencies"

# 4. Verificar número de responsabilidades por microservicio
echo "4. Validando microservicios..."
kubectl get deployments -n production -o json | \
  jq -r '.items[] | "\(.metadata.name): \(.metadata.labels.responsibility // "⚠️  Sin label responsibility")"'

# 5. Verificar complejidad ciclomática
echo "5. Complejidad ciclomática (max 10)..."
dotnet build /p:RunCodeAnalysis=true /p:AnalysisLevel=latest

# Resultado esperado:
# ✅ Clases < 200 líneas
# ✅ Métodos < 50 líneas
# ✅ Complejidad < 10
# ✅ No circular dependencies
# ✅ Cada servicio con label "responsibility"
```

---

## 12. Referencias

**SOLID Principles:**

- [Single Responsibility Principle, Robert C. Martin](https://blog.cleancoder.com/uncle-bob/2014/05/08/SingleReponsibilityPrinciple.html)
- [SOLID Principles in C#, Microsoft](https://docs.microsoft.com/en-us/dotnet/architecture/modern-web-apps-azure/architectural-principles#single-responsibility)

**Code Quality:**

- [Clean Code, Robert C. Martin](https://www.oreilly.com/library/view/clean-code-a/9780136083238/)
- [SonarQube Rules for C#](https://rules.sonarsource.com/csharp/)
- [Roslyn Analyzers](https://github.com/dotnet/roslyn-analyzers)
