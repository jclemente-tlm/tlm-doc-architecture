---
id: formato-fechas-moneda
sidebar_position: 4
title: Formato de Fechas y Moneda
description: Convención para representar fechas, horas, monedas y números
---

## 1. Principio

Los formatos de datos temporales, monetarios y numéricos deben ser consistentes y seguir estándares internacionales para evitar ambigüedades y facilitar la integración.

## 2. Reglas

### Regla 1: Fechas y Horas en ISO 8601 UTC

- **Formato**: `YYYY-MM-DDTHH:mm:ss.sssZ`
- **Ejemplo correcto**: `"2024-01-15T10:30:00.000Z"`
- **Ejemplo incorrecto**: `"15/01/2024"`, `"2024-01-15 10:30:00"`, `"Jan 15, 2024"`
- **Justificación**: Estándar internacional sin ambigüedad

```json
✅ Correcto:
{
  "createdAt": "2024-01-15T10:30:00.000Z",
  "updatedAt": "2024-01-15T14:45:30.123Z"
}

❌ Incorrecto:
{
  "createdAt": "15/01/2024 10:30",
  "updatedAt": "2024-01-15 14:45:30"
}
```

### Regla 2: Zona Horaria Siempre UTC

- **Formato**: Terminar siempre en `Z` (Zulu time = UTC)
- **NO usar**: Offsets locales (`-05:00`, `+02:00`)
- **Conversión**: Cliente convierte a zona local si necesario

```json
✅ Siempre UTC:
{
  "orderPlacedAt": "2024-01-15T10:30:00.000Z"
}

❌ NO usar timezone local:
{
  "orderPlacedAt": "2024-01-15T05:30:00.000-05:00"  // ❌ Lima time
}
```

### Regla 3: Solo Fecha (sin hora)

- **Formato**: `YYYY-MM-DD`
- **Ejemplo correcto**: `"2024-01-15"`
- **Uso**: Fechas de nacimiento, vencimientos, etc.

```json
{
  "birthDate": "1985-03-20",
  "expirationDate": "2024-12-31"
}
```

### Regla 4: Duración en ISO 8601

- **Formato**: `P[n]Y[n]M[n]DT[n]H[n]M[n]S`
- **Ejemplo correcto**: `"PT2H30M"` (2 horas 30 minutos)
- **Uso**: Tiempos de procesamiento, SLAs

```json
{
  "processingTime": "PT15M", // 15 minutos
  "slaResponseTime": "PT4H", // 4 horas
  "subscriptionPeriod": "P1M" // 1 mes
}
```

### Regla 5: Moneda con Código ISO 4217

- **Formato**: Objeto con `amount` (decimal) + `currency` (código ISO)
- **Ejemplo correcto**:

```json
{
  "price": {
    "amount": 1234.56,
    "currency": "PEN"
  },
  "discount": {
    "amount": 123.45,
    "currency": "PEN"
  }
}
```

- **Ejemplo incorrecto**:

```json
❌ Incorrecto:
{
  "price": 1234.56,           // ¿En qué moneda?
  "priceUSD": "$1,234.56",    // String formateado, no operable
  "amount": "1234.56 PEN"     // String mezclado
}
```

### Regla 6: Precisión Decimal en Moneda

- **Formato**: Máximo 2 decimales para monedas estándar
- **Excepciones**: Criptomonedas (8 decimales), materias primas (4 decimales)

```json
{
  "price": {
    "amount": 1234.56, // ✅ 2 decimales
    "currency": "PEN"
  },
  "bitcoinPrice": {
    "amount": 0.00012345, // ✅ 8 decimales para crypto
    "currency": "BTC"
  }
}
```

### Regla 7: Porcentajes como Decimal

- **Formato**: Número decimal (1.00 = 100%)
- **Ejemplo correcto**: `0.15` para 15%, `1.00` para 100%
- **Ejemplo incorrecto**: `15` para 15%, `"15%"` como string

```json
✅ Correcto:
{
  "taxRate": 0.18,           // 18% IGV
  "discountRate": 0.10       // 10% descuento
}

❌ Incorrecto:
{
  "taxRate": 18,             // Ambiguo
  "discountRate": "10%"      // String no operable
}
```

## 3. Códigos ISO 4217 Comunes

| Moneda          | Código | Decimales |
| --------------- | ------ | --------- |
| Sol Peruano     | PEN    | 2         |
| Dólar Americano | USD    | 2         |
| Euro            | EUR    | 2         |
| Peso Colombiano | COP    | 2         |
| Peso Chileno    | CLP    | 0         |
| Bitcoin         | BTC    | 8         |

## 4. Tabla de Referencia Rápida

| Tipo de Dato    | Formato                    | Ejemplo                                    |
| --------------- | -------------------------- | ------------------------------------------ |
| Fecha y hora    | `YYYY-MM-DDTHH:mm:ss.sssZ` | `"2024-01-15T10:30:00.000Z"`               |
| Solo fecha      | `YYYY-MM-DD`               | `"2024-01-15"`                             |
| Solo hora       | `HH:mm:ss`                 | `"14:30:00"`                               |
| Duración        | ISO 8601 duration          | `"PT2H30M"`                                |
| Moneda          | `{ amount, currency }`     | `{ "amount": 1234.56, "currency": "PEN" }` |
| Porcentaje      | Decimal                    | `0.18` (= 18%)                             |
| Booleano        | `true`/`false`             | `true` (no `"true"`, `1`, `"yes"`)         |
| Números grandes | Number (no string)         | `1234567890`                               |

