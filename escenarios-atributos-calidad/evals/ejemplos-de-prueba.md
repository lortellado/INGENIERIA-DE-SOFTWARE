# Ejemplos usados para testear la skill `escenarios-atributos-calidad`

Acá dejamos registradas las pruebas que hicimos antes de entregar la skill. La consigna del TP pide explícitamente testearla con ejemplos conocidos, así que decidimos armar un set chico pero representativo: un caso por cada uno de los tres análisis que tiene que hacer la skill (identificar el atributo, chequear si el escenario está completo, y armar el árbol de utilidad), y sumamos un caso extra —la Prueba 3— usando un escenario que ya está publicado en el libro de la materia, para poder comparar la salida contra algo conocido y no solo confiar en nuestro propio criterio.

La skill no salió bien a la primera. La fuimos ajustando en varias vueltas a medida que la probábamos con enunciados propios (no solo con los casos "formales" de este documento), y cada vez que encontramos algo raro lo documentamos acá para que quede el rastro de qué se corrigió y por qué.

## Iteración 2: la skill no encadenaba los tres análisis

Después de la primera tanda de pruebas (la que se detalla más abajo), nos pusimos a probar la skill con enunciados nuestros y ahí saltó el problema: si le pasábamos un enunciado informal, la skill hacía **uno o dos** de los tres análisis, pero no los tres juntos. Había que pedirle expresamente cada paso por separado, lo cual no era la idea.

¿Por qué pasaba esto? En la primera versión del `SKILL.md` habíamos modelado "Modo A", "Modo B" y "Modo C" como si fueran caminos alternativos —se elegía uno según el tipo de input que llegaba—. Un enunciado informal terminaba disparando nada más que el Modo A, y ahí se cortaba.

Para solucionarlo, reescribimos el `SKILL.md` de forma que, frente a un enunciado informal (que pasa a ser el comportamiento por defecto), los tres análisis se ejecuten uno atrás del otro y en una sola respuesta, como si fueran 4 pasos de un mismo flujo:

1. Identificar qué atributo o atributos de calidad están en juego.
2. Chequear si el escenario está completo, comparándolo contra el enunciado original. En este flujo automático el chequeo ya no frena la respuesta: si falta algo, la skill elige la opción más razonable entre las alternativas posibles, lo deja explícito como supuesto, y sigue adelante en vez de quedarse esperando que el usuario responda.
3. Armar la tabla completa de 6 partes.
4. Ubicar el escenario dentro de un árbol de utilidad acotado (Utilidad → atributo → refinamiento → el escenario recién armado, con su etiqueta H/M/L).

El comportamiento "bloqueante" original —avisar qué falta, dar opciones y esperar a que el usuario elija antes de generar nada— no lo sacamos, pero pasó a ser una excepción: solo se activa si el usuario pide puntualmente ese chequeo sobre un escenario ya armado (por ejemplo, preguntando directamente "¿está completo este escenario?"), o si pide de forma explícita que no se asuma nada sin confirmar antes. Lo mismo con el árbol de utilidad "suelto" (sin partir de un enunciado puntual, para todo un sistema): sigue disponible, pero como caso aparte.

Volvimos a correr la Prueba 1 después de este arreglo para confirmar que ahora sí funcionaba (está más abajo, en "Prueba 1 — re-test post-fix").

## Iteración 3: el árbol de utilidad tenía que ser completo, no de una sola rama

Revisando el resultado de la Iteración 2 nos dimos cuenta de otra cosa: el Paso 4 armaba un árbol con una sola rama, la del atributo que se había detectado en el Paso 1, cuando en realidad un árbol de utilidad (Sección 19.4 del libro) tiene que cubrir varios atributos del sistema, no uno solo. Y la consigna del TP también lo pide así.

