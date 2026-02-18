---
id: rbac
sidebar_position: 1
title: Role-Based Access Control (RBAC)
description: Control de acceso basado en roles para gestionar permisos de forma escalable
---

# Role-Based Access Control (RBAC)

## Contexto

Este estándar define **RBAC (Role-Based Access Control)**: modelo de control de acceso donde permisos se asignan a **roles**, y usuarios se asignan a roles. Evita gestionar permisos individualmente por usuario (no escalable). Complementa el [lineamiento de Mínimo Privilegio](../../lineamientos/seguridad/04-minimo-privilegio.md) mediante **abstracción de permisos en roles**.

---

## Concepto Fundamental

```yaml
# Sin RBAC (❌) vs Con RBAC (✅)

Without RBAC (Direct Permission Assignment):

  User: juan.perez@talma.com
    Permissions:
      - orders:read
      - orders:create
      - orders:update
      - customers:read
      - invoices:read
      - products:read

  User: maria.garcia@talma.com
    Permissions:
      - orders:read
      - orders:create
      - orders:update
      - customers:read
      - invoices:read
      - products:read

  Problems:
    ❌ Repetición (same permissions copied per user)
    ❌ No escalable (100 users = 100 copies)
    ❌ Hard to update (new permission = update 100 users)
    ❌ Error-prone (forgot to add permission to one user)
    ❌ No audit trail (who has what?)

With RBAC (Role-Based):

  Role: Sales Representative
    Permissions:
      - orders:read
      - orders:create
      - orders:update
      - customers:read
      - invoices:read
      - products:read

  Users:
    - juan.perez@talma.com → Role: Sales Representative
    - maria.garcia@talma.com → Role: Sales Representative

  Benefits:
    ✅ DRY (permissions defined once)
    ✅ Escalable (1000 users = 1 role definition)
    ✅ Easy update (update role = all users updated)
    ✅ Consistent (all Sales Reps have same permissions)
    ✅ Auditable (who has "Sales Representative" role?)

# Adding New Permission

Without RBAC:
  - Update 100 users individually ❌

With RBAC:
  - Update 1 role definition → 100 users inherit ✅
```

## RBAC Components

```yaml
# Core Concepts

1. Permission (Leaf):

   Format: resource:action

   Examples:
     - orders:read → Can view orders
     - orders:create → Can create orders
     - orders:delete → Can delete orders
     - customers:update → Can modify customer data
     - invoices:approve → Can approve invoices

2. Role (Collection of Permissions):

   Role: Sales Representative
     Permissions:
       - orders:read
       - orders:create
       - orders:update
       - customers:read
       - products:read

   Role: Sales Manager
     Permissions:
       - orders:* (all order operations)
       - customers:*
       - products:*
       - invoices:read
       - invoices:approve
       - reports:sales

3. User-Role Assignment:

   User: juan.perez@talma.com
     Roles:
       - Sales Representative

   User: maria.garcia@talma.com
     Roles:
       - Sales Manager
       - Admin

4. Role Hierarchy (Inheritance):

   Role: Admin
     Inherits:
       - Sales Manager
       - Billing Manager

     Result: Admin has ALL permissions from both roles
```

## Implementation (Keycloak)

```yaml
# ✅ Keycloak RBAC Configuration

Realm: talma

# 1. Define Roles

Realm Roles:

  sales-representative:
    Description: "Sales team member - can manage orders"
    Composite: false

  sales-manager:
    Description: "Sales team leader - can approve orders"
    Composite: true
    Composite Roles:
      - sales-representative (inherits all permissions)

  admin:
    Description: "System administrator"
    Composite: true
    Composite Roles:
      - sales-manager
      - billing-manager
      - platform-engineer

# 2. Define Client Roles (Per Service)

Client: sales-service

  Client Roles:

    orders:read:
      Description: "View orders"

    orders:create:
      Description: "Create new orders"

    orders:update:
      Description: "Modify existing orders"

    orders:delete:
      Description: "Delete orders"

    orders:approve:
      Description: "Approve orders (manager only)"

# 3. Map Roles to Permissions

Role Mappings:

  sales-representative → Client Roles (sales-service):
    - orders:read
    - orders:create
    - orders:update

  sales-manager → Client Roles (sales-service):
    - orders:read
    - orders:create
    - orders:update
    - orders:delete
    - orders:approve

# 4. Assign Users to Roles

User: juan.perez@talma.com
  Role Mappings:
    Realm Roles:
      - sales-representative

User: maria.garcia@talma.com
  Role Mappings:
    Realm Roles:
      - sales-manager

# 5. JWT Token Claims

JWT Token for juan.perez@talma.com:

{
  "sub": "user-123",
  "email": "juan.perez@talma.com",
  "realm_access": {
    "roles": ["sales-representative"]
  },
  "resource_access": {
    "sales-service": {
      "roles": [
        "orders:read",
        "orders:create",
        "orders:update"
      ]
    }
  }
}
```

