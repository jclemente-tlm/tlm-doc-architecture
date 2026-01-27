---
id: naming-endpoints
sidebar_position: 1
title: Naming - Endpoints REST
description: Convención de nomenclatura para endpoints y recursos REST
---

## 1. Principio

Los endpoints REST deben ser predecibles, consistentes y seguir las mejores prácticas de diseño RESTful para facilitar su uso y mantenimiento.

## 2. Reglas

### Regla 1: Estructura Base

- **Formato**: `/api/v{version}/{recurso}[/{id}][/{sub-recurso}]`
- **Ejemplo correcto**: `/api/v1/users`, `/api/v1/users/123`, `/api/v1/users/123/orders`
- **Ejemplo incorrecto**: `/api/users`, `/getUserById`, `/api/v1/getUser`
- **Justificación**: Versionado explícito, jerarquía clara

### Regla 2: Nombres de Recursos en Plural

- **Formato**: Sustantivos en plural, kebab-case
- **Ejemplo correcto**: `/api/v1/users`, `/api/v1/order-items`, `/api/v1/payment-methods`
- **Ejemplo incorrecto**: `/api/v1/user`, `/api/v1/OrderItems`, `/api/v1/payment_methods`
- **Justificación**: Consistencia, representa colecciones

```
✅ Correcto:
GET    /api/v1/users
GET    /api/v1/users/123
POST   /api/v1/users
PUT    /api/v1/users/123
DELETE /api/v1/users/123

❌ Incorrecto:
GET    /api/v1/user
GET    /api/v1/getUser/123
POST   /api/v1/createUser
```

### Regla 3: Kebab-Case para Recursos Compuestos

- **Formato**: `kebab-case` (palabras separadas por guiones)
- **Ejemplo correcto**: `/api/v1/order-items`, `/api/v1/payment-methods`, `/api/v1/user-profiles`
- **Ejemplo incorrecto**: `/api/v1/orderItems`, `/api/v1/order_items`, `/api/v1/OrderItems`

### Regla 4: Sub-recursos y Relaciones

- **Formato**: `/{recurso}/{id}/{sub-recurso}`
- **Ejemplo correcto**: `/api/v1/users/123/orders`, `/api/v1/orders/456/items`
- **Justificación**: Representa relaciones jerárquicas

```
✅ Ejemplos válidos:
GET /api/v1/users/123/orders           # Órdenes de un usuario
GET /api/v1/orders/456/items           # Items de una orden
GET /api/v1/users/123/addresses/789    # Dirección específica de un usuario
```

### Regla 5: Acciones No-CRUD (Excepciones)

Cuando no es posible mapear a CRUD, usar verbos pero como sub-recurso:

- **Formato**: `POST /{recurso}/{id}/{accion}`
- **Ejemplo correcto**: `POST /api/v1/orders/123/cancel`, `POST /api/v1/users/456/activate`
- **Ejemplo incorrecto**: `GET /api/v1/cancelOrder/123`, `POST /api/v1/activateUser`

```
✅ Correcto:
POST /api/v1/orders/123/cancel
POST /api/v1/payments/456/refund
POST /api/v1/users/789/reset-password

❌ Incorrecto:
POST /api/v1/cancelOrder/123
GET  /api/v1/refundPayment/456
```

### Regla 6: Filtrado, Ordenamiento y Búsqueda

Usar query parameters, **no** incluir en path:

- **Formato**: `GET /{recurso}?{filter}&{sort}`
- **Ejemplo correcto**: `/api/v1/users?status=active&sort=createdAt`
- **Ejemplo incorrecto**: `/api/v1/users/active`, `/api/v1/users/sorted-by-date`

## 3. Mapeo HTTP Methods

| Operación           | Method | Endpoint            | Body                | Respuesta           |
| ------------------- | ------ | ------------------- | ------------------- | ------------------- |
| Listar todos        | GET    | `/api/v1/users`     | -                   | 200 + array         |
| Obtener uno         | GET    | `/api/v1/users/123` | -                   | 200 + objeto        |
| Crear               | POST   | `/api/v1/users`     | Usuario             | 201 + objeto creado |
| Actualizar completo | PUT    | `/api/v1/users/123` | Usuario completo    | 200 + objeto        |
| Actualizar parcial  | PATCH  | `/api/v1/users/123` | Campos a actualizar | 200 + objeto        |
| Eliminar            | DELETE | `/api/v1/users/123` | -                   | 204 sin body        |

