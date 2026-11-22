# Guía de uso del chat: qué escribirle al asistente

Sirve igual para `python3 -m trotamundos_asistente chat --usuario ana` (consola) que para el endpoint
`POST /v1/asistente/mensajes` del servidor. Usuarios de prueba: **ana** (2 reservas en el viaje «Madrid en
diciembre», con agencia preferida) y **beto** (viaje «Roma en enero», sin agencia preferida).

> El modelo de lenguaje es un **simulador por reglas**: entiende frases simples con palabras clave, no
> lenguaje totalmente libre. Si algo no se entiende, el asistente lo dice y sugiere qué puede hacer.

## Acciones que soporta

| # | Acción | Caso de uso | ¿Necesita confirmación? |
|---|---|---|---|
| 1 | Ver la lista de mis viajes | UC10 | No |
| 2 | Ver el detalle de un viaje (sus reservas) | UC10 | No |
| 3 | Proponer un cambio de fecha en una reserva (inicio o fin de un vuelo o alojamiento) | UC11 | **Sí**: se confirma o cancela aparte |
| 4 | Recibir una guía para un problema menor (contraseña, correo, notificaciones, carga manual) | UC12 | No |
| 5 | Ser derivado a la agencia (pedidos que debe resolver una persona) | UC13 | No |

Todo lo demás (borrar viajes, cancelar reservas, pagos, ver datos de otras personas) **no está soportado**:
lo riesgoso se deriva a una persona y el resto responde «No te entendí».

## Ejemplos por acción

### 1. Ver mis viajes
- `mis viajes`
- `ver mis viajes` · `mostrame mis viajes`
- `qué tengo reservado` · `mis reservas` · `mis vuelos` · `mis vacaciones` · `mi próximo viaje`

### 2. Ver el detalle de un viaje
Por nombre o por identificador (los dos funcionan):
- `mostrame el viaje de Madrid` · `hotel de Madrid`
- `mostrame el viaje v-ana-1`

### 3. Cambiar la fecha de una reserva
Hay que decir **qué reserva** (hotel/alojamiento o vuelo), **qué fecha** (entrada/inicio/ida o salida/fin/vuelta)
y **la fecha nueva** (`AAAA-MM-DD` o `DD/MM/AAAA`). El viaje se indica por nombre o ID (si hay uno solo, puede omitirse).
- `cambiá la salida del hotel de Madrid al 30/12/2026`
- `cambiá la salida del hotel del viaje v-ana-1 al 2026-12-30`
- `mover la ida del vuelo al 17/12/2026`

El asistente **no aplica nada** hasta que se confirme:
- En la consola, pregunta `¿Confirmás el cambio? [s/n]`.
- Por la API: `POST /v1/asistente/acciones/{accionId}/confirmar` (o `/cancelar`). La confirmación vence a los 5 minutos y sirve una sola vez.

Casos que se rechazan con explicación: fecha de inicio posterior al fin, fecha igual a la actual, fecha inválida o viaje/reserva inexistente.

### 4. Guías de ayuda
- `olvidé mi contraseña` → guía G-01
- `mi reserva del correo no aparece` → G-02
- `cómo configuro las notificaciones` → G-03
- `quiero cargar una reserva a mano` → G-04

### 5. Derivación a la agencia
Se activa con palabras como reembolso, pago, tarjeta, cancelar, emergencia, urgente, reclamo, o con pedidos como
`quiero hablar con una persona`. También si el asistente no te entiende **dos veces seguidas**.
- `necesito un reembolso`
- `quiero cancelar mi vuelo`
- `quiero hablar con una persona`

## Ejemplo de conversación completa (usuario `ana`)

```
ana> mis viajes
asistente> Tus viajes:
- v-ana-1 · Madrid en diciembre (PLANIFICADO, 2026-12-18 a 2026-12-28)

ana> hotel de Madrid
asistente> Madrid en diciembre (PLANIFICADO, 2026-12-18 a 2026-12-28):
- R-A1 · vuelo · Aerolíneas Demo · 2026-12-18 → 2026-12-18 (CONFIRMADA)
- R-A2 · alojamiento · Hotel Gran Vía · 2026-12-18 → 2026-12-28 (CONFIRMADA)

ana> cambiá la salida del hotel de Madrid al 30/12/2026
asistente> Preparé este cambio, pero TODAVÍA NO lo apliqué:
En el viaje «Madrid en diciembre», cambiar la fecha de fin de la reserva de alojamiento (Hotel Gran Vía) del 2026-12-28 al 2026-12-30.
Confirmalo o cancelalo. Tenés 5 minutos.
¿Confirmás el cambio? [s/n] s
asistente> Listo, el cambio fue aplicado.

ana> necesito un reembolso
asistente> Esto lo tiene que resolver una persona. Abrí el caso C-0001 con Agencia Sur; se van a comunicar con vos.
```

## Qué muestran estos mensajes sobre el diseño

| Probá | Respuesta | Escenario |
|---|---|---|
| `mostrame el viaje v-beto-1` (como ana) | `No encontré ese viaje en tu cuenta…` | QA-13: no se ve lo de otra persona |
| `cambiá la entrada del hotel del viaje v-ana-1 al 2027-01-01` | `Con esa fecha el inicio quedaría después del fin…` | UC11: valida antes de proponer |
| `quiero cancelar mi vuelo` (como beto) | `…no tenés una agencia preferida configurada…` | UC13: no inventa un caso |
| `blabla` | `No te entendí bien. Puedo mostrarte tus viajes…` | Dos veces seguidas → derivación |
| cualquier mensaje con `--falla-modelo` | `El asistente no está disponible…` + alternativas | QA-15 (guías y derivación siguen andando) |

## Límites a tener en cuenta
Máximo 1000 caracteres por mensaje, 20 mensajes por minuto por usuario (después responde 429), y el historial
de la conversación se conserva 24 horas.
