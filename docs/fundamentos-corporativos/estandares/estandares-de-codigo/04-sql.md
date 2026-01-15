---
title: "SQL"
description: "Lineamientos de estilo, buenas prácticas y seguridad para SQL, PostgreSQL y Oracle."
id: 04-sql
sidebar_position: 4
---

## Introducción

Este documento define los lineamientos para escribir código SQL en Talma, incluyendo recomendaciones específicas para PostgreSQL y Oracle.

## Objetivo

Promover consultas SQL legibles, eficientes y seguras, aplicando buenas prácticas para cada motor. Fomentar que la lógica de negocio resida en las aplicaciones y que las bases de datos sean solo repositorios de datos.

## Alcance

Aplica a todos los desarrolladores que trabajen con SQL, PostgreSQL u Oracle en la organización.

---

## Principios clave para SQL

- Nombres descriptivos y consistentes para tablas, columnas y objetos. Consulta la [guía de convenciones de nombres](../convenciones-de-nombres/04-objetos-base-datos.md).
- Usa MAYÚSCULAS para palabras reservadas.
- Indenta consultas para mejorar la legibilidad.
- Evita SELECT * y usa solo las columnas necesarias.
- Documenta procedimientos, funciones y vistas.

### Ejemplos generales

| Correcto                                 | Incorrecto         |
|------------------------------------------|-------------------|
| SELECT user_id, created_at FROM users;   | select * from users; |
| UPDATE orders SET status = 'paid';       | update Orders set Status='paid'; |

---

## Buenas prácticas generales

- Usa transacciones para operaciones críticas.
- Indexa columnas usadas en búsquedas frecuentes.
- Prefiere consultas simples y evita subconsultas innecesarias.
- Usa parámetros en consultas para evitar SQL Injection.
- Valida y normaliza datos antes de insertarlos.

---

## Lineamientos para PostgreSQL

- Nombres descriptivos y consistentes para tablas, columnas y objetos. Consulta la [guía de convenciones de nombres](../convenciones-de-nombres/04-objetos-base-datos.md).
- Usa tipos de datos nativos de Postgres (ej: `SERIAL`, `UUID`, `JSONB`).
- Prefiere `RETURNING` para obtener valores tras un `INSERT` o `UPDATE`.
- Aprovecha funciones y operadores avanzados (`ARRAY`, `COALESCE`, `ILIKE`).
- Usa `EXPLAIN ANALYZE` para optimizar consultas complejas.
- Evita funciones y extensiones no estándar si se busca portabilidad.

**Ejemplo de uso de RETURNING:**

```sql
INSERT INTO users (name, email) VALUES ('Ana', 'ana@mail.com') RETURNING user_id;
```

---

## Lineamientos para Oracle

- Usa secuencias (`SEQUENCE`) para claves primarias autoincrementales.
- Prefiere `NVL` para manejo de valores nulos.
- Usa `MERGE` para operaciones upsert.
- Aprovecha `PL/SQL` para lógica compleja y procedimientos almacenados.
- Usa `EXPLAIN PLAN` para analizar el rendimiento de las consultas.

**Ejemplo de uso de SEQUENCE:**

```sql
INSERT INTO users (user_id, name) VALUES (user_seq.NEXTVAL, 'Ana');
```

:::danger
Evita el uso de DBLINKS en Oracle. Su uso está prohibido por razones de seguridad y mantenibilidad.
:::

---

## Lineamiento clave: lógica de negocio en la aplicación

- La lógica de negocio debe implementarse en la aplicación, no en la base de datos.
- Evita procedimientos almacenados, triggers y lógica compleja en la base de datos, salvo casos justificados y documentados.
- Mantener los queries embebidos en la aplicación permite versionarlos junto al código, facilitando trazabilidad, revisiones y despliegues controlados.

---

### Ejemplos de lógica en la aplicación (C# .NET 8)

#### 1. Separación de lógica de negocio y acceso a datos

**Servicio de dominio (lógica de negocio):**

```csharp
public class OrderService
{
    private readonly IOrderRepository _orderRepository;
    public OrderService(IOrderRepository orderRepository)
    {
        _orderRepository = orderRepository;
    }

    public async Task<bool> PagarPedidoAsync(int orderId)
    {
        var order = await _orderRepository.GetByIdAsync(orderId);
        if (order == null || order.Status == "paid")
            return false;
        order.Status = "paid";
        await _orderRepository.UpdateAsync(order);
        return true;
    }
}
```

**Acceso a datos (repository):**

```csharp
public class OrderRepository : IOrderRepository
{
    private readonly DbContext _dbContext;
    public OrderRepository(DbContext dbContext)
    {
        _dbContext = dbContext;
    }

    public async Task<Order?> GetByIdAsync(int orderId)
    {
        return await _dbContext.Orders.FindAsync(orderId);
    }

    public async Task UpdateAsync(Order order)
    {
        _dbContext.Orders.Update(order);
        await _dbContext.SaveChangesAsync();
    }
}
```

---

#### 2. Entity Framework con SQL raw para PostgreSQL

```csharp
// Usando interpolación segura con FromSqlInterpolated (Npgsql)
var users = await dbContext.Users
    .FromSqlInterpolated($@"SELECT user_id, name, email FROM users WHERE is_active = {true}")
    .ToListAsync();
```

- Los parámetros se pasan con interpolación segura (`$@"...{param}"`).
- Nombres de columnas y tablas en minúsculas y snake_case.

---

#### 3. Entity Framework con SQL raw para Oracle

```csharp
// Usando parámetros con nombre y OracleParameter
var statusParam = new OracleParameter("status", "PENDING");
var orders = await dbContext.Orders
    .FromSqlRaw("SELECT ORDER_ID, STATUS FROM ORDERS WHERE STATUS = :status", statusParam)
    .ToListAsync();
```

- Los parámetros se definen explícitamente con `OracleParameter` y se referencian con `:nombre`.
- Nombres de columnas y tablas en mayúsculas.

---

## Seguridad

- Usa siempre parámetros en consultas para evitar SQL Injection.
- Limita privilegios de usuarios y roles en la base de datos.
- No expongas información sensible en mensajes de error.

---

## Referencias

- [Guía de estilo SQL](https://www.sqlstyle.guide/es/)
- [Documentación oficial de PostgreSQL](https://www.postgresql.org/docs/)
- [Documentación oficial de Oracle](https://docs.oracle.com/en/database/)
- [Documentación oficial de SQL Server](https://docs.microsoft.com/es-es/sql/)

## Última revisión

- Fecha: 2025-08-08
- Responsable: Equipo de Arquitectura