## 4. Tabla de Referencia Rápida

| Escenario          | Endpoint                           | Method |
| ------------------ | ---------------------------------- | ------ |
| Listar usuarios    | `/api/v1/users`                    | GET    |
| Crear usuario      | `/api/v1/users`                    | POST   |
| Obtener usuario    | `/api/v1/users/123`                | GET    |
| Actualizar usuario | `/api/v1/users/123`                | PUT    |
| Eliminar usuario   | `/api/v1/users/123`                | DELETE |
| Órdenes de usuario | `/api/v1/users/123/orders`         | GET    |
| Cancelar orden     | `/api/v1/orders/456/cancel`        | POST   |
| Filtrar activos    | `/api/v1/users?status=active`      | GET    |
| Ordenar por fecha  | `/api/v1/users?sort=createdAt`     | GET    |
| Paginar            | `/api/v1/users?page=2&pageSize=20` | GET    |

## 5. Versionado en URL

- **v1, v2, v3**: Versión en el path (recomendado)
- **NO usar**: Query params (`?version=1`), headers personalizados

```
✅ Correcto:
/api/v1/users
/api/v2/users

❌ Incorrecto:
/api/users?version=1
/api/users (con header X-API-Version: 1)
```

## 6. Casos Especiales

### Health Checks

```
GET /health          # Simple health check
GET /health/ready    # Readiness probe
GET /health/live     # Liveness probe
```

### Búsqueda Compleja

```
POST /api/v1/users/search    # Body con criterios complejos
```

### Operaciones en Batch

```
POST /api/v1/users/batch     # Crear múltiples
PUT  /api/v1/users/batch     # Actualizar múltiples
```

## 7. Checklist

- [ ] Todos los endpoints siguen `/api/v{version}/{recurso}`
- [ ] Recursos en plural (`/users`, no `/user`)
- [ ] kebab-case para recursos compuestos (`/order-items`)
- [ ] Verbos HTTP correctos (GET, POST, PUT, PATCH, DELETE)
- [ ] Query parameters para filtros (no en path)
- [ ] Acciones no-CRUD como sub-recursos (`/orders/123/cancel`)
- [ ] Documentación actualizada en OpenAPI/Swagger

## 8. Referencias

### Estándares Relacionados

- [Diseño REST](../../estandares/apis/01-diseno-rest.md) - Implementación técnica de APIs REST
- [Versionado APIs](../../estandares/apis/04-versionado.md) - Estrategias de versionado
- [OpenAPI/Swagger](../../estandares/documentacion/03-openapi-swagger.md) - Documentación de endpoints

### Lineamientos Relacionados

- [Diseño de APIs](../../lineamientos/arquitectura/06-diseno-de-apis.md) - Lineamientos arquitectónicos

### Principios Relacionados

- [Contratos de Comunicación](../../principios/arquitectura/06-contratos-de-comunicacion.md) - Fundamento de APIs estables
- [Simplicidad Intencional](../../principios/arquitectura/07-simplicidad-intencional.md) - APIs simples y predecibles

### Otras Convenciones

- [Headers HTTP](./02-headers-http.md) - Convenciones de headers
- [Formato Respuestas](./03-formato-respuestas.md) - Estructura de respuestas JSON
- [Formato Fechas y Moneda](./04-formato-fechas-moneda.md) - Formatos de datos

---

**Última actualización**: 26 de enero 2026  
**Responsable**: Equipo de Arquitectura

## 7. Herramientas de Validación

### OpenAPI / Swagger

```yaml
paths:
  /api/v1/users:
    get:
      summary: List users
      operationId: listUsers
    post:
      summary: Create user
      operationId: createUser
  /api/v1/users/{userId}:
    get:
      summary: Get user by ID
      parameters:
        - name: userId
          in: path
          required: true
          schema:
            type: integer
```

## 📖 Referencias

### Estándares relacionados

- [Diseño REST](/docs/fundamentos-corporativos/estandares/apis/diseno-rest)
- [Versionado de APIs](/docs/fundamentos-corporativos/estandares/apis/versionado)

### Convenciones relacionadas

- [Parámetros Query](./02-parametros-query.md)
- [Headers HTTP](./03-headers-http.md)

### Recursos externos

- [REST API Design Best Practices](https://restfulapi.net/)
- [Microsoft REST API Guidelines](https://github.com/microsoft/api-guidelines)

---

**Última revisión**: 26 de enero 2026
**Responsable**: Equipo de Arquitectura
