# 8. Conceptos transversales

## 8.1 Seguridad

| Aspecto         | Implementación         | Tecnología         |
|-----------------|-----------------------|--------------------|
| Autenticación   | JWT                   | .NET 8, ASP.NET Core |
| Autorización    | Claims y roles        | .NET 8, ASP.NET Core |
| Cifrado         | TLS 1.3, AES-256      | HTTPS, PostgreSQL  |
| Datos sensibles | Cifrado en reposo y tránsito | AWS KMS, TLS 1.3 |

## 8.2 Observabilidad

| Tipo        | Herramienta     | Propósito         |
|-------------|-----------------|-------------------|
| Logs        | Serilog         | Registro eventos  |
| Métricas    | Prometheus      | Monitoreo         |
| Trazas      | OpenTelemetry   | Trazabilidad      |
| Health      | Health Checks   | Estado servicios  |

## 8.3 Multi-tenancy

| Aspecto         | Implementación         | Propósito              |
|-----------------|-----------------------|------------------------|
| Aislamiento     | Por tenant            | Separación de datos    |
| Configuración   | Por tenant            | Personalización        |
| Rate limiting   | Por tenant            | Protección recursos    |

## 8.4 Persistencia

- Almacenamiento de eventos y estados en PostgreSQL (AWS RDS).
- Esquema y configuración por tenant para aislamiento.
- Consultas optimizadas mediante índices y particionamiento.

## 8.5 Comunicación e integración

- Integración con sistemas externos mediante eventos (AWS SQS, SITA Messaging).
- Publicación y consumo de eventos con garantías de entrega.
- API REST para ingesta y consulta de eventos.

## 8.6 Testing

- Pruebas unitarias y de integración sobre lógica de dominio y eventos.
- Validación de contratos de eventos y proyecciones.
