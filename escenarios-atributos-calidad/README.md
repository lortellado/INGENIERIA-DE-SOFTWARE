# Skill: `escenarios-atributos-calidad`

Skill de Claude desarrollada para el Trabajo Práctico de Ingeniería de Software (arquitectura de software), en base a *Software Architecture in Practice* (Bass, Clements, Kazman, 4ta ed.).

## ¿Qué hace?

Actúa como un **Arquitecto de Software Senior**. Ante un enunciado, ejercicio o situación de un sistema, ejecuta automáticamente y en una sola respuesta un flujo de 4 pasos:

1. **Detecta el atributo de calidad involucrado** (discutiendo candidatos alternativos si el enunciado es ambiguo entre más de uno).
2. **Chequea la completitud** del escenario contra el enunciado original: para lo que no esté explícito, resuelve con un supuesto razonable y lo deja aclarado (sin frenar la respuesta).
3. **Genera la tabla completa** con la plantilla de 6 partes del SEI.
4. **Construye el árbol de utilidad completo del sistema** (varios atributos relevantes, no solo el detectado), incorporando el escenario del paso anterior como una de sus hojas, todas etiquetadas con Valor de Negocio / Riesgo Técnico (H/M/L).

Además, admite pedidos puntuales cuando el usuario los pide explícitamente:
- Chequeo de completitud "bloqueante" sobre un escenario ya armado (no genera la tabla hasta que el usuario decide cómo completarlo).
- Árbol de utilidad general para todo un sistema, sin partir de un único enunciado.
- Solo la identificación del atributo, sin el resto del flujo.

## Estructura del repositorio

```
escenarios-atributos-calidad/
├── README.md                                  ← este archivo
├── SKILL.md                                    ← definición de la skill (rol, comportamiento, formato de salida)
├── references/
│   ├── plantilla-6-partes-sei.md              ← detalle de las 6 partes del escenario (Cap. 3.3)
│   ├── atributos-de-calidad-guia.md           ← resumen de cada atributo de calidad + palabras clave (Caps. 4–14)
│   └── arbol-utilidad-guia.md                 ← estructura y proceso para construir el árbol de utilidad (Cap. 19.4)
└── evals/
    └── ejemplos-de-prueba.md                   ← 4 casos de prueba documentados (input, output, evaluación),
                                                    incluyendo un ejemplo tomado directamente del libro de la materia
```

## Base bibliográfica

Toda la skill está construida a partir de:
- **Sección 3.3** — definición y estructura del escenario de calidad de 6 partes del SEI.
- **Capítulos 4 a 14** — definición de cada atributo de calidad y sus "general scenarios".
- **Sección 19.4** — construcción del árbol de utilidad.

Los archivos dentro de `references/` no son transcripciones literales del libro, sino resúmenes/síntesis propios pensados para que la skill los consulte como material de apoyo ("focusing" de la skill), tal como pide la consigna del TP.

## Cómo se usa

Al invocar la skill (por ejemplo, cargándola en un proyecto de Claude o pasándole el `SKILL.md` como skill activa), Claude la activa automáticamente cuando el usuario:
- Menciona atributos de calidad, ASR, o el método de escenarios del SEI.
- Pega un enunciado o situación de un sistema y pide identificar el atributo de calidad involucrado.
- Pega un escenario (completo o parcial) y pide que se revise si está bien formado.
- Pide armar un árbol de utilidad.

## Validación

La skill fue testeada en 4 iteraciones (corrigiendo tres problemas detectados en el uso real: el flujo no se ejecutaba completo ante un enunciado, el árbol de utilidad quedaba acotado a un solo atributo, y el campo `description` superaba el límite de 200 caracteres de Claude.ai). El detalle completo de estas pruebas —incluyendo los problemas detectados, las correcciones aplicadas, los inputs y los outputs obtenidos— está documentado en `evals/ejemplos-de-prueba.md`.

## Cómo subirla a Claude.ai (para que persista entre chats)

1. Ir a `claude.ai/customize/skills` (Configuración → Customize → Skills).
2. Habilitar **Code execution** si no lo está (requisito de la función Skills).
3. Click en **"+ Add"** y subir este `.zip` (la carpeta `escenarios-atributos-calidad/` debe quedar en la raíz del zip, tal como está armado).
4. Activar el toggle de la skill una vez subida.

A partir de ahí, la skill queda disponible automáticamente en todos los chats nuevos, sin necesidad de volver a pegar el `SKILL.md`.
