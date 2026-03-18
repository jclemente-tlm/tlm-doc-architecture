## 1. Introducción y objetivos

Describe los requisitos relevantes y las fuerzas impulsoras que los arquitectos de software y el equipo de desarrollo deben considerar. Estos incluyen

objetivos comerciales subyacentes, características esenciales y requisitos funcionales del sistema,
objetivos de calidad para la arquitectura,
partes interesadas relevantes y sus expectativas
1.1 Descripción general de los requisitos
Contenido
Breve descripción de los requisitos funcionales, factores impulsores y extracto (o resumen) de los requisitos. Enlaces a los documentos de requisitos (preferiblemente existentes) con información sobre dónde encontrarlos.

Motivación
Desde el punto de vista de los usuarios finales, un sistema se crea o modifica para mejorar el soporte de una actividad empresarial y/o mejorar la calidad.

Forma
Breve descripción textual, probablemente en formato de caso de uso tabular. Si existen documentos de requisitos, esta descripción general debe hacer referencia a ellos.

Mantenga estos extractos lo más breves posible. Equilibre la legibilidad de este documento con la posible redundancia en relación con los documentos de requisitos.

Ejemplos
Ejemplo de descripción general: Unidad de seguimiento de tráfico
Ejemplo de descripción general: Comprobador de integridad de HTML
<insertar descripción general de los requisitos>
1.2 Objetivos de calidad
Contenido
Los tres objetivos de calidad principales (máximo cinco) para la arquitectura, cuyo cumplimiento es de máxima importancia para las principales partes interesadas. Nos referimos a los objetivos de calidad para la arquitectura. No los confunda con los objetivos del proyecto. No son necesariamente idénticos.

La norma ISO 25010 ofrece una buena descripción general de posibles temas de interés:

Categorías de requisitos de calidad ISO 25010

Motivación
Debe conocer los objetivos de calidad de sus principales partes interesadas, ya que influirán en decisiones arquitectónicas fundamentales. Asegúrese de ser muy concreto sobre estas cualidades y evite las palabras de moda. Si usted, como arquitecto, no sabe cómo se evaluará la calidad de su trabajo…

Forma
Una tabla con los objetivos de calidad más importantes y escenarios concretos, ordenados por prioridades.

Consulte la sección 10 (Requisitos de calidad) para obtener una descripción completa de los escenarios de calidad.

Ejemplos
Ejemplos de escenarios de calidad: Comprobador de integridad de HTML
Ejemplo de escenarios de calidad: TrafficPursuitUnit
<insertar tabla de objetivos de calidad aquí>
1.3 Partes interesadas
Contenido
Descripción general explícita de las partes interesadas del sistema, es decir, todas las personas, roles u organizaciones que

debe conocer la arquitectura
Hay que estar convencido de la arquitectura
tener que trabajar con la arquitectura o con el código
Necesitan la documentación de la arquitectura para su trabajo.
tienen que tomar decisiones sobre el sistema o su desarrollo
Motivación
Debe conocer a todas las partes involucradas en el desarrollo del sistema o afectadas por él. De lo contrario, podría encontrarse con sorpresas desagradables más adelante en el proceso de desarrollo. Estas partes interesadas determinan el alcance y el nivel de detalle de su trabajo y sus resultados.

Forma
Tabla con nombres de roles, nombres de personas y sus expectativas con respecto a la arquitectura y su documentación.

<Complete la tabla de partes interesadas:>
Rol/Nombre  Contacto Esperanzas de heredar
… … …

## 2. Restricciones de la arquitectura

Contenido
Cualquier requisito que limite la libertad de los arquitectos de software para tomar decisiones de diseño e implementación, o sobre el proceso de desarrollo. Estas restricciones, en ocasiones, trascienden los sistemas individuales y son aplicables a organizaciones y empresas en su conjunto.

Motivación
Los arquitectos deben saber exactamente dónde tienen libertad en sus decisiones de diseño y dónde deben ceñirse a las restricciones. Las restricciones siempre deben abordarse, aunque pueden ser negociables.

Forma
Tablas sencillas de restricciones con explicaciones. Si es necesario, se pueden subdividir en restricciones técnicas, organizativas y políticas, y convenciones (p. ej., directrices de programación o control de versiones, documentación o convenciones de nomenclatura).

