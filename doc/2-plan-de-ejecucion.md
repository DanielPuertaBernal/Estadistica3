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

Ya no son "desviaciones del protocolo". Son tres cosas distintas, y conviene no mezclarlas:

- **A — Requisito del parcial sin cubrir.** El enunciado lo pide y el script no lo hace.
  Hay que implementarlo o justificar por qué no.
- **B — Decisión a justificar.** El script ya lo hace; hay que poder defenderlo, porque
  nadie prometió hacerlo así.
- **C — Bug o verificación.** Algo está mal o sin comprobar, aparte de todo lo demás.

### Tomás — §1–§3 y §9–§11

| # | Tipo | Pendiente |
|---|---|---|
| T1 | ✅ | ~~La carga leía un CSV suelto del directorio actual.~~ **Resuelto.** Lee `data/archive.zip` con `zipfile` sin descomprimir en disco y escribe en `salidas/`. Rutas resueltas desde la raíz del repositorio. Verificado de punta a punta: 64.461 → 63.803 filas |
| T2 | **A** | Reglas de coherencia (punto 11 del parcial). El script tiene dos: `Age1stCode ≤ Age` y `YearsCodePro ≤ YearsCode`. Decidir si alcanzan y si hace falta tolerancia por redondeo de encuesta |
| T3 | **B** | Ante una fila incoherente el script solo la **marca** con una bandera booleana: no corrige ni imputa. Es defendible —no se sabe cuál de las dos columnas está mal— pero hay que decirlo con esas palabras en el informe |
| T4 | **C** | Reproducibilidad (punto 12). La semilla está fijada pero nadie comprobó que dos corridas den el mismo archivo. Correr dos veces y comparar el hash |

### Juan Diego — §4–§4.5

| # | Tipo | Pendiente |
|---|---|---|
| J1 | **A** | Eliminación de filas (punto 5). El script no descarta ninguna fila por exceso de vacíos. Decidir si se implementa un umbral o si se justifica conservarlas todas |
| J2 | **B** | Todo faltante categórico va a `"Desconocido"`, sin distinguir a quien no respondió de quien nunca recibió la pregunta. El protocolo entregado solo promete `"Desconocido"`, así que cumple; pero es la clase de matiz que preguntan |
| J3 | ✅ | ~~`pct_nulos` se calculaba antes de la conversión de tipos.~~ **Resuelto.** Se recalcula en §4.1 ya con los tipos corregidos. La conversión no genera ningún nulo nuevo en este dataset, así que no cambia ninguna decisión — pero el umbral queda apoyado en los números correctos |
| J4 | **C** | El script imprime que `ConvertedComp` llega a 46,1% de nulos. Verificar ese número contra la corrida real: **P7 pregunta exactamente por el umbral** y esa cifra es la que lo justifica |

### Daniel — §5–§8

| # | Tipo | Pendiente |
|---|---|---|
| D1 | ✅ | ~~Duplicados con `keep="first"`.~~ **Resuelto.** Ahora conserva el registro más completo, con el primero como desempate. **0 grupos cambian de ganador**: los duplicados son encuestas casi vacías con la misma cantidad de campos llenos. Dato listo para **P22** |
| D2 | ✅ | ~~Solo hacía `strip`.~~ **Resuelto.** Unifica mayúsculas solo donde hay colisión real, hacia la variante más frecuente; no baja todo a minúsculas, que destruiría `United States`. Verificado: **0 colisiones**, 80.590 categorías antes y después |
| D3 | ✅ | ~~Columnas de respuesta múltiple sin tratar.~~ **Resuelto.** Son **20**, no 19. Se agregaron 20 columnas `n_<pregunta>`, la tabla `salidas/frecuencias_respuesta_multiple.csv` con las 286 opciones reales, y binarias `usa_<opción>` para `LanguageWorkedWith` |
| D4 | ✅ | ~~Cola larga sin agrupar.~~ **Resuelto.** Columnas `Country_agrupado` y `Ethnicity_agrupado` al lado de las originales. **El dato para el informe:** la cola de `Ethnicity` es el 3,9% de la gente, la de `Country` el 30,1%. Agrupar países mete casi un tercio en `"Otros"` |
| D5 | ✅ | ~~`WorkWeekHrs ÷ 10` sin respaldo impreso.~~ **Resuelto.** El script ahora imprime la evidencia: los 62 corregidos quedan entre 22,5 y 47,5 h/semana, contra un 90% central de 30 a 50 en el resto de la encuesta. Falta el párrafo del informe |
| D6 | ✅ | ~~`CompTotal` anulado sin justificación impresa.~~ **Resuelto.** El script imprime que hay **142 monedas distintas** en el dataset: por eso no se reconstruye y el análisis usa `ConvertedComp`, ya en USD. Falta el párrafo del informe |

### Los tres juntos

| # | Tipo | Pendiente |
|---|---|---|
| E1 | **B** | **El orden del pipeline.** El script imputa antes de tratar atípicos. Metodológicamente es discutible —los valores imputados aprietan Q1 y Q3—, pero §8 lo compensa: calcula los límites sobre los datos **sin imputar**, guardados en `valores_antes_de_imputar`. El protocolo entregado no fija ningún orden, así que no hay promesa rota. **Pero es el primer lugar donde va a mirar quien sepa del tema.** Hay que explicar ese parche sin titubear |
| E2 | **B** | El factor del rango intercuartílico es **1,5**, y el protocolo entregado solo dice "rango intercuartílico", sin número. Es el valor estándar, pero nadie se comprometió a él: saber por qué 1,5 y no 3 — **P15** |
| E3 | **B** | El protocolo entregado no promete ninguna tabla de acciones para atípicos; el script clasifica en cinco categorías igual. Eso es **más** de lo prometido, y está bien — pero solo si los tres pueden explicar los cinco casos — **P16** |
| E4 | ✅ | ~~Numeración interna inconsistente.~~ **Resuelto.** Había una sola referencia mal: §3 decía que la verificación de tipos ocurre en "sección 7" cuando está en §6. Las demás citas verificadas y correctas |
| E5 | ✅ | ~~El repositorio guardaba un borrador que nadie entregó, con nombre de protocolo.~~ **Resuelto.** `doc/1-protocolo-previo-de-limpieza.md` es ahora la transcripción literal del documento entregado |
| E6 | **C** | Dos erratas en el protocolo entregado: dice `Respondentm` en vez de `Respondent`, y "sí coinciden" en vez de "si coinciden". Están transcritas tal cual porque el archivo es el registro de lo entregado. Decidir si se corrigen en el informe final o se dejan |

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
