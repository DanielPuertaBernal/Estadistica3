# 2. Plan de ejecución y revisión

**Equipo:** Daniel Puerta Bernal · Tomás Marín Estrada · Juan Diego Guzmán Chalarca

El código ya está escrito: un único script, `limpieza_stackoverflow.py`, que cubre
de la carga al dataset limpio. El protocolo congelado está en
`doc/1-protocolo-previo-de-limpieza.md`.

Este documento ya no reparte la escritura del código. Reparte la **revisión** y las
**correcciones pendientes**, que es lo que queda.

---

## Por qué el reparto cambió

El plan original separaba el trabajo en módulos `src/`, un archivo por persona, para
que nadie se bloqueara esperando a otro. Ese reparto ya no aplica: el código llegó
completo y en un solo archivo, y el profesor pidió que el script viva en la raíz del
repositorio.

Lo que sí sigue vigente es la razón de fondo del plan: **la sustenta una sola persona,
elegida al azar, sin notas**. Así que cada integrante tiene que poder explicar línea
por línea una parte que no escribió. Por eso el reparto de abajo es por secciones del
script, y cada quien revisa un bloque completo, no fragmentos sueltos.

---

## Reparto de secciones

| Secciones del script | Contenido | Revisa |
|---|---|---|
| §1 – §3 | Carga, exploración inicial, corrección de tipos | **Tomás** |
| §4 – §4.5 | Nulos, imputación numérica y categórica, tabla de sesgo, histogramas | **Juan Diego** |
| §5 – §7 | Duplicados, verificación de tipos, normalización de categóricas | **Daniel** |
| §8 | Tratamiento de atípicos (los 5 casos + conteo de pérdida) | **Daniel** |
| §9 – §11 | Coherencia, variables derivadas, guardado del dataset limpio | **Tomás** |

**Qué significa "revisar":** no es leer por encima. Quien revisa una sección tiene que
poder defenderla en la sustentación sin el autor al lado, y tiene que resolver los
pendientes de esa sección que están listados abajo.

> **Nota de carga.** Daniel queda con §5 a §8, que incluye el punto de atípicos: el más
> pesado del parcial y el que más preguntas tiene en el banco de sustentación (P15, P16).
> Si al arrancar se ve desbalanceado, lo natural es mover §5–§7 a otra persona y dejar
> §8 solo.

---

## Pendientes: desviaciones del protocolo

El script no cumple todo lo que el protocolo congeló. **Esto no es un error del código:
el parcial pide reportar las desviaciones punto por punto con evidencia.** Pero hay que
decidir, en cada línea de esta tabla, si se corrige el código o si se reporta la
desviación con justificación.

Cada pendiente está asignado a quien revisa la sección donde vive.

### Tomás — §1–§3 y §9–§11

| # | Pendiente | Referencia | Qué hay que decidir o hacer |
|---|---|---|---|
| T1 | ~~La carga lee un CSV suelto del directorio actual~~ | Protocolo 1.9 | ✅ **Resuelto.** Lee `data/archive.zip` con `zipfile` sin descomprimir en disco, escribe en `data/stackoverflow_limpio.csv` y resuelve todas las rutas desde la raíz del repositorio. Verificado: corre de punta a punta, 64.461 → 63.803 filas |
| T2 | Las reglas de coherencia no aplican la tolerancia de 1 año | Protocolo 1.6 | El protocolo da margen de 1 año por redondeo de encuesta en `Age1stCode ≤ Age` y `YearsCodePro ≤ YearsCode`. El script compara sin tolerancia |
| T3 | El script solo **marca** las filas incoherentes con banderas booleanas | Protocolo 1.6 | El protocolo compromete una acción: corregir si es reconstruible (ej. invertir los dos valores), si no, tratar como faltante e imputar. Decidir si se cumple o si se reporta la bandera como desviación justificada |
| T4 | No se verifica que dos corridas produzcan el mismo archivo | Punto 12 · Protocolo 1.9 | La semilla está fijada, pero falta la prueba. Correr dos veces y comparar el hash del CSV de salida |

### Juan Diego — §4–§4.5

| # | Pendiente | Referencia | Qué hay que decidir o hacer |
|---|---|---|---|
| J1 | La eliminación de filas no está implementada | Protocolo 1.2 | Falta el umbral del 80% de campos vacíos por fila y la exigencia de `Respondent`, `MainBranch`, `Country`, `Employment`. Es un punto completo del protocolo que no aparece en el código |
| J2 | El faltante estructural no se distingue del faltante normal | Protocolo 1.3 | El protocolo pide marcar `"No aplica"` cuando la pregunta nunca se le hizo al encuestado. El script manda todo lo categórico a `"Desconocido"` |
| J3 | `pct_nulos` se calcula en §2, **antes** de la conversión de tipos de §3 | — | `pd.to_numeric(errors="coerce")` puede generar nulos nuevos. El umbral del 50% de §4.1 está decidiendo con porcentajes viejos. Recalcular después de la conversión y verificar si cambia alguna decisión |
| J4 | La justificación impresa en §4.1 afirma que `ConvertedComp` llega a 46,1% | Protocolo 1.1 | Verificar ese número contra la corrida real y dejarlo como evidencia en el informe (P7 del banco pregunta exactamente por el umbral) |

### Daniel — §5–§8

