# 1. Protocolo previo de limpieza

**Dataset:** Stack Overflow Developer Survey — `palvinder2006/stackoverflow`
**Equipo:** _(nombres)_

> Este documento se congela ANTES de ver el resultado de aplicar las reglas.
> Una vez firmado no puede modificarse. Las desviaciones se reportan al final del
> trabajo, punto por punto, con la evidencia que las motivó.

> **Borrador.** Las decisiones y justificaciones de abajo son una propuesta para
> discutir y reescribir con palabras del equipo. No son el texto final.

---

## 1.1 Eliminación de columnas por faltantes

| Campo | Decisión |
|---|---|
| Umbral | Se elimina toda columna con más del 50% de faltantes |
| Justificación | En una encuesta, un campo vacío casi siempre significa que la pregunta no le correspondía a esa persona, no que el dato se haya perdido. Un umbral más exigente castigaría a las preguntas sobre remuneración, que son opcionales por naturaleza y a la vez centrales para el estudio. |
| Excepciones | Ninguna. Con este umbral no se elimina ninguna columna, y eso se reporta como resultado del protocolo, no como un paso omitido. |

## 1.2 Eliminación de filas

| Campo | Decisión |
|---|---|
| ¿Se eliminan filas con algún faltante? | No |
| Umbral por fila | Se descarta la fila con más del 80% de campos vacíos |
| Columnas obligatorias | `Respondent`, `MainBranch`, `Country`, `Employment` |
| Justificación | Casi nadie respondió absolutamente todas las preguntas, así que exigir el registro completo dejaría el estudio sin datos. Hay una diferencia real entre quien eligió no responder algo y quien abandonó la encuesta a mitad de camino: lo primero es información, lo segundo es ruido. Las columnas obligatorias son las que respondió prácticamente todo el mundo, así que exigirlas apenas cuesta registros. |

## 1.3 Criterio de imputación por tipo de variable

| Tipo de variable | Estrategia | Justificación |
|---|---|---|
| Numérica simétrica | Media | Ninguna variable numérica de este dataset resultó simétrica, así que la regla se declara pero se reportará que no llegó a aplicarse. |
| Numérica asimétrica | Mediana | Cuando la distribución tiene una cola larga, la media se corre hacia los valores extremos y deja de representar al encuestado típico. |
| Categórica | Categoría explícita `"Desconocido"` | Imputar con la moda inventa una respuesta y engorda artificialmente la categoría más común. Marcarla como desconocida conserva el hecho de que faltaba. |
| Faltante estructural | No se imputa; se marca `"No aplica"` | Si la pregunta nunca se le hizo al encuestado, cualquier valor que pongamos es ficción. |

Criterio simétrica vs. asimétrica: `|skew| < 0,5` simétrica; `≥ 0,5` asimétrica.

## 1.4 Corrección de tipos de datos

| Campo | Decisión |
|---|---|
| Etiquetas no numéricas | Se mapean al valor límite antes de convertir: `"Less than 1 year"` → 0,5 · `"More than 50 years"` → 51 · `"Younger than 5 years"` → 4 · `"Older than 85"` → 86. Afecta a `YearsCode`, `YearsCodePro` y `Age1stCode`. |
| Por qué conviene | Recupera para el análisis numérico tres variables de experiencia que hoy el software lee como texto. |
| Riesgo asumido | El valor asignado en los extremos es una convención nuestra, no un dato del encuestado. Queda documentado. |
| Fechas | No aplica: el dataset no contiene columnas de fecha. Se declara explícitamente para que no parezca un punto omitido. |

## 1.5 Normalización de valores categóricos