Corregimos el Paso 4 para que el árbol siempre salga completo: la skill propone entre 3 y 5 atributos relevantes según el tipo de sistema del que se esté hablando (no solo el que detectó en el Paso 1), reutiliza el escenario que ya armó en el Paso 3 como la hoja de ese atributo, y para los demás atributos agrega escenarios-hoja propuestos por ella misma. Todas las hojas quedan etiquetadas en H/M/L. Este mismo criterio se aplica también cuando se pide el árbol "suelto", sin un enunciado de base.

Volvimos a correr la Prueba 1 una vez más para chequear esta segunda corrección (ver "Prueba 1 — re-test 2").

## Iteración 4: nos pasamos del límite de caracteres que pide Claude.ai

Cuando quisimos subir la skill a **Settings > Skills** de claude.ai —la idea era que quedara guardada ahí y no tener que reenviar el `SKILL.md` en cada chat nuevo— nos encontramos con que el campo `description` del frontmatter tenía 1026 caracteres. La plataforma pide como máximo 200 (está en la documentación oficial de Claude, en support.claude.com/en/articles/12512198-how-to-create-custom-skills), así que directamente no iba a andar como debía.

Lo arreglamos acortando `description` a 200 caracteres justos, dejando lo esencial para que la skill se dispare en el momento correcto (enunciado de arquitectura, ASR, atributos de calidad). Todo el detalle que antes estaba ahí —la lista larga de atributos, ATAM, etc.— lo movimos a una sección nueva al principio del cuerpo del `SKILL.md` ("Cuándo se activa esta skill"), que no tiene ese límite de caracteres.

---

## Prueba 1 — identificar el atributo y armar la tabla (primera versión, antes de la Iteración 2)

Acá queríamos ver si, dada una situación contada en criollo (sin ninguna estructura de escenario), la skill era capaz de identificar bien el atributo de calidad, discutir otros candidatos si correspondía, y armar la tabla completa aclarando los supuestos que tuvo que hacer.

Le pasamos:
> "Un sistema de cajero automático debe ser fácil de usar por una persona mayor."

Y esto fue lo que hizo: identificó Usabilidad como atributo principal, mencionó Seguridad como candidato secundario y explicó por qué terminó descartándolo, armó la tabla completa de 6 partes con un escenario concreto (retiro de efectivo en un ATM, usuario mayor sin experiencia previa), y dejó bien aclarados los supuestos que tuvo que inventar porque el enunciado no los daba (qué operación, qué umbrales de tiempo y de errores).

En un primer momento lo dimos por bueno. El problema apareció después, cuando seguimos probando la skill con enunciados nuestros fuera de este set de pruebas "formal": nos dimos cuenta de que identificar el atributo y tirar la tabla era, en realidad, apenas uno de los tres análisis que tenía que hacer, y que no estaba encadenando sola el chequeo de completitud ni el árbol de utilidad. Toda esta historia está contada en la Iteración 2, al principio del documento.

### Prueba 1 — segunda vuelta, después del primer arreglo

Acá lo que queríamos confirmar era que, con la corrección ya aplicada, el mismo input disparara los tres análisis uno atrás del otro, en una sola respuesta, y no solo la identificación con su tabla.

Usamos el mismo input de antes: *"Un sistema de cajero automático debe ser fácil de usar por una persona mayor."*

Con el `SKILL.md` corregido, la respuesta trajo los cuatro pasos juntos: primero identificó Usabilidad (mencionando y descartando Seguridad, igual que antes), después chequeó explícitamente que ninguna de las 6 partes venía dada en el enunciado y mostró, para cada una, qué opciones consideró y cuál eligió como supuesto —sin frenarse a esperar que le confirmáramos nada—, siguió con la tabla completa ya armada con esos supuestos resueltos, y cerró ubicando el escenario en un árbol de utilidad, etiquetado (H, M) con su justificación, ofreciendo además ampliarlo con otros atributos del sistema.