Ejemplos
Ejemplo de restricciones: Comprobador de integridad de HTML
<insertar restricciones relevantes>

## 3. Contexto y alcance

Contenido
El alcance y contexto del sistema, como su nombre indica, delimitan el sistema (es decir, su alcance) de todos sus interlocutores (sistemas y usuarios vecinos, es decir, el contexto del sistema). De esta manera, especifica las interfaces externas.

Si es necesario, diferencie el contexto empresarial (entradas y salidas específicas del dominio) del contexto técnico (canales, protocolos, hardware).

Motivación
Las interfaces de dominio y las interfaces técnicas con los socios de comunicación se encuentran entre los aspectos más críticos de su sistema. Asegúrese de comprenderlas completamente.

Forma
Varios diagramas de contexto
Listas de socios de comunicación y sus interfaces.
Ejemplos
Vea a continuación, separado en contexto comercial y técnico.

3.1 Contexto empresarial
Contenido
Especificación de todos los interlocutores (usuarios, sistemas informáticos, etc.) con explicaciones de las entradas y salidas o interfaces específicas del dominio. Opcionalmente, puede añadir formatos o protocolos de comunicación específicos del dominio.

Motivación
Todas las partes interesadas deben comprender qué datos se intercambian con el entorno del sistema.

Forma
Todo tipo de diagramas que muestran el sistema como una caja negra y especifican las interfaces del dominio para los socios de comunicación.

Como alternativa (o adicionalmente), puede usar una tabla. El título de la tabla es el nombre de su sistema; las tres columnas contienen el nombre del interlocutor, las entradas y las salidas.

Ejemplos
Ejemplo de contexto empresarial: Comprobador de integridad de HTML
Ejemplo de contexto empresarial: MaMa
Ejemplo de contexto empresarial: TrafficPursuitUnit
Ejemplo de contexto empresarial: status.arc42.orgt
<insertar diagrama o tabla>
<(opcionalmente:) insertar explicación de las interfaces de dominio externo>
3.2 Contexto técnico
Contenido
Interfaces técnicas (canales y medios de transmisión) que conectan su sistema con su entorno. Además, se incluye una asignación de entradas/salidas específicas del dominio a los canales, es decir, una explicación de qué canal utiliza la E/S.

Motivación
Muchas partes interesadas toman decisiones arquitectónicas basándose en las interfaces técnicas entre el sistema y su contexto. En particular, los diseñadores de infraestructura o hardware deciden estas interfaces técnicas.

Forma
Por ejemplo, un diagrama de implementación UML que describe canales hacia sistemas vecinos, junto con una tabla de mapeo que muestra las relaciones entre canales y entradas/salidas.

Ejemplos
Ejemplo de contexto técnico: Comprobador de integridad de HTML
Ejemplo de contexto técnico: TrafficPursuitUnit
<insertar diagrama o tabla>
<(opcionalmente:) insertar explicación de las interfaces técnicas>
<insertar asignación de entrada/salida a canales>

## 4. Estrategia de solución

Contenido
Un breve resumen y explicación de las decisiones fundamentales y las estrategias de solución que configuran la arquitectura del sistema. Estas incluyen:

decisiones tecnológicas
decisiones sobre la descomposición de nivel superior del sistema, por ejemplo, el uso de un patrón arquitectónico o un patrón de diseño
decisiones sobre cómo alcanzar objetivos clave de calidad
decisiones organizativas relevantes, por ejemplo, seleccionar un proceso de desarrollo o delegar determinadas tareas a terceros.
Motivación
Estas decisiones constituyen los pilares de su arquitectura y son la base de muchas otras decisiones detalladas o reglas de implementación.

Forma
Mantenga breve la explicación de estas decisiones clave.

Justifique su decisión y sus razones,
basándose en el planteamiento del problema, los objetivos de calidad y las limitaciones clave. Consulte los detalles en las siguientes secciones ( sección 5 para detalles estructurales, sección 8 para conceptos transversales).

Podría utilizar una lista de enfoques de solución o una tabla similar a la siguiente:

Objetivo de calidad Guión Enfoque de solución Enlace a los detalles
<Objetivo Q 1>  <Texto> <Texto> <Enlace>
<Objetivo Q 2>  <Texto> <Texto> <Enlace>
Ejemplos
Ejemplo de estrategia de solución: Comprobador de integridad de HTML
Ejemplo de estrategia de solución: MaMa
<insertar estrategia de solución>
lista o tabla

## 5. Vista de bloques de construcción

Contenido
La vista de bloques de construcción muestra la descomposición estática del sistema en bloques de construcción (módulos, componentes, subsistemas, clases, interfaces, paquetes, bibliotecas, marcos, capas, particiones, niveles, funciones, macros, operaciones, estructuras de datos, …) así como sus dependencias (relaciones, asociaciones, …)

Esta vista es obligatoria para toda documentación arquitectónica. En analogía con una casa, este es el plano de planta .

Motivación
Mantenga una visión general de su código fuente haciendo que su estructura sea comprensible a través de la abstracción.

Esto le permite comunicarse con sus partes interesadas en un nivel abstracto sin revelar detalles de implementación.

Forma
La vista de bloques de construcción es una colección jerárquica de cuadros negros y cuadros blancos (ver la figura a continuación) y sus descripciones.

Alcance y contexto, diagrama de nivel 1 y nivel 2

El nivel 1 es la descripción de caja blanca del sistema general junto con las descripciones de caja negra de todos los bloques de construcción que contiene.
El nivel 2 amplía algunos bloques de construcción del nivel 1. Por lo tanto, contiene la descripción del cuadro blanco de los bloques de construcción seleccionados del nivel 1, junto con las descripciones del cuadro negro de sus bloques de construcción internos.
El nivel 3 (no se muestra en el diagrama anterior) amplía los detalles de los bloques de construcción seleccionados del nivel 2, y así sucesivamente.
Ejemplos
Ejemplo de vista de bloque de construcción: Comprobador de integridad de HTML
Ejemplo de vista de bloque de construcción: status.arc42.org
Ejemplo de bloque de construcción Vista de nivel 1: Unidad de seguimiento del tráfico
Ejemplo de bloque de construcción Vista de nivel 2: Unidad de seguimiento del tráfico
5.1 Sistema general de Whitebox
Aquí se describe la descomposición del sistema general utilizando la siguiente plantilla de caja blanca . Contiene

un diagrama general
una motivación para la descomposición
Descripciones de caja negra de los bloques de construcción que contiene. Para ello, le ofrecemos alternativas:
Utilice una tabla para obtener una descripción general breve y pragmática de todos los bloques de construcción contenidos y sus interfaces.
Utilice una lista de descripciones de caja negra de los bloques de construcción según la plantilla de caja negra (véase más abajo). Según la herramienta elegida, esta lista podría consistir en subcapítulos (en archivos de texto), subpáginas (en una wiki) o elementos anidados (en una herramienta de modelado).
(opcional:) interfaces importantes, que no se explican en las plantillas de caja negra de un bloque de construcción, pero que son muy importantes para comprender la caja blanca.
Dado que hay tantas formas de especificar interfaces, ¿por qué no proporcionar una plantilla específica para ellas?

En el mejor de los casos, podrás salirte con la tuya con ejemplos o firmas simples.

<insertar diagrama general del sistema general>
<describa la motivación/razonamiento para la descomposición general del sistema>
<describe los bloques de construcción contenidos (cajas negras)>
<(opcionalmente) describe interfaces importantes>
Inserta tus explicaciones de las cajas negras del nivel 1:

Si utiliza el formato tabular, solo describirá sus cajas negras con nombre y responsabilidad de acuerdo con el siguiente esquema:

Nombre Responsabilidad
<caja negra 1>  <Texto>
<caja negra 2>  <Texto>
Su encabezado es el nombre de la caja negra. Si utiliza una lista de descripciones de cajas negras, deberá completar una plantilla de caja negra independiente para cada componente importante.

A veces puede ser útil modificar la tabla con columnas adicionales:

Nombre Responsabilidad Interfaces Código
  <caja negra 1>  <Texto> ¿Cuales son las principales interfaces de este bloque? ¿Donde se encuentra el código?
  <caja negra 2>  <Texto> —”— —”—
