# 2. Plan de ejecución y revisión

**Equipo:** Daniel Puerta Bernal · Tomás Marín Estrada · Juan Diego Guzmán Chalarca

El código ya está escrito: un único script, `limpieza_stackoverflow.py`, que cubre de la
carga al dataset limpio.

Este documento no reparte la escritura del código. Reparte la **revisión** y el trabajo
que queda.

---

## Lectura obligatoria antes de seguir

**El protocolo entregado son cuatro reglas, no nueve secciones.** Durante un tiempo el
repositorio guardó un borrador largo que nunca se firmó ni se entregó, y el trabajo
pendiente se midió contra él por error. Ese borrador ya se descartó:
`doc/1-protocolo-previo-de-limpieza.md` es hoy la transcripción literal de lo que el
docente tiene en la mano.

Esa diferencia cambia todo el trabajo pendiente, así que va primero.

### Lo que el protocolo entregado realmente compromete

| # | Regla comprometida | ¿El script la cumple? |
|---|---|---|
| 1 | Se descarta toda columna a la que le falte más de la mitad de los datos | ✅ Sí — umbral >50% en §4.1 |
| 2 | Numérica simétrica → promedio · Numérica asimétrica → mediana · Categórica → categoría `"Desconocido"` | ✅ Sí — §4.2 decide por sesgo, §4.5 crea `"Desconocido"` |
| 3 | Atípicos por rango intercuartílico, no por k desviaciones estándar | ✅ Sí — §8 usa RIC |
| 4 | Dos filas son la misma respuesta si coinciden en todas las columnas menos `Respondent` | ✅ Sí — §5 compara sin `Respondent` |

**El script cumple las cuatro. No hay ninguna desviación del protocolo entregado.**

### Lo que el protocolo entregado NO compromete

Esto importa igual, porque define qué es una desviación y qué no:

- No fija el **orden** de las operaciones.
- No fija el **factor** del rango intercuartílico.
- No fija una **tabla de acciones** para los atípicos.
- No dice nada de **eliminación de filas**, corrección de tipos, normalización de texto,
  reglas de coherencia, semilla ni rutas de archivos.

Todo lo que el script hace en esos puntos es **decisión libre del equipo**, no una promesa
rota. Se defiende por sus méritos; no se reporta como desviación.

> **Reglas que NO los atan.** El borrador descartado prometía cosas que nunca se
> entregaron: umbral de filas al 80%, tolerancia de 1 año en coherencia, prohibición de
> "corregir inventando un valor", orden de aplicación, rutas de entrada y salida.
> **Ninguna de esas ata al equipo.** Si alguien las menciona en la sustentación, no salen
> del protocolo entregado.

---

## Por qué el reparto cambió

El plan original separaba el trabajo en módulos `src/`, un archivo por persona, para que
nadie se bloqueara esperando a otro. Ese reparto ya no aplica: el código llegó completo y
en un solo archivo, y el profesor pidió que el script viva en la raíz.

Lo que sí sigue vigente es la razón de fondo: **la sustenta una sola persona, elegida al
azar, sin notas**. Cada integrante tiene que poder explicar línea por línea una parte que
no escribió. Por eso el reparto es por secciones del script, y cada quien revisa un bloque
completo.

## Reparto de secciones

| Secciones del script | Contenido | Revisa |
|---|---|---|
| §1 – §3 | Carga, exploración inicial, corrección de tipos | **Tomás** |
| §4 – §4.5 | Nulos, imputación numérica y categórica, tabla de sesgo, histogramas | **Juan Diego** |
| §5 – §7 | Duplicados, verificación de tipos, normalización de categóricas | **Daniel** |
| §8 | Tratamiento de atípicos (los 5 casos + conteo de pérdida) | **Daniel** |
| §9 – §11 | Coherencia, variables derivadas, guardado del dataset limpio | **Tomás** |

**Qué significa "revisar":** no es leer por encima. Quien revisa una sección tiene que
poder defenderla en la sustentación sin el autor al lado, y resolver los pendientes de esa
sección.

> **Nota de carga.** Daniel queda con §5 a §8, que incluye atípicos: el punto más pesado y
> el que más preguntas tiene en el banco (P15, P16). Si se ve desbalanceado, lo natural es
> mover §5–§7 a otra persona y dejar §8 solo.

---

## Pendientes

**Estado al día de hoy:** Daniel terminó todo su código. Tomás y Juan Diego todavía no
arrancaron. El código que llegó del compañero ya cubre buena parte de sus bloques, así
que lo que les queda es **menos de lo que parece**: verificar, completar dos huecos y
escribir.

| | Código | Escritura |
|---|---|---|
| **Daniel** | ✅ completo | 5 párrafos del informe |
| **Tomás** | 2 huecos reales (T4, T5) | 2 párrafos |
| **Juan Diego** | ✅ ya cumple; falta verificar un número | 3 párrafos |

