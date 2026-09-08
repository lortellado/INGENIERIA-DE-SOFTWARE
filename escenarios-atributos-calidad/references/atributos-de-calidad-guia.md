# Guía de atributos de calidad (Caps. 4–14)

Base: Bass, Clements, Kazman — *Software Architecture in Practice*, 4ta ed. Resumen orientado a ayudar a **identificar qué atributo de calidad está involucrado** en una situación informal (Modo A), y a construir el "general scenario" de cada uno.

Para cada atributo: definición breve, palabras/pistas clave que suelen aparecer en un enunciado, y la forma típica del estímulo y la respuesta según el "general scenario" del libro.

## Disponibilidad (Availability) — Cap. 4
- **Definición**: capacidad del sistema de estar operativo y prestar servicio cuando se lo necesita, incluyendo detectar fallas, repararse y seguir funcionando (posiblemente degradado).
- **Pistas**: falla, caída, no disponible, tiempo de actividad, recuperación, redundancia, tolerancia a fallos, "sigue funcionando aunque...".
- **Estímulo típico**: una falla (de hardware, software, red).
- **Respuesta típica**: detectar la falla, notificar, seguir operando (posiblemente con funcionalidad reducida) o recuperarse.
- **Medida típica**: % de disponibilidad (ej. 99.99%), tiempo de detección de la falla, tiempo de reparación (MTTR).

## Deployability — Cap. 5
- **Definición**: facilidad y predictibilidad con la que el sistema puede pasar a producción (deploy) y, si hace falta, revertirse (rollback).
- **Pistas**: despliegue, release, actualización en producción, rollback, pipeline de CI/CD, downtime en el deploy.
- **Estímulo típico**: una nueva versión lista para desplegar.
- **Respuesta típica**: desplegar sin (o con mínima) interrupción del servicio, permitir rollback si algo falla.
- **Medida típica**: tiempo/esfuerzo del despliegue, cantidad de defectos introducidos, tiempo de rollback.

## Eficiencia energética (Energy Efficiency) — Cap. 6
- **Definición**: uso eficiente de la energía consumida por el sistema (relevante en móviles, IoT, data centers).
- **Pistas**: batería, consumo energético, autonomía, apagar recursos, dispositivos móviles/IoT.
- **Estímulo típico**: recursos ociosos o carga baja/alta.
- **Respuesta típica**: reducir consumo (apagar/reducir frecuencia de recursos) manteniendo un nivel de servicio aceptable.
- **Medida típica**: % de energía ahorrada, impacto en latencia aceptado a cambio del ahorro.

## Integrabilidad (Integrability) — Cap. 7
- **Definición**: facilidad y riesgo de integrar un componente nuevo (propio o de terceros) al sistema.
- **Pistas**: integrar, componente externo, API de terceros, marketplace de componentes, "conectar con otro sistema".
- **Estímulo típico**: aparece un nuevo componente que debe integrarse.
- **Respuesta típica**: integrarlo exitosamente respetando las interfaces existentes.
- **Medida típica**: tiempo/esfuerzo (horas-persona) de integración, cantidad de cambios necesarios en otros componentes.

## Modificabilidad (Modifiability) — Cap. 8
- **Definición**: facilidad, costo y riesgo de hacer un cambio al sistema (agregar, quitar o modificar funcionalidad) sin efectos secundarios no deseados.
- **Pistas**: cambio, mantenimiento, nueva funcionalidad, modificar, extender, portar a otra plataforma.
- **Estímulo típico**: un desarrollador/stakeholder pide un cambio.
- **Respuesta típica**: implementar, testear y desplegar el cambio sin afectar otras partes del sistema.
- **Medida típica**: costo/tiempo del cambio (horas-persona), cantidad de módulos afectados.