| # | Pendiente | Referencia | Qué hay que decidir o hacer |
|---|---|---|---|
| D1 | Los duplicados parciales se resuelven con `keep="first"` | Protocolo 1.8 | El protocolo dice conservar el **registro más completo** y, en caso de empate, el primero. El script no ordena por completitud antes de descartar |
| D2 | La normalización de texto solo hace `strip` | Protocolo 1.5 | El protocolo pide `strip` **y minúsculas**, y verificar que el número de categorías no baje (si baja, se fusionaron categorías distintas) |
| D3 | Las columnas de respuesta múltiple separadas por `;` no se tratan | Protocolo 1.5 · Punto 9 | Son 19 columnas. El protocolo pide derivar columnas de conteo y binarias, sin modificar las originales |
| D4 | Las categorías de baja frecuencia no se agrupan | Protocolo 1.5 | Agrupar en `"Otros"` las categorías con menos del 1% de los registros en `Ethnicity` y `Country` |
| D5 | `WorkWeekHrs > 168` se corrige **dividiendo entre 10** | Protocolo 1.6 | El protocolo dice textual: *"todo valor fuera de rango se trata como faltante e imputa; no se corrige inventando un valor"*. El código hace justo lo contrario. Es la desviación más discutible: la división entre 10 es defendible, pero contradice algo que ya estaba firmado |
| D6 | `CompTotal` se anula por umbral fijo de 10⁹ | Protocolo 1.6 | El protocolo pide **cruzar con `CompFreq` y la moneda** antes de actuar: si el valor reconstruye un error de unidad (anual puesto en el campo mensual), se corrige. El script no hace ese cruce |

### Los tres juntos

| # | Pendiente | Referencia | Qué hay que decidir o hacer |
|---|---|---|---|
| E1 | **El orden del pipeline está invertido respecto al protocolo** | Protocolo 1.9 | El protocolo fija: tipos → coherencia → columnas → filas → duplicados → atípicos → imputación → normalización. El script hace: tipos → imputación → duplicados → normalización → atípicos → coherencia. El protocolo advierte explícitamente *"imputar antes de tratar los atípicos contaminaría las medias y medianas con valores imposibles"*. El propio código lo admite sin querer: §8 guarda `valores_antes_de_imputar` para poder calcular Q1 y Q3 sobre datos limpios. Ese parche existe **porque** el orden está mal. Es la decisión más grande que queda: reordenar el pipeline, o reportar la desviación explicando que el parche produce el mismo resultado |
| E2 | Archivos pesados fuera del control de versiones | README | ✅ **Parcialmente resuelto.** Se borró la carpeta del compañero (CSV duplicado verificado por hash contra `archive/`, más salidas regenerables). El dataset limpio pesa 103.189.512 bytes, a 1,6 MB del límite duro de GitHub: se versiona comprimido en `data/stackoverflow_limpio.zip` (8,8 MB) y el CSV suelto quedó en `.gitignore`. **Pendiente:** al aplicar D3 (columnas derivadas de respuesta múltiple) el CSV crece; hay que reconfirmar que el ZIP sigue siendo la vía y volver a comprimir después de cada corrida |
| E3 | ~~Ubicación del script en el repositorio~~ | — | ✅ **Resuelto.** Quedó en la raíz del repositorio, `limpieza_stackoverflow.py`, por indicación del profesor |
| E4 | Numeración interna inconsistente | — | Los comentarios del script se refieren a "sección 7" y "sección 8" con números que no coinciden con los encabezados reales. Cosmético, pero confunde en la sustentación |

---

## Cierre

| Tarea | Responsable |
|---|---|
| Reporte de desviaciones respecto al protocolo, punto por punto, con la evidencia | los 3 |
| Comparación dataset inicial vs. dataset final | Daniel |
| Declaración de uso de herramientas de IA, al inicio del documento | los 3 |
| Armar el comprimido: código, declaración, dataset original y dataset limpio | Juan Diego |
| Presentación de 10 minutos | Tomás |
| Firmar el protocolo (`doc/1-protocolo-previo-de-limpieza.md` sigue con la tabla de firmas vacía) | los 3 |

---

## Checkpoints

| # | Condición para avanzar |
|---|---|
| 1 | Cada quien leyó su bloque completo y puede explicarlo sin el código al frente |
| 2 | Cada pendiente de la tabla tiene una decisión: se corrige, o se reporta como desviación justificada |
| 3 | Las correcciones acordadas están aplicadas y el script corre de principio a fin sin errores |
| 4 | Dos corridas seguidas producen archivos con el mismo hash |
| 5 | Revisión cruzada superada: cada uno defendió el bloque del otro |

## Reglas de trabajo

- **Una rama por persona.** `main` solo recibe trabajo terminado.
- **El archivo original no se toca.** Nunca. La limpieza escribe un archivo nuevo.
- **El protocolo no se reescribe.** Está congelado. Lo que cambia se reporta como
  desviación, con la evidencia que la motivó.
- **Nada de notebooks compartidos.** El código vive en `.py`.

## Preparación de la sustentación

El banco de 40 preguntas del enunciado es la guía de estudio. Las más duras, y quién
las tiene cubiertas con su bloque:

| Pregunta | Tema | Quién debería tener la mejor respuesta |
|---|---|---|
| P7 | Por qué ese umbral de nulos | Juan Diego |
| P15 · P16 | Método de atípicos y el que se conservó | Daniel |
| P22 | Qué define un duplicado real | Daniel |
| P32 | Si llegan 500 registros nuevos, ¿el código aguanta? | Tomás |

Pero ojo: eso es quién tiene la ventaja, no quién sustenta. Sustenta uno solo, al azar.
