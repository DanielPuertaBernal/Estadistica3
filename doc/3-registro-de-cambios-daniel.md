# 3. Registro de cambios — Daniel

Qué tocó Daniel del código que llegó del compañero, y por qué. Cubre su bloque de
revisión (§5–§8, pendientes D1–D6), el bug J3 y la limpieza del repositorio.

Uso interno: **no va en la entrega**. Tomás y Juan Diego llevan su propio registro.

## Script de limpieza

| Sección | Cambio | Motivo |
|---|---|---|
| §1 | Lee `data/archive.zip` con `zipfile`, sin descomprimir en disco. Rutas resueltas desde la raíz del repositorio | Leía un CSV suelto del directorio actual; solo corría desde una carpeta |
| §4.1 | El % de nulos se recalcula después de convertir tipos | Se medía en §2, antes de la conversión. `to_numeric(errors="coerce")` puede crear nulos nuevos y el umbral del 50% decidía con datos viejos. **En este dataset no cambia ninguna decisión**, pero el umbral queda apoyado en los números correctos |
| §5 | De cada grupo de duplicados se conserva el registro **más completo**, no el primero del archivo. Empate: el primero | El orden del archivo no significa nada. Se imprime cuántos grupos cambian de ganador: **0** — los duplicados son encuestas casi vacías con la misma cantidad de campos llenos |
| §7 | Normalización: se recortan espacios siempre; las mayúsculas se unifican **solo donde hay colisión real**, hacia la variante más frecuente. Se cuentan categorías antes y después | Pasar todo a minúsculas convertiría `United States` en `united states` sin arreglar nada: **0 columnas** tienen colisiones. El conteo antes/después prueba que no se fusionó ninguna categoría distinta |
| §7.1 | **Nuevo.** Detecta las 20 columnas de respuesta múltiple (`;`), agrega `n_<pregunta>` con cuántas opciones marcó cada persona, exporta `salidas/frecuencias_respuesta_multiple.csv` con las 286 opciones reales, y genera binarias `usa_<opción>` para `LanguageWorkedWith` | Contar frecuencias sin separar da resultados sin sentido: `Python;SQL` y `SQL;Python` cuentan como categorías distintas. Binarias para una sola pregunta porque expandir las 20 agregaría 286 columnas |
| §7.2 | **Nuevo.** Columnas `Country_agrupado` y `Ethnicity_agrupado`: categorías bajo el 1% pasan a `"Otros"`. Las originales no se tocan | Las dos tienen cola larga, pero muy distinta: en `Ethnicity` la cola es el **3,9%** de la gente (agrupar es barato); en `Country` es el **30,1%** (agrupar metería casi un tercio de los encuestados en una categoría que no significa nada) |
| §7 | Se corrigen caracteres de control dentro de las categorías y se colapsan espacios repetidos | El punto 9 pide corregir errores por caracteres especiales. Los había: **`CurrencyDesc` traía 4 valores con un tabulador adentro** (`'e\tCook Islands dollar'`) |
| §8 | Evidencia impresa para dos decisiones que antes iban sin respaldo | `WorkWeekHrs ÷ 10`: los 62 valores corregidos quedan entre 22,5 y 47,5 h/semana. `CompTotal`: hay **142 monedas** distintas, por eso no se reconstruye y el análisis usa `ConvertedComp` (ya en USD) |
| §8 | **Caso 6 nuevo.** `ConvertedComp` alto (2.301 registros) clasificado como **subpoblación distinta**: se conserva y se marca con `subpoblacion_salario_alto` | Faltaba la quinta categoría que pide el punto 10, y faltaba clasificar este grupo. No están repartidos al azar: **48,6% son de EE.UU. contra 19,5% del dataset**, 91% con empleo de tiempo completo contra 70%, mediana de 9 años de experiencia contra 6 |
| §8 | **Caso 7 nuevo.** `YearsCode` (3.119) y `YearsCodePro` (1.894) separados en dos grupos dentro del mismo marcado | Faltaban por clasificar. El mismo marcado juntaba cosas distintas: **47 y 4 casos imposibles** (implicarían programar desde antes de los 5 años) → error de digitación, se imputan con la mediana; **3.072 y 1.890 veteranos reales** (edad mediana 50 y 52) → observación válida extrema, se conservan |

**Resultado:** 64.461 × 61 → **63.803 × 111**. Sin errores, de punta a punta.

### Un bug que apareció al implementar el caso 7

La marca auxiliar `_age_era_real` (para no acusar de error de digitación a una fila
cuya edad imputamos nosotros) se colaba en el tratamiento de categóricas: §7 la pasaba
a texto con `astype(str)` y `False` se volvía la cadena `"False"`, que en Python es
verdadera. Resultado: 651 falsos errores de digitación en vez de 47.

Se arregló excluyendo de `columnas_categoricas` todo lo que empiece con `_`. Convención
nueva: **prefijo `_` = andamiaje interno del script**, fuera de todo tratamiento y
borrado antes de guardar.

## Dependencias

`requirements.txt` pasó de **111 paquetes a 3**. El script solo importa `pandas`, `numpy` y
`matplotlib`; el resto era el stack de Jupyter, `kaggle`, `seaborn`, `requests` y su cola de
transitivas, sin ningún consumidor en el código. Las transitivas reales (`pillow`,
`python-dateutil`, `fonttools`, etc.) las resuelve pip sola.

## Repositorio

| Cambio | Motivo |
|---|---|
| Script a la raíz, archivo único | Indicación del profesor |
| Borrada la carpeta `archive/` | Era el original descomprimido; quedó de sobra al leer el ZIP directo |
| `data/` solo con `archive.zip` | Indicación del profesor. El limpio y todo lo derivado van a `salidas/`, ignorado por git |
| Borrado el Excel de entrega | Indicación del profesor |
| `doc/1-protocolo-previo-de-limpieza.md` reemplazado por la transcripción literal de lo entregado | El repo guardaba un borrador de 9 secciones que nunca se firmó ni se entregó, con nombre de protocolo |
| `README` sin instrucciones de descarga de Kaggle | El dataset viaja en el repo: clonar y correr alcanza |

## Lo que NO se tocó

Las cuatro reglas del protocolo entregado: umbral del 50% para columnas, imputación por
sesgo, rango intercuartílico para atípicos, y duplicado = todas las columnas menos
`Respondent`. **El script las cumplía y las sigue cumpliendo.**

Pendientes abiertos y su reparto: `doc/2-plan-de-ejecucion.md`.