## Implementation (.NET)

```csharp
// ✅ RBAC Authorization in ASP.NET Core

// 1. Policy-Based Authorization

public class Startup
{
    public void ConfigureServices(IServiceCollection services)
    {
        services.AddAuthorization(options =>
        {
            // ✅ Policy: Requires specific permission
            options.AddPolicy("CanReadOrders", policy =>
                policy.RequireClaim("roles", "orders:read"));

            options.AddPolicy("CanCreateOrders", policy =>
                policy.RequireClaim("roles", "orders:create"));

            options.AddPolicy("CanApproveOrders", policy =>
                policy.RequireClaim("roles", "orders:approve"));

            // ✅ Policy: Requires role
            options.AddPolicy("SalesManager", policy =>
                policy.RequireRole("sales-manager"));

            // ✅ Policy: Custom requirement
            options.AddPolicy("CanDeleteOrder", policy =>
                policy.Requirements.Add(new OrderOwnerRequirement()));
        });

        services.AddSingleton<IAuthorizationHandler, OrderOwnerAuthorizationHandler>();
    }
}

// 2. Controller Authorization

[ApiController]
[Route("api/orders")]
[Authorize] // ✅ Requires authentication
public class OrdersController : ControllerBase
{
    private readonly IOrderService _orderService;

    // ✅ Public endpoint - any authenticated user
    [HttpGet]
    [Authorize(Policy = "CanReadOrders")]
    public async Task<IActionResult> GetOrders()
    {
        var orders = await _orderService.GetOrdersAsync();
        return Ok(orders);
    }

    // ✅ Restricted - requires specific permission
    [HttpPost]
    [Authorize(Policy = "CanCreateOrders")]
    public async Task<IActionResult> CreateOrder([FromBody] CreateOrderRequest request)
    {
        var orderId = await _orderService.CreateOrderAsync(request);
        return Created($"/api/orders/{orderId}", orderId);
    }

    // ✅ Manager only
    [HttpPost("{id}/approve")]
    [Authorize(Policy = "CanApproveOrders")]
    public async Task<IActionResult> ApproveOrder(Guid id)
    {
        await _orderService.ApproveOrderAsync(id);
        return NoContent();
    }

    // ✅ Custom authorization (resource-based)
    [HttpDelete("{id}")]
    [Authorize(Policy = "CanDeleteOrder")]
    public async Task<IActionResult> DeleteOrder(Guid id)
    {
        await _orderService.DeleteOrderAsync(id);
        return NoContent();
    }
}

// 3. Custom Authorization Handler

public class OrderOwnerRequirement : IAuthorizationRequirement { }

public class OrderOwnerAuthorizationHandler : AuthorizationHandler<OrderOwnerRequirement>
{
    private readonly IHttpContextAccessor _httpContextAccessor;
    private readonly IOrderService _orderService;

    protected override async Task HandleRequirementAsync(
        AuthorizationHandlerContext context,
        OrderOwnerRequirement requirement)
    {
        // ✅ Admin can delete any order
        if (context.User.IsInRole("admin"))
        {
            context.Succeed(requirement);
            return;
        }

        // ✅ Sales Manager can delete any order
        if (context.User.IsInRole("sales-manager"))
        {
            context.Succeed(requirement);
            return;
        }

        // ✅ Regular user can only delete own orders
        var httpContext = _httpContextAccessor.HttpContext;
        var orderIdStr = httpContext.Request.RouteValues["id"]?.ToString();

        if (!Guid.TryParse(orderIdStr, out var orderId))
        {
            context.Fail();
            return;
        }

        var order = await _orderService.GetByIdAsync(orderId);
        var userId = context.User.GetUserId();

        if (order.CreatedBy == userId)
        {
            // ✅ User owns this order
            context.Succeed(requirement);
        }
        else
        {
            context.Fail();
        }
    }
}

// 4. Manual Permission Check

public class OrderService : IOrderService
{
    private readonly IAuthorizationService _authz;
    private readonly IHttpContextAccessor _httpContextAccessor;

    public async Task CancelOrderAsync(Guid orderId)
    {
        var user = _httpContextAccessor.HttpContext.User;

        // ✅ Check permission programmatically
        var authResult = await _authz.AuthorizeAsync(user, orderId, "CanCancelOrder");

        if (!authResult.Succeeded)
        {
            throw new UnauthorizedAccessException("User cannot cancel this order");
        }

        // Business logic...
    }
}
```