Esto ya lo aprobamos: las cuatro salidas venían juntas, en una sola respuesta, así que el problema original quedaba resuelto. Lo que notamos, eso sí, es que el árbol que armó en el Paso 4 tenía una sola rama (la de Usabilidad) — y ahí fue cuando surgió la Iteración 3.

### Prueba 1 — tercera vuelta, con el árbol de utilidad ya completo

Esta vez queríamos chequear que, después de corregir la Iteración 3, el Paso 4 armara el árbol completo del sistema (con varios atributos) y no se quedara solo con el que había detectado en el Paso 1.

Mismo input de siempre: *"Un sistema de cajero automático debe ser fácil de usar por una persona mayor."*

Y ahora sí, el árbol salió con 4 atributos relevantes para un cajero automático:

```
Utilidad
├── Usabilidad
│   └── Facilidad de aprendizaje de usuarios sin experiencia
│       └── [Escenario del Paso 3: retiro de efectivo por un usuario mayor] (H, M)
├── Seguridad
│   └── Autenticación segura sin fricción para usuarios con baja alfabetización digital
│       └── [Escenario] Bloqueo de tarjeta solo tras el 3er intento fallido de PIN,
│           con explicación clara al usuario. (H, H)
├── Disponibilidad
│   └── Recuperación ante falla del cajero durante una operación
│       └── [Escenario] Pérdida de conexión durante un retiro; el sistema revierte
│           la transacción sin descontar el monto. (H, H)
└── Rendimiento
    └── Tiempo de respuesta ante cada paso del flujo
        └── [Escenario] Confirmación de operación respondida en menos de 3 segundos. (M, L)
```

La rama de Usabilidad reutilizó el mismo escenario que ya se había armado en el Paso 3, no inventó uno nuevo para esa hoja. Las otras tres ramas sí trajeron escenarios propuestos por la skill, cada uno con su etiqueta H/M/L justificada. Con esto dimos por aprobada la prueba, sin más observaciones.

---

## Prueba 2 — pedirle puntualmente que chequee si un escenario está completo

Esta prueba iba por otro lado: queríamos ver que, cuando uno le pide directamente a la skill que revise si un escenario ya armado está completo (que es la excepción al flujo automático que quedó definida en el `SKILL.md`), no se apure a generar la tabla ni el árbol, sino que primero avise qué falta y dé opciones concretas para completarlo, esperando a que el usuario decida.

Le pasamos:
> "¿Está completo este escenario?: Cuando el servidor falla, el sistema debe notificar al operador."

(Agregamos la pregunta "¿está completo este escenario?" a propósito, para que quedara claro que estábamos pidiendo la excepción del modo bloqueante. Si hubiéramos mandado el mismo texto sin la pregunta, según cómo quedó definida la skill después de la Iteración 2, se habría disparado el flujo automático completo en vez del chequeo puntual — de hecho la Prueba 3 es justamente un caso así.)

La skill marcó el escenario como incompleto, identificó bien que Estímulo y Respuesta sí estaban (aunque de forma parcial), y señaló que faltaban o eran ambiguas la Fuente del estímulo, el Artefacto, el Ambiente y la Medida de la respuesta. Para cada una de esas partes dio 2 o 3 opciones concretas, nada de sugerencias genéricas tipo "definí mejor esto". Y, como se esperaba, no generó ni la tabla ni el árbol de utilidad — se quedó esperando que eligiéramos cómo completar el escenario. Aprobado sin observaciones.

---

## Prueba 3 — el flujo completo puesto a prueba con un ejemplo del propio libro

Acá la idea era otra: correr el flujo automático completo (identificación, chequeo, tabla y árbol) sobre un escenario que ya está publicado en la bibliografía de la materia, sin pedirle nada puntual a la skill. Nos servía para dos cosas a la vez: comprobar que no inventara supuestos de más cuando el enunciado ya traía toda la información (el Paso 2 tiene que darse cuenta de que ahí no falta nada), y ver si igual aportaba algo de valor como arquitecto, más allá de simplemente transcribir lo que ya estaba escrito.