Tres tipos de pendiente, y conviene no mezclarlos:

- **A — Requisito del parcial sin cubrir.** El enunciado lo pide y el script no lo hace.
- **B — Decisión a justificar.** El script ya lo hace; hace falta un párrafo que lo
  defienda, porque el protocolo entregado no prometía nada al respecto.
- **C — Bug o verificación.** Algo está mal o sin comprobar.

### Daniel — §5–§8 · código terminado

| # | Tipo | Estado |
|---|---|---|
| D1 | ✅ | Duplicados: conserva el registro más completo. 0 grupos cambian de ganador — los duplicados son encuestas casi vacías |
| D2 | ✅ | Normalización: caracteres de control corregidos (`CurrencyDesc` traía 4 valores con tabulador), espacios y colisiones de mayúsculas. 80.590 categorías antes y después |
| D3 | ✅ | 20 columnas de respuesta múltiple: conteos `n_<pregunta>`, tabla de 286 opciones en `salidas/`, binarias para `LanguageWorkedWith` |
| D4 | ✅ | `Country_agrupado` y `Ethnicity_agrupado`. Cola de `Ethnicity` = 3,9% de la gente; la de `Country` = 30,1% |
| D5 | ✅ | `WorkWeekHrs ÷ 10`: evidencia impresa, 62 valores entre 22,5 y 47,5 h/semana |
| D6 | ✅ | `CompTotal`: 142 monedas distintas en el dataset, por eso no se reconstruye |
| D7 | ✅ | Caso 6: `ConvertedComp` alto = **subpoblación distinta**, la quinta categoría que faltaba. Se conserva y se marca |
| D8 | ✅ | Caso 7: `YearsCode` y `YearsCodePro` separados en 47+4 errores de digitación contra 3.072+1.890 veteranos reales |

**Le queda solo escribir** (ver *Lo que nadie puede delegar*, abajo): D5, D6, E1, E2, E3.

### Tomás — §1–§3 y §9–§11 · sin arrancar

| # | Tipo | Pendiente |
|---|---|---|
| T1 | ✅ | Carga desde `data/archive.zip`, rutas desde la raíz del repositorio |
| T2 | **B** | Las reglas de coherencia comparan sin tolerancia. El enunciado no exige tolerancia, así que alcanza con justificar la decisión |
| T3 | **B** | Ante una fila incoherente el script solo la **marca**, no corrige ni imputa. Defendible —no se sabe cuál de las dos columnas está mal— pero hay que decirlo así en el informe |
| T4 | **C** | **Punto 12.** La semilla está fijada pero nadie comprobó que dos corridas den el mismo archivo. Correr dos veces y comparar el hash del CSV. Es de las cosas más rápidas de toda la lista |
| T5 | **A** | **Punto 11, hueco real.** El enunciado pide textual *"verificar valores máximos y mínimos para variables numéricas"*. §9 solo tiene las dos reglas lógicas; falta el chequeo de rangos sobre el dataset ya limpio |
| T6 | **C** | **Punto 3.** El enunciado nombra `.info()`; el script usa `dtypes.value_counts()` más el shape por separado. Cubre lo mismo, pero agregar la llamada literal cuesta una línea y cierra el punto sin discusión |

### Juan Diego — §4–§4.5 · sin arrancar, pero el código ya cumple

| # | Tipo | Pendiente |
|---|---|---|
| J1 | **B** | **Corrección importante:** el enunciado dice *"aplicar **alguna o varias** de las siguientes estrategias"*, y eliminar registros incompletos es una de varias. No implementarlo **no es un hueco**: basta con justificar por qué se eligió imputar en vez de eliminar |
| J2 | **B** | Todo faltante categórico va a `"Desconocido"`, sin distinguir a quien no respondió de quien nunca recibió la pregunta. El enunciado acepta `"Desconocido"` explícitamente, así que cumple; es un matiz que preguntan |
| J3 | ✅ | El % de nulos se recalcula después de convertir tipos. La conversión no genera ningún nulo nuevo, así que no cambia ninguna decisión |
| J4 | **C** | Verificar contra la corrida real que `ConvertedComp` da 46,1% de nulos. **P7 pregunta exactamente por el umbral** y esa cifra es la que lo sostiene |

Los puntos 5 y 6 del parcial ya están cubiertos por el código: umbral del 50%, imputación
por sesgo, tabla antes/después, histogramas superpuestos y la comparación de dos
estrategias sobre `ConvertedComp` en §4.4.

### Los tres juntos