## Role Matrix

```yaml
# ✅ Standard Roles Definition

Role: Platform Administrator
  Description: Full system access
  Permissions:
    - *:* (all resources, all actions)
  Users: 2-3 people only
  MFA: REQUIRED

Role: Security Administrator
  Permissions:
    - users:*
    - roles:*
    - permissions:*
    - audit-logs:read
    - security-configs:*
  Users: Security team
  MFA: REQUIRED

Role: DevOps Engineer
  Permissions:
    - deployments:*
    - infrastructure:*
    - logs:read
    - metrics:read
    - alerts:*
  Users: Platform team
  MFA: REQUIRED

Role: Developer
  Permissions:
    - code:read
    - code:write
    - deployments:dev
    - deployments:qa
    - logs:read (dev/qa only)
  Users: Development team
  MFA: RECOMMENDED

Role: Sales Manager
  Permissions:
    - orders:*
    - customers:*
    - products:read
    - invoices:read
    - invoices:approve
    - reports:sales
  Users: Sales leadership
  MFA: RECOMMENDED

Role: Sales Representative
  Permissions:
    - orders:read
    - orders:create
    - orders:update
    - customers:read
    - customers:create
    - products:read
  Users: Sales team
  MFA: OPTIONAL

Role: Billing Administrator
  Permissions:
    - invoices:*
    - payments:*
    - refunds:*
    - financial-reports:*
  Users: Finance team
  MFA: REQUIRED

Role: Read-Only User
  Permissions:
    - orders:read
    - customers:read
    - products:read
    - reports:read
  Users: BI analysts, executives
  MFA: OPTIONAL

# Role Hierarchy

Admin
  ├─► DevOps Engineer
  ├─► Security Administrator
  └─► Business Roles
       ├─► Sales Manager
       │    └─► Sales Representative
       └─► Billing Administrator
```

## Database Schema

```sql
-- ✅ RBAC Database Schema

-- Roles table
CREATE TABLE roles (
    role_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    role_name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    is_system_role BOOLEAN DEFAULT false, -- Can't be deleted
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Permissions table
CREATE TABLE permissions (
    permission_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    resource VARCHAR(100) NOT NULL, -- 'orders', 'customers'
    action VARCHAR(50) NOT NULL,    -- 'read', 'create', 'update', 'delete'
    description TEXT,
    UNIQUE(resource, action)
);

-- Role-Permission mapping
CREATE TABLE role_permissions (
    role_id UUID REFERENCES roles(role_id) ON DELETE CASCADE,
    permission_id UUID REFERENCES permissions(permission_id) ON DELETE CASCADE,
    granted_at TIMESTAMP DEFAULT NOW(),
    granted_by UUID REFERENCES users(user_id),
    PRIMARY KEY (role_id, permission_id)
);

-- User-Role mapping
CREATE TABLE user_roles (
    user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,
    role_id UUID REFERENCES roles(role_id) ON DELETE CASCADE,
    assigned_at TIMESTAMP DEFAULT NOW(),
    assigned_by UUID REFERENCES users(user_id),
    expires_at TIMESTAMP, -- Optional: Time-bound roles
    PRIMARY KEY (user_id, role_id)
);

-- Role hierarchy (inheritance)
CREATE TABLE role_hierarchy (
    parent_role_id UUID REFERENCES roles(role_id) ON DELETE CASCADE,
    child_role_id UUID REFERENCES roles(role_id) ON DELETE CASCADE,
    PRIMARY KEY (parent_role_id, child_role_id),
    CHECK (parent_role_id != child_role_id) -- Prevent self-reference
);

-- Audit log
CREATE TABLE role_audit_log (
    audit_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(user_id),
    action VARCHAR(50) NOT NULL, -- 'ROLE_ASSIGNED', 'ROLE_REVOKED', 'PERMISSION_ADDED'
    target_role_id UUID REFERENCES roles(role_id),
    target_user_id UUID REFERENCES users(user_id),
    previous_value JSONB,
    new_value JSONB,
    performed_by UUID REFERENCES users(user_id),
    performed_at TIMESTAMP DEFAULT NOW(),
    ip_address INET
);

-- Query: Get all permissions for user (including inherited)

CREATE OR REPLACE FUNCTION get_user_permissions(p_user_id UUID)
RETURNS TABLE(resource VARCHAR, action VARCHAR) AS $$
BEGIN
    RETURN QUERY
    WITH RECURSIVE role_tree AS (
        -- Direct roles
        SELECT r.role_id, r.role_name
        FROM user_roles ur
        JOIN roles r ON ur.role_id = r.role_id
        WHERE ur.user_id = p_user_id
          AND (ur.expires_at IS NULL OR ur.expires_at > NOW())

        UNION ALL

        -- Inherited roles (parent roles)
        SELECT r.role_id, r.role_name
        FROM role_tree rt
        JOIN role_hierarchy rh ON rt.role_id = rh.child_role_id
        JOIN roles r ON rh.parent_role_id = r.role_id
    )
    SELECT DISTINCT p.resource, p.action
    FROM role_tree rt
    JOIN role_permissions rp ON rt.role_id = rp.role_id
    JOIN permissions p ON rp.permission_id = p.permission_id;
END;
$$ LANGUAGE plpgsql;

-- Usage
SELECT * FROM get_user_permissions('user-123');
-- Returns:
-- resource  | action
-- orders    | read
-- orders    | create
-- customers | read
```