<Nombre Caja Negra 1>
Aquí describe <caja negra 1> según la siguiente plantilla de caja negra :

Propósito/Responsabilidad
Interfaces, cuando no se extraen como párrafos separados. Estas interfaces pueden incluir cualidades y características de rendimiento.
(Opcional) Características de calidad/rendimiento de la caja negra, disponibilidad electrónica, comportamiento en tiempo de ejecución, ….
(Opcional) Ubicación del directorio/archivo
(Opcional) Requisitos cumplidos (si necesita trazabilidad de los requisitos).
(Opcional) Problemas/cuestiones/riesgos abiertos
Puedes utilizar una tabla o texto.

<Propósito/Responsabilidad>

<Interfaz(es)>

<(Opcional) Características de calidad/rendimiento>

<(Opcional) Ubicación del directorio/archivo>

<(Opcional) Requisitos cumplidos>

<(opcional) Problemas/Problemas/Riesgos abiertos>

<Nombre caja negra 2>
<plantilla de caja negra>

<Nombre caja negra n>
<plantilla de caja negra>

<Nombre interfaz 1>
…

<Nombre de la interfaz m>
5.2 Nivel 2
Aquí puedes especificar la estructura interna de (algunos) bloques de construcción del nivel 1 como cuadros blancos.

Debe decidir qué componentes de su sistema son lo suficientemente importantes como para justificar una descripción tan detallada. Priorice la relevancia sobre la exhaustividad. Especifique los componentes importantes, sorprendentes, arriesgados, complejos o volátiles. Omita las partes normales, simples, aburridas o estandarizadas de su sistema.

5.2.1 Caja blanca <bloque de construcción 1>
Especifica la estructura interna del bloque de construcción 1 .

Utilice la plantilla de caja blanca (ver arriba).

< Insertar plantilla de cuadro blanco del bloque de construcción 1 >

5.2.2 Caja blanca <bloque de construcción 2>
< Insertar plantilla de cuadro blanco para el bloque de construcción 2 >

…

5.2.n Caja blanca <bloque de construcción n>
< Insertar plantilla de cuadro blanco para el bloque de construcción n >

5.3 Nivel 3
Aquí puedes especificar la estructura interna de (algunos) bloques de construcción del nivel 2 como cuadros blancos.

Cuando necesite niveles más detallados de su arquitectura, copie esta parte de arc42 para obtener niveles adicionales.

5.3.1 Caja blanca <bloque de construcción x.1>
Especifica la estructura interna del bloque de construcción x.1 .

< Insertar plantilla de caja blanca del bloque de construcción x.1 >

5.3.2 Caja blanca <bloque de construcción x.2>
< Insertar plantilla de caja blanca del bloque de construcción x.2 >

5.3.3 Caja blanca <bloque de construcción y.1>
< Insertar plantilla de caja blanca del bloque de construcción y.1 >

## 6. Vista de tiempo de ejecución

Contenido
La vista de tiempo de ejecución describe el comportamiento concreto y las interacciones de los bloques de construcción del sistema en forma de escenarios de las siguientes áreas:

Casos de uso o características importantes: ¿cómo los ejecutan los bloques de construcción?
Interacciones en interfaces externas críticas: ¿cómo cooperan los bloques de construcción con los usuarios y los sistemas vecinos?
Operación y administración: lanzamiento, puesta en marcha, parada
escenarios de error y excepción
Observación: El criterio principal para la selección de posibles escenarios (secuencias, flujos de trabajo) es su relevancia arquitectónica . No es importante describir un gran número de escenarios. Se recomienda documentar una selección representativa.

Motivación
Debe comprender cómo las instancias de los bloques de construcción de su sistema realizan su trabajo y se comunican en tiempo de ejecución. Principalmente, capturará escenarios en su documentación para comunicar su arquitectura a las partes interesadas que tienen menos disposición o capacidad para leer y comprender los modelos estáticos (vista de bloques de construcción, vista de implementación).

Forma
Hay muchas anotaciones para describir escenarios, por ejemplo:

lista numerada de pasos (en lenguaje natural)
diagramas de actividades o diagramas de flujo
diagramas de secuencia
BPMN o EPC (cadenas de procesos de eventos)
máquinas de estados
…
Ejemplos
Ejemplo de vista en tiempo de ejecución: Comprobador de integridad de HTML
Ejemplo de vista de tiempo de ejecución: MaMa
Ejemplo de vista de tiempo de ejecución: TrafficPursuitUnit
6.1 <Escenario de ejecución 1>
<insertar diagrama de tiempo de ejecución o descripción textual del escenario>

< Insertar descripción de los aspectos notables de las interacciones entre las instancias de bloques de construcción representadas en este diagrama.

6.2 <Escenario de ejecución 2>
…
6.n <Escenario de ejecución n>

## 7. Vista de implementación

Contenido
La vista de implementación describe:

la infraestructura técnica utilizada para ejecutar su sistema, con elementos de infraestructura como ubicaciones geográficas, entornos, computadoras, procesadores, canales y topologías de red, así como otros elementos de infraestructura y
la asignación de bloques de construcción (de software) a esos elementos de infraestructura.
A menudo, los sistemas se ejecutan en diferentes entornos, por ejemplo, de desarrollo, de pruebas y de producción. En tales casos, es necesario documentar todos los entornos relevantes.

Documente especialmente la vista de implementación cuando su software se ejecuta como un sistema distribuido con más de una computadora, procesador, servidor o contenedor o cuando diseña y construye sus propios procesadores y chips de hardware.

Desde una perspectiva de software, basta con capturar los elementos de la infraestructura necesarios para mostrar la implementación de los componentes básicos. Los arquitectos de hardware pueden ir más allá y describir la infraestructura con el nivel de detalle que necesiten.

Motivación
El software no funciona sin hardware. Esta infraestructura subyacente puede influir, y lo hará, en su sistema o en algunos conceptos transversales. Por lo tanto, es necesario conocer la infraestructura.

Forma
Quizás el diagrama de implementación de mayor nivel ya se encuentre en la sección 3.2 como contexto técnico, con su propia infraestructura como una caja negra. En esta sección, analizará esta caja negra mediante diagramas de implementación adicionales.

UML ofrece diagramas de implementación para expresar esa visión. Úselo, probablemente con diagramas anidados, cuando su infraestructura sea más compleja.
Cuando las partes interesadas (de hardware) prefieran otros tipos de diagramas en lugar del diagrama de implementación UML, permítales utilizar cualquier tipo que pueda mostrar nodos y canales de la infraestructura.
Ejemplos
Ejemplo de vista de implementación: Unidad de seguimiento de tráfico
Ejemplo de vista de implementación: Comprobador de integridad de HTML
Ejemplo de vista de implementación: Unidad de seguimiento de tráfico de nivel 2
7.1 Nivel de infraestructura 1
Describa (generalmente en una combinación de diagramas, tablas y texto):

la distribución de su sistema a múltiples ubicaciones, entornos, ordenadores, procesadores, .. así como las conexiones físicas entre ellos
Justificación o motivación importante para esta estructura de despliegue
Características de calidad y/o rendimiento de la infraestructura
el mapeo de artefactos de software (bloques de construcción) a elementos de la infraestructura
Para entornos múltiples o implementaciones alternativas, copie esa sección de arc42 para todos los entornos relevantes. **

< Insertar diagrama de descripción general de la infraestructura >

Motivación
<insertar descripción de la motivación o explicación en formato de texto>

(opcional) Características de calidad y/o rendimiento
<opcionalmente inserte descripción de características de calidad o rendimiento>

Cartografía
< Insertar descripción del mapeo de bloques de construcción >

7.2 Infraestructura Nivel 2
Aquí puede incluir la estructura interna de (algunos) elementos de infraestructura del nivel de infraestructura 1.

Copie la estructura del nivel 1 para cada elemento seleccionado.

7.2.1 < Elemento de infraestructura 1 >
< insertar diagrama + explicación >

7.2.2 < Elemento de infraestructura 1 >
< insertar diagrama + explicación >

…
< insertar diagrama + explicación >

7.2.n < Elemento de infraestructura 1 >
< insertar diagrama + explicación >

## 8. Conceptos transversales