| # | Tipo | Pendiente |
|---|---|---|
| E1 | **B** | **El orden del pipeline.** Imputa antes de tratar atípicos. §8 lo compensa calculando Q1 y Q3 sobre los datos **sin imputar**. El protocolo entregado no fija ningún orden, así que no hay promesa rota — pero es el primer lugar donde va a mirar quien sepa |
| E2 | **B** | **Por qué factor 1,5 y no 3.** El protocolo entregado dice "rango intercuartílico" sin número: nadie se comprometió a 1,5. Es **P15** |
| E3 | **B** | Los 7 casos de atípicos, explicados uno por uno. Es **P16** |
| E4 | ✅ | Numeración interna: había una sola referencia mal (§3 decía "sección 7" por §6) |
| E5 | ✅ | El borrador de 9 secciones ya no está; `doc/1-protocolo-previo-de-limpieza.md` es la transcripción de lo entregado |
| E6 | **C** | Dos erratas en el protocolo entregado (`Respondentm`, "sí coinciden"). Decidir si se corrigen en el informe final |

---

## Lo que nadie puede delegar

El parcial prohíbe generar con IA el documento de entrega, el protocolo, **las
justificaciones y las conclusiones**. Y **P34 pregunta textual**: *"¿En qué punto usó una
herramienta de IA y qué le pidió exactamente? Muéstreme qué cambió usted de lo que le
entregó."*

Todos los números ya están impresos por el script. Los párrafos los escribe el equipo:

| Párrafo | Quién | El dato ya está |
|---|---|---|
| E2 — por qué factor 1,5 | los 3 | Declarado en §8 |
| E1 — por qué el orden no contamina | los 3 | §8 usa datos sin imputar |
| E3 — los 7 casos de atípicos | Daniel | Todos impresos con evidencia |
| D5 — por qué dividir entre 10 no es inventar | Daniel | 62 valores → 22,5 a 47,5 h |
| D6 — por qué no se reconstruye `CompTotal` | Daniel | 142 monedas distintas |
| J1 — por qué imputar y no eliminar filas | Juan Diego | Umbral del 50% en §4.1 |
| J2 — por qué `"Desconocido"` y no la moda | Juan Diego | §4.5 |
| T3 — por qué marcar y no corregir | Tomás | §9, dos columnas de bandera |

**El más importante es E2.** "¿Por qué 1,5?" es P15, y el protocolo entregado no fija el
factor. Si nadie puede responderlo, el punto más pesado del parcial queda sin defensa.

---

## Cierre

| Tarea | Responsable |
|---|---|
| Comparación dataset inicial vs. dataset final | Daniel |
| Declaración de uso de IA al inicio del documento (ya redactada en el protocolo entregado: Claude para código, Gemini para estilo) | los 3 |
| Armar el comprimido: código, declaración, dataset original y dataset limpio | Juan Diego |
| Presentación de 10 minutos | Tomás |

**La entrega es un archivo comprimido, no este repositorio.** El dataset limpio se toma de
`salidas/stackoverflow_limpio.csv`.

> **Este plan no entra al comprimido.** Es coordinación interna. El parcial prohíbe generar
> con IA el documento de entrega, el protocolo, las justificaciones y las conclusiones:
> esos textos los escribe el equipo.

## Checkpoints

| # | Condición para avanzar |
|---|---|
| 1 | Cada quien leyó su bloque completo y puede explicarlo sin el código al frente |
| 2 | Cada pendiente tipo **A** tiene una decisión: se implementa o se justifica |
| 3 | Cada pendiente tipo **B** tiene un párrafo escrito que lo defiende |
| 4 | Los bugs tipo **C** están corregidos o descartados con evidencia |
| 5 | Dos corridas seguidas producen archivos con el mismo hash |
| 6 | Revisión cruzada superada: cada uno defendió el bloque del otro |

## Reglas de trabajo

- **Una rama por persona.** `main` solo recibe trabajo terminado.
- **El archivo original no se toca.** Nunca. La limpieza escribe un archivo nuevo.
- **El protocolo entregado no se reescribe.** Ya está en manos del profesor.
- **Nada de notebooks compartidos.** El código vive en `.py`.

## Preparación de la sustentación

Sustenta **una sola persona, elegida al azar, sin notas**. El banco de 40 preguntas es la
guía de estudio. Las más duras, y quién tiene ventaja por su bloque:

| Pregunta | Tema | Ventaja |
|---|---|---|
| P7 | Por qué ese umbral de nulos | Juan Diego |
| P15 · P16 | Método de atípicos y el que se conservó | Daniel |
| P22 | Qué define un duplicado real | Daniel |
| P32 | Si llegan 500 registros nuevos, ¿el código aguanta? | Tomás |
| P33 | Qué parte escribió cada integrante | los 3 |
| P34 | En qué punto se usó IA y qué cambió el equipo | los 3 |

Ventaja no es quién sustenta. Sustenta uno solo, al azar.