## 5. Tipos de Datos en Respuestas

```json
{
  "id": 123, // number
  "name": "Juan Pérez", // string
  "isActive": true, // boolean
  "birthDate": "1985-03-20", // date (string ISO)
  "createdAt": "2024-01-15T10:30:00.000Z", // datetime (string ISO)
  "price": {
    // money (object)
    "amount": 1234.56,
    "currency": "PEN"
  },
  "taxRate": 0.18, // percentage (decimal)
  "tags": ["vip", "corporate"], // array
  "metadata": {
    // object
    "source": "web",
    "campaign": "summer2024"
  }
}
```

## 6. Casos Especiales

### Rangos de Fechas

```json
{
  "startDate": "2024-01-01T00:00:00.000Z",
  "endDate": "2024-12-31T23:59:59.999Z"
}
```

### Multi-moneda

```json
{
  "prices": [
    { "amount": 100.0, "currency": "PEN" },
    { "amount": 27.5, "currency": "USD" },
    { "amount": 25.0, "currency": "EUR" }
  ]
}
```

### Valores Nulos vs Ausentes

```json
✅ Campo opcional ausente:
{
  "name": "Juan"
  // middleName no está presente
}

✅ Campo conocido sin valor:
{
  "name": "Juan",
  "middleName": null  // Sabemos que no tiene segundo nombre
}

❌ Evitar:
{
  "name": "Juan",
  "middleName": ""    // String vacío puede ser ambiguo
}
```

## 7. Herramientas de Validación

### Serialización JSON (.NET)

```csharp
public class JsonSerializerOptions
{
    public JsonSerializerOptions()
    {
        PropertyNamingPolicy = JsonNamingPolicy.CamelCase;
        DefaultIgnoreCondition = JsonIgnoreCondition.WhenWritingNull;
        Converters.Add(new JsonStringEnumConverter());

        // Fechas en UTC ISO 8601
        Converters.Add(new DateTimeConverter());
    }
}

public class DateTimeConverter : JsonConverter<DateTime>
{
    public override void Write(Utf8JsonWriter writer, DateTime value, JsonSerializerOptions options)
    {
        writer.WriteStringValue(value.ToUniversalTime().ToString("O")); // ISO 8601
    }
}
```

### Serialización TypeScript

```typescript
export class Money {
  constructor(
    public amount: number,
    public currency: string,
  ) {
    if (!this.isValidCurrency(currency)) {
      throw new Error(`Invalid currency code: ${currency}`);
    }
  }

  private isValidCurrency(code: string): boolean {
    return ["PEN", "USD", "EUR", "COP", "CLP"].includes(code);
  }

  toJSON() {
    return {
      amount: Number(this.amount.toFixed(2)),
      currency: this.currency,
    };
  }
}

// Fechas siempre en UTC
export const serializeDate = (date: Date): string => {
  return date.toISOString(); // "2024-01-15T10:30:00.000Z"
};
```

### Validación de Schema (JSON Schema)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "createdAt": {
      "type": "string",
      "format": "date-time",
      "pattern": "^\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}\\.\\d{3}Z$"
    },
    "price": {
      "type": "object",
      "properties": {
        "amount": { "type": "number" },
        "currency": {
          "type": "string",
          "enum": ["PEN", "USD", "EUR", "COP", "CLP"]
        }
      },
      "required": ["amount", "currency"]
    }
  }
}
```

## 8. Checklist

- [ ] Fechas en ISO 8601 (`YYYY-MM-DDTHH:mm:ss.sssZ`)
- [ ] Siempre UTC (terminan en `Z`)
- [ ] Moneda en formato objeto con `amount` y `currency`
- [ ] Código de moneda ISO 4217 (`USD`, `EUR`, `PEN`)
- [ ] Cantidades numéricas (no strings)
- [ ] Decimales con punto (no coma)
- [ ] Precisión: 2 decimales para monedas estándar
- [ ] Validación con Regex/FluentValidation
- [ ] Documentación actualizada

## 9. Referencias

### Estándares Relacionados

- [Diseño REST](../../estandares/apis/01-diseno-rest.md) - Implementación de APIs
- [Validación y Errores](../../estandares/apis/03-validacion-y-errores.md) - Validación de formatos

### Lineamientos Relacionados

- [Diseño de APIs](../../lineamientos/arquitectura/06-diseno-de-apis.md) - Convenciones de APIs

### Principios Relacionados

- [Contratos de Comunicación](../../principios/arquitectura/06-contratos-de-comunicacion.md) - Formatos consistentes

### Otras Convenciones

- [Formato Respuestas](./03-formato-respuestas.md) - Estructura de respuestas

### Documentación Externa

- [ISO 8601 - Date and Time](https://www.iso.org/iso-8601-date-and-time-format.html)
- [ISO 4217 - Currency Codes](https://www.iso.org/iso-4217-currency-codes.html)
- [RFC 3339 - Date/Time on the Internet](https://datatracker.ietf.org/doc/html/rfc3339)

---

**Última revisión**: 26 de enero 2026  
**Responsable**: Equipo de Arquitectura
