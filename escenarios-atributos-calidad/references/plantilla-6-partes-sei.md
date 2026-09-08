# La plantilla de 6 partes del SEI (escenario de atributo de calidad)

Base: Bass, Clements, Kazman — *Software Architecture in Practice*, 4ta ed., Sección 3.3.

Un requisito de calidad expresado como "el sistema debe ser rápido" o "el sistema debe ser seguro" no es verificable ni testeable. El SEI propone expresar cada requisito de calidad como un **escenario de 6 partes**, que sí es concreto y medible. Esta es la definición de cada parte, con las preguntas que ayudan a completarla.

## 1. Fuente del estímulo (stimulus source)
Es la entidad que generó el estímulo: puede ser un humano, otro sistema, un sensor, un componente interno, el propio sistema, etc.
- Pregunta guía: **¿de dónde viene el evento?**
- Importa porque el origen puede cambiar cómo el sistema debería tratar el estímulo (ej: un pedido de un usuario autenticado se trata distinto que uno de un usuario anónimo).

## 2. Estímulo (stimulus)
Es la condición o evento que llega al sistema y dispara la necesidad de una respuesta. Es distinto según el atributo: para rendimiento es la llegada de un evento/carga; para disponibilidad es una falla; para seguridad es un ataque o intento de acceso; para modificabilidad es un pedido de cambio; para usabilidad es una acción del usuario.
- Pregunta guía: **¿qué es lo que ocurre?**

## 3. Artefacto (artifact)
Es la parte del sistema que recibe/es afectada por el estímulo: puede ser todo el sistema, un subsistema, un componente específico, una colección de componentes.
- Pregunta guía: **¿a qué parte del sistema le llega esto?**
- Cuanto más preciso, mejor: no es lo mismo "el sistema" que "el módulo de autenticación".

## 4. Ambiente (environment)
Es el conjunto de circunstancias en las que ocurre el escenario: puede ser un estado operativo normal, sobrecarga, modo de arranque, modo degradado, en desarrollo/testing, etc.
- Pregunta guía: **¿en qué condiciones/estado está el sistema cuando esto pasa?**
- Es fácil de omitir, pero cambia mucho la respuesta esperada (la misma falla en operación normal vs. en modo degradado puede requerir respuestas distintas).

## 5. Respuesta (response)
Es la actividad que el sistema (o los desarrolladores, si es un atributo de tiempo de desarrollo como modificabilidad o testeabilidad) debe llevar a cabo tras el estímulo.
- Pregunta guía: **¿qué tiene que hacer el sistema (o el equipo) en respuesta?**

## 6. Medida de la respuesta (response measure)
Es la forma cuantificable de verificar si la respuesta fue satisfactoria. Es la parte más importante para que el escenario sea testeable, y también la que más frecuentemente se omite o se deja vaga.
- Pregunta guía: **¿cómo se mide el éxito? ¿con qué número/umbral?**
- Ejemplos de buenas medidas: "en menos de 2 segundos", "con 99.99% de disponibilidad", "sin pérdida de datos", "en menos de 3 horas-persona de esfuerzo", "el 90% de los usuarios completa la tarea sin ayuda".
- Una respuesta sin medida cuantificable (ej: "el sistema debe responder rápido") **no es un escenario completo**, aunque tenga las otras 5 partes.

## Señales de que un escenario está incompleto

Un escenario suele estar incompleto cuando:
- Falta explícitamente alguna de las 6 partes.
- La respuesta está descripta pero sin medida cuantificable (muy común: "el sistema debe recuperarse rápido" sin decir en cuánto tiempo).
- El ambiente no está especificado y el estímulo podría comportarse distinto según el estado del sistema (ej: no es lo mismo una falla durante operación normal que durante un pico de carga).
- El artefacto es demasiado genérico ("el sistema") cuando el enunciado en realidad sugiere un componente específico.
- La fuente del estímulo es ambigua cuando podría ser relevante distinguir (ej: "un usuario" sin aclarar si es un usuario autenticado, un administrador, un sistema externo).

No todo escenario necesita las 6 partes con el mismo nivel de detalle en toda circunstancia (el propio libro aclara que a veces se omiten partes en etapas tempranas de elicitación), pero para considerarlo "completo" en el sentido de que ya se puede diseñar y testear contra él, las 6 partes deben estar presentes y ser lo suficientemente concretas — especialmente la medida de la respuesta.
