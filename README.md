# Análisis Inicial y Requerimientos - Sistema "Trotamundos"

Este documento captura el análisis inicial del sistema Trotamundos, definiendo el alcance, los actores involucrados, los casos de uso priorizados y los atributos de calidad que guiarán el diseño arquitectónico (ADD).

---

## Actores Externos

* **Viajero:** Usuario final web/móvil.
* **Sistemas de terceros:** Aerolíneas, hoteles, autos, trenes, autobuses.
* **Proveedores de correo electrónico.**
* **Agencia de viajes preferida** del usuario.
* **Equipo de datos** (Analítica).
* **Redes sociales** (Para compartir itinerarios).
* **Otros usuarios invitados**, que ven itinerarios compartidos.

---

## Casos de Uso (UC)

### Casos de Uso Primarios (Drivers Arquitectónicos)
Estos casos de uso son esenciales para el modelo de negocio y condicionan fuertemente la estructura macro de la arquitectura.

* **UC1: Sondear y escanear correos para agregar reservas automáticamente.**
  * *Justificación:* Es muy relevante para el negocio, de hecho, la idea es "único punto de verdad... mitigar la frustración de rastrear múltiples aplicaciones y bandejas de correo". Hay que sondear una enorme cantidad de correos dentro de una ventana de 5 minutos, con acceso sensible a datos personales.
* **UC4: Visualizar reservas agrupadas por viaje.**
  * *Justificación:* Es el producto en sí, lleva a cabo la idea presentada en el UC1. Es el camino de lectura que utilizan los usuarios, condicionando Rendimiento, Escalabilidad y Disponibilidad.
* **UC7: Compartir un itinerario con personas designadas.**
  * *Justificación:* En el texto se menciona que "... debe garantizarse... permitir el uso compartido de itinerarios asegurando que solo personas específicas designadas puedan visualizarlo", por lo tanto, es algo con lo que el sistema debe contar, y es muy importante la parte de seguridad.
* **UC8: Consultar analíticas de viajes (Actor: Equipo de datos).**
  * *Justificación:* Importante, primordial para los stakeholders e interesados en el sistema. Son consultas pesadas que pueden competir con las del usuario y afectar su latencia.
* **UC9: Obtener detalles, actualizaciones y cancelaciones de reservas desde los sistemas de terceros por API.**
  * *Justificación:* Importante para el sistema, de acá se desprende el QA de Performance cuando menciona que "Las actualizaciones de viaje deben presentarse en la aplicación dentro de los 5 minutos posteriores a su generación por la fuente externa...".

### Casos de Uso Secundarios
Funcionalidad estándar o agregados que se apoyan sobre la estructura de los casos de uso primarios.

* **UC2: Filtrar y gestionar listas de remitentes seguros (whitelists).**
  * *Justificación:* No es tan esencial para el negocio, es importante para el usuario. Es lógica de filtrado sobre algo que UC1 ya define.
* **UC3: Agregar, actualizar, eliminar reservas manualmente.**
  * *Justificación:* Importante para el usuario, además de que el sistema se encargue de hacerlo de forma automática (UC1). Es una operación estándar sobre datos que ya existen.
* **UC5: Archivar o eliminar viajes completados.**
  * *Justificación:* No es estrictamente necesario, pero sí importante para llevar un mejor control y mantener una interfaz más limpia.
* **UC6: Integrar la resolución de problemas con la agencia preferida del usuario.**
  * *Justificación:* Importante para el negocio, pero es otra integración con un tercero que no agrega decisiones estructurales nuevas.

---

## Restricciones (Constraints)
Condiciones innegociables impuestas sobre el diseño del sistema.

* **CON1:** Interfaz centrada en el viaje, accesible vía web y dispositivo móvil.
* **CON2:** Uso de APIs estándar para integrarse con sistemas de terceros.

## Preocupaciones Arquitectónicas (CRN)
Temas transversales que la arquitectura debe resolver sin afectar los flujos principales.

* **CRN1:** Recolección de datos analíticos de viajes.

---

## Atributos de Calidad (QA)
Cualidades sistémicas que la arquitectura debe garantizar.

* **Rendimiento:** Actualizaciones de viaje visibles en < 5 minutos desde la fuente externa. Tiempos de respuesta: Web < 800 ms, Móvil < 1.4 s.
* **Disponibilidad:** Tolerancia máxima de 5 minutos de inactividad no planificada al mes. Uso global y accesible en todo momento.
* **Escalabilidad:** Soportar 15 millones de cuentas, 2 millones de activos semanales y picos dramáticos.
* **Interoperabilidad:** Integración fluida con aerolíneas/hoteles vía APIs estándar, proveedores de correo y redes sociales.
* **Seguridad y Privacidad:** Acceso autorizado a correos y control de visibilidad al compartir itinerarios.
* **Evolucionabilidad y Mantenibilidad:** Preparado para integrar nuevos medios de transporte en el futuro y garantizar trazabilidad arquitectónica.
* **Usabilidad:** Uso de capacidades nativas (GPS).
* **Internacionalización:** Soporte multiregión.