## Rendimiento (Performance) — Cap. 9
- **Definición**: capacidad del sistema de responder a tiempo ante eventos, bajo cierta carga.
- **Pistas**: rápido, lento, tiempo de respuesta, throughput, carga, latencia, cantidad de usuarios simultáneos.
- **Estímulo típico**: llegada de uno o más eventos/pedidos (posiblemente con cierta frecuencia o carga).
- **Respuesta típica**: procesar el/los evento(s) dentro de un tiempo aceptable.
- **Medida típica**: latencia (ej. "en menos de 2 segundos"), throughput (ej. "2000 solicitudes en 30 segundos"), tasa de error bajo carga.

## Safety — Cap. 10
- **Definición**: capacidad del sistema de evitar entrar en estados peligrosos que puedan causar daño, lesiones o pérdida de vidas, y de recuperarse o limitar el daño si ocurre.
- **Pistas**: daño físico, lesión, estado peligroso, sistema médico/automotriz/industrial, "puede lastimar a alguien".
- **Estímulo típico**: una falla o condición que podría llevar a un estado inseguro.
- **Respuesta típica**: detectar el estado inseguro, pasar a un modo seguro, notificar, limitar el daño.
- **Medida típica**: tiempo de detección/transición a modo seguro, ausencia de estados peligrosos.

## Seguridad (Security) — Cap. 11
- **Definición**: protección de datos y servicios frente a accesos no autorizados, manteniendo disponibilidad para usuarios legítimos (confidencialidad, integridad, disponibilidad — CIA).
- **Pistas**: ataque, acceso no autorizado, autenticación, autorización, datos sensibles, hackeo, permisos, contraseña.
- **Estímulo típico**: un intento de ataque o acceso (autorizado o no).
- **Respuesta típica**: detectar, resistir, reaccionar y/o recuperarse del intento; mantener la confidencialidad/integridad de los datos.
- **Medida típica**: % de intentos detectados/bloqueados, tiempo de detección, datos comprometidos (debería ser ninguno).

## Testeabilidad (Testability) — Cap. 12
- **Definición**: facilidad con la que el software puede hacer evidentes sus fallas mediante testing.
- **Pistas**: testing, cobertura de tests, encontrar bugs, facilidad de probar un componente.
- **Estímulo típico**: se completa una unidad de desarrollo y se la quiere testear.
- **Respuesta típica**: ejecutar tests que logren cierta cobertura o detección de fallas.
- **Medida típica**: % de cobertura, tiempo para lograr esa cobertura, cantidad de fallas detectadas por test.

## Usabilidad (Usability) — Cap. 13
- **Definición**: facilidad con la que el usuario logra realizar la tarea deseada, y el nivel de soporte que el sistema le da (aprendizaje, eficiencia de uso, manejo de errores, adaptación, satisfacción).
- **Pistas**: fácil de usar, usuario (mayor, novato, no técnico), aprender a usar, interfaz, experiencia de usuario, ayuda, tutorial.
- **Estímulo típico**: un usuario quiere aprender a usar el sistema, usarlo eficientemente, o recuperarse de un error.
- **Respuesta típica**: el sistema facilita la tarea (con ayuda contextual, deshacer, valores por defecto, etc.).
- **Medida típica**: tiempo para completar la tarea, cantidad de errores del usuario, % de usuarios que logran la tarea sin ayuda.

## Otros atributos (Cap. 14)
El libro aclara que esta lista no es exhaustiva: pueden aparecer atributos "a medida" según el dominio (ej. **buildability**, **conceptual integrity**, **development distributability**, o atributos propios de sistemas físicos como peso, tamaño, consumo). Si un enunciado no encaja bien en ninguno de los atributos anteriores, es válido proponer un atributo específico del dominio, siguiendo el mismo proceso: definirlo, dar pistas de estímulo/respuesta, y construir su escenario de 6 partes por analogía con los de arriba.

## Nota sobre solapamientos

Es normal (y está reconocido en el libro) que un mismo enunciado toque más de un atributo — por ejemplo, un ataque de denegación de servicio es simultáneamente un tema de Seguridad y de Disponibilidad. En esos casos, no forzar una única respuesta "correcta": explicitar los candidatos y justificar cuál es el foco principal según el enunciado.
