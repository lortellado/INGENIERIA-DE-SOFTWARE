# Prototipo

> Segunda entrega. El código está en el repositorio, carpeta `prototipo-asistente/` (ver README). Esta página documenta alcance, ejecución y trazabilidad.

## Alcance

Prototipo funcional (MVP) del **Assistant Service** de la Iteración 5, enfoque *spec-driven*: primero los contratos (`specs/openapi.yaml`, `specs/asyncapi.yaml`, ADR-026) y luego el código, con una prueba que verifica que ambos coinciden.

Cubre los casos de uso **UC10** (consultas), **UC11** (cambio con confirmación), **UC12** (guías) y **UC13** (derivación) y los escenarios de calidad **QA-13 a QA-17**. No cubre las Iteraciones 1–4: esos servicios están simulados.

## Qué está implementado y qué simulado

* **Implementado:** Conversation API, Conversation Manager, Tool Executor, Action Confirmation Manager, Escalation Policy, Guide Catalog, Language Model Port (timeout + circuit breaker + fallback), Data Minimizer, Conversation Store (TTL), límite por usuario y tope de concurrencia, Audit Publisher.
* **Simulado:** Trip Query, Trip Command, Agency Integration, Audit Log, API Gateway/Identity Provider y el **modelo de lenguaje** (adaptador por reglas, intercambiable por uno real sin tocar otros componentes).

## Cómo ejecutarlo

```
python3 -m trotamundos_asistente chat --usuario ana
python3 -m trotamundos_asistente servidor --puerto 8080
python3 -m unittest discover -s tests -t . -v
```

Solo requiere Python 3.9+, sin instalar paquetes.

## Trazabilidad

| ADR | Componente | Archivo | Prueba |
|---|---|---|---|
| ADR-031 | Tool Executor, Escalation Policy, Guide Catalog | `herramientas.py`, `politica.py`, `guias.py` | `test_funcional.py`, `test_seguridad.py` |
| ADR-032 | Conversation API (identidad por JWT) | `api.py`, `sesion.py` | `test_seguridad.py` (QA-13) |
| ADR-033 | Action Confirmation Manager | `confirmaciones.py` | `test_confirmacion.py` (QA-14) |
| ADR-034 | Language Model Port | `modelo.py`, `adaptadores.py` | `test_disponibilidad.py` (QA-15), `test_modificabilidad.py` (QA-16) |
| ADR-035 | Data Minimizer | `minimizador.py` | `test_seguridad.py` |
| ADR-036 | Conversation Store, límites | `almacen.py`, `limites.py` | `test_limites.py` (QA-17) |
| ADR-026 | Contratos | `specs/` | `test_contrato.py` |

## Resultados de las pruebas

74 pruebas automáticas, todas pasan. Ejemplos por escenario:

* **QA-13:** pedir el viaje de otro usuario no revela datos ni llegan al modelo; ninguna herramienta recibe usuario; herramientas inexistentes se rechazan y auditan.
* **QA-14:** proponer no modifica; confirmar es de un solo uso (10 confirmaciones simultáneas aplican una sola); vence a los 5 min; otro usuario recibe 403 y queda auditado.
* **QA-15:** con el modelo caído responde 503 con alternativas, el panel sigue, las guías y derivaciones siguen, y el circuito evita insistir.
* **QA-16:** otro adaptador funciona sin cambios en el resto; ningún componente referencia un adaptador concreto.
* **QA-17:** el 21.º mensaje del minuto recibe 429; en un pico de 24 usuarios nunca hay más de 8 turnos simultáneos y el panel responde igual.

## Supuestos y limitaciones

Valores de configuración definidos por el grupo (Iteración 5, Step 7), contratos de servicios existentes asumidos (CRN-19), almacenamiento en memoria, modelo simulado. Ver README para el detalle.