El ejemplo lo sacamos de Bass, Clements y Kazman, *Software Architecture in Practice*, 4ta ed., capítulo 4 (Disponibilidad), Figura 4.1:

> "Un servidor en una granja de servidores falla durante la operación normal, y el sistema informa al operador y continúa operando sin downtime."

Identificó Disponibilidad sin dudar demasiado (descartó Safety porque no había ningún indicio de daño físico de por medio). En el chequeo de completitud se dio cuenta de que las 6 partes ya estaban ahí, explícitas o fáciles de inferir del propio enunciado —fuente, estímulo, artefacto, ambiente, respuesta y medida—, así que no tuvo que asumir nada. Ahora bien, sí hizo una observación por su cuenta: dijo que "sin downtime" es una medida un poco débil por ser binaria, y sugirió reforzarla con algo como el MTTR, enlazando la idea con los conceptos de MTBF/MTTR que aparecen en ese mismo capítulo del libro. Esto no le impidió seguir con el resto del flujo. Armó la tabla con los datos que ya estaban en el enunciado, y cerró con el árbol de utilidad completo (Disponibilidad, Rendimiento, Seguridad y algún otro atributo relevante para una granja de servidores), usando el escenario recién armado como la hoja de Disponibilidad —etiquetada (H, H)— y sumando propuestas propias para las demás ramas.

Esta prueba nos dejó bastante conformes: es la que mejor muestra que la skill está atada a la bibliografía real de la cátedra, y confirma que el chequeo de completitud no inventa cosas de la nada cuando el enunciado ya alcanza.

---

## Prueba 4 — pedirle el árbol de utilidad sin partir de ningún escenario puntual

Por último quisimos probar el caso en el que a uno directamente le interesa el árbol de utilidad de todo un sistema, sin dar un enunciado específico ni decir qué atributos usar. Acá esperábamos que la skill reconociera esto como la excepción "árbol suelto" y propusiera ella misma los atributos que le parecieran razonables.

Le dijimos:
> "Necesito armar un árbol de utilidad para un sistema de e-commerce."

Y propuso cuatro atributos que tienen sentido para un e-commerce —Rendimiento, Disponibilidad, Seguridad y Usabilidad—, aclarando de entrada que era una propuesta suya porque no le habíamos dado ninguna pista. Para cada atributo armó un refinamiento y al menos un escenario-hoja, etiquetó todo en H/M/L, y marcó como más prioritarias las hojas de Disponibilidad y Seguridad de pagos (ambas H/H). También ofreció expandir cualquier hoja a la tabla completa si queríamos más detalle. Sin observaciones.

---

## Cómo quedó la validación en general

En total fueron cuatro iteraciones. Arrancamos con 4 pruebas que cubrían cada análisis por separado, y todas pasaron bien individualmente — el problema apareció recién cuando empezamos a usar la skill "de verdad", fuera de este set formal, y notamos que no encadenaba los tres análisis solos ante un enunciado informal (Iteración 1). Corregimos eso reescribiendo el flujo como una secuencia de 4 pasos que se ejecutan siempre juntos (Iteración 2), y volvimos a correr la Prueba 1 para confirmarlo. Ahí notamos un segundo problema: el árbol de utilidad quedaba limitado a un solo atributo (Iteración 3), así que lo corregimos para que siempre salga completo, con varios atributos relevantes del sistema. Por último, al preparar todo para subirlo a Claude.ai nos topamos con que el campo `description` se pasaba largo del límite de 200 caracteres que pide la plataforma, y lo acortamos (Iteración 4).

Con estas cuatro vueltas, entendemos que la skill ya cubre lo que pide la consigna del TP —generar escenarios con el template de 6 partes, chequear su completitud, y armar el árbol de utilidad completo— tanto en el flujo automático como en los casos puntuales, y queda lista para subirse a Claude.ai sin problemas de formato.
