# Contenedores y Despliegue

## Propósito
Definir los criterios arquitectónicos relacionados con el runtime, el despliegue y la operación de los sistemas, garantizando consistencia entre entornos, aislamiento de componentes y capacidad de evolución, sin prescribir tecnologías o configuraciones específicas.

## Alcance
Aplica a todos los sistemas, servicios y componentes ejecutables que formen parte de la arquitectura corporativa, independientemente del entorno donde se desplieguen.

## Criterios Arquitectónicos

### Uso de Contenedores como Unidad de Despliegue
La arquitectura adopta el contenedor como unidad estándar de despliegue, bajo los siguientes criterios:

- Cada componente ejecutable debe empaquetarse de forma aislada
- El artefacto desplegable debe ser inmutable
- El comportamiento del componente debe ser consistente entre entornos
- El runtime no debe depender de configuraciones locales del entorno de ejecución

El uso de contenedores busca consistencia, aislamiento y previsibilidad, no solo estandarización técnica.

---

### Separación de Componentes Stateless y Stateful
La arquitectura debe priorizar componentes stateless siempre que sea posible.

Criterios:

- El estado de la aplicación debe externalizarse
- Los componentes stateless deben poder escalar horizontalmente
- Los componentes stateful requieren justificación arquitectónica explícita

Cuando se utilicen componentes stateful:
- Debe existir una razón de dominio o técnica clara
- El impacto en escalabilidad, resiliencia y operación debe estar documentado

---

### Gestión de Configuración Externa
La configuración debe gestionarse como una preocupación separada del código y del artefacto desplegable:

- El artefacto no debe contener configuraciones dependientes del entorno
- La configuración debe poder variar entre entornos sin recompilación
- Los cambios de configuración no deben implicar cambios de código

La separación de configuración es un requisito para la portabilidad y la operación segura.

---

### Gestión de Entornos
La arquitectura debe definir y respetar una separación clara entre entornos:

- Cada entorno debe estar aislado de los demás
- La arquitectura debe ser consistente entre entornos
- La promoción entre entornos debe ser controlada y trazable

Las diferencias entre entornos deben limitarse a configuración y capacidad, no a diseño arquitectónico.

## Antipatrones
- Artefactos distintos por entorno
- Configuración embebida en el código o en el artefacto
- Dependencias del entorno local para la ejecución
- Uso indiscriminado de componentes stateful sin justificación
- Diferencias arquitectónicas entre entornos

## Resultado Esperado
Sistemas desplegables de forma consistente, predecible y controlada, con una arquitectura de runtime clara, aislada y preparada para escalar y evolucionar sin fricción operativa.