| Campo | Decisión |
|---|---|
| Normalización de texto | `strip` y minúsculas, como medida defensiva. Se verificó que el dataset ya viene estandarizado, así que no esperamos cambios; se deja constancia igual. |
| Verificación del riesgo | Comparar el número de categorías antes y después. Si baja, fusionamos categorías que en realidad eran distintas y hay que revisar. |
| Respuesta múltiple | Varias columnas guardan más de una respuesta en la misma celda, separadas por punto y coma. No se modifican: se derivan columnas nuevas de conteo y binarias. Contar frecuencias sin separarlas daría resultados sin sentido. |
| Categorías de baja frecuencia | Agrupar en `"Otros"` las categorías con menos del 1% de los registros en `Ethnicity` y `Country`, que arrastran una cola larga de valores con muy pocos casos. |

## 1.6 Reglas de coherencia

| Regla | Condición esperada | Acción si se viola |
|---|---|---|
| Edad plausible | `10 ≤ Age ≤ 100` | _(a decidir)_ |
| Horas semanales posibles | `1 ≤ WorkWeekHrs ≤ 168` | _(a decidir)_ |
| Salario en rango humano | `CompTotal < 10⁹` | _(a decidir)_ |
| No se programa antes de nacer | `Age1stCode ≤ Age` | _(a decidir)_ |
| La experiencia profesional cabe en la total | `YearsCodePro ≤ YearsCode` | _(a decidir)_ |

## 1.7 Detección de atípicos

| Campo | Decisión |
|---|---|
| Método | Rango intercuartílico |
| Parámetro | Factor 1,5 |
| Justificación | El criterio de las k desviaciones estándar no se sostiene con estos datos: en la variable de remuneración total la desviación estándar ni siquiera puede calcularse, porque los valores extremos desbordan el cálculo. Y en distribuciones tan sesgadas, la media y la desviación ya vienen arrastradas por los mismos atípicos que queremos encontrar. El rango intercuartílico se apoya en cuantiles y no sufre ese problema. |
| Alcance | Las variables numéricas del dataset y las tres recuperadas en 1.4 |

**Regla de acción.** La acción sigue a la clasificación, no al revés.
Eliminar es la última opción y exige justificación.

| Clasificación | Acción comprometida |
|---|---|
| Error de digitación | Corregir si el valor correcto es deducible; si no, tratar como faltante e imputar según 1.3 |
| Error de unidad o escala | Convertir a la unidad correcta y conservar |
| Observación válida extrema | Conservar sin modificar |
| Subpoblación distinta | Conservar y marcar con una variable indicadora para analizarla aparte |
| Observación contaminante | Eliminar, documentando el criterio caso por caso |

> Candidato para el caso obligatorio de "atípico que NO debe eliminarse": el método
> marca buena parte de los salarios más altos de la muestra. Son sueldos reales del
> sector, no errores.

## 1.8 Duplicados

| Campo | Decisión |
|---|---|
| Qué define un duplicado real | Coincidencia en todas las columnas excepto `Respondent` |
| Justificación | `Respondent` es un número correlativo, distinto en cada fila. Incluirlo en la comparación garantiza que jamás se detecte un duplicado, que es justo lo que el parcial advierte al excluir los datos de tipo identificador. |
| Duplicados exactos | Comparando el registro completo no aparece ninguno. La prueba se repite sin el identificador. |
| Duplicados parciales | Conservar el registro más completo y, en caso de empate, el primero. |

## 1.9 Reproducibilidad

| Campo | Decisión |
|---|---|
| Semilla aleatoria | 42, fijada al inicio del script |
| Archivo de entrada | `data/archive.zip` — no se modifica |
| Archivo de salida | `data/stackoverflow_limpio.csv` |
| Orden de aplicación | Tipos (1.4) → coherencia (1.6) → columnas (1.1) → filas (1.2) → duplicados (1.8) → atípicos (1.7) → imputación (1.3) → normalización (1.5). Imputar antes de tratar los atípicos contaminaría las medias y medianas con valores imposibles. |

---

## Firma del equipo

| Integrante | Firma | Fecha |
|---|---|---|
| | | |
| | | |
| | | |