Contenido
Esta sección describe conceptos transversales (prácticas, patrones, normativas o ideas de solución). Estos conceptos suelen estar relacionados con múltiples bloques de construcción. Pueden incluir diversos temas, como los que se muestran en el siguiente diagrama:

Diagrama de conceptos transversales

Motivación
Los conceptos constituyen la base de la integridad conceptual (consistencia y homogeneidad) de la arquitectura. Por lo tanto, son una contribución importante para lograr las cualidades internas del sistema.

Este es el lugar en la plantilla que proporcionamos para una especificación cohesiva de dichos conceptos.

Muchos de estos conceptos se relacionan con varios de los componentes básicos o influyen en ellos.

Forma
La forma puede variar:

Documentos conceptuales con cualquier tipo de estructura
Implementaciones de ejemplo, especialmente para conceptos técnicos.
Extractos o escenarios de modelos transversales que utilizan notaciones de las vistas de arquitectura
Estructura de esta sección
Seleccione sólo los temas más necesarios para su sistema y asígnele a cada uno un encabezado de nivel 2 en esta sección (por ejemplo, 8.1, 8.2, etc.).

NO INTENTE cubrir todos los temas del diagrama mencionado anteriormente.

Fondo
Algunos temas dentro de los sistemas suelen abarcar múltiples bloques de construcción, elementos de hardware o procesos de desarrollo. Podría ser más fácil comunicar o documentar estos temas transversales en un lugar central, en lugar de repetirlos en la descripción de los bloques de construcción, elementos de hardware o procesos de desarrollo en cuestión.

Algunos conceptos pueden afectar a todos los elementos de un sistema, mientras que otros podrían ser relevantes solo para algunos. En el diagrama anterior, el registro afecta a los tres componentes, mientras que la seguridad solo afecta a dos.

Algunos ejemplos de la vida real:

Dentro de un sistema, se debe establecer un formato común para los mensajes de registro, junto con una convención común para elegir el destino de registro adecuado. Estas decisiones, junto con ejemplos de implementación, podrían describirse como "concepto de registro".
Un sistema tiene numerosos servicios backend que se comunican entre sí mediante llamadas a procedimientos remotos o REST basado en https.
Los servicios que llaman (“consumidores”) siempre necesitan autenticarse ante el servicio llamado (“proveedor”).
Para esta autenticación se debe utilizar un servicio de autorización común central.
Los detalles técnicos y organizativos de dicha autenticación podrían describirse como “concepto de autenticación de backend”.
(tomado del HTML Sanity Checker, ver más abajo): todos los componentes del verificador (7+) dentro del sistema están estructurados de acuerdo al patrón de estrategia.
Ejemplos
Concepto de ejemplo: Comprobador de integridad de HTML (dominio + URI)
Concepto de ejemplo: Comprobador de integridad de HTML (algoritmos de comprobación múltiple)
Concepto de ejemplo: Modelo de entidad de dominio TrafficPursuitUnit
Concepto de ejemplo: TrafficPursuitUnit, manejo de eventos
<describe conceptos aquí>

## 9. Decisiones de arquitectura

Contenido
Decisiones arquitectónicas importantes, costosas, a gran escala o arriesgadas, incluyendo sus fundamentos. Con "decisiones" nos referimos a la selección de una alternativa con base en criterios determinados.

Utilice su criterio para decidir si una decisión arquitectónica debe documentarse aquí, en esta sección central, o si es mejor documentarla localmente (por ejemplo, dentro de la plantilla de caja blanca de un bloque de construcción). Evite textos redundantes. Consulte la sección 4, donde ya registró las decisiones más importantes de su arquitectura.

Motivación
Las partes interesadas de su sistema deberían poder comprender y rastrear sus decisiones.

Forma
ADR ( registro de decisiones de arquitectura ) para cada decisión importante
lista o tabla, ordenada por importancia y consecuencias o
Más detallado en forma de secciones separadas por decisión.
Antecedentes (sobre las ADR)
Los fragmentos de documentación más pequeños son más fáciles de leer, crear y mantener. En lo que respecta a las decisiones de arquitectura, los equipos de desarrollo suelen:

conocer la decisión, tal como se ve, por ejemplo, en el código fuente, pero
Extraño la motivación detrás de esa decisión (ver Nygard 2011 )
Por lo tanto, debes documentar algunas decisiones importantes junto con su motivación y razonamiento.

Nuestra propuesta sobre las decisiones
Mantener una colección de decisiones arquitectónicamente significativas , aquellas decisiones que afectan la estructura, características de calidad, dependencias e interfaces importantes (especialmente externas) o técnicas de construcción (gracias a Michael Nygard por esta propuesta )

Puedes seguir la estructura de Nygard, que funciona de la siguiente manera:

Sección Descripción
Título Las decisiones deben tener un nombre propio. Por ejemplo, «ADR 42: Patrón de estrategia para algoritmos de verificación múltiple» o «ADR 9: Capa de claves para la gestión de secretos».
Contexto Describa la situación, incluyendo los aspectos técnicos, políticos, sociales y del proyecto. Estas fuerzas podrían estar en tensión.
Decisión ¿Cuál es nuestra decisión ( responder a las fuerzas descritas en el contexto)
Estado Una decisión puede ser "propuesta" si las partes interesadas importantes aún no la han acordado, o "aceptada" una vez acordada. También podría ser "obsoleta" o "reemplazada", preferiblemente con una referencia a su reemplazo.
Consecuencias ¿Qué consecuencias ocurrirán o podrían ocurrir como consecuencia de esta decisión? Aquí deben enumerarse todas las consecuencias, no solo las positivas. Una decisión en particular puede tener consecuencias positivas, negativas o neutrales, pero todas ellas afectan al equipo y al proyecto en el futuro.
Puede encontrar estructuras adicionales de ADR en la colección ADR de Github

Ejemplos
Ejemplo de decisión: utilizar ADR en formato Nygard
Ejemplo de decisión: Comprobador de integridad de HTML
Ejemplo de decisión: TrafficPursuitUnit
<describe aquí decisiones arquitectónicas importantes>

## 10. Requisitos de calidad

Contenido
Esta sección contiene todos los requisitos de calidad relevantes.

Los requisitos más importantes ya se describieron en la sección 1.2 (objetivos de calidad), por lo que solo deben mencionarse aquí. En esta sección 10, también debe incluir los requisitos de calidad de menor importancia, que no generen grandes riesgos si no se cumplen completamente (aunque podrían ser deseables ).

Motivación
Dado que los requisitos de calidad tendrán mucha influencia en las decisiones arquitectónicas, usted debe saber qué cualidades son realmente importantes para las partes interesadas, de una manera específica y medible.

Más información
Consulte el extenso modelo de calidad Q42 en <https://quality.arc42.org> .

Ejemplos
Ejemplos de escenarios de calidad: Comprobador de integridad de HTML
Ejemplo de escenarios de calidad: TrafficPursuitUnit
10.1 Descripción general de los requisitos de calidad
Contenido
Una descripción general o resumen de los requisitos de calidad.

Motivación
A menudo nos encontramos con docenas (o incluso cientos) de requisitos de calidad detallados. En esta sección general, debería intentar resumirlos, por ejemplo, describiendo categorías o temas (como sugieren las normas ISO 25010:2023 o Q42).

Si estas descripciones resumidas ya son precisas, suficientemente específicas y mensurables, puede omitir la sección 10.2.

Forma
Utilice una tabla sencilla donde cada línea contenga una categoría o tema y una breve descripción del requisito de calidad. Como alternativa, puede usar un mapa mental para estructurar estos requisitos de calidad.

En la literatura, también se ha descrito la idea de un árbol de atributos de calidad , que toma el término genérico «calidad» como raíz y utiliza una forma arborizada del término. [Bass+21] introdujo el término «Árbol de Utilidad de Atributos de Calidad» para este propósito.

<Proporcione aquí una descripción general de los requisitos de calidad>

10.2 Escenarios de calidad
Contenido
Los escenarios de calidad concretan los requisitos de calidad y permiten determinar si se cumplen (en el sentido de criterios de aceptación). Asegúrese de que sus escenarios sean específicos y medibles.

Hay dos tipos de escenarios especialmente útiles:

Los escenarios de uso (también llamados escenarios de aplicación o escenarios de caso de uso) describen la reacción del sistema en tiempo de ejecución ante un estímulo determinado. Esto también incluye escenarios que describen la eficiencia o el rendimiento del sistema. Ejemplo: El sistema reacciona a la solicitud de un usuario en un segundo.
Los escenarios de cambio describen el efecto deseado de una modificación o ampliación del sistema o de su entorno inmediato. Ejemplo: Se implementa una funcionalidad adicional o se modifican los requisitos de un atributo de calidad, y se mide el esfuerzo o la duración del cambio.
Forma
La información típica para escenarios detallados incluye lo siguiente:

En forma breve (favorecida en el modelo Q42):

Contexto/Antecedentes : ¿Qué tipo de sistema o componente, cuál es el entorno o la situación?
Fuente/Estímulo : ¿Quién o qué inicia o desencadena un comportamiento, reacción o acción?
Criterios de aceptación/métrica : una respuesta que incluye una medida o métrica
La forma larga de los escenarios (favorecida por el SEI y [Bass+21]) es más detallada e incluye la siguiente información:

ID de escenario : un identificador único para el escenario.
Nombre del escenario : un nombre corto y descriptivo para el escenario.
Fuente : La entidad (usuario, sistema o evento) que inicia el escenario.
Estímulo : El evento o condición desencadenante que el sistema debe abordar.
Entorno : El contexto o condición operacional bajo el cual el sistema experimenta el estímulo.
Artefacto : Los bloques de construcción u otros elementos del sistema afectados por el estímulo.
Respuesta : El resultado o comportamiento que el sistema exhibe en reacción al estímulo.
Medida de respuesta : El criterio o métrica mediante el cual se evalúa la respuesta del sistema.
Ejemplos
Consulte el sitio web del modelo de calidad Q42 para obtener ejemplos detallados de los requisitos de calidad.

Más información
Len Bass, Paul Clements, Rick Kazman: “Arquitectura de software en la práctica”, 4.ª edición, Addison-Wesley, 2021.
<describa escenarios de calidad aquí>

Véase también
Desde enero de 2023, arc42 ofrece un modelo de calidad pragmático que propone etiquetar los requisitos de calidad con hashtags o etiquetas como #flexible, #eficiente, #utilizable, #operable, #testable, #seguro, #seguro” y #confiable. 0 Q42, el modelo de calidad arc42, con ocho etiquetas para las calidades del sistema

## 11. Riesgos y deuda técnica

Contenido
Una lista de riesgos técnicos o deudas técnicas identificados, ordenados por prioridad

Motivación
“ La gestión de riesgos es gestión de proyectos para adultos ” (Tim Lister, Atlantic Systems Guild).

Este debe ser su lema para la detección y evaluación sistemática de riesgos y deudas técnicas en la arquitectura, que serán necesarias para las partes interesadas de la gestión (por ejemplo, gerentes de proyectos, propietarios de productos) como parte del análisis general de riesgos y la planificación de la medición.

Forma
Listado de riesgos y/o deudas técnicas, probablemente incluyendo medidas sugeridas para minimizar, mitigar o evitar riesgos o reducir deudas técnicas.

Ejemplos
Ejemplo de riesgo: Comprobador de integridad de HTML
Ejemplo de riesgo: TrafficPursuitUnit
<insertar lista o tabla de problemas conocidos, riesgos o deuda técnica>

## 12. Glosario

Contenido
Los términos técnicos y de dominio más importantes que utilizan las partes interesadas cuando discuten el sistema.

También puede ver el glosario como fuente de traducciones si trabaja en un entorno multilingüe (es decir, en modelos de desarrollo offshore).

Motivación
Debe definir claramente sus términos, para que todos los interesados

tienen una comprensión idéntica de estos términos
no utilice sinónimos ni homónimos
Forma
Una tabla simple con columnas <Término> y <Definición>
Potencialmente más columnas para traducciones
Término Definición
<Término-1> <definición-1>
<Termino-2> <definición-2>
Ejemplos
Glosario de ejemplo: Comprobador de integridad de HTML (tabular)
<insertar tabla de glosario (y opcionalmente traducción)>