---

## Escenarios de Calidad (SEI)

### Escenario 1: Rendimiento (Actualizaciones)
* **Fuente del Estímulo:** Sistema externo (por ejemplo, una aerolínea).
* **Estímulo:** Se genera un cambio en una reserva (por ejemplo, una cancelación de vuelo).
* **Artefacto:** Subsistema que obtiene y procesa las actualizaciones externas.
* **Entorno:** Operación normal y también durante un pico de carga.
* **Respuesta:** El sistema detecta el cambio, lo procesa y lo muestra en el itinerario del viajero.
* **Medida de Respuesta:** La actualización es visible en la aplicación en menos de 5 minutos desde que se generó en la fuente externa.

### 2. Rendimiento (respuesta web < 800 ms)
* **Fuente:** Usuario.
* **Estímulo:** Un viajero solicita su panel de viajes.
* **Artefacto:** El subsistema que controla las reservas.
* **Entorno:** Operación normal y pico de carga.
* **Respuesta:** El sistema le muestra al usuario sus reservas.
* **Medida:** Visible en, a lo sumo, 800 ms.

### 3. Rendimiento (primer despliegue móvil < 1.4 s)
* **Fuente:** Usuario.
* **Estímulo:** El usuario quiere ingresar a la aplicación desde el teléfono.
* **Artefacto:** El subsistema que se encarga de mostrar la interfaz.
* **Entorno:** Operación normal y en pico de carga.
* **Respuesta:** El sistema muestra la interfaz de usuario.
* **Medida:** Visible en menos de 1.4 segundos.

### 4. Disponibilidad (uso global y accesible en todo momento)
* **Fuente:** Interna (infraestructura, falla de un servidor) o externa (caída de un proveedor).
* **Estímulo:** Ocurre una falla en un componente.
* **Artefacto:** El sistema.
* **Entorno:** Operación normal y pico de carga.
* **Respuesta:** El sistema detecta la falla, y los usuarios siguen siendo atendidos desde componentes sin interrupción visible.
* **Medida:** Inactividad no planificada acumulada <= 5 minutos por mes.

### 5. Escalabilidad
* **Fuente:** Los viajeros (2 millones de usuarios activos semanales) y los sistemas externos que envían actualizaciones.
* **Estímulo:** La carga sube de golpe por una disrupción climática masiva, y muchos viajeros consultan sus reservas y llegan muchas actualizaciones a la vez.
* **Artefacto:** El sistema completo.
* **Entorno:** Pico de carga, con la base de 15 millones de cuentas.
* **Respuesta:** El sistema agrega capacidad automáticamente y mantiene el servicio sin degradarlo.
* **Medida:** Soporta N veces la carga normal (por ejemplo, 5 veces), con respuesta web <= 800 ms y actualizaciones visibles en menos de 5 minutos.

### 6. Seguridad (acceso a los correos)
* **Fuente:** Un atacante externo, o un usuario que intenta acceder a la casilla de otro.
* **Estímulo:** Intenta leer los correos de una cuenta sin la autorización del titular.
* **Artefacto:** El subsistema de integración con proveedores de correo (y las credenciales o tokens que guarda).
* **Entorno:** Operación normal y pico de carga.
* **Respuesta:** El sistema verifica la autorización del titular, deniega el acceso, y registra y notifica el intento.
* **Medida:** El 100% de los accesos no autorizados es rechazado, con 0 correos expuestos.

### 7. Seguridad (itinerarios compartidos)
* **Fuente:** Una persona no designada (con o sin cuenta).
* **Estímulo:** Intenta ver un itinerario compartido con otras personas.
* **Artefacto:** El subsistema que controla el acceso a los itinerarios compartidos.
* **Entorno:** Operación normal y pico de carga.
* **Respuesta:** El sistema verifica que la persona esté designada, deniega la visualización y registra el intento.
* **Medida:** El 100% de los intentos de personas no designadas es rechazado, no se expone ningún dato del itinerario.

### 8. Interoperabilidad
* **Fuente:** Un sistema externo (por ejemplo, una aerolínea) que envía una actualización por su API estándar.
* **Estímulo:** Llega un mensaje con el detalle de una reserva (cambio o cancelación).
* **Artefacto:** El subsistema de integración con terceros.
* **Entorno:** Operación normal y pico de carga.
* **Respuesta:** El sistema interpreta el mensaje y lo incorpora. Si es inválido, lo rechaza y lo registra.
* **Medida:** 100% de los mensajes válidos procesados correctamente, y 100% de los inválidos rechazados y registrados.

### 9. Evolucionabilidad
* **Fuente:** Interna, expansión del sistema.
* **Estímulo:** Se agregan nuevos medios de transporte.
* **Artefacto:** El subsistema encargado de integrar los distintos medios de transporte.
* **Entorno:** Operación normal y pico de carga.
* **Respuesta:** Se incorpora el nuevo medio sin modificar los existentes, se prueba y se despliega.
* **Medida:** Ningún usuario se ve afectado en el uso de la aplicación mientras se trabaja en evolucionar el sistema.

