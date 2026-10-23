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