## Permission Naming Convention

```yaml
# ✅ Resource:Action Format

Format: {service}.{resource}:{action}

Examples:

  Sales Service:
    - sales.orders:read
    - sales.orders:create
    - sales.orders:update
    - sales.orders:delete
    - sales.orders:approve (custom action)
    - sales.customers:read
    - sales.customers:create

  Billing Service:
    - billing.invoices:read
    - billing.invoices:create
    - billing.invoices:approve
    - billing.payments:process
    - billing.refunds:issue

  Platform:
    - platform.users:manage
    - platform.roles:manage
    - platform.deployments:trigger
    - platform.infrastructure:modify

Wildcards:

  - sales.orders:* (all actions on orders)
  - sales.*:read (read all resources in sales service)
  - *:* (all permissions - admin only)

Anti-Patterns:

  ❌ Vague: "admin", "power-user"
  ❌ No namespace: "read", "write"
  ❌ Action-only: "delete" (delete what?)

  ✅ Specific: "sales.orders:delete"
```

## Monitoring & Audit

```yaml
# ✅ RBAC Audit Trail

Log All Changes:

  - Role assigned to user
    User: maria.garcia@talma.com
    Role: sales-manager
    Assigned By: admin@talma.com
    Timestamp: 2024-01-15 10:30:00

  - Permission added to role
    Role: sales-representative
    Permission: orders:approve (NEW)
    Added By: security-admin@talma.com
    Timestamp: 2024-01-15 11:00:00

  - Role revoked from user
    User: juan.perez@talma.com
    Role: developer (REVOKED)
    Reason: Left company
    Revoked By: hr@talma.com
    Timestamp: 2024-01-15 15:00:00

Quarterly Access Review:

  Report: "Users with elevated permissions"

  Query:
    SELECT u.email, r.role_name, ur.assigned_at
    FROM users u
    JOIN user_roles ur ON u.user_id = ur.user_id
    JOIN roles r ON ur.role_id = r.role_id
    WHERE r.role_name IN ('admin', 'security-administrator', 'platform-engineer')
    ORDER BY ur.assigned_at DESC;

  Action: Manager reviews and approves/revokes

Alerts:

  - Admin role assigned → CRITICAL alert (requires approval)
  - Permission added to role → INFO (audit log)
  - User assigned to multiple high-privilege roles → WARNING (review)
```

---

## Requisitos Técnicos

### MUST (Obligatorio)

- **MUST** usar RBAC (no direct permission assignment)
- **MUST** definir roles estándar por función (Sales Rep, Manager, Admin)
- **MUST** seguir naming convention: `resource:action`
- **MUST** auditar cambios de roles (who, what, when)
- **MUST** review access quarterly (remove stale assignments)

### SHOULD (Fuertemente recomendado)

- **SHOULD** usar role hierarchy (inheritance)
- **SHOULD** implementar resource-based authorization (owner checks)
- **SHOULD** usar policy-based authorization (not role checks in code)
- **SHOULD** aplicar MFA para roles privilegiados (admin, devops)

### MUST NOT (Prohibido)

- **MUST NOT** hardcodear permisos por usuario (use roles)
- **MUST NOT** usar roles ambiguos ("power-user", "advanced")
- **MUST NOT** asignar `*:*` wildcard excepto admin
- **MUST NOT** skip audit log (all role changes logged)

---

## Referencias

- [Lineamiento: Mínimo Privilegio](../../lineamientos/seguridad/04-minimo-privilegio.md)
- [ABAC](./abac.md)
- [JIT Access](./jit-access.md)
- [Access Reviews](./access-reviews.md)
- [Service Accounts](./service-accounts.md)