### 10. Internacionalización
* **Fuente:** Nuevos usuarios ubicados en distintas partes del mundo.
* **Estímulo:** Usan el sistema desde sus países.
* **Artefacto:** El sistema completo.
* **Entorno:** Operación normal y pico de carga.
* **Respuesta:** El sistema verifica que cada usuario es atendido desde su región con su idioma y sus formatos.
* **Medida:** Se mantienen los tiempos de <= 800 ms para web y 1.4 s para móvil.

### 11. Usabilidad (GPS)
* **Fuente:** Usuario.
* **Estímulo:** Quiere ver su ubicación respecto de un punto de su itinerario (por ejemplo, cómo llegar al hotel).
* **Artefacto:** La aplicación móvil.
* **Entorno:** Operación normal, en un dispositivo con GPS.
* **Respuesta:** La aplicación solicita el permiso, obtiene la ubicación y muestra la información en el contexto del viaje.
* **Medida:** Completa la tarea y obtiene la ubicación en pocos segundos.

---

## Tabla de Priorización de Drivers

| ID | DRIVER | IMPORTANCIA | DIFICULTAD | JUSTIFICACIÓN |
| :--- | :--- | :--- | :--- | :--- |
| **UC1** | Agregar reservas automáticamente. | ALTA | ALTA | Es el negocio en sí, lo mas importante y el objetivo. |
| **UC2** | Filtrar listas de remitentes. | BAJA | BAJA | Si no estuviese el negocio sigue funcionando, quizás con una funcionalidad menos, pero funciona. |
| **UC3** | Agregar, actualizar y eliminar reservas manualmente. | BAJA | BAJA | No tan necesario porque también se hace de forma automática. |
| **UC4** | Visualizar reservas agrupadas. | ALTA | BAJA | Primordial para el negocio, es uno de los puntos importantes para reducir la frustración de los clientes. La funcionalidad es simple pero la dificultad viene dada por QA2, QA3 y QA5. |
| **UC5** | Archivar o eliminar viajes completados. | BAJA | BAJA | Si no estuviese el negocio existe igual, se puede hacer un filtrado donde los viajes completados quedan al final y los actuales al inicio. |
| **UC6** | Integración con agencia preferida. | MEDIA | BAJA | Importante por satisfacción de usuario, sigue con la idea de tener todo en un mismo lugar. |
| **UC7** | Compartir itinerario con designados. | ALTA | MEDIA | Importante por los controles de seguridad que deben hacerse. Reutiliza el patrón de integración del UC9. |
| **UC8** | Consultar analíticas de viajes. | ALTA | MEDIA | Como stakeholder o parte del equipo de datos es muy importante. Puede generar consultas pesadas que contrastan con la latencia de los usuarios. |
| **UC9** | Obtener detalles, actualizaciones y cancelaciones de reservas. | ALTA | ALTA | Importante para el cliente, sin esto el negocio perdería mucha fuerza. |
| **QA1** | Rendimiento (actualizaciones) | ALTA | ALTA | Importante para mantener toda la información actualizada y con el menor retraso posible. |
| **QA2** | Rendimiento (web) | ALTA | MEDIA | Importante por la velocidad y el volumen de usuarios, siendo el camino que usan todos. |
| **QA3** | Rendimiento (móvil) | ALTA | MEDIA | Idem. |
| **QA4** | Disponibilidad. | ALTA | ALTA | Importante por satisfacción de usuario, 5 minutos por mes de inactividad y uso global. |
| **QA5** | Escalabilidad. | ALTA | ALTA | Importante para conocer los límites del sistema y poder expandirlos en caso de ser necesario, es algo a tener en cuenta desde el principio. |
| **QA6** | Seguridad (correos) | ALTA | ALTA | Importante porque es de lo más relevante del negocio. |
| **QA7** | Seguridad (itinerarios) | ALTA | MEDIA | Importante por ser algo que el sistema debe garantizar, pero se puede implementar mediante tokens de autorización. |
| **QA8** | Interoperabilidad. | ALTA | ALTA | Importante por el tema de reenvío de mensajes con terceros, permitiendo que todo esté en un mismo lugar. |
| **QA9** | Evolucionabilidad. | MEDIA | MEDIA | Importante para los interesados para prevenir futuros dolores de cabeza, no tanto para el usuario porque no conoce hasta donde quiere escalar el sistema. |
| **QA10** | Internacionalización. | MEDIA | ALTA | Importante por la globalización, implica decidir donde viven los datos y mantener la latencia de cada región. |
| **QA11** | Usabilidad. | BAJA | BAJA | Importante por ser relevante para el usuario, es una capacidad del dispositivo sin impacto estructural. |
| **CRN1** | Recolección de datos analíticos. | MEDIA | MEDIA | Es un tema transversal a todo el negocio. |
