# Trotamundos – Prototipo del Asistente Virtual (Iteración 5)

MVP del **Assistant Service** definido en la Iteración 5 de ADD (ADR-031 a ADR-036).
Python 3.9+ **sin dependencias externas** (solo biblioteca estándar).

## Qué es real y qué está simulado

| Real (lo que se diseñó en la Iteración 5) | Simulado (existe desde las Iteraciones 1–4) |
|---|---|
| Conversation API, Conversation Manager | Trip Query, Trip Command |
| Tool Executor (4 herramientas cerradas) | Agency Integration |
| Action Confirmation Manager | API Gateway + Identity Provider (JWT) |
| Escalation Policy, Guide Catalog | Audit Log |
| Language Model Port (timeout, circuit breaker) | **El LLM** (un adaptador por reglas) |
| Data Minimizer, Conversation Store (TTL), límites | |

El modelo es un **adaptador simulado por reglas** (no llama a ningún LLM real). Para usar uno real basta
con escribir otra clase con el método `generar(contexto, herramientas)` (ver `adaptadores.py`); ningún otro
componente cambia (QA-16, hay una prueba que lo verifica).

## Cómo ejecutarlo

Desde esta carpeta:

```bash
python3 -m trotamundos_asistente chat --usuario ana      # chat de consola (usuarios: ana, beto)
python3 -m trotamundos_asistente chat --falla-modelo     # igual, pero con el modelo caído (QA-15)
python3 -m trotamundos_asistente servidor --puerto 8080  # API REST
```

Frases para probar en el chat (como `ana`):

| Escribí… | Qué demuestra |
|---|---|
| `mis viajes` / `mostrame el viaje v-ana-1` | UC10 consulta |
| `cambiá la salida del hotel del viaje v-ana-1 al 30/12/2026` | UC11: propone, **no aplica**; pide confirmar (s/n) |
| `mostrame el viaje v-beto-1` | QA-13: no revela el viaje de otro usuario |
| `olvidé mi contraseña` | UC12: guía del catálogo (sin usar el modelo) |
| `quiero un reembolso` / `quiero cancelar mi vuelo` | UC13: derivación a la agencia (Ana sí tiene; Beto no) |
| `blabla` dos veces seguidas | derivación por incomprensión reiterada |

Con el servidor levantado (otra terminal):

```bash
TOKEN=$(curl -s -X POST localhost:8080/dev/login -d '{"usuario":"ana"}' | python3 -c 'import sys,json;print(json.load(sys.stdin)["token"])')
curl -s -X POST localhost:8080/v1/asistente/mensajes -H "Authorization: Bearer $TOKEN" \
     -d '{"mensaje":"cambiá la salida del hotel del viaje v-ana-1 al 2026-12-30"}'
# copiar el accionId de la respuesta:
curl -s -X POST localhost:8080/v1/asistente/acciones/ACCION_ID/confirmar -H "Authorization: Bearer $TOKEN"
```

`/dev/login` y `GET /v1/viajeros/me/viajes`, `GET /v1/viajes/{id}` son rutas de apoyo (Identity Provider y
panel simulados); el contrato del asistente es `specs/openapi.yaml`.

**¿Qué le escribo al asistente?** Lista completa de acciones, frases de ejemplo y una conversación completa en [`EJEMPLOS.md`](EJEMPLOS.md).

## Cómo probarlo

```bash
python3 -m unittest discover -s tests -t . -v
```

74 pruebas, ~2 s. No necesitan red ni instalar nada.

## Trazabilidad ADR → componente → archivo → prueba

| ADR | Decisión | Componente | Archivo | Pruebas |
|---|---|---|---|---|
| 031 | LLM con herramientas cerradas; derivación por reglas; guías | Tool Executor, Escalation Policy, Guide Catalog | `herramientas.py`, `politica.py`, `guias.py` | `test_funcional.py` (UC10–13), `test_seguridad.py::TestHerramientasCerradas` |
| 032 | Identidad propagada por JWT; ninguna herramienta recibe usuario | Conversation API, Pasarela | `api.py`, `sesion.py`, `simulators/pasarela.py` | `test_seguridad.py` (QA-13) |
| 033 | Confirmación en 2 pasos, un solo uso, atada al contenido, con vencimiento | Action Confirmation Manager | `confirmaciones.py`, `almacen.py` | `test_confirmacion.py` (QA-14) |
| 034 | Language Model Port, timeout, circuit breaker, fallback | Language Model Port | `modelo.py`, `adaptadores.py` | `test_disponibilidad.py` (QA-15), `test_modificabilidad.py` (QA-16) |
| 035 | Minimización de datos hacia el modelo | Data Minimizer | `minimizador.py` | `test_seguridad.py::TestMinimizacion` |
| 036 | Servicio sin estado + Conversation Store con TTL, límite por usuario, prioridad del panel | Conversation Store, límites | `almacen.py`, `limites.py` | `test_limites.py` (QA-17), `test_funcional.py::TestConsultas` |
| 026 | Spec-first | Contratos | `specs/openapi.yaml`, `specs/asyncapi.yaml` | `test_contrato.py` |

## Estructura

```
specs/            openapi.yaml (REST), asyncapi.yaml (eventos de auditoría)
trotamundos_asistente/
  api.py          Conversation API + armado de la aplicación
  asistente.py    Conversation Manager (orquesta un turno)
  herramientas.py Tool Executor          confirmaciones.py  Action Confirmation Manager
  politica.py     Escalation Policy      guias.py           Guide Catalog
  modelo.py       Language Model Port    adaptadores.py     modelos simulados
  minimizador.py  Data Minimizer          almacen.py         Conversation Store
  limites.py      tasa y concurrencia    auditoria.py       Audit Publisher
  simulators/     Trip Query/Command, Agency Integration, Audit Log, Gateway/IdP
tests/            pruebas por escenario de calidad
```

## Supuestos y límites del prototipo

* Valores a validar (están en `config.py`): expiración de confirmación 5 min, historial 24 h, timeout del
  modelo 2 s, 2 fallos abren el circuito 10 s, 20 mensajes/min por usuario, 8 turnos simultáneos.
* Los contratos de los servicios existentes (CRN-19) son supuestos documentados en `simulators/servicios.py`.
* Todo está en memoria; el servidor es de una sola instancia. En producción serían Redis/DB y varias réplicas.
* Los JWT usan HS256 con secreto aleatorio por ejecución; en producción los emite el Identity Provider.
* El modelo simulado entiende fechas `AAAA-MM-DD` o `DD/MM/AAAA` y solo cambios de inicio/fin de una reserva.
* Los textos de las guías son de ejemplo.
