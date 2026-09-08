# Árbol de utilidad (Utility Tree)

Base: Bass, Clements, Kazman — *Software Architecture in Practice*, 4ta ed., Sección 19.4.

El árbol de utilidad es una herramienta que un arquitecto usa cuando no tiene acceso directo y constante a todos los stakeholders para elicitar requisitos, y necesita organizar y priorizar los requisitos de calidad (ASRs — Architecturally Significant Requirements) que él mismo cree relevantes para el sistema.

## Estructura

El árbol tiene 4 niveles, de la raíz a las hojas:

1. **Raíz**: el nodo se llama literalmente "Utilidad" (Utility). Representa la "bondad" general del sistema.
2. **Segundo nivel — Atributos de calidad**: se listan los atributos de calidad relevantes para el sistema (ej: Rendimiento, Disponibilidad, Seguridad, Usabilidad, Modificabilidad). No hace falta cubrir todos los atributos posibles del libro — solo los que importan para ese sistema en particular.
3. **Tercer nivel — Refinamientos**: cada atributo se refina en aspectos más específicos y accionables. Por ejemplo:
   - Rendimiento → "latencia de datos", "throughput de transacciones"
   - Disponibilidad → "recuperación ante falla de nodo", "detección de fallas de red"
   - Seguridad → "confidencialidad de datos de pago", "autenticación de usuarios"
   - Usabilidad → "tiempo de aprendizaje de usuarios nuevos", "eficiencia de usuarios frecuentes"

   Estos refinamientos son justamente los que se eligen para que se ajusten al sistema en cuestión, no una lista fija.
4. **Hojas — Escenarios concretos**: cada refinamiento se lleva a uno o más escenarios concretos de 6 partes (o al menos a una versión resumida del estímulo y la respuesta esperada).

## Priorización de las hojas

Cada escenario-hoja se etiqueta con dos valores, en escala **Alto (H) / Medio (M) / Bajo (L)**:

- **Valor de negocio**: qué tan importante es este escenario para el negocio/los stakeholders si se lograra. Idealmente lo asigna un stakeholder o el project decision maker; si no está disponible, el arquitecto puede estimarlo con criterio propio, aclarándolo.
- **Riesgo técnico**: qué tan difícil/riesgoso es, desde el punto de vista técnico, lograr esa respuesta. Lo asigna el arquitecto, según su experiencia y conocimiento del dominio.

La combinación de ambos valores es lo que permite priorizar: los escenarios (H, H) — alto valor de negocio y alto riesgo técnico — son los que más atención merecen del arquitecto, porque son los que más podrían hacer fracasar el proyecto si no se atienden a tiempo. Los (L, L) son los que menos urgen.

## Ejemplo de formato de presentación

```
Utilidad
├── Rendimiento
│   ├── Latencia de checkout
│   │   └── [Escenario] Un usuario confirma su compra en un pico de 500 pedidos/minuto,
│   │       el sistema procesa la confirmación en menos de 2 segundos. (H, M)
│   └── Throughput de búsquedas
│       └── [Escenario] 1000 búsquedas concurrentes se resuelven en menos de 1 segundo cada una. (M, L)
├── Disponibilidad
│   └── Recuperación ante falla de servidor
│       └── [Escenario] Un servidor de la granja falla en operación normal; el sistema
│           notifica al operador y sigue funcionando sin downtime. (H, H)
└── Seguridad
    └── Confidencialidad de datos de pago
        └── [Escenario] Un atacante intenta acceder a datos de tarjetas; el sistema
            detecta y bloquea el intento, sin exposición de datos. (H, H)
```

## Cómo construirlo en esta skill

1. Si el usuario no especificó qué atributos son relevantes, proponerlos con criterio de arquitecto (basado en el tipo de sistema que describe), pero dejar en claro que son una propuesta y que el usuario puede ajustarlos.
2. Para cada atributo elegido, generar 1–2 refinamientos razonables.
3. Para cada refinamiento, generar al menos un escenario-hoja (puede resumirse: estímulo → respuesta, sin necesidad de desplegar la tabla completa de 6 partes salvo que el usuario pida el detalle de esa hoja en particular).
4. Etiquetar cada hoja con (Valor de Negocio, Riesgo Técnico) en H/M/L, aclarando brevemente el porqué de esa estimación.
5. Si el usuario pide expandir una hoja puntual, ahí sí generar la tabla completa de 6 partes del SEI para ese escenario.
