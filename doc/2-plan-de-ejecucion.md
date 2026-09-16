# 2. Plan de ejecución y revisión

**Equipo:** Daniel Puerta Bernal · Tomás Marín Estrada · Juan Diego Guzmán Chalarca

El código ya está escrito: un único script, `limpieza_stackoverflow.py`, que cubre de la
carga al dataset limpio.

Este documento no reparte la escritura del código. Reparte la **revisión** y el trabajo
que queda.

---

## Lectura obligatoria antes de seguir

**El protocolo que se entregó NO es el archivo `doc/1-protocolo-previo-de-limpieza.md`
de este repositorio.** Ese archivo es un borrador largo, de nueve secciones, que nunca se
firmó ni se entregó. Lo que el profesor tiene en la mano es un documento mucho más corto,
con cuatro reglas y la declaración de uso de IA.

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

> **Ojo con el borrador del repositorio.** `doc/1-protocolo-previo-de-limpieza.md` tiene
> reglas que suenan comprometidas pero nunca se entregaron: umbral de filas al 80%,
> tolerancia de 1 año en coherencia, prohibición de "corregir inventando un valor", orden
> de aplicación, rutas de entrada y salida. **Ninguna de esas ata al equipo.** Decidan si
> ese archivo se queda como borrador histórico, se renombra para que nadie lo confunda con
> el entregado, o se borra. Si llega a la sustentación como si fuera el protocolo, van a
> terminar defendiendo reglas que nunca prometieron cumplir.

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
| J3 | **C** | **Bug.** `pct_nulos` se calcula en §2, antes de la conversión de tipos de §3. `pd.to_numeric(errors="coerce")` puede generar nulos nuevos, así que el umbral del 50% de §4.1 decide con porcentajes viejos. Recalcular después de la conversión y ver si cambia alguna decisión |
| J4 | **C** | El script imprime que `ConvertedComp` llega a 46,1% de nulos. Verificar ese número contra la corrida real: **P7 pregunta exactamente por el umbral** y esa cifra es la que lo justifica |

### Daniel — §5–§8

| # | Tipo | Pendiente |
|---|---|---|
| D1 | **B** | Duplicados: el script usa `keep="first"`, sin preferir el registro más completo. El protocolo entregado no promete nada sobre eso, así que cumple. Vale saber cuántas filas cambiarían con el otro criterio — **P22** |
| D2 | **A** | Normalización de categóricas (punto 9). El script solo hace `strip`, sin unificar mayúsculas. Decidir si hace falta, y verificar que el número de categorías no baje: si baja, se fusionaron categorías distintas |
| D3 | **A** | Columnas de respuesta múltiple separadas por `;` (punto 9). Son 19. Contar frecuencias sin separarlas da resultados sin sentido. Decidir si se derivan columnas de conteo o binarias |
| D4 | **B** | Categorías de baja frecuencia en `Ethnicity` y `Country`: hoy no se agrupan. Decisión libre; si se deja así, justificar por qué la cola larga no molesta |
| D5 | **B** | `WorkWeekHrs > 168` se corrige **dividiendo entre 10**. Al dividir, los 62 valores caen entre 22,5 y 47,5 horas semanales: creíble. Es una corrección inventada, pero el protocolo entregado no lo prohíbe. **Defenderla con ese dato**, no con la intuición |
| D6 | **B** | `CompTotal` se anula por encima de 10⁹ sin cruzar con `CompFreq` ni la moneda. Se justifica porque esa columna no entra al análisis de sueldos (para eso está `ConvertedComp`, ya en USD). Decirlo así en el informe |

### Los tres juntos

| # | Tipo | Pendiente |
|---|---|---|
| E1 | **B** | **El orden del pipeline.** El script imputa antes de tratar atípicos. Metodológicamente es discutible —los valores imputados aprietan Q1 y Q3—, pero §8 lo compensa: calcula los límites sobre los datos **sin imputar**, guardados en `valores_antes_de_imputar`. El protocolo entregado no fija ningún orden, así que no hay promesa rota. **Pero es el primer lugar donde va a mirar quien sepa del tema.** Hay que explicar ese parche sin titubear |
| E2 | **B** | El factor del rango intercuartílico es **1,5**, y el protocolo entregado solo dice "rango intercuartílico", sin número. Es el valor estándar, pero nadie se comprometió a él: saber por qué 1,5 y no 3 — **P15** |
| E3 | **B** | El protocolo entregado no promete ninguna tabla de acciones para atípicos; el script clasifica en cinco categorías igual. Eso es **más** de lo prometido, y está bien — pero solo si los tres pueden explicar los cinco casos — **P16** |
| E4 | **C** | Numeración interna inconsistente: los comentarios del script hablan de "sección 7" y "sección 8" con números que no coinciden con los encabezados reales. Cosmético, pero confunde en la sustentación |
| E5 | **A** | Decidir qué pasa con `doc/1-protocolo-previo-de-limpieza.md`: borrador histórico, renombrado o borrado. Hoy cualquiera que lo abra va a creer que es el protocolo entregado |

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
