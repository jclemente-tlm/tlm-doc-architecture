# Integración y Comunicación

## Propósito
Definir los criterios arquitectónicos para la comunicación entre sistemas y servicios, garantizando desacoplamiento, claridad de responsabilidades, resiliencia y capacidad de evolución en el ecosistema de soluciones.

## Alcance
Aplica a toda interacción entre sistemas, servicios, componentes o dominios, tanto internos como externos a la organización.

## Criterios Arquitectónicos

### Comunicación Síncrona y Asíncrona
La elección del modelo de comunicación debe basarse en criterios arquitectónicos, no en conveniencia técnica.

#### Comunicación Síncrona
Es adecuada cuando:
- Se requiere una respuesta inmediata para continuar el flujo
- La operación es corta y predecible
- El consumidor depende del resultado para tomar decisiones inmediatas

Consideraciones:
- Introduce acoplamiento temporal
- Propaga fallas entre componentes
- Debe usarse de forma consciente y limitada

---

#### Comunicación Asíncrona
Es adecuada cuando:
- Se busca desacoplamiento temporal entre productor y consumidor
- Se tolera consistencia eventual
- Existen uno o más consumidores independientes
- Se prioriza resiliencia y escalabilidad

Consideraciones:
- Los flujos deben diseñarse para eventualidad
- El orden y la duplicidad deben ser considerados desde el diseño
- No debe asumirse entrega inmediata

---

### Eventos y APIs
La arquitectura debe diferenciar claramente el propósito de cada mecanismo:

- **APIs** exponen capacidades y operaciones explícitas
- **Eventos** comunican hechos que ya ocurrieron en el dominio

Criterios:
- Los eventos representan hechos inmutables del dominio
- Los productores de eventos no conocen a los consumidores
- Las APIs no deben usarse para publicar eventos
- Los eventos no deben utilizarse como mecanismo de orquestación centralizada sin control arquitectónico

---

### Reglas de Acoplamiento
Toda comunicación entre componentes debe cumplir:

- Contratos explícitos y versionados
- Acoplamiento mínimo entre productor y consumidor
- Ausencia de dependencias implícitas de implementación
- Independencia de ciclos de despliegue siempre que sea posible

El acoplamiento técnico nunca debe dictar la estructura del dominio.

---

### Idempotencia
La arquitectura debe asumir fallas y reintentos como condiciones normales de operación:

- Las operaciones deben ser idempotentes cuando exista posibilidad de reintentos
- Los mensajes duplicados no deben generar efectos colaterales
- El diseño debe permitir reprocesamiento seguro

La idempotencia es un requisito arquitectónico, no una optimización.

## Antipatrones
- Uso indiscriminado de comunicación síncrona
- Orquestación distribuida sin reglas claras
- Eventos que representan comandos o intenciones
- Dependencias implícitas entre servicios
- Diseño que asume entrega única o sin fallas

## Resultado Esperado
Sistemas integrados de forma clara y predecible, con comunicaciones desacopladas, resilientes y alineadas al dominio, capaces de evolucionar sin generar dependencias rígidas o efectos colaterales inesperados.
